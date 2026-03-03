from io import BytesIO
import requests
import streamlit as st


def structure_analyze(uploaded_file):
    bytes_io = BytesIO(uploaded_file.getvalue())
    # TODO: Нужно вызвать API бэка
    answer = requests() 
    write_answer(answer)    


def style_analyze(uploaded_file):
    bytes_io = BytesIO(uploaded_file.getvalue())
    # TODO: Нужно вызвать API бэка
    answer = requests() 
    write_answer(answer)    


def logic_analyze(uploaded_file):
    bytes_io = BytesIO(uploaded_file.getvalue())
    # TODO: Нужно вызвать API бэка
    answer = requests() 
    write_answer(answer)


def write_answer(answer):
   flex.write("### Answer")
   flex.write(answer)


st.title("AI Academic Writing Assistant")
uploaded_file = st.file_uploader(label="Upload your manuscript", type=["txt", "docx", "pdf"])
flex = st.container()
if uploaded_file is not None:
    flex_1 = flex.container(horizontal=True, horizontal_alignment="center")

    flex_1.button("Structure", on_click=structure_analyze, args=[uploaded_file])
    flex_1.button("Style", on_click=style_analyze, args=[uploaded_file])
    flex_1.button("Readability and Logic", on_click=logic_analyze, args=[uploaded_file])

flex.divider()

