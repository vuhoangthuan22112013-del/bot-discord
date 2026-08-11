import os, asyncio, random, time, secrets, discord
from discord.ext import commands

# =========================
# BET88 DISCORD BOT
# =========================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

USERS = {}
CODES = {}

TX = {
    "active": False,
    "bets": {},
    "message": None
}

START_MONEY = 5000
MAX_BET = 10_000_000

BAU = {
    "ca": "🐟",
    "tom": "🦐",
    "cua": "🦀",
    "bau": "🍐",
    "ga": "🐓",
    "nai": "🦌"
}

TUXI = {
    "bao": "🖐️",
    "bua": "✊",
    "keo": "✌️"
}


# =========================
# HỖ TRỢ
# =========================

def user(uid, name="Player"):
    if uid not in USERS:
        USERS[uid] = {
            "name": name,
            "cash": START_MONEY,
            "bank": 0,
            "debt": 0,
            "daily": 0
        }
    return USERS[uid]


def money(n):
    return f"{int(n):,}$"


def footer(text):
    return text + "\n\n💎 BET88"


def embed(title, text, color=0x3498DB):
    return discord.Embed(
        title=title,
        description=footer(text),
        color=color
    )


def is_admin(ctx):
    return ctx.author.guild_permissions.administrator


# =========================
# ONLINE
# =========================

@bot.event
async def on_ready():
    print(f"BET88 ONLINE: {bot.user}")
    await bot.change_presence(
        activity=discord.Game("!trogiup | BET88")
    )


# =========================
# TRỢ GIÚP
# =========================

@bot.command()
async def trogiup(ctx):
    text = (
        "🎲 `!tx tai 1000`\n"
        "🎲 `!tx xiu 1000`\n"
        "🦀 `!bc cua 1000`\n"
        "🪙 `!xd chan 1000`\n"
        "🎰 `!quay 1000`\n"
        "✊ `!tuxi bao 1000`\n\n"
        "💳 `!vi`\n"
        "🎁 `!diemdanh`\n"
        "🎫 `!thuongcode CODE`\n"
        "🏦 `!vaybot 50000`\n"
        "💵 `!trano 50000`\n\n"
        "👑 ADMIN\n"
        "🔐 `!taocode 50000 100`\n"
        "💰 `!settien @user 10000`\n"
        "🔄 `!resettien @user`"
    )

    await ctx.send(
        embed=embed("📖 TRỢ GIÚP", text)
    )


# =========================
# VÍ
# =========================

@bot.command()
async def vi(ctx):
    x = user(ctx.author.id, ctx.author.name)

    text = (
        f"👤 Người chơi: `{ctx.author.name}`\n"
        f"💵 Tiền: `{money(x['cash'])}`\n"
        f"🏦 Ngân hàng: `{money(x['bank'])}`\n"
        f"💸 Nợ: `{money(x['debt'])}`"
    )

    await ctx.send(
        embed=embed("💳 VÍ", text, 0xFFD700)
    )


# =========================
# ĐIỂM DANH
# =========================

@bot.command()
async def diemdanh(ctx):
    x = user(ctx.author.id, ctx.author.name)
    now = time.time()

    if now - x["daily"] < 43200:
        return await ctx.send(
            embed=embed(
                "🎁 ĐIỂM DANH",
                "❌ Bạn đã điểm danh!\n"
                "⏰ Quay lại sau 12 giờ.",
                0xE74C3C
            )
        )

    reward = 2500
    x["daily"] = now
    x["cash"] += reward

    text = (
        "🎉 ĐIỂM DANH THÀNH CÔNG!\n\n"
        f"💰 Tiền thưởng: `+{money(reward)}`\n"
        f"💵 Đã vào ví: `{money(reward)}`\n"
        f"👛 Ví hiện tại: `{money(x['cash'])}`\n\n"
        "🍀 Chúc anh em may mắn!"
    )

    await ctx.send(
        embed=embed("🎁 ĐIỂM DANH", text, 0x2ECC71)
    )


# =========================
# TÀI XỈU
# =========================

@bot.command()
async def tx(ctx, ch=None, amount: int = None):

    if ch not in ("tai", "xiu") or not amount or amount <= 0:
        return await ctx.send(
            "❌ Dùng: `!tx tai 1000` hoặc `!tx xiu 1000`"
        )

    if amount > MAX_BET:
        return await ctx.send(
            f"❌ Cược tối đa `{money(MAX_BET)}/ván`!"
        )

    x = user(ctx.author.id, ctx.author.name)

    if x["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền!")

    if ctx.author.id in TX["bets"]:
        return await ctx.send(
            "❌ Bạn đã cược trong ván này!"
        )

    if not TX["active"]:

        TX["active"] = True
        TX["bets"] = {}

        TX["message"] = await ctx.send(
            embed=embed(
                "TÀI XỈU",
                "🎯 Anh em gõ `!tx <tai/xiu> <tiền>`\n"
                "💰 Cược tối đa: `10,000,000$/ván`\n"
                "⏱️ Thời gian: `30 giây`\n\n"
                "🔥 Tài: `0$` | ❄️ Xỉu: `0$`"
            )
        )

        asyncio.create_task(run_tx())

    x["cash"] -= amount

    TX["bets"][ctx.author.id] = (
        ch,
        amount,
        ctx.author.name
    )

    tai = sum(
        b[1]
        for b in TX["bets"].values()
        if b[0] == "tai"
    )

    xiu = sum(
        b[1]
        for b in TX["bets"].values()
        if b[0] == "xiu"
    )

    await TX["message"].edit(
        embed=embed(
            "TÀI XỈU",
            "🎯 Anh em gõ `!tx <tai/xiu> <tiền>`\n"
            "💰 Cược tối đa: `10,000,000$/ván`\n"
            "⏱️ Thời gian: `30 giây`\n\n"
            f"🔥 Tài: `{money(tai)}` | "
            f"❄️ Xỉu: `{money(xiu)}`"
        )
    )


async def run_tx():

    await asyncio.sleep(30)

    dice = [
        random.randint(1, 6),
        random.randint(1, 6),
        random.randint(1, 6)
    ]

    total = sum(dice)
    result = "tai" if total >= 11 else "xiu"

    wins = []
    loses = []

    for uid, bet in TX["bets"].items():

        choice, amount, name = bet
        x = user(uid)

        if choice == result:

            prize = amount * 2
            x["cash"] += prize

            wins.append(
                f"🏆 {name}: `+{money(prize)}`"
            )

        else:

            loses.append(
                f"💸 {name}: `-{money(amount)}`"
            )

    icon = "🔥" if result == "tai" else "❄️"

    text = (
        "KẾT QUẢ\n\n"
        f"[ {dice[0]} | {dice[1]} | {dice[2]} ]\n\n"
        f"🔥 Tổng: `{total}`\n"
        f"{icon} **{result.upper()}**\n\n"
        "🏆 THẮNG\n"
        + ("\n".join(wins) if wins else "Không có")
        + "\n\n"
        "💸 THUA\n"
        + ("\n".join(loses) if loses else "Không có")
        + "\n\n"
        "🍀 Chúc anh em may mắn!"
    )

    await TX["message"].edit(
        embed=embed(
            "TÀI XỈU",
            text,
            0x2ECC71 if wins else 0xE74C3C
        )
    )

    TX["active"] = False
    TX["bets"] = {}
    TX["message"] = None


# =========================
# BẦU CUA
# =========================

@bot.command()
async def bc(ctx, choice=None, amount: int = None):

    if choice not in BAU or not amount or amount <= 0:
        return await ctx.send(
            "❌ Dùng: `!bc cua 1000`"
        )

    x = user(ctx.author.id, ctx.author.name)

    if x["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền!")

    x["cash"] -= amount

    msg = await ctx.send(
        embed=embed(
            "🦀",
            f"🎯 Bạn chọn: {BAU[choice]} {choice.upper()}\n"
            f"💰 Cược: `{money(amount)}`\n\n"
            "🥁 ĐANG LẮC...\n"
            "🪘 Lắc... Lắc... Lắc..."
        )
    )

    await asyncio.sleep(2)

    result = [
        random.choice(list(BAU)),
        random.choice(list(BAU)),
        random.choice(list(BAU))
    ]

    count = result.count(choice)

    if count:

        prize = amount * (count + 1)
        x["cash"] += prize

        text = (
            f"[ {BAU[result[0]]} | "
            f"{BAU[result[1]]} | "
            f"{BAU[result[2]]} ]\n\n"
            f"🎯 Bạn chọn: {BAU[choice]} "
            f"{choice.upper()}\n"
            f"💥 Kết quả: {BAU[choice]} "
            f"{choice.upper()}\n\n"
            "🏆 THẮNG\n"
            f"🎉 Tiền thắng: `+{money(prize)}`\n"
            f"💵 Đã vào ví: `{money(prize)}`\n"
            f"👛 Ví hiện tại: `{money(x['cash'])}`\n\n"
            "🍀 Chúc anh em may mắn!"
        )

        color = 0x2ECC71

    else:

        text = (
            f"[ {BAU[result[0]]} | "
            f"{BAU[result[1]]} | "
            f"{BAU[result[2]]} ]\n\n"
            "💸 THUA\n"
            f"📉 Tiền mất: `-{money(amount)}`\n"
            f"👛 Ví hiện tại: `{money(x['cash'])}`"
        )

        color = 0xE74C3C

    await msg.edit(
        embed=embed("🦀", text, color)
    )


# =========================
# XÓC ĐĨA
# =========================

@bot.command()
async def xd(ctx, choice=None, amount: int = None):

    if choice not in ("chan", "le") or not amount:
        return await ctx.send(
            "❌ Dùng: `!xd chan 1000` hoặc `!xd le 1000`"
        )

    x = user(ctx.author.id, ctx.author.name)

    if x["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền!")

    x["cash"] -= amount

    msg = await ctx.send(
        embed=embed(
            "🪙",
            f"🎯 Bạn chọn: `{choice.upper()}`\n"
            f"💰 Cược: `{money(amount)}`\n\n"
            "🟡 ĐANG XÓC...\n"
            "🪙 Xóc... Xóc... Xóc...\n"
            "👀 Kết quả đang được giữ kín..."
        )
    )

    await asyncio.sleep(2)

    red = random.randint(0, 4)
    result = "chan" if red % 2 == 0 else "le"

    balls = ["⚪", "⚪", "⚪", "⚪"]

    for i in random.sample(range(4), red):
        balls[i] = "🔴"

    show = " | ".join(balls)

    if result == choice:

        prize = amount * 2
        x["cash"] += prize

        text = (
            f"[ {show} ]\n\n"
            f"💥 Kết quả: **{result.upper()}**\n\n"
            "🏆 THẮNG\n"
            f"🎉 Tiền thắng: `+{money(prize)}`\n"
            f"💵 Đã vào ví: `{money(prize)}`\n"
            f"👛 Ví hiện tại: `{money(x['cash'])}`\n\n"
            "🍀 Chúc anh em may mắn!"
        )

        color = 0x2ECC71

    else:

        text = (
            f"[ {show} ]\n\n"
            f"💥 Kết quả: **{result.upper()}**\n\n"
            "💸 THUA\n"
            f"📉 Tiền mất: `-{money(amount)}`\n"
            f"👛 Ví hiện tại: `{money(x['cash'])}`"
        )

        color = 0xE74C3C

    await msg.edit(
        embed=embed("🪙", text, color)
    )


# =========================
# SLOT
# =========================

@bot.command()
async def quay(ctx, amount: int = None):

    if not amount or amount <= 0:
        return await ctx.send(
            "❌ Dùng: `!quay 1000`"
        )

    x = user(ctx.author.id, ctx.author.name)

    if x["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền!")

    x["cash"] -= amount

    msg = await ctx.send(
        embed=embed(
            "🎰",
            f"💰 Cược: `{money(amount)}`\n\n"
            "🟡 ĐANG QUAY...\n"
            "🎰 Quay... Quay... Quay..."
        )
    )

    await asyncio.sleep(2)

    icons = [
        "🍒",
        "🍋",
        "🔔",
        "⭐",
        "💎",
        "7️⃣"
    ]

    slots = [
        random.choice(icons),
        random.choice(icons),
        random.choice(icons)
    ]

    same = max(
        slots.count(i)
        for i in set(slots)
    )

    if same >= 2:

        prize = amount * (5 if same == 3 else 2)
        x["cash"] += prize

        text = (
            f"[ {' | '.join(slots)} ]\n\n"
            f"✨ {same} BIỂU TƯỢNG\n\n"
            "🏆 THẮNG\n"
            f"🎉 Tiền thắng: `+{money(prize)}`\n"
            f"💵 Đã vào ví: `{money(prize)}`\n"
            f"👛 Ví hiện tại: `{money(x['cash'])}`\n\n"
            "🍀 Chúc anh em may mắn!"
        )

        color = 0x2ECC71

    else:

        text = (
            f"[ {' | '.join(slots)} ]\n\n"
            "💸 THUA\n"
            f"📉 Tiền mất: `-{money(amount)}`\n"
            f"👛 Ví hiện tại: `{money(x['cash'])}`"
        )

        color = 0xE74C3C

    await msg.edit(
        embed=embed("🎰", text, color)
    )


# =========================
# TÙ XÌ
# =========================

@bot.command()
async def tuxi(ctx, choice=None, amount: int = None):

    if choice not in TUXI or not amount:
        return await ctx.send(
            "❌ Dùng: `!tuxi bao 1000`"
        )

    x = user(ctx.author.id, ctx.author.name)

    if x["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền!")

    x["cash"] -= amount

    bot_choice = random.choice(list(TUXI))

    win = {
        "bao": "bua",
        "bua": "keo",
        "keo": "bao"
    }

    text = (
        f"👤 Bạn: {TUXI[choice]} {choice.upper()}\n"
        f"🤖 Bot: {TUXI[bot_choice]} "
        f"{bot_choice.upper()}\n\n"
    )

    if choice == bot_choice:

        x["cash"] += amount
        text += (
            "🤝 HÒA\n"
            "💵 Hoàn lại tiền cược."
        )

        color = 0xF1C40F

    elif win[choice] == bot_choice:

        prize = amount * 2
        x["cash"] += prize

        text += (
            "🏆 THẮNG\n"
            f"🎉 Tiền thắng: `+{money(prize)}`\n"
            f"💵 Đã vào ví: `{money(prize)}`"
        )

        color = 0x2ECC71

    else:

        text += (
            "💸 THUA\n"
            f"📉 Tiền mất: `-{money(amount)}`"
        )

        color = 0xE74C3C

    text += (
        f"\n👛 Ví hiện tại: `{money(x['cash'])}`"
    )

    await ctx.send(
        embed=embed("✊", text, color)
    )


# =========================
# CODE THƯỞNG
# =========================

@bot.command()
async def taocode(ctx, amount: int = None, uses: int = 100):

    if not is_admin(ctx):
        return await ctx.send("⛔ Chỉ Admin!")

    if not amount or amount <= 0:
        return await ctx.send(
            "❌ Dùng: `!taocode 50000 100`"
        )

    code = "BET88-" + secrets.token_hex(3).upper()

    CODES[code] = [
        amount,
        uses,
        set()
    ]

    text = (
        "👑 ADMIN\n\n"
        f"🎟️ Mã: `{code}`\n"
        f"💰 Giá trị: `{money(amount)}`\n"
        f"👥 Lượt dùng: `{uses}`\n"
        "🟢 Đang hoạt động"
    )

    await ctx.send(
        embed=embed(
            "🔐 TẠO CODE",
            text,
            0x9B59B6
        )
    )


@bot.command()
async def thuongcode(ctx, code=None):

    if not code:
        return await ctx.send(
            "❌ Dùng: `!thuongcode CODE`"
        )

    code = code.upper()

    if code not in CODES:
        return await ctx.send(
            "❌ Code không tồn tại!"
        )

    amount, limit, used = CODES[code]

    if ctx.author.id in used:
        return await ctx.send(
            "❌ Bạn đã dùng code này!"
        )

    if len(used) >= limit:
        return await ctx.send(
            "❌ Code đã hết lượt!"
        )

    used.add(ctx.author.id)

    x = user(ctx.author.id, ctx.author.name)
    x["cash"] += amount

    text = (
        f"🎟️ Mã: `{code}`\n"
        f"💰 Phần thưởng: `+{money(amount)}`\n"
        f"💵 Đã vào ví: `{money(amount)}`\n"
        f"👛 Ví hiện tại: `{money(x['cash'])}`"
    )

    await ctx.send(
        embed=embed(
            "🎫 CODE THƯỞNG",
            text,
            0x2ECC71
        )
    )


# =========================
# VAY BOT
# =========================

@bot.command()
async def vaybot(ctx, amount: int = None):

    if not amount or amount <= 0 or amount > 50000:
        return await ctx.send(
            "❌ Vay từ `1$` đến `50,000$`."
        )

    x = user(ctx.author.id, ctx.author.name)

    if x["debt"] > 0:
        return await ctx.send(
            "❌ Bạn đang có khoản nợ!"
        )

    x["cash"] += amount
    x["debt"] = amount

    text = (
        f"💰 Khoản vay: `{money(amount)}`\n"
        f"💵 Đã nhận: `{money(amount)}`\n"
        f"💸 Nợ hiện tại: `{money(amount)}`\n\n"
        f"📌 Trả: `!trano {amount}`"
    )

    await ctx.send(
        embed=embed(
            "🏦",
            text,
            0xF1C40F
        )
    )


@bot.command()
async def trano(ctx, amount: int = None):

    if not amount or amount <= 0:
        return await ctx.send(
            "❌ Dùng: `!trano 50000`"
        )

    x = user(ctx.author.id, ctx.author.name)

    if x["debt"] <= 0:
        return await ctx.send(
            "❌ Bạn không có nợ!"
        )

    if amount > x["debt"]:
        amount = x["debt"]

    if amount > x["cash"]:
        return await ctx.send(
            "❌ Không đủ tiền!"
        )

    x["cash"] -= amount
    x["debt"] -= amount

    text = (
        f"💰 Đã trả: `{money(amount)}`\n"
        f"💸 Nợ còn: `{money(x['debt'])}`\n"
        f"👛 Ví: `{money(x['cash'])}`\n\n"
        + (
            "🟢 ĐÃ TRẢ HẾT!"
            if x["debt"] == 0
            else "🟡 VẪN CÒN NỢ"
        )
    )

    await ctx.send(
        embed=embed(
            "💵",
            text,
            0x2ECC71
        )
    )


# =========================
# ADMIN
# =========================

@bot.command()
async def admin(ctx):

    if not is_admin(ctx):
        return await ctx.send(
            "⛔ Chỉ Admin!"
        )

    text = (
        "👑 QUẢN TRỊ VIÊN\n\n"
        "🔐 `!taocode 50000 100`\n"
        "💰 `!settien @user 10000`\n"
        "🔄 `!resettien @user`\n"
        "🎫 `!thuongcode CODE`\n\n"
        "⚡ CHỈ ADMIN SỬ DỤNG"
    )

    await ctx.send(
        embed=embed(
            "👑 ADMIN",
            text,
            0x9B59B6
        )
    )


@bot.command()
async def settien(ctx, member: discord.Member = None,
                   amount: int = None):

    if not is_admin(ctx):
        return await ctx.send(
            "⛔ Chỉ Admin!"
        )

    if not member or amount is None:
        return await ctx.send(
            "❌ Dùng: `!settien @user 10000`"
        )

    x = user(member.id, member.name)
    x["cash"] = max(0, amount)

    await ctx.send(
        embed=embed(
            "👑",
            f"👤 Người chơi: {member.mention}\n"
            f"💰 Tiền mới: `{money(amount)}`",
            0x9B59B6
        )
    )


@bot.command()
async def resettien(ctx, member: discord.Member = None):

    if not is_admin(ctx):
        return await ctx.send(
            "⛔ Chỉ Admin!"
        )

    if not member:
        return await ctx.send(
            "❌ Dùng: `!resettien @user`"
        )

    x = user(member.id, member.name)

    x["cash"] = START_MONEY
    x["bank"] = 0
    x["debt"] = 0

    await ctx.send(
        embed=embed(
            "🔄",
            f"👤 Người chơi: {member.mention}\n"
            f"💵 Ví: `{money(START_MONEY)}`",
            0x9B59B6
        )
    )


# =========================
# CHẠY BOT
# =========================

TOKEN = os.getenv("TOKEN_BOT")

if not TOKEN:
    print("❌ Chưa có TOKEN_BOT trong Secrets!")
else:
    bot.run(TOKEN)
