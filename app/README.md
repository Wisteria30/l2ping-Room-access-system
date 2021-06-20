# ファイル構成

<details open>
<summary>
app/
</summary>
<dl>
    <dt>main.py</dt>
        <dd>ルートファイル</dd>
    <dt>config.py </dt>
        <dd>環境変数関係</dd>
    <details>
        <summary>
        app/slack_bot/ : SlackBot関係
        </summary>
        <dt>slack_bot/mu_bot.py </dt>
            <dd>インタラクティブ系のハンドル処理（ソケットモード）</dd>
        <dt>slack_bot/command.py </dt>
            <dd>コマンドの詳細な処理</dd>
        <dt>slack_bot/bot_info.py </dt>
            <dd>ボット情報（ボットとしてのユーザ ID など）</dd>
        <dt>slack_bot/block_kit.py </dt>
            <dd>メッセージで用いる BlockKit のヘルパー</dd>
    </details>
    <details>
        <summary>
        app/surveillance/ : 入退室関係
        </summary>
        <dt>surveillance/l2ping.py </dt>
            <dd>l2ping を用いて誰が入退室したかを監視する処理など</dd>
        <dt>surveillance/status.py </dt>
            <dd>現在の部屋の状態</dd>
    </details>
</dl>
</details>
