# SlackAPIでのアプリ作成の流れ
- SlackAPIの[アプリ管理画面](https://api.slack.com/apps)にアクセス
- Create New Appでアプリを作成（名前などは適切なものにする．）
- ソケットモードの有効化
    - 左のタブでソケットモードを選択してオンにする（`connections:write`は必須）
    - xapp-xxxxxxxがApp-Level Tokensで後で使うのでコピーしておく（忘れてもBasic Informationから参照可）
- チャンネルへの書き込み権限などを与える
    - OAuth & PermissionsでBotレベルで権限を付与する
    - `app_mentions:read`，`chat:write`に権限を与えておく
- イベントの登録
    - OAuthの登録でメンションなどを読み込めたりできるようになったので，それに付随したイベントの登録をする
    - Event Subscriptions -> Subscribe to bot eventsで`app_mention`と`message.channels`を登録する
    - 実は先にイベント登録すると自動的にOAuth & Permissionsが追加してくれるんだけどね．．．
- 最後にBotアプリをワークスペースへ追加し，完了．


# テスト環境
```sh
# まとめてファイルにしておいたら楽
export SLACK_APP_TOKEN="xapp-"
export SLACK_BOT_TOKEN="xoxb-"
export DEFAULT_SLACK_CHANNEL="任意"
docker-compose build
docker-compose up
```

# 本番環境
今どうやっているかわからないので，仮にvenvを使っていると仮定
```sh
cd src
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip slack-bolt
export SLACK_APP_TOKEN="xapp-"
export SLACK_BOT_TOKEN="xoxb-"
export DEFAULT_SLACK_CHANNEL="任意"
export PRODUCTION="true"
python app.py
```