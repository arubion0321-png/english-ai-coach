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

# システム指示文（既習文法制限つき）
system_instruction = """
あなたは中学校の英語学習をサポートする優しく熱心なAIコーチです。

【重要なルール：文法と単語のレベル制限】
・必ず「日本の公立中学校で学習する範囲（特に中1〜中2レベル）」の英文・文法・語彙のみを使用してください。
・高校レベルの文法（仮定法、分詞構文、複雑な関係代名詞など）や難解な単語は絶対に使わないでください。
・より簡単で直感的な表現（例：want to, like to, because, when など）に言い換えて提案してください。

【役割とルール】
1. 生徒からの質問（テーマ決め、構成、作文添削）に親身に応答してください。
2. 構成や表現を聞かれた場合は「3つの異なるアプローチ」の選択肢と、中2までに習う文法の簡単な解説を提示してください。
3. 作文添削や写真の読み込み時、絶対に正解の全文を与えず、ヒントと褒め言葉だけを渡してください。
4. 簡潔で親しみやすい回答を心がけてください。
"""

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# 送信時の処理用関数
def handle_submit():
    user_text = st.session_state.temp_user_text.strip()
    uploaded_file = st.session_state.temp_uploaded_file

    if not user_text and not uploaded_file:
        st.warning("メッセージを入力するか、写真を添付してください。")
        return

    # 表示用のテキスト作成
    display_text = user_text if user_text else "添付した写真を添削してください。"
    if uploaded_file:
        display_text = f"📷 [写真を添付しました]\n{display_text}"

    # ユーザーメッセージを履歴保存
    st.session_state.messages.append({"role": "user", "content": display_text})

    # Geminiへの送信内容構築
    contents = []
    for msg in st.session_state.messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

    current_parts = []
    if user_text:
        current_parts.append(types.Part.from_text(text=user_text))
    else:
        current_parts.append(types.Part.from_text(text="添付した作文の写真を添削してください。"))

    if uploaded_file:
        image = Image.open(uploaded_file)
        current_parts.append(image)

    contents.append(types.Content(role="user", parts=current_parts))

    # AIの回答生成
    config = types.GenerateContentConfig(system_instruction=system_instruction)
    max_retries = 3
    response_text = ""

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
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

    # 回答を履歴保存
    st.session_state.messages.append({"role": "assistant", "content": response_text})

    # 送信完了後に入力欄のテキストをクリア
    st.session_state.temp_user_text = ""


# 1. これまでの会話履歴を表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.divider()

# 2. 入力エリア（送信後に自動で空になります）
with st.container():
    st.subheader("💬 AIコーチに相談・質問する")
    st.text_area(
        "メッセージを入力してね（例：パターン3で書いてみたい！）",
        height=100,
        key="temp_user_text"
    )
    
    st.file_uploader(
        "📷 手書き作文の写真を添削してもらう場合はこちら（任意）",
        type=["jpg", "jpeg", "png"],
        key="temp_uploaded_file"
    )
    
    st.button("AIコーチに送信する", type="primary", on_click=handle_submit)
