import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 設定 ---
# スプレッドシートのURL（フェーズ1-1で控えたものに書き換えてください）
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/xxxxxxxx/edit"

CAPTIONS = [
    "伝票番号",
    "塩やきそば",
    "塩焼きそば+たまご",
    "ソース焼きそば",
    "ソース焼きそば+たまご",
    "ラムネ"
]

# --- ページ設定 ---
st.set_page_config(page_title="焼きそば注文入力", layout="centered")
st.title("🍜 焼きそば注文入力")

# --- データベース接続 ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("データベース接続設定が見つかりません。")
    st.stop()

# --- データ保存関数 ---
def save_data(new_data):
    try:
        # 既存データを読み込む
        df = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
        
        # 新しい行を作成して結合
        new_row = pd.DataFrame([new_data], columns=CAPTIONS)
        updated_df = pd.concat([df, new_row], ignore_index=True)
        
        # 保存（更新）
        conn.update(spreadsheet=SPREADSHEET_URL, data=updated_df)
        return True
    except Exception as e:
        st.error(f"保存エラー: {e}")
        return False

# --- 入力フォーム ---
with st.form(key='order_form', clear_on_submit=True):
    inputs = []
    
    # 伝票番号（数値入力）
    inputs.append(st.number_input(CAPTIONS[0], min_value=0, step=1, value=0, format="%d"))
    
    # 商品（数値入力）
    for i in range(1, 6):
        inputs.append(st.number_input(CAPTIONS[i], min_value=0, step=1, value=0, format="%d"))

    submit_btn = st.form_submit_button("注文を確定する")

    if submit_btn:
        # バリデーション: 伝票番号が0の場合は警告など
        if inputs[0] == 0:
            st.warning("⚠️ 伝票番号を入力してください。")
        else:
            if save_data(inputs):
                st.success(f"✅ 伝票番号 {inputs[0]} を記録しました！")
                st.cache_data.clear() # キャッシュクリア

# --- データ確認用（オプション） ---
with st.expander("現在のデータを確認する"):
    try:
        df_display = conn.read(spreadsheet=SPREADSHEET_URL, ttl=5)
        st.dataframe(df_display.style.format(precision=0))
    except:
        st.write("データ読み込み中...")