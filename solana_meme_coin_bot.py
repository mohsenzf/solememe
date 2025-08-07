# ✅ Solana Meme Coin Analyzer Telegram Bot (Phase 1)
# Features:
# - Fetch new Solana tokens from Birdeye API
# - Analyze token based on liquidity, ownership, honeypot, volume, holders, etc.
# - Score the token and classify as Low/Medium/High potential
# - Send report to Telegram via bot

import requests
import time
import json
from telegram import Bot

# === CONFIG ===
BOT_TOKEN = "7553024834:AAHTU0ydEDDtfLVlS8NTJr70d4wqSIi6tQQ"
CHAT_ID = "109258932"  # Replace with your own Telegram user ID or group ID
BIRDEYE_API = "https://public-api.birdeye.so/public/tokenlist?sort_by=created_at&sort_type=desc&page=1&limit=10"
HEADERS = {"X-API-KEY": "public"}

bot = Bot(token=BOT_TOKEN)

# === SCORING LOGIC ===
def score_token(data):
    score = 0
    reasons = []

    if data.get("liquidity_usd", 0) > 5000:
        score += 15
        reasons.append("✅ Good liquidity")
    else:
        reasons.append("❌ Low liquidity")

    if data.get("volume_24h", 0) > 5000:
        score += 10
        reasons.append("✅ Good 24h volume")
    else:
        reasons.append("❌ Low volume")

    if data.get("holders", 0) > 100:
        score += 10
        reasons.append("✅ Enough holders")
    else:
        reasons.append("❌ Low holders")

    if data.get("is_locked"):
        score += 10
        reasons.append("✅ Liquidity is locked")
    else:
        reasons.append("❌ Liquidity not locked")

    if not data.get("honeypot", False):
        score += 10
        reasons.append("✅ Not a honeypot")
    else:
        reasons.append("❌ Potential honeypot")

    if data.get("max_wallet_percent", 0) < 10:
        score += 10
        reasons.append("✅ No whale wallet")
    else:
        reasons.append("❌ Whale wallet detected")

    return score, reasons

# === DUMMY DATA FETCH FUNCTION ===
def fetch_new_tokens():
    response = requests.get(BIRDEYE_API, headers=HEADERS)
    if response.status_code == 200:
        tokens = response.json().get("data", [])
        return tokens
    return []

# === MAIN LOOP ===
def main_loop():
    sent_tokens = set()
    while True:
        print("Checking new tokens...")
        tokens = fetch_new_tokens()
        for token in tokens:
            address = token.get("address")
            if address in sent_tokens:
                continue

            token_data = {
                "name": token.get("name"),
                "symbol": token.get("symbol"),
                "address": address,
                "liquidity_usd": token.get("liquidity", 0),
                "volume_24h": token.get("volume_24h", 0),
                "holders": token.get("holders", 0),
                "is_locked": token.get("is_liquidity_locked", False),
                "honeypot": token.get("is_honeypot", False),
                "max_wallet_percent": token.get("max_wallet_percent", 100)
            }

            score, reasons = score_token(token_data)
            if score >= 50:
                category = "🟢 High Potential" if score >= 80 else "🟡 Medium Potential"
                msg = f"\n💠 <b>{token_data['name']} ({token_data['symbol']})</b>"
                msg += f"\n🔗 <code>{token_data['address']}</code>"
                msg += f"\n📊 Score: <b>{score}/100</b> - {category}"
                msg += f"\n💧 Liquidity: ${token_data['liquidity_usd']:.2f}"
                msg += f"\n📈 Volume 24h: ${token_data['volume_24h']:.2f}"
                msg += f"\n👥 Holders: {token_data['holders']}"
                msg += f"\n\n" + "\n".join(reasons)
                msg += f"\n\n📉 Chart: https://birdeye.so/token/{address}?chain=solana"

                bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='HTML')
                sent_tokens.add(address)

        time.sleep(60 * 5)  # check every 5 minutes

# Uncomment the line below to run the loop
# main_loop()
