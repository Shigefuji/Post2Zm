import json
import datetime
from base64 import b64encode
from http import HTTPStatus
import requests




## Push Test

class ZmChat:
    BASE_URL = "https://api.zoom.us/v2"
    TOKEN_URL = "https://zoom.us/oauth/token"
    TIMEZONE = "Asia/Tokyo"


    def __init__(self, config_path):
        """
        初期化メソッド。設定ファイルを読み込み、必要な情報をインスタンス変数に設定します。

        Args:
            config_path (str): 設定ファイルのパス。
        """
        with open(config_path, 'r',encoding='utf-8') as config_file:
            config_data = json.load(config_file)
        self.account_id = config_data["ZOOM_ACCOUNT_ID"]
        self.client_id = config_data["ZOOM_CLIENT_ID"]
        self.client_secret = config_data["ZOOM_CLIENT_SECRET"]
        self.channel_name = config_data["ZOOM_CHANNEL_NAME"]
        self.access_token = None

    def _retrieve_access_token(self):
        """
        アクセストークンを取得します。
        """
        url = f"{self.TOKEN_URL}?grant_type=account_credentials&account_id={self.account_id}"
        encoded_credentials = b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {"Authorization": f"Basic {encoded_credentials}"}
        response = requests.post(url=url, headers=headers)
        if response.status_code == HTTPStatus.OK:
            self.access_token = response.json()["access_token"]
        else:
            raise Exception("アクセストークンの取得に失敗しました。")

    def _send_request(self, method, endpoint, payload=None, params=None):
        """
        Zoom APIへのリクエストを送信します。

        Args:
            method (str): HTTPメソッド（"GET"、"POST"、"PUT"など）。
            endpoint (str): APIのエンドポイント。
            payload (dict, optional): リクエストのペイロード。デフォルトはNone。
            params (dict, optional): リクエストのパラメータ。デフォルトはNone。

        Returns:
            dict: レスポンスのJSONデータ。

        Raises:
            Exception: リクエストが失敗した場合。
        """
        if not self.access_token:
            self._retrieve_access_token()
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        response = requests.request(
             method, url, headers=headers, json=payload, params=params
        )
        if response.status_code in [HTTPStatus.OK, HTTPStatus.CREATED]:
            return response.json()
        else:
            raise Exception(
                f"{method} {endpoint}の実行に失敗しました。"
                f"ステータスコード: {response.status_code}"
            )

    def _load_message_history(self):
        """
        メッセージ履歴を読み込みます。

        Returns:
            dict: メッセージ履歴の辞書。日付をキーとし、メッセージを値とします。
        """
        if os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}

    def schedule_meeting(self, topic=None, start_time=None, duration=60):
        """
        ミーティングをスケジュールします。

        Args:
            topic (str, optional): ミーティングのトピック。デフォルトはNone。
            start_time (str, optional): ミーティングの開始時間（ISO 8601形式）。デフォルトはNone。
            duration (int, optional): ミーティングの継続時間（分）。デフォルトは60。

        Returns:
            str: 作成されたミーティングの参加URL。
        """
        payload = {
            "topic": topic,
            "start_time": start_time,
            "duration": duration,
            "timezone": self.TIMEZONE
        }
        response = self._send_request("POST", "/users/me/meetings", payload)
        return response.get("join_url")

    def create_chat_channel(self, channel_name):
        """
        チャットチャンネルを作成します。

        Args:
            channel_name (str): チャンネルの名前。

        Returns:
            str: 作成されたチャットチャンネルの参加URL。
        """
        payload = {"name": channel_name, "type": 1}
        response = self._send_request("POST", "/chat/users/me/channels", payload)
        return response.get("join_url")

    def get_channel_id(self, channel_name):
        """
        指定された名前のチャットチャンネルのIDを取得します。

        Args:
            channel_name (str): チャンネルの名前。

        Returns:
            str: チャンネルのID。

        Raises:
            Exception: 指定された名前のチャンネルが見つからなかった場合。
        """
        params = {'page_size': 50}
        response = self._send_request("GET", "/chat/users/me/channels", params=params)
        for channel in response.get('channels', []):
            if channel['name'] == channel_name:
                return channel['id']
        raise Exception(f'指定された名前のチャンネル "{channel_name}" が見つかりませんでした。')
    
    def get_today_messages(self, channel_id):
        """
        指定されたチャンネルから当日のメッセージを取得します。

        Args:
            channel_id (str): チャンネルのID。

        Returns:
            list: 当日のメッセージリスト。
        """
        today = datetime.date.today().isoformat()
        params = {
            'to_channel': channel_id,
            'date': today,
        }
        response = self._send_request("GET", f"/chat/users/me/messages", params=params)
        return [message['message'] for message in response.get('messages', [])]

    def send_message(self, channel_name, message):
        """
        指定されたチャットチャンネルにメッセージを送信します。

        Args:
            channel_name (str): チャンネルの名前。
            message (str): 送信するメッセージ。
        """
        
        channel_id = self.get_channel_id(channel_name)
        today_messages = self.get_today_messages(channel_id)

        # 当日すでに同じメッセージが送信されている場合は送信しない
        if message in today_messages:
            print(f"同じメッセージがすでに本日送信されています: {message}")
            return
        
        payload = {"message": message, "to_channel": self.get_channel_id(channel_name)}
        self._send_request("POST", "/chat/users/me/messages", payload)

    def update_presence_status(self, status):
        """
        ユーザーのプレゼンスステータスを更新します。

        Args:
            status (str): 更新するステータス。
        """
        #payload = {"duration": 720, "status": status}
        payload = {"status":status}
        self._send_request("PUT", "/users/me/presence_status", payload)

    def run(self):
        """
        現在の時間に基づいて挨拶メッセージをチャットチャンネルに送信します。
        """
        try:
            current_hour = datetime.datetime.now().hour
            greeting_message = "おはようございます" if current_hour < 12 else "お疲れさまでした"
            self.send_message(self.channel_name, greeting_message)
            # Type of Status
            # Away,Available,In_Calendar_Event,Presenting,In_A_Zoom_Meeting,On_A_Call,Out_of_Office,Busy
            # current_status = "Available" if current_hour < 12 else "Out_of_Office"            
            # self.update_presence_status(current_status)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    zm_chat = ZmChat('.env.local')
    zm_chat.run()
