# This file is a part of TG-
# Coding : Jyothis Jayanth [@EverythingSuckz]


from ..vars import Var
from pyrogram import Client, utils
from os import getcwd

utils.MIN_CHANNEL_ID = -1002947483647

StreamBot = Client(
    name="WebStreamer",
    api_id=Var.API_ID,
    api_hash=Var.API_HASH,
    workdir="WebStreamer",
    plugins={"root": "WebStreamer/bot/plugins"},
    bot_token=Var.BOT_TOKEN,
    sleep_threshold=Var.SLEEP_THRESHOLD,
    workers=Var.WORKERS,
)

multi_clients = {}
work_loads = {}
