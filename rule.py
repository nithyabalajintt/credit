import yfinance as yf
import requests
from rule_decision import rule_function  # Your actual scoring logic
 
# Step 1: Get ticker from company name
import requests
 
def search_ticker_by_company_name(company_name):
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={company_name}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        results = response.json().get("quotes", [])
        
        for result in results:
            if result.get("quoteType") in ["EQUITY", "ETF"] and "symbol" in result:
                return result["symbol"]
        return None
    except Exception as e:
        print(f"Error fetching ticker for '{company_name}': {e}")
        return None
  
# Step 2: Fetch FY2024 data from yfinance
def fetch_fy2024_financial_data(ticker_symbol, loan_value, collateral_value, credit_score):
    ticker = yf.Ticker(ticker_symbol)
    income_stmt = ticker.financials.T
    balance_sheet = ticker.balance_sheet.T
 
    fy_2024 = None
    for idx in income_stmt.index:
        if "2024" in str(idx):
            fy_2024 = idx
            break
    if fy_2024 is None:
        return None
 
    def safe_div(numerator, denominator):
        try:
            return numerator / denominator
        except (KeyError, TypeError, ZeroDivisionError):
            return None
 
    data = {
        "Net Profit Margin %": safe_div(income_stmt.loc[fy_2024].get('Net Income'), income_stmt.loc[fy_2024].get('Total Revenue')) * 100 if income_stmt.loc[fy_2024].get('Total Revenue') else None,
        "Return on Equity %": safe_div(income_stmt.loc[fy_2024].get('Net Income'), balance_sheet.loc[fy_2024].get('Total Stockholder Equity')) * 100,
        "Return on Assets %": safe_div(income_stmt.loc[fy_2024].get('Net Income'), balance_sheet.loc[fy_2024].get('Total Assets')) * 100,
        "Current Ratio": safe_div(balance_sheet.loc[fy_2024].get('Total Current Assets'), balance_sheet.loc[fy_2024].get('Total Current Liabilities')),
        "Asset Turnover Ratio": safe_div(income_stmt.loc[fy_2024].get('Total Revenue'), balance_sheet.loc[fy_2024].get('Total Assets')),
        "Debt Equity Ratio": safe_div(balance_sheet.loc[fy_2024].get('Total Liab'), balance_sheet.loc[fy_2024].get('Total Stockholder Equity')),
        "Debt To Asset Ratio": safe_div(balance_sheet.loc[fy_2024].get('Total Liab'), balance_sheet.loc[fy_2024].get('Total Assets')),
        "Interest Coverage Ratio": safe_div(income_stmt.loc[fy_2024].get('EBIT'), income_stmt.loc[fy_2024].get('Interest Expense')),
        "Loan Value": loan_value,
        "Collateral Value": collateral_value,
        "Credit Score": credit_score
    }
 
    return data
 
# Step 3: Master evaluation function
def evaluate_company_risk(company_name, loan_value, collateral_value, credit_score):
    ticker = search_ticker_by_company_name(company_name)
    if not ticker:
        print(f"Ticker not found for company: {company_name}")
        return
 
    print(f"\nCompany: {company_name} | Ticker: {ticker}")
    data = fetch_fy2024_financial_data(ticker, loan_value, collateral_value, credit_score)
    if not data:
        print("FY2024 financial data not found.")
        return
 
    risk_score = rule_function(data)
    print(f"Final Risk Score: {risk_score}")
 
# Step 4: Main function for CLI use
if __name__ == "__main__":
    company = input("Enter company name: ")
    loan = float(input("Enter loan value: "))
    collateral = float(input("Enter collateral value: "))
    credit = int(input("Enter credit score: "))
 
    evaluate_company_risk(company, loan, collateral, credit)
 
