# Calendar to Google

クリップボードの日付を検知して、Googleカレンダーにイベントを追加するデスクトップアプリです。
WindowsとmacOSに対応しています。

## 特徴

*   **クリップボード監視**: テキストをコピー（Ctrl+C / Cmd+C）するだけで、日付を自動検出します。
*   **自動ダイアログ表示**: 日付が含まれるテキストをコピーすると、自動的に編集ウィンドウがポップアップします。
*   **多様な日付形式に対応**:
    *   日本語: `2024年12月25日`, `12月25日`, `来週の金曜日`, `明日`, `14:00` など
    *   英語: `Dec 25`, `December 25th`, `25 Dec`, `12/25/2024` など
*   **Googleカレンダー連携**: ワンクリックでGoogleカレンダーに予定を追加できます。
*   **モダンなUI**: ダークモード対応の美しいインターフェース（CustomTkinter採用）。

## インストール方法

### Windows

1.  `install_setup.bat` をダブルクリックして実行します。
    *   必要なライブラリ等が自動的にインストールされます。
    *   デスクトップにショートカットが作成されます。

### macOS / Linux

1.  `install_setup.command` を実行します。
    *   ターミナルで実行するか、Finderから開いてください。
    *   必要なライブラリがインストールされ、起動スクリプトの権限が設定されます。

## 初期設定 (Google API)

このアプリを使用するには、Google Cloud Platformで作成した `credentials.json` が必要です。

1.  [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成し、Google Calendar APIを有効にします。
2.  「OAuth 2.0 クライアント ID」を作成し、JSONファイルをダウンロードします。
3.  ダウンロードしたファイルを `credentials.json` という名前に変更します。
4.  アプリを起動し、タスクトレイアイコンを右クリック -> 「Register Credentials...」を選択して、`credentials.json` を読み込ませてください。
    *   または、ユーザーホームディレクトリの `.calendar-to-google` フォルダに直接配置しても構いません。

## 使い方

1.  **起動**:
    *   Windows: デスクトップのショートカット、または `start.bat`
    *   Mac: `start.command`
2.  **イベント追加**:
    *   ウェブサイトやメールなどで、日付を含むテキストを選択し、コピー（Ctrl+C / Cmd+C）します。
    *   自動的に「Add to Google Calendar」ウィンドウが開きます。
    *   タイトルや時間を編集し、「Add to Calendar」をクリックします。
3.  **タスクトレイメニュー**:
    *   **Add Clipboard to Calendar...**: 手動でクリップボードの内容からイベントを作成します。
    *   **Add Detected Event...**: 直近で検知したイベントを再度開きます。
    *   **Status**: 現在の状態や検知したイベントを表示します。
    *   **Register Credentials...**: API認証情報を登録します。
    *   **Quit**: アプリを終了します。

## 開発者向け情報

### 依存ライブラリ
*   Python 3.10+
*   customtkinter
*   google-api-python-client
*   google-auth-oauthlib
*   keyboard (Windows only)
*   pystray
*   pillow
*   pyperclip
*   python-dateutil
*   uv (Package Manager)

### ディレクトリ構成
*   `calendar_to_google/`: ソースコード
*   `install_setup.bat`: Windows用インストーラー
*   `install_setup.command`: Mac用インストーラー
*   `start.bat`: Windows用起動スクリプト
*   `start.command`: Mac用起動スクリプト

## ライセンス
MIT License
