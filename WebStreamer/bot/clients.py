import asyncio
import logging
import os
import base64
import requests
from ..vars import Var
from pyrogram import Client
from WebStreamer.utils import TokenParser
from . import multi_clients, work_loads, StreamBot

parser = TokenParser()
GITHUB_TOKEN = parser.get_github_token()
GITHUB_USERNAME = parser.get_github_username()
GITHUB_REPO = parser.get_github_repo()
GITHUB_API_URL = "https://api.github.com"

async def upload_to_github(file_path, repo_path):
    print(f"Uploading {file_path} to GitHub")
    url = f"{GITHUB_API_URL}/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{repo_path}"
    with open(file_path, "rb") as file:
        content = base64.b64encode(file.read()).decode()
    data = {
        "message": f"Add {repo_path}",
        "content": content,
        "branch": "main"  # Adjust the branch as needed
    }
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.put(url, json=data, headers=headers)
    response.raise_for_status()
    print(f"Uploaded {file_path} to GitHub")

async def download_from_github(repo_path, file_path):
    print(f"Downloading {repo_path} from GitHub")
    url = f"{GITHUB_API_URL}/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{repo_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = base64.b64decode(response.json()["content"])
        with open(file_path, "wb") as file:
            file.write(content)
        print(f"Downloaded {repo_path} from GitHub")
    elif response.status_code == 404:
        print(f"{repo_path} not found in GitHub")
    else:
        response.raise_for_status()

async def initialize_clients():
    multi_clients[0] = StreamBot
    work_loads[0] = 0
    all_tokens = parser.parse_from_env()
    if not all_tokens:
        print("No additional clients found, using default client")
        return

    async def start_client(client_id, token):
        try:
            print(f"Starting - Client {client_id}")
            if client_id == len(all_tokens):
                await asyncio.sleep(2)
                print("This will take some time, please wait...")
            session_name = f"client_{client_id}_session"
            session_file = f"{session_name}.session"

            # Download session file from GitHub
            await download_from_github(session_file, session_file)

            client = await Client(
                session_name=session_name,
                api_id=Var.API_ID,
                api_hash=Var.API_HASH,
                bot_token=token,
                sleep_threshold=Var.SLEEP_THRESHOLD,
                no_updates=True,
                in_memory=False
            ).start()
            work_loads[client_id] = 0

            # Upload session file to GitHub
            await upload_to_github(session_file, session_file)

            return client_id, client
        except Exception:
            logging.error(f"Failed starting Client - {client_id} Error:", exc_info=True)

    clients = await asyncio.gather(*[start_client(i, token) for i, token in all_tokens.items()])
    multi_clients.update(dict(clients))
    if len(multi_clients) != 1:
        Var.MULTI_CLIENT = True
        print("Multi-Client Mode Enabled")
    else:
        print("No additional clients were initialized, using default client")
