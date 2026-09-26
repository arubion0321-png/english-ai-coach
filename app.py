import streamlit as st
import google.generativeai as genai
from PIL import Image

# 画面設定
st.set_page_config(page_title="英語スピーチ AIコーチ", page_icon="📝")
st.title("📝 英語スピーチ AIコーチ")
st.write("テーマの相談から英文のヒント添削まで、AIコーチと一緒にスピーチを作ろう！")

# 安全な設定エリア（Secrets）からAPIキーを取得
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("APIキーの設定が必要です。")
    st.stop()

genai.configure(api_key=api_key)

system_instruction = """
あなたは中学校の英語学習をサポートする優しく熱心なAIコーチです。

【役割と厳格なルール】
1. 生徒からの質問（テーマ決め、構成の相談、作文の添削など）に親身に応答してください。
2. 構成や表現を聞かれた場合は、生徒が自発的に選べるように「3つの異なるアプローチ（例：パッション型、エンジョイ型、メッセージ型）」の選択肢と、中2文法（不定詞、動名詞、助動詞など）の簡単な解説を提示してください。
3. 作文の添削を求められた場合、絶対に「正解の全文」をそのまま与えてはいけません。「時制に注意しよう」「動詞の形を思い出してね」のように、ヒントと褒め言葉だけを渡してください。
4. 中学2年生で習う文法知識を意識させつつ、1回の返答は簡潔にして会話を続けてください。
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    system_instruction=system_instruction
)

# チャット履歴の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# 過去メッセージの描画
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 1. チャット入力欄（上側）
prompt = st.chat_input("質問や英文を入力してね...")

# 2. 画像アップロード欄（下側）
uploaded_file = st.file_uploader("手書き作文の写真をアップロード（任意）", type=["jpg", "jpeg", "png"])

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("AIコーチが考え中..."):
            if uploaded_file and len(st.session_state.messages) == 1:
                image = Image.open(uploaded_file)
                response = model.generate_content([prompt, image])
            else:
                response = model.generate_content([m["content"] for m in st.session_state.messages])
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
