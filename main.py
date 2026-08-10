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
cooldowns = {}
diemdanh_cooldowns = {}

tx_session = {
    "active": False,
    "msg": None,
    "bets": {},
    "total_tai": 0,
    "total_xiu": 0
}

# Màu thanh dọc bên trái
BLUE = 0x3498DB
ORANGE = 0xF1C40F
GREEN = 0x2ECC71
RED = 0xE74C3C


def make_embed(title, text, color):
    return discord.Embed(
        title=title,
        description=text,
        color=color
    )


def check_spam(uid, cmd, seconds=1.5):
    now = time.time()
    key = f"{uid}_{cmd}"

    if key in cooldowns:
        left = seconds - (now - cooldowns[key])
        if left > 0:
            return round(left, 1)

    cooldowns[key] = now
    return 0


def get_user(uid, name="Thành viên"):
    if uid not in users:
        users[uid] = {
            "name": name,
            "cash": 4899,
            "bank": 0,
            "hang": "Người chơi Thường",
            "ga": "Gà Công Nghiệp 🐥"
        }

    return users[uid]


# =========================
# READY
# =========================

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="!trogiup | Casino Bet88")
    )
    print(f"✅ BOT ĐÃ ONLINE: {bot.user}")


# =========================
# TRỢ GIÚP
# =========================

@bot.command(name="trogiup", aliases=["help"])
async def trogiup(ctx):

    cd = check_spam(ctx.author.id, "trogiup")

    if cd:
        return await ctx.send(
            f"⚠️ {ctx.author.mention} Đợi **{cd}** giây."
        )

    e = make_embed(
        "🎰 CASINO BET88 - TRỢ GIÚP",
        (
            "⚔️ **ĐỐI KHÁNG (PVP)**\n"
            "`!danhbai` `!thachdau` `!dagapvp` `!tuxipvp @User`\n\n"

            "🎲 **CASINO (SOLO)**\n"
            "`!tx` `!daga` `!tuxi` `!bc` `!xd`\n"
            "`!bai` `!rl` `!quay` `!duangua` `!coinflip`\n\n"

            "🏛️ **HỆ THỐNG**\n"
            "`!vi` `!gui` `!rut` `!chuyen`\n"
            "`!diemdanh` `!bxh` `!nhapcode`"
        ),
        BLUE
    )

    e.set_footer(text="🎁 Chúc bạn may mắn tại Casino Bet88!")

    await ctx.send(embed=e)


# =========================
# VÍ
# =========================

@bot.command(name="vi", aliases=["money", "bal"])
async def vi_cmd(ctx, member: discord.Member = None):

    target = member or ctx.author
    u = get_user(target.id, target.name)

    tag = target.id % 10000

    e = make_embed(
        "💳 THÔNG TIN TÀI KHOẢN",
        (
            f"👤 **Chủ tài khoản:** "
            f"{target.name.upper()}_{tag:04d}\n\n"

            f"🏷️ **Hạng thẻ:** {u['hang']}\n"
            f"🐓 **Gà chiến:** {u['ga']}\n\n"

            f"💵 **Tiền mặt:** `{u['cash']:,}$`\n"
            f"🏦 **Két sắt:** `{u['bank']:,}$`"
        ),
        BLUE
    )

    await ctx.send(embed=e)


# =========================
# ĐIỂM DANH
# =========================

@bot.command(name="diemdanh")
async def diemdanh_cmd(ctx):

    cd = check_spam(ctx.author.id, "diemdanh", 2)

    if cd:
        return await ctx.send(
            f"⚠️ {ctx.author.mention} Đợi **{cd}** giây."
        )

    uid = ctx.author.id
    now = time.time()

    if (
        uid in diemdanh_cooldowns
        and now - diemdanh_cooldowns[uid] < 43200
    ):
        return await ctx.send(
            "⚠️ Bạn đã điểm danh trong 12 giờ qua!"
        )

    diemdanh_cooldowns[uid] = now

    reward = 2593
    u = get_user(uid, ctx.author.name)
    u["cash"] += reward

    e = make_embed(
        "🎁 ĐIỂM DANH THÀNH CÔNG",
        f"💰 Bạn nhận được **+{reward:,}$** vào ví.",
        GREEN
    )

    await ctx.send(embed=e)


# =========================
# QUAY SLOT
# =========================

@bot.command(name="quay")
async def quay_cmd(ctx, bet: int = None):

    cd = check_spam(ctx.author.id, "quay")

    if cd:
        return await ctx.send(
            f"⚠️ Đợi **{cd}** giây."
        )

    if not bet or bet <= 0:
        return await ctx.send(
            "❌ Cú pháp: `!quay [tiền]`"
        )

    u = get_user(ctx.author.id, ctx.author.name)

    if u["cash"] < bet:
        return await ctx.send(
            f"❌ Ví chỉ còn `{u['cash']:,}$`."
        )

    u["cash"] -= bet

    slots = ["🍋", "🔔", "🍒", "⭐", "💎"]

    s1 = random.choice(slots)
    s2 = random.choice(slots)
    s3 = random.choice(slots)

    # CAM - ĐANG QUAY
    e = make_embed(
        "🎰 MÁY SLOT BET88",
        (
            "🟠 **ĐANG QUAY...**\n\n"
            f"`[ {s1} ] [ ❔ ] [ ❔ ]`"
        ),
        ORANGE
    )

    msg = await ctx.send(embed=e)

    await asyncio.sleep(0.6)

    e.description = (
        "🟠 **ĐANG QUAY...**\n\n"
        f"`[ {s1} ] [ {s2} ] [ ❔ ]`"
    )

    await msg.edit(embed=e)

    await asyncio.sleep(0.7)

    win = s1 == s2 == s3

    if win:

        reward = bet * 4
        u["cash"] += bet + reward

        e = make_embed(
            "🎰 MÁY SLOT BET88",
            (
                f"`[ {s1} ] [ {s2} ] [ {s3} ]`\n\n"
                "✨ **NỔ HŨ THÀNH CÔNG!**\n"
                f"💰 Nhận **+{reward:,}$**"
            ),
            GREEN
        )

    else:

        e = make_embed(
            "🎰 MÁY SLOT BET88",
            (
                f"`[ {s1} ] [ {s2} ] [ {s3} ]`\n\n"
                "💸 **TRẬT HŨ!**\n"
                f"Mất **-{bet:,}$**"
            ),
            RED
        )

    await msg.edit(embed=e)


# =========================
# TÀI XỈU
# =========================

@bot.command(name="tx", aliases=["taixiu"])
async def tx_cmd(ctx, choice: str = None, bet: int = None):

    global tx_session

    uid = ctx.author.id
    u = get_user(uid, ctx.author.name)

    # -------------------------
    # MỞ PHIÊN
    # -------------------------

    if not choice:

        if tx_session["active"]:
            return await ctx.send(
                "⚠️ Sòng Tài Xỉu đang mở rồi!"
            )

        tx_session["active"] = True
        tx_session["bets"] = {}
        tx_session["total_tai"] = 0
        tx_session["total_xiu"] = 0

        e = make_embed(
            "🎲 SÒNG TÀI XỈU 30S 🎲",
            (
                "Gõ `!tx <tai/xiu> <tiền>`\n"
                "(Tối đa 10,000,000$/ván)\n\n"

                "⏱️ **Thời gian: 30 giây**\n\n"

                "Tổng **TÀI:** `0$` | "
                "Tổng **XỈU:** `0$`"
            ),
            ORANGE
        )

        msg = await ctx.send(embed=e)
        tx_session["msg"] = msg

        # 20 giây
        await asyncio.sleep(10)

        if not tx_session["active"]:
            return

        e.description = (
            "Gõ `!tx <tai/xiu> <tiền>`\n"
            "(Tối đa 10,000,000$/ván)\n\n"

            "⏱️ **Thời gian: 20 giây**\n\n"

            f"Tổng **TÀI:** `{tx_session['total_tai']:,}$` | "
            f"Tổng **XỈU:** `{tx_session['total_xiu']:,}$`"
        )

        await msg.edit(embed=e)

        # 10 giây
        await asyncio.sleep(10)

        if not tx_session["active"]:
            return

        e.description = (
            "Gõ `!tx <tai/xiu> <tiền>`\n"
            "(Tối đa 10,000,000$/ván)\n\n"

            "⏱️ **Thời gian: 10 giây**\n\n"

            f"Tổng **TÀI:** `{tx_session['total_tai']:,}$` | "
            f"Tổng **XỈU:** `{tx_session['total_xiu']:,}$`"
        )

        await msg.edit(embed=e)

        # Hết giờ
        await asyncio.sleep(10)

        if not tx_session["active"]:
            return

        tx_session["active"] = False

        # XÓC BÁT - CAM
        e = make_embed(
            "🎲 NHÀ CÁI ĐANG XÓC BÁT...",
            (
                "🥣 **Đang xóc...**\n\n"
                "`[ ❔ ] - [ ❔ ] - [ ❔ ]`"
            ),
            ORANGE
        )

        await msg.edit(embed=e)

        await asyncio.sleep(2)

        # -------------------------
        # KẾT QUẢ
        # -------------------------

        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        d3 = random.randint(1, 6)

        total = d1 + d2 + d3

        result = "tai" if total >= 11 else "xiu"
        result_text = "TÀI 🔴" if result == "tai" else "XỈU 🔵"

        winners = []
        losers = []

        for pid, data in tx_session["bets"].items():

            player = get_user(pid)
            amount = data["amount"]

            if data["choice"] == result:

                player["cash"] += amount * 2

                winners.append(
                    f"• {data['name']} `(+{amount:,}$)`"
                )

            else:

                losers.append(
                    f"• {data['name']} `(-{amount:,}$)`"
                )

        win_text = "\n".join(winners) if winners else "Không có"
        lose_text = "\n".join(losers) if losers else "Không có"

        # Nếu có người thắng -> xanh lá
        # Không có người thắng -> đỏ
        result_color = GREEN if winners else RED

        e = make_embed(
            "🎲 KẾT QUẢ TÀI XỈU 🎲",
            (
                "Xúc xắc\n"
                f"`[ {d1} ] - [ {d2} ] - [ {d3} ]` "
                f"→ **{total} Điểm ({result_text})**\n\n"

                "🎉 **THẮNG**\n"
                f"```{win_text}```\n"

                "💸 **THUA**\n"
                f"```{lose_text}```"
            ),
            result_color
        )

        await msg.edit(embed=e)

        return

    # -------------------------
    # ĐẶT CƯỢC
    # -------------------------

    choice = choice.lower()

    if choice not in ["tai", "xiu"]:
        return await ctx.send(
            "❌ Dùng: `!tx tai 100` hoặc `!tx xiu 100`"
        )

    if not tx_session["active"]:
        return await ctx.send(
            "❌ Chưa có phiên Tài Xỉu!"
        )

    if not bet or bet <= 0:
        return await ctx.send(
            "❌ Số tiền cược không hợp lệ!"
        )

    if bet > 10000000:
        return await ctx.send(
            "❌ Tối đa **10,000,000$ / ván**."
        )

    if u["cash"] < bet:
        return await ctx.send(
            f"❌ Ví chỉ còn `{u['cash']:,}$`."
        )

    u["cash"] -= bet

    # Nếu cược lại thì hoàn tiền cược cũ
    if uid in tx_session["bets"]:

        old = tx_session["bets"][uid]

        if old["choice"] == "tai":
            tx_session["total_tai"] -= old["amount"]
        else:
            tx_session["total_xiu"] -= old["amount"]

    tx_session["bets"][uid] = {
        "name": ctx.author.name,
        "choice": choice,
        "amount": bet
    }

    if choice == "tai":
        tx_session["total_tai"] += bet
    else:
        tx_session["total_xiu"] += bet

    e = make_embed(
        "🎲 ĐẶT CƯỢC THÀNH CÔNG",
        (
            f"👤 {ctx.author.mention}\n"
            f"🎯 Cửa: **{choice.upper()}**\n"
            f"💰 Cược: **{bet:,}$**"
        ),
        GREEN
    )

    await ctx.send(embed=e)


# =========================
# XÓC ĐĨA
# =========================

@bot.command(name="xd", aliases=["xocdia"])
async def xd_cmd(ctx, choice: str = None, bet: int = None):

    cd = check_spam(ctx.author.id, "xd")

    if cd:
        return await ctx.send(
            f"⚠️ Đợi **{cd}** giây."
        )

    if (
        not choice
        or choice.lower() not in ["chan", "le"]
        or not bet
        or bet <= 0
    ):
        return await ctx.send(
            "❌ Cú pháp: `!xd chan 100` hoặc `!xd le 100`"
        )

    u = get_user(ctx.author.id, ctx.author.name)

    if u["cash"] < bet:
        return await ctx.send(
            f"❌ Ví chỉ còn `{u['cash']:,}$`."
        )

    u["cash"] -= bet

    # CAM
    e = make_embed(
        "🪙 XÓC ĐĨA BET88",
        "🪙 **ĐANG XÓC ĐĨA...**",
        ORANGE
    )

    msg = await ctx.send(embed=e)

    await asyncio.sleep(0.8)

    e.description = "🥣 **ĐẶT BÁT XUỐNG...**"

    await msg.edit(embed=e)

    await asyncio.sleep(0.8)

    reds = random.randint(0, 4)

    board = "🔴" * reds + "⚪" * (4 - reds)

    even = reds % 2 == 0
    result = "CHẴN" if even else "LẺ"

    win = (
        (choice.lower() == "chan" and even)
        or
        (choice.lower() == "le" and not even)
    )

    if win:

        u["cash"] += bet * 2

        e = make_embed(
            "🪙 XÓC ĐĨA BET88",
            (
                f"🥣 **Kết quả:** {board}\n"
                f"📊 **{result} - {reds} Đỏ**\n\n"
                "🎉 **THẮNG!**\n"
                f"💰 Nhận **+{bet:,}$**"
            ),
            GREEN
        )

    else:

        e = make_embed(
            "🪙 XÓC ĐĨA BET88",
            (
                f"🥣 **Kết quả:** {board}\n"
                f"📊 **{result} - {reds} Đỏ**\n\n"
                "💸 **THUA!**\n"
                f"Mất **-{bet:,}$**"
            ),
            RED
        )

    await msg.edit(embed=e)


# =========================
# BẦU CUA
# =========================

@bot.command(name="bc", aliases=["baucua"])
async def bc_cmd(ctx, choice: str = None, bet: int = None):

    cd = check_spam(ctx.author.id, "bc")

    if cd:
        return await ctx.send(
            f"⚠️ Đợi **{cd}** giây."
        )

    animals = {
        "ca": "🐟",
        "tom": "🦐",
        "cua": "🦀",
        "bau": "🥒",
        "ga": "🐓",
        "nai": "🦌"
    }

    if (
        not choice
        or choice.lower() not in animals
        or not bet
        or bet <= 0
    ):
        return await ctx.send(
            "❌ Cú pháp: `!bc ca 100`"
        )

    u = get_user(ctx.author.id, ctx.author.name)

    if u["cash"] < bet:
        return await ctx.send(
            f"❌ Ví chỉ còn `{u['cash']:,}$`."
        )

    u["cash"] -= bet

    # CAM
    e = make_embed(
        "🎲 BẦU CUA BET88",
        "🟠 **ĐANG LẮC HỘT...**",
        ORANGE
    )

    msg = await ctx.send(embed=e)

    await asyncio.sleep(0.7)

    e.description = "🥣 **ĐANG MỞ BÁT...**"

    await msg.edit(embed=e)

    await asyncio.sleep(0.7)

    keys = list(animals)

    d1 = random.choice(keys)
    d2 = random.choice(keys)
    d3 = random.choice(keys)

    results = [d1, d2, d3]
    matches = results.count(choice.lower())

    display = (
        f"`[ {animals[d1]} ] "
        f"[ {animals[d2]} ] "
        f"[ {animals[d3]} ]`"
    )

    if matches:

        reward = bet * matches
        u["cash"] += bet + reward

        e = make_embed(
            "🎲 BẦU CUA BET88",
            (
                f"{display}\n\n"
                f"🎉 **TRÚNG {matches} CON!**\n"
                f"💰 Nhận **+{reward:,}$**"
            ),
            GREEN
        )

    else:

        e = make_embed(
            "🎲 BẦU CUA BET88",
            (
                f"{display}\n\n"
                "💸 **KHÔNG TRÚNG!**\n"
                f"Mất **-{bet:,}$**"
            ),
            RED
        )

    await msg.edit(embed=e)


# =========================
# CHẠY BOT
# =========================

token = os.getenv("TOKEN_BOT")

if not token:
    print("❌ Chưa có TOKEN_BOT!")
else:
    bot.run(token)
