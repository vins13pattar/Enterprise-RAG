FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir fastapi 'uvicorn[standard]' sqlmodel 'psycopg[binary]' pydantic-settings 'python-jose[cryptography]' 'passlib[bcrypt]' python-multipart redis qdrant-client boto3 prometheus-client httpx langgraph
COPY . .
CMD ["python","-m","apps.worker.main"]
