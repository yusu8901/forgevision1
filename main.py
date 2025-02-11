import streamlit as st
import requests
import json

import os
from dotenv import load_dotenv
load_dotenv()

def upload_file(file_content, filename, user):
    upload_url = "https://api.dify.ai/v1/files/upload"
    headers = {
        "Authorization": f"Bearer {os.getenv('API_KEY')}",
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

def run_workflow(file_id1, file_id2, review_request_id, user, response_mode="blocking"):
    workflow_url = "https://api.dify.ai/v1/workflows/run"
    headers = {
        "Authorization": f"Bearer {os.getenv('API_KEY')}",
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

# Streamlitのメイン処理
st.title("Dify ワークフロー実行")
st.write("2つのテキストファイルとレビュー項目を指定して、Difyワークフローを実行します。")

# ファイルアップロードウィジェット
file1 = st.file_uploader("1つ目のファイルを選択(md)", type=['md'])
file2 = st.file_uploader("2つ目のファイルを選択(md)", type=['md'])

review_request = st.text_area("レビュー項目を入力", help="レビューで確認してほしい項目を入力してください")

# ユーザー
user = "difyuser"

# 実行ボタン
if st.button("ワークフローを実行"):
    if file1 is not None and file2 is not None and review_request:
        with st.spinner("処理中..."):
            # ファイルをアップロード
            file_id1 = upload_file(file1.getvalue(), file1.name, user)
            file_id2 = upload_file(file2.getvalue(), file2.name, user)
            
            # レビュー項目をテキストファイルとしてアップロード
            review_request_id = upload_file(review_request.encode(), "review_request.txt", user)
            
            if file_id1 and file_id2 and review_request_id:
                # ワークフローを実行
                result = run_workflow(file_id1, file_id2, review_request_id, user)
                
                # 結果を表示
                st.success("ワークフローが正常に実行されました")
                st.write(result)
                # st.write(result["data"]["outputs"]["text"])
            else:
                st.error("ファイルのアップロードに失敗しました")
    else:
        st.warning("2つのファイルを選択し、レビュー項目を入力してください")
