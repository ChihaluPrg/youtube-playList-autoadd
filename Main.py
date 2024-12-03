from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

# 認証情報とスコープ
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]


def authenticate():
    """認証を実行し、YouTube APIクライアントを作成する"""
    creds = None
    # トークンが保存されている場合はロード
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # 認証が必要な場合
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret_193398376279-cvv26b9bqtro21otvct4452m5ihi5jtq.apps.googleusercontent.com.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # トークンを保存
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)


def get_latest_video_id(youtube, channel_id):
    """特定のチャンネルの最新動画IDを取得する"""
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        order="date",
        type="video",
        maxResults=1
    )
    response = request.execute()
    if "items" in response and len(response["items"]) > 0:
        video_id = response["items"][0]["id"]["videoId"]
        print(f"チャンネル {channel_id} の最新動画ID: {video_id}")
        return video_id
    else:
        print(f"チャンネル {channel_id} の最新動画が見つかりませんでした。")
        return None


def add_video_to_playlist(youtube, playlist_id, video_id):
    """動画をプレイリストに追加する"""
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id,
                }
            }
        }
    )
    response = request.execute()
    print(f"動画がプレイリスト {playlist_id} に追加されました: {response['id']}")


if __name__ == "__main__":
    # 認証を行いYouTube APIクライアントを取得
    youtube = authenticate()

    # チャンネルIDとプレイリストIDのペア
    channel_playlist_pairs = [
        {"channel_id": "UChwgNUWPM-ksOP3BbfQHS5Q", "playlist_id": "PLsRy2iansSOCrqZ24JhoeAFl1sGW196x7"},
        {"channel_id": "UCf-wG6PlxW7rpixx1tmODJw", "playlist_id": "PLsRy2iansSOBfjNIy-9dwsF0s4-5ALMW5"}
    ]

    # 各チャンネルの最新動画を取得し、対応するプレイリストに追加
    for pair in channel_playlist_pairs:
        channel_id = pair["channel_id"]
        playlist_id = pair["playlist_id"]

        # チャンネルの最新動画を取得
        latest_video_id = get_latest_video_id(youtube, channel_id)

        # 動画をプレイリストに追加
        if latest_video_id:
            add_video_to_playlist(youtube, playlist_id, latest_video_id)
