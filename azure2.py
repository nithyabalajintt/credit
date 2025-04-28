prompt_template = """
You are a financial risk expert responsible for evaluating a company's loan risk based on their financial data. Your task is to generate unique synthetic financial data for each company, including:

    - A **Risk Score** that ranges from 0 to 100, where:
        - A **Risk Score of 0** represents **minimum risk** and indicates a financially stable company.
        - A **Risk Score of 100** represents **maximum risk** and indicates a financially unstable company.

    The higher the risk score, the greater the likelihood that the company may default on the loan.

    ### Input Features to Consider:
    Below are the financial features provided. These features help assess the company's financial health, loan eligibility, and associated risk:

    1. **Net Income Continuous Operations**: 
        - A higher value indicates profitability and financial health.
        - **Impact on Risk**: Higher values reduce risk.

    2. **Total Revenue**:
        - A higher revenue suggests strong operations, reducing risk.

    3. **Stockholders' Equity**:
        - A higher equity reduces risk, indicating financial strength.

    4. **Total Debt**:
        - Higher debt increases the risk of default.

    5. **Current Liabilities**:
        - Higher current liabilities suggest potential liquidity issues, increasing risk.

    6. **EBIT**:
        - A higher EBIT usually lowers risk due to strong earnings performance.

    7. **Current Assets**:
        - More current assets reduce the risk by helping manage short-term obligations.

    8. **Total Assets**:
        - A higher value in assets generally reduces risk.

    9. **Net Profit Margin (%)**:
        - A higher profit margin reduces risk.

    10. **Return on Equity (ROE) (%)**:
        - High ROE reduces risk due to efficient use of equity.

    11. **Return on Assets (ROA) (%)**:
        - A high ROA reduces risk as it shows efficient use of assets.

    12. **Asset Turnover Ratio**:
        - A higher ratio indicates better asset utilization and reduces risk.

    13. **Current Ratio**:
        - A higher current ratio reduces the risk of defaulting on short-term obligations.

    14. **Interest Expense**:
        - Higher interest expenses increase risk due to debt servicing costs.

    15. **Debt Equity Ratio**:
        - A higher ratio increases financial risk.

    16. **Debt To Asset Ratio**:
        - A higher ratio increases the company’s risk of default.

    17. **Interest Coverage Ratio**:
        - A higher ratio reduces risk by ensuring the company can meet interest payments.

    ### Calculating the Risk Score:
    The higher the values of indicators like **Net Income**, **Revenue**, **Stockholders' Equity**, **EBIT**, **Net Profit Margin**, **ROE**, and **ROA**, the lower the risk score will be.
    Conversely, **Total Debt**, **Current Liabilities**, **Interest Expense**, **Debt-to-Equity**, and **Debt-to-Asset ratios** are negative indicators that increase the risk score.

    ### Unique Loan and Risk Data:
    Based on the financial features of each company, generate the following synthetic financial data:

    1. **Loan Value**: A realistic loan value ranging from ₹10,00,000 to ₹50 Crore.
    2. **Collateral Value**: A realistic collateral value ranging from ₹10,00,000 to ₹55 Crore.
    3. **Loan Tenure**: A loan tenure between 6 to 240 months.
    4. **Loan to Collateral Ratio**: The ratio of Loan Value to Collateral Value.
    5. **Credit Score**: A realistic credit score ranging from 300 to 850.
    6. **Risk Score**: A risk score between 0 and 100, reflecting the company's loan risk.
    7. **Explanation**: An explanation of how the financial data impacts the loan and risk scores.

    Ensure the values for each company are distinct, based on the financial data provided for each company. The features will vary between companies, so generate different values for each row based on the provided information.

    ### Response Format:
    Respond ONLY with JSON in the following format:
    {
        "Loan Value": 10000000,
        "Collateral Value": 15000000,
        "Loan Tenure (Months)": 120,
        "Loan to Collateral Ratio": 0.666,
        "Credit Score": 750,
        "Risk Score": 20,
        "Explanation": "The company has strong profitability and moderate debt, leading to a good credit score and low risk."
    }
"""
