import streamlit as st
import urllib.request
try:
    from markitdown import MarkItDown
except ImportError:
    from markitdown_no_magika import MarkItDown
import tempfile
import os
import base64

st.set_page_config(page_title="MarkItDown", page_icon="📝")

st.title("📝 MarkItDown - PDF to Markdown")
st.write("PDFをアップロードして、Markdownに変換します。変換後は自由にコピーやダウンロードが可能です。")

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
    # PDF Preview
    st.subheader("PDF プレビュー")
    base64_pdf = base64.b64encode(pdf_content).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

    with st.spinner("PDFをMarkdownに変換しています... しばらくお待ちください。"):
        md = MarkItDown()

        # Save PDF content to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_content)
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
                file_name=f"{os.path.splitext(pdf_name)[0]}.md",
                mime="text/markdown"
            )

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
else:
    st.info("PDFファイルをアップロードするか、URLを入力して開始してください。")
