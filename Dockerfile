FROM python:3.12-slim
WORKDIR /app

# Copied and installed separately from the rest of the source so this layer
# only rebuilds when requirements.txt actually changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["python3", "main.py"]
