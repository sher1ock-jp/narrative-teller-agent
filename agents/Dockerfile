FROM python:3.13-slim

ARG ROOT_DIR=/app
ENV ROOT_DIR=${ROOT_DIR}

WORKDIR ${ROOT_DIR}

# 1) 依存定義のみ先にコピー
COPY pyproject.toml ${ROOT_DIR}/

# 2) pip → uvCLI → 依存解決
RUN pip install --upgrade pip \
    && pip install --no-cache-dir uv \
    && uv sync

# 3) 残りのソースをコピー
COPY . ${ROOT_DIR}/

# 4) ポート解放 & 起動
EXPOSE 8080
CMD ["sh", "-c", "uv run main.py --host 0.0.0.0 --port $PORT"]