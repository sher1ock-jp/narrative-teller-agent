FROM python:3.13-slim

ARG ROOT_DIR=/app
ENV ROOT_DIR=${ROOT_DIR}
ENV PYTHONPATH=${ROOT_DIR}

WORKDIR ${ROOT_DIR}

# 1) 依存定義＋lock を先にコピーしてキャッシュ効かせる
COPY agents/pyproject.toml agents/uv.lock ./

# 2) uv CLI を使って依存を同期
RUN pip install --upgrade pip \
    && pip install --no-cache-dir uv \
    && uv sync

# 3) 残りのソースをコピー
COPY agents/ ./

# 4) OpenAI API キーをビルド／実行時に渡す
ARG OPENAI_API_KEY
ENV OPENAI_API_KEY=${OPENAI_API_KEY}

# 5) ポート宣言
EXPOSE 8080
ENV PORT=8080

# 6) コンテナ起動
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
