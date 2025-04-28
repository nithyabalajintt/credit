import os
import json
import pandas as pd
from dotenv import load_dotenv
from openai import AzureOpenAI
import warnings
import re

warnings.filterwarnings("ignore")
load_dotenv()

# 1) Azure OpenAI client setup
client = AzureOpenAI(
    azure_endpoint   = os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"],
    api_key          = os.environ["AZURE_OPENAI_API_KEY"],
    api_version      = os.environ["API_VERSION_GA"],
)
print("AzureOpenAI client initialized")

# 2) Paths
INPUT_PATH  = "output/Company_Financials_Cleaned.xlsx"
OUTPUT_PATH = "output/Company_Financials_Synthetic_First5.xlsx"

# 3) Load first 5 rows
df_full = pd.read_excel(INPUT_PATH)
df5     = df_full.iloc[:5].reset_index(drop=True)
print("\n=== INPUT (first 5 rows) ===")
print(df5)

# 4) Prepare features
features = df5.drop(columns=[
    "Company", "Industry", "Sector", "Financial Year", 
    "Net Income Continuous Operations", "Total Revenue", 
    "Stockholders Equity", "Total Assets", "Current Assets", 
    "Current Liabilities", "Inventory", "Total Debt", 
    "Interest Expense", "EBIT"
], errors="ignore")

# Add new columns with NA
new_columns = ["Loan Value", "Collateral Value", "Loan Tenure", "Credit Score", "Risk Score"]
for col in new_columns:
    df5[col] = pd.NA
print("\n=== With New Columns ===")
print(df5)

# Convert features dataframe to string
str_df = features.to_string(index=False)

# 5) JSON parser
def parse_json_response(text: str):
    txt = text.strip().strip("```")
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", txt, re.DOTALL)
        return json.loads(m.group(0)) if m else None

# 6) Prompt Template (fixed with f-string)
prompt_template = f"""
You are a financial risk expert responsible for evaluating a company's loan risk based on their financial data. Your task is to generate a "Risk Score" that ranges from 0 to 100, where:

- A Risk Score of 0 represents minimum risk and indicates a financially stable company.
- A Risk Score of 100 represents maximum risk and indicates a financially unstable company.

The lower the risk score, the safer the company is deemed to be for issuing a loan. The higher the risk score, the greater the likelihood that the company may default on the loan.

### Input Features to Consider:
Below are the financial features provided:

9. Net Profit Margin (%): Higher is better.
10. Return on Equity (ROE) (%): Higher is better.
11. Return on Assets (ROA) (%): Higher is better.
12. Asset Turnover Ratio: Higher is better.
13. Current Ratio: Higher than 1 is good.
15. Debt Equity Ratio: Lower is better.
16. Debt To Asset Ratio: Lower is better.
17. Interest Coverage Ratio: Higher than 3 is good.

### Calculating the Risk Score:
Your risk score should be based on the combined analysis of all features.

Positive indicators (reduce risk): Net Profit Margin, ROE, ROA, Asset Turnover, Current Ratio, Interest Coverage.  
Negative indicators (increase risk): Debt, Liabilities, Interest Expense, Debt-to-Equity, Debt-to-Asset.

Consider:
- If collateral > loan value -> Risk Score between 0-10
- If loan << Total Revenue and Assets -> Risk Score between 0-10
- Otherwise increase risk appropriately.

### Final Instructions:
Generate the loan and risk details based on these features:
- Loan value: ₹10,00,000 to ₹50,00,00,000
- Collateral value: ₹10,00,000 to ₹55,00,00,000
- Loan tenure: 6 to 240 months
- Credit score: 300 to 900

Introduce reasonable variations across companies.

### Your Response Format:
Respond ONLY with a JSON list like this:

[
    {{
        "Loan Value": 10000000,
        "Collateral Value": 15000000,
        "Loan Tenure (Months)": 120,
        "Credit Score": 750,
        "Risk Score": 20,
        "Explanation": "Strong profitability and low debt leads to low risk."
    }},
    {{
        "Loan Value": 25000000,
        "Collateral Value": 22000000,
        "Loan Tenure (Months)": 180,
        "Credit Score": 700,
        "Risk Score": 40,
        "Explanation": "Moderate financial health but higher loan to collateral ratio."
    }}
]

No extra text.

### Financial Features Table:
{str_df}
"""

# 7) Call Azure OpenAI
resp = client.chat.completions.create(
    model    = os.environ["AZURE_OPENAI_DEPLOYMENT"],
    messages = [
        {"role": "system", "content": "You generate synthetic loan & risk data."},
        {"role": "user", "content": prompt_template}
    ],
    temperature=0.6,
    max_tokens=1500
)

raw = resp.choices[0].message.content
print(f"[Raw response]\n{raw}")


