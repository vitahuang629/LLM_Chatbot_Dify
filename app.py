import requests
import streamlit as st
import base64
from sqlalchemy import create_engine
from datetime import datetime
import pandas as pd

host = '.....'
port = 3306
user = 'vita'
password = '....'
database = 'fdl'

# 创建到 MySQL 的连接引擎
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}', echo=True, pool_pre_ping=True, isolation_level="AUTOCOMMIT")

# 儲存訊息到 MySQL
def insert_message(conversation_id, role, content, user_question):  # 添加 user_question 參數
    try:
        # 將資料轉為 DataFrame 格式
        data = pd.DataFrame({
            'conversation_id': [conversation_id],
            'role': [role],
            'content': [content],
            'user_question': [user_question],  # 新增這行來存儲用戶問題
            'created_at': [datetime.now()]  # 使用當前時間戳
        })
        # 將資料寫入資料庫的 conversation_history 表
        data.to_sql('conversation_history', con=engine, if_exists='append', index=False)
    except Exception as e:
        st.error(f"Error while inserting to MySQL: {e}")



# 為了之後要自由配置版面的顯示大小，預設用到全部版面
st.set_page_config(layout="wide")

@st.cache_data
def get_img(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

local_image_path = 'pexels-no-name-14543-66997.jpg'  # 確保圖片在同一文件夾中
img = get_img(local_image_path)

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background: linear-gradient(rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.5)), 
                url("data:image/jpeg;base64,{img}");
    background-size: cover;
}}
[data-testid="stMarkdownContainer"] {{
    text-align: center;
}}
.chat-message p {{
    font-weight: bold !important;  /* 將字體加深 */
    font-size: 1.1em !important;   /* 增加字體大小 */
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

doc_name = "M-W-2-051_全球禮金、紅利、獎金分發辦法-2024.09.24.pdf"

with st.sidebar:
    st.info("**使用文檔來源**", icon="👋🏾")
    st.markdown(
        """
        <div style="text-align: left;">
        * 全球禮金、紅利、獎金分發辦法 - 2024.09.24 <br>
        * 出勤打卡規範 - 2024.09.30 <br>
        * 同仁內部推薦獎勵辦法 - 2024.09.24 <br>
        * 懲處細則與金額規範 - 2024.03.01 <br>
        * 服裝儀容規範 - 2022.12.12 <br>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        ---
        <span style="color: purple; font-weight: bold;">Created By: 黃瑜婷Vita</span>
        """,
        unsafe_allow_html=True
    )
# st.sidebar.markdown("""
#     使用文檔來源:
#     * M-W-2-051_全球禮金、紅利、獎金分發辦法-2024.09.24
#     * M-W-2-013_出勤打卡規範-2024.09.30
#     * M-W-2-004_同仁內部推薦獎勵辦法-2024.09.24
#     * M-W-2-001_懲處細則與金額規範-2024.03.01
#     * M-W-2-012_服裝儀容規範-2022.12.12
#     """)

if st.button('不要按喔'):
    st.text("為什麼要按我！")
    st.markdown("[點我跳轉到網址](https://crm-p10.xiaoshouyi.com/)", unsafe_allow_html=True)
dify_api_key = "app-JkDMoTRYUVrozdXmmofRRgGc"

url = "https://api.dify.ai/v1/chat-messages"

st.markdown("<h1 style='text-align: center;'>HR Robot 😎</h1>", unsafe_allow_html=True)

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.session_state.conversation_id == "":
    st.markdown("<h3 style='text-align: center;'>Welcome to the HR Robot! How can I assist you today?</h3>", unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f"<b>{message['content']}</b>", unsafe_allow_html=True)

prompt = st.chat_input("Enter your question")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        headers = {
            'Authorization': f'Bearer {dify_api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            "inputs": {},
            "query": prompt,
            "response_mode": "blocking",
            "conversation_id": st.session_state.conversation_id,
            "user": "aianytime",
            "files": []
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()

            full_response = response_data.get('answer', '')
            new_conversation_id = response_data.get('conversation_id', st.session_state.conversation_id)
            st.session_state.conversation_id = new_conversation_id

            # 儲存 assistant 的回覆到 MySQL
            insert_message(
                conversation_id=st.session_state.conversation_id,  # 對應的 conversation_id
                role="assistant",  # 表示回覆者是 assistant
                content=full_response,  # 儲存 assistant 的回覆內容
                user_question=prompt  # 將用戶的問題作為對應的問題存入
            )

        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")
            full_response = "An error occurred while fetching the response."

        message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

        # 保存機器人的回答到 MySQL
        #insert_message(st.session_state.conversation_id, "assistant", full_response)

