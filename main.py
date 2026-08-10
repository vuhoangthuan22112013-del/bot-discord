import os
import asyncio
import random
import time
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

users = {}
tx_rooms = {}
last_checkin = {}

ORANGE = 0xF39C12
GREEN = 0x2ECC71
RED = 0xE74C3C


def get_user(uid, name="Thành viên"):
    if uid not in users:
        users[uid] = {
            "name": name,
            "cash": 4899,
            "bank": 0
        }
    return users[uid]


def money(n):
    return f"{n:,}$"


def make_embed(title, text, color=ORANGE):
    return discord.Embed(
        title=title,
        description=text,
        color=color
    )


@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino Bet88")
    )
    print(f"✅ BOT ONLINE: {bot.user}")


# ================= TRỢ GIÚP =================

@bot.command(name="trogiup", aliases=["help"])
async def trogiup(ctx):

    e = make_embed(
        "🎰 CASINO BET88 UY TÍN",

        "⚔️ **ĐỐI KHÁNG (PVP)**\n"
        "`!danhbai`, `!thachdau`, `!dagapvp`, `!tuxipvp @User`\n\n"

        "🎲 **CASINO (SOLO)**\n"
        "`!tx`, `!daga`, `!tuxi`, `!bc`, `!xd`, `!bai`, "
        "`!rl`, `!quay`, `!duangua`, `!coinflip`\n\n"

        "🏛️ **HỆ THỐNG**\n"
        "`!vi`, `!gui`, `!rut`, `!chuyen`, "
        "`!diemdanh`, `!bxh`, `!nhapcode`"
    )

    await ctx.send(embed=e)


# ================= VÍ =================

@bot.command(name="vi", aliases=["money", "bal"])
async def vi(ctx, member: discord.Member = None):

    target = member or ctx.author
    u = get_user(target.id, target.name)

    e = make_embed(
        f"💳 TÀI KHOẢN {target.name}",
        f"💵 **Tiền mặt:** `{money(u['cash'])}`\n"
        f"🏦 **Két sắt:** `{money(u['bank'])}`",
        ORANGE
    )

    await ctx.send(embed=e)


# ================= TÀI XỈU =================

async def start_tx(ctx):

    guild_id = ctx.guild.id

    if guild_id in tx_rooms:
        return

    tx_rooms[guild_id] = {
        "bets": {},
        "tai": 0,
        "xiu": 0
    }

    msg = await ctx.send(
        embed=make_embed(
            "🟠 🎲 SÒNG TÀI XỈU BET88",
            f"👤 **{ctx.author.name}** đã mở phiên!\n\n"
            "🎯 Đặt cược:\n"
            "`!tx tai 1000`\n"
            "`!tx xiu 1000`\n\n"
            "⏱️ **THỜI GIAN: 30 GIÂY**\n"
            "⚠️ Mỗi người chỉ được cược **1 lần**.",
            ORANGE
        )
    )

    for left in [20, 10]:

        await asyncio.sleep(10)

        if guild_id not in tx_rooms:
            return

        room = tx_rooms[guild_id]

        await msg.edit(
            embed=make_embed(
                "🟠 🎲 SÒNG TÀI XỈU BET88",
                "🎯 `!tx tai <tiền>` hoặc `!tx xiu <tiền>`\n\n"
                f"⏱️ **CÒN {left} GIÂY**\n\n"
                f"🔴 Tài: `{money(room['tai'])}`\n"
                f"🔵 Xỉu: `{money(room['xiu'])}`",
                ORANGE
            )
        )

    await asyncio.sleep(10)

    if guild_id not in tx_rooms:
        return

    room = tx_rooms[guild_id]

    await msg.edit(
        embed=make_embed(
            "🟠 🎲 NHÀ CÁI ĐANG XÓC BÁT...",
            "## 🎲  [ ❔ ]   [ ❔ ]   [ ❔ ]\n\n"
            "🟠 **ĐANG XÓC...**",
            ORANGE
        )
    )

    await asyncio.sleep(0.8)

    await msg.edit(
        embed=make_embed(
            "🟠 🎲 NHÀ CÁI ĐANG XÓC BÁT...",
            "## 🎲  [ 🔴 ]   [ ❔ ]   [ ❔ ]",
            ORANGE
        )
    )

    await asyncio.sleep(0.8)

    await msg.edit(
        embed=make_embed(
            "🟠 🎲 NHÀ CÁI ĐANG XÓC BÁT...",
            "## 🎲  [ 🔴 ]   [ ⚪ ]   [ ❔ ]",
            ORANGE
        )
    )

    await asyncio.sleep(0.8)

    dice = [
        random.randint(1, 6),
        random.randint(1, 6),
        random.randint(1, 6)
    ]

    total = sum(dice)

    result = "tai" if total >= 11 else "xiu"
    result_text = "TÀI" if result == "tai" else "XỈU"

    winners = []
    losers = []

    for uid, bet in room["bets"].items():

        u = get_user(uid)

        if bet["choice"] == result:

            payout = bet["amount"] * 2
            u["cash"] += payout

            winners.append(
                f"🏆 **{bet['name']}** +`{money(payout)}`"
            )

        else:

            losers.append(
                f"💸 **{bet['name']}** -`{money(bet['amount'])}`"
            )

    text = (
        f"## 🎲  [ {dice[0]} ]   [ {dice[1]} ]   [ {dice[2]} ]\n\n"
        f"### ➜ **{total} ĐIỂM — {result_text}**\n\n"
        "🏆 **THẮNG**\n"
        + ("\n".join(winners) if winners else "Không có")
        + "\n\n💸 **THUA**\n"
        + ("\n".join(losers) if losers else "Không có")
    )

    color = GREEN if winners else RED

    await msg.edit(
        embed=make_embed(
            "🟢 🎲 MỞ BÁT BET88" if winners
            else "🔴 🎲 MỞ BÁT BET88",
            text,
            color
        )
    )

    del tx_rooms[guild_id]


@bot.command(name="tx", aliases=["taixiu"])
async def tx(ctx, choice=None, amount=None):

    guild_id = ctx.guild.id

    # !tx => tự mở phiên
    if choice is None:

        if guild_id in tx_rooms:
            return await ctx.send(
                "⚠️ Sòng Tài Xỉu đang mở rồi!"
            )

        asyncio.create_task(start_tx(ctx))
        return

    choice = choice.lower()

    if choice not in ["tai", "xiu"]:
        return await ctx.send(
            "❌ Dùng: `!tx tai 1000` hoặc `!tx xiu 1000`"
        )

    if amount is None or amount <= 0:
        return await ctx.send(
            "❌ Số tiền không hợp lệ!"
        )

    if guild_id not in tx_rooms:
        return await ctx.send(
            "❌ Chưa có phiên! Gõ `!tx` để mở."
        )

    room = tx_rooms[guild_id]
    uid = ctx.author.id

    if uid in room["bets"]:
        return await ctx.send(
            "⚠️ Bạn chỉ được cược **1 lần mỗi ván**!"
        )

    u = get_user(uid, ctx.author.name)

    if u["cash"] < amount:
        return await ctx.send(
            f"❌ Không đủ tiền! Ví còn `{money(u['cash'])}`."
        )

    u["cash"] -= amount

    room["bets"][uid] = {
        "name": ctx.author.name,
        "choice": choice,
        "amount": amount
    }

    room[choice] += amount

    await ctx.send(
        embed=make_embed(
            "🟠 ĐẶT CƯỢC THÀNH CÔNG",
            f"👤 {ctx.author.mention}\n"
            f"🎯 Cửa: **{choice.upper()}**\n"
            f"💰 Cược: `{money(amount)}`",
            ORANGE
        )
    )


# ================= SLOT =================

@bot.command(name="quay")
async def quay(ctx, amount=None):

    if amount is None or amount <= 0:
        return await ctx.send(
            "❌ Dùng: `!quay 1000`"
        )

    u = get_user(ctx.author.id, ctx.author.name)

    if u["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"] -= amount

    icons = [
        "🍒",
        "🍋",
        "🔔",
        "⭐",
        "💎"
    ]

    result = [
        random.choice(icons),
        random.choice(icons),
        random.choice(icons)
    ]

    msg = await ctx.send(
        embed=make_embed(
            "🟠 🎰 MÁY SLOT BET88",
            "## 🎰  [ ❔ ]   [ ❔ ]   [ ❔ ]\n\n"
            "🟠 **ĐANG QUAY...**",
            ORANGE
        )
    )

    shown = []

    for icon in result:

        await asyncio.sleep(0.9)

        shown.append(icon)

        boxes = "   ".join(
            f"[ {x} ]" for x in shown
        )

        boxes += "   " + "   ".join(
            "[ ❔ ]" for _ in range(3 - len(shown))
        )

        await msg.edit(
            embed=make_embed(
                "🟠 🎰 MÁY SLOT BET88",
                f"## 🎰  {boxes}\n\n"
                "🟠 **ĐANG QUAY...**",
                ORANGE
            )
        )

    counts = [
        result.count(x)
        for x in set(result)
    ]

    highest = max(counts)

    if highest == 3:

        payout = amount * 5
        u["cash"] += payout

        title = "🟢 🎰 JACKPOT BET88"
        text = (
            f"## 🎰  [ {result[0]} ]   "
            f"[ {result[1]} ]   "
            f"[ {result[2]} ]\n\n"
            f"🎉 **JACKPOT x5!**\n"
            f"💰 Nhận `{money(payout)}`"
        )

        color = GREEN

    elif highest == 2:

        payout = amount * 2
        u["cash"] += payout

        title = "🟢 🎰 MÁY SLOT BET88"
        text = (
            f"## 🎰  [ {result[0]} ]   "
            f"[ {result[1]} ]   "
            f"[ {result[2]} ]\n\n"
            f"🎉 **2 BIỂU TƯỢNG x2!**\n"
            f"💰 Nhận `{money(payout)}`"
        )

        color = GREEN

    else:

        title = "🔴 🎰 MÁY SLOT BET88"
        text = (
            f"## 🎰  [ {result[0]} ]   "
            f"[ {result[1]} ]   "
            f"[ {result[2]} ]\n\n"
            f"💸 **TRƯỢT!**\n"
            f"Mất `{money(amount)}`"
        )

        color = RED

    await msg.edit(
        embed=make_embed(
            title,
            text,
            color
        )
    )


# ================= XÓC ĐĨA =================

@bot.command(name="xd", aliases=["xocdia"])
async def xd(ctx, choice=None, amount=None):

    if choice is None or choice.lower() not in ["chan", "le"]:
        return await ctx.send(
            "❌ Dùng `!xd chan 1000` hoặc `!xd le 1000`"
        )

    if amount is None or amount <= 0:
        return await ctx.send(
            "❌ Số tiền không hợp lệ!"
        )

    u = get_user(ctx.author.id, ctx.author.name)

    if u["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"] -= amount

    coins = []

    for i in range(4):
        coins.append(
            "🔴" if random.randint(0, 1) else "⚪"
        )

    msg = await ctx.send(
        embed=make_embed(
            "🟠 🪙 XÓC ĐĨA BET88",
            "## 🪙 [ ❔ ] [ ❔ ] [ ❔ ] [ ❔ ]\n\n"
            "🟠 **ĐANG XÓC...**",
            ORANGE
        )
    )

    shown = []

    for coin in coins:

        await asyncio.sleep(0.6)

        shown.append(coin)

        boxes = " ".join(
            f"[ {x} ]" for x in shown
        )

        boxes += " " + " ".join(
            "[ ❔ ]" for _ in range(4 - len(shown))
        )

        await msg.edit(
            embed=make_embed(
                "🟠 🪙 XÓC ĐĨA BET88",
                f"## 🪙 {boxes}\n\n"
                "🟠 **ĐANG MỞ...**",
                ORANGE
            )
        )

    reds = coins.count("🔴")

    result = "chan" if reds in [2, 4] else "le"

    win = choice.lower() == result

    if win:

        payout = amount * 2
        u["cash"] += payout

        title = "🟢 🪙 XÓC ĐĨA BET88"
        color = GREEN

        text = (
            f"## 🪙 {' '.join(coins)}\n\n"
            f"🎯 **{result.upper()} — {reds} ĐỎ**\n"
            f"🏆 THẮNG!\n"
            f"💰 Nhận `{money(payout)}`"
        )

    else:

        title = "🔴 🪙 XÓC ĐĨA BET88"
        color = RED

        text = (
            f"## 🪙 {' '.join(coins)}\n\n"
            f"🎯 **{result.upper()} — {reds} ĐỎ**\n"
            f"💸 THUA!\n"
            f"Mất `{money(amount)}`"
        )

    await msg.edit(
        embed=make_embed(
            title,
            text,
            color
        )
    )


# ================= BẦU CUA =================

@bot.command(name="bc", aliases=["baucua", "bx"])
async def bc(ctx, choice=None, amount=None):

    animals = {
        "ca": "🐟",
        "tom": "🦐",
        "cua": "🦀",
        "bau": "🥒",
        "ga": "🐓",
        "nai": "🦌"
    }

    if choice is None or choice.lower() not in animals:
        return await ctx.send(
            "❌ Ví dụ: `!bc cua 1000`"
        )

    if amount is None or amount <= 0:
        return await ctx.send(
            "❌ Số tiền không hợp lệ!"
        )

    u = get_user(ctx.author.id, ctx.author.name)

    if u["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"] -= amount

    result = [
        random.choice(list(animals)),
        random.choice(list(animals)),
        random.choice(list(animals))
    ]

    msg = await ctx.send(
        embed=make_embed(
            "🟠 🎲 BẦU CUA BET88",
            "## 🎲 [ ❔ ] [ ❔ ] [ ❔ ]\n\n"
            "🟠 **ĐANG QUAY...**",
            ORANGE
        )
    )

    shown = []

    for animal in result:

        await asyncio.sleep(0.8)

        shown.append(animal)

        boxes = " ".join(
            f"[ {animals[x]} ]"
            for x in shown
        )

        boxes += " " + " ".join(
            "[ ❔ ]"
            for _ in range(3 - len(shown))
        )

        await msg.edit(
            embed=make_embed(
                "🟠 🎲 BẦU CUA BET88",
                f"## 🎲 {boxes}\n\n"
                "🟠 **ĐANG MỞ...**",
                ORANGE
            )
        )

    matches = result.count(choice.lower())

    if matches == 1:

        multiplier = 1.5

    elif matches == 2:

        multiplier = 2

    elif matches == 3:

        multiplier = 3

    else:

        multiplier = 0

    if multiplier:

        payout = int(amount * multiplier)

        u["cash"] += payout

        title = "🟢 🎲 BẦU CUA BET88"
        color = GREEN

        text = (
            f"## 🎲 [ {animals[result[0]]} ] "
            f"[ {animals[result[1]]} ] "
            f"[ {animals[result[2]]} ]\n\n"
            f"🏆 **TRÚNG {matches} CON — x{multiplier}**\n"
            f"💰 Nhận `{money(payout)}`"
        )

    else:

        title = "🔴 🎲 BẦU CUA BET88"
        color = RED

        text = (
            f"## 🎲 [ {animals[result[0]]} ] "
            f"[ {animals[result[1]]} ] "
            f"[ {animals[result[2]]} ]\n\n"
            f"💸 **KHÔNG TRÚNG!**\n"
            f"Mất `{money(amount)}`"
        )

    await msg.edit(
        embed=make_embed(
            title,
            text,
            color
        )
    )


# ================= ĐIỂM DANH =================

@bot.command(name="diemdanh")
async def diemdanh(ctx):

    now = time.time()
    uid = ctx.author.id

    if now - last_checkin.get(uid, 0) < 43200:
        return await ctx.send(
            "⚠️ Bạn đã điểm danh rồi! Thử lại sau 12 giờ."
        )

    last_checkin[uid] = now

    reward = 2593

    get_user(uid, ctx.author.name)["cash"] += reward

    await ctx.send(
        embed=make_embed(
            "🟢 🎁 ĐIỂM DANH",
            f"🎉 {ctx.author.mention}\n"
            f"💰 **+{money(reward)}**",
            GREEN
        )
    )


# ================= TOKEN =================

token = os.getenv("TOKEN_BOT")

if not token:
    raise RuntimeError(
        "❌ Chưa đặt biến môi trường TOKEN_BOT!"
    )

bot.run(token)
