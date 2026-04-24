FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
COPY uv.lock* .

RUN uv sync --frozen || uv sync

COPY . .

RUN uv run python rag/build_index.py

ENV TASK_ID=task1_easy
ENV SEED=42

EXPOSE 7860

CMD ["uv", "run", "python", "server/app.py"]