import streamlit as st
import google.generativeai as genai
from PIL import Image

# 画面設定
st.set_page_config(page_title="英語スピーチ AIコーチ", page_icon="📝")
st.title("📝 英語スピーチ AIコーチ")
st.write("テーマの相談から英文のヒント添削まで、AIコーチと一緒にスピーチを作ろう！")

# SecretsからAPIキーを取得
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("APIキー（GEMINI_API_KEY）が設定されていません。Streamlit CloudのSecretsを確認してください。")
    st.stop()

# APIの設定
genai.configure(api_key=api_key)

system_instruction = """
あなたは中学校の英語学習をサポートする優しく熱心なAIコーチです。

【役割と厳格なルール】
1. 生徒からの質問（テーマ決め、構成の相談、作文の添削など）に親身に応答してください。
2. 構成や表現を聞かれた場合は、生徒が自発的に選べるように「3つの異なるアプローチ（例：パッション型、エンジョイ型、メッセージ型）」の選択肢と、中2文法（不定詞、動名詞、助動詞など）の簡単な解説を提示してください。
3. 作文の添削を求められた場合、絶対に「正解の全文」をそのまま与えてはいけません。「時制に注意しよう」「動詞の形を思い出してね」のように、ヒントと褒め言葉だけを渡してください。
4. 中学2年生で習う文法知識を意識させつつ、1回の返答は簡潔にして会話を続けてください。
"""

# フォーム形式にして処理を安定化
with st.form(key="speech_form"):
    user_text = st.text_area("💬 質問や英文を入力してね", placeholder="ここにメッセージを入力...", height=120)
    uploaded_file = st.file_uploader("📷 手書き作文の写真をアップロード（任意）", type=["jpg", "jpeg", "png"])
    submit_button = st.form_submit_button("AIコーチに送信する", type="primary")

# 送信ボタンが押された時の処理
if submit_button:
    if not user_text and not uploaded_file:
        st.warning("メッセージを入力するか、写真をアップロードしてください。")
    else:
        with st.spinner("AIコーチが回答を作成中...（数秒お待ちください）"):
            try:
                # 汎用的なモデル名で指定
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=system_instruction
                )

                contents = []
                if user_text:
                    contents.append(user_text)
                if uploaded_file:
                    image = Image.open(uploaded_file)
                    contents.append(image)
                
                # AIからの返答を取得
                response = model.generate_content(contents)
                
                # 結果を表示
                st.success("AIコーチからのアドバイス：")
                st.markdown(response.text)
                
            except Exception as e:
                # 万が一止まった場合にエラー内容を画面に出す
                st.error(f"APIエラーが発生しました: {type(e).__name__} - {e}")
