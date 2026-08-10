import os
import random
import asyncio
import time
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

users = {}
TX = {"active": False, "bets": {}}

ORANGE = 0xF39C12
GREEN = 0x2ECC71
RED = 0xE74C3C
BLUE = 0x3498DB


def get_user(member):
    if member.id not in users:
        users[member.id] = {
            "cash": 4899,
            "bank": 0,
            "role": "Không có",
            "debt": 0,
            "loan_time": 0,
            "debtor": False
        }
    return users[member.id]


def fmt(n):
    return f"{n:,}$"


def emb(title, text, color):
    return discord.Embed(title=title, description=text, color=color)


# =========================
# KIỂM TRA NỢ
# =========================

def can_play(member):
    u = get_user(member)

    if u["debtor"] or u["debt"] > 0:
        return False

    return True


async def debt_timer(member):
    u = get_user(member)

    await asyncio.sleep(3600)

    if u["debt"] > 0:
        u["debtor"] = True

        try:
            await member.edit(nick="Con Nợ")
        except:
            pass

        try:
            await member.send(
                "🔴 Khoản vay của bạn đã quá 1 giờ!\n"
                "Bạn đã trở thành **Con Nợ** và không thể chơi game "
                "cho tới khi trả hết nợ."
            )
        except:
            pass


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

    text = (
        "### 🎲 CASINO\n"
        "**`!tx tai 1000`**\n"
        "**`!tx xiu 1000`**\n"
        "**`!bc cua 1000`**\n"
        "**`!xd chan 1000`**\n"
        "**`!xd le 1000`**\n"
        "**`!quay 1000`**\n\n"

        "### 💰 TÀI KHOẢN\n"
        "**`!vi`**\n"
        "**`!gui 1000`**\n"
        "**`!rut 1000`**\n"
        "**`!chuyen @user 1000`**\n"
        "**`!vay 1000`**\n"
        "**`!trano 1000`**\n\n"

        "### 🛒 CỬA HÀNG\n"
        "**`!cuahang`**\n"
        "**`!muan vip`**\n"
        "**`!muan daigia`**\n"
        "**`!muan typhu`**"
    )

    await ctx.send(embed=emb("🎰 CASINO BET88", text, BLUE))


# =========================
# VÍ
# =========================

@bot.command(name="vi")
async def vi(ctx):

    u = get_user(ctx.author)

    debt = fmt(u["debt"]) if u["debt"] else "0$"

    await ctx.send(
        embed=emb(
            f"💳 VÍ CỦA {ctx.author.display_name}",
            f"💵 Tiền mặt: **{fmt(u['cash'])}**\n"
            f"🏦 Ngân hàng: **{fmt(u['bank'])}**\n"
            f"💸 Nợ: **{debt}**\n"
            f"👑 Role: **{u['role']}**",
            BLUE
        )
    )


# =========================
# GỬI NGÂN HÀNG
# =========================

@bot.command(name="gui")
async def gui(ctx, amount: int = None):

    if not amount or amount <= 0:
        return await ctx.send("❌ Dùng: `!gui số_tiền`")

    u = get_user(ctx.author)

    if amount > u["cash"]:
        return await ctx.send("❌ Không đủ tiền mặt.")

    u["cash"] -= amount
    u["bank"] += amount

    await ctx.send(
        embed(
            "🏦 NGÂN HÀNG",
            f"Đã gửi **{fmt(amount)}**.",
            GREEN
        )
    )


# =========================
# RÚT
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
            f"Đã rút **{fmt(amount)}**.",
            GREEN
        )
    )


# =========================
# VAY
# =========================

@bot.command(name="vay")
async def vay(ctx, amount: int = None):

    if not amount or amount < 1000 or amount > 50000:
        return await ctx.send(
            "❌ Chỉ được vay từ **1.000$ đến 50.000$**.\n"
            "Ví dụ: `!vay 10000`"
        )

    u = get_user(ctx.author)

    if u["debt"] > 0:
        return await ctx.send(
            f"❌ Bạn đang nợ **{fmt(u['debt'])}**. "
            "Hãy trả hết trước khi vay tiếp."
        )

    u["cash"] += amount
    u["debt"] = amount
    u["loan_time"] = time.time()
    u["debtor"] = False

    await ctx.send(
        embed(
            "💰 VAY TIỀN",
            f"Bạn đã vay **{fmt(amount)}**.\n\n"
            "⏰ Thời hạn: **1 giờ**\n"
            "⚠️ Quá 1 giờ chưa trả sẽ thành **Con Nợ** "
            "và không được chơi.",
            ORANGE
        )
    )

    asyncio.create_task(debt_timer(ctx.author))


# =========================
# TRẢ NỢ
# =========================

@bot.command(name="trano")
async def tramo(ctx, amount: int = None):

    if not amount or amount <= 0:
        return await ctx.send("❌ Dùng: `!trano số_tiền`")

    u = get_user(ctx.author)

    if u["debt"] <= 0:
        return await ctx.send("✅ Bạn không có khoản nợ.")

    if amount > u["debt"]:
        amount = u["debt"]

    if amount > u["cash"]:
        return await ctx.send("❌ Bạn không đủ tiền mặt để trả nợ.")

    u["cash"] -= amount
    u["debt"] -= amount

    if u["debt"] == 0:
        u["debtor"] = False
        u["loan_time"] = 0

        try:
            await ctx.author.edit(nick=None)
        except:
            pass

        msg = (
            "🎉 Bạn đã trả hết nợ!\n"
            "🟢 Bạn có thể chơi lại bình thường."
        )
    else:
        msg = f"💸 Còn nợ: **{fmt(u['debt'])}**"

    await ctx.send(
        embed(
            "💳 TRẢ NỢ",
            msg,
            GREEN
        )
    )


# =========================
# CHUYỂN TIỀN
# =========================

@bot.command(name="chuyen")
async def chuyen(ctx, member: discord.Member = None, amount: int = None):

    if not member or not amount:
        return await ctx.send("❌ Dùng: `!chuyen @user số_tiền`")

    if amount < 1 or amount > 10_000_000:
        return await ctx.send(
            "❌ Chỉ chuyển từ **1$ đến 10.000.000$**."
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
        f"💸 {ctx.author.mention} → {member.mention}: "
        f"**{fmt(amount)}**"
    )


# =========================
# QUAY
# =========================

@bot.command(name="quay")
async def quay(ctx, amount: int = None):

    if not can_play(ctx.author):
        return await ctx.send(
            "🔴 **CON NỢ!** Bạn phải trả hết nợ mới được chơi."
        )

    if not amount or amount < 100 or amount > 10_000_000:
        return await ctx.send("❌ Cược từ 100$ đến 10.000.000$.")

    u = get_user(ctx.author)

    if amount > u["cash"]:
        return await ctx.send("❌ Bạn không đủ tiền.")

    u["cash"] -= amount

    s = ["🍒", "🍋", "🔔", "⭐", "💎"]

    a = random.choice(s)
    b = random.choice(s)
    c = random.choice(s)

    msg = await ctx.send(
        embed(
            "🎰 SLOT",
            f"🟠 **ĐANG QUAY...**\n\n"
            f"**[ {a} ] [ ? ] [ ? ]**",
            ORANGE
        )
    )

    await asyncio.sleep(.6)

    await msg.edit(
        embed=emb(
            "🎰 SLOT",
            f"🟠 **ĐANG QUAY...**\n\n"
            f"**[ {a} ] [ {b} ] [ ? ]**",
            ORANGE
        )
    )

    await asyncio.sleep(.6)

    await msg.edit(
        embed=emb(
            "🎰 SLOT",
            f"**[ {a} ] [ {b} ] [ {c} ]**",
            ORANGE
        )
    )

    await asyncio.sleep(.4)

    if a == b == c:
        reward = amount * 5
        u["cash"] += reward

        text = (
            f"**[ {a} ] [ {b} ] [ {c} ]**\n\n"
            f"🟢 **JACKPOT x5!**\n"
            f"💰 Nhận **{fmt(reward)}**"
        )

        color = GREEN

    elif a == b or a == c or b == c:
        reward = int(amount * 1.5)
        u["cash"] += reward

        text = (
            f"**[ {a} ] [ {b} ] [ {c} ]**\n\n"
            f"🟢 **2 hình giống nhau x1.5!**\n"
            f"💰 Nhận **{fmt(reward)}**"
        )

        color = GREEN

    else:
        text = (
            f"**[ {a} ] [ {b} ] [ {c} ]**\n\n"
            f"🔴 **THUA!**\n"
            f"💸 Mất **{fmt(amount)}**"
        )

        color = RED

    await msg.edit(embed=emb("🎰 SLOT", text, color))


# =========================
# XÓC ĐĨA
# =========================

@bot.command(name="xd")
async def xd(ctx, choice: str = None, amount: int = None):

    if not can_play(ctx.author):
        return await ctx.send(
            "🔴 **CON NỢ!** Trả hết nợ mới được chơi."
        )

    if choice not in ["chan", "le"]:
        return await ctx.send(
            "❌ Dùng: `!xd chan 1000` hoặc `!xd le 1000`"
        )

    if not amount or amount < 100 or amount > 10_000_000:
        return await ctx.send("❌ Cược từ 100$ đến 10.000.000$.")

    u = get_user(ctx.author)

    if amount > u["cash"]:
        return await ctx.send("❌ Bạn không đủ tiền.")

    u["cash"] -= amount

    # CHỈ HIỆN XÓC TRƯỚC
    msg = await ctx.send(
        embed(
            "🪙 XÓC ĐĨA",
            "🟠 **Xóc... Xóc... Xóc...**",
            ORANGE
        )
    )

    await asyncio.sleep(2)

    coins = [random.randint(0, 1) for _ in range(4)]
    red = sum(coins)

    result = "chan" if red in [2, 4] else "le"
    result_text = "CHẴN" if result == "chan" else "LẺ"

    board = "  ".join(
        "[ 🔴 ]" if x else "[ ⚪ ]"
        for x in coins
    )

    win = choice == result

    if win:
        reward = amount * 2
        u["cash"] += reward

        text = (
            f"**{board}**\n\n"
            f"🎯 Kết quả: **{result_text}**\n"
            f"🔴 Số đỏ: **{red}**\n\n"
            f"🟢 **THẮNG x2!**\n"
            f"💰 Nhận **{fmt(reward)}**"
        )

    else:
        text = (
            f"**{board}**\n\n"
            f"🎯 Kết quả: **{result_text}**\n"
            f"🔴 Số đỏ: **{red}**\n\n"
            f"🔴 **THUA!**\n"
            f"💸 Mất **{fmt(amount)}**"
        )

    await msg.edit(
        embed=emb(
            "🪙 XÓC ĐĨA",
            text,
            GREEN if win else RED
        )
    )


# =========================
# BẦU CUA
# =========================

@bot.command(name="bc")
async def bc(ctx, choice: str = None, amount: int = None):

    if not can_play(ctx.author):
        return await ctx.send(
            "🔴 **CON NỢ!** Trả hết nợ mới được chơi."
        )

    animals = {
        "ca": "🐟",
        "tom": "🦐",
        "cua": "🦀",
        "bau": "🥒",
        "ga": "🐓",
        "nai": "🦌"
    }

    if choice not in animals:
        return await ctx.send(
            "❌ `!bc ca/tom/cua/bau/ga/nai số_tiền`"
        )

    if not amount or amount < 100 or amount > 10_000_000:
        return await ctx.send("❌ Cược từ 100$ đến 10.000.000$.")

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
            "🟠 **ĐANG QUAY...**",
            ORANGE
        )
    )

    await asyncio.sleep(.7)

    await msg.edit(
        embed=emb(
            "🎲 BẦU CUA",
            f"**[ {animals[results[0]]} ]**",
            ORANGE
        )
    )

    await asyncio.sleep(.7)

    await msg.edit(
        embed=emb(
            "🎲 BẦU CUA",
            f"**[ {animals[results[0]]} ] "
            f"[ {animals[results[1]]} ]**",
            ORANGE
        )
    )

    await asyncio.sleep(.7)

    await msg.edit(
        embed=emb(
            "🎲 BẦU CUA",
            f"**[ {animals[results[0]]} ] "
            f"[ {animals[results[1]]} ] "
            f"[ {animals[results[2]]} ]**",
            ORANGE
        )
    )

    count = results.count(choice)

    if count:
        reward = amount * (1 + count)
        u["cash"] += reward

        text = (
            f"**[ {animals[results[0]]} ] "
            f"[ {animals[results[1]]} ] "
            f"[ {animals[results[2]]} ]**\n\n"
            f"🟢 **TRÚNG {count} CON — x{1 + count}!**\n"
            f"💰 Nhận **{fmt(reward)}**"
        )

        color = GREEN

    else:
        text = (
            f"**[ {animals[results[0]]} ] "
            f"[ {animals[results[1]]} ] "
            f"[ {animals[results[2]]} ]**\n\n"
            f"🔴 **THUA!**\n"
            f"💸 Mất **{fmt(amount)}**"
        )

        color = RED

    await msg.edit(
        embed=emb("🎲 BẦU CUA", text, color)
    )


# =========================
# TÀI XỈU
# =========================

@bot.command(name="tx")
async def tx(ctx, choice: str = None, amount: int = None):

    global TX

    if not can_play(ctx.author):
        return await ctx.send(
            "🔴 **CON NỢ!** Trả hết nợ mới được chơi."
        )

    if choice not in ["tai", "xiu"]:
        return await ctx.send(
            "❌ `!tx tai 1000` hoặc `!tx xiu 1000`"
        )

    if not amount or amount < 100 or amount > 10_000_000:
        return await ctx.send("❌ Cược từ 100$ đến 10.000.000$.")

    u = get_user(ctx.author)

    if u["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền.")

    if TX["active"]:

        if ctx.author.id in TX["bets"]:
            return await ctx.send("❌ Bạn chỉ được cược 1 lần.")

        u["cash"] -= amount

        TX["bets"][ctx.author.id] = {
            "choice": choice,
            "amount": amount,
            "name": ctx.author.display_name
        }

        return await ctx.send(
            embed(
                "🎲 ĐẶT CƯỢC",
                f"👤 {ctx.author.mention}\n"
                f"💰 **{fmt(amount)}** → **{choice.upper()}**",
                ORANGE
            )
        )

    # MỞ PHIÊN
    TX["active"] = True
    TX["bets"] = {}

    u["cash"] -= amount

    TX["bets"][ctx.author.id] = {
        "choice": choice,
        "amount": amount,
        "name": ctx.author.display_name
    }

    msg = await ctx.send(
        embed(
            "🎲 TÀI XỈU",
            "🟠 **ĐANG NHẬN CƯỢC**\n\n"
            "⏱️ **30 giây**\n"
            "👥 Mỗi người chỉ được cược **1 lần**.",
            ORANGE
        )
    )

    await asyncio.sleep(20)

    if not TX["active"]:
        return

    await msg.edit(
        embed=emb(
            "🎲 TÀI XỈU",
            "🟠 **ĐANG NHẬN CƯỢC**\n\n"
            "⏱️ Còn **10 giây**\n"
            f"👥 Đã cược: **{len(TX['bets'])}**",
            ORANGE
        )
    )

    await asyncio.sleep(10)

    TX["active"] = False

    d = [
        random.randint(1, 6),
        random.randint(1, 6),
        random.randint(1, 6)
    ]

    total = sum(d)
    result = "tai" if total >= 11 else "xiu"

    text = (
        f"🎲 **[ {d[0]} ] [ {d[1]} ] [ {d[2]} ]**\n\n"
        f"📊 Tổng: **{total}**\n"
        f"🎯 Kết quả: **{result.upper()}**\n\n"
    )

    win_count = 0

    for uid, bet in TX["bets"].items():

        player = users[uid]

        if bet["choice"] == result:

            reward = bet["amount"] * 2
            player["cash"] += reward
            win_count += 1

            text += (
                f"🟢 **{bet['name']}** +{fmt(reward)}\n"
            )

        else:

            text += (
                f"🔴 **{bet['name']}** -{fmt(bet['amount'])}\n"
            )

    TX["bets"] = {}

    await msg.edit(
        embed=emb(
            "🎲 KẾT QUẢ TÀI XỈU",
            text,
            GREEN if win_count else RED
        )
    )


# =========================
# SHOP
# =========================

@bot.command(name="cuahang")
async def cuahang(ctx):

    await ctx.send(
        embed=emb(
            "🛒 CỬA HÀNG ROLE",
            "### 💛 VIP\n"
            "**10.000.000$** → `!muan vip`\n\n"
            "### 💙 ĐẠI GIA\n"
            "**5.000.000$** → `!muan daigia`\n\n"
            "### 💜 TỶ PHÚ\n"
            "**1.000.000.000$** → `!muan typhu`",
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
            "❌ `!muan vip` / `!muan daigia` / `!muan typhu`"
        )

    u = get_user(ctx.author)
    price = prices[role_name]
    name = names[role_name]

    if u["cash"] < price:
        return await ctx.send("❌ Không đủ tiền.")

    role = discord.utils.get(ctx.guild.roles, name=name)

    if not role:
        return await ctx.send(
            f"❌ Server chưa có role **{name}**."
        )

    if role >= ctx.guild.me.top_role:
        return await ctx.send(
            "❌ Role này cao hơn role của bot."
        )

    u["cash"] -= price
    u["role"] = name

    try:
        await ctx.author.add_roles(role)
    except discord.Forbidden:
        return await ctx.send(
            "❌ Bot không có quyền thêm role."
        )

    # VIP đổi nickname
    if role_name == "vip":
        try:
            base = ctx.author.display_name
            if not base.startswith("VIP | "):
                await ctx.author.edit(nick=f"VIP | {base}")
        except:
            pass

    await ctx.send(
        embed=emb(
            "👑 MUA ROLE THÀNH CÔNG",
            f"👤 {ctx.author.mention}\n"
            f"👑 Role: **{name}**\n"
            f"💰 Giá: **{fmt(price)}**",
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
