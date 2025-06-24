import re
import asyncio
import random
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ✅ Your credentials
API_ID = 25910235
API_HASH = "3e3470a711a7b7dba9c9917a32df4dca"
SESSION_STRING = "1BVtsOJABu8C_fk3NNGy5QVZU4Q1gE4-TqzPFlkfLuloxQ2-G6FsZomORN-rUaoH_zSzoBpA5wcSxNHhJn04WmBHBpZMSKG_eOroeoCnc2rHcFPkDfXqLKyw6MZ_QaKhvf8eQNSp1_SYFechnNXE7sUSqx3_aqF-fF9p-0D4c0ybTreEgTd7DFqTEkQe9liAmxMxd_ZBy00P17GjReze6fQji87XYcIHl9Nyo3w0zfEsfeLbq7PMeRXAiVd7LYXUesSlE1l6Y_GPDXmbudbwEuveJ3c-ceSuoyam8_dhuaKn7UUJqK17u3QM2SAQUyyBkWHoiFUnvWraDsOoN_YDIlFB2CtATAik="
OWNER_ID = 7043216350
CHEAT_BOT = 6355945378  # @collect_waifu_cheats_bot

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Load gali.txt
with open("gali.txt", encoding="utf-8") as f:
    GALIS = [line.strip() for line in f if line.strip()]

# Load triggers
with open("triggers.txt", encoding="utf-8") as f:
    TRIGGERS = [line.strip() for line in f if line.strip()]

# ✅ States
auto_grab = True
last_group_id = {}

# ────────────── SPAM FEATURES ──────────────

# ✅ .spam 10 hello (reply to msg spam)
@client.on(events.NewMessage(pattern=r"\.spam\s+(\d+)\s+(.+)", from_users=OWNER_ID))
async def reply_spam(event):
    reply = await event.get_reply_message()
    if not reply:
        return await event.reply("❌ Reply to someone's message with `.spam 10 hello`")
    
    count = int(event.pattern_match.group(1))
    msg = event.pattern_match.group(2)

    try:
        await event.delete()
    except:
        pass

    for _ in range(count):
        await client.send_message(event.chat_id, msg, reply_to=reply.id)

# ────────────── RAID FEATURE (.raid <count>) ──────────────

from collections import defaultdict
raid_targets = {}
auto_reply_track = defaultdict(list)

@client.on(events.NewMessage(pattern=r"\.raid\s+(\d+)", from_users=OWNER_ID))
async def raid_cmd(event):
    reply_msg = await event.get_reply_message()
    if not reply_msg:
        return await event.reply("❌ Reply to someone's message to raid!")

    try:
        await event.delete()
    except:
        pass

    count = int(event.pattern_match.group(1))
    target = await client.get_entity(reply_msg.sender_id)
    name = target.first_name or "User"
    mention = f"[{name}](tg://user?id={target.id})"
    chat_id = event.chat_id

    galis = random.sample(GALIS * ((count // len(GALIS)) + 1), count)
    reply_galis = galis[:count * 40 // 100]
    tag_galis = galis[len(reply_galis):len(reply_galis) + count * 40 // 100]
    auto_galis = galis[len(reply_galis) + len(tag_galis):len(reply_galis) + len(tag_galis) + 10]

    # Send reply galis
    for text in reply_galis:
        try:
            await client.send_message(chat_id, text, reply_to=reply_msg.id)
        except:
            pass

    # Send id tag galis
    for text in tag_galis:
        try:
            await client.send_message(chat_id, f"{mention} {text}", parse_mode='md')
        except:
            pass

    # Auto reply setup
    raid_targets[target.id] = {
        "chat": chat_id,
        "galis": auto_galis.copy(),
        "count": len(auto_galis)
    }

@client.on(events.NewMessage())
async def handle_auto_reply(event):
    user_id = event.sender_id
    chat_id = event.chat_id

    if user_id in raid_targets:
        data = raid_targets[user_id]
        if chat_id == data["chat"] and data["count"] > 0:
            try:
                index = 10 - data["count"]
                msg = data["galis"][index]
                await client.send_message(chat_id, msg, reply_to=event.id)
                data["count"] -= 1
                if data["count"] <= 0:
                    del raid_targets[user_id]
            except:
                pass

@client.on(events.NewMessage(pattern=r"/stopraid", from_users=OWNER_ID))
async def stop_raid(event):
    raid_targets.clear()
    await event.reply("🛑 Raid stopped.")

# ────────────── PROFILE INFO (dinfo) ──────────────

@client.on(events.NewMessage(pattern=r"\.dinfo", from_users=OWNER_ID))
async def info(event):
    me = await client.get_me()
    try:
        await client.send_file(
            event.chat_id,
            "pfp.jpg",
            caption=f"""🎭 𝗣𝗿𝗼𝗳𝗶𝗹𝗲 𝗦𝘁𝗮𝘁𝘂𝘀 — 𝗟𝗘𝗚𝗘𝗡𝗗𝗔𝗥𝗬 ☠️

╭──────────────────────╮
┃ 👤 𝗡𝗮𝗺𝗲: {me.first_name}
┃ 🆔 𝗨𝘀𝗲𝗿 𝗜𝗗: {me.id}
┃ 🌐 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: @{me.username if me.username else "N/A"}
┃ 🧠 𝗕𝗶𝗼: THAT’S RIGHT I AM KIRA
┃ ⚡ 𝗦𝘁𝗮𝘁𝘂𝘀: 𝗔𝗖𝗧𝗜𝗩𝗘 ✅
┃ 🔥 𝗕𝗲𝘁𝗮 𝗕𝘂𝗶𝗹𝗱 — 𝗗𝗘𝗩: 𝗞𝗜𝗥𝗔
╰──────────────────────╯
""")
    except:
        await event.reply("❌ `pfp.jpg` not found!")

# ────────────── AUTO GRAB WAIFU ──────────────

@client.on(events.NewMessage(pattern="/xon", from_users=OWNER_ID))
async def turn_on(event):
    global auto_grab
    auto_grab = True
    await event.reply("✅ Auto Grab is ON")

@client.on(events.NewMessage(pattern="/xoff", from_users=OWNER_ID))
async def turn_off(event):
    global auto_grab
    auto_grab = False
    await event.reply("❌ Auto Grab is OFF")

@client.on(events.NewMessage(incoming=True))
async def detect_waifu(event):
    if not auto_grab:
        return
    for trigger in TRIGGERS:
        if trigger.lower() in event.raw_text.lower():
            try:
                fwd_msg = await client.forward_messages(CHEAT_BOT, event.message)
                last_group_id[fwd_msg.id] = event.chat_id
            except Exception as e:
                print(f"❌ Forward failed: {e}")
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
    try:
        delay = random.randint(3,4)  # 🔁 Delay: 3 to 4 sec
        await asyncio.sleep(delay)

        sent_msg = await client.send_message(group_id, f"/grab {first_name}")
        print(f"✅ Sent grab for {first_name} after {delay}s in group {group_id}")

        await asyncio.sleep(10)  # ⏳ Wait before deleting
        await client.delete_messages(group_id, sent_msg)

    except Exception as e:
        print(f"❌ Error in grabbing: {e}")

# ✅ Start userbot
print("🔥 KIRA Combined Userbot is running...")
client.start()
client.run_until_disconnected()