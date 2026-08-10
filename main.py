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


# ================= GIAO DIỆN =================

BLUE = 0x3498DB
ORANGE = 0xF39C12
GREEN = 0x2ECC71
RED = 0xE74C3C


def embed(title, text, color=BLUE):
    return discord.Embed(
        title=title,
        description=text,
        color=color
    )


# ================= TIỆN ÍCH =================

def check_spam(user_id, cmd_name, limit_seconds=1.5):
    now = time.time()
    key = f"{user_id}_{cmd_name}"

    if key in cooldowns:
        diff = now - cooldowns[key]

        if diff < limit_seconds:
            return round(limit_seconds - diff, 1)

    cooldowns[key] = now
    return 0.0


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


# ================= BOT ONLINE =================

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="!trogiup | Casino Bet88")
    )

    print(f"✅ BOT ĐÃ SẴN SÀNG: {bot.user}")


# ================= TRỢ GIÚP =================

@bot.command(name="trogiup", aliases=["help"])
async def trogiup_cmd(ctx):

    cd = check_spam(
        ctx.author.id,
        "trogiup",
        1.5
    )

    if cd > 0:
        return await ctx.send(
            f"⚠️ {ctx.author.mention} Gõ từ từ thôi! "
            f"Đợi **{cd}** giây nữa!"
        )

    text = (
        "🎰 **CASINO BET88**\n\n"

        "⚔️ **ĐỐI KHÁNG (PVP)**\n"
        "`!danhbai`\n"
        "`!thachdau`\n"
        "`!dagapvp`\n"
        "`!tuxipvp @User`\n\n"

        "🎲 **CASINO**\n"
        "`!tx tai 100`\n"
        "`!tx xiu 100`\n"
        "`!daga`\n"
        "`!tuxi`\n"
        "`!bc cua 100`\n"
        "`!xd chan 100`\n"
        "`!bai`\n"
        "`!rl`\n"
        "`!quay 100`\n"
        "`!duangua`\n"
        "`!coinflip`\n\n"

        "💰 **TÀI KHOẢN**\n"
        "`!vi`\n"
        "`!gui`\n"
        "`!rut`\n"
        "`!chuyen`\n"
        "`!diemdanh`\n"
        "`!bxh`\n"
        "`!nhapcode`"
    )

    await ctx.send(
        embed=embed(
            "🎰 CASINO BET88",
            text,
            BLUE
        )
    )


# ================= ĐIỂM DANH =================

@bot.command(name="diemdanh")
async def diemdanh_cmd(ctx):

    cd = check_spam(
        ctx.author.id,
        "diemdanh",
        2.0
    )

    if cd > 0:
        return await ctx.send(
            f"⚠️ {ctx.author.mention} Gõ từ từ thôi! "
            f"Đợi **{cd}** giây nữa!"
        )

    user_id = ctx.author.id
    now = time.time()

    if (
        user_id in diemdanh_cooldowns
        and now - diemdanh_cooldowns[user_id] < 12 * 3600
    ):
        return await ctx.send(
            f"⚠️ {ctx.author.mention} "
            "Bạn đã điểm danh trong 12 giờ qua rồi!"
        )

    diemdanh_cooldowns[user_id] = now

    reward = 2593

    u = get_user(
        user_id,
        ctx.author.name
    )

    u["cash"] += reward

    await ctx.send(
        embed=embed(
            "🎁 ĐIỂM DANH THÀNH CÔNG",
            f"💰 Cộng vào ví: **+{reward:,}$**",
            GREEN
        )
    )


# ================= VÍ =================

@bot.command(name="vi", aliases=["money", "bal"])
async def vi_cmd(
    ctx,
    member: discord.Member = None
):

    target = member if member else ctx.author

    u = get_user(
        target.id,
        target.name
    )

    tag_id = target.id % 10000

    text = (
        f"👤 Chủ tài khoản: "
        f"**{target.name.upper()}_{tag_id:04d}**\n\n"

        f"💳 Hạng thẻ: **{u['hang']}**\n"
        f"🐓 Gà chiến: **{u['ga']}**\n\n"

        f"💵 Tiền mặt: **{u['cash']:,}$**\n"
        f"🏦 Két sắt: **{u['bank']:,}$**"
    )

    await ctx.send(
        embed=embed(
            "💳 THÔNG TIN TÀI KHOẢN",
            text,
            BLUE
        )
    )


# ================= SLOT =================

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
            f"⚠️ {ctx.author.mention} Gõ từ từ thôi! "
            f"Đợi **{cd}** giây nữa!"
        )

    if not bet or bet <= 0:
        return await ctx.send(
            "❌ Cú pháp: `!quay [tiền]`"
        )

    u = get_user(
        ctx.author.id,
        ctx.author.name
    )

    if u["cash"] < bet:
        return await ctx.send(
            f"❌ Bạn không đủ tiền mặt!\n"
            f"💵 Ví còn **{u['cash']:,}$**"
        )

    u["cash"] -= bet

    slots = [
        "🍋",
        "🔔",
        "🍒",
        "⭐",
        "💎"
    ]

    s1 = random.choice(slots)
    s2 = random.choice(slots)
    s3 = random.choice(slots)

    msg = await ctx.send(
        embed=embed(
            "🎰 MÁY SLOT BET88",
            "🟠 **ĐANG QUAY...**\n\n"
            f"`[ {s1} ] [ ❓ ] [ ❓ ]`",
            ORANGE
        )
    )

    await asyncio.sleep(0.6)

    await msg.edit(
        embed=embed(
            "🎰 MÁY SLOT BET88",
            "🟠 **ĐANG QUAY...**\n\n"
            f"`[ {s1} ] [ {s2} ] [ ❓ ]`",
            ORANGE
        )
    )

    await asyncio.sleep(0.6)

    if s1 == s2 == s3:

        reward = bet * 4

        u["cash"] += bet + reward

        text = (
            f"`[ {s1} ] [ {s2} ] [ {s3} ]`\n\n"
            "🟢 **NỔ HŨ THÀNH CÔNG!**\n"
            f"💰 Nhận **+{reward:,}$**"
        )

        color = GREEN

    else:

        text = (
            f"`[ {s1} ] [ {s2} ] [ {s3} ]`\n\n"
            "🔴 **TRẬT HŨ!**\n"
            f"💸 Mất **-{bet:,}$**"
        )

        color = RED

    await msg.edit(
        embed=embed(
            "🎰 MÁY SLOT BET88",
            text,
            color
        )
    )


# ================= TÀI XỈU =================

@bot.command(name="tx", aliases=["taixiu"])
async def taixiu_cmd(
    ctx,
    choice: str = None,
    bet: int = None
):

    global tx_session

    user_id = ctx.author.id

    u = get_user(
        user_id,
        ctx.author.name
    )

    # ---------- MỞ PHIÊN ----------

    if not choice:

        if tx_session["active"]:

            return await ctx.send(
                embed=embed(
                    "🎲 TÀI XỈU",
                    "🟠 **SÒNG ĐANG MỞ!**\n\n"
                    "Hãy dùng:\n"
                    "`!tx tai số_tiền`\n"
                    "`!tx xiu số_tiền`",
                    ORANGE
                )
            )

        tx_session["active"] = True
        tx_session["bets"] = {}
        tx_session["total_tai"] = 0
        tx_session["total_xiu"] = 0

        msg = await ctx.send(
            embed=embed(
                "🎲 SÒNG TÀI XỈU BET88",
                f"👤 Người mở bát: **{ctx.author.name}**\n\n"
                "🟠 **ĐANG NHẬN CƯỢC**\n\n"
                "⏱️ Thời gian: **30 giây**\n\n"
                "🎯 `!tx tai số_tiền`\n"
                "🎯 `!tx xiu số_tiền`",
                ORANGE
            )
        )

        tx_session["msg"] = msg

        for remaining in [20, 10]:

            await asyncio.sleep(10)

            if not tx_session["active"]:
                return

            try:

                await msg.edit(
                    embed=embed(
                        "🎲 SÒNG TÀI XỈU BET88",
                        "🟠 **ĐANG NHẬN CƯỢC**\n\n"
                        f"⏱️ Còn **{remaining} giây**\n\n"
                        f"💰 Tài: **{tx_session['total_tai']:,}$**\n"
                        f"💰 Xỉu: **{tx_session['total_xiu']:,}$**\n\n"
                        "🎯 `!tx tai số_tiền`\n"
                        "🎯 `!tx xiu số_tiền`",
                        ORANGE
                    )
                )

            except:
                pass

        await asyncio.sleep(10)

        if not tx_session["active"]:
            return

        tx_session["active"] = False

        try:

            await msg.edit(
                embed=embed(
                    "🎲 TÀI XỈU BET88",
                    "🟠 **NHÀ CÁI ĐANG XÓC BÁT...**\n\n"
                    "`[ ❓ ] [ ❓ ] [ ❓ ]`",
                    ORANGE
                )
            )

        except:
            pass

        await asyncio.sleep(2)

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

        for uid, data in tx_session["bets"].items():

            player = get_user(uid)

            amount = data["amount"]
            player_choice = data["choice"]
            player_name = data["name"]

            if player_choice == result:

                player["cash"] += amount * 2

                winners.append(
                    f"🟢 {player_name} "
                    f"**+{amount:,}$**"
                )

            else:

                losers.append(
                    f"🔴 {player_name} "
                    f"**-{amount:,}$**"
                )

        win_text = (
            "\n".join(winners)
            if winners
            else "Không có"
        )

        lose_text = (
            "\n".join(losers)
            if losers
            else "Không có"
        )

        final_text = (
            f"🎲 `[ {d1} ] [ {d2} ] [ {d3} ]`\n\n"
            f"🎯 Tổng điểm: **{total}**\n"
            f"🏆 Kết quả: **{result_text}**\n\n"

            "🟢 **THẮNG**\n"
            f"{win_text}\n\n"

            "🔴 **THUA**\n"
            f"{lose_text}"
        )

        try:

            await msg.edit(
                embed=embed(
                    "🎲 TÀI XỈU — KẾT QUẢ",
                    final_text,
                    GREEN if winners else RED
                )
            )

        except:

            await ctx.send(
                embed=embed(
                    "🎲 TÀI XỈU — KẾT QUẢ",
                    final_text,
                    GREEN if winners else RED
                )
            )

        tx_session["bets"] = {}

        return

    # ---------- ĐẶT CƯỢC ----------

    choice = choice.lower()

    if choice not in ["tai", "xiu"]:

        return await ctx.send(
            embed=embed(
                "🎲 TÀI XỈU",
                "❌ Cú pháp:\n\n"
                "`!tx tai 100`\n"
                "`!tx xiu 100`",
                RED
            )
        )

    if not tx_session["active"]:

        return await ctx.send(
            embed=embed(
                "🎲 TÀI XỈU",
                "🔴 **CHƯA CÓ PHIÊN!**\n\n"
                "Dùng `!tx` để mở phiên.",
                RED
            )
        )

    if not bet or bet <= 0:

        return await ctx.send(
            embed=embed(
                "🎲 TÀI XỈU",
                "🔴 Số tiền cược không hợp lệ!",
                RED
            )
        )

    if user_id in tx_session["bets"]:

        return await ctx.send(
            embed=embed(
                "🎲 TÀI XỈU",
                "🔴 **BẠN ĐÃ CƯỢC RỒI!**\n\n"
                "Mỗi người chỉ được cược 1 lần.",
                RED
            )
        )

    if u["cash"] < bet:

        return await ctx.send(
            embed=embed(
                "🎲 TÀI XỈU",
                f"🔴 Không đủ tiền!\n"
                f"💵 Ví còn **{u['cash']:,}$**",
                RED
            )
        )

    u["cash"] -= bet

    if choice == "tai":
        tx_session["total_tai"] += bet
    else:
        tx_session["total_xiu"] += bet

    tx_session["bets"][user_id] = {
        "name": ctx.author.name,
        "choice": choice,
        "amount": bet
    }

    await ctx.send(
        embed=embed(
            "🎯 ĐẶT CƯỢC THÀNH CÔNG",
            f"👤 {ctx.author.mention}\n\n"
            f"🎯 Cửa: **{choice.upper()}**\n"
            f"💰 Cược: **{bet:,}$**\n\n"
            "🟢 Đã tham gia phiên Tài Xỉu.",
            GREEN
        )
    )


# ================= XÓC ĐĨA =================

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
            f"⚠️ {ctx.author.mention} Gõ từ từ thôi! "
            f"Đợi **{cd}** giây nữa!"
        )

    if (
        not choice
        or choice.lower() not in ["chan", "le"]
        or not bet
        or bet <= 0
    ):

        return await ctx.send(
            embed=embed(
                "🪙 XÓC ĐĨA",
                "❌ Cú pháp:\n"
                "`!xd chan 100`\n"
                "`!xd le 100`",
                RED
            )
        )

    u = get_user(
        ctx.author.id,
        ctx.author.name
    )

    if u["cash"] < bet:

        return await ctx.send(
            embed=embed(
                "🪙 XÓC ĐĨA",
                f"🔴 Không đủ tiền!\n"
                f"💵 Ví còn **{u['cash']:,}$**",
                RED
            )
        )

    u["cash"] -= bet

    msg = await ctx.send(
        embed=embed(
            "🪙 XÓC ĐĨA BET88",
            "🟠 **ĐANG XÓC ĐĨA...**",
            ORANGE
        )
    )

    await asyncio.sleep(0.8)

    await msg.edit(
        embed=embed(
            "🪙 XÓC ĐĨA BET88",
            "🟠 **ĐANG LẮC...**",
            ORANGE
        )
    )

    await asyncio.sleep(0.8)

    reds = random.randint(0, 4)

    board = (
        "🔴" * reds
        + "⚪" * (4 - reds)
    )

    is_chan = reds % 2 == 0

    result_name = (
        "CHẴN"
        if is_chan
        else "LẺ"
    )

    win = (
        (
            choice.lower() == "chan"
            and is_chan
        )
        or (
            choice.lower() == "le"
            and not is_chan
        )
    )

    if win:

        u["cash"] += bet * 2

        text = (
            f"🪙 {board}\n\n"
            f"🎯 Kết quả: **{result_name}**\n"
            f"🔴 Số đỏ: **{reds}**\n\n"
            f"🟢 **THẮNG!**\n"
            f"💰 Nhận **+{bet:,}$**"
        )

        color = GREEN

    else:

        text = (
            f"🪙 {board}\n\n"
            f"🎯 Kết quả: **{result_name}**\n"
            f"🔴 Số đỏ: **{reds}**\n\n"
            f"🔴 **THUA!**\n"
            f"💸 Mất **-{bet:,}$**"
        )

        color = RED

    await msg.edit(
        embed=embed(
            "🪙 XÓC ĐĨA BET88",
            text,
            color
        )
    )


# ================= BẦU CUA =================

@bot.command(name="bc", aliases=["baucua"])
async def baucua_cmd(
    ctx,
    choice: str = None,
    bet: int = None
):

    cd = check_spam(
        ctx.author.id,
        "bc",
        1.5
    )

    if cd > 0:

        return await ctx.send(
            f"⚠️ {ctx.author.mention} Gõ từ từ thôi! "
            f"Đợi **{cd}** giây nữa!"
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
            embed=embed(
                "🎲 BẦU CUA",
                "❌ Cú pháp:\n"
                "`!bc ca 100`\n"
                "`!bc tom 100`\n"
                "`!bc cua 100`\n"
                "`!bc bau 100`\n"
                "`!bc ga 100`\n"
                "`!bc nai 100`",
                RED
            )
        )

    choice = choice.lower()

    u = get_user(
        ctx.author.id,
        ctx.author.name
    )

    if u["cash"] < bet:

        return await ctx.send(
            embed=embed(
                "🎲 BẦU CUA",
                f"🔴 Không đủ tiền!\n"
                f"💵 Ví còn **{u['cash']:,}$**",
                RED
            )
        )

    u["cash"] -= bet

    msg = await ctx.send(
        embed=embed(
            "🎲 BẦU CUA BET88",
            "🟠 **ĐANG LẮC HỘT...**\n\n"
            "`[ ❓ ] [ ❓ ] [ ❓ ]`",
            ORANGE
        )
    )

    await asyncio.sleep(0.7)

    keys = list(animals.keys())

    d1 = random.choice(keys)
    d2 = random.choice(keys)
    d3 = random.choice(keys)

    matches = [
        d1,
        d2,
        d3
    ].count(choice)

    result = (
        f"`[ {animals[d1]} ] "
        f"[ {animals[d2]} ] "
        f"[ {animals[d3]} ]`"
    )

    if matches > 0:

        reward = bet * matches

        u["cash"] += bet + reward

        text = (
            f"{result}\n\n"
            f"🟢 **TRÚNG {matches} CON!**\n"
            f"💰 Nhận **+{reward:,}$**"
        )

        color = GREEN

    else:

        text = (
            f"{result}\n\n"
            "🔴 **THUA!**\n"
            f"💸 Mất **-{bet:,}$**"
        )

        color = RED

    await msg.edit(
        embed=embed(
            "🎲 BẦU CUA BET88",
            text,
            color
        )
    )


# ================= CHẠY BOT =================

token = os.getenv("TOKEN_BOT")

if not token:
    print("❌ KHÔNG TÌM THẤY TOKEN_BOT!")
else:
    bot.run(token)
