import os
import pandas as pd
import time
from openai import AzureOpenAI
from dotenv import load_dotenv
import warnings
import io
 
warnings.filterwarnings("ignore")
load_dotenv()
 
# Azure OpenAI Client
client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version=os.environ["API_VERSION_GA"],
)
print("AzureOpenAI client initialized")
 
INPUT_PATH = "output/Company_Financials_Cleaned.xlsx"
OUTPUT_PATH = "output/Company_Financials_Synthetic_First100.xlsx"
 
# Load data
df_full = pd.read_excel(INPUT_PATH)
df_batch = df_full.iloc[:100].copy().reset_index(drop=True)
 
# Add synthetic columns
synthetic_cols = ["Loan Value", "Collateral Value", "Loan Tenure", "Credit Score", "Risk Score"]
for col in synthetic_cols:
    df_batch[col] = pd.NA
 
# Define prompt format for single row
def build_prompt(row_dict):
    context = "You are a financial expert generating synthetic loan and credit details."
    details = "\n".join([f"{k}: {v}" for k, v in row_dict.items()])
    instruction = """\n\nBased on the above financial details, generate the following for this company:
- Loan Value (Rs)(1000000 to 500000000)
- Collateral Value(Rs)(1000000 to 550000000)
- Loan Tenure(Months)(6 to 240)
- Credit Score (between 300 and 900)
- Risk Score (between 0 and 100)
 Make sure to give values from minimum to maximum. try to understand the data. the positives and negative effect on the risk score and calculate the requried detials. dont
Respond only in pipe-separated format:
Loan Value | Collateral Value | Loan Tenure | Credit Score | Risk Score
"""
    return f"{context}\n{details}{instruction}"
 
# Process in 2 batches
for batch_start in [0, 50]:
    batch_end = batch_start + 50
    print(f"\nProcessing rows {batch_start} to {batch_end - 1}")
    for i in range(batch_start, batch_end):
        row_data = df_batch.iloc[i].drop(synthetic_cols, errors='ignore').dropna().to_dict()
        prompt = build_prompt(row_data)
 
        try:
            response = client.chat.completions.create(
                model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
                messages=[
                    {"role": "system", "content": "You generate synthetic loan and risk data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=200
            )
            content = response.choices[0].message.content.strip()
            parts = [x.strip() for x in content.split('|')]
 
            if len(parts) == 5:
                df_batch.loc[i, synthetic_cols] = parts
                print(f"Row {i} processed.")
            else:
                print(f"Row {i} - unexpected output: {content}")
        except Exception as e:
            print(f"Row {i} failed: {e}")
        time.sleep(1.5)
 
# Save final DataFrame
df_batch.to_excel(OUTPUT_PATH, index=False)
print(f"Saved synthetic dataset to: {OUTPUT_PATH}")
