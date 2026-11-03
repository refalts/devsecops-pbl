FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
# Jalankan sebagai non-root user (least privilege)
RUN useradd -r -u 1001 appuser && chown -R appuser /srv
USER appuser
ENV DB_PATH=/tmp/app.db
EXPOSE 5000
HEALTHCHECK CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:5000/health')"
CMD ["python", "-m", "app.app"]
