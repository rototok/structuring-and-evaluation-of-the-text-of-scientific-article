from io import BytesIO
import os
import requests
import streamlit as st
import time


# url подтягивается из docker-compose.yml
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


# так как streamlit перезапускает скрипт после каждого действия пользователя,
# отрисовать все в колбэке по нажатию кнопку не представляется возможным
# именно для того, чтобы всё корректно и вовремя отражалось, нужны стейты сессии
if "task_id" not in st.session_state: # id таски в celery
    st.session_state.task_id = None

if "status" not in st.session_state: # статус таски в celery
    st.session_state.status = None

if "running" not in st.session_state: # флаг, отражающий необходимость ожидания ответа от celery
    st.session_state.running = False

if "result" not in st.session_state: # ответ от бэка для отображения на странице
    st.session_state.result = None


# кол-бэк для кнопок, который отправляет запрос по API
def analyze_file(uploaded_file, module):
    bytes_io = BytesIO(uploaded_file.getvalue())

    # так как мы уже считали файл, подаем его в формате (название, данные в байтах, тип файла (application/type))
    files = {"file": (uploaded_file.name, bytes_io, uploaded_file.type)}

    response = requests.post(
         f"{BACKEND_URL}/analyzers/{module}",
         files=files,
         timeout=30
    ) 

    if response.status_code != 202:
         st.error(f"Error: {response.text}")
         return
    
    data = response.json()
    
    st.session_state.task_id = data["task_id"]
    st.session_state.status = "PENDING"
    st.session_state.running = True

    st.info(f"Task submitted. Task_id: {st.session_state.task_id}")


# функция для проверки статуса задачи
# как только получили ответ от бэка - меняем статус
def check_status():
    status_response = requests.get(
         f"{BACKEND_URL}/status/{st.session_state.task_id}",
         timeout=10
         )
       
    status_data = status_response.json()
    status = status_data["status"]
       
    if status == "SUCCESS":
       result_response = requests.get(
            f"{BACKEND_URL}/result/{st.session_state.task_id}",
            timeout=30
            )
       st.session_state.result = result_response.json()["result"]
       st.session_state.status = status
       st.session_state.running = False

    elif status == "FAILURE":
       st.error("Task failed")


st.title("AI Academic Writing Assistant")
uploaded_file = st.file_uploader(label="Upload your manuscript", type=["txt", "docx", "pdf"])

flex = st.container()
if uploaded_file is not None:
    container = flex.container(horizontal=True, horizontal_alignment="center")

    container.button("Structure", on_click=analyze_file, args=[uploaded_file, "structure"])
    container.button("Style", on_click=analyze_file, args=[uploaded_file, "style"])
    container.button("Readability and Logic", on_click=analyze_file, args=[uploaded_file, "logic"])

flex.divider()


if st.session_state.running:
    check_status()
    st.info(st.session_state.status)
    time.sleep(2)
    st.rerun()

if st.session_state.result:
    flex.write("### Answer")
    flex.write(st.session_state.result)