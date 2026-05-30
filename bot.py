import asyncio
import time
import random
import sqlite3
import html
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from aiohttp import web
import os

# ==================== CONFIG ====================
BOT_TOKEN = "8899146901:AAHenfTssLA6krnnaxFunQ3-jzIhLoeb9N4"
OWNER_ID = 8962957839
CO_OWNER_ID = 8722144519
BOT_USERNAME = "ITACHI_X_ARCH_bot"
PORT = int(os.environ.get("PORT", 8080))

# ==================== DATABASE ====================
db = sqlite3.connect("bot_data.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS sudo (user_id INTEGER PRIMARY KEY)")
cursor.execute("CREATE TABLE IF NOT EXISTS mute (user_id INTEGER PRIMARY KEY)")
cursor.execute("CREATE TABLE IF NOT EXISTS stickers (file_id TEXT PRIMARY KEY)")
cursor.execute("CREATE TABLE IF NOT EXISTS warnings (user_id INTEGER, count INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS banned (user_id INTEGER PRIMARY KEY)")
db.commit()

# ==================== GLOBAL VARIABLES ====================
raid_active = False
current_raid_chat = None
current_raid_target = None
bot_start_time = datetime.now()

# ==================== LOGGING ====================
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== RAID LINES ====================
RAID_LINES = [
    "ke samne koi bol sakta hai kya? 😭👑",
    "Aukat me rehna seekh le abhi bhi waqt hai! 🔥⚡",
    "Ab tera chat se gayab hone ka samay aa gaya hai! ☣️💀",
    "Beta, baap se panga nahi lete, samjhe? ⚔️",
    "Tera system hang kar denge beta! 🔥🤖",
    "Aaj teri aukat dikha denge! 💥🌟",
    "Bhag jaa yahan se! 🗑️🚶",
    "Itachi aur Geto ka order hai! 👑👑""TERI MUMMY KI CHUT!",
"BAHEN KE LODE TERI DADI KI BLACK HAIRY PUSSY",
"TERI MUMMY KO ULTA LTKAKR TAANGDUGA AUR USKI CHUT MARUNGA!",
"BSDK TERI MUMMY TERI DADI SB RANDI KI BACHI H",
"BAHENKLODO TUMHARI MAA MERI SETTING",
"TERI MUMMY RANDI H RANDI BSDK",
"TERI MUMMY KI PUSSY M SCOOTER DALDUGA",
"TERI MUMMY KI PUSSY ME CUM KRODUGA RANDI MAA K BACHE",
"TERA KHANDAN HI RANDIYO KA H",
"TERI DADI KI PUSSY ME MERA LUND",
"TERI MUMMY KO CHODKR ULTA LTKAKR USKE MUH ME LODA DEDUGA",
"TERI MUMMY KO DEEPTHROAT DEDUGA MADARCHOD K BACHE",
"TERA PAPA BHI RANDI KI AULAD H BSDK",
"TERI MUMMY KO YOGA SIKHADUGA AUR USKO DIFFERENT STYLES ME CHODUGA",
"TERA PAPA HU MAI TERI MUMMY KA BF JIS S VO CHUDKR GYI THI",
"TERI MAA KI PUSSY ME SCOOTER DALDUGA BAHEN KE LODE",
"TERI MAA KI CHUT ME BIHARI GUTKA KHAKR THUK KR CHALE GYE THE",
"TERI MAA KA BOSDA RANDI K BEEJ",
"TERI MAA KI CHUT ME 2 FINGER DEKR USKA PAANI NIKALDUGA",
"TERI MAA K MUH ME GAS PIPE DEKR USKI GAAND ME FIRE LGAKR TERE BAAP KI GAAND JALAUGA",
"TERI RANDI MAA KO CHODKR MAINE GB ROAD PR BEACH DIYA THA",
"TERI MUMMY K HAATH DIVAR PR LGVADIYE THE 10 BIHARIYO NE",
"TERI MAA KO TORRENT BANAKER SEED KAR DUNGA",
"TERI MAA KE BHOSDE ME FIREWALL LAGA DUNGA",
"TERI MAA KI CHUT ME SSD BOOT KAR DUNGA",
"TERI MAA BHOSDE ME NFT MINT KAR DUNGA",
"TERI MAA KA LUND OLX PE BECH DUNGA",
"TERI MAA KI GAAND ME QR CODE CHIPKA DUNGA",
"TERI MAA KA ONLYFANS LIVE KAR DUNGA",
"TERI LAGE KO TORRENT BANAKER SEED KAR DUNGA",
"TERI LAGE KE BHOSDE ME FIREWALL LAGA DUNGA",
"TERI LAGE KI CHUT ME SSD BOOT KAR DUNGA",
"TERI BEHEN KO TORRENT BANAKER SEED KAR DUNGA",
"TERI BEHEN KE BHOSDE ME FIREWALL LAGA DUNGA",
"TERI BEHEN KI CHUT ME SSD BOOT KAR DUNGA",
"TERI BEHEN KA LUND OLX PE BECH DUNGA",
"TERI BEHEN KI GAAND ME QR CODE CHIPKA DUNGA",
"TERI BEHEN KA BHOSDA NFT ME MINT KAR DUNGA",
"TERI BEHEN KA ONLYFANS LIVE KAR DUNGA",
"TERI BEHEN KO ZIP FILE ME COMPRESS KAR DUNGA",
"TERI BEHEN KE BHOSDE ME PYTHON RUN KAR DUNGA",
"TERI BEHEN KE LODE KO AIRDROP KAR DUNGA",
"TERI BEHEN KO BARCODE LAGA KE SCAN KARWA DUNGA",
"TERI BEHEN KO AI TOOL SE UPSCALE KAR DUNGA",
"TERE BAAP KO TORRENT BANAKER SEED KAR DUNGA",
"TERE BAAP KE BHOSDE ME FIREWALL LAGA DUNGA",
"TERE BAAP KI CHUT ME SSD BOOT KAR DUNGA",
"TERE BAAP KA LUND OLX PE BECH DUNGA",
"TERE BAAP KI GAAND ME QR CODE CHIPKA DUNGA",
"TERE BAAP KA BHOSDA NFT ME MINT KAR DUNGA",
"TERE BAAP KA ONLYFANS LIVE KAR DUNGA",
"TERE BAAP KO ZIP FILE ME COMPRESS KAR DUNGA",
"TERE BAAP KE BHOSDE ME PYTHON RUN KAR DUNGA",
"TERE BAAP KE LODE KO AIRDROP KAR DUNGA",
"TERE BAAP KO BARCODE LAGA KE SCAN KARWA DUNGA",
"TERE BAAP KO AI TOOL SE UPSCALE KAR DUNGA",
"TERI FAMILY KO TORRENT BANAKER SEED KAR DUNGA",
"TERI FAMILY KE BHOSDE ME FIREWALL LAGA DUNGA",
"TERI FAMILY KI CHUT ME SSD BOOT KAR DUNGA",
"TERI FAMILY KA LUND OLX PE BECH DUNGA",
"TERI FAMILY KI GAAND ME QR CODE CHIPKA DUNGA",
"TERI FAMILY KA BHOSDA NFT ME MINT KAR DUNGA",
"TERI FAMILY KA ONLYFANS LIVE KAR DUNGA",
"TERI FAMILY KO ZIP FILE ME COMPRESS KAR DUNGA",
"TERI FAMILY KE BHOSDE ME PYTHON RUN KAR DUNGA",
"TERI FAMILY KE LODE KO AIRDROP KAR DUNGA",
"TERI FAMILY KO BARCODE LAGA KE SCAN KARWA DUNGA",
"TERI FAMILY KO AI TOOL SE UPSCALE KAR DUNGA",
"TERE KUTTE KO TORRENT BANAKER SEED KAR DUNGA",
"TERE KUTTE KE BHOSDE ME FIREWALL LAGA DUNGA",
"TERE KUTTE KI CHUT ME SSD BOOT KAR DUNGA",
"TERE KUTTE KA LUND OLX PE BECH DUNGA",
"TERE KUTTE KI GAAND ME QR CODE CHIPKA DUNGA",
"TERE KUTTE KA BHOSDA NFT ME MINT KAR DUNGA",
"TERE KUTTE KA ONLYFANS LIVE KAR DUNGA",
"TERE KUTTE KO ZIP FILE ME COMPRESS KAR DUNGA",
"TERE KUTTE KE BHOSDE ME PYTHON RUN KAR DUNGA",
"TERE KUTTE KE LODE KO AIRDROP KAR DUNGA",
"TERE KUTTE KO BARCODE LAGA KE SCAN KARWA DUNGA",
"TERE KUTTE KO AI TOOL SE UPSCALE KAR DUNGA",
"TERI AUKAAT KO TORRENT BANAKER SEED KAR DUNGA",
"TERI AUKAAT KE BHOSDE ME FIREWALL LAGA DUNGA",
"TERI AUKAAT KI CHUT ME SSD BOOT KAR DUNGA",
"TERI AUKAAT KA LUND OLX PE BECH DUNGA",
"TERI AUKAAT KI GAAND ME QR CODE CHIPKA DUNGA",
"TERI AUKAAT KA BHOSDA NFT ME MINT KAR DUNGA",
"TERI AUKAAT KA ONLYFANS LIVE KAR DUNGA",
"TERI AUKAAT KO ZIP FILE ME COMPRESS KAR DUNGA",
"TERI AUKAAT KE BHOSDE ME PYTHON RUN KAR DUNGA",
"TERI AUKAAT KE LODE KO AIRDROP KAR DUNGA",
"TERI AUKAAT KO BARCODE LAGA KE SCAN KARWA DUNGA",
"TERI AUKAAT KO AI TOOL SE UPSCALE KAR DUNGA",
"TERI MUMMY KO TORRENT BANAKER SEED KAR DUNGA",
"TERI MUMMY KE BHOSDE ME FIREWALL LAGA DUNGA",
"TERI MUMMY KI CHUT ME SSD BOOT KAR DUNGA",
"TERI MUMMY KA LUND OLX PE BECH DUNGA",
"TERI MUMMY KI GAAND ME QR CODE CHIPKA DUNGA",
"TERI MUMMY KA BHOSDA NFT ME MINT KAR DUNGA",
"TERI MUMMY KA ONLYFANS LIVE KAR DUNGA",
"TERI MUMMY KO ZIP FILE ME COMPRESS KAR DUNGA",
"TERI MUMMY KE BHOSDE ME PYTHON RUN KAR DUNGA",
"TERI MUMMY KE LODE KO AIRDROP KAR DUNGA",
"TERI MUMMY KO BARCODE LAGA KE SCAN KARWA DUNGA",
"TERI MUMMY KO AI TOOL SE UPSCALE KAR DUNGA",
"TERE DADA KO TORRENT BANAKER SEED KAR DUNGA",
"TERE DADA KE BHOSDE ME FIREWALL LAGA DUNGA",
"TERE DADA KI CHUT ME SSD BOOT KAR DUNGA",
"TERE DADA KA LUND OLX PE BECH DUNGA",
"TERE DADA KI GAAND ME QR CODE CHIPKA DUNGA",
"TERE DADA KA BHOSDA NFT ME MINT KAR DUNGA",
"TERE DADA KA ONLYFANS LIVE KAR DUNGA",
"TERE DADA KO ZIP FILE ME COMPRESS KAR DUNGA",
"TERE DADA KE BHOSDE ME PYTHON RUN KAR DUNGA",
"TERE DADA KE LODE KO AIRDROP KAR DUNGA",
"TERE DADA KO BARCODE LAGA KE SCAN KARWA DUNGA",
"TERE DADA KO AI TOOL SE UPSCALE KAR DUNGA"
]

# ==================== UNAUTH ROASTS ====================
UNAUTH_ROASTS = [
    "🚫 ACCESS DENIED 🚫\n\nSirf Itachi aur Geto ke launde yahan command chala sakte hain!\nTeri aukat: 0%",
    "⚠️ INTRUDER ALERT ⚠️\n\nTu kaun hai bhosdike? Ye bot ITACHI X GETO ka hai!\nPermission le pehle! 🍼",
    "🔴 SECURITY BREACH 🔴\n\nUnauthorized access detected!\nOwner: ITACHI\nCo-Owner: GETO 👑"
]

# ==================== COMMAND LIST ====================
COMMAND_REGISTRY = {
    ".alive": "🔥 System Status",
    ".mute": "🔇 Silence Protocol",
    ".unmute": "🔊 Voice Restore",
    ".raid": "💣 Mass Destruction",
    ".stop": "🛑 Emergency Halt",
    ".s": "🛑 Quick Halt",
    ".sudo": "👑 God Mode",
    ".addsticker": "📦 Sticker Add",
    ".reset": "🔄 Factory Reset",
    ".stickers": "🎨 Sticker Pack",
    ".warn": "⚠️ Warning",
    ".warns": "📊 Warnings",
    ".ban": "🔨 Ban",
    ".unban": "🔓 Unban",
    ".speed": "⚡ Speed Test",
    ".ping": "📡 Ping",
    ".stats": "📈 Statistics"
}

# ==================== HELPER FUNCTIONS ====================
def is_sudo(user_id):
    cursor.execute("SELECT user_id FROM sudo WHERE user_id=?", (user_id,))
    return cursor.fetchone() is not None

def is_muted(user_id):
    cursor.execute("SELECT user_id FROM mute WHERE user_id=?", (user_id,))
    return cursor.fetchone() is not None

def is_banned(user_id):
    cursor.execute("SELECT user_id FROM banned WHERE user_id=?", (user_id,))
    return cursor.fetchone() is not None

def is_supreme(user_id):
    return user_id == OWNER_ID or user_id == CO_OWNER_ID

def is_authorized(user_id):
    return is_supreme(user_id) or is_sudo(user_id)

def get_warnings(user_id):
    cursor.execute("SELECT count FROM warnings WHERE user_id=?", (user_id,))
    res = cursor.fetchone()
    return res[0] if res else 0

# ==================== DASHBOARD ====================
def get_dashboard():
    keyboard = [
        [InlineKeyboardButton("⚡ ADD TO GROUP ⚡", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
        [InlineKeyboardButton("👑 OWNERS", callback_data="owners"), 
         InlineKeyboardButton("📜 COMMANDS", callback_data="commands"),
         InlineKeyboardButton("📊 STATS", callback_data="stats")],
        [InlineKeyboardButton("🎨 STICKERS", callback_data="stickers"),
         InlineKeyboardButton("💀 RAID INFO", callback_data="raidinfo"),
         InlineKeyboardButton("⚙️ BOT INFO", callback_data="botinfo")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ==================== RAID TASK EXECUTION ====================
async def run_raid_operation(context: ContextTypes.DEFAULT_TYPE):
    global raid_active, current_raid_chat, current_raid_target
    idx = 0
    while raid_active and current_raid_target:
        try:
            line = RAID_LINES[idx % len(RAID_LINES)]
            mention = f'<a href="tg://user?id={current_raid_target.id}">{html.escape(current_raid_target.first_name)}</a>'
            payload = f"{mention} {line}"
            await context.bot.send_message(chat_id=current_raid_chat, text=payload, parse_mode="HTML")
            idx += 1
            await asyncio.sleep(0.22)
        except Exception as e:
            logger.error(f"Active Raid Loop Exception: {e}")
            await asyncio.sleep(0.5)

# ==================== STICKER PACK SENDER ====================
async def send_stickers(chat_id, context, count=10):
    cursor.execute("SELECT file_id FROM stickers")
    stickers = cursor.fetchall()
    if not stickers:
        return 0
    sent = 0
    for sticker in stickers[:count]:
        try:
            await context.bot.send_sticker(chat_id=chat_id, sticker=sticker[0])
            await asyncio.sleep(0.25)
            sent += 1
        except Exception:
            pass
    return sent

# ==================== CALLBACK QUERY CONTROLLER ====================
async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "owners":
        text = f"👑 <b>SUPREME OWNERS MATRIX</b> 👑\n\n• Owner: <a href='tg://user?id={OWNER_ID}'>Itachi</a>\n• Co-Owner: <a href='tg://user?id={CO_OWNER_ID}'>Geto</a>\n\nStatus: Absolute Core Dominance Active."
        await query.edit_message_text(text, parse_mode="HTML")
    elif query.data == "commands":
        text = "📜 <b>COMMAND CATALOGUE MODULE</b> 📜\n\n"
        for cmd, desc in COMMAND_REGISTRY.items():
            text += f"• <code>{cmd}</code> ➔ <b>{desc}</b>\n"
        await query.edit_message_text(text, parse_mode="HTML")
    elif query.data == "stats":
        cursor.execute("SELECT COUNT(*) FROM sudo")
        sudo_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM mute")
        mute_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM stickers")
        sticker_count = cursor.fetchone()[0]
        uptime = datetime.now() - bot_start_time
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        text = f"📊 <b>REAL-TIME MONITOR LOGS</b> 📊\n\n• Sudo Layers: <code>{sudo_count}</code>\n• Restricted Nodes: <code>{mute_count}</code>\n• Buffers: <code>{sticker_count}</code>\n• Engine Uptime: <code>{hours}h {minutes}m</code>"
        await query.edit_message_text(text, parse_mode="HTML")
    elif query.data == "stickers":
        cursor.execute("SELECT COUNT(*) FROM stickers")
        count = cursor.fetchone()[0]
        text = f"🎨 <b>STORAGE REPOSITORY (STICKERS)</b> 🎨\n\n• Total Synced Pack: <code>{count}</code>\n\nUse <code>.stickers</code> inside chat to dump packet data."
        await query.edit_message_text(text, parse_mode="HTML")
    elif query.data == "raidinfo":
        text = f"💀 <b>OBLITERATION SUITE PARAMETERS</b> 💀\n\n• Throttle Speed: <code>LIGHTSPEED MAXIMUM (0.22s)</code>\n• Protocol: <code>Clean Mention Matrix Link</code>\n• Kill-Switches: <code>.stop</code> | <code>.s</code>\n• Total Lines: <code>{len(RAID_LINES)}</code>"
        await query.edit_message_text(text, parse_mode="HTML")
    elif query.data == "botinfo":
        text = "⚙️ <b>ENGINE ARCHITECTURE CONFIG</b> ⚙️\n\n• Operational Prefix: <code>.</code>\n• Structure Security: <code>KERNEL VERIFIED OVERRIDE</code>\n• Version State: <code>9.0 Premium Matrix Terminal</code>"
        await query.edit_message_text(text, parse_mode="HTML")

# ==================== MAIN CORE MESSAGE ROUTER ====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global raid_active, current_raid_chat, current_raid_target
    
    if not update.message:
        return
        
    user = update.message.from_user
    chat_id = update.effective_chat.id
    text = update.message.text.strip() if update.message.text else ""
    
    # 1. Absolute Filters (Ban/Mute Stream Cleansing)
    if (is_banned(user.id) or is_muted(user.id)) and not is_supreme(user.id):
        try:
            await update.message.delete()
        except Exception:
            pass
        return
        
    # /start Entry Point Handler
    if text == "/start":
        start_msg = "🤖 <b>CYBER CORE ARCHITECTURE ACTIVE</b> 🤖\n\n• Owner Cluster: <b>ITACHI</b>\n• Sub-Owner Layer: <b>GETO</b>\n• Engine State: <b>ULTRA PRO MAX HIGH LATENCY SPEED</b>\n\nSelect operation node below:"
        await update.message.reply_text(start_msg, reply_markup=get_dashboard(), parse_mode="HTML")
        return
        
    # 2. Strict Prefix Trigger Evaluation
    if not text.startswith('.'):
        return
        
    parts = text.split(maxsplit=1)
    command = parts[0].lower()
    
    if command not in COMMAND_REGISTRY:
        await update.message.reply_text(f"❓ <b>UNKNOWN PACKET</b> ❓\n\n<code>{command}</code> does not exist inside internal core. Type <code>.commands</code> for options.", parse_mode="HTML")
        return
        
    # 3. Execution Signal Processing Notification
    try:
        processing_signal = await update.message.reply_text(f"<code>⚡ [INITIALIZING MODULE]: Executing '{command}' stream...</code>", parse_mode="HTML")
        await asyncio.sleep(0.3)
        await processing_signal.delete()
    except Exception:
        pass
        
    # 4. Global Security Verification Barrier
    if not is_authorized(user.id):
        roast = random.choice(UNAUTH_ROASTS)
        await update.message.reply_text(roast)
        return
        
    # ==================== CONTROLLER COMMAND LOGIC ====================
    try:
        # Emergency Stops (.stop / .s)
        if command in [".stop", ".s"]:
            if raid_active:
                raid_active = False
                current_raid_chat = None
                current_raid_target = None
                await update.message.reply_text("🛑 <b>[ HARDWARE OVERRIDE TRIGGERED ]</b>\n\nAll current continuous loops and raid channels frozen completely!", parse_mode="HTML")
            else:
                await update.message.reply_text("⚠️ <b>SYSTEM IDLE</b>: No loops are running at the moment.", parse_mode="HTML")
            return

        elif command == ".reset":
            if not is_supreme(user.id):
                await update.message.reply_text("❌ <b>Unauthorized Authorization Matrix Reset. Option limited to absolute deities.</b>", parse_mode="HTML")
                return
            raid_active = False
            current_raid_chat = None
            current_raid_target = None
            cursor.execute("DELETE FROM sudo")
            cursor.execute("DELETE FROM mute")
            cursor.execute("DELETE FROM warnings")
            cursor.execute("DELETE FROM banned")
            db.commit()
            await update.message.reply_text("🔄 <b>[ SYSTEM RESET MATRIX INJECTED ]</b>\n\nMemory registries wiped. Factory configurations re-allocated successfully.", parse_mode="HTML")
            return

        elif command == ".alive":
            load_msg = await update.message.reply_text("<code>🚨 INITIALIZING DEEP SYSTEM SCAN: [░░░░░░░░░░] 0%</code>", parse_mode="HTML")
            animation_frames = [
                ("<code>🚨 INJECTING MALWARE TO MAIN REPO: [██░░░░░░░░] 20%</code>", 0.7),
                ("<code>🚨 RE-ROUTING PROXY FIREWALL:      [█████░░░░░] 50%</code>", 0.7),
                ("<code>🚨 BYPASSING TELEGRAM PROTOCOLS:  [████████░░] 80%</code>", 0.7),
                ("<code>🚨 OVERLORD ACCESS DECRYPTED:      [██████████] 100%</code>", 0.6)
            ]
            for frame_text, frame_delay in animation_frames:
                await asyncio.sleep(frame_delay)
                await load_msg.edit_text(frame_text, parse_mode="HTML")
                
            await asyncio.sleep(0.4)
            alive_payload = (
                f"👑 <b>🔥 BOT IS ACTIVE WITH PEAK INTEL 🔥</b> 👑\n\n"
                f"⚡ <b>Owner Matrix:</b> <a href='tg://user?id={OWNER_ID}'>Itachi Sama</a>\n"
                f"⚡ <b>Co-Owner Layer:</b> <a href='tg://user?id={CO_OWNER_ID}'>Geto Sama</a>\n\n"
                f"📡 <b>Status Level:</b> <code>ULTRA HIGH SPEED ACTIVE MODE</code>"
            )
            await load_msg.edit_text(alive_payload, parse_mode="HTML")
            return

        elif command == ".mute":
            if not update.message.reply_to_message:
                await update.message.reply_text("❌ Reply to a target node to deploy silence parameters.")
                return
            target = update.message.reply_to_message.from_user
            if is_supreme(target.id):
                await update.message.reply_text("🤬 **Trying to mute the Creators? Keep dreaming, kid.**")
                return
                
            load_msg = await update.message.reply_text("<code>🔇 DECOUPLING TARGET CONNECTION PIPELINE... [□□□□]</code>", parse_mode="HTML")
            mute_frames = [
                ("<code>🔇 ERASING CHAT PERMISSIONS BUFFER...   [■■□□] 50%</code>", 0.8),
                ("<code>🔇 ISOLATING DATAFRAME CHANNELS...       [■■■■] 100%</code>", 0.8)
            ]
            for m_text, m_delay in mute_frames:
                await asyncio.sleep(m_delay)
                await load_msg.edit_text(m_text, parse_mode="HTML")

            cursor.execute("INSERT OR IGNORE INTO mute VALUES (?)", (target.id,))
            db.commit()
            
            destruction_text = (
                f"⚡ <b>[ CONTEXT PROTOCOL: TOTAL ERADICATION ]</b> ⚡\n\n"
                f"👑 <b>Supreme Commands Dispensed By:</b> <a href='tg://user?id={OWNER_ID}'>Itachi</a> & <a href='tg://user?id={CO_OWNER_ID}'>Geto</a>\n\n"
                f"☣️ Target node <a href='tg://user?id={target.id}'>{html.escape(target.first_name)}</a> has been dropped inside absolute dark space. "
                f"Every message emitted by this user from now on will be instantly disintegrated into void data packets! 💀"
            )
            await load_msg.edit_text(destruction_text, parse_mode="HTML")
            return

        elif command == ".unmute":
            if not update.message.reply_to_message:
                await update.message.reply_text("❌ Reply to an inactive target node to restore stream.")
                return
            target = update.message.reply_to_message.from_user
            cursor.execute("DELETE FROM mute WHERE user_id=?", (target.id,))
            db.commit()
            await update.message.reply_text(f"🔊 <b>[ SIGNAL OVERRIDE RESTORED ]</b>\n\nUser <a href='tg://user?id={target.id}'>{html.escape(target.first_name)}</a> data stream restored. Messages enabled.", parse_mode="HTML")
            return

        elif command == ".sudo":
            if not update.message.reply_to_message:
                await update.message.reply_text("❌ Reply to a profile node to evaluate sudo authorization.")
                return
            target = update.message.reply_to_message.from_user
            
            if is_supreme(target.id):
                if is_sudo(user.id):
                    cursor.execute("DELETE FROM sudo WHERE user_id=?", (user.id,))
                cursor.execute("INSERT OR IGNORE INTO mute VALUES (?)", (user.id,))
                db.commit()
                
                insult = (
                    f"🚫 <b>[ ABSOLUTE BREACH PROTECTION DETECTED ]</b> 🚫\n\n"
                    f"Launde <a href='tg://user?id={user.id}'>{html.escape(user.first_name)}</a>, teri itni himmat ki tu absolute gods (<a href='tg://user?id={OWNER_ID}'>Itachi</a> / <a href='tg://user?id={CO_OWNER_ID}'>Geto</a>) ke upar authority command chalayega?\n\n"
                    f"💀 <b>TERI SUDO PERMISSION INSTANTLY STRIPPED AND NODE DROPPED INTO ABSOLUTE SILENCE LAYER!</b>"
                )
                await update.message.reply_text(insult, parse_mode="HTML")
                return

            cursor.execute("INSERT OR IGNORE INTO sudo VALUES (?)", (target.id,))
            db.commit()
            await update.message.reply_text(f"⚡ <b>[ SUDO CLUSTER ELEVATION ]</b>\n\nNode <a href='tg://user?id={target.id}'>{html.escape(target.first_name)}</a> has been verified and added to active sudo authorization matrices.", parse_mode="HTML")
            return

        elif command == ".stickers":
            await update.message.reply_text("🎨 <i>Dumping synced sticker stream packets...</i>", parse_mode="HTML")
            sent = await send_stickers(chat_id, context, 10)
            if sent > 0:
                await update.message.reply_text(f"✅ <b>Data verification complete: [{sent}/10] sticker arrays deployed inside chat instance.</b>", parse_mode="HTML")
            else:
                await update.message.reply_text("❌ <b>Packet empty. Use <code>.addsticker</code> to parse raw data.</b>", parse_mode="HTML")
            return

        elif command == ".addsticker":
            if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
                await update.message.reply_text("❌ Reply to a raw active sticker payload to copy signature.")
                return
            stk_id = update.message.reply_to_message.sticker.file_id
            cursor.execute("INSERT OR IGNORE INTO stickers VALUES (?)", (stk_id,))
            db.commit()
            cursor.execute("SELECT COUNT(*) FROM stickers")
            count = cursor.fetchone()[0]
            await update.message.reply_text(f"📦 <b>[ PACK SYNC COMPLETE ]</b>\n\nSticker parsed successfully into binary storage nodes. Total synced: <code>{count}</code>", parse_mode="HTML")
            return

        elif command == ".raid":
            if not update.message.reply_to_message:
                await update.message.reply_text("❌ Reply to a target profile to deploy targeted execution loops.")
                return
            if raid_active:
                await update.message.reply_text("⚠️ **Active raid threads are already running. Execute `.stop` first.**")
                return
            target = update.message.reply_to_message.from_user
            raid_active = True
            current_raid_chat = chat_id
            current_raid_target = target
            await update.message.reply_text(f"💣 <b>[ LIGHTSPEED REAL-TAG PROTOCOL INJECTED ]</b>\n\nTargeting: <a href='tg://user?id={target.id}'>{html.escape(target.first_name)}</a>\nSpeed Matrix: <code>MAX THROTTLE ACTIVE</code>", parse_mode="HTML")
            asyncio.create_task(run_raid_operation(context))
            return

        elif command == ".warn":
            if not update.message.reply_to_message:
                await update.message.reply_text("❌ Reply to a profile to issue system anomalies.")
                return
            target = update.message.reply_to_message.from_user
            if is_supreme(target.id):
                await update.message.reply_text("🤬 **Creators do not accept system error codes.**")
                return
            current_warns = get_warnings(target.id) + 1
            cursor.execute("INSERT OR REPLACE INTO warnings VALUES (?, ?)", (target.id, current_warns))
            db.commit()
            if current_warns >= 3:
                cursor.execute("INSERT OR IGNORE INTO mute VALUES (?)", (target.id,))
                db.commit()
                await update.message.reply_text(f"⚠️ <b>[ LIMIT EXCEEDED - AUTO MUTED ]</b>\n\nNode: <a href='tg://user?id={target.id}'>{html.escape(target.first_name)}</a>\nLog Records: <code>{current_warns}/3</code> status downgraded to MUTED.", parse_mode="HTML")
            else:
                await update.message.reply_text(f"⚠️ <b>[ INTRUSION LOG REGISTERED ]</b>\n\nTarget Node: <a href='tg://user?id={target.id}'>{html.escape(target.first_name)}</a>\nSystem Violations: <code>{current_warns}/3</code>", parse_mode="HTML")
            return

        elif command == ".warns":
            if not update.message.reply_to_message:
                await update.message.reply_text("❌ Reply to a profile to scan records.")
                return
            target = update.message.reply_to_message.from_user
            warns = get_warnings(target.id)
            muted_status = "RESTRICTED (MUTED)" if is_muted(target.id) else "PERMITTED (ACTIVE)"
            await update.message.reply_text(f"📊 <b>HARDWARE SYSTEM LOG PROFILE</b>\n\n• User Name: <a href='tg://user?id={target.id}'>{html.escape(target.first_name)}</a>\n• Anomalies Stored: <code>{warns}/3</code>\n• Network Flow State: <b>{muted_status}</b>", parse_mode="HTML")
            return

        elif command == ".ban":
            if not is_supreme(user.id):
                await update.message.reply_text("❌ <b>Access restricted. Function bound to higher admin modules.</b>")
                return
            if not update.message.reply_to_message:
                await update.message.reply_text("❌ Reply to a target node to ban permanently.")
                return
            target = update.message.reply_to_message.from_user
            if is_supreme(target.id):
                await update.message.reply_text("🤬 **Cannot truncate developer profile node keys.**")
                return
            cursor.execute("INSERT OR IGNORE INTO banned VALUES (?)", (target.id,))
            db.commit()
            await update.message.reply_text(f"🔨 <b>[ PERMANENT HARDWARE TRUNCATION ]</b>\n\nNode <a href='tg://user?id={target.id}'>{html.escape(target.first_name)}</a> blacklisted from running loops.", parse_mode="HTML")
            return

        elif command == ".unban":
            if not is_supreme(user.id):
                await update.message.reply_text("❌ <b>Access restricted. Module closed.</b>")
                return
            if not update.message.reply_to_message:
                await update.message.reply_text("❌ Reply to an inactive target node to unlock data links.")
                return
            target = update.message.reply_to_message.from_user
            cursor.execute("DELETE FROM banned WHERE user_id=?", (target.id,))
            db.commit()
            await update.message.reply_text(f"🔓 <b>[ NETWORK OVERRIDE RESTORED ]</b>\n\nProfile <a href='tg://user?id={target.id}'>{html.escape(target.first_name)}</a> node unbanned.", parse_mode="HTML")
            return

        elif command == ".speed":
            start_t = time.time()
            msg = await update.message.reply_text("⚡ <i>Measuring server latency packets...</i>", parse_mode="HTML")
            latency = (time.time() - start_t) * 1000
            await msg.edit_text(f"⚡ <b>NETWORK THROTTLE PROFILE</b> ⚡\n\n• Response Time: <code>{latency:.2f} ms</code>\n• Engine Load: <code>OPTIMIZED LIGHTSPEED MAX</code>", parse_mode="HTML")
            return

        elif command == ".ping":
            start_t = time.time()
            m = await update.message.reply_text("🏓 <i>Sending echo packet...</i>", parse_mode="HTML")
            latency = (time.time() - start_t) * 1000
            await m.edit_text(f"🏓 <b>PONG INTERCEPT DETECTED</b> 🏓\n\n• Signal Lag: <code>{latency:.2f} ms</code>", parse_mode="HTML")
            return

        elif command == ".stats":
            cursor.execute("SELECT COUNT(*) FROM sudo")
            sudo_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM mute")
            mute_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM stickers")
            sticker_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM banned")
            ban_count = cursor.fetchone()[0]
            uptime = datetime.now() - bot_start_time
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            await update.message.reply_text(f"📊 <b>CORE TERMINAL DATA DUMP</b> 📊\n\n• Privileged Nodes: <code>{sudo_count}</code>\n• Silenced Pipes: <code>{mute_count}</code>\n• Blacklisted Keys: <code>{ban_count}</code>\n• Synced Elements: <code>{sticker_count}</code>\n• Total Engine Uptime: <code>{hours}h {minutes}m</code>\n• Layer Strategy: <code>DARKSIDE MATRIX PRO MAX</code>", parse_mode="HTML")
            return

    except Exception as error:
        logger.error(f"Internal Core Defect: {error}")
        try:
            await update.message.reply_text(f"⚠️ <b>ITACHI SIR bot me koi problem hai jo problem hai vo check kijiye syntax broken.</b>\n\nTraceback Entry: <code>{str(error)[:80]}</code>", parse_mode="HTML")
        except Exception:
            pass

# ==================== WEB SERVER FOR RENDER ====================
async def health(request):
    return web.Response(text="ITACHI BOT IS RUNNING 🔥", status=200)

async def web_server():
    try:
        app_web = web.Application()
        app_web.router.add_get("/", health)
        app_web.router.add_get("/health", health)
        runner = web.AppRunner(app_web)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()
        print(f"🌐 Web running on port {PORT}")
    except Exception as e:
        print(f"Web error: {e}")

async def run_bot():
    # Start web server
    await web_server()
    
    # Start Telegram bot
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT | filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callbacks))
    
    print("=" * 60)
    print("💎 MATRIX TELEMETRY INSTANCE DEPLOYED WITHOUT HIDDEN BAD CHARS")
    print(f"👑 Absolute Owner Node ID: {OWNER_ID}")
    print(f"👑 Co-Owner Authority ID: {CO_OWNER_ID}")
    print("=" * 60)
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # Keep bot running
    while True:
        await asyncio.sleep(3600)

# ==================== INITIALIZATION BOOT ENGINE ====================
if __name__ == "__main__":
    asyncio.run(run_bot())
