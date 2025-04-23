# Dockerfile & Cloud Build 解説

以下は `/agents/Dockerfile` と `cloudbuild.yaml` を用いたビルド・デプロイの流れ、および動作した理由／問題点をまとめたものです。

---

## 1. Dockerfile の構成

1) ベースイメージ & WORKDIR 設定

```dockerfile
FROM python:3.13-slim
ARG ROOT_DIR=/app
ENV ROOT_DIR=${ROOT_DIR}
ENV PYTHONPATH=${ROOT_DIR}
WORKDIR ${ROOT_DIR}
```
- `python:3.13-slim` を使用し、`/app` を作業ディレクトリ・パスとする。  
- `PYTHONPATH` にも同じルートを指定し、コンテナ内でモジュールを直接参照可能に。

2) 依存関係のインストール

```dockerfile
COPY agents/pyproject.toml ${ROOT_DIR}/pyproject.toml
RUN pip install --upgrade pip \
    && pip install --no-cache-dir fastapi==0.115.12 uvicorn==0.34.2 python-dotenv openai google-adk==0.2.0 litellm==1.67.0
```
- 依存定義ファイル (`pyproject.toml`) を先にコピーし、レイヤーキャッシュを活用。  
- `pip install` で必要なライブラリを固定バージョンでインストール。

3) ソースコードのコピー

```dockerfile
COPY agents/main.py ${ROOT_DIR}/
COPY agents/manga-agents ${ROOT_DIR}/manga-agents/
```
- アプリ本体をコンテナ内にコピー。

4) デバッグ用ログ出力

```dockerfile
RUN echo "Directory structure:" && find ${ROOT_DIR} -type f | sort
```
- ビルド時にコンテナ内のファイル構成を確認。

5) ポート設定 & 起動

```dockerfile
EXPOSE 8080
ENV PORT=8080
CMD ["sh","-c","uv run main.py --host 0.0.0.0 --port $PORT"]
```
- `EXPOSE` はメタ情報としてポートを宣言。  
- `CMD` で `uv run` による Uvicorn サーバ起動。`--host 0.0.0.0` で全インターフェースをリッスンし、環境変数 `$PORT` を利用。

---

## 2. cloudbuild.yaml の流れ

```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '--build-arg'
      - 'ROOT_DIR=/app'
      - '-t'
      - '${_REGION}-docker.pkg.dev/$PROJECT_ID/...:latest'
      - '.'
    env:
      - 'GOOGLE_CLOUD_PROJECT=${PROJECT_ID}'
      - 'GOOGLE_CLOUD_REGION=${_REGION}'
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '${_REGION}-docker.pkg.dev/...:latest']
images:
  - '${_REGION}-docker.pkg.dev/...:latest'
```
- Docker イメージをビルド & タグ付け (`--build-arg` で ROOT_DIR を渡す)。  
- Artifact Registry にプッシュ。  
- 成功後、Cloud Run などにデプロイ可能なイメージが生成される。

---

## 3. デプロイが成功した理由

- **キャッシュ最適化**: 依存定義のみ先にコピーし、pyproject.toml 変更時のみ再インストール。
- **uv CLI**: `uv sync` や `uv run` による lockfile に基づく一貫性ある環境構築。
- **Cloud Build**: イメージビルド & プッシュが正常終了。
- **コンテナ起動**: Uvicorn が `$PORT`（8080）でリッスンし、Cloud Run でも接続可能。

---

## 4. 動作しなかった理由 (OpenAI API キー不足)

- `Dockerfile` では `ARG OPENAI_API_KEY` を設定し、`ENV OPENAI_API_KEY=${OPENAI_API_KEY}` で環境変数化しているが、**実際にビルドまたは実行時に値が渡されていなかった**。
- コンテナ内で `os.getenv('OPENAI_API_KEY')` が `None` となり、openai クライアント初期化時に認証エラーが発生。

### 対策

- **実行時に環境変数を渡す**: 例えば `docker run -e OPENAI_API_KEY=<キー>`、Cloud Run の環境変数設定などでキーを注入。
- **Secret Manager や .env ファイル** を利用し、安全にキーを管理。
- **起動前チェック**: FastAPI の startup イベントでキーの有無を検証し、早期にエラーを通知。

---

以上がビルド・デプロイ構成と動作上のポイントです。問題や追加質問があればご連絡ください。
