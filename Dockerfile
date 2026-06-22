FROM python:3.11

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y \
    gcc \
    portaudio19-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN sed -i '/pywin32/d' requirements.txt && \
    sed -i '/pypiwin32/d' requirements.txt && \
    sed -i 's/protobuf==.*/protobuf/g' requirements.txt && \
    sed -i 's/mediapipe==.*/mediapipe/g' requirements.txt && \
    pip install --no-cache-dir -r requirements.txt



EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]