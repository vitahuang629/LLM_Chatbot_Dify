# 使用官方 Python 映像檔
FROM python:3.9

# 設定工作目錄
WORKDIR /app

# 複製本地檔案到容器
COPY . /app

# 安裝 pipenv
RUN pip install pipenv

# 使用 Pipenv 安裝依賴項
RUN pipenv install --deploy --ignore-pipfile

# 開放 Streamlit 使用的預設埠 (8501)
EXPOSE 8501

# 設定容器啟動時執行的命令
CMD ["pipenv", "run", "streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]