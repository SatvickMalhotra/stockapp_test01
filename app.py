import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# Initialize session state to store transactions
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# App title
st.title("Stock Portfolio Tracker 📈")

# Input form for transactions
with st.form("transaction_form"):
    ticker = st.text_input("Stock Ticker (e.g., AAPL)", placeholder="AAPL").upper()
    action = st.selectbox("Action", ["Buy", "Sell"])
    shares = st.number_input("Shares", min_value=0.1, step=0.1)
    price = st.number_input("Price per Share ($)", min_value=0.01)
    date = st.date_input("Transaction Date")
    submitted = st.form_submit_button("Add Transaction")

    if submitted:
        st.session_state.transactions.append({
            "Ticker": ticker,
            "Action": action,
            "Shares": shares,
            "Price": price,
            "Date": date.strftime("%Y-%m-%d")
        })

# Display transactions
st.subheader("Your Transactions")
if st.session_state.transactions:
    df_transactions = pd.DataFrame(st.session_state.transactions)
    st.dataframe(df_transactions)
else:
    st.write("No transactions yet.")

# Calculate P&L and portfolio value
if st.button("Calculate Portfolio"):
    portfolio = {}
    for transaction in st.session_state.transactions:
        ticker = transaction["Ticker"]
        if ticker not in portfolio:
            portfolio[ticker] = {"Shares": 0, "Cost": 0.0}
        
        if transaction["Action"] == "Buy":
            portfolio[ticker]["Shares"] += transaction["Shares"]
            portfolio[ticker]["Cost"] += transaction["Shares"] * transaction["Price"]
        else:
            portfolio[ticker]["Shares"] -= transaction["Shares"]
            portfolio[ticker]["Cost"] -= transaction["Shares"] * transaction["Price"]

    # Fetch live prices
    current_prices = {}
    for ticker in portfolio.keys():
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        current_prices[ticker] = hist["Close"].iloc[-1] if not hist.empty else 0.0

    # Generate portfolio summary
    df_portfolio = pd.DataFrame({
        "Ticker": portfolio.keys(),
        "Shares": [v["Shares"] for v in portfolio.values()],
        "Avg Cost": [v["Cost"] / v["Shares"] if v["Shares"] != 0 else 0 for v in portfolio.values()],
        "Current Price": [current_prices[ticker] for ticker in portfolio.keys()],
        "Market Value": [current_prices[ticker] * v["Shares"] for ticker, v in portfolio.items()]
    })
    df_portfolio["P&L"] = df_portfolio["Market Value"] - df_portfolio["Avg Cost"] * df_portfolio["Shares"]
    
    st.subheader("Portfolio Summary")
    st.dataframe(df_portfolio)

    # Visualize performance
    st.line_chart(df_portfolio.set_index("Ticker")["Market Value"])
else:
    st.info("Click to calculate your portfolio performance.")
