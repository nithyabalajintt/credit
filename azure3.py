import os
import time
import json
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from openai import AzureOpenAI
import concurrent.futures
import warnings

warnings.filterwarnings("ignore")
load_dotenv()  

# ── 1) Azure OpenAI Credentials ───────────────────────────────────────────────
model_name      = os.environ["AZURE_OPENAI_MODEL_NAME"]
endpoint_url    = os.environ["AZURE_OPENAI_ENDPOINT"]
api_key         = os.environ["AZURE_OPENAI_API_KEY"]
deployment_name = os.environ["AZURE_OPENAI_DEPLOYMENT"]
api_version     = os.environ["API_VERSION_GA"]

# ── 2) Initialize the AzureOpenAI client ──────────────────────────────────────
client = AzureOpenAI(
    azure_endpoint=endpoint_url,
    azure_deployment=deployment_name,
    api_key=api_key,
    api_version=api_version,
)

# ── 3) File paths ──────────────────────────────────────────────────────────────
INPUT_PATH  = "output/Company_Financials_Cleaned.xlsx"
OUTPUT_PATH = "output/Company_Financials_Synthetic_With_Explainability.xlsx"
CHECKPOINT_PATH = "output/Checkpoint_Synthetic.xlsx"

# ── 4) Load & prepare your data ───────────────────────────────────────────────
df       = pd.read_excel(INPUT_PATH)
df       = df.iloc[:50]
features = df.drop(columns=["Company", "Industry", "Sector", "Financial Year"], errors="ignore")
print(df)

# ── 5) JSON parsing helper ────────────────────────────────────────────────────
def parse_json_response(text: str):
    text = text.strip()
    # strip markdown code fences if present
    if text.startswith("```") and text.endswith("```"):
        text = text.strip("```").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
print(text) 

# ── 6) Single-row synthetic generator ──────────────────────────────────────────
def generate_synthetic(financials: dict):
    prompt = f"""
You are a financial risk expert.

Given these company financials (₹ or %):
{financials}

Rules:
- Loan Value: ₹0–₹50 Crore (realistic).
- Collateral Value: ≥ Loan Value, up to ₹55 Crore.
- Loan Tenure: 6–240 months.
- Credit Score: integer 300–900.
- Risk Score: 0–100 (lower is safer).
- Provide a one-line “Explanation” for Credit & Risk decisions.

Respond ONLY with JSON in exactly this format:
{{
  "Loan Value": 2500000,
  "Collateral Value": 7500000,
  "Loan Tenure (Months)": 120,
  "Credit Score": 720,
  "Risk Score": 18,
  "Explanation": "Good profitability and low debt led to a high credit score and low risk."
}}
"""
    try:
        resp = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role":"system","content":"You generate synthetic loan & risk data."},
                {"role":"user",  "content":prompt}
            ],
            temperature=0.6,
            max_tokens=500
        )
        content = resp.choices[0].message.content
        return parse_json_response(content)
    except Exception as e:
        print(f"⚠️ Azure OpenAI call error: {e}")
        return None

# ── 7) Function to handle processing in parallel ───────────────────────────────
def process_batch(batch_data, batch_idx):
    print(f"Processing batch {batch_idx}...")
    synthetic_rows = []
    for _, row in batch_data.iterrows():
        fin = row.dropna().to_dict()
        out = generate_synthetic(fin)
        if not out:
            out = {
                "Loan Value": None,
                "Collateral Value": None,
                "Loan Tenure (Months)": None,
                "Credit Score": None,
                "Risk Score": None,
                "Explanation": "Generation failed."
            }
        synthetic_rows.append(out)
    # Save the intermediate batch results
    batch_df = pd.DataFrame(synthetic_rows)
    batch_df.to_excel(CHECKPOINT_PATH, index=False)
    return synthetic_rows

# ── 8) Split the data into smaller batches and process them in parallel ─────────
def process_data_in_parallel(features, num_threads=5, batch_size=100):
    # Split the data into batches
    batches = [features.iloc[i:i + batch_size] for i in range(0, len(features), batch_size)]

    # Process batches in parallel using ThreadPoolExecutor
    all_synthetic_rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(process_batch, batch, i) for i, batch in enumerate(batches)]
        for future in concurrent.futures.as_completed(futures):
            all_synthetic_rows.extend(future.result())
    
    return all_synthetic_rows

# ── 9) Merge & save ───────────────────────────────────────────────────────────
synthetic_rows = process_data_in_parallel(features)
syn_df = pd.DataFrame(synthetic_rows)
final = pd.concat([df.reset_index(drop=True), syn_df], axis=1)
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
final.to_excel(OUTPUT_PATH, index=False)

print(f"✅ Finished! Saved to {OUTPUT_PATH}")
