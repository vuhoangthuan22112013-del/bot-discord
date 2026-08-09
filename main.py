import os
import asyncio
import random
import discord
from discord.ext import commands
from collections import Counter

intents = discord.Intents.default()
intents.message_content = True

# Tắt help_command mặc định để không bị đụng độ alias 'help'
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
users = {}

def get_user(uid):
    if uid not in users:
        users[uid] = {"cash": 10000, "bank": 0}
    return users[uid]

@bot.event
async def on_ready():
    print(f"✅ BOT ONLINE THÀNH CÔNG: {bot.user}")

# --- MENU & TRỢ GIÚP ---
@bot.command(name="menu", aliases=["trogiup"])
async def menu_cmd(ctx):
    embed = discord.Embed(
        title="🎰 CASINO BET88 UY TÍN 🎰",
        description="Chào mừng bạn đến với hệ thống giải trí đổi thưởng!",
        color=0xFFD700
    )
    embed.add_field(
        name="⚔️ ĐỐI KHÁNG PVP",
        value="`!thachdau @User [tiền]` (hoặc `!danhbai`)",
        inline=False
    )
    embed.add_field(
        name="🎲 CASINO SOLO",
        value="`!tx [tai/xiu] [tiền]`\n`!coinflip [ngua/up] [tiền]`\n`!quay [tiền]`\n`!bc [bau/cua/tom/ca/ga/nai] [tiền]`\n`!xd [chan/le] [tiền]`",
        inline=False
    )
    embed.add_field(
        name="🏛️ HỆ THỐNG",
        value="`!vi`, `!gui [tiền]`, `!rut [tiền]`, `!chuyen @User [tiền]`, `!diemdanh`, `!bxh`, `!nhapcode [code]`",
        inline=False
    )
    embed.set
    
