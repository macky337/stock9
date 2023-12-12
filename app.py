import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt
import pandas_datareader as pdr
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import matplotlib.font_manager as fm


# 新しいフォントを指定
font_path = r'C:\Users\user\AppData\Local\Microsoft\Windows\Fonts\ipaexg.ttf'  # フォントファイルへのパス
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = 'Meiryo'


# Streamlit UI
st.title('stock9_chart')

# サイドバー: ユーザー入力
selected_stock = st.sidebar.text_input("銘柄ティッカーを入力してください", "AAPL,GOOG,META,AMZN,ARM,AMD,INTC,CRWD,NVDA")
time_frame = st.sidebar.selectbox("タイムフレームを選択", ["1d", "1wk", "1mo"])
period = st.sidebar.selectbox("期間を選択", ["3M", "6M", "1Y", "3Y", "5Y", "10Y"])
moving_averages = st.sidebar.multiselect("移動平均を選択", ["5D", "25D", "75D", "200D"])
display_mode = st.sidebar.selectbox("表示モードを選択", ["Single", "Multiple"])

# ユーザーの入力から銘柄リストを作成
symbols = [s.strip().upper() for s in selected_stock.split(',')]

# 期間をdatetimeに変換
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

        # 終値を取得
        last_close = df['Close'].iloc[-1]

        ax.plot(df['Close'], label='終値')

        # 出来高をプロットするための新しい軸を作成
        ax2 = ax.twinx()
        ax2.bar(df.index, df['Volume'], alpha=0.3, color='grey')
        ax2.set_ylabel('Volume')
        ax2.grid(False)

        # タイトルに銘柄名と終値を表示
        ax.set_title(f"{symbol} - 終値: {last_close:.2f}")

        # ... (残りのプロットロジック)

    except Exception as e:
        st.sidebar.text(f"エラー: {symbol} - {str(e)}")

if display_mode == "Single":
    symbol = st.sidebar.selectbox("銘柄を選択", symbols)
    fig, ax1 = plt.subplots(figsize=(20, 10))
    plot_chart(ax1, symbol, period, time_frame, moving_averages)
    plt.tight_layout()
    st.pyplot(fig)
else:
    fig, axs = plt.subplots(3, 3, figsize=(24, 15))  # 3x3のグリッドでサブプロットを作成
    fig.suptitle('株価とボリューム', fontsize=20)
    axs = axs.flatten()

    for i, symbol in enumerate(symbols):
        if i < 9:  # 最大9つのチャートを表示
            plot_chart(axs[i], symbol, period, time_frame, moving_averages)
        else:
            axs[i].set_visible(False)  # 9つ以上のチャートは表示しない

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    st.pyplot(fig)
