from io import BytesIO
import os
import requests
import time

import streamlit as st


# url is taken from docker-compose.yml
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


# session states are necessary to render data correctly 
# since the streamlit rerun the script each time user interact with the UI

# task id in celery
if "task_id" not in st.session_state: 
    st.session_state.task_id = None

# task status in celery
if "status" not in st.session_state:
    st.session_state.status = None

# flag; waiting response from celery
if "running" not in st.session_state:
    st.session_state.running = False

# result from back to show on page
if "result" not in st.session_state: 
    st.session_state.result = None


# button callback to send request
def analyze_file(uploaded_file, module):
    bytes_io = BytesIO(uploaded_file.getvalue())

    # formatting file as (file name, bytes, application/type)
    files = {"file": (uploaded_file.name, bytes_io, uploaded_file.type)}

    try:
       response = requests.post(
            f"{BACKEND_URL}/analyzers/{module}",
            files=files,
            timeout=30 # TODO: calculate necessary timeout
       ) 

       if response.status_code != 202:
            st.error(f"Error: {response.text}")
            return
      
       data = response.json()
       st.session_state.task_id = data["task_id"]
       st.session_state.running = True

       st.info(f"Task submitted. Task id: {st.session_state.task_id}")
       
    except Exception as e:
       st.error(f"ANALYZE_FILE. Connection error: {e}")


def check_status():
    try:
       status_response = requests.get(
           f"{BACKEND_URL}/status/{st.session_state.task_id}",
           timeout=10 # TODO: calculate necessary timeout
           )
         
       status_data = status_response.json()
       st.session_state.status = status_data["status"]

       if st.session_state.status == "SUCCESS":
          result_response = requests.get(
               f"{BACKEND_URL}/result/{st.session_state.task_id}",
               timeout=30 # TODO: calculate necessary timeout
               )
          st.session_state.result = result_response.json()["result"]
          st.session_state.running = False

       elif st.session_state.status == "FAILURE":
          st.error("Task failed")

    except Exception as e:
        st.error(f"CHECK_STATUS. Connection error: {e}")


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

    # there is no built-in autorefresh in streamlit
    time.sleep(3)
    st.rerun()

if st.session_state.result:
    flex.write("### Answer")
    flex.text(st.session_state.result)