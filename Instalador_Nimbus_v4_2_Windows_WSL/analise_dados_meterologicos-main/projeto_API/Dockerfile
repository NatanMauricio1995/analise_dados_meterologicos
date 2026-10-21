FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY projeto_API/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY projeto_API/ /app/projeto_API/
COPY shared/ /app/shared/
EXPOSE 5000
CMD ["python", "projeto_API/app.py"]
