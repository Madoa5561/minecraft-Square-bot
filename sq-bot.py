import time
import random
from CHRLINE_Square import CHRLINE
import requests

LAST_RESPONSE_TIME = {}

client = CHRLINE(authTokenOrEmail="",
                device="IOSIPAD",
                useThrift=True)
note1 = """📕ルール📕

人のアイテムを盗む行為
人を建築物を破壊する行為
人に嫌がらせ、不快に思われる行為
人をリスキルする行為
荒らし行為
鯖主があまりよろしくないと思う行為
サーバーを意図的に重くさせる"""

note2 = """『もっと見る』を押してください

統合版限定マルチプレイサーバー

マルチワールドに入るにはまず認証をする必要があります
認証はLINE上で完結します。
認証用の別トークに参加してください

『認証』"""

def process_events(client):
    events = client.fetchMyEvents()
    MOYASHI = True
    try:
        while MOYASHI:
            try:
                events = client.fetchMyEvents(syncToken=events.syncToken)
                for e in events.events:
                    if e.type == 29:  # chat Message Event
                        msg = e.payload.notificationMessage.squareMessage.message
                        to = msg.to
                        text = msg.text
                        if text and is_allowed_to_respond(to):
                            if text == "test":
                                client.sendSquareMessage(to, append_random_emoji("動いてるよ"))
                            elif text == "認証":
                                try:
                                    # URL生成APIにリクエストを送る
                                    res = requests.get("http://127.0.0.1:7334/generate_url_59b22d41-2bc2-b996-fa5d-851ccbf02121")
                                    
                                    # サーバーが応答しない場合のエラーハンドリング
                                    res.raise_for_status()  # ステータスコードが200番台でない場合、例外を発生させる
                                    
                                    # レスポンスをJSON形式で取得
                                    url = res.json().get("url", None)
                                    
                                    # URLが存在する場合
                                    if url:
                                        client.sendSquareMessage(to, f"以下のURLを押してマインクラフト上でのIDをいれてください\nYour ID:{msg._from}\n{url}")
                                    else:
                                        client.sendSquareMessage(to, "認証用のURLを取得できませんでした。もう一度お試しください。")
                                except requests.exceptions.RequestException as e:
                                    # リクエストに失敗した場合のエラーハンドリング
                                    print(f"リクエストエラー: {e}")
                                    client.sendSquareMessage(to, "認証のリクエストに失敗しました。後で再試行してください。")
                            elif text == note1 and not msg._from == "p18d719adbbd6003279714c4121e5023e":
                                client.destroySquareMessage(to, msg.id, None)
                            elif text == note2 and not msg._from == "p18d719adbbd6003279714c4121e5023e":
                                client.destroySquareMessage(to, msg.id, None)
                            else:
                                pass
                        else:
                            pass
            except Exception as e:
                print(e)
    except KeyboardInterrupt:
        MOYASHI = False
        print("イベント取得を停止しました")
        client.is_login = False
        print("アカウントからログアウトしました")
        return


def append_random_emoji(message: str) -> str:
    emojis = [
        "😊", "😂", "😍", "😎", "😢", "😡", "😱", "😴", "😇", "🤔", "🥳", "🤩", "😜", "😋", "😏", "😬", "🤯", "😵", "🤗", "😷",
        "😃", "😄", "😁", "😆", "😅", "🤣", "😌", "😉", "🙃", "😋", "😛", "😝", "😜", "🤪", "🤨", "🧐", "🤓", "😎", "🥸", "🤩",
        "🥳", "😏", "😒", "😞", "😔", "😟", "😕", "🙁", "☹️", "😣", "😖", "😫", "😩", "🥺", "😢", "😭", "😤", "😠", "😡", "🤬",
        "🤯", "😳", "🥵", "🥶", "😱", "😨", "😰", "😥", "😓", "🤗", "🤔", "🤭", "🤫", "🤥", "😶", "😐", "😑", "😬", "🙄", "😯",
        "😦", "😧", "😮", "😲", "🥱", "😴", "🤤", "😪", "😵", "🤐", "🥴", "🤢", "🤮", "🤧", "😷", "🤒", "🤕", "🤑", "🤠", "😈",
        "👿", "👹", "👺", "🤡", "💩", "👻", "💀", "☠️", "👽", "👾", "🤖", "🎃", "😺", "😸", "😹", "😻", "😼", "😽", "🙀", "😿",
        "😾", "🙈", "🙉", "🙊", "💋", "💌", "💘", "💝", "💖", "💗", "💓", "💞", "💕", "💟", "❣️", "💔", "❤️", "🧡", "💛", "💚",
        "💙", "💜", "🤎", "🖤", "🤍", "💯", "💢", "💥", "💫", "💦", "💨", "🕳️", "💣", "💬", "👁️‍🗨️", "🗨️", "🗯️", "💭", "💤"
    ]
    random_emoji = random.choice(emojis)
    return f"{message} [{random_emoji}]"


def is_allowed_to_respond(to) -> bool:
    current_time = time.time()
    if to in LAST_RESPONSE_TIME:
        if current_time - LAST_RESPONSE_TIME[to] < 3:
            return False
    LAST_RESPONSE_TIME[to] = current_time
    return True
process_events(client)
