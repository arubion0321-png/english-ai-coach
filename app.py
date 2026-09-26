import streamlit as st
import re
import time
from google import genai
from google.genai import types

# 画面設定
st.set_page_config(page_title="英語スピーチ AIコーチ", page_icon="📝")
st.title("📝 英語スピーチ AIコーチ")
st.write("テーマの相談から英文のヒント添削まで、AIコーチと一緒にスピーチを作ろう！")

# SecretsからAPIキーを取得
raw_api_key = st.secrets.get("GEMINI_API_KEY", "")

# キーから非ASCII文字（全角スペース等）を物理的に除去
clean_api_key = re.sub(r'[^\x00-\x7F]+', '', str(raw_api_key)).strip()

if not clean_api_key:
    st.error("APIキー（GEMINI_API_KEY）が正しく読み込めません。Secretsを確認してください。")
    st.stop()

# 安全なキーでクライアントを初期化
client = genai.Client(api_key=clean_api_key)

system_instruction = """
あなたは中学校の英語学習をサポートする優しく熱心なAIコーチです。

【役割とルール】
1. 生徒からの質問（テーマ決め、構成、作文添削）に親身に応答してください。
2. 構成や表現を聞かれた場合は「3つの異なるアプローチ」の選択肢と、中2文法の簡単な解説を提示してください。
3. 作文添削では絶対に正解の全文を与えず、ヒントと褒め言葉だけを渡してください。
4. 簡潔で親しみやすい回答を心がけてください。
"""

# 入力フォーム
with st.form(key="speech_form"):
    user_text = st.text_area("💬 質問や英文を入力してね", placeholder="ここにメッセージを入力...", height=120)
    submit_button = st.form_submit_button("AIコーチに送信する", type="primary")

if submit_button:
    if not user_text:
        st.warning("メッセージを入力してください。")
    else:
        with st.spinner("AIコーチが回答を作成中...（数秒でお答えします）"):
            config = types.GenerateContentConfig(
                system_instruction=system_instruction
            )
            
            # サーバー混雑対策（自動リトライ処理）
            max_retries = 3
            success = False
            
            for attempt in range(max_retries):
                try:
                    # 最も安定している gemini-1.5-flash を使用
                    response = client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=user_text,
                        config=config
                    )
                    
                    st.success("AIコーチからのアドバイス：")
                    st.markdown(response.text)
                    success = True
                    break
                except Exception as e:
                    # 混雑エラーの場合は1秒待って再試行
                    if attempt < max_retries - 1:
                        time.sleep(1)
                    else:
                        st.error(f"エラーが発生しました: {e}")
