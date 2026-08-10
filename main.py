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


def money(uid):
    if uid not in users:
        users[uid] = 4899
    return users[uid]


def box(title, text, color=ORANGE):
    return discord.Embed(title=title, description=text, color=color)


@bot.event
async def on_ready():
    print(f"BOT ONLINE: {bot.user}")
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino")
    )


# ================= MENU =================

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
    await ctx.send(embed=box("🎰 CASINO BET88", text, BLUE))


# ================= VÍ =================

@bot.command(name="vi", aliases=["bal", "money"])
async def vi(ctx):
    await ctx.send(embed=box(
        "💳 VÍ CỦA BẠN",
        f"👤 {ctx.author.mention}\n💵 **{money(ctx.author.id):,}$**",
        BLUE
    ))


# ================= ĐIỂM DANH =================

@bot.command(name="diemdanh")
async def diemdanh(ctx):
    reward = 2593
    users[ctx.author.id] = money(ctx.author.id) + reward

    await ctx.send(embed=box(
        "🎁 ĐIỂM DANH",
        f"{ctx.author.mention}\n"
        f"💰 Nhận **+{reward:,}$**\n"
        f"💵 Ví: **{money(ctx.author.id):,}$**",
        GREEN
    ))


# ================= TÀI XỈU =================

@bot.command(name="tx", aliases=["taixiu"])
async def taixiu(ctx, choice: str = None, bet: int = None):
    global tx

    if choice is None:
        return await ctx.send(
            "❌ Dùng: `!tx tai 1000` hoặc `!tx xiu 1000`"
        )

    choice = choice.lower()

    if choice not in ["tai", "xiu"]:
        return await ctx.send("❌ Chỉ được chọn `tai` hoặc `xiu`.")

    if not bet or bet <= 0:
        return await ctx.send("❌ Số tiền cược không hợp lệ.")

    if money(ctx.author.id) < bet:
        return await ctx.send("❌ Bạn không đủ tiền.")

    # Tự mở phiên nếu chưa có
    if tx is None:
        tx = {
            "bets": {},
            "channel": ctx.channel
        }

        await ctx.send(embed=box(
            "🟠 SÒNG TÀI XỈU",
            "🎲 Phiên mới đã mở!\n"
            "⏱️ Thời gian cược: **30 giây**\n"
            "👥 Mỗi người chỉ được cược **1 lần**.",
            ORANGE
        ))

        asyncio.create_task(tx_game(tx["channel"]))

    # Một người chỉ được cược 1 lần
    if ctx.author.id in tx["bets"]:
        return await ctx.send(
            f"❌ {ctx.author.mention} Bạn đã cược rồi!"
        )

    users[ctx.author.id] = money(ctx.author.id) - bet

    tx["bets"][ctx.author.id] = {
        "name": ctx.author.display_name,
        "choice": choice,
        "bet": bet
    }

    await ctx.send(embed=box(
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

    dice = [
        random.randint(1, 6),
        random.randint(1, 6),
        random.randint(1, 6)
    ]

    total = sum(dice)
    result = "tai" if total >= 11 else "xiu"

    winners = []
    losers = []

    for uid, betdata in tx["bets"].items():

        if betdata["choice"] == result:
            reward = betdata["bet"] * 2
            users[uid] = money(uid) + reward

            winners.append(
                f"• {betdata['name']}: **+{reward:,}$**"
            )
        else:
            losers.append(
                f"• {betdata['name']}: **-{betdata['bet']:,}$**"
            )

    win_text = "\n".join(winners) if winners else "Không có"
    lose_text = "\n".join(losers) if losers else "Không có"

    await channel.send(embed=box(
        "🎲 KẾT QUẢ TÀI XỈU",
        f"🎲 `[ {dice[0]} ] [ {dice[1]} ] [ {dice[2]} ]`\n\n"
        f"🔥 **{total} ĐIỂM — {result.upper()}**\n\n"
        f"🟢 **THẮNG**\n{win_text}\n\n"
        f"🔴 **THUA**\n{lose_text}",
        GREEN if winners else RED
    ))

    tx = None


# ================= SLOT =================

@bot.command(name="quay")
async def quay(ctx, bet: int = None):

    if not bet or bet <= 0:
        return await ctx.send("❌ Dùng: `!quay 1000`")

    if money(ctx.author.id) < bet:
        return await ctx.send("❌ Bạn không đủ tiền.")

    users[ctx.author.id] = money(ctx.author.id) - bet

    icons = ["🍒", "🍋", "🔔", "⭐", "💎"]

    result = []

    msg = await ctx.send(embed=box(
        "🎰 MÁY SLOT",
        "🎰 `[ ? ] [ ? ] [ ? ]`",
        ORANGE
    ))

    for i in range(3):
        result.append(random.choice(icons))

        await asyncio.sleep(0.7)

        shown = " ] [ ".join(result)

        await msg.edit(embed=box(
            "🎰 MÁY SLOT",
            f"🎰 `[ {shown} ]`",
            ORANGE
        ))

    if result[0] == result[1] == result[2]:

        reward = bet * 5
        users[ctx.author.id] = money(ctx.author.id) + reward

        await msg.edit(embed=box(
            "🎰 JACKPOT",
            f"🎰 `[ {' ] [ '.join(result)} ]`\n\n"
            f"🏆 **JACKPOT x5!**\n"
            f"💰 Nhận **{reward:,}$**",
            GREEN
        ))

    elif (
        result[0] == result[1]
        or result[0] == result[2]
        or result[1] == result[2]
    ):

        reward = int(bet * 2)
        users[ctx.author.id] = money(ctx.author.id) + reward

        await msg.edit(embed=box(
            "🎰 SLOT THẮNG",
            f"🎰 `[ {' ] [ '.join(result)} ]`\n\n"
            f"✨ **THẮNG x2!**\n"
            f"💰 Nhận **{reward:,}$**",
            GREEN
        ))

    else:

        await msg.edit(embed=box(
            "🎰 SLOT THUA",
            f"🎰 `[ {' ] [ '.join(result)} ]`\n\n"
            f"💸 **THUA!**\n"
            f"Mất **{bet:,}$**",
            RED
        ))


# ================= XÓC ĐĨA =================

@bot.command(name="xd", aliases=["xocdia"])
async def xocdia(ctx, choice: str = None, bet: int = None):

    if choice not in ["chan", "le"] or not bet or bet <= 0:
        return await ctx.send(
            "❌ Dùng: `!xd chan 1000` hoặc `!xd le 1000`"
        )

    if money(ctx.author.id) < bet:
        return await ctx.send("❌ Bạn không đủ tiền.")

    users[ctx.author.id] = money(ctx.author.id) - bet

    coins = []

    msg = await ctx.send(embed=box(
        "🪙 XÓC ĐĨA",
        "🪙 Đang xóc...",
        ORANGE
    ))

    for i in range(4):

        coins.append(random.choice(["🔴", "⚪"]))

        await asyncio.sleep(0.5)

        await msg.edit(embed=box(
            "🪙 XÓC ĐĨA",
            f"`{' '.join(coins)}`\n\n🪙 Đang xóc...",
            ORANGE
        ))

    red = coins.count("🔴")

    result = "chan" if red in [2, 4] else "le"

    if result == choice:

        reward = bet * 2
        users[ctx.author.id] = money(ctx.author.id) + reward

        await msg.edit(embed=box(
            "🪙 XÓC ĐĨA — THẮNG",
            f"`{' '.join(coins)}`\n\n"
            f"🎯 **{result.upper()}**\n"
            f"🏆 Nhận **{reward:,}$**",
            GREEN
        ))

    else:

        await msg.edit(embed=box(
            "🪙 XÓC ĐĨA — THUA",
            f"`{' '.join(coins)}`\n\n"
            f"🎯 **{result.upper()}**\n"
            f"💸 Mất **{bet:,}$**",
            RED
        ))


# ================= BẦU CUA =================

@bot.command(name="bc", aliases=["baucua"])
async def baucua(ctx, choice: str = None, bet: int = None):

    animals = {
        "ca": "🐟",
        "tom": "🦐",
        "cua": "🦀",
        "bau": "🥒",
        "ga": "🐓",
        "nai": "🦌"
    }

    if choice not in animals or not bet or bet <= 0:
        return await ctx.send(
            "❌ Dùng: `!bc cua 1000`"
        )

    if money(ctx.author.id) < bet:
        return await ctx.send("❌ Bạn không đủ tiền.")

    users[ctx.author.id] = money(ctx.author.id) - bet

    msg = await ctx.send(embed=box(
        "🎲 BẦU CUA",
        "🎲 `[ ? ] [ ? ] [ ? ]`",
        ORANGE
    ))

    result = []

    for i in range(3):

        result.append(random.choice(list(animals)))

        await asyncio.sleep(0.7)

        shown = " ] [ ".join(
            animals[x] for x in result
        )

        await msg.edit(embed=box(
            "🎲 BẦU CUA",
            f"🎲 `[ {shown} ]`",
            ORANGE
        ))

    count = result.count(choice)

    if count > 0:

        reward = bet * (count + 1)

        users[ctx.author.id] = money(ctx.author.id) + reward

        await msg.edit(embed=box(
            "🎲 BẦU CUA — THẮNG",
            f"🎲 `[ {' ] [ '.join(animals[x] for x in result)} ]`\n\n"
            f"🎯 Ra **{count} con {choice.upper()}**\n"
            f"🏆 **x{count + 1}**\n"
            f"💰 Nhận **{reward:,}$**",
            GREEN
        ))

    else:

        await msg.edit(embed=box(
            "🎲 BẦU CUA — THUA",
            f"🎲 `[ {' ] [ '.join(animals[x] for x in result)} ]`\n\n"
            f"💸 **THUA!**\n"
            f"Mất **{bet:,}$**",
            RED
        ))


# ================= CHẠY BOT =================

token = os.getenv("TOKEN_BOT")

if not token:
    print("❌ Không tìm thấy TOKEN_BOT!")
else:
    print("🚀 Đang khởi động bot...")
    bot.run(token)
