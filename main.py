import os
import asyncio
import random
import discord
from discord.ext import commands
from collections import Counter

intents = discord.Intents.default()
intents.message_content = True

# Tắt lệnh help mặc định để không bị đụng độ
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
    embed.set_footer(text="Gõ !diemdanh để nhận xu miễn phí mỗi ngày!")
    await ctx.send(embed=embed)

# --- HỆ THỐNG TÀI KHOẢN ---
@bot.command(name="vi", aliases=["money", "bal"])
async def check_vi(ctx):
    u = get_user(ctx.author.id)
    await ctx.send(f"💰 **Tài sản của {ctx.author.name}:**\n- Tiền mặt: `{u['cash']:,}` $\n- Ngân hàng: `{u['bank']:,}` $")

@bot.command(name="diemdanh", aliases=["daily"])
async def diem_danh(ctx):
    u = get_user(ctx.author.id)
    reward = random.randint(5000, 20000)
    u["cash"] += reward
    await ctx.send(f"🎉 **{ctx.author.name}** đã điểm danh và nhận được `{reward:,}` $!")

@bot.command(name="gui", aliases=["guitien"])
async def gui_tien(ctx, amount: str = None):
    u = get_user(ctx.author.id)
    if not amount:
        return await ctx.send("❌ Cú pháp: `!gui 5000` hoặc `!gui all`")
    val = u["cash"] if amount.lower() == "all" else int(amount) if amount.isdigit() else 0
    if val <= 0 or u["cash"] < val:
        return await ctx.send("❌ Số tiền không hợp lệ hoặc bạn không đủ tiền mặt!")
    u["cash"] -= val
    u["bank"] += val
    await ctx.send(f"🏦 Bạn đã gửi thành công `{val:,}` $ vào ngân hàng!")

@bot.command(name="rut", aliases=["ruttien"])
async def rut_tien(ctx, amount: str = None):
    u = get_user(ctx.author.id)
    if not amount:
        return await ctx.send("❌ Cú pháp: `!rut 5000` hoặc `!rut all`")
    val = u["bank"] if amount.lower() == "all" else int(amount) if amount.isdigit() else 0
    if val <= 0 or u["bank"] < val:
        return await ctx.send("❌ Số tiền không hợp lệ hoặc bạn không đủ tiền ngân hàng!")
    u["bank"] -= val
    u["cash"] += val
    await ctx.send(f"💵 Bạn đã rút thành công `{val:,}` $ về ví tiền mặt!")

@bot.command(name="chuyen", aliases=["chuyentien"])
async def chuyen_tien(ctx, member: discord.Member = None, amount: int = None):
    if not member or not amount or amount <= 0:
        
