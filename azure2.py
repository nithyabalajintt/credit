import random

# Function to simulate company financial data with varying risk and loan characteristics
def generate_company_data(num_rows=50):
    company_data = []
    
    for _ in range(num_rows):
        # Randomly simulate financial data for each company
        total_assets = random.randint(10_000_000, 100_000_000)  # Total assets between ₹1 Cr and ₹100 Cr
        net_income = random.randint(-50_000_000, 50_000_000)  # Net income could be negative or positive
        equity = random.randint(5_000_000, 50_000_000)  # Stockholders' equity between ₹50 Lakhs and ₹5 Cr
        total_debt = random.randint(1_000_000, 30_000_000)  # Debt between ₹10 Lakhs and ₹3 Cr
        current_liabilities = random.randint(500_000, 15_000_000)  # Current liabilities from ₹5 Lakhs to ₹1.5 Cr
        EBIT = random.randint(-10_000_000, 30_000_000)  # EBIT from -₹1 Cr to ₹3 Cr
        current_assets = random.randint(2_000_000, 15_000_000)  # Current assets from ₹20 Lakhs to ₹1.5 Cr
        net_profit_margin = random.uniform(-5, 20)  # Profit margin between -5% to 20%
        return_on_equity = random.uniform(-5, 25)  # ROE between -5% to 25%
        return_on_assets = random.uniform(-5, 20)  # ROA between -5% to 20%
        asset_turnover_ratio = random.uniform(0, 5)  # Asset turnover between 0 and 5
        current_ratio = random.uniform(0.5, 3)  # Current ratio between 0.5 and 3
        interest_expense = random.randint(100_000, 5_000_000)  # Interest expense between ₹1 Lakh and ₹50 Lakhs
        debt_equity_ratio = random.uniform(0.5, 3)  # Debt to equity ratio between 0.5 and 3
        debt_to_asset_ratio = random.uniform(0.2, 0.9)  # Debt to asset ratio between 0.2 and 0.9
        interest_coverage_ratio = random.uniform(1, 6)  # Interest coverage ratio between 1 and 6
        
        # Calculate Risk Score (based on an inverse relation to financial health)
        risk_score = 0
        if net_income < 0: risk_score += 20  # Net income loss increases risk
        if total_debt > 20_000_000: risk_score += 15  # High debt increases risk
        if equity < 10_000_000: risk_score += 15  # Low equity increases risk
        if current_liabilities > current_assets: risk_score += 10  # Liquidity issue increases risk
        if EBIT < 0: risk_score += 10  # Negative EBIT increases risk
        if net_profit_margin < 0: risk_score += 5  # Negative profit margin increases risk
        
        # Simulate loan value, collateral value, and loan tenure
        loan_value = min(50000000, max(1000000, total_assets * 0.1 + net_income * 0.03))
        collateral_value = min(55000000, max(1000000, equity * 0.8))
        loan_tenure = random.randint(12, 240)  # Loan tenure between 1 to 20 years
        
        # Loan to Collateral ratio
        loan_to_collateral_ratio = loan_value / collateral_value
        
        # Credit score (inversely related to risk score)
        credit_score = max(300, 800 - risk_score)
        
        # Explanation for risk score
        explanation = f"Risk score is based on financial health. Net income: {net_income}, Debt: {total_debt}, Equity: {equity}, Liquidity: {current_liabilities - current_assets}, Profit margin: {net_profit_margin}%"
        
        # Create the company row with generated values
        company_data.append({
            "Loan Value": loan_value,
            "Collateral Value": collateral_value,
            "Loan Tenure (Months)": loan_tenure,
            "Loan to Collateral Ratio": round(loan_to_collateral_ratio, 3),
            "Credit Score": credit_score,
            "Risk Score": risk_score,
            "Explanation": explanation
        })
    
    return company_data

# Generate 50 rows of simulated company data
company_data = generate_company_data(num_rows=50)

# Print the generated data for verification
for company in company_data:
    print(company)
