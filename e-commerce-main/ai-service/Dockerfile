FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
# Upgrade pip and set increased pip timeout to reduce read timeouts for large wheels (e.g. torch)
RUN pip install --upgrade pip setuptools wheel \
 && PIP_DEFAULT_TIMEOUT=120 pip install --no-cache-dir --retries 10 --timeout 120 \
	--extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

COPY . .

EXPOSE 8006

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8006", "--reload"]
