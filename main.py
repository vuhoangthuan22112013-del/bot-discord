import os, random, asyncio
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

users = {}

ORANGE = 0xF39C12
GREEN = 0x2ECC71
RED = 0xE74C3C
BLUE = 0x3498DB

def user(uid, name="Thành viên"):
    if uid not in users:
        users[uid] = {
            "name": name,
            "cash": 5000,
            "bank": 0
        }
    return users[uid]

def emb(title, text, color):
    return discord.Embed(
        title=title,
        description=text,
        color=color
    )

@bot.event
async def on_ready():
    print(f"✅ BOT ONLINE: {bot.user}")
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino")
    )

# ==================== VÍ ====================

@bot.command(name="vi")
async def vi(ctx):
    u = user(ctx.author.id, ctx.author.name)

    await ctx.send(embed=emb(
        "💳 TÀI KHOẢN",
        f"👤 **{ctx.author.display_name}**\n\n"
        f"💵 Tiền mặt\n"
        f"**{u['cash']:,}$**\n\n"
        f"🏦 Két sắt\n"
        f"**{u['bank']:,}$**",
        BLUE
    ))

# ==================== SLOT ====================

@bot.command(name="quay", aliases=["qua"])
async def quay(ctx, bet: int = 0):

    u = user(ctx.author.id, ctx.author.name)

    if bet <= 0:
        return await ctx.send(
            embed=emb(
                "❌ SỬ DỤNG LỆNH",
                "`!quay 1000`",
                RED
            )
        )

    if u["cash"] < bet:
        return await ctx.send(
            embed=emb(
                "❌ KHÔNG ĐỦ TIỀN",
                f"Ví của bạn chỉ còn **{u['cash']:,}$**.",
                RED
            )
        )

    u["cash"] -= bet

    icons = ["🍒", "🍋", "🔔", "⭐", "💎"]

    a = random.choice(icons)
    b = random.choice(icons)
    c = random.choice(icons)

    msg = await ctx.send(
        embed=emb(
            "🎰 SLOT BET88",
            f"💰 Cược: **{bet:,}$**\n\n"
            f"## `[ {a} ] [ ❔ ] [ ❔ ]`\n\n"
            f"🟧 **ĐANG QUAY...**",
            ORANGE
        )
    )

    await asyncio.sleep(0.7)

    await msg.edit(
        embed=emb(
            "🎰 SLOT BET88",
            f"💰 Cược: **{bet:,}$**\n\n"
            f"## `[ {a} ] [ {b} ] [ ❔ ]`\n\n"
            f"🟧 **ĐANG QUAY...**",
            ORANGE
        )
    )

    await asyncio.sleep(0.7)

    await msg.edit(
        embed=emb(
            "🎰 SLOT BET88",
            f"💰 Cược: **{bet:,}$**\n\n"
            f"## `[ {a} ] [ {b} ] [ {c} ]`\n\n"
            f"🟧 **ĐANG KIỂM TRA...**",
            ORANGE
        )
    )

    await asyncio.sleep(0.5)

    if a == b == c:
        mult = 5
    elif a == b or a == c or b == c:
        mult = 2
    else:
        mult = 0

    if mult:
        win = bet * mult
        u["cash"] += win

        await msg.edit(
            embed=emb(
                "🟩 🎰 SLOT BET88",
                f"## `[ {a} ] [ {b} ] [ {c} ]`\n\n"
                f"🎉 **THẮNG x{mult}!**\n\n"
                f"💵 Nhận: **{win:,}$**\n"
                f"💰 Số dư: **{u['cash']:,}$**",
                GREEN
            )
        )

    else:
        await msg.edit(
            embed=emb(
                "🟥 🎰 SLOT BET88",
                f"## `[ {a} ] [ {b} ] [ {c} ]`\n\n"
                f"💸 **THUA!**\n\n"
                f"Mất: **{bet:,}$**\n"
                f"💰 Số dư: **{u['cash']:,}$**",
                RED
            )
        )

# ==================== XÓC ĐĨA ====================

@bot.command(name="xd")
async def xd(ctx, choice: str = "", bet: int = 0):

    choice = choice.lower()
    u = user(ctx.author.id, ctx.author.name)

    if choice not in ["chan", "le"] or bet <= 0:
        return await ctx.send(
            embed=emb(
                "❌ SỬ DỤNG LỆNH",
                "`!xd chan 1000`\n`!xd le 1000`",
                RED
            )
        )

    if u["cash"] < bet:
        return await ctx.send(
            embed=emb(
                "❌ KHÔNG ĐỦ TIỀN",
                f"Ví còn **{u['cash']:,}$**.",
                RED
            )
        )

    u["cash"] -= bet

    coins = [
        "🔴" if random.randint(0, 1) else "⚪"
        for _ in range(4)
    ]

    msg = await ctx.send(
        embed=emb(
            "🪙 XÓC ĐĨA BET88",
            f"🎯 Cửa: **{choice.upper()}**\n"
            f"💰 Cược: **{bet:,}$**\n\n"
            f"## `[ ❔ ] [ ❔ ] [ ❔ ] [ ❔ ]`\n\n"
            f"🟧 **ĐANG XÓC...**",
            ORANGE
        )
    )

    for i in range(4):
        await asyncio.sleep(0.55)

        show = coins[:i + 1]
        show += ["❔"] * (4 - len(show))

        board = " ] [ ".join(show)

        await msg.edit(
            embed=emb(
                "🪙 XÓC ĐĨA BET88",
                f"🎯 Cửa: **{choice.upper()}**\n"
                f"💰 Cược: **{bet:,}$**\n\n"
                f"## `[ {board} ]`\n\n"
                f"🟧 **ĐANG MỞ...**",
                ORANGE
            )
        )

    reds = coins.count("🔴")

    result = "chan" if reds in [2, 4] else "le"

    board = " ] [ ".join(coins)

    if result == choice:

        win = bet * 2
        u["cash"] += win

        await msg.edit(
            embed=emb(
                "🟩 🪙 XÓC ĐĨA",
                f"## `[ {board} ]`\n\n"
                f"🎯 Kết quả: **{result.upper()}**\n"
                f"🔴 Số đỏ: **{reds}**\n\n"
                f"🎉 **THẮNG x2!**\n"
                f"💵 Nhận: **{win:,}$**",
                GREEN
            )
        )

    else:

        await msg.edit(
            embed=emb(
                "🟥 🪙 XÓC ĐĨA",
                f"## `[ {board} ]`\n\n"
                f"🎯 Kết quả: **{result.upper()}**\n"
                f"🔴 Số đỏ: **{reds}**\n\n"
                f"💸 **THUA!**\n"
                f"Mất: **{bet:,}$**",
                RED
            )
        )

# ==================== BẦU CUA ====================

@bot.command(name="bc")
async def bc(ctx, choice: str = "", bet: int = 0):

    animals = {
        "ca": "🐟",
        "tom": "🦐",
        "cua": "🦀",
        "bau": "🥒",
        "ga": "🐓",
        "nai": "🦌"
    }

    choice = choice.lower()
    u = user(ctx.author.id, ctx.author.name)

    if choice not in animals or bet <= 0:
        return await ctx.send(
            embed=emb(
                "❌ SỬ DỤNG LỆNH",
                "`!bc ca 1000`\n"
                "`!bc tom 1000`\n"
                "`!bc cua 1000`\n"
                "`!bc bau 1000`\n"
                "`!bc ga 1000`\n"
                "`!bc nai 1000`",
                RED
            )
        )

    if u["cash"] < bet:
        return await ctx.send(
            embed=emb(
                "❌ KHÔNG ĐỦ TIỀN",
                f"Ví còn **{u['cash']:,}$**.",
                RED
            )
        )

    u["cash"] -= bet

    result = [
        random.choice(list(animals))
        for _ in range(3)
    ]

    msg = await ctx.send(
        embed=emb(
            "🎲 BẦU CUA BET88",
            f"🎯 Cửa: **{animals[choice]} {choice.upper()}**\n"
            f"💰 Cược: **{bet:,}$**\n\n"
            f"## `[ ❔ ] [ ❔ ] [ ❔ ]`\n\n"
            f"🟧 **ĐANG QUAY...**",
            ORANGE
        )
    )

    for i in range(3):

        await asyncio.sleep(0.7)

        show = []

        for j in range(3):
            if j <= i:
                show.append(animals[result[j]])
            else:
                show.append("❔")

        board = " ] [ ".join(show)

        await msg.edit(
            embed=emb(
                "🎲 BẦU CUA BET88",
                f"🎯 Cửa: **{choice.upper()}**\n"
                f"💰 Cược: **{bet:,}$**\n\n"
                f"## `[ {board} ]`\n\n"
                f"🟧 **ĐANG MỞ...**",
                ORANGE
            )
        )

    count = result.count(choice)

    board = " ] [ ".join(
        animals[x] for x in result
    )

    if count == 1:
        mult = 1.5
    elif count == 2:
        mult = 2
    elif count == 3:
        mult = 3
    else:
        mult = 0

    if mult:

        win = int(bet * mult)

        u["cash"] += win

        await msg.edit(
            embed=emb(
                "🟩 🎲 BẦU CUA",
                f"## `[ {board} ]`\n\n"
                f"🎯 Trúng: **{count} con**\n\n"
                f"🎉 **THẮNG x{mult}!**\n"
                f"💵 Nhận: **{win:,}$**",
                GREEN
            )
        )

    else:

        await msg.edit(
            embed=emb(
                "🟥 🎲 BẦU CUA",
                f"## `[ {board} ]`\n\n"
                f"❌ Không trúng con nào.\n\n"
                f"💸 **THUA!**\n"
                f"Mất: **{bet:,}$**",
                RED
            )
        )

# ==================== TÀI XỈU ====================

tx_room = {
    "open": False,
    "bets": {},
    "message": None
}

@bot.command(name="tx")
async def tx(ctx, choice: str = "", bet: int = 0):

    choice = choice.lower()
    u = user(ctx.author.id, ctx.author.name)

    if choice not in ["tai", "xiu"] or bet <= 0:

        return await ctx.send(
            embed=emb(
                "🎲 TÀI XỈU",
                "Dùng:\n"
                "`!tx tai 1000`\n"
                "hoặc\n"
                "`!tx xiu 1000`",
                BLUE
            )
        )

    if not tx_room["open"]:

        tx_room["open"] = True
        tx_room["bets"] = {}

        tx_room["message"] = await ctx.send(
            embed=emb(
                "🎲 TÀI XỈU BET88",
                "🟧 **PHIÊN MỚI ĐÃ MỞ**\n\n"
                "🎯 `!tx tai <tiền>`\n"
                "🎯 `!tx xiu <tiền>`\n\n"
                "⏱️ Thời gian: **30 giây**\n"
                "⚠️ Mỗi người chỉ được cược **1 lần**.",
                ORANGE
            )
        )

        asyncio.create_task(tx_finish())

    if ctx.author.id in tx_room["bets"]:

        return await ctx.send(
            "⚠️ Bạn đã cược trong phiên này rồi!"
        )

    if u["cash"] < bet:

        return await ctx.send(
            embed=emb(
                "❌ KHÔNG ĐỦ TIỀN",
                f"Bạn có **{u['cash']:,}$**.",
                RED
            )
        )

    u["cash"] -= bet

    tx_room["bets"][ctx.author.id] = {
        "choice": choice,
        "bet": bet,
        "name": ctx.author.display_name
    }

    await ctx.send(
        embed=emb(
            "🟧 ĐẶT CƯỢC THÀNH CÔNG",
            f"👤 **{ctx.author.display_name}**\n\n"
            f"🎯 Cửa: **{choice.upper()}**\n"
            f"💰 Cược: **{bet:,}$**",
            ORANGE
        )
    )

async def tx_finish():

    await asyncio.sleep(30)

    if not tx_room["open"]:
        return

    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    d3 = random.randint(1, 6)

    total = d1 + d2 + d3

    result = "tai" if total >= 11 else "xiu"

    msg = tx_room["message"]

    await msg.edit(
        embed=emb(
            "🟧 🎲 NHÀ CÁI ĐANG XÓC BÁT",
            f"## `[ ❔ ] [ ❔ ] [ ❔ ]`\n\n"
            f"🟧 **ĐANG XÓC...**",
            ORANGE
        )
    )

    await asyncio.sleep(.7)

    await msg.edit(
        embed=emb(
            "🟧 🎲 NHÀ CÁI ĐANG XÓC BÁT",
            f"## `[ {d1} ] [ ❔ ] [ ❔ ]`\n\n"
            f"🟧 **ĐANG XÓC...**",
            ORANGE
        )
    )

    await asyncio.sleep(.7)

    await msg.edit(
        embed=emb(
            "🟧 🎲 NHÀ CÁI ĐANG XÓC BÁT",
            f"## `[ {d1} ] [ {d2} ] [ ❔ ]`\n\n"
            f"🟧 **ĐANG XÓC...**",
            ORANGE
        )
    )

    await asyncio.sleep(.7)

    wins = []
    loses = []

    for uid, data in tx_room["bets"].items():

        u = user(uid, data["name"])

        if data["choice"] == result:

            payout = data["bet"] * 2

            u["cash"] += payout

            wins.append(
                f"🏆 **{data['name']}** +{payout:,}$"
            )

        else:

            loses.append(
                f"💸 **{data['name']}** -{data['bet']:,}$"
            )

    text = (
        f"## `[ {d1} ] [ {d2} ] [ {d3} ]`\n\n"
        f"🎯 **{total} ĐIỂM — {result.upper()}**\n\n"
        f"🏆 **THẮNG**\n"
        f"{chr(10).join(wins) if wins else 'Không có'}\n\n"
        f"💸 **THUA**\n"
        f"{chr(10).join(loses) if loses else 'Không có'}"
    )

    color = GREEN if wins else RED

    await msg.edit(
        embed=emb(
            f"{'🟩' if wins else '🟥'} 🎲 KẾT QUẢ TÀI XỈU",
            text,
            color
        )
    )

    tx_room["open"] = False
    tx_room["bets"] = {}
    tx_room["message"] = None

# ==================== TRỢ GIÚP ====================

@bot.command(name="trogiup", aliases=["help"])
async def trogiup(ctx):

    await ctx.send(
        embed=emb(
            "🎰 CASINO BET88",
            "**🎲 CASINO**\n\n"
            "`!tx tai 1000`\n"
            "`!tx xiu 1000`\n"
            "`!bc cua 1000`\n"
            "`!quay 1000`\n"
            "`!xd chan 1000`\n"
            "`!xd le 1000`\n\n"
            "**💳 HỆ THỐNG**\n"
            "`!vi`",
            BLUE
        )
    )

# ==================== TOKEN ====================

token = os.getenv("TOKEN_BOT")

if not token:
    raise RuntimeError(
        "❌ Chưa tìm thấy TOKEN_BOT trong Environment Variables!"
    )

bot.run(token)
