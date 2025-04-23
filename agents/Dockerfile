FROM python:3.13-slim

ARG ROOT_DIR=/app
ENV ROOT_DIR=${ROOT_DIR}
ENV PYTHONPATH=${ROOT_DIR}

WORKDIR ${ROOT_DIR}

# 1) 依存定義ファイルを先にコピー
COPY agents/pyproject.toml ${ROOT_DIR}/pyproject.toml

# 2) 依存関係のインストール - 必要なパッケージを明示的にインストール
RUN pip install --upgrade pip \
    && pip install --no-cache-dir fastapi==0.115.12 uvicorn==0.34.2 python-dotenv openai google-adk==0.2.0 litellm==1.67.0

# OPENAI APIキー環境変数設定
ARG OPENAI_API_KEY
ENV OPENAI_API_KEY=${OPENAI_API_KEY}

# 3) アプリケーションのソースコードをコピー
COPY agents/main.py ${ROOT_DIR}/
COPY agents/manga-agents ${ROOT_DIR}/manga-agents/

# 4) デバッグ用のログ出力
RUN echo "Directory structure:" && find ${ROOT_DIR} -type f | sort

# 5) ポート設定
EXPOSE 8080
ENV PORT=8080

# 6) アプリケーション起動（バッファリングなしでログを出力）
CMD ["python", "-u", "main.py"]