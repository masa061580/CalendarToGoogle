# Calendar to Google

クリップボードのテキストからGoogleカレンダーにイベントを追加するシステムトレイアプリ

## 機能

- クリップボードの日付/イベントテキストを監視
- 右クリックメニューからGoogleカレンダーに追加
- 日本語の日付形式に対応
- イベント追加前に編集ダイアログで確認・修正可能

## 対応する日付形式

### 日付
- `2024/12/25` または `2024-12-25`
- `12/25` または `12-25`
- 日本語: `2024年12月25日`, `12月25日`
- 相対日付: `今日`, `明日`, `明後日`
- 曜日: `月曜日` - `日曜日`

### 時間（オプション）
- `14:30`
- `14時30分`
- `14時`

---

## インストール手順

### 1. Pythonのインストール

#### Windows
1. [Python公式サイト](https://www.python.org/downloads/)からPython 3.10以上をダウンロード
2. インストーラーを実行
3. **重要**: 「Add Python to PATH」にチェックを入れてインストール

#### macOS
```bash
# Homebrewを使用（推奨）
brew install python@3.12

# または公式サイトからダウンロード
# https://www.python.org/downloads/macos/
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
```

### 2. uvのインストール

uv は高速なPythonパッケージマネージャーです。

#### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### macOS / Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

インストール後、ターミナル/PowerShellを再起動してください。

### 3. アプリケーションのセットアップ

```bash
# プロジェクトディレクトリに移動
cd Calendar-to-Google

# 依存関係をインストール
uv sync
```

---

## Google Calendar API の設定

### 1. Google Cloud Console でプロジェクトを作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 右上の「プロジェクトを選択」→「新しいプロジェクト」をクリック
3. プロジェクト名を入力（例: `calendar-to-google`）して「作成」

### 2. Google Calendar API を有効化

1. 左メニューから「APIとサービス」→「ライブラリ」を選択
2. 検索バーで「Google Calendar API」を検索
3. 「Google Calendar API」をクリック
4. 「有効にする」ボタンをクリック

### 3. OAuth 同意画面の設定

1. 左メニューから「APIとサービス」→「OAuth 同意画面」を選択
2. User Type で「外部」を選択して「作成」
3. 以下を入力:
   - アプリ名: `Calendar to Google`（任意）
   - ユーザーサポートメール: 自分のメールアドレス
   - デベロッパーの連絡先情報: 自分のメールアドレス
4. 「保存して次へ」をクリック
5. スコープの設定はそのまま「保存して次へ」
6. テストユーザーに自分のGoogleアカウントを追加
7. 「保存して次へ」→「ダッシュボードに戻る」

### 4. OAuth クライアント ID の作成

1. 左メニューから「APIとサービス」→「認証情報」を選択
2. 上部の「+ 認証情報を作成」→「OAuth クライアント ID」をクリック
3. アプリケーションの種類: 「デスクトップアプリ」を選択
4. 名前を入力（例: `calendar-to-google-client`）
5. 「作成」をクリック
6. 表示されたダイアログで「JSONをダウンロード」をクリック
7. ダウンロードされた `client_secret_XXXXX.json` ファイルを保存

### 5. 認証情報ファイルの登録

#### 方法A: アプリから登録（推奨）

1. アプリを起動
2. トレイアイコンを右クリック →「Register Credentials...」を選択
3. ダウンロードしたJSONファイルを選択
4. 「認証情報を登録しました」と表示されれば完了

#### 方法B: 手動で配置

ダウンロードしたJSONファイルを以下の場所に `credentials.json` としてコピー:

- **Windows**: `C:\Users\<ユーザー名>\.calendar-to-google\credentials.json`
- **macOS/Linux**: `~/.calendar-to-google/credentials.json`

---

## 使い方

### アプリの起動

#### Windows
- `start.bat` をダブルクリック
- または `run_silent.vbs` でコンソールなしで起動

#### macOS / Linux
```bash
./start.sh
# または
uv run calendar-to-google
```

### 基本的な使い方

1. アプリを起動するとシステムトレイにカレンダーアイコンが表示されます
2. 日付を含むテキストをコピー（Ctrl+C / Cmd+C）
3. 日付が検出されるとアイコンが黄色に変わり、通知が表示されます
4. トレイアイコンを右クリック →「Add Clipboard to Calendar...」を選択
5. 編集ダイアログでイベント内容を確認・修正
6. 「Add to Calendar」をクリックでGoogleカレンダーに追加

### 初回認証

初めてイベントを追加する際、ブラウザが開いてGoogleアカウントでの認証を求められます。
認証を完了すると、以降は自動的にログインされます。

### トレイメニュー

| メニュー項目 | 説明 |
|------------|------|
| Add Clipboard to Calendar... | クリップボードの内容からイベントを作成 |
| Add Detected Event... | 最後に検出されたイベントを追加 |
| Status | 現在の状態を表示 |
| Register Credentials... | Google API認証情報を登録 |
| Quit | アプリを終了 |

### アイコンの色

| 色 | 状態 |
|----|------|
| 緑 | 認証済み・待機中 |
| 黄 | 日付検出済み / 認証情報登録済み（未認証） |
| グレー | 認証情報未登録 |

---

## 対応プラットフォーム

| OS | 対応状況 | 備考 |
|----|---------|------|
| Windows 10/11 | ✅ | 推奨環境 |
| macOS | ✅ | クリップボード監視はポーリング方式 |
| Linux | ⚠️ | デスクトップ環境が必要、pyperclipの追加設定が必要な場合あり |

### Linux での追加設定

Linuxでクリップボードを使用するには、以下のいずれかが必要です:

```bash
# xclip を使用する場合
sudo apt install xclip

# または xsel を使用する場合
sudo apt install xsel
```

---

## トラブルシューティング

### 「credentials.json が見つかりません」

→ Google Cloud Console から認証情報をダウンロードし、アプリの「Register Credentials...」から登録してください。

### 認証エラーが発生する

→ `~/.calendar-to-google/token.json` を削除して再認証してください。

### クリップボードが監視されない (Linux)

→ `xclip` または `xsel` がインストールされているか確認してください。

### アプリが起動しない

→ `startup_error.log` ファイルを確認してください。

---

## ライセンス

MIT
