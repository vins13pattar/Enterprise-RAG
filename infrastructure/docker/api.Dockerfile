FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir fastapi 'uvicorn[standard]' sqlmodel 'psycopg[binary]' pydantic-settings 'python-jose[cryptography]' 'passlib[bcrypt]' python-multipart redis qdrant-client boto3 prometheus-client httpx langgraph
COPY . .
CMD ["uvicorn","apps.api.app.main:app","--host","0.0.0.0","--port","8000"]
