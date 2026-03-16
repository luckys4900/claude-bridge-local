# GitHub セットアップ手順

## 1. GitHub でリポジトリを作成

1. https://github.com/new にアクセス
2. リポジトリ名を入力（例: `claude-bridge-local`）
3. **Create repository** をクリック

## 2. リモートを追加してプッシュ

GitHub で作成したリポジトリの URL を取得し、以下を実行:

```bash
# リモート追加（URL は自分のリポジトリに置き換え）
git remote add origin https://github.com/YOUR_USERNAME/claude-bridge-local.git

# プッシュ
git branch -M main
git push -u origin main
```

SSH を使う場合:
```bash
git remote add origin git@github.com:YOUR_USERNAME/claude-bridge-local.git
git push -u origin main
```

## 3. 初回セットアップ時の注意

- **config.json** は .gitignore に含まれているため、GitHub にはプッシュされません（APIキー保護）
- クローン後は `copy config.json.example config.json` で設定ファイルを作成してください
