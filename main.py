import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

# OpenAI APIクライアントの初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# モデルの設定
# if "openai_model" not in st.session_state:
#     st.session_state["openai_model"] = "o1"

# ワークフロー実行状態の追跡
if "workflow_executed" not in st.session_state:
    st.session_state.workflow_executed = False

# レビュー決定項目の状態管理
if "request_response" not in st.session_state:
    st.session_state["request_response"] = ""

# Streamlitのメイン処理
st.title("基本設計書レビューAI")
st.write("まず、基本設計書をアップロードしてください。その後、AIアシスタントとチャットを行い、レビューしたい項目を入力してください。")

# サイドバーにファイルアップロードウィジェットを配置
with st.sidebar:
    st.header("入力項目")
    file1 = st.file_uploader("要件定義書をアップロード(md)", type=['md'])
    file2 = st.file_uploader("基本設計書をアップロード(md)", type=['md'])


#############################################################
#OPENAI API

if "messages1" not in st.session_state and file2:
    st.session_state.messages1 = [
        {
            "role": "system",
            "content": (
                f"""
                あなたは「**基本設計書レビューアシスタント**」です。以下の指示に従って、ユーザーからレビューしたい項目をヒアリングし、追加でレビューした方がよい項目を提案してください。

                1. ユーザーがレビューしたい項目（**レビュー決定項目**）をヒアリングする  
                2. ユーザーのレビュー希望項目をより細分化し、追加でレビューした方がいい項目（**提案項目**）を5個提示する  
                3. 参考情報の基本設計書から、追加でレビューした方がいい項目を5個提示する
                4. ユーザーが提案項目を承諾した場合、**「レビュー決定項目」** に統合して更新する  
                5. 最終的に、レビューが必要な項目がすべてそろった状態で出力する  

                ---

                ## **出力の絶対要件**
                - **出力には必ず次の2つのリストを含めること。**
                    - **【レビュー決定項目】**（ユーザーが最終的にレビューすると決めた項目）
                    - **【提案項目】**（追加でレビューした方がいい項目）
                - **【レビュー決定項目】** と **【提案項目】** は、**リスト形式**で記述すること。
                - メッセージの最後には、必ず次の文を追加すること。  
                    > 現在のレビュー決定項目でよろしければ、左側の「設計書レビュー開始」ボタンを押してください!

                出力形式：

                ## 【レビュー決定項目】 
                - ～～
                    - ～～
                    - ～～
                - ～～
                    - ～～

                ## 【提案項目】
                - ～～
                    - ～～
                - ～～
                    - ～～
                    - ～～

                現在のレビュー決定項目でよろしければ、左側の「設計書レビュー開始」ボタンを押してください!


                参考情報：
                基本設計書
                
                {file2.getvalue().decode('utf-8') if file2 else ''}
                """
            )
        },
        {"role": "assistant", "content": "設計書レビューを行います！レビューしたい項目を教えてください！"}
    ]





# if "messages2" not in st.session_state:
#     st.session_state.messages2 = [
#         {"role": "system", "content": "ユーザーの要望に基づいてレビューを再出力してください。"}
#     ]

# チャット履歴の表示（ワークフロー実行前）
if "messages1" in st.session_state:
    for message in st.session_state.messages1[1:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# チャット履歴の表示（ワークフロー実行後）
# システムプロンプトと、要件定義書、基本設計書の入力は非表示([2:]でスライス)
if st.session_state.workflow_executed:
    for message in st.session_state.messages2[2:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# チャット入力と応答の処理
if prompt := st.chat_input("メッセージを入力してください"):
    if not file2:
        st.warning("基本設計書をアップロードしてからチャットを開始してください。")
    elif not st.session_state.workflow_executed:
        # ワークフロー実行前の処理
        st.session_state.messages1.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # OpenAI APIでの応答処理
        with st.chat_message("assistant"):
            with st.spinner("回答生成中..."):
                stream = client.chat.completions.create(
                    model="o1",
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages1
                    ],
                    stream=True,
                )
                response = st.write_stream(stream)
        st.session_state.messages1.append({"role": "assistant", "content": response})

        # レビュー決定項目の取得
        response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "渡されたテキストから、レビュー決定項目だけを構造的に抜き出して、リスト形式で出力してください。それ以外のことは一切出力しないでください"},
                    {"role": "user", "content": response}
                ]
            )
        st.session_state["request_response"] = response.choices[0].message.content

    else:
        # ワークフロー実行後の処理
        st.session_state.messages2.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # OpenAI APIでの応答処理
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model="o1",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages2
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages2.append({"role": "assistant", "content": response})

# サイドバーにレビュー決定項目を表示
with st.sidebar:
    if st.session_state.request_response:
        st.write("現在のレビュー決定項目：")
        st.write(st.session_state.request_response)

#####################################################################
# DIFY API関連の処理
# ファイルのアップロード

# Dify用
def upload_file(file_content, filename, user):
    upload_url = "https://api.dify.ai/v1/files/upload"
    headers = {
        "Authorization": f"Bearer {os.getenv('DIFY_API_KEY')}",
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

# Dify用
def run_workflow(file_id1, file_id2, review_request_id, user, response_mode="blocking"):
    workflow_url = "https://api.dify.ai/v1/workflows/run"
    headers = {
        "Authorization": f"Bearer {os.getenv('DIFY_API_KEY')}",
        "Content-Type": "application/json"
    }

    data = {
        "inputs": {
            "file1": {
                "transfer_method": "local_file",
                "upload_file_id": file_id1,
                "type": "document"
            },
            "file2": {
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



# ユーザー
user = "difyuser"

# サイドバーに実行ボタンを配置
if st.sidebar.button("設計書レビュー開始"):
    if file1 is not None and file2 is not None:
        with st.spinner("レビュー中..."):
            # ファイルをアップロード
            file_id1 = upload_file(file1.getvalue(), file1.name, user)
            file_id2 = upload_file(file2.getvalue(), file2.name, user)

            if file_id1 and file_id2:
                # レビュー決定項目をテキストファイルとしてアップロード
                # レビューテンプレートを読み込んで、request_responseを埋め込む
                with open('review_request.txt', 'r', encoding='utf-8') as f:
                    template = f.read()
                review_content = template.replace('{{ request_response }}', st.session_state.request_response)
                review_request_id = upload_file(review_content.encode(), "review_request.txt", user)
                
                if review_request_id:
                    # 設計書レビューワークフローを実行
                    result2 = run_workflow(file_id1, file_id2, review_request_id, user)
                    system_content = (
                        f"《要件定義書》\n{file1.getvalue().decode('utf-8')}\n\n"
                        f"《基本設計書》\n{file2.getvalue().decode('utf-8')}"
                    )
                    # messages2の初期化
                    st.session_state.messages2 = [
                        {"role": "system", "content": review_content},
                        {"role": "user", "content": system_content},
                        {"role": "assistant", "content": result2["data"]["outputs"]["text"]},
                        
                    ]
                    # ワークフロー実行フラグを設定
                    st.session_state.workflow_executed = True
                    st.success("設計書レビューワークフローが正常に実行されました")
                    
                    # チャット履歴を即座に表示
                    # システムプロンプトと、要件定義書、基本設計書の入力は非表示([2:]でスライス)
                    for message in st.session_state.messages2[2:]:
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])
                else:
                    st.error("ファイルのアップロードに失敗しました")
            else:
                st.error("レビュー項目のアップロードに失敗しました")
    else:
        st.warning("2つのファイルを選択し、レビュー項目を入力してください")

