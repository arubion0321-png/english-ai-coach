import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="APIキー動作チェック", page_icon="🔑")
st.title("🔑 APIキー動作テスト")

# 1. Secretsからキーの取得テスト
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ エラー: Streamlit Cloudの Secrets に 'GEMINI_API_KEY' が設定されていません。")
    st.stop()
else:
    st.success(f"⭕ Secretsの読み込み成功！（キーの先頭: {api_key[:5]}...）")

# 2. Gemini APIへの接続テスト
if st.button("APIキーの通信テストを実行する", type="primary"):
    with st.spinner("Google Gemini に接続テスト中..."):
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # 超軽量なテストメッセージを送信
            response = model.generate_content("Hello")
            
            st.balloons() # 成功のお祝いアニメーション
            st.success("🎉 APIキーは正常に機能しています！Geminiからの応答も受信できました！")
            st.info(f"AIからのテスト応答: {response.text}")
            
        except Exception as e:
            st.error("❌ APIキーまたは通信でエラーが発生しました。")
            st.code(str(e))
