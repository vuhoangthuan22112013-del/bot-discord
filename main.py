import os
import random
import asyncio
import time
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

users = {}

TX = {
    "active": False,
    "bets": {}
}


# =========================
# USER
# =========================

def get_user(member):
    if member.id not in users:
        users[member.id] = {
            "cash": 4899,
            "bank": 0,
            "role": "Không có"
        }
    return users[member.id]


def fmt(n):
    return f"{n:,}$"


# =========================
# EMBED
# =========================

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


# =========================
# READY
# =========================

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino")
    )
    print(f"BOT ONLINE: {bot.user}")


# =========================
# HELP
# =========================

@bot.command(name="trogiup")
async def trogiup(ctx):

    e = embed(
        "🎰 CASINO BET88",
        "⚔️ **PVP**\n"
        "`!danhbai` `!thachdau`\n\n"

        "🎲 **CASINO**\n"
        "`!tx tai 1000`\n"
        "`!tx xiu 1000`\n"
        "`!bc cua 1000`\n"
        "`!xd chan 1000`\n"
        "`!xd le 1000`\n"
        "`!quay 1000`\n\n"

        "🏦 **TÀI KHOẢN**\n"
        "`!vi`\n"
        "`!gui 1000`\n"
        "`!rut 1000`\n"
        "`!chuyen @user 1000`\n\n"

        "🛒 **CỬA HÀNG**\n"
        "`!cuahang`\n"
        "`!muan vip`\n"
        "`!muan daigia`\n"
        "`!muan typhu`",
        BLUE
    )

    await ctx.send(embed=e)


# =========================
# VI
# =========================

@bot.command(name="vi", aliases=["money", "bal"])
async def vi(ctx, member: discord.Member = None):

    member = member or ctx.author
    u = get_user(member)

    e = embed(
        f"💳 VÍ CỦA {member.display_name}",
        f"💵 **Tiền mặt:** `{fmt(u['cash'])}`\n"
        f"🏦 **Ngân hàng:** `{fmt(u['bank'])}`\n"
        f"👑 **Role:** `{u['role']}`",
        BLUE
    )

    await ctx.send(embed=e)


# =========================
# GUI
# =========================

@bot.command(name="gui")
async def gui(ctx, amount: int = None):

    if not amount or amount <= 0:
        return await ctx.send("❌ Dùng: `!gui số_tiền`")

    u = get_user(ctx.author)

    if amount > u["cash"]:
        return await ctx.send("❌ Bạn không đủ tiền mặt.")

    u["cash"] -= amount
    u["bank"] += amount

    await ctx.send(
        embed=embed(
            "🏦 NGÂN HÀNG",
            f"Đã gửi `{fmt(amount)}` vào ngân hàng.",
            GREEN
        )
    )


# =========================
# RUT
# =========================

@bot.command(name="rut")
async def rut(ctx, amount: int = None):

    if not amount or amount <= 0:
        return await ctx.send("❌ Dùng: `!rut số_tiền`")

    u = get_user(ctx.author)

    if amount > u["bank"]:
        return await ctx.send("❌ Ngân hàng không đủ tiền.")

    u["bank"] -= amount
    u["cash"] += amount

    await ctx.send(
        embed(
            "💵 RÚT TIỀN",
            f"Đã rút `{fmt(amount)}`.",
            GREEN
        )
    )


# =========================
# CHUYEN
# =========================

@bot.command(name="chuyen")
async def chuyen(ctx, member: discord.Member = None, amount: int = None):

    if not member or not amount:
        return await ctx.send(
            "❌ Dùng: `!chuyen @người số_tiền`"
        )

    if amount < 1 or amount > 10_000_000:
        return await ctx.send(
            "❌ Chỉ được chuyển từ 1$ đến 10.000.000$."
        )

    if member.id == ctx.author.id:
        return await ctx.send("❌ Không thể chuyển cho chính mình.")

    sender = get_user(ctx.author)
    receiver = get_user(member)

    if sender["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền.")

    sender["cash"] -= amount
    receiver["cash"] += amount

    await ctx.send(
        f"💸 {ctx.author.mention} đã chuyển "
        f"`{fmt(amount)}` cho {member.mention}."
    )


# =========================
# QUAY
# =========================

@bot.command(name="quay")
async def quay(ctx, amount: int = None):

    if not amount or amount <= 0:
        return await ctx.send("❌ Dùng: `!quay số_tiền`")

    u = get_user(ctx.author)

    if amount > u["cash"]:
        return await ctx.send("❌ Bạn không đủ tiền.")

    u["cash"] -= amount

    symbols = ["🍒", "🍋", "🔔", "⭐", "💎"]

    a = random.choice(symbols)
    b = random.choice(symbols)
    c = random.choice(symbols)

    msg = await ctx.send(
        embed(
            "🎰 SLOT",
            "🟠 **Đang quay...**\n\n"
            f"`{a}   ?   ?`",
            ORANGE
        )
    )

    await asyncio.sleep(0.7)

    await msg.edit(
        embed=embed(
            "🎰 SLOT",
            "🟠 **Đang quay...**\n\n"
            f"`{a}   {b}   ?`",
            ORANGE
        )
    )

    await asyncio.sleep(0.7)

    await msg.edit(
        embed=embed(
            "🎰 SLOT",
            f"`{a}   {b}   {c}`",
            ORANGE
        )
    )

    await asyncio.sleep(0.5)

    if a == b == c:
        reward = amount * 5
        u["cash"] += reward

        await msg.edit(
            embed=embed(
                "🎰 JACKPOT!",
                f"`{a}   {b}   {c}`\n\n"
                f"🟢 **JACKPOT x5!**\n"
                f"Nhận `{fmt(reward)}`",
                GREEN
            )
        )

    elif a == b or a == c or b == c:
        reward = int(amount * 1.5)
        u["cash"] += reward

        await msg.edit(
            embed=embed(
                "🎰 SLOT",
                f"`{a}   {b}   {c}`\n\n"
                f"🟢 **2 hình giống nhau x1.5!**\n"
                f"Nhận `{fmt(reward)}`",
                GREEN
            )
        )

    else:

        await msg.edit(
            embed=embed(
                "🎰 SLOT",
                f"`{a}   {b}   {c}`\n\n"
                f"🔴 **THUA!**\n"
                f"Mất `{fmt(amount)}`",
                RED
            )
        )


# =========================
# XOC DIA
# =========================

@bot.command(name="xd")
async def xd(ctx, choice: str = None, amount: int = None):

    if choice not in ["chan", "le"] or not amount or amount <= 0:
        return await ctx.send(
            "❌ Dùng: `!xd chan 1000` hoặc `!xd le 1000`"
        )

    u = get_user(ctx.author)

    if amount > u["cash"]:
        return await ctx.send("❌ Bạn không đủ tiền.")

    u["cash"] -= amount

    msg = await ctx.send(
        embed(
            "🪙 XÓC ĐĨA",
            "🟠 **Xóc... Xóc... Xóc...**",
            ORANGE
        )
    )

    await asyncio.sleep(1.5)

    coins = [random.randint(0, 1) for _ in range(4)]
    red_count = sum(coins)

    result = "chan" if red_count % 2 == 0 else "le"
    result_text = "CHẴN" if result == "chan" else "LẺ"

    board = " ".join("🔴" if x else "⚪" for x in coins)

    win = choice == result

    if win:
        u["cash"] += amount * 2

    await msg.edit(
        embed=embed(
            "🪙 XÓC ĐĨA",
            f"{board}\n\n"
            f"Kết quả: **{result_text}**\n"
            f"Số đỏ: **{red_count}**",
            GREEN if win else RED
        )
    )


# =========================
# BAU CUA
# =========================

@bot.command(name="bc")
async def bc(ctx, choice: str = None, amount: int = None):

    animals = {
        "ca": "🐟",
        "tom": "🦐",
        "cua": "🦀",
        "bau": "🥒",
        "ga": "🐓",
        "nai": "🦌"
    }

    if choice not in animals or not amount or amount <= 0:
        return await ctx.send(
            "❌ Dùng: `!bc ca/tom/cua/bau/ga/nai số_tiền`"
        )

    u = get_user(ctx.author)

    if amount > u["cash"]:
        return await ctx.send("❌ Bạn không đủ tiền.")

    u["cash"] -= amount

    results = [
        random.choice(list(animals)),
        random.choice(list(animals)),
        random.choice(list(animals))
    ]

    msg = await ctx.send(
        embed(
            "🎲 BẦU CUA",
            "🟠 **Đang quay...**",
            ORANGE
        )
    )

    await asyncio.sleep(0.7)

    await msg.edit(
        embed=embed(
            "🎲 BẦU CUA",
            f"`{animals[results[0]]}`",
            ORANGE
        )
    )

    await asyncio.sleep(0.7)

    await msg.edit(
        embed=embed(
            "🎲 BẦU CUA",
            f"`{animals[results[0]]}  {animals[results[1]]}`",
            ORANGE
        )
    )

    await asyncio.sleep(0.7)

    await msg.edit(
        embed=embed(
            "🎲 BẦU CUA",
            f"`{animals[results[0]]}  "
            f"{animals[results[1]]}  "
            f"{animals[results[2]]}`",
            ORANGE
        )
    )

    count = results.count(choice)

    if count:

        multiplier = 1 + count
        reward = amount * multiplier
        u["cash"] += reward

        await msg.edit(
            embed=embed(
                "🎲 BẦU CUA",
                f"`{animals[results[0]]}  "
                f"{animals[results[1]]}  "
                f"{animals[results[2]]}`\n\n"
                f"🟢 **TRÚNG {count} CON! x{multiplier}**\n"
                f"Nhận `{fmt(reward)}`",
                GREEN
            )
        )

    else:

        await msg.edit(
            embed=embed(
                "🎲 BẦU CUA",
                f"`{animals[results[0]]}  "
                f"{animals[results[1]]}  "
                f"{animals[results[2]]}`\n\n"
                f"🔴 **THUA!**\n"
                f"Mất `{fmt(amount)}`",
                RED
            )
        )


# =========================
# TAI XIU
# =========================

@bot.command(name="tx")
async def tx(ctx, choice: str = None, amount: int = None):

    global TX

    if choice not in ["tai", "xiu"]:
        return await ctx.send(
            "❌ Dùng: `!tx tai 1000` hoặc `!tx xiu 1000`"
        )

    if not amount or amount < 100 or amount > 10_000_000:
        return await ctx.send(
            "❌ Cược từ 100$ đến 10.000.000$."
        )

    u = get_user(ctx.author)

    if u["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền.")

    # Nếu chưa có phiên thì tự mở
    if not TX["active"]:

        TX["active"] = True
        TX["bets"] = {}

        msg = await ctx.send(
            embed(
                "🎲 TÀI XỈU",
                "🟠 **PHIÊN MỚI ĐÃ MỞ!**\n\n"
                "Thời gian: **30 giây**\n"
                "Mỗi người chỉ được cược **1 lần**.\n\n"
                "🔴 TÀI\n"
                "🔵 XỈU",
                ORANGE
            )
        )

        # Người mở phiên cũng được cược luôn
        u["cash"] -= amount
        TX["bets"][ctx.author.id] = {
            "choice": choice,
            "amount": amount,
            "name": ctx.author.display_name
        }

        await msg.edit(
            embed=embed(
                "🎲 TÀI XỈU",
                f"🟠 **ĐÃ CƯỢC!**\n\n"
                f"{ctx.author.mention}: "
                f"`{fmt(amount)}` **{choice.upper()}**\n\n"
                f"⏱️ **30 giây** để người khác cược.",
                ORANGE
            )
        )

        # Đếm 30 giây
        for sec in [20, 10]:
            await asyncio.sleep(10)

            if not TX["active"]:
                return

            await msg.edit(
                embed=embed(
                    "🎲 TÀI XỈU",
                    f"🟠 **ĐANG NHẬN CƯỢC**\n\n"
                    f"⏱️ Còn **{sec} giây**\n"
                    f"👥 Người đã cược: **{len(TX['bets'])}**",
                    ORANGE
                )
            )

        await asyncio.sleep(10)

        if not TX["active"]:
            return

        TX["active"] = False

        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        d3 = random.randint(1, 6)

        total = d1 + d2 + d3
        result = "tai" if total >= 11 else "xiu"

        text = (
            f"🎲 `{d1}  {d2}  {d3}`\n\n"
            f"**{total} ĐIỂM → {result.upper()}**\n\n"
        )

        winners = 0

        for uid, bet in TX["bets"].items():

            player = users[uid]

            if bet["choice"] == result:

                reward = bet["amount"] * 2
                player["cash"] += reward
                winners += 1

                text += (
                    f"🟢 {bet['name']} +`{fmt(reward)}`\n"
                )

            else:

                text += (
                    f"🔴 {bet['name']} -`{fmt(bet['amount'])}`\n"
                )

        TX["bets"] = {}

        await msg.edit(
            embed=embed(
                "🎲 KẾT QUẢ TÀI XỈU",
                text,
                GREEN if winners else RED
            )
        )

        return

    # Đã có phiên
    if ctx.author.id in TX["bets"]:
        return await ctx.send(
            "❌ Bạn đã cược rồi. Mỗi người chỉ được cược 1 lần."
        )

    u["cash"] -= amount

    TX["bets"][ctx.author.id] = {
        "choice": choice,
        "amount": amount,
        "name": ctx.author.display_name
    }

    await ctx.send(
        embed(
            "🎲 ĐẶT CƯỢC",
            f"🟠 {ctx.author.mention}\n"
            f"Cược `{fmt(amount)}` vào **{choice.upper()}**.",
            ORANGE
        )
    )


# =========================
# SHOP
# =========================

@bot.command(name="cuahang")
async def cuahang(ctx):

    await ctx.send(
        embed(
            "🛒 CỬA HÀNG ROLE",
            "💛 **VIP** — `10.000.000$`\n"
            "`!muan vip`\n\n"
            "💙 **Đại Gia** — `5.000.000$`\n"
            "`!muan daigia`\n\n"
            "💜 **Tỷ Phú** — `1.000.000.000$`\n"
            "`!muan typhu`",
            BLUE
        )
    )


# =========================
# MUA ROLE
# =========================

@bot.command(name="muan")
async def muan(ctx, role_name: str = None):

    prices = {
        "vip": 10_000_000,
        "daigia": 5_000_000,
        "typhu": 1_000_000_000
    }

    names = {
        "vip": "VIP",
        "daigia": "Đại Gia",
        "typhu": "Tỷ Phú"
    }

    if role_name not in prices:
        return await ctx.send(
            "❌ Dùng: `!muan vip`, `!muan daigia`, `!muan typhu`"
        )

    u = get_user(ctx.author)

    price = prices[role_name]
    role_display = names[role_name]

    if u["cash"] < price:
        return await ctx.send("❌ Bạn không đủ tiền.")

    role = discord.utils.get(
        ctx.guild.roles,
        name=role_display
    )

    if not role:
        return await ctx.send(
            f"❌ Server chưa tạo role **{role_display}**."
        )

    if role >= ctx.guild.me.top_role:
        return await ctx.send(
            "❌ Role này đang cao hơn hoặc bằng role của bot."
        )

    u["cash"] -= price
    u["role"] = role_display

    try:
        await ctx.author.add_roles(role)
    except discord.Forbidden:
        return await ctx.send(
            "❌ Bot không có quyền gán role."
        )

    await ctx.send(
        embed(
            "👑 MUA ROLE THÀNH CÔNG",
            f"{ctx.author.mention}\n\n"
            f"Đã mua **{role_display}**\n"
            f"Giá: `{fmt(price)}`",
            GREEN
        )
    )


# =========================
# TOKEN
# =========================

TOKEN = os.getenv("TOKEN_BOT")

if not TOKEN:
    print("❌ Không tìm thấy TOKEN_BOT!")
else:
    bot.run(TOKEN)
