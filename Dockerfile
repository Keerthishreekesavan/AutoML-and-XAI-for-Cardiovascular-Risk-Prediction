FROM eclipse-temurin:11-jdk

RUN apt-get update && apt-get install -y python3 python3-pip python3-venv

WORKDIR /app
COPY . .

# create venv
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# install packages inside venv (NOT system python)
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]