import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt
import pandas_datareader as pdr
from datetime import datetime, timedelta
import matplotlib.dates as mdates

# Streamlit UI
st.title('stock9_chart')

# サイドバー: ユーザー入力
selected_stock = st.sidebar.text_input("銘柄をカンマ区切りで入力してください（例: AAPL,MSFT,GOOGL,AMZN,META,TSLA,NVDA,CRWD,ARM）", "AAPL,MSFT,GOOGL,AMZN,META,TSLA,NVDA,CRWD,ARM")
time_frame = st.sidebar.selectbox("タイムフレームを選択", ["1d", "1wk", "1mo"])
period = st.sidebar.selectbox("期間を選択", ["3M", "6M", "1Y", "3Y", "5Y", "10Y"])
moving_averages = st.sidebar.multiselect("移動平均を選択", ["5D", "25D", "75D", "200D"])
display_mode = st.sidebar.selectbox("表示モードを選択", ["Single", "Multiple"])

# データ取得 & プロット
symbols = selected_stock.split(',')

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

        ax.plot(df['Close'], label='終値')

        # 最終終値とその日付を取得
        last_date = df.index[-1]
        last_close = df['Close'].iloc[-1]

        # 前日の終値を取得
        if len(df) > 1:
            previous_close = df['Close'].iloc[-2]
        else:
            previous_close = last_close

        # 前日比を計算
        change = last_close - previous_close
        percent_change = (change / previous_close) * 100 if previous_close != 0 else 0

        # 移動平均の計算と描画
        for ma in moving_averages:
            if len(df) >= int(ma[:-1]):  # データが十分にあるか確認
                df['MA' + ma] = df['Close'].rolling(window=int(ma[:-1])).mean()
                ax.plot(df['MA' + ma], label=f'{ma} 移動平均')

        # 終値と前日比を注釈としてチャートに表示
        ax.annotate(f'{last_close:.2f}\n({change:+.2f}, {percent_change:+.2f}%)',
                    xy=(last_date, last_close),
                    xytext=(15, 0),
                    textcoords='offset points',
                    arrowprops=dict(arrowstyle='->'),
                    horizontalalignment='right',
                    verticalalignment='bottom',
                    fontsize=8)

        # タイトルに終値と前日比を追加
        ax.set_title(f"{symbol} {last_close:.2f} ({change:+.2f}, {percent_change:+.2f}%)", fontsize=14)
        ax.legend(loc='upper left')
        ax.get_xaxis().set_visible(True)

        # X軸の日付フォーマットを設定
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

    except Exception as e:
        st.sidebar.text(f"エラー: {symbol} - {str(e)}")


if display_mode == "Single":
    # インデントされたコードブロック
    # 例えば、シングル表示モード用の処理
    symbol = st.sidebar.selectbox("銘柄を選択", symbols)
    symbol = symbol.strip().upper()

    fig, ax1 = plt.subplots(figsize=(12, 6))
    plot_chart(ax1, symbol, period, time_frame, moving_averages)
    plt.tight_layout()
    st.pyplot(fig)
else:
    # インデントされたコードブロック
    # 例えば、マルチプル表示モード用の処理
    fig, axs = plt.subplots(3, 3, figsize=(18, 12))
    fig.suptitle('株価とボリューム', fontsize=20)
    axs = axs.flatten()

    # 各銘柄のチャートをプロットする処理
    for i, symbol in enumerate(symbols):
        symbol = symbol.strip().upper()
        plot_chart(axs[i], symbol, period, time_frame, moving_averages)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    st.pyplot(fig)
