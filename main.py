import os
import asyncio
import random
import time
import discord
from discord.ext import commands
from collections import Counter

# =========================
# CẤU HÌNH BOT
# =========================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

users = {}
cooldowns = {}


# =========================
# CHỐNG SPAM
# =========================

def check_spam(user_id, cmd_name, limit_seconds=2.0):
    now = time.time()
    key = f"{user_id}_{cmd_name}"

    if key in cooldowns:
        diff = now - cooldowns[key]

        if diff < limit_seconds:
            return round(limit_seconds - diff, 1)

    cooldowns[key] = now
    return 0.0


# =========================
# TÀI KHOẢN
# =========================

def get_user(uid):
    if uid not in users:
        users[uid] = {
            "cash": 5003,
            "bank": 0
        }

    return users[uid]


# =========================
# BOT READY
# =========================

@bot.event
async def on_ready():
    print(f"✅ BOT ĐÃ SẴN SÀNG: {bot.user}")
    print(f"🆔 ID: {bot.user.id}")


# =========================================================
# MENU HELP - GIỐNG ẢNH
# =========================================================

@bot.command(name="help", aliases=["menu", "lenh"])
async def help_cmd(ctx):

    embed = discord.Embed(
        title="🎰 CASINO BET88 UY TÍN 🎰",
        description="━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        color=discord.Color.blurple()
    )

    # PVP
    embed.add_field(
        name="⚔️ ĐỐI KHÁNG (PVP)",
        value=(
            "`!danhbai @User`\n"
            "`!thachdau @User`\n"
            "`!dagapvp @User`\n"
            "`!tuxipvp @User`"
        ),
        inline=False
    )

    # SOLO
    embed.add_field(
        name="🎲 CASINO (SOLO)",
        value=(
            "`!tx [tài/xỉu] [tiền]`\n"
            "`!daga [tiền]`\n"
            "`!tuxi [tiền]`\n"
            "`!bc [cửa] [tiền]`\n"
            "`!xd [chẵn/lẻ] [tiền]`\n"
            "`!bai [tiền]`\n"
            "`!rl [tiền]`\n"
            "`!quay [tiền]`\n"
            "`!duangua [cửa] [tiền]`\n"
            "`!coinflip [ngửa/sấp] [tiền]`"
        ),
        inline=False
    )

    # SYSTEM
    embed.add_field(
        name="🏦 HỆ THỐNG",
        value=(
            "`!vi` - Xem số dư\n"
            "`!gui [tiền]` - Gửi ngân hàng\n"
            "`!rut [tiền]` - Rút tiền\n"
            "`!chuyen @User [tiền]` - Chuyển tiền\n"
            "`!diemandanh` - Điểm danh\n"
            "`!bxh` - Bảng xếp hạng\n"
            "`!nhapcode [code]` - Nhập code"
        ),
        inline=False
    )

    embed.set_footer(
        text="🎰 BET88 • Dùng !help để xem lại menu"
    )

    await ctx.send(embed=embed)


# =========================================================
# !VI - XEM VÍ
# =========================================================

@bot.command(name="vi", aliases=["money", "bal"])
async def vi_cmd(ctx, member: discord.Member = None):

    cd = check_spam(ctx.author.id, "vi", 1.5)

    if cd > 0:
        return await ctx.send(
            f"⚠️ {ctx.author.mention} Gõ từ từ thôi! Đợi **{cd}s**."
        )

    target = member if member else ctx.author
    u = get_user(target.id)

    msg = (
        f"💳 **TÀI SẢN CỦA {target.display_name}**\n\n"
        f"💵 Tiền mặt: `{u['cash']:,} $`\n"
        f"🏦 Ngân hàng: `{u['bank']:,} $`\n"
        f"💰 Tổng tài sản: `{u['cash'] + u['bank']:,} $`"
    )

    await ctx.send(msg)


# =========================================================
# !QUAY - SLOT
# =========================================================

@bot.command(name="quay")
async def quay_cmd(ctx, bet: int = None):

    cd = check_spam(ctx.author.id, "quay", 1.5)

    if cd > 0:
        return await ctx.send(
            f"⚠️ Đợi **{cd}s** rồi quay tiếp."
        )

    if not bet or bet <= 0:
        return await ctx.send(
            "❌ Cú pháp: `!quay [tiền_cược]`"
        )

    u = get_user(ctx.author.id)

    if u["cash"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền mặt!")

    symbols = ["💎", "🔔", "🍋", "🍒"]

    msg = await ctx.send(
        "🎰 **VÒNG QUAY**\n"
        "[ ❔ ] [ ❔ ] [ ❔ ]"
    )

    await asyncio.sleep(0.5)

    await msg.edit(
        content=
        "🎰 **VÒNG QUAY**\n"
        "[ 💎 ] [ ❔ ] [ ❔ ]"
    )

    await asyncio.sleep(0.5)

    is_win = random.random() < 0.4

    if is_win:
        s = random.choice(symbols)
        r1 = s
        r2 = s
        r3 = random.choice(symbols)
    else:
        r1, r2, r3 = random.sample(symbols, 3)

    cnt = Counter([r1, r2, r3])
    max_f = max(cnt.values())

    if max_f >= 2:

        win = bet * max_f
        u["cash"] += win - bet

        await msg.edit(
            content=
            f"🎰 **KẾT QUẢ**\n"
            f"[ {r1} ] [ {r2} ] [ {r3} ]\n\n"
            f"✨ **Trúng {max_f} con (x{max_f})!**\n"
            f"💰 Nhận: `+{win:,} $`"
        )

    else:

        u["cash"] -= bet

        await msg.edit(
            content=
            f"🎰 **KẾT QUẢ**\n"
            f"[ {r1} ] [ {r2} ] [ {r3} ]\n\n"
            f"😢 **Chúc bạn may mắn lần sau!**\n"
            f"💸 Mất: `-{bet:,} $`"
        )


# =========================================================
# !XD - XÓC ĐĨA
# =========================================================

@bot.command(name="xd", aliases=["xocdia"])
async def xocdia_cmd(ctx, choice: str = None, bet: int = None):

    cd = check_spam(ctx.author.id, "xd", 1.5)

    if cd > 0:
        return await ctx.send(
            f"⚠️ Đợi **{cd}s** rồi chơi tiếp."
        )

    if (
        not choice
        or choice.lower() not in ["chan", "le"]
        or not bet
        or bet <= 0
    ):
        return await ctx.send(
            "❌ Cú pháp: `!xd [chan/le] [tiền]`"
        )

    u = get_user(ctx.author.id)

    if u["cash"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền mặt!")

    msg = await ctx.send(
        "🪙 **XÓC ĐĨA**\n"
        "📳 *Đang xóc...*"
    )

    await asyncio.sleep(0.8)

    red_count = random.randint(0, 4)

    ket_qua = (
        "chan"
        if red_count % 2 == 0
        else "le"
    )

    board = (
        "🔴" * red_count
        + "⚪" * (4 - red_count)
    )

    result = (
        f"🪙 **XÓC ĐĨA - KẾT QUẢ**\n\n"
        f"🥣 Bát mở: `{board}`\n"
        f"🔴 Đỏ: `{red_count}`\n"
        f"🎯 Kết quả: **{ket_qua.upper()}**"
    )

    if choice.lower() == ket_qua:

        u["cash"] += bet

        result += (
            f"\n\n🎉 **THẮNG!**\n"
            f"💰 Nhận `+{bet:,} $`"
        )

    else:

        u["cash"] -= bet

        result += (
            f"\n\n💸 **THUA!**\n"
            f"💰 Mất `-{bet:,} $`"
        )

    await msg.edit(content=result)


# =========================================================
# !BC - BẦU CUA
# =========================================================

@bot.command(name="bc", aliases=["baucua"])
async def baucua_cmd(ctx, choice: str = None, bet: int = None):

    cd = check_spam(ctx.author.id, "bc", 1.5)

    if cd > 0:
        return await ctx.send(
            f"⚠️ Đợi **{cd}s** rồi chơi tiếp."
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
            "❌ Cú pháp:\n"
            "`!bc ca 100`\n"
            "`!bc tom 100`\n"
            "`!bc cua 100`\n"
            "`!bc bau 100`\n"
            "`!bc ga 100`\n"
            "`!bc nai 100`"
        )

    u = get_user(ctx.author.id)

    if u["cash"] < bet:
        return await ctx.send(
            "❌ Bạn không đủ tiền mặt!"
        )

    msg = await ctx.send(
        "🎲 **BẦU CUA**\n"
        "🥣 *Đang lắc...*"
    )

    await asyncio.sleep(0.8)

    keys = list(animals.keys())

    d1 = random.choice(keys)
    d2 = random.choice(keys)
    d3 = random.choice(keys)

    result_list = [d1, d2, d3]

    matches = result_list.count(
        choice.lower()
    )

    result = (
        "🎲 **BẦU CUA - KẾT QUẢ**\n\n"
        f"{animals[d1]} **{d1.upper()}**  "
        f"{animals[d2]} **{d2.upper()}**  "
        f"{animals[d3]} **{d3.upper()}**"
    )

    if matches > 0:

        win = int(bet * matches * 1.5)

        u["cash"] += win

        result += (
            f"\n\n✨ **Trúng {matches} con!**\n"
            f"💰 Nhận `+{win:,} $`"
        )

    else:

        u["cash"] -= bet

        result += (
            f"\n\n😢 **Không trúng!**\n"
            f"💸 Mất `-{bet:,} $`"
        )

    await msg.edit(content=result)


# =========================================================
# !TX - TÀI XỈU
# =========================================================

@bot.command(name="tx", aliases=["taixiu"])
async def taixiu_cmd(ctx, choice: str = None, bet: int = None):

    cd = check_spam(ctx.author.id, "tx", 2.0)

    if cd > 0:
        return await ctx.send(
            f"⚠️ Đợi **{cd}s** rồi chơi tiếp."
        )

    if not choice or choice.lower() not in ["tai", "xiu"]:
        return await ctx.send(
            "❌ Cú pháp:\n"
            "`!tx tai 100`\n"
            "`!tx xiu 100`"
        )

    if not bet or bet <= 0:
        return await ctx.send(
            "❌ Số tiền cược không hợp lệ!"
        )

    u = get_user(ctx.author.id)

    if u["cash"] < bet:
        return await ctx.send(
            "❌ Bạn không đủ tiền mặt!"
        )

    choice = choice.lower()

    msg = await ctx.send(
        "🎲 **TÀI XỈU BET88**\n\n"
        "🎲 [ ❔ ] [ ❔ ] [ ❔ ]\n"
        "⏳ Đang lắc xúc xắc..."
    )

    await asyncio.sleep(0.7)

    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    d3 = random.randint(1, 6)

    total
