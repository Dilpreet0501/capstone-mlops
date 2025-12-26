FROM python:3.10-slim



WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure the model directory exists and is copied (Bake-in pattern)
# The fetch-model script pulls to inference/model/
COPY model/ /app/model/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
