import streamlit as st
from markitdown import MarkItDown
import tempfile
import os

st.set_page_config(page_title="MarkItDown", page_icon="📝")

st.title("📝 MarkItDown - PDF to Markdown")
st.write("PDFをアップロードして、Markdownに変換します。変換後は自由にコピーやダウンロードが可能です。")

uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("変換中..."):
        md = MarkItDown()

        # Save uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            # Convert PDF to Markdown
            result = md.convert(tmp_path)

            st.success("変換が完了しました！")

            st.subheader("Markdown プレビュー")
            # Display result in st.code for easy copying
            st.code(result.text_content, language="markdown")

            # Provide download button
            st.download_button(
                label="Markdownとしてダウンロード",
                data=result.text_content,
                file_name=f"{os.path.splitext(uploaded_file.name)[0]}.md",
                mime="text/markdown"
            )

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
else:
    st.info("PDFファイルをアップロードして開始してください。")
