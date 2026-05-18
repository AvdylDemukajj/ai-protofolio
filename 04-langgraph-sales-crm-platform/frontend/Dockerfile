FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir streamlit requests pandas

COPY frontend ./frontend
COPY backend/models.py ./backend/models.py
COPY backend/config.py ./backend/config.py

ENV PYTHONPATH=/app

EXPOSE 8501

CMD ["streamlit", "run", "frontend/app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
