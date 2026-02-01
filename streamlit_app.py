import streamlit as st

st.set_page_config(page_title="Stlite File Converter", page_icon="🔄")

st.title("Stlite File Converter")
st.write("以下のツールをご利用いただけます：")

st.page_link("pages/markitdown.py", label="MarkItDown (PDF to Markdown)", icon="📝")
