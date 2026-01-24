import streamlit as st
try:
    from markitdown import MarkItDown
except ImportError:
    from markitdown_no_magika import MarkItDown
import tempfile
import os
import base64
import pypdf
import pandas as pd

st.set_page_config(page_title="MarkItDown", page_icon="📝", layout="wide")

st.title("📝 MarkItDown - PDF to Markdown")
st.write("PDFをアップロードして、Markdownに変換します。AI連携によりテーブル構造の維持も可能です。")

# Sidebar settings
with st.sidebar:
    st.header("⚙️ 設定")
    api_key = st.text_input("OpenAI API Key (任意)", type="password", help="テーブルや複雑なレイアウトの抽出精度を向上させるために使用します。")
    llm_model = st.selectbox("使用モデル", ["gpt-4o", "gpt-4o-mini"], index=0)

    st.markdown("---")
    st.info("💡 **ヒント**: PDFのテーブル構造が崩れる場合は、OpenAI APIキーを入力してAI連携を有効にするか、『📊 テーブル抽出』タブを確認してください。")
    st.markdown("""
    ### 使い方
    1. PDFファイルをアップロードします。
    2. 自動的にMarkdownへの変換が始まります。
    3. テーブルの精度が低い場合は、OpenAI APIキーを設定して再試行してください。
    4. または、『テーブル抽出』タブから直接テーブルデータを取得できます。
    """)

uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type=["pdf"])

if uploaded_file is not None:
    # Save uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        col1, col2 = st.columns([1, 1])

        with col1:
            # PDF Preview
            st.subheader("📄 PDF プレビュー")
            base64_pdf = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)

        with col2:
            tab_md, tab_table = st.tabs(["📝 Markdown", "📊 テーブル抽出"])

            with tab_md:
                st.subheader("Markdown 変換結果")
                with st.spinner("PDFをMarkdownに変換しています..."):
                    if api_key:
                        from openai import OpenAI
                        try:
                            client = OpenAI(api_key=api_key)
                            md = MarkItDown(llm_client=client, llm_model=llm_model)
                        except Exception as e:
                            st.warning(f"AI連携の初期化に失敗しました。通常モードで実行します: {e}")
                            md = MarkItDown()
                    else:
                        md = MarkItDown()

                    try:
                        # Convert PDF to Markdown
                        result = md.convert(tmp_path)
                        st.success("変換完了！")
                        st.code(result.text_content, language="markdown")
                        st.download_button(
                            label="Markdownとしてダウンロード",
                            data=result.text_content,
                            file_name=f"{os.path.splitext(uploaded_file.name)[0]}.md",
                            mime="text/markdown"
                        )
                    except Exception as e:
                        st.error(f"MarkItDown変換エラー: {e}")

            with tab_table:
                st.subheader("データ抽出 (Layoutモード)")
                st.write("PDFのレイアウトを維持したままテキストを抽出します。Markdownでテーブルが崩れる場合の参考にしてください。")

                with st.spinner("レイアウトを解析中..."):
                    try:
                        reader = pypdf.PdfReader(tmp_path)
                        for i, page in enumerate(reader.pages):
                            st.markdown(f"#### ページ {i+1}")
                            # Layout-aware text extraction
                            text = page.extract_text(extraction_mode="layout")
                            st.code(text)
                    except Exception as e:
                        st.error(f"抽出エラー: {e}")

    except Exception as e:
        st.error(f"予期しないエラーが発生しました: {e}")
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
else:
    st.info("PDFファイルをアップロードして開始してください。")
