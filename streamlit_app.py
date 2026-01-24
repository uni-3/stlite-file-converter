import streamlit as st

st.title("Hello stlite!")
st.write("This is a Streamlit app running entirely in your browser.")

name = st.text_input("What is your name?", "World")
st.write(f"Hello, {name}!")

if st.button("Click me!"):
    st.balloons()
    st.success("You clicked the button!")
