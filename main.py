import os
import random
import time
import asyncio
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN_BOT")
START = 2000

users = {}
codes = {}
spam = {}
loans = {}

intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)


# =========================
# HỆ THỐNG
# =========================

def U(m):
    if m.id not in users:
        users[m.id] = {
            "cash": START,
            "bank": 0,
            "daily": "",
            "muted": False
        }
    return users[m.id]


def fm(n):
    return f"{n:,}$"


def E(title, text, color=0x3498DB):
    return discord.Embed(
        title=title,
        description=text,
        color=color
    )


def adm(ctx):
    return ctx.author.guild_permissions.administrator


def block(ctx):
    u = U(ctx.author)

    if u["muted"]:
        asyncio.create_task(
            ctx.send("🔇 Bạn đang bị khóa mõm, không thể chơi hoặc nói chuyện.")
        )
        return True

    if ctx.author.id in loans:
        if time.time() > loans[ctx.author.id]["due"]:
            asyncio.create_task(
                ctx.send(
                    "🔴 **CON NỢ!** Bạn không được chơi.\n"
                    "💳 Dùng `!trano số_tiền` để trả nợ."
                )
            )
            return True

    return False


# =========================
# CHỐNG SPAM
# =========================

@bot.check
async def anti_spam(ctx):

    if ctx.author.bot:
        return False

    now = time.time()
    old = spam.get(ctx.author.id, 0)

    if now - old < 1.2:
        return False

    spam[ctx.author.id] = now
    return True


# =========================
# BOT ONLINE
# =========================

@bot.event
async def on_ready():

    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino")
    )

    print("BOT ONLINE:", bot.user)


# =========================
# TRỢ GIÚP
# =========================

@bot.command()
async def trogiup(ctx):

    if ctx.author.guild_permissions.administrator:

        text = (
            "## 🎰 GAME\n"
            "`!quay 100`\n"
            "`!bc cua 100`\n"
            "`!xd chan 100`\n"
            "`!xd le 100`\n"
            "`!tx tai 100`\n\n"

            "## 💰 TÀI KHOẢN\n"
            "`!vi`\n"
            "`!vay 1000`\n"
            "`!trano 1000`\n"
            "`!diemdanh`\n"
            "`!bxh`\n\n"

            "## 🎟️ CODE\n"
            "`!nhapcode CODE`\n\n"

            "## 🛡️ ADMIN\n"
            "`!taocode tiền lượt`\n"
            "`!thuongcode tiền lượt`\n"
            "`!settien @user tiền`\n"
            "`!reset tien @user`\n"
            "`!kick @user`\n"
            "`!ban @user`\n"
            "`!khoamom @user`\n"
            "`!unkhoamom @user`"
        )

    else:

        text = (
            "## 🎰 GAME\n"
            "`!quay 100`\n"
            "`!bc cua 100`\n"
            "`!xd chan 100`\n"
            "`!xd le 100`\n"
            "`!tx tai 100`\n\n"

            "## 💰 TÀI KHOẢN\n"
            "`!vi`\n"
            "`!vay 1000`\n"
            "`!trano 1000`\n"
            "`!diemdanh`\n"
            "`!bxh`\n\n"

            "## 🎟️ CODE\n"
            "`!nhapcode CODE`"
        )

    await ctx.send(
        embed=E(
            "📖 HƯỚNG DẪN CASINO",
            text
        )
    )


# =========================
# VÍ
# =========================

@bot.command()
async def vi(ctx, m: discord.Member = None):

    m = m or ctx.author
    u = U(m)

    loan = loans.get(
        m.id,
        {}
    ).get("amount", 0)

    status = "🟢 Bình thường"

    if m.id in loans and time.time() > loans[m.id]["due"]:
        status = "🔴 CON NỢ"

    await ctx.send(
        embed=E(
            f"💳 VÍ CỦA {m.display_name}",
            f"💵 Tiền: **{fm(u['cash'])}**\n"
            f"🏦 Ngân hàng: **{fm(u['bank'])}**\n"
            f"💸 Khoản vay: **{fm(loan)}**\n"
            f"📌 Trạng thái: **{status}**"
        )
    )


# =========================
# ĐIỂM DANH
# =========================

@bot.command()
async def diemdanh(ctx):

    u = U(ctx.author)

    today = time.strftime("%Y-%m-%d")

    if u["daily"] == today:
        return await ctx.send(
            "⏰ Hôm nay bạn đã điểm danh rồi."
        )

    money = random.randint(1000, 3000)

    u["cash"] += money
    u["daily"] = today

    await ctx.send(
        embed=E(
            "🎁 ĐIỂM DANH",
            f"🎉 Bạn nhận **{fm(money)}**!\n"
            f"💰 Số dư: **{fm(u['cash'])}**",
            0x2ECC71
        )
    )


# =========================
# BXH
# =========================

@bot.command()
async def bxh(ctx):

    arr = sorted(
        users.items(),
        key=lambda x: x[1]["cash"] + x[1]["bank"],
        reverse=True
    )[:5]

    text = ""

    for i, (uid, u) in enumerate(arr, 1):

        member = ctx.guild.get_member(uid)

        name = (
            member.display_name
            if member
            else str(uid)
        )

        text += (
            f"**{i}.** {name} — "
            f"💰 `{fm(u['cash'] + u['bank'])}`\n"
        )

    await ctx.send(
        embed=E(
            "🏆 TOP 5 GIÀU NHẤT",
            text,
            0xF1C40F
        )
    )


# =========================
# VAY
# =========================

@bot.command()
async def vay(ctx, amount: int = None):

    if not amount or not 1000 <= amount <= 50000:
        return await ctx.send(
            "❌ Chỉ được vay **1.000$ - 50.000$**."
        )

    if ctx.author.id in loans:
        return await ctx.send(
            "❌ Bạn đang có khoản vay."
        )

    U(ctx.author)["cash"] += amount

    loans[ctx.author.id] = {
        "amount": amount,
        "due": time.time() + 3600
    }

    await ctx.send(
        embed=E(
            "💳 VAY TIỀN THÀNH CÔNG",
            f"✅ Bạn đã vay **{fm(amount)}**.\n"
            "⏰ Thời hạn: **1 giờ**.\n"
            "⚠️ Quá hạn sẽ thành **CON NỢ**.\n\n"
            f"💡 Trả bằng `!trano {amount}`",
            0xF39C12
        )
    )


# =========================
# TRẢ NỢ
# =========================

@bot.command()
async def trano(ctx, amount: int = None):

    if ctx.author.id not in loans:
        return await ctx.send(
            "❌ Bạn không có khoản nợ."
        )

    debt = loans[ctx.author.id]["amount"]

    if amount != debt:
        return await ctx.send(
            f"❌ Phải trả đúng **{fm(debt)}**."
        )

    u = U(ctx.author)

    if u["cash"] < debt:
        return await ctx.send(
            "❌ Bạn không đủ tiền."
        )

    u["cash"] -= debt

    del loans[ctx.author.id]

    await ctx.send(
        embed=E(
            "✅ ĐÃ TRẢ NỢ",
            f"{ctx.author.mention} đã trả **{fm(debt)}**.\n"
            "🟢 Bạn được phép chơi lại!",
            0x2ECC71
        )
    )


# =========================
# QUAY 777
# =========================

@bot.command()
async def quay(ctx, amount: int = None):

    if block(ctx):
        return

    if not amount or amount < 1:
        return await ctx.send(
            "❌ `!quay số_tiền`"
        )

    u = U(ctx.author)

    if amount > u["cash"]:
        return await ctx.send(
            "❌ Không đủ tiền."
        )

    u["cash"] -= amount

    symbols = [
        "🍒",
        "🍋",
        "⭐",
        "🔔",
        "💎"
    ]

    a, b, c = [
        random.choice(symbols)
        for _ in range(3)
    ]

    msg = await ctx.send(
        embed=E(
            "🎰 7️⃣7️⃣7️⃣",
            "🔵 **【 ○ 】 【 ○ 】 【 ○ 】**",
            0xF39C12
        )
    )

    await asyncio.sleep(.5)

    await msg.edit(
        embed=E(
            "🎰 7️⃣7️⃣7️⃣",
            f"🔵 **【 {a} 】 【 ○ 】 【 ○ 】**",
            0xF39C12
        )
    )

    await asyncio.sleep(.5)

    await msg.edit(
        embed=E(
            "🎰 7️⃣7️⃣7️⃣",
            f"🔵 **【 {a} 】 【 {b} 】 【 ○ 】**",
            0xF39C12
        )
    )

    await asyncio.sleep(.5)

    if a == b == c:

        win = amount * 5
        u["cash"] += win

        result = (
            f"🟢 **JACKPOT x5!**\n"
            f"💰 +{fm(win)}"
        )

        color = 0x2ECC71

    elif len({a, b, c}) < 3:

        win = amount * 2
        u["cash"] += win

        result = (
            f"🟢 **2 HÌNH GIỐNG NHAU x2!**\n"
            f"💰 +{fm(win)}"
        )

        color = 0x2ECC71

    else:

        result = (
            f"🔴 **THUA!**\n"
            f"💸 -{fm(amount)}"
        )

        color = 0xE74C3C

    await msg.edit(
        embed=E(
            "🎰 7️⃣7️⃣7️⃣",
            f"🔵 **【 {a} 】 【 {b} 】 【 {c} 】**\n\n"
            f"{result}",
            color
        )
    )


# =========================
# BẦU CUA
# =========================

@bot.command()
async def bc(ctx, choice: str = None, amount: int = None):

    if block(ctx):
        return

    icons = {
        "ca": "🐟",
        "tom": "🦐",
        "cua": "🦀",
        "bau": "🥒",
        "ga": "🐓",
        "nai": "🦌"
    }

    if choice not in icons or not amount or amount < 1:
        return await ctx.send(
            "❌ `!bc ca/tom/cua/bau/ga/nai số_tiền`"
        )

    u = U(ctx.author)

    if amount > u["cash"]:
        return await ctx.send(
            "❌ Không đủ tiền."
        )

    u["cash"] -= amount

    result = [
        random.choice(list(icons))
        for _ in range(3)
    ]

    msg = await ctx.send(
        embed=E(
            "🎲 BẦU CUA",
            "🔵 **◯   ◯   ◯**",
            0xF39C12
        )
    )

    await asyncio.sleep(.7)

    board = "  ".join(
        f"【 {icons[x]} 】"
        for x in result
    )

    count = result.count(choice)

    if count:

        win = amount * (count + 1)
        u["cash"] += win

        text = (
            f"{board}\n\n"
            f"🟢 **TRÚNG {count} CON! x{count + 1}**\n"
            f"💰 +{fm(win)}"
        )

        color = 0x2ECC71

    else:

        text = (
            f"{board}\n\n"
            f"🔴 **THUA!**\n"
            f"💸 -{fm(amount)}"
        )

        color = 0xE74C3C

    await msg.edit(
        embed=E(
            "🎲 BẦU CUA",
            text,
            color
        )
    )


# =========================
# XÓC ĐĨA - ĐÃ SỬA
# =========================

@bot.command()
async def xd(ctx, choice: str = None, amount: int = None):

    if block(ctx):
        return

    if choice not in ("chan", "le") or not amount:
        return await ctx.send(
            "❌ `!xd chan 100` hoặc `!xd le 100`"
        )

    try:
        amount = int(amount)
    except:
        return await ctx.send(
            "❌ Số tiền không hợp lệ."
        )

    u = U(ctx.author)

    if amount < 100:
        return await ctx.send(
            "❌ Cược tối thiểu **100$**."
        )

    if amount > u["cash"]:
        return await ctx.send(
            "❌ Không đủ tiền."
        )

    u["cash"] -= amount

    # MÀN HÌNH XÓC
    msg = await ctx.send(
        embed=E(
            "🪙 XÓC ĐĨA",
            "🔴 ⚪ 🔴 🔴\n\n"
            "🥣 **Xóc... Xóc... Xóc...**",
            0xF39C12
        )
    )

    await asyncio.sleep(1.5)

    # 4 quân
    balls = [
        random.randint(0, 1)
        for _ in range(4)
    ]

    number = sum(balls)

    result = (
        "chan"
        if number % 2 == 0
        else "le"
    )

    board = " ".join(
        "🔴" if x else "⚪"
        for x in balls
    )

    result_name = (
        "CHẴN"
        if result == "chan"
        else "LẺ"
    )

    if choice == result:

        win = amount * 2
        u["cash"] += win

        text = (
            f"{board}\n\n"
            f"🎯 **Kết quả: {result_name}**\n"
            f"🔴 **Số đỏ: {number}**\n\n"
            f"🟢 **THẮNG x2!**\n"
            f"💰 Nhận **{fm(win)}**"
        )

        color = 0x2ECC71

    else:

        text = (
            f"{board}\n\n"
            f"🎯 **Kết quả: {result_name}**\n"
            f"🔴 **Số đỏ: {number}**\n\n"
            f"🔴 **THUA!**\n"
            f"💸 Mất **{fm(amount)}**"
        )

        color = 0xE74C3C

    await msg.edit(
        embed=E(
            "🪙 XÓC ĐĨA",
            text,
            color
        )
    )


# =========================
# TÀI XỈU
# =========================

@bot.command()
async def tx(ctx, choice: str = None, amount: int = None):

    if block(ctx):
        return

    if choice not in ("tai", "xiu") or not amount:
        return await ctx.send(
            "❌ `!tx tai 100` hoặc `!tx xiu 100`"
        )

    u = U(ctx.author)

    if amount < 100 or amount > 10000000:
        return await ctx.send(
            "❌ Cược không hợp lệ."
        )

    if amount > u["cash"]:
        return await ctx.send(
            "❌ Không đủ tiền."
        )

    u["cash"] -= amount

    msg = await ctx.send(
        embed=E(
            "🎲 TÀI XỈU",
            "🔵 ◯   ◯   ◯\n\n"
            "⏳ Đang lắc...",
            0xF39C12
        )
    )

    await asyncio.sleep(1.5)

    dice = [
        random.randint(1, 6)
        for _ in range(3)
    ]

    total = sum(dice)

    result = (
        "tai"
        if total >= 11
        else "xiu"
    )

    if choice == result:

        win = amount * 2
        u["cash"] += win

        text = (
            f"🎲 **{' '.join(map(str, dice))}**\n"
            f"🎯 **{total} → {result.upper()}**\n"
            f"🟢 **+{fm(win)}**"
        )

        color = 0x2ECC71

    else:

        text = (
            f"🎲 **{' '.join(map(str, dice))}**\n"
            f"🎯 **{total} → {result.upper()}**\n"
            f"🔴 **-{fm(amount)}**"
        )

        color = 0xE74C3C

    await msg.edit(
        embed=E(
            "🎲 KẾT QUẢ TÀI XỈU",
            text,
            color
        )
    )


# =========================
# TẠO CODE ADMIN
# =========================

@bot.command()
async def taocode(ctx, amount: int = None, uses: int = None):

    if not adm(ctx):
        return await ctx.send("⛔ Chỉ Admin.")

    if not amount or not uses:
        return await ctx.send(
            "❌ `!taocode tiền lượt`"
        )

    code = (
        "CASINO" +
        str(random.randint(100000, 999999))
    )

    codes[code] = [
        amount,
        uses
    ]

    try:

        await ctx.author.send(
            f"🎟️ **CODE ADMIN**\n\n"
            f"🔑 `{code}`\n"
            f"💰 {fm(amount)}\n"
            f"🎫 {uses} lượt"
        )

        await ctx.send(
            "✅ Code đã được gửi riêng vào DM."
        )

    except:

        await ctx.send(
            f"⚠️ Không gửi DM được: `{code}`"
        )


# =========================
# THƯỞNG CODE
# =========================

@bot.command()
async def thuongcode(ctx, amount: int = None, uses: int = None):

    if not adm(ctx):
        return await ctx.send("⛔ Chỉ Admin.")

    if not amount or not uses:
        return await ctx.send(
            "❌ `!thuongcode tiền lượt`"
        )

    code = (
        "THUONG" +
        str(random.randint(100000, 999999))
    )

    codes[code] = [
        amount,
        uses
    ]

    await ctx.send(
        embed=E(
            "🎁 🎟️ THƯỞNG CODE",
            f"🔑 **CODE:** `{code}`\n"
            f"💰 **Tiền:** `{fm(amount)}`\n"
            f"🎫 **Lượt:** `{uses}`\n\n"
            f"📌 Nhập: `!nhapcode {code}`",
            0x3498DB
        )
    )


# =========================
# NHẬP CODE
# =========================

@bot.command()
async def nhapcode(ctx, code: str = None):

    if not code:
        return await ctx.send(
            "❌ Nhập code."
        )

    code = code.upper()

    if code not in codes:
        return await ctx.send(
            "❌ Code không tồn tại."
        )

    amount, uses = codes[code]

    if uses <= 0:
        return await ctx.send(
            "❌ Code hết lượt."
        )

    U(ctx.author)["cash"] += amount
    codes[code][1] -= 1

    await ctx.send(
        embed=E(
            "🎟️ NHẬP CODE THÀNH CÔNG",
            f"💰 Nhận **{fm(amount)}**\n"
            f"🎫 Còn **{uses - 1} lượt**",
            0x2ECC71
        )
    )


# =========================
# SET TIỀN ADMIN
# =========================

@bot.command()
async def settien(
    ctx,
    m: discord.Member = None,
    amount: int = None
):

    if not adm(ctx):
        return await ctx.send("⛔ Chỉ Admin.")

    if not m or amount is None:
        return await ctx.send(
            "❌ `!settien @user tiền`"
        )

    U(m)["cash"] = max(0, amount)

    await ctx.send(
        f"🛡️ Đã set tiền {m.mention} → "
        f"**{fm(amount)}**."
    )


# =========================
# RESET
# =========================

@bot.command()
async def reset(
    ctx,
    what: str = None,
    m: discord.Member = None
):

    if not adm(ctx):
        return await ctx.send("⛔ Chỉ Admin.")

    if what != "tien" or not m:
        return await ctx.send(
            "❌ `!reset tien @user`"
        )

    U(m)["cash"] = START
    U(m)["bank"] = 0

    await ctx.send(
        f"♻️ {m.mention} đã reset về "
        f"**{fm(START)}**."
    )


# =========================
# KICK
# =========================

@bot.command()
async def kick(
    ctx,
    m: discord.Member = None
):

    if not adm(ctx):
        return await ctx.send("⛔ Chỉ Admin.")

    if not m:
        return await ctx.send(
            "❌ `!kick @user`"
        )

    await m.kick()

    await ctx.send(
        f"👢 Đã kick {m.mention}."
    )


# =========================
# BAN
# =========================

@bot.command()
async def ban(
    ctx,
    m: discord.Member = None
):

    if not adm(ctx):
        return await ctx.send("⛔ Chỉ Admin.")

    if not m:
        return await ctx.send(
            "❌ `!ban @user`"
        )

    await m.ban()

    await ctx.send(
        f"🔨 Đã ban {m.mention}."
    )


# =========================
# KHÓA MÕM
# =========================

@bot.command()
async def khoamom(
    ctx,
    m: discord.Member = None
):

    if not adm(ctx):
        return await ctx.send("⛔ Chỉ Admin.")

    if not m:
        return await ctx.send(
            "❌ `!khoamom @user`"
        )

    U(m)["muted"] = True

    await ctx.send(
        f"🔇 {m.mention} đã bị **khóa mõm**."
    )


# =========================
# MỞ KHÓA MÕM
# =========================

@bot.command()
async def unkhoamom(
    ctx,
    m: discord.Member = None
):

    if not adm(ctx):
        return await ctx.send("⛔ Chỉ Admin.")

    if not m:
        return await ctx.send(
            "❌ `!unkhoamom @user`"
        )

    U(m)["muted"] = False

    await ctx.send(
        f"🔊 {m.mention} đã được **mở khóa**.\n"
        "🟢 Có thể chơi và nói chuyện lại."
    )


# =========================
# LỖI
# =========================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(
        error,
        commands.CommandNotFound
    ):
        return

    if isinstance(
        error,
        commands.MissingRequiredArgument
    ):
        return await ctx.send(
            "❌ Thiếu thông tin. "
            "Gõ `!trogiup`."
        )

    if isinstance(
        error,
        commands.BadArgument
    ):
        return await ctx.send(
            "❌ Sai cú pháp."
        )

    if isinstance(
        error,
        commands.CommandOnCooldown
    ):
        return

    print("ERROR:", error)


# =========================
# CHẠY BOT
# =========================

if not TOKEN:

    print(
        "❌ Không tìm thấy biến "
        "TOKEN_BOT!"
    )

else:

    print("🚀 Đang khởi động bot...")

    bot.run(TOKEN)
