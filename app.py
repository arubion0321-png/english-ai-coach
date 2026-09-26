import streamlit as st
import re
import time
from PIL import Image
from google import genai
from google.genai import types

# 画面設定
st.set_page_config(page_title="英語スピーチ AIコーチ", page_icon="📝")
st.title("📝 英語スピーチ AIコーチ")
st.write("テーマの相談から英文のヒント添削まで、AIコーチと一緒にスピーチを作ろう！")

# APIキーの取得とクリーンアップ
raw_api_key = st.secrets.get("GEMINI_API_KEY", "")
clean_api_key = re.sub(r'[^\x00-\x7F]+', '', str(raw_api_key)).strip()

if not clean_api_key:
    st.error("APIキー（GEMINI_API_KEY）が正しく読み込めません。Secretsを確認してください。")
    st.stop()

# クライアント初期化
client = genai.Client(api_key=clean_api_key)

system_instruction = """
あなたは中学校の英語学習をサポートする優しく熱心なAIコーチです。

【役割とルール】
1. 生徒からの質問（テーマ決め、構成、作文添削）に親身に応答してください。
2. 構成や表現を聞かれた場合は「3つの異なるアプローチ」の選択肢と、中2文法の簡単な解説を提示してください。
3. 作文添削や写真の読み込み時、絶対に正解の全文を与えず、ヒントと褒め言葉だけを渡してください。
4. 簡潔で親しみやすい回答を心がけてください。
"""

# セッション状態にチャット履歴を初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# 1. 過去の会話履歴を上に表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 2. 下部に写真アップロードと入力欄を配置
st.divider()  # 区切り線
uploaded_file = st.file_uploader("📷 手書き作文の写真を添付（任意）", type=["jpg", "jpeg", "png"])

if user_input := st.chat_input("質問やメッセージを入力してね（例：パターン3で書いてみたい！）"):
    # 写真がある場合の表示テキスト作成
    display_text = user_input
    if uploaded_file:
        display_text = f"📷 [写真を添付しました]\n{user_input}"
        
    # ユーザーメッセージを表示・履歴追加
    st.chat_message("user").markdown(display_text)
    st.session_state.messages.append({"role": "user", "content": display_text})

    # AIへの送信データ構築
    contents = []
    
    # 過去の文脈（履歴）を追加
    for msg in st.session_state.messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

    # 今回の送信内容（テキスト + 画像があれば追加）
    current_parts = [types.Part.from_text(text=user_input)]
    if uploaded_file:
        image = Image.open(uploaded_file)
        current_parts.append(image)
        
    contents.append(types.Content(role="user", parts=current_parts))

    # AIからの回答処理
    with st.chat_message("assistant"):
        with st.spinner("AIコーチが考えています..."):
            config = types.GenerateContentConfig(
                system_instruction=system_instruction
            )
            
            max_retries = 3
            response_text = ""
            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=contents,
                        config=config
                    )
                    response_text = response.text
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(1)
                    else:
                        response_text = f"申し訳ありません、エラーが発生しました: {e}"

            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
