FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -e .
CMD ["streamlit","run","src/ozon_ai_operator/dashboard/app.py","--server.address=0.0.0.0"]
