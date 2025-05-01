import os
import time
import pandas as pd
import Other.scrape_financial_data as yf

# Load the CSV files for both Equity and SME tickers
equity_file_path = "equity_tickers.csv"
sme_file_path = "sme_tickers.csv"

# Load the equity and SME tickers into pandas DataFrames
equity_df = pd.read_csv(equity_file_path)
sme_df = pd.read_csv(sme_file_path)

# Check the available columns for both DataFrames
print(f"Available columns in equity CSV: {equity_df.columns}")
print(f"Available columns in SME CSV: {sme_df.columns}")

# Extract the tickers for both, assuming the column is named 'SYMBOL'
equity_tickers = equity_df['SYMBOL'].dropna().unique().tolist()
sme_tickers = sme_df['SYMBOL'].dropna().unique().tolist()

# Combine both lists of tickers
all_tickers = equity_tickers + sme_tickers
all_tickers = [ticker.strip().upper() + ".NS" for ticker in all_tickers]  # Add '.NS' suffix for NSE

# Output folder to save financials
out_dir = "Financials"
os.makedirs(out_dir, exist_ok=True)

# Loop through all tickers and fetch their financial data
for ticker in all_tickers:
    print(f"Processing {ticker} ...", end=" ")
    stock = yf.Ticker(ticker)
    
    # Fetch financial data
    bs = stock.balance_sheet
    is_ = stock.income_stmt
    cf = stock.cash_flow

    # Skip tickers with no financial data
    if bs.empty and is_.empty and cf.empty:
        print("No financials data")
        continue

    # Save to Excel file
    path = os.path.join(out_dir, f"{ticker}_financials.xlsx")
    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        if not bs.empty:
            bs.to_excel(writer, sheet_name="Balance Sheet")
        if not is_.empty:
            is_.to_excel(writer, sheet_name="Income Statement")
        if not cf.empty:
            cf.to_excel(writer, sheet_name="Cash Flow Statement")
    print("Saved")
    
    # Delay to avoid hitting API rate limits
    time.sleep(1)

print("All financials have been saved in the 'Financials' folder.")
