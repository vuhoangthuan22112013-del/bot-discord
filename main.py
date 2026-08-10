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
cooldowns = {}
diemdanh_cooldowns = {}

# =========================================================
# TÀI XỈU
# =========================================================

tx_session = {
    "active": False,
    "msg": None,
    "bets": {},
    "total_tai": 0,
    "total_xiu": 0,
    "task": None
}


# =========================================================
# MÀU EMBED
# =========================================================

COLOR_ORANGE = discord.Color.from_rgb(255, 140, 0)
COLOR_GREEN = discord.Color.from_rgb(46, 204, 113)
COLOR_RED = discord.Color.from_rgb(231, 76, 60)
COLOR_BLUE = discord.Color.from_rgb(52, 152, 219)


# =========================================================
# CHỐNG SPAM
# =========================================================

def check_spam(user_id, cmd_name, limit_seconds=1.5):
    now = time.time()
    key = f"{user_id}_{cmd_name}"

    if key in cooldowns:
        diff = now - cooldowns[key]

        if diff < limit_seconds:
            return round(limit_seconds - diff, 1)

    cooldowns[key] = now
    return 0.0


# =========================================================
# TÀI KHOẢN
# =========================================================

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


# =========================================================
# BOT ONLINE
# =========================================================

@bot.event
async def on_ready():

    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(
            name="!trogiup | Casino Bet88"
        )
    )

    print(
        f"✅ BOT ĐÃ SẴN SÀNG HOẠT ĐỘNG: {bot.user}"
    )


# =========================================================
# MENU TRỢ GIÚP
# GIỮ NGUYÊN KIỂU MENU BẠN ĐÃ CHỌN
# =========================================================

@bot.command(name="trogiup", aliases=["help"])
async def trogiup_cmd(ctx):

    cd = check_spam(
        ctx.author.id,
        "trogiup",
        1.5
    )

    if cd > 0:
        return await ctx.send(
            f"⚠️ {ctx.author.mention} "
            f"Gõ từ từ thôi! Đợi **{cd}** giây nữa!"
        )

    embed = discord.Embed(
        title="🎰 CASINO BET88 UY TÍN 🎰",
        color=COLOR_BLUE
    )

    embed.add_field(
        name="⚔️ ĐỐI KHÁNG (PVP)",
        value=(
            "`!danhbai`, `!thachdau`, "
            "`!dagapvp`, `!tuxipvp @User`"
        ),
        inline=False
    )

    embed.add_field(
        name="🎲 CASINO (SOLO)",
        value=(
            "`!tx`, `!daga`, `!tuxi`, `!bc`, "
            "`!xd`, `!bai`, `!rl`, `!quay`,\n"
            "`!duangua`, `!coinflip`"
        ),
        inline=False
    )

    embed.add_field(
        name="🏛️ HỆ THỐNG",
        value=(
            "`!vi`, `!gui`, `!rut`, `!chuyen`, "
            "`!diemdanh`, `!bxh`, `!nhapcode`"
        ),
        inline=False
    )

    await ctx.send(embed=embed)


# =========================================================
# ĐIỂM DANH
# =========================================================

@bot.command(name="diemdanh")
async def diemdanh_cmd(ctx):

    cd = check_spam(
        ctx.author.id,
        "diemdanh",
        2.0
    )

    if cd > 0:
        return await ctx.send(
            f"⚠️ {ctx.author.mention} "
            f"Gõ từ từ thôi! Đợi **{cd}** giây nữa!"
        )

    user_id = ctx.author.id
    now = time.time()

    if (
        user_id in diemdanh_cooldowns
        and
        now - diemdanh_cooldowns[user_id]
        < 12 * 3600
    ):
        return await ctx.send(
            f"⚠️ {ctx.author.mention} "
            f"Bạn đã điểm danh trong 12 giờ qua rồi!"
        )

    diemdanh_cooldowns[user_id] = now

    reward = 2593

    u = get_user(
        user_id,
        ctx.author.name
    )

    u["cash"] += reward

    await ctx.send(
        f"🎁 {ctx.author.mention} "
        f"Điểm danh! `+{reward:,}$`"
    )


# =========================================================
# VÍ
# =========================================================

@bot.command(name="vi", aliases=["money", "bal"])
async def vi_cmd(
    ctx,
    member: discord.Member = None
):

    target = (
        member
        if member
        else ctx.author
    )

    u = get_user(
        target.id,
        target.name
    )

    tag_id = target.id % 10000

    embed = discord.Embed(
        title="💳 TÀI KHOẢN",
        color=COLOR_BLUE
    )

    embed.add_field(
        name="👤 Thành viên",
        value=(
            f"**{target.name.upper()}_{tag_id:04d}**"
        ),
        inline=False
    )

    embed.add_field(
        name="🏷️ Hạng thẻ",
        value=u["hang"],
        inline=False
    )

    embed.add_field(
        name="🐥 Gà chiến",
        value=u["ga"],
        inline=False
    )

    embed.add_field(
        name="💵 Tiền mặt",
        value=f"`{u['cash']:,}$`",
        inline=True
    )

    embed.add_field(
        name="🏦 Két sắt",
        value=f"`{u['bank']:,}$`",
        inline=True
    )

    await ctx.send(embed=embed)


# =========================================================
# HÀM TẠO EMBED GAME
# =========================================================

def game_embed(
    title,
    description,
    color,
    footer=None
):

    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )

    if footer:
        embed.set_footer(
            text=footer
        )

    return embed


# =========================================================
# TÀI XỈU
#
# DÙNG:
# !tx tai 1000
# !tx xiu 1000
#
# KHÔNG CẦN !tx TRƯỚC
# =========================================================

@bot.command(name="tx", aliases=["taixiu"])
async def taixiu_cmd(
    ctx,
    choice: str = None,
    bet: int = None
):

    global tx_session

    if not choice:

        if tx_session["active"]:

            return await ctx.send(
                "⚠️ Phiên Tài Xỉu đang diễn ra!\n"
                "Hãy dùng:\n"
                "`!tx tai số tiền` hoặc "
                "`!tx xiu số tiền`"
            )

        return await ctx.send(
            "🎲 Cú pháp:\n"
            "`!tx tai 1000`\n"
            "`!tx xiu 1000`"
        )

    choice = choice.lower()

    if choice not in [
        "tai",
        "xiu"
    ]:

        return await ctx.send(
            "❌ Chỉ được chọn `tai` hoặc `xiu`."
        )

    if not bet or bet <= 0:

        return await ctx.send(
            "❌ Số tiền cược không hợp lệ."
        )

    u = get_user(
        ctx.author.id,
        ctx.author.name
    )

    if u["cash"] < bet:

        return await ctx.send(
            f"❌ Bạn không đủ tiền!\n"
            f"Ví còn `{u['cash']:,}$`."
        )

    # =====================================================
    # NẾU CHƯA CÓ PHIÊN -> TỰ ĐỘNG MỞ
    # =====================================================

    if not tx_session["active"]:

        tx_session["active"] = True
        tx_session["bets"] = {}
        tx_session["total_tai"] = 0
        tx_session["total_xiu"] = 0

    # =====================================================
    # MỖI NGƯỜI CHỈ ĐƯỢC ĐẶT 1 LẦN
    # =====================================================

    if ctx.author.id in tx_session["bets"]:

        return await ctx.send(
            f"⚠️ {ctx.author.mention} "
            f"Bạn đã đặt cược rồi!\n"
            f"Mỗi người chỉ được cược **1 lần/ván**."
        )

    # Trừ tiền ngay khi đặt
    u["cash"] -= bet

    tx_session["bets"][ctx.author.id] = {
        "name": ctx.author.name,
        "choice": choice,
        "amount": bet
    }

    if choice == "tai":
        tx_session["total_tai"] += bet
    else:
        tx_session["total_xiu"] += bet

    # =====================================================
    # EMBED ĐANG CHẠY MÀU CAM
    # =====================================================

    embed = game_embed(
        "🎲 SÒNG TÀI XỈU BET88",
        (
            "🟠 **ĐANG NHẬN CƯỢC**\n\n"
            f"👤 {ctx.author.mention}\n"
            f"🎯 Cửa: **{choice.upper()}**\n"
            f"💰 Cược: `{bet:,}$`\n\n"
            "⏱️ Phiên sẽ kết thúc sau **30 giây**.\n"
            "Mỗi người chỉ được cược **1 lần**."
        ),
        COLOR_ORANGE
    )

    # =====================================================
    # PHIÊN MỚI -> TẠO TASK 30 GIÂY
    # =====================================================

    if tx_session["msg"] is None:

        msg = await ctx.send(
            embed=embed
        )

        tx_session["msg"] = msg

        tx_session["task"] = asyncio.create_task(
            finish_tx()
        )

    else:

        try:

            await tx_session["msg"].edit(
                embed=embed
            )

        except:
            pass

    await ctx.send(
        f"✅ {ctx.author.mention} "
        f"Đã cược `{bet:,}$` vào "
        f"**{choice.upper()}**!"
    )


# =========================================================
# KẾT THÚC TÀI XỈU
# =========================================================

async def finish_tx():

    global tx_session

    # 30 giây
    await asyncio.sleep(30)

    if not tx_session["active"]:
        return

    tx_session["active"] = False

    # =====================================================
    # ĐANG XÓC BÁT - CAM
    # =====================================================

    msg = tx_session["msg"]

    if msg:

        try:

            embed = game_embed(
                "🎲 NHÀ CÁI ĐANG XÓC BÁT...",
                (
                    "🟠 **ĐANG QUAY...**\n\n"
                    "🎲 `[ ? ] [ ? ] [ ? ]`\n\n"
                    "⏳ Chờ kết quả..."
                ),
                COLOR_ORANGE
            )

            await msg.edit(
                embed=embed
            )

        except:
            pass

    await asyncio.sleep(2)

    # =====================================================
    # XÚC XẮC
    # =====================================================

    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    d3 = random.randint(1, 6)

    total = d1 + d2 + d3

    result = (
        "tai"
        if total >= 11
        else "xiu"
    )

    result_text = (
        "TÀI"
        if result == "tai"
        else "XỈU"
    )

    winners = []
    losers = []

    # =====================================================
    # TÍNH THẮNG THUA
    # =====================================================

    for uid, data in tx_session["bets"].items():

        u = get_user(uid)

        amount = data["amount"]

        if data["choice"] == result:

            # Nhận tổng x2
            u["cash"] += amount * 2

            winners.append(
                f"🟢 **{data['name']}** "
                f"`+{amount * 2:,}$`"
            )

        else:

            losers.append(
                f"🔴 **{data['name']}** "
                f"`-{amount:,}$`"
            )

    winner_text = (
        "\n".join(winners)
        if winners
        else "Không có"
    )

    loser_text = (
        "\n".join(losers)
        if losers
        else "Không có"
    )

    # =====================================================
    # KẾT QUẢ
    # =====================================================

    if winners and not losers:

        final_color = COLOR_GREEN

    elif losers and not winners:

        final_color = COLOR_RED

    else:

        final_color = COLOR_GREEN

    embed = game_embed(
        "🎲 KẾT QUẢ TÀI XỈU",
        (
            f"🟢 **KẾT QUẢ**\n\n"
            f"🎲 `[ {d1} ] [ {d2} ] [ {d3} ]`\n\n"
            f"💥 Tổng: **{total}**\n"
            f"🏆 Kết quả: **{result_text}**\n\n"
            f"🟢 **THẮNG**\n"
            f"{winner_text}\n\n"
            f"🔴 **THUA**\n"
            f"{loser_text}"
        ),
        final_color,
        "Phiên Tài Xỉu đã kết thúc."
    )

    if msg:

        try:

            await msg.edit(
                embed=embed
            )

        except:
            pass

    # Reset phiên
    tx_session["msg"] = None
    tx_session["bets"] = {}
    tx_session["total_tai"] = 0
    tx_session["total_xiu"] = 0
    tx_session["task"] = None


# =========================================================
# QUAY SLOT
#
# !quay 1000
#
# 1 giống = x1.5
# 2 giống = x2
# 3 giống = x5
# =========================================================

@bot.command(name="quay")
async def quay_cmd(
    ctx,
    bet: int = None
):

    cd = check_spam(
        ctx.author.id,
        "quay",
        1.5
    )

    if cd > 0:

        return await ctx.send(
            f"⚠️ Gõ từ từ thôi! "
            f"Đợi **{cd}** giây."
        )

    if not bet or bet <= 0:

        return await ctx.send(
            "❌ Cú pháp: `!quay 1000`"
        )

    u = get_user(
        ctx.author.id,
        ctx.author.name
    )

    if u["cash"] < bet:

        return await ctx.send(
            f"❌ Bạn không đủ tiền!\n"
            f"Ví còn `{u['cash']:,}$`."
        )

    u["cash"] -= bet

    symbols = [
        "🍋",
        "🔔",
        "🍒",
        "⭐",
        "💎"
    ]

    # Chọn kết quả trước
    result = [
        random.choice(symbols),
        random.choice(symbols),
        random.choice(symbols)
    ]

    msg = await ctx.send(
        embed=game_embed(
            "🎰 MÁY SLOT BET88",
            (
                "🟠 **ĐANG QUAY...**\n\n"
                "`[ ❓ ] [ ❓ ] [ ❓ ]`\n\n"
                f"💰 Cược: `{bet:,}$`"
            ),
            COLOR_ORANGE
        )
    )

    # =====================================================
    # QUAY TỪNG Ô
    # =====================================================

    await asyncio.sleep(0.8)

    await msg.edit(
        embed=game_embed(
            "🎰 MÁY SLOT BET88",
            (
                "🟠 **ĐANG QUAY...**\n\n"
                f"`[ {result[0]} ] [ ❓ ] [ ❓ ]`\n\n"
                f"💰 Cược: `{bet:,}$`"
            ),
            COLOR_ORANGE
        )
    )

    await asyncio.sleep(0.8)

    await msg.edit(
        embed=game_embed(
            "🎰 MÁY SLOT BET88",
            (
                "🟠 **ĐANG QUAY...**\n\n"
                f"`[ {result[0]} ] [ {result[1]} ] [ ❓ ]`\n\n"
                f"💰 Cược: `{bet:,}$`"
            ),
            COLOR_ORANGE
        )
    )

    await asyncio.sleep(0.8)

    await msg.edit(
        embed=game_embed(
            "🎰 MÁY SLOT BET88",
            (
                "🟠 **ĐANG QUAY...**\n\n"
                f"`[ {result[0]} ] [ {result[1]} ] "
                f"[ {result[2]} ]`\n\n"
                f"💰 Cược: `{bet:,}$`"
            ),
            COLOR_ORANGE
        )
    )

    await asyncio.sleep(0.5)

    # =====================================================
    # TÍNH SỐ LƯỢNG GIỐNG NHAU
    # =====================================================

    counts = {}

    for symbol in result:
        counts[symbol] = (
            counts.get(symbol, 0) + 1
        )

    highest = max(
        counts.values()
    )

    if highest == 3:

        multiplier = 5
        result_text = "🎉 **JACKPOT x5!**"
        win = True

    elif highest == 2:

        multiplier = 2
        result_text = "✨ **2 HÌNH GIỐNG NHAU x2!**"
        win = True

    elif highest == 1:

        multiplier = 1.5
        result_text = "✨ **1 HÌNH x1.5!**"
        win = True

    else:

        multiplier = 0
        result_text = "💥 **THUA!**"
        win = False

    # Với 3 biểu tượng luôn có ít nhất 1 cái,
    # nên theo luật này luôn có thưởng.
    # Nếu muốn 1 hình không phải thắng, có thể đổi sau.

    reward = int(
        bet * multiplier
    )

    if win:

        u["cash"] += reward

        embed = game_embed(
            "🎰 MÁY SLOT BET88",
            (
                f"🟢 **THẮNG!**\n\n"
                f"`[ {result[0]} ] [ {result[1]} ] "
                f"[ {result[2]} ]`\n\n"
                f"{result_text}\n"
                f"💰 Nhận: `+{reward:,}$`"
            ),
            COLOR_GREEN
        )

    else:

        embed = game_embed(
            "🎰 MÁY SLOT BET88",
            (
                f"🔴 **THUA!**\n\n"
                f"`[ {result[0]} ] [ {result[1]} ] "
                f"[ {result[2]} ]`\n\n"
                f"{result_text}\n"
                f"💸 Mất: `-{bet:,}$`"
            ),
            COLOR_RED
        )

    await msg.edit(
        embed=embed
    )


# =========================================================
# XÓC ĐĨA
#
# !xd chan 1000
# !xd le 1000
#
# 1,3 = LẺ
# 2,4 = CHẴN
#
# THẮNG x2
# =========================================================

@bot.command(name="xd", aliases=["xocdia"])
async def xocdia_cmd(
    ctx,
    choice: str = None,
    bet: int = None
):

    cd = check_spam(
        ctx.author.id,
        "xd",
        1.5
    )

    if cd > 0:

        return await ctx.send(
            f"⚠️ Gõ từ từ thôi! "
            f"Đợi **{cd}** giây."
        )

    if (
        not choice
        or choice.lower()
        not in ["chan", "le"]
        or not bet
        or bet <= 0
    ):

        return await ctx.send(
            "❌ Cú pháp:\n"
            "`!xd chan 1000`\n"
            "`!xd le 1000`"
        )

    choice = choice.lower()

    u = get_user(
        ctx.author.id,
        ctx.author.name
    )

    if u["cash"] < bet:

        return await ctx.send(
            f"❌ Bạn không đủ tiền!\n"
            f"Ví còn `{u['cash']:,}$`."
        )

    u["cash"] -= bet

    # 4 đồng
    coins = [
        random.choice(
            ["🔴", "⚪"]
        )
        for _ in range(4)
    ]

    msg = await ctx.send(
        embed=game_embed(
            "🪙 XÓC ĐĨA BET88",
            (
                "🟠 **ĐANG XÓC...**\n\n"
                "`[ ❓ ] [ ❓ ] [ ❓ ] [ ❓ ]`\n\n"
                f"🎯 Cửa: **{choice.upper()}**\n"
                f"💰 Cược: `{bet:,}$`"
            ),
            COLOR_ORANGE
        )
    )

    await asyncio.sleep(0.8)

    await msg.edit(
        embed=game_embed(
            "🪙 XÓC ĐĨA BET88",
            (
                "🟠 **ĐANG XÓC...**\n\n"
                f"`[ {coins[0]} ] [ ❓ ] "
                f"[ ❓ ] [ ❓ ]`\n\n"
                f"🎯 Cửa: **{choice.upper()}**"
            ),
            COLOR_ORANGE
        )
    )

    await asyncio.sleep(0.5)

    await msg.edit(
        embed=game_embed(
            "🪙 XÓC ĐĨA BET88",
            (
                "🟠 **ĐANG XÓC...**\n\n"
                f"`[ {coins[0]} ] [ {coins[1]} ] "
                f"[ ❓ ] [ ❓ ]`\n\n"
                f"🎯 Cửa: **{choice.upper()}**"
            ),
            COLOR_ORANGE
        )
    )

    await asyncio.sleep(0.5)

    await msg.edit(
        embed=game_embed(
            "🪙 XÓC ĐĨA BET88",
            (
                "🟠 **ĐANG XÓC...**\n\n"
                f"`[ {coins[0]} ] [ {coins[1]} ] "
                f"[ {coins[2]} ] [ ❓ ]`\n\n"
                f"🎯 Cửa: **{choice.upper()}**"
            ),
            COLOR_ORANGE
        )
    )

    await asyncio.sleep(0.5)

    await msg.edit(
        embed=game_embed(
            "🪙 XÓC ĐĨA BET88",
            (
                "🟠 **ĐANG XÓC...**\n\n"
                f"`[ {coins[0]} ] [ {coins[1]} ] "
                f"[ {coins[2]} ] [ {coins[3]} ]`\n\n"
                f"🎯 Cửa: **{choice.upper()}**"
            ),
            COLOR_ORANGE
        )
    )

    await asyncio.sleep(0.5)

    reds = coins.count("🔴")

    is_chan = (
        reds in [2, 4]
    )

    result = (
        "chan"
        if is_chan
        else "le"
    )

    result_text = (
        "CHẴN"
        if is_chan
        else "LẺ"
)
    win = (
    (choice == "chan" and is_chan)
    or
    (choice == "le" and not is_chan)
)

if win:
    u["cash"] += bet * 2

    result_embed = game_embed(
        "🪙 XÓC ĐĨA BET88",
        (
            f"🔴🔴 **KẾT QUẢ**\n\n"
            f"[ {coins[0]} ] [ {coins[1]} ]\n"
            f"[ {coins[2]} ] [ {coins[3]} ]\n\n"
            f"🎯 Kết quả: **{result_text}**\n"
            f"🏆 Bạn **THẮNG**!\n"
            f"💰 Nhận: **+{bet * 2:,}$**"
        ),
        COLOR_GREEN
    )
else:
    result_embed = game_embed(
        "🪙 XÓC ĐĨA BET88",
        (
            f"🔴🔴 **KẾT QUẢ**\n\n"
            f"[ {coins[0]} ] [ {coins[1]} ]\n"
            f"[ {coins[2]} ] [ {coins[3]} ]\n\n"
            f"🎯 Kết quả: **{result_text}**\n"
            f"💸 Bạn **THUA**!\n"
            f"💰 Mất: **-{bet:,}$**"
        ),
        COLOR_RED
    )

    await msg.edit(embed=result_embed)


# KHỞI CHẠY BOT
bot.run(os.getenv("TOKEN_BOT"))
