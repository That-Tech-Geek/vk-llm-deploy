FROM python:3.11-slim
WORKDIR /app
COPY app /app/app
COPY deploy.py /app/deploy.py
COPY model /app/model
RUN pip install --no-cache-dir fastapi uvicorn torch transformers peft
ENV API_KEY="dummy-key"
EXPOSE 10000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","10000"]
