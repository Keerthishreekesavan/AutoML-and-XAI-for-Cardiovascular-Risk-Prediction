FROM openjdk:11

# Install Python + tools
RUN apt-get update && apt-get install -y python3 python3-pip

WORKDIR /app
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]