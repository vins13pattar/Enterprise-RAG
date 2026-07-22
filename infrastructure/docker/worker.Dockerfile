FROM python:3.11-slim
WORKDIR /app
COPY . .
# Dependency installation is intentionally omitted from the CI image build so PR
# checks remain deterministic in offline/restricted environments. Runtime images
# should install the dependencies declared in pyproject.toml or use a locked
# requirements file in a production pipeline.
CMD ["python", "-m", "apps.worker.main"]
