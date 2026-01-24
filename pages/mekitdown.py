import streamlit as st
try:
    from markitdown import MarkItDown
except ImportError:
    from markitdown_no_magika import MarkItDown
import tempfile
import os
import base64
import pypdf

st.set_page_config(page_title="MarkItDown", page_icon="📝", layout="wide")

st.title("📝 MarkItDown - PDF to Markdown")
st.write("PDFをアップロードして、Markdownに変換します。テーブル構造の確認には『Layoutモード』も活用できます。")

# Sidebar settings
with st.sidebar:
    st.header("⚙️ 設定")
    st.info("💡 **ヒント**: 標準のMarkdown変換でテーブル構造が崩れる場合は、『📊 Layoutモード』タブを確認してください。")
    st.markdown("""
    ### 使い方
    1. PDFファイルをアップロードします。
    2. 自動的にMarkdownへの変換が始まります。
    3. テーブルの並びが不自然な場合は、『Layoutモード』タブで物理的な配置を確認できます。
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
            tab_md, tab_layout = st.tabs(["📝 Markdown", "📊 Layoutモード"])

            with tab_md:
                st.subheader("Markdown 変換結果")
                with st.spinner("PDFをMarkdownに変換しています..."):
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

            with tab_layout:
                st.subheader("テキスト抽出 (Layoutモード)")
                st.write("PDFの物理的なレイアウトを維持したままテキストを抽出します。テーブルの構造確認に役立ちます。")

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
