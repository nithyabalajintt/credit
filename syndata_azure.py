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
print("✅ AzureOpenAI client initialized")

# 2) Paths
INPUT_PATH  = "output/Company_Financials_Cleaned.xlsx"
OUTPUT_PATH = "output/Company_Financials_Synthetic_First5.xlsx"

# 3) Load first 5 rows
df_full = pd.read_excel(INPUT_PATH)
df5     = df_full.iloc[:5].reset_index(drop=True)
print("\n=== INPUT (first 5 rows) ===")
print(df5)

# 4) Prepare features
features = df5.drop(columns=["Company","Industry","Sector","Financial Year"], errors="ignore")

# 5) JSON parser
def parse_json_response(text: str):
    txt = text.strip().strip("```")
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", txt, re.DOTALL)
        return json.loads(m.group(0)) if m else None

# 6) Your exact prompt template (braces escaped)
prompt_template = """
You are a financial risk expert responsible for evaluating a company's loan risk based on their financial data. Your task is to generate a "Risk Score" that ranges from 0 to 100, where:

    - A **Risk Score of 0** represents **minimum risk** and indicates a financially stable company.
    - A **Risk Score of 100** represents **maximum risk** and indicates a financially unstable company.

    The lower the risk score, the safer the company is deemed to be for issuing a loan. The higher the risk score, the greater the likelihood that the company may default on the loan.

    ### Input Features to Consider:
    Below are the financial features provided. These features help assess the company's financial health, loan eligibility, and associated risk:

    1. **Net Income Continuous Operations**: 
        - This is the company's net income derived from its core business operations.
        - A higher value indicates profitability and financial health.
        - **Range**: Negative to positive values. A negative value is a sign of losses.
        - **Impact on Risk**: Higher values are generally associated with lower risk.

    2. **Total Revenue**:
        - This is the total revenue generated from the company's operations.
        - **Range**: Values typically range from 0 to several billions depending on the size of the company.
        - **Impact on Risk**: Higher revenue indicates strong operations, which lowers the risk.

    3. **Stockholders' Equity**:
        - This represents the residual interest in the assets of the company after liabilities are deducted. It's an indicator of the company's net worth.
        - **Range**: A company can have negative or positive equity depending on its assets and liabilities.
        - **Impact on Risk**: Higher equity reduces risk as it indicates financial strength.

    4. **Total Debt**:
        - This is the total amount of debt the company has accumulated.
        - **Range**: Values can range from very low to extremely high amounts.
        - **Impact on Risk**: Higher debt increases the risk of default.

    5. **Current Liabilities**:
        - The company’s short-term financial obligations.
        - **Range**: This is typically within the company’s current liabilities, often up to a few billion in large companies.
        - **Impact on Risk**: Higher current liabilities suggest the company may face liquidity issues, increasing risk.

    6. **EBIT (Earnings Before Interest and Taxes)**:
        - This is the company’s earnings before accounting for interest and taxes.
        - **Range**: Values can range from negative to positive depending on the profitability.
        - **Impact on Risk**: A higher EBIT usually lowers risk as it shows strong earnings performance.

    7. **Current Assets**:
        - These are assets that can be converted into cash within a year.
        - **Range**: This could range from very low to high depending on the company’s operational efficiency.
        - **Impact on Risk**: More current assets reduce the risk as they help in managing short-term obligations.

    8. **Total Assets**:
        - The total value of everything the company owns.
        - **Range**: It varies from small companies with a few million to large firms worth billions.
        - **Impact on Risk**: A higher value in assets usually means less risk as the company can cover its debts.

    9. **Net Profit Margin (%)**:
        - This is the percentage of revenue that turns into profit.
        - **Range**: This ranges from negative (losses) to positive, with higher percentages being more favorable.
        - **Impact on Risk**: A higher profit margin means more efficiency, reducing risk.

    10. **Return on Equity (ROE) (%)**:
        - This is the return generated on shareholders’ equity.
        - **Range**: This can range from negative values to very high positive values.
        - **Impact on Risk**: A high ROE indicates efficient use of equity and is associated with lower risk.

    11. **Return on Assets (ROA) (%)**:
        - Measures how efficiently assets are used to generate profit.
        - **Range**: A higher positive percentage indicates better asset utilization.
        - **Impact on Risk**: High ROA reduces risk as it shows efficient use of assets.

    12. **Asset Turnover Ratio**:
        - This measures how effectively the company is using its assets to generate sales.
        - **Range**: Typically between 0 and 5, higher is better.
        - **Impact on Risk**: A higher ratio means better asset utilization and lower risk.

    13. **Current Ratio**:
        - This ratio compares a company’s current assets to its current liabilities.
        - **Range**: Ideal ratio is 1 or higher; anything less than 1 indicates potential liquidity issues.
        - **Impact on Risk**: Higher current ratios reduce the risk of defaulting on short-term obligations.

    14. **Interest Expense**:
        - The cost of the company’s debt, i.e., interest payments.
        - **Range**: Higher expenses indicate higher debt servicing costs.
        - **Impact on Risk**: Higher interest expenses increase risk as it burdens cash flows.

    15. **Debt Equity Ratio**:
        - A measure of the company’s financial leverage.
        - **Range**: A ratio greater than 1 indicates more debt than equity.
        - **Impact on Risk**: A higher debt-to-equity ratio increases financial risk.

    16. **Debt To Asset Ratio**:
        - This shows what proportion of a company’s assets are financed by debt.
        - **Range**: The ratio ranges from 0 (no debt) to 1 (100% of assets are financed by debt).
        - **Impact on Risk**: A higher ratio increases the company’s risk of default.

    17. **Interest Coverage Ratio**:
        - This measures the company’s ability to pay interest on its debt.
        - **Range**: A higher ratio (greater than 3) is favorable.
        - **Impact on Risk**: A higher ratio reduces risk as it shows the company can easily meet interest obligations.

    ### Calculating the Risk Score:
    Your risk score should be based on the combined analysis of all the above features. The higher the values of indicators like **Net Income**, **Revenue**, **Stockholders' Equity**, **EBIT**, **Net Profit Margin**, **ROE**, and **ROA**, the lower the risk score will be.
    
    Conversely, **Total Debt**, **Current Liabilities**, **Interest Expense**, **Debt-to-Equity**, and **Debt-to-Asset ratios** are negative indicators and their high values will increase the risk score.
    
    ### Feature Importance and Risk Impact:
    1. **High Impact Features**: **Net Income**, **Total Revenue**, **Stockholders’ Equity**, **Total Debt**, and **EBIT**. These features play a significant role in determining the loan risk. A sudden drop in any of these can greatly increase the risk.
    2. **Medium Impact Features**: **Current Assets**, **Total Assets**, **Net Profit Margin**, **Return on Equity**, **Return on Assets**.
    3. **Low Impact Features**: **Current Ratio**, **Interest Expense**, **Debt Equity Ratio**, **Debt To Asset Ratio**, **Interest Coverage Ratio**.
    
    ### Final Instructions:
    Generate the loan and risk details based on these features. 
    The loan value should be realistic (₹10,00,000 to ₹50 Crore), 
    collateral should be at realistic (₹10,00,000 to ₹55 Crore), 
    loan tenure should be between 6 to 240 months.
    
    For each company row, ensure that all features are considered consistently and the impact of each feature on the final risk score is explained in the output.
    
    Respond ONLY with JSON in the following format:
    
    {{
    "Loan Value": 10000000,
    "Collateral Value": 15000000,
    "Loan Tenure (Months)": 120,
    "Loan to Collateral Ratio": 0.666,
    "Credit Score": 750,
    "Risk Score": 20,
    "Explanation": "The company has strong profitability and moderate debt, leading to a good credit score and low risk."
    }}
"""

# 7) LLM call
def generate_synthetic(fin_dict):
    fin_json = json.dumps(fin_dict, indent=2)
    prompt = prompt_template.format(financials=fin_json)
    print(f"\n--- Prompt for row ---\n{prompt}")
    resp = client.chat.completions.create(
        model    = os.environ["AZURE_OPENAI_DEPLOYMENT"],
        messages = [
            {"role":"system", "content":"You generate synthetic loan & risk data."},
            {"role":"user",   "content":prompt}
        ],
        temperature=0.6,
        max_tokens = 800
    )
    raw = resp.choices[0].message.content
    print(f"[Raw response]\n{raw}")
    parsed = parse_json_response(raw)
    print(f"[Parsed JSON]\n{parsed}")
    return parsed

# 8) Loop & collect
synthetic_rows = []
for idx, row in features.iterrows():
    print(f"\n>>> Processing row {idx}")
    res = generate_synthetic(row.to_dict())
    if not res:
        print(f"⚠️ Row {idx} failed.")
        res = {
            "Loan Value": None,
            "Collateral Value": None,
            "Loan Tenure (Months)": None,
            "Loan to Collateral Ratio": None,
            "Credit Score": None,
            "Risk Score": None,
            "Explanation": "Generation failed.",
            "Feature Impact Weightage": {}
        }
    synthetic_rows.append(res)

# 9) Merge & save
syn_df = pd.DataFrame(synthetic_rows)
final = pd.concat([df5, syn_df], axis=1)
print("\n=== FINAL MERGED DF ===")
print(final)

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
final.to_excel(OUTPUT_PATH, index=False)
print(f"\n✅ Saved output to {OUTPUT_PATH}")
