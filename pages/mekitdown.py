import streamlit as st
import urllib.request
try:
    from markitdown import MarkItDown
except ImportError:
    from markitdown_no_magika import MarkItDown
import tempfile
import os
import base64

st.set_page_config(page_title="MarkItDown", page_icon="📝", layout="wide")

st.title("📝 MarkItDown - PDF to Markdown")
st.write("PDFをアップロードして、Markdownに変換します。")

# Sidebar settings
with st.sidebar:
    st.header("⚙️ 設定")
    st.markdown("""
    ### 使い方
    1. PDFファイルをアップロードするか、URLを入力します。
    2. 自動的にMarkdownへの変換が始まります。
    """)

uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type=["pdf"])
url = st.text_input("またはPDFのURLを入力してください")

pdf_content = None
pdf_name = None

if uploaded_file is not None:
    pdf_content = uploaded_file.getvalue()
    pdf_name = uploaded_file.name
elif url:
    try:
        with st.spinner("URLからPDFをダウンロードしています..."):
            with urllib.request.urlopen(url) as response:
                pdf_content = response.read()
                pdf_name = url.split("/")[-1] or "downloaded_file.pdf"
                if not pdf_name.lower().endswith(".pdf"):
                    pdf_name += ".pdf"
    except Exception as e:
        st.error(f"URLからの取得に失敗しました: {e}")

if pdf_content is not None:
    # Save PDF content to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_content)
        tmp_path = tmp.name

    try:
        col1, col2 = st.columns([1, 1])

        with col1:
            # PDF Preview
            st.subheader("📄 PDF プレビュー")
            base64_pdf = base64.b64encode(pdf_content).decode('utf-8')
            # Using <embed> for better PDF compatibility in some browsers
            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf">'
            st.markdown(pdf_display, unsafe_allow_html=True)

        with col2:
            st.subheader("Markdown 変換結果")

            # Caching conversion result
            file_id = f"{pdf_name}_{len(pdf_content)}"
            if "last_file_id" not in st.session_state or st.session_state.last_file_id != file_id:
                with st.spinner("PDFをMarkdownに変換しています..."):
                    md = MarkItDown()
                    try:
                        # Convert PDF to Markdown
                        result = md.convert(tmp_path)
                        st.session_state.md_content = result.text_content
                        st.session_state.last_file_id = file_id
                    except Exception as e:
                        st.error(f"MarkItDown変換エラー: {e}")

            if "md_content" in st.session_state:
                st.code(st.session_state.md_content, language="markdown")
                st.download_button(
                    label="Markdownとしてダウンロード",
                    data=st.session_state.md_content,
                    file_name=f"{os.path.splitext(pdf_name)[0]}.md",
                    mime="text/markdown"
                )

    except Exception as e:
        st.error(f"予期しないエラーが発生しました: {e}")
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
else:
    st.info("PDFファイルをアップロードするか、URLを入力して開始してください。")
