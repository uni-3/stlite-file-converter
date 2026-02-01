import streamlit as st
import urllib.request
try:
    from markitdown import MarkItDown
except ImportError:
    from markitdown_no_magika import MarkItDown
import tempfile
import os
import base64
from tabulate import tabulate
import re
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextLine

st.set_page_config(page_title="MarkItDown", page_icon="📝", layout="wide")

st.title("📝 MarkItDown - PDF to Markdown")
st.write("PDFをアップロードして、Markdownに変換します。")

# Sidebar settings
with st.sidebar:
    st.header("⚙️ 設定")

    enable_table_extraction = st.checkbox(
        "テーブル構造を解析する",
        value=True,
        help="PDF内の表を検出し、Markdownのテーブル形式に変換を試みます。"
    )

    st.markdown("""
    ### 使い方
    1. PDFファイルをアップロードするか、URLを入力します。
    2. 自動的にMarkdownへの変換が始まります。
    """)

def extract_tables_from_pdf(pdf_path):
    """pdfminer.sixを使用した純Pythonのテーブル抽出ロジック"""
    all_tables = []
    try:
        for i, page_layout in enumerate(extract_pages(pdf_path)):
            elements = []
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    for text_line in element:
                        if isinstance(text_line, LTTextLine):
                            elements.append(text_line)

            if not elements:
                continue

            # Y座標でグループ化（行の検出）
            tolerance = 3
            rows = []
            elements.sort(key=lambda e: e.bbox[1], reverse=True)

            if elements:
                current_row = [elements[0]]
                for i_e in range(1, len(elements)):
                    if abs(elements[i_e].bbox[1] - current_row[0].bbox[1]) <= tolerance:
                        current_row.append(elements[i_e])
                    else:
                        rows.append(current_row)
                        current_row = [elements[i_e]]
                rows.append(current_row)

            table_data = []
            for row in rows:
                row.sort(key=lambda e: e.bbox[0])
                row_cells = []
                for line in row:
                    text = line.get_text().strip()
                    if text:
                        # 2つ以上のスペースで区切られている場合は分割
                        parts = re.split(r'\s{2,}', text)
                        row_cells.extend(parts)

                if len(row_cells) > 0:
                    table_data.append(row_cells)

            # テーブルらしいかどうかの判定（複数列の行が複数あるか）
            multi_col_count = sum(1 for r in table_data if len(r) > 1)
            if multi_col_count >= 2:
                # 表として採用
                md_table = tabulate(table_data, headers="firstrow", tablefmt="github")
                all_tables.append(f"### Page {i+1}\n\n{md_table}")
    except Exception as e:
        st.warning(f"テーブル解析中にエラーが発生しました: {e}")

    return all_tables

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
        # Markdown conversion result
        st.subheader("Markdown 変換結果")

        # Caching conversion result
        file_id = f"{pdf_name}_{len(pdf_content)}_{enable_table_extraction}"
        if "last_file_id" not in st.session_state or st.session_state.last_file_id != file_id:
            with st.status("PDFをMarkdownに変換しています...", expanded=True) as status:
                md = MarkItDown()
                try:
                    # Convert PDF to Markdown using MarkItDown
                    result = md.convert(tmp_path)
                    md_content = result.text_content

                    # Table extraction if enabled
                    tables_content = ""
                    if enable_table_extraction:
                        status.update(label="テーブル構造を解析中...", state="running")
                        tables = extract_tables_from_pdf(tmp_path)
                        if tables:
                            tables_content = "## 📋 抽出されたテーブル\n\n" + "\n\n".join(tables)
                            status.update(label="テーブルの解析が完了しました", state="complete")
                        else:
                            status.update(label="明確なテーブルは見つかりませんでした", state="complete")
                    else:
                        status.update(label="変換が完了しました", state="complete")

                    st.session_state.md_content = md_content
                    st.session_state.tables_content = tables_content
                    st.session_state.last_file_id = file_id
                except Exception as e:
                    st.error(f"MarkItDown変換エラー: {e}")
                    status.update(label="変換中にエラーが発生しました", state="error")

        if "md_content" in st.session_state:
            st.code(st.session_state.md_content, language="markdown")

            if "tables_content" in st.session_state and st.session_state.tables_content:
                st.code(st.session_state.tables_content, language="markdown")

            # Combine main content and tables for download
            download_content = st.session_state.md_content
            if "tables_content" in st.session_state and st.session_state.tables_content:
                download_content += "\n\n" + st.session_state.tables_content

            st.download_button(
                label="Markdownとしてダウンロード",
                data=download_content,
                file_name=f"{os.path.splitext(pdf_name)[0]}.md",
                mime="text/markdown"
            )

        st.divider()

        # PDF Preview
        st.subheader("📄 PDF プレビュー")
        base64_pdf = base64.b64encode(pdf_content).decode('utf-8')
        # Using <embed> for better PDF compatibility in some browsers
        pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf">'
        st.markdown(pdf_display, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"予期しないエラーが発生しました: {e}")
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
else:
    st.info("PDFファイルをアップロードするか、URLを入力して開始してください。")
