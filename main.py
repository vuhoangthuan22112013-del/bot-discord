import os
import asyncio
import random
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

users = {}

# =========================
# TÀI KHOẢN
# =========================

def user(uid, name):
    if uid not in users:
        users[uid] = {
            "name": name,
            "cash": 4899,
            "bank": 0
        }
    return users[uid]


# =========================
# EMBED
# =========================

def game_embed(title, text, color):
    return discord.Embed(
        title=title,
        description=text,
        color=color
    )


ORANGE = 0xF39C12
GREEN = 0x2ECC71
RED = 0xE74C3C
BLUE = 0x3498DB


# =========================
# READY
# =========================

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino")
    )
    print("BOT ONLINE:", bot.user)


# =========================
# MENU
# =========================

@bot.command(name="trogiup")
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

    await ctx.send(
        embed=game_embed(
            "🎰 CASINO BET88 UY TÍN",
            text,
            ORANGE
        )
    )


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
        f"🏦 Ngân hàng: **{u['bank']:,}$**"
    )

    await ctx.send(
        embed=game_embed("💳 VÍ TIỀN", text, BLUE)
    )


# =========================================================
# TÀI XỈU
# =========================================================

tx = {
    "active": False,
    "bets": {},
    "message": None
}


@bot.command(name="tx")
async def taixiu(ctx, choice=None, amount=None):

    if choice is None or amount is None:
        return await ctx.send("❌ Dùng: `!tx tai 100` hoặc `!tx xiu 100`")

    choice = choice.lower()

    if choice not in ("tai", "xiu"):
        return await ctx.send("❌ Chọn `tai` hoặc `xiu`.")

    try:
        amount = int(amount)
    except:
        return await ctx.send("❌ Số tiền không hợp lệ.")

    if amount <= 0:
        return await ctx.send("❌ Số tiền phải lớn hơn 0.")

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền.")

    # Nếu chưa có phiên -> người đầu tiên tự mở
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
            embed=game_embed(
                "🟧 🎲 TÀI XỈU",
                f"🎯 **{ctx.author.name}** đã mở phiên!\n\n"
                f"🟧 Cửa: **{choice.upper()}**\n"
                f"💰 Cược: **{amount:,}$**\n\n"
                f"⏱️ **30 giây** nhận cược\n"
                f"📝 Người khác dùng `!tx tai số_tiền` hoặc `!tx xiu số_tiền`",
                ORANGE
            )
        )

        tx["message"] = msg

        # Đếm 30 giây
        await asyncio.sleep(30)

        if not tx["active"]:
            return

        tx["active"] = False

        # Xóc
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

                player["cash"] += bet["amount"] * 2

                winners.append(
                    f"🏆 **{bet['name']}** +{bet['amount'] * 2:,}$"
                )

            else:

                losers.append(
                    f"💸 **{bet['name']}** -{bet['amount']:,}$"
                )

        win_text = "\n".join(winners) or "Không có"
        lose_text = "\n".join(losers) or "Không có"

        await msg.edit(
            embed=game_embed(
                "🟩 🎲 KẾT QUẢ TÀI XỈU",
                f"🎲 `[ {d1} ] [ {d2} ] [ {d3} ]`\n\n"
                f"🎯 **{total} điểm — {result.upper()}**\n\n"
                f"🏆 **THẮNG**\n{win_text}\n\n"
                f"💸 **THUA**\n{lose_text}",
                GREEN
            )
        )

        tx["bets"] = {}

        return

    # Đã có phiên
    if ctx.author.id in tx["bets"]:
        return await ctx.send("❌ Bạn đã cược 1 lần trong phiên này rồi.")

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền.")

    u["cash"] -= amount

    tx["bets"][ctx.author.id] = {
        "name": ctx.author.name,
        "choice": choice,
        "amount": amount
    }

    await ctx.send(
        embed=game_embed(
            "🟧 ĐẶT CƯỢC THÀNH CÔNG",
            f"👤 **{ctx.author.name}**\n\n"
            f"🎯 Cửa: **{choice.upper()}**\n"
            f"💰 Cược: **{amount:,}$**",
            ORANGE
        )
    )


# =========================================================
# XÓC ĐĨA
# =========================================================

@bot.command(name="xd")
async def xocdia(ctx, choice=None, amount=None):

    if choice not in ("chan", "le") or amount is None:
        return await ctx.send("❌ Dùng: `!xd chan 100` hoặc `!xd le 100`")

    try:
        amount = int(amount)
    except:
        return await ctx.send("❌ Số tiền không hợp lệ.")

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền.")

    u["cash"] -= amount

    # 4 cục hiện cùng lúc
    reds = random.randint(0, 4)

    coins = ["🔴"] * reds + ["⚪"] * (4 - reds)
    random.shuffle(coins)

    result = "chan" if reds in (2, 4) else "le"
    win = result == choice

    coin_text = " ".join(coins)

    if win:
        u["cash"] += amount * 2

        text = (
            f"{coin_text}\n\n"
            f"🎯 Kết quả: **{result.upper()}**\n"
            f"🔴 Số đỏ: **{reds}**\n\n"
            f"🎉 **THẮNG x2!**\n"
            f"💵 Nhận: **{amount * 2:,}$**"
        )

        color = GREEN

    else:

        text = (
            f"{coin_text}\n\n"
            f"🎯 Kết quả: **{result.upper()}**\n"
            f"🔴 Số đỏ: **{reds}**\n\n"
            f"💸 **THUA!**\n"
            f"💵 Mất: **{amount:,}$**"
        )

        color = RED

    msg = await ctx.send(
        embed=game_embed("🪙 XÓC ĐĨA", text, color)
    )


# =========================================================
# BẦU CUA
# =========================================================

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
            "❌ Dùng: `!bc bau 100`, `!bc cua 100`..."
        )

    try:
        amount = int(amount)
    except:
        return await ctx.send("❌ Số tiền không hợp lệ.")

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

    if count:

        reward = amount * (count + 0.5)

        # đảm bảo số nguyên
        reward = int(reward)

        u["cash"] += amount + reward

        text = (
            f"`[ {animals[result[0]]} ] "
            f"[ {animals[result[1]]} ] "
            f"[ {animals[result[2]]} ]`\n\n"
            f"🎯 Trúng **{count} con**\n\n"
            f"🎉 **THẮNG x{1 + count * 0.5:g}!**\n"
            f"💵 Nhận: **{amount + reward:,}$**"
        )

        color = GREEN

    else:

        text = (
            f"`[ {animals[result[0]]} ] "
            f"[ {animals[result[1]]} ] "
            f"[ {animals[result[2]]} ]`\n\n"
            f"💸 **THUA!**\n"
            f"💵 Mất: **{amount:,}$**"
        )

        color = RED

    await ctx.send(
        embed=game_embed("🎲 BẦU CUA", text, color)
    )


# =========================================================
# QUAY SLOT
# =========================================================

@bot.command(name="quay")
async def quay(ctx, amount=None):

    if amount is None:
        return await ctx.send("❌ Dùng: `!quay 100`")

    try:
        amount = int(amount)
    except:
        return await ctx.send("❌ Số tiền không hợp lệ.")

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền.")

    u["cash"] -= amount

    symbols = ["🍒", "🍋", "🔔", "⭐", "💎"]

    a = random.choice(symbols)
    b = random.choice(symbols)
    c = random.choice(symbols)

    msg = await ctx.send(
        embed=game_embed(
            "🟧 🎰 QUAY SLOT",
            f"`[ {a} ] [ ❔ ] [ ❔ ]`",
            ORANGE
        )
    )

    await asyncio.sleep(0.5)

    await msg.edit(
        embed=game_embed(
            "🟧 🎰 QUAY SLOT",
            f"`[ {a} ] [ {b} ] [ ❔ ]`",
            ORANGE
        )
    )

    await asyncio.sleep(0.5)

    await msg.edit(
        embed=game_embed(
            "🟧 🎰 QUAY SLOT",
            f"`[ {a} ] [ {b} ] [ {c} ]`",
            ORANGE
        )
    )

    count = max(
        [a, b, c].count(a),
        [a, b, c].count(b),
        [a, b, c].count(c)
    )

    if count == 3:
        multiplier = 5
    elif count == 2:
        multiplier = 2
    else:
        multiplier = 1.5

    # Chỉ thắng khi có ít nhất 1 biểu tượng trùng
    if count >= 1:

        reward = int(amount * multiplier)
        u["cash"] += reward

        text = (
            f"`[ {a} ] [ {b} ] [ {c} ]`\n\n"
            f"🎉 **THẮNG x{multiplier:g}!**\n"
            f"💵 Nhận: **{reward:,}$**"
        )

        color = GREEN

    else:

        text = (
            f"`[ {a} ] [ {b} ] [ {c} ]`\n\n"
            f"💸 **THUA!**\n"
            f"💵 Mất: **{amount:,}$**"
        )

        color = RED

    await msg.edit(
        embed=game_embed("🎰 QUAY SLOT", text, color)
    )


# =========================
# TOKEN
# =========================

token = os.getenv("TOKEN_BOT")

if not token:
    print("❌ Chưa có TOKEN_BOT!")
else:
    print("🚀 Đang khởi động bot...")
    bot.run(token)
