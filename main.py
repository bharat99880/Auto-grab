import os
import re
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import InputPeerUser, UserStatusRecently, ChannelParticipantsSearch

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION_STRING")
OWNER_ID = int(os.environ.get("OWNER_ID"))

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

CHEAT_BOT = 6355945378  # @collect_waifu_cheats_bot
ALLOWED_GROUPS = set()
last_group_id = {}  # Maps forwarded message ID to group

# Read trigger lines from file
with open("triggers.txt", encoding="utf-8") as f:
    TRIGGERS = [line.strip() for line in f if line.strip()]

# Define the commands
@client.on(events.NewMessage(pattern='/xadd (\-?\d+)', from_users=OWNER_ID))
async def add_group(event):
    gid = int(event.pattern_match.group(1))
    ALLOWED_GROUPS.add(gid)
    await event.reply(f"✅ Group {gid} added.")

@client.on(events.NewMessage(pattern='/xremove (\-?\d+)', from_users=OWNER_ID))
async def remove_group(event):
    gid = int(event.pattern_match.group(1))
    ALLOWED_GROUPS.discard(gid)
    await event.reply(f"❌ Group {gid} removed.")

@client.on(events.NewMessage(pattern='/xlist', from_users=OWNER_ID))
async def list_groups(event):
    if ALLOWED_GROUPS:
        await event.reply("📋 Allowed Groups:\n" + "\n".join([str(i) for i in ALLOWED_GROUPS]))
    else:
        await event.reply("❌ No groups added.")

@client.on(events.NewMessage(pattern='/xon', from_users=OWNER_ID))
async def turn_on(event):
    global auto_grab
    auto_grab = True
    await event.reply("✅ Auto Grab is ON")

@client.on(events.NewMessage(pattern='/xoff', from_users=OWNER_ID))
async def turn_off(event):
    global auto_grab
    auto_grab = False
    await event.reply("❌ Auto Grab is OFF")

@client.on(events.NewMessage(incoming=True))
async def detect_waifu(event):
    if event.chat_id not in ALLOWED_GROUPS:
        return

    for trigger in TRIGGERS:
        if trigger in event.raw_text and auto_grab:
            try:
                fwd = await client.forward_messages(CHEAT_BOT, event.message)
                last_group_id[fwd.id] = event.chat_id
                print(f"✅ Forwarded to cheat bot from group {event.chat_id}")
            except Exception as e:
                print(f"❌ Failed to forward: {e}")
            break

@client.on(events.NewMessage(from_users=CHEAT_BOT))
async def reply_from_cheat_bot(event):
    text = event.raw_text
    match = re.search(r"Humanizer:\s*/grab\s+([a-zA-Z]+)", text)
    if not match:
        return

    first_name = match.group(1).lower()
    reply_msg = await event.get_reply_message()
    if not reply_msg or reply_msg.id not in last_group_id:
        return

    group_id = last_group_id[reply_msg.id]
    if group_id not in ALLOWED_GROUPS:
        return

    try:
        delay = random.randint(5, 10)  # Random delay between 5-10 seconds
        await asyncio.sleep(delay)
        await client.send_message(group_id, f"/grab {first_name}")
        await client.delete_messages(group_id, reply_msg)  # Auto delete after sending
        print(f"✅ Sent grab for: {first_name}")
    except Exception as e:
        print(f"❌ Error sending grab: {e}")

print("🚀 Userbot is running...")
client.start()
client.run_until_disconnected()