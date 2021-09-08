import asyncio
import sys

from pyrogram import Client, filters
from pyrogram.types import Dialog, Message

HI_BOT = "hiofficialbot"

name = sys.argv[1]
if len(sys.argv) != 2:
    print("Pass session name in arguments")
    sys.exit(1)

app = Client(name)


claim_msg = "👋 Claim Daily Reward"


async def find_hi_chat(app: Client) -> Dialog:
    async for d in app.iter_dialogs():
        if d.chat.username == HI_BOT and d.chat.type == "bot":
            print(f"Hi chat id is {d.chat.id}")
            return d


async def main() -> None:
    await app.start()

    claim_request_processed = False

    @app.on_message(filters.bot)
    def claimer(client: Client, message: Message) -> None:
        chat_id = message.chat.id
        if message.chat.username != HI_BOT:
            return
        markup = message.reply_markup
        nonlocal claim_request_processed
        if not markup and not claim_request_processed:
            rv = client.send_message(chat_id, "Replying to bot question")
            print(f"Replied to bot question, return value {rv}")
            # sometimes bot asks open ended questions and we want to reply only once
            claim_request_processed = True
            return
        keyboard = getattr(markup, "inline_keyboard", None)
        if not keyboard:
            return
        option = keyboard[0][0]
        data = option.callback_data
        if not data or data == "NICKNAME_CB":
            return
        print(f"Callback answer is {option.text}")
        rv = client.request_callback_answer(chat_id, message.message_id, data)
        claim_request_processed = True
        print(f"replied, {rv}")

    hi = await find_hi_chat(app)
    if not hi:
        raise Exception("Cannot find HI bot, ensure you started converstaion with bot")
    while True:
        print("Sending claim message")
        claim_request_processed = False
        await app.send_message(hi.chat.id, claim_msg)
        print("Sleeping for a day...")
        await asyncio.sleep(60 * 60 * 24)


app.run(main())
