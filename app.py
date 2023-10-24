import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt
import pandas_datareader as pdr
from datetime import datetime, timedelta
import matplotlib.dates as mdates

# Streamlit UI
st.title('Stock Price App')

# Sidebar: User Input
selected_stock = st.sidebar.text_input("Enter stock symbols (comma separated):", "AAPL,MSFT,GOOGL,AMZN,META,TSLA,NVDA,NFLX,ARM")
time_frame = st.sidebar.selectbox("Select Time Frame", ["1d", "1wk", "1mo"])
period = st.sidebar.selectbox("Select Period", ["3M", "6M", "1Y", "3Y", "5Y", "10Y"])
moving_averages = st.sidebar.multiselect("Select Moving Averages", ["5D", "25D", "75D", "200D"])
display_mode = st.sidebar.selectbox("Select Display Mode", ["Single", "Multiple"])

# Get Data & Plotting
symbols = selected_stock.split(',')

# Period to datetime mapping
period_mapping = {
    "3M": timedelta(days=90),
    "6M": timedelta(days=180),
    "1Y": timedelta(days=365),
    "3Y": timedelta(days=3*365),
    "5Y": timedelta(days=5*365),
    "10Y": timedelta(days=10*365),
}

def plot_chart(ax, symbol, period, time_frame, moving_averages):
    try:
        if symbol.endswith('.JP'):
            df = pdr.stooq.StooqDailyReader(symbols=symbol, start=datetime.now()-period_mapping[period]).read()
        else:
            df = yf.download(symbol, start=datetime.now()-period_mapping[period], interval=time_frame)

        ax.plot(df['Close'], label=symbol)
        ax.set_title(symbol, fontsize=14)
        ax.legend(loc='upper left')
        ax.get_xaxis().set_visible(True)
        
        if period in ["3M", "6M"]:
            ax.xaxis.set_major_locator(mdates.MonthLocator())
        elif period == "1Y":
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        elif period == "10Y":
            ax.xaxis.set_major_locator(mdates.YearLocator())
        else:
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%y-%m-%d'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        for ma in moving_averages:
            df[ma] = df['Close'].rolling(window=int(ma[:-1])).mean()
            ax.plot(df[ma], label=f"{ma} MA")
        
        ax2 = ax.twinx()
        ax2.fill_between(df.index, df['Volume'], alpha=0.1, label='Volume')
        ax2.legend(loc='upper right')
        ax2.get_yaxis().set_visible(False)
        
        st.sidebar.text(f"Loaded: {symbol}")
    except Exception as e:
        st.sidebar.text(f"Error: {symbol} - {str(e)}")


if display_mode == "Single":
    symbol = st.sidebar.selectbox("Select a symbol to display", symbols)
    symbol = symbol.strip().upper()

    fig, ax1 = plt.subplots(figsize=(12, 6))
    plot_chart(ax1, symbol, period, time_frame, moving_averages)
    plt.tight_layout()
    st.pyplot(fig)
else:
    if len(symbols) > 9:
        st.sidebar.text("Please enter up to 9 symbols only.")
    else:
        fig, axs = plt.subplots(3, 3, figsize=(18, 12))
        fig.suptitle('Stock Prices and Volume', fontsize=20)
        axs = axs.flatten()

        for i, symbol in enumerate(symbols):
            symbol = symbol.strip().upper()
            plot_chart(axs[i], symbol, period, time_frame, moving_averages)

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        st.pyplot(fig)

    st.sidebar.text("Note: Add '.JP' for Japanese stocks.")
