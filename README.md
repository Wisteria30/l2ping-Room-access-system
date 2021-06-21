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
export DEFAULT_SLACK_CHANNEL="必須"
docker-compose build
# pysenをPASSしないと立ち上がらない
docker-compose up
```

# 本番環境
今どうやっているかわからないので，仮にvenvを使っていると仮定
```sh
cd app
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip slack-bolt aiohttp
export SLACK_APP_TOKEN="xapp-"
export SLACK_BOT_TOKEN="xoxb-"
export DEFAULT_SLACK_CHANNEL="必須"
export PRODUCTION="true"
python main.py
```

# TODO
- [x] リファクタリング
    - 何も考えず実装したせいで，シーケンス図的にもぐちゃぐちゃになっているので，根本的にファイルの構成を見直す．（クラスにするとか）
- [ ] 権限を正しく設定
    - ``set_channnel``コマンドは現状だれでも実行できてしまうので，権限がある人が実行したかどうかを判断する必要がある
- [ ] 本当に退出したのか？
    - トイレじゃないのかとかを考えたときにボタンで本当に退出したかを聞くようにする（ボタンの通知とそれに付随したアクションの追加）
    - メッセージに気がつかないときがあると思うで，3回連続でpingがNGだった場合はこちらでcloseと判断する（とか）
- [ ] Slack-Botからl2pingを制御
    - 現状：l2pingとSlack-Botを非同期のタスクとしてmainから同時に起動している
    - Slack-Botから監視開始と停止をできればいいかなと．メンションでstart，stopは認識できるようにはしている（スラッシュコマンドとかショートカットコマンドでもいいかも！）
