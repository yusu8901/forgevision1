import streamlit as st
import requests
import json

import os
from dotenv import load_dotenv
load_dotenv()


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

# Streamlitのメイン処理
st.title("設計書レビュー")
st.write("2つのファイルとレビュー項目を指定して、ワークフローを実行します。")

# サイドバーにファイルアップロードウィジェットを配置
with st.sidebar:
    st.header("入力項目")
    file1 = st.file_uploader("基本設計書をアップロード(md)", type=['md'])
    file2 = st.file_uploader("要件定義書をアップロード(md)", type=['md'])
    review_request = st.text_area("レビュー項目を入力", help="レビューで確認してほしい項目を入力してください")

# ユーザー
user = "difyuser"

# サイドバーに実行ボタンを配置
if st.sidebar.button("ワークフローを実行"):
    if file1 is not None and file2 is not None and review_request:
        with st.spinner("処理中..."):
            # ファイルをアップロード
            file_id1 = upload_file2(file1.getvalue(), file1.name, user)
            file_id2 = upload_file2(file2.getvalue(), file2.name, user)
            
            # レビュー項目をテキストファイルとしてアップロード
            review_request_id = upload_file1(review_request.encode(), "review_request.txt", user)

            if review_request_id:
                # ワークフローを実行
                result1 = run_workflow1(review_request_id, user)
                
                # 結果を表示
                st.success("ワークフローが正常に実行されました")
                st.write(result1)
                # st.write(result1["data"]["outputs"]["text"])
            
            if file_id1 and file_id2 :
                # ワークフローを実行
                result2 = run_workflow2(file_id1, file_id2, review_request_id, user)
                
                # 結果を表示
                st.success("ワークフローが正常に実行されました")
                st.write(result2)
                # st.write(result2["data"]["outputs"]["text"])
            else:
                st.error("ファイルのアップロードに失敗しました")
    else:
        st.warning("2つのファイルを選択し、レビュー項目を入力してください")
