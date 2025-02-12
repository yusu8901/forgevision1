import streamlit as st
import requests
import json

import os
from dotenv import load_dotenv
load_dotenv()

# Streamlitのメイン処理
st.title("設計書レビューAI")
st.write("2つのファイルとレビュー項目を指定して、ワークフローを実行します。")


#######ヒアリング部分#######################################################
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


# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

#  Streamlitのページ設定
st.write("レビューしたい項目を入力してください。")


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


#####################################################################


# プロンプト生成用
def upload_file1(file_content, filename, user):
    upload_url = "https://api.dify.ai/v1/files/upload"
    headers = {
        "Authorization": f"Bearer {os.getenv('API_KEY1')}",
    }
    
    try:
        files = {
            'file': (filename, file_content, 'text/plain')
        }
        data = {
            "user": user,
            "type": "TXT"
        }
        
        response = requests.post(upload_url, headers=headers, files=files, data=data)
        if response.status_code == 201:
            return response.json().get("id")
        else:
            st.error(f"ファイルのアップロードに失敗しました。ステータス コード: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
        return None

# 設計書レビュー用
def upload_file2(file_content, filename, user):
    upload_url = "https://api.dify.ai/v1/files/upload"
    headers = {
        "Authorization": f"Bearer {os.getenv('API_KEY2')}",
    }
    
    try:
        files = {
            'file': (filename, file_content, 'text/plain')
        }
        data = {
            "user": user,
            "type": "TXT"
        }
        
        response = requests.post(upload_url, headers=headers, files=files, data=data)
        if response.status_code == 201:
            return response.json().get("id")
        else:
            st.error(f"ファイルのアップロードに失敗しました。ステータス コード: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
        return None

# プロンプト生成用
def run_workflow1(review_request_id, user, response_mode="blocking"):
    workflow_url = "https://api.dify.ai/v1/workflows/run"
    headers = {
        "Authorization": f"Bearer {os.getenv('API_KEY1')}",
        "Content-Type": "application/json"
    }

    data = {
        "inputs": {
            "review_request": {
                "transfer_method": "local_file",
                "upload_file_id": review_request_id,
                "type": "document"
            }
        },
        "response_mode": response_mode,
        "user": user
    }

    try:
        response = requests.post(workflow_url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"ワークフローの実行がステータス コードで失敗しました: {response.status_code}")
            return {"status": "error", "message": f"Failed to execute workflow, status code: {response.status_code}"}
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
        return {"status": "error", "message": str(e)}
    
# 設計書レビュー用
def run_workflow2(file_id1, file_id2, review_request_id, user, response_mode="blocking"):
    workflow_url = "https://api.dify.ai/v1/workflows/run"
    headers = {
        "Authorization": f"Bearer {os.getenv('API_KEY2')}",
        "Content-Type": "application/json"
    }

    data = {
        "inputs": {
            "upload_file1": {
                "transfer_method": "local_file",
                "upload_file_id": file_id1,
                "type": "document"
            },
            "upload_file2": {
                "transfer_method": "local_file",
                "upload_file_id": file_id2,
                "type": "document"
            },
            "review_request": {
                "transfer_method": "local_file",
                "upload_file_id": review_request_id,
                "type": "document"
            }
        },
        "response_mode": response_mode,
        "user": user
    }

    try:
        response = requests.post(workflow_url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"ワークフローの実行がステータス コードで失敗しました: {response.status_code}")
            return {"status": "error", "message": f"Failed to execute workflow, status code: {response.status_code}"}
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
        return {"status": "error", "message": str(e)}



# サイドバーにファイルアップロードウィジェットを配置
with st.sidebar:
    st.header("入力項目")
    file1 = st.file_uploader("基本設計書をアップロード(md)", type=['md'])
    file2 = st.file_uploader("要件定義書をアップロード(md)", type=['md'])
    # review_request = st.text_area("レビュー項目を入力", help="レビューで確認してほしい項目を入力してください")

# ユーザー
user = "difyuser"

# サイドバーに実行ボタンを配置
if st.sidebar.button("ワークフローを実行"):
    if file1 is not None and file2 is not None:
        with st.spinner("処理中..."):
            # ヒアリング部分の最後の応答を取得
            last_assistant_message = next((msg["content"] for msg in reversed(st.session_state.messages) if msg["role"] == "assistant"), None)
            if last_assistant_message:
                review_request = last_assistant_message
            
            # ファイルをアップロード
            file_id1 = upload_file2(file1.getvalue(), file1.name, user)
            file_id2 = upload_file2(file2.getvalue(), file2.name, user)
            
            # レビュー項目をテキストファイルとしてアップロード（最後のアシスタントの応答を使用）
            review_request_id = upload_file1(review_request.encode(), "review_request.txt", user)

            if review_request_id:
                # ワークフローを実行
                result1 = run_workflow1(review_request_id, user)
                st.success("プロンプト生成ワークフローが正常に実行されました")
                st.write(result1)

                if file_id1 and file_id2:
                    # 設計書レビューワークフローを実行
                    result2 = run_workflow2(file_id1, file_id2, review_request_id, user)
                    st.success("設計書レビューワークフローが正常に実行されました")
                    st.write(result2["data"]["outputs"]["text"])
                else:
                    st.error("ファイルのアップロードに失敗しました")
            else:
                st.error("レビュー項目のアップロードに失敗しました")
    else:
        st.warning("2つのファイルを選択し、レビュー項目を入力してください")
