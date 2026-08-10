import os
import random
import asyncio
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

users = {}
tx = None

ORANGE = 0xFF8C00
GREEN = 0x00C853
RED = 0xF44336
BLUE = 0x2196F3

def user(uid):
    if uid not in users:
        users[uid] = 4899
    return users[uid]

def embed(title, text, color=ORANGE):
    return discord.Embed(title=title, description=text, color=color)

@bot.event
async def on_ready():
    print(f"BOT ONLINE: {bot.user}")
    await bot.change_presence(
        activity=discord.Game("!trogiup | Casino")
    )

# ================= MENU =================

@bot.command(name="trogiup")
async def help_cmd(ctx):
    text = (
        "🎰 **CASINO BET88 UY TÍN**\n\n"
        "⚔️ **ĐỐI KHÁNG (PVP)**\n"
        "`!danhbai`, `!thachdau`, `!dagapvp`, `!tuxipvp @User`\n\n"
        "🎲 **CASINO (SOLO)**\n"
        "`!tx`, `!daga`, `!tuxi`, `!bc`, `!xd`, `!bai`, `!rl`, `!quay`, `!duangua`, `!coinflip`\n\n"
        "🏛️ **HỆ THỐNG**\n"
        "`!vi`, `!gui`, `!rut`, `!chuyen`, `!diemdanh`, `!bxh`, `!nhapcode`"
    )
    await ctx.send(embed=embed("🎰 CASINO BET88", text, BLUE))

# ================= VÍ =================

@bot.command(name="vi")
async def vi(ctx):
    await ctx.send(embed=embed(
        "💳 VÍ CỦA BẠN",
        f"👤 {ctx.author.mention}\n💵 **{user(ctx.author.id):,}$**",
        BLUE
    ))

# ================= TÀI XỈU =================

@bot.command(name="tx")
async def taixiu(ctx, choice: str = None, bet: int = None):
    global tx

    if choice is None:
        return await ctx.send("❌ Dùng: `!tx tai 1000` hoặc `!tx xiu 1000`")

    choice = choice.lower()

    if choice not in ("tai", "xiu"):
        return await ctx.send("❌ Chọn `tai` hoặc `xiu`.")

    if not bet or bet <= 0:
        return await ctx.send("❌ Số tiền không hợp lệ.")

    if user(ctx.author.id) < bet:
        return await ctx.send("❌ Bạn không đủ tiền.")

    # Nếu chưa có phiên thì tự mở
    if tx is None:
        tx = {
            "bets": {},
            "channel": ctx.channel.id
        }

        await ctx.send(embed=embed(
            "🟠 SÒNG TÀI XỈU",
            "🎲 Phiên mới đã mở!\n"
            "⏱️ Thời gian cược: **30 giây**",
            ORANGE
        ))

        asyncio.create_task(tx_game(ctx.channel))

    # Mỗi người chỉ cược 1 lần
    if ctx.author.id in tx["bets"]:
        return await ctx.send("❌ Bạn chỉ được cược **1 lần mỗi phiên**.")

    user(ctx.author.id) -= 0
    users[ctx.author.id] -= bet

    tx["bets"][ctx.author.id] = {
        "name": ctx.author.display_name,
        "choice": choice,
        "bet": bet
    }

    await ctx.send(embed=embed(
        "🟠 ĐẶT CƯỢC THÀNH CÔNG",
        f"👤 {ctx.author.mention}\n"
        f"🎯 Cửa: **{choice.upper()}**\n"
        f"💰 Cược: **{bet:,}$**",
        ORANGE
    ))

async def tx_game(channel):
    global tx

    await asyncio.sleep(30)

    if tx is None:
        return

    d = [random.randint(1, 6) for _ in range(3)]
    total = sum(d)
    result = "tai" if total >= 11 else "xiu"

    win = []
    lose = []

    for uid, b in tx["bets"].items():
        if b["choice"] == result:
            users[uid] += b["bet"] * 2
            win.append(f"• {b['name']} +{b['bet'] * 2:,}$")
        else:
            lose.append(f"• {b['name']} -{b['bet']:,}$")

    text = (
        f"🎲 `[ {d[0]} ] [ {d[1]} ] [ {d[2]} ]`\n\n"
        f"🔥 **{total} điểm — {result.upper()}**\n\n"
        f"🟢 **THẮNG**\n"
        f"{chr(10).join(win) if win else 'Không có'}\n\n"
        f"🔴 **THUA**\n"
        f"{chr(10).join(lose) if lose else 'Không có'}"
    )

    await channel.send(embed=embed(
        "🎲 KẾT QUẢ TÀI XỈU",
        text,
        GREEN if win else RED
    ))

    tx = None

# ================= QUAY =================

@bot.command(name="quay")
async def quay(ctx, bet: int = None):
    if not bet or bet <= 0:
        return await ctx.send("❌ Dùng: `!quay 1000`")

    if user(ctx.author.id) < bet:
        return await ctx.send("❌ Không đủ tiền.")

    users[ctx.author.id] -= bet

    icons = ["🍒", "🍋", "🔔", "⭐", "💎"]
    result = []

    msg = await ctx.send(embed=embed(
        "🟠 🎰 MÁY SLOT",
        "🎰 `[ ? ] [ ? ] [ ? ]`",
        ORANGE
    ))

    for i in range(3):
        result.append(random.choice(icons))
        await asyncio.sleep(0.7)

        await msg.edit(embed=embed(
            "🟠 🎰 MÁY SLOT",
            f"🎰 `[ {' ] [ '.join(result)} ]`",
            ORANGE
        ))

    same = len(set(result))

    if same == 1:
        multi = 5
    elif same == 2:
        multi = 2
    else:
        multi = 1.5

    # 3 biểu tượng giống nhau = jackpot
    if result[0] == result[1] == result[2]:
        reward = int(bet * 5)
        users[ctx.author.id] += reward
        color = GREEN
        text = f"🎰 `{
