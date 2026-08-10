import os
import asyncio
import random
import time
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

users = {}

MIN_BET = 100
MAX_BET = 10_000_000


def user(uid, name):
    if uid not in users:
        users[uid] = {
            "name": name,
            "cash": 4899,
            "bank": 0,
            "last_interest": time.time()
        }

    # Lãi ngân hàng 2%/ngày
    u = users[uid]
    now = time.time()
    days = int((now - u["last_interest"]) / 86400)

    if days > 0 and u["bank"] > 0:
        u["bank"] = int(u["bank"] * (1.02 ** days))
        u["last_interest"] += days * 86400

    return u


def embed(title, text, color):
    return discord.Embed(
        title=title,
        description=text,
        color=color
    )


ORANGE = 0xF39C12
GREEN = 0x2ECC71
RED = 0xE74C3C
BLUE = 0x3498DB


@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino")
    )
    print(f"BOT ONLINE: {bot.user}")


# =========================
# TRỢ GIÚP
# =========================

@bot.command(name="trogiup", aliases=["help"])
async def trogiup(ctx):

    text = (
        "🎰 **CASINO BET88 UY TÍN**\n\n"
        "⚔️ **ĐỐI KHÁNG (PVP)**\n"
        "`!danhbai`, `!thachdau`, `!dagapvp`, `!tuxipvp @User`\n\n"
        "🎲 **CASINO (SOLO)**\n"
        "`!tx`, `!daga`, `!tuxi`, `!bc`, `!xd`, `!bai`, `!rl`, `!quay`, `!duangua`, `!coinflip`\n\n"
        "🏛️ **HỆ THỐNG**\n"
        "`!vi`, `!gui`, `!rut`, `!chuyen`, `!diemdanh`, `!bxh`, `!nhapcode`"
    )

    await ctx.send(embed=embed(
        "🎰 CASINO BET88 UY TÍN",
        text,
        ORANGE
    ))


# =========================
# VÍ
# =========================

@bot.command(name="vi")
async def vi(ctx, member: discord.Member = None):

    member = member or ctx.author
    u = user(member.id, member.name)

    text = (
        f"👤 **{member.name}**\n\n"
        f"💵 Tiền mặt: **{u['cash']:,}$**\n"
        f"🏦 Ngân hàng: **{u['bank']:,}$**\n"
        f"📈 Lãi ngân hàng: **2% / ngày**"
    )

    await ctx.send(embed=embed(
        "💳 VÍ TIỀN",
        text,
        BLUE
    ))


# =========================
# GỬI NGÂN HÀNG
# !gui 1000
# =========================

@bot.command(name="gui")
async def gui(ctx, amount=None):

    if amount is None:
        return await ctx.send("❌ Dùng: `!gui số_tiền`")

    try:
        amount = int(amount)
    except:
        return await ctx.send("❌ Số tiền không hợp lệ.")

    if amount <= 0:
        return await ctx.send("❌ Số tiền phải lớn hơn 0.")

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < amount:
        return await ctx.send("❌ Tiền mặt không đủ.")

    u["cash"] -= amount
    u["bank"] += amount

    await ctx.send(embed=embed(
        "🏦 GỬI NGÂN HÀNG",
        f"👤 {ctx.author.mention}\n\n"
        f"💰 Đã gửi: **{amount:,}$**\n"
        f"🏦 Số dư ngân hàng: **{u['bank']:,}$**\n"
        f"📈 Lãi: **2% / ngày**",
        GREEN
    ))


# =========================
# RÚT NGÂN HÀNG
# !rut 1000
# =========================

@bot.command(name="rut")
async def rut(ctx, amount=None):

    if amount is None:
        return await ctx.send("❌ Dùng: `!rut số_tiền`")

    try:
        amount = int(amount)
    except:
        return await ctx.send("❌ Số tiền không hợp lệ.")

    if amount <= 0:
        return await ctx.send("❌ Số tiền phải lớn hơn 0.")

    u = user(ctx.author.id, ctx.author.name)

    if u["bank"] < amount:
        return await ctx.send("❌ Ngân hàng không đủ tiền.")

    u["bank"] -= amount
    u["cash"] += amount

    await ctx.send(embed=embed(
        "🏦 RÚT TIỀN",
        f"👤 {ctx.author.mention}\n\n"
        f"💵 Đã rút: **{amount:,}$**\n"
        f"💰 Tiền mặt: **{u['cash']:,}$**\n"
        f"🏦 Ngân hàng: **{u['bank']:,}$**",
        GREEN
    ))


# =========================
# CHUYỂN TIỀN
# !chuyen @user 1000
# =========================

@bot.command(name="chuyen")
async def chuyen(ctx, member: discord.Member = None, amount=None):

    if member is None or amount is None:
        return await ctx.send(
            "❌ Dùng: `!chuyen @nguoichoi 1000`"
        )

    if member.id == ctx.author.id:
        return await ctx.send("❌ Không thể chuyển cho chính mình.")

    try:
        amount = int(amount)
    except:
        return await ctx.send("❌ Số tiền không hợp lệ.")

    if amount < 1 or amount > MAX_BET:
        return await ctx.send(
            f"❌ Chỉ được chuyển từ **1$ → {MAX_BET:,}$**."
        )

    sender = user(ctx.author.id, ctx.author.name)
    receiver = user(member.id, member.name)

    if sender["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền mặt.")

    sender["cash"] -= amount
    receiver["cash"] += amount

    await ctx.send(embed=embed(
        "💸 CHUYỂN TIỀN",
        f"👤 **{ctx.author.name}** ➜ **{member.name}**\n\n"
        f"💰 Số tiền: **{amount:,}$**\n\n"
        f"✅ Chuyển tiền thành công!",
        GREEN
    ))


# =========================
# TÀI XỈU
# =========================

tx = {
    "active": False,
    "bets": {},
    "message": None
}


@bot.command(name="tx", aliases=["taixiu"])
async def taixiu(ctx, choice=None, amount=None):

    if choice is None or amount is None:
        return await ctx.send(
            "❌ Dùng: `!tx tai 100` hoặc `!tx xiu 100`"
        )

    choice = choice.lower()

    if choice not in ("tai", "xiu"):
        return await ctx.send("❌ Chọn `tai` hoặc `xiu`.")

    try:
        amount = int(amount)
    except:
        return await ctx.send("❌ Số tiền không hợp lệ.")

    if amount < MIN_BET or amount > MAX_BET:
        return await ctx.send(
            f"❌ Tài Xỉu chỉ cược **100$ → {MAX_BET:,}$**."
        )

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền.")

    # MỞ PHIÊN
    if not tx["active"]:

        tx["active"] = True
        tx["bets"] = {}

        u["cash"] -= amount

        tx["bets"][ctx.author.id] = {
            "name": ctx.author.name,
            "choice": choice,
            "amount": amount
        }

        msg = await ctx.send(
            embed(
                "🟧 🎲 TÀI XỈU",
                f"👤 **{ctx.author.name}** đã mở phiên!\n\n"
                f"🎯 Cửa: **{choice.upper()}**\n"
                f"💰 Cược: **{amount:,}$**\n\n"
                f"⏱️ **30 GIÂY** nhận cược\n"
                f"📝 `!tx tai số_tiền` hoặc `!tx xiu số_tiền`",
                ORANGE
            )
        )

        tx["message"] = msg

        await asyncio.sleep(30)

        if not tx["active"]:
            return

        tx["active"] = False

        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        d3 = random.randint(1, 6)

        total = d1 + d2 + d3
        result = "tai" if total >= 11 else "xiu"

        winners = []
        losers = []

        for uid, bet in tx["bets"].items():

            player = user(uid, bet["name"])

            if bet["choice"] == result:

                reward = bet["amount"] * 2
                player["cash"] += reward

                winners.append(
                    f"🏆 **{bet['name']}** +{reward:,}$"
                )

            else:

                losers.append(
                    f"💸 **{bet['name']}** -{bet['amount']:,}$"
                )

        win_text = "\n".join(winners) or "Không có"
        lose_text = "\n".join(losers) or "Không có"

        await msg.edit(
            embed=embed(
                "🟩 🎲 KẾT QUẢ TÀI XỈU",
                f"🎲 `[ {d1} ] [ {d2} ] [ {d3} ]`\n\n"
                f"🎯 **{total} ĐIỂM — {result.upper()}**\n\n"
                f"🏆 **THẮNG**\n{win_text}\n\n"
                f"💸 **THUA**\n{lose_text}",
                GREEN
            )
        )

        tx["bets"] = {}

        return

    # NGƯỜI CHƠI KHÁC CƯỢC
    if ctx.author.id in tx["bets"]:
        return await ctx.send(
            "❌ Bạn chỉ được cược **1 lần / phiên**."
        )

    u["cash"] -= amount

    tx["bets"][ctx.author.id] = {
        "name": ctx.author.name,
        "choice": choice,
        "amount": amount
    }

    await ctx.send(
        embed(
            "🟧 ĐẶT CƯỢC THÀNH CÔNG",
            f"👤 **{ctx.author.name}**\n\n"
            f"🎯 Cửa: **{choice.upper()}**\n"
            f"💰 Cược: **{amount:,}$**",
            ORANGE
        )
    )


# =========================
# XÓC ĐĨA
# =========================

@bot.command(name="xd")
async def xocdia(ctx, choice=None, amount=None):

    if choice not in ("chan", "le") or amount is None:
        return await ctx.send(
            "❌ Dùng: `!xd chan 100` hoặc `!xd le 100`"
        )

    try:
        amount = int(amount)
    except:
        return await ctx.send("❌ Số tiền không hợp lệ.")

    if amount < MIN_BET or amount > MAX_BET:
        return await ctx.send(
            f"❌ Cược từ 100$ → {MAX_BET:,}$."
        )

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền.")

    u["cash"] -= amount

    reds = random.randint(0, 4)

    coins = ["🔴"] * reds + ["⚪"] * (4 - reds)
    random.shuffle(coins)

    result = "chan" if reds in (2, 4) else "le"

    if result == choice:

        reward = amount * 2
        u["cash"] += reward

        text = (
            f"`[ {coins[0]} ] [ {coins[1]} ] "
            f"[ {coins[2]} ] [ {coins[3]} ]`\n\n"
            f"🎯 Kết quả: **{result.upper()}**\n"
            f"🔴 Số đỏ: **{reds}**\n\n"
            f"🎉 **THẮNG x2!**\n"
            f"💵 Nhận: **{reward:,}$**"
        )

        color = GREEN

    else:

        text = (
            f"`[ {coins[0]} ] [ {coins[1]} ] "
            f"[ {coins[2]} ] [ {coins[3]} ]`\n\n"
            f"🎯 Kết quả: **{result.upper()}**\n"
            f"🔴 Số đỏ: **{reds}**\n\n"
            f"💸 **THUA!**\n"
            f"💵 Mất: **{amount:,}$**"
        )

        color = RED

    await ctx.send(embed=embed(
        "🪙 XÓC ĐĨA",
        text,
        color
    ))


# =========================
# BẦU CUA
# =========================

@bot.command(name="bc")
async def baucua(ctx, choice=None, amount=None):

    animals = {
        "bau": "🥒",
        "cua": "🦀",
        "tom": "🦐",
        "ca": "🐟",
        "ga": "🐓",
        "nai": "🦌"
    }

    if choice not in animals or amount is None:
        return await ctx.send(
            "❌ Dùng: `!bc bau 100`..."
        )

    try:
        amount = int(amount)
    except:
        return await ctx.send("❌ Số tiền không hợp lệ.")

    if amount < MIN_BET or amount > MAX_BET:
        return await ctx.send(
            f"❌ Cược từ 100$ → {MAX_BET:,}$."
        )

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền.")

    u["cash"] -= amount

    result = [
        random.choice(list(animals)),
        random.choice(list(animals)),
        random.choice(list(animals))
    ]

    count = result.count(choice)

    if count == 0:

        text = (
            f"`[ {animals[result[0]]} ] "
            f"[ {animals[result[1]]} ] "
            f"[ {animals[result[2]]} ]`\n\n"
            f"💸 **THUA!**\n"
            f"💵 Mất: **{amount:,}$**"
        )

        color = RED

    else:

        multiplier = {
            1: 1.5,
            2: 2,
            3: 3
        }[count]

        reward = int(amount * multiplier)
        u["cash"] += reward

        text = (
            f"`[ {animals[result[0]]} ] "
            f"[ {animals[result[1]]} ] "
            f"[ {animals[result[2]]} ]`\n\n"
            f"🎯 Trúng **{count} con**\n\n"
            f"🎉 **THẮNG x{multiplier:g}!**\n"
            f"💵 Nhận: **{reward:,}$**"
        )

        color = GREEN

    await ctx.send(
        embed=embed("🎲 BẦU CUA", text, color)
    )


# =========================
# QUAY SLOT
# =========================

@bot.command(name="quay")
async def quay(ctx, amount=None):

    if amount is None:
        return await ctx.send("❌ Dùng: `!quay 100`")

    try:
        amount = int(amount)
    except:
        return await ctx.send("❌ Số tiền không hợp lệ.")

    if amount < MIN_BET or amount > MAX_BET:
        return await ctx.send(
            f"❌ Cược từ 100$ → {MAX_BET:,}$."
        )

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền.")

    u["cash"] -= amount

    symbols = ["🍒", "🍋", "🔔", "⭐", "💎"]

    a = random.choice(symbols)
    b = random.choice(symbols)
    c = random.choice(symbols)

    msg = await ctx.send(
        embed=embed(
            "🟧 🎰 QUAY SLOT",
            "`[ ❔ ] [ ❔ ] [ ❔ ]`",
            ORANGE
        )
    )

    await asyncio.sleep(0.5)

    await msg.edit(
        embed=embed(
            "🟧 🎰 QUAY SLOT",
            f"`[ {a} ] [ ❔ ] [ ❔ ]`",
            ORANGE
        )
    )

    await asyncio.sleep(0.5)

    await msg.edit(
        embed=embed(
            "🟧 🎰 QUAY SLOT",
            f"`[ {a} ] [ {b} ] [ ❔ ]`",
            ORANGE
        )
    )

    await asyncio.sleep(0.5)

    await msg.edit(
        embed=embed(
            "🟧 🎰 QUAY SLOT",
            f"`[ {a} ] [ {b} ] [ {c} ]`",
            ORANGE
        )
    )

    counts = [
        [a, b, c].count(a),
        [a, b, c].count(b),
        [a, b, c].count(c)
    ]

    count = max(counts)

    # 3 giống = JACKPOT x5
    if count == 3:

        reward = amount * 5
        u["cash"] += reward

        text = (
            f"`[ {a} ] [ {b} ] [ {c} ]`\n\n"
            f"💥 **JACKPOT x5!**\n"
            f"💵 Nhận: **{reward:,}$**"
        )

        color = GREEN

    # 2 giống = x1.5
    elif count == 2:

        reward = int(amount * 1.5)
        u["cash"] += reward

        text = (
            f"`[ {a} ] [ {b} ] [ {c} ]`\n\n"
            f"🎉 **THẮNG x1.5!**\n"
            f"💵 Nhận: **{reward:,}$**"
        )

        color = GREEN

    # 1 giống = THUA
    else:

        text = (
            f"`[ {a} ] [ {b} ] [ {c} ]`\n\n"
            f"💸 **THUA!**\n"
            f"💵 Mất: **{amount:,}$**"
        )

        color = RED

    await msg.edit(
        embed=embed(
            "🎰 QUAY SLOT",
            text,
            color
        )
    )


# =========================
# CHẠY BOT
# =========================

token = os.getenv("TOKEN_BOT")

if not token:
    print("❌ Không tìm thấy TOKEN_BOT!")
else:
    print("🚀 Đang khởi động bot...")
    bot.run(token)
