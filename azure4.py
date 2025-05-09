import os
import json
import pandas as pd
from dotenv import load_dotenv
from openai import AzureOpenAI
import warnings
import re
import time
import io
from io import StringIO
from langchain.prompts import PromptTemplate
 
warnings.filterwarnings("ignore")
load_dotenv()
 
# 1) Azure OpenAI client setup
client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version=os.environ["API_VERSION_GA"],
)
print("AzureOpenAI client initialized")
 
# 2) Paths
INPUT_PATH = "output/Company_Financials_Cleaned.xlsx"
OUTPUT_PATH = "output/Company_Financials_Synthetic_First100"
 
# 3) Load first 100 rows
df_full = pd.read_excel(INPUT_PATH)
df_batch = df_full.iloc[:100].reset_index(drop=True)
print("\n=== INPUT (first 5 rows) ===")
print(df_batch.head())
 
# 4) Add synthetic columns with placeholders
new_columns = ["Loan Value", "Collateral Value", "Loan Tenure", "Credit Score", "Risk Score"]
for col in new_columns:
    df_batch[col] = pd.NA
 
# 5) Features passed to LLM (without dropped columns)
features = df_batch.drop(columns=["Company", "Industry", "Sector", "Financial Year",
                                  "Net Income Continuous Operations", "Total Revenue",
                                  "Stockholders Equity", "Total Assets", "Current Assets",
                                  "Current Liabilities", "Inventory", "Total Debt",
                                  "Interest Expense", "EBIT"], errors="ignore")

features_50 = features.iloc[0:50] 
features_100 = features.iloc[50:100] 
print()
#list_df = [features_50,features_100]
#str_df = features.to_string(index=False)
 
# 6) Prompt for LLM
prompt_template = """
You are a financial risk expert responsible for evaluating a company's loan risk based on their financial data. Your task is to generate a "Risk Score" that ranges from 0 to 100, where:

    - A Risk Score of 0 represents **minimum risk** and indicates a financially stable company.
    - A Risk Score of 100 represents **maximum risk** and indicates a financially unstable company.

    The lower the risk score, the safer the company is deemed to be for issuing a loan. The higher the risk score, the greater the likelihood that the company may default on the loan.

    ### Input Features to Consider:
    Below are the financial features provided. These features help assess the company's financial health, loan eligibility, and associated risk:

    1. Net Profit Margin (%):
        - This is the percentage of revenue that turns into profit.
        - Range: This ranges from negative (losses) to positive, with higher percentages being more favorable.
        - Impact on Risk: A higher profit margin means more efficiency, reducing risk.

    2. Return on Equity (ROE) (%):
        - This is the return generated on shareholders’ equity.
        - Range: This can range from negative values to very high positive values.
        - Impact on Risk: A high ROE indicates efficient use of equity and is associated with lower risk.

    3. Return on Assets (ROA) (%):
        - Measures how efficiently assets are used to generate profit.
        - Range: A higher positive percentage indicates better asset utilization.
        - Impact on Risk: High ROA reduces risk as it shows efficient use of assets.

    4. Asset Turnover Ratio:
        - This measures how effectively the company is using its assets to generate sales.
        - Range: Typically between 0 and 5, higher is better.
        - Impact on Risk: A higher ratio means better asset utilization and lower risk.

    5. Current Ratio:
        - This ratio compares a company’s current assets to its current liabilities.
        - Range: Ideal ratio is 1 or higher; anything less than 1 indicates potential liquidity issues.
        - Impact on Risk: Higher current ratios reduce the risk of defaulting on short-term obligations.

    6. Debt Equity Ratio:
        - A measure of the company’s financial leverage.
        - Range: A ratio greater than 1 indicates more debt than equity.
        - Impact on Risk: A higher debt-to-equity ratio increases financial risk.

    7. Debt To Asset Ratio:
        - This shows what proportion of a company’s assets are financed by debt.
        - Range: The ratio ranges from 0 (no debt) to 1 (100% of assets are financed by debt).
        - **Impact on Risk**: A higher ratio increases the company’s risk of default.

    8. Interest Coverage Ratio:
        - This measures the company’s ability to pay interest on its debt.
        - Range: A higher ratio (greater than 3) is favorable.
        - Impact on Risk: A higher ratio reduces risk as it shows the company can easily meet interest obligations.

    ### Calculating the Risk Score:
    Your risk score should be based on the combined analysis of all the above features. The higher the values of indicators like current ratio,Incterest coverage ratio, Net Profit Margin, ROE, ROA, Asset Turnover ratios the lower the risk score will be.
    
    Conversely, Total Debt, Current Liabilities, Interest Expense, Debt-to-Equity, and Debt-to-Asset ratios are negative indicators and their high values will increase the risk score.
    
    For each company row, ensure that all features are considered consistently and the impact of each feature on the final risk score is explained in the output.

    ### Final Instructions:
    Generate the loan and risk details based on these features. 
    The loan value should be realistic (₹1000000 to ₹500000000), 
    collateral should be at realistic (₹1000000 to ₹550000000), 
    loan tenure should be realistic (6 to 240 months)
    credit score to be realistic between (300 to 900)
    risk score to be realistic (0-100)

    There should be variation in data. For Example, 
    where the colalteral value is greter than the loan value, the risk score will be 0-10 and vice versa
    if the loan amount is very less than the Total Revenue and Total Assest - risk score will be 0-10 and vice versa
    So give data simiar to these use cases across the features and range.
 
### Instructions:
- Output only the new columns in the same order: Loan Value | Collateral Value | Loan Tenure | Credit Score | Risk Score
- Use ‘|’ as the separator.
- Do not repeat values across rows.
- No additional explanation or commentary. Just the data table.
- understand the range, there are multiple batches, remember what output you have given to previous and try not to give same output.
Example Format:
Loan Value|Collateral Value|Loan Tenure|Credit Score|Risk Score
50000000|70000000|120|850|8
70000000|50000000|60|400|90
...
 
Here is the dataset for which you must generate the above synthetic columns:
{str_df}
"""
 
# 7) Call Azure OpenAI
list_df = [features_50,features_100]
#str_df = features.to_string(index=False)
i = 0
for single_df in list_df:
    str_df = single_df.to_string(index=False)
    temp_prompt=PromptTemplate(input_variables=["str_df"],template =prompt_template)
    final_prompt = temp_prompt.format(str_df=str_df)
    resp = client.chat.completions.create(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        messages=[
            {"role": "system", "content": "You generate synthetic loan and risk data."},
            {"role": "user", "content": final_prompt}
        ],
        temperature=0.6,
        max_tokens=2500  # You may increase this if needed
    )
    raw = resp.choices[0].message.content.strip()
    print(f"[Raw response]\n{raw[:1000]}...")  # Preview first 1000 characters
 
    # 8) Convert raw LLM output to DataFrame
    def string_to_dataframe(raw_string, delimiter='|'):
        data = io.StringIO(raw_string)
        df = pd.read_csv(data, delimiter=delimiter)
        df.columns = [col.strip().title() for col in df.columns]
        return df
 
    df_synthetic = string_to_dataframe(raw)
 
    # 9) Merge synthetic values back
    for col in new_columns:
        df_batch[col] = df_synthetic[col].astype(str).str.replace(",", "").astype(float)
    
    # 10) Save to Excel
    i+=1
    df_batch.to_excel(OUTPUT_PATH+str(i)+'.xlsx', index=False)
    print(f"Output saved to {OUTPUT_PATH}")
    time.sleep(5)