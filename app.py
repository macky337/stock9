import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt
import pandas_datareader as pdr
from datetime import datetime, timedelta
import matplotlib.font_manager as fm

# 新しいフォントを指定
font_path = r'C:\Users\user\AppData\Local\Microsoft\Windows\Fonts\ipaexg.ttf'  # フォントファイルへのパス
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = 'Meiryo'

# Streamlit UI
st.title('Stock9_Chart')

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

        # 整数インデックス列を追加
        df.reset_index(inplace=True)
        df['IntIndex'] = df.index    

        # 終値を描画
        ax.plot(df['IntIndex'], df['Close'], label='終値')

        # X軸のラベルを日付に設定
        ax.set_xticks(df['IntIndex'][::len(df)//10])  # X軸のラベル数を調整
        ax.set_xticklabels([date.strftime('%Y-%m-%d') for date in df['Date'][::len(df)//10]], rotation=45)

        # 出来高をプロットするための新しい軸を作成
        ax2 = ax.twinx()
        ax2.bar(df.index, df['Volume'], alpha=0.3, color='grey')
        ax2.set_ylabel('Volume')
        ax2.grid(False)

        # 移動平均の計算と描画
        for ma in moving_averages:
            if len(df) >= int(ma[:-1]):  # データが十分にあるか確認
                df['MA' + ma] = df['Close'].rolling(window=int(ma[:-1])).mean()
                ax.plot(df['MA' + ma], label=f'{ma} 移動平均')

        ax.legend(loc='upper left')

        # タイトルに銘柄名と終値を表示（フォントサイズを3倍に設定）
        last_close = df['Close'].iloc[-1] if not df.empty else 0
        ax.set_title(f"{symbol} - 終値: {last_close:.2f}", fontsize=30)  # または必要に応じて fontsize=36 に設定


    except Exception as e:
        st.sidebar.text(f"エラー: {symbol} - {str(e)}")

# シングル表示モードの場合のフィギュアサイズを調整
if display_mode == "Single":
    symbol = st.sidebar.selectbox("銘柄を選択", symbols)
    fig, ax1 = plt.subplots(figsize=(30, 15))  # 幅と高さを大きく設定
    plot_chart(ax1, symbol, period, time_frame, moving_averages)
    st.pyplot(fig)

# マルチプル表示モードの場合のフィギュアサイズを調整
else:
    fig, axs = plt.subplots(3, 3, figsize=(40, 24))  # 幅と高さを大きく設定
    fig.suptitle('株価とボリューム', fontsize=20)
    axs = axs.flatten()

    for i, symbol in enumerate(symbols):
        if i < 9:  # 最大9つのチャートを表示
            plot_chart(axs[i], symbol, period, time_frame, moving_averages)
        else:
            axs[i].set_visible(False)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    st.pyplot(fig)

