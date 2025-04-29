import os
import json
import pandas as pd
from dotenv import load_dotenv
from openai import AzureOpenAI
import warnings
import re
import io
from io import StringIO

warnings.filterwarnings("ignore")
load_dotenv()


# 1) Azure OpenAI client setup
client = AzureOpenAI(
    azure_endpoint   = os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"],
    api_key          = os.environ["AZURE_OPENAI_API_KEY"],
    api_version      = os.environ["API_VERSION_GA"],
)
print(" AzureOpenAI client initialized")

# 2) Paths
INPUT_PATH  = "output/Company_Financials_Cleaned.xlsx"
OUTPUT_PATH = "output/Company_Financials_Synthetic_First5.xlsx"

# 3) Load first 5 rows
df_full = pd.read_excel(INPUT_PATH)
df5     = df_full.iloc[:100].reset_index(drop=True)
print("\n=== INPUT (first 5 rows) ===")
print(df5)

# 4) Prepare features
new_columns = ["Loan Value", "Collateral Value", "Loan Tenure", "Credit Score", "Risk Score"]
for col in new_columns:
    df5[col] = pd.NA
features = df5.drop(columns=["Company","Industry","Sector","Financial Year","Net Income Continuous Operations", 
                             "Total Revenue", "Stockholders Equity", "Total Assets", "Current Assets", 
                             "Current Liabilities", "Inventory", "Total Debt","Interest Expense","EBIT"], errors="ignore")

print(features)

str_df = features.to_string()



# 6) Prompt
prompt_template = f"""
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
    
    Can you fill in the blanks for the required columns by introducing variations in the values. 
    Please fill the blank values in this dataframe: {str_df}

    There should be variation in data. For Example, 
    where the colalteral value is greter than the loan value, the risk score will be 0-10 and vice versa
    if the loan amount is very less than the Total Revenue and Total Assest - risk score will be 0-10 and vice versa
    So give data simiar to these use cases across the features and range.

    Separate the column names by '|'  
    dont give additional commentary, only give the columns and the numerical values
    create a table with columns and their respective values that can be saved in a csv file.
   
""".format(str_df=str_df)

resp = client.chat.completions.create(
        model    = os.environ["AZURE_OPENAI_DEPLOYMENT"],
        messages = [
            {"role":"system", "content":"You generate synthetic loan & risk data."},
            {"role":"user",   "content":prompt_template}
        ],
        temperature=0.6,
        max_tokens = 800
    )
raw = resp.choices[0].message.content
print(f"[Raw response]\n{raw}")

cols=list(features.columns)
def string_to_dataframe(raw, delimiter='|', names=cols):

    """

    Converts a string to a Pandas DataFrame.
 
    Args:

        data_string (str): The string data.

        delimiter (str, optional): The delimiter separating values. Defaults to '|'.

        header (list, optional): List of column names. If None, it infers from the first row or assigns default integer indices.
 
    Returns:

        pd.DataFrame: The resulting DataFrame.

    """

    data = io.StringIO(raw)
    print(data)
    print(list(features.columns))
   
    df = pd.read_csv(data,names=cols)

    return df
    
# 9) Convert synthetic data to DataFrame using string_to_dataframe function
df_synthetic = string_to_dataframe(raw)  
 
# Save updated dataframe to Excel
df_synthetic.to_excel(OUTPUT_PATH, index=False)  # Saving the DataFrame to Excel
print(f"Output saved to {OUTPUT_PATH}")
 

