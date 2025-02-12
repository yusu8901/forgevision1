import requests
import json
import streamlit as st
import os
from dotenv import load_dotenv

# .env ファイルを読み込む
load_dotenv()

# Difyのchat-messagesエンドポイント
API_URL = "https://api.dify.ai/v1/chat-messages"

# APIキーを環境変数から取得
API_KEY = os.getenv("API_KEY3")

# リクエスト共通ヘッダー
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json',
}

def start_conversation(query: str, inputs: dict = {}):
    """
    新規会話を開始し、conversation_idと最初の応答を返す関数
    query: ユーザーからの最初の質問
    inputs: 必要に応じて渡す変数（初回の呼び出し時のみ有効）
    """
    data = {
        "inputs": inputs,
        "query": query,
        "response_mode": "blocking",  # "streaming"も可能
        "conversation_id": "",        # 新規会話は空文字列または省略
        "user": "user-123"            # ユーザーを表すIDを任意で指定
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        resp_json = response.json()
        conversation_id = resp_json.get("conversation_id", None)
        answer = resp_json.get("answer", "")
        return conversation_id, answer
    else:
        st.error(f"Error: {response.text}")
        return None, None

def continue_conversation(conversation_id: str, query: str):
    """
    既存のconversation_idを用いて会話を継続
    query: ユーザーからの追加の問いかけ
    """
    data = {
        "inputs": {},
        "query": query,
        "response_mode": "blocking",
        "conversation_id": conversation_id,
        "user": "user-123"
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        resp_json = response.json()
        answer = resp_json.get("answer", "")
        return answer
    else:
        st.error(f"Error: {response.text}")
        return ""

# Streamlitのページ設定
st.title("Dify Chat Bot")

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

# チャット履歴の表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# チャット入力と応答の処理
if prompt := st.chat_input("メッセージを入力してください"):
    # ユーザーメッセージの表示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Difyでの応答処理
    with st.chat_message("assistant"):
        if st.session_state.conversation_id is None:
            # 新規会話の開始
            conversation_id, response = start_conversation(prompt)
            if conversation_id:
                st.session_state.conversation_id = conversation_id
        else:
            # 既存の会話の継続
            response = continue_conversation(st.session_state.conversation_id, prompt)

        if response:
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            st.error("応答の取得に失敗しました。")
