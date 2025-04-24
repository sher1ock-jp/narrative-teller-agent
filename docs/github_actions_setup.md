# GitHub Actions Setup for Cloud Run Deployment

このドキュメントでは、GitHub ActionsとGoogle Cloud Runを使用したCICD環境の設定方法について説明します。

## 前提条件

1. Google Cloud Platformのプロジェクト
2. 適切な権限を持つサービスアカウント
3. Cloud SQLインスタンス（オプション）
4. GitHubリポジトリへのアクセス権限

## 必要なシークレット

GitHub Actionsで使用するために、以下のシークレットをリポジトリに設定する必要があります：

- `GCP_PROJECT_ID`: Google CloudプロジェクトのプロジェクトID
- `GCP_WORKLOAD_IDENTITY_PROVIDER`: Workload Identity Federationのプロバイダー
- `GCP_SERVICE_ACCOUNT`: デプロイに使用するサービスアカウントのメールアドレス
- `OPENAI_API_KEY`: OpenAI APIキー
- `CLOUD_SQL_CONNECTION_STRING`: Cloud SQLへの接続文字列（例：`postgresql://user:password@host:port/database`）

## ワークフローの設定

`.github/workflows/deploy.yml`ファイルには、以下の主要なステップが含まれています：

1. コードのチェックアウト
2. Google Cloud認証
3. Docker認証
4. コンテナのビルドとプッシュ
5. Cloud Runへのデプロイ

## Google Cloud設定手順

### 1. サービスアカウントの作成

```bash
# サービスアカウントの作成
gcloud iam service-accounts create github-actions-sa \
  --description="Service account for GitHub Actions" \
  --display-name="GitHub Actions SA"

# 必要な権限の付与
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:github-actions-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:github-actions-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:github-actions-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:github-actions-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

### 2. Workload Identity Federationの設定

```bash
# Workload Identity Poolの作成
gcloud iam workload-identity-pools create github-actions-pool \
  --location="global" \
  --description="GitHub Actions pool" \
  --display-name="GitHub Actions Pool"

# Workload Identity Providerの作成
gcloud iam workload-identity-pools providers create-oidc github-actions-provider \
  --location="global" \
  --workload-identity-pool="github-actions-pool" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# サービスアカウントとWorkload Identity Providerの関連付け
gcloud iam service-accounts add-iam-policy-binding github-actions-sa@PROJECT_ID.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions-pool/attribute.repository/OWNER/REPO"
```

### 3. Artifact Registryの設定

```bash
# リポジトリの作成
gcloud artifacts repositories create manga-agent \
  --repository-format=docker \
  --location=asia-northeast1 \
  --description="Docker repository for manga-agent"
```

### 4. Cloud SQLの設定（オプション）

```bash
# Cloud SQLインスタンスの作成
gcloud sql instances create manga-agent-db \
  --database-version=POSTGRES_13 \
  --tier=db-f1-micro \
  --region=asia-northeast1

# データベースの作成
gcloud sql databases create manga-agent-db \
  --instance=manga-agent-db

# ユーザーの作成
gcloud sql users create manga-agent-user \
  --instance=manga-agent-db \
  --password=YOUR_PASSWORD
```

## GitHub Secretsの設定

GitHubリポジトリの「Settings」→「Secrets and variables」→「Actions」で以下のシークレットを設定します：

1. `GCP_PROJECT_ID`: Google CloudプロジェクトのプロジェクトID
2. `GCP_WORKLOAD_IDENTITY_PROVIDER`: Workload Identity Providerの完全なリソース名
   例: `projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions-pool/providers/github-actions-provider`
3. `GCP_SERVICE_ACCOUNT`: サービスアカウントのメールアドレス
   例: `github-actions-sa@PROJECT_ID.iam.gserviceaccount.com`
4. `OPENAI_API_KEY`: OpenAI APIキー
5. `CLOUD_SQL_CONNECTION_STRING`: Cloud SQLへの接続文字列

## デプロイの確認

GitHub Actionsワークフローが正常に実行されると、Cloud Runサービスが作成され、アプリケーションがデプロイされます。デプロイされたURLはワークフローの出力で確認できます。

## トラブルシューティング

1. **認証エラー**: GCP_WORKLOAD_IDENTITY_PROVIDERとGCP_SERVICE_ACCOUNTの値を確認してください。
2. **ビルドエラー**: Dockerfileが正しいパスにあることを確認してください。
3. **デプロイエラー**: サービスアカウントに必要な権限があることを確認してください。
4. **データベース接続エラー**: CLOUD_SQL_CONNECTION_STRINGの形式と値を確認してください。
