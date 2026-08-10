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


def line():
    return "━━━━━━━━━━━━━━━━━━"


# ================= BOT ONLINE =================

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="!trogiup | Casino Bet88")
    )

    print(f"✅ BOT ĐÃ SẴN SÀNG HOẠT ĐỘNG: {bot.user}")


# ================= TRỢ GIÚP =================

@bot.command(name="trogiup", aliases=["help"])
async def trogiup_cmd(ctx):

    cd = check_spam(ctx.author.id, "trogiup", 1.5)

    if cd > 0:
        return await ctx.send(
            f"⚠️ {ctx.author.mention} Gõ từ từ thôi! "
            f"Đợi **{cd}** giây nữa!"
        )

    menu_text = (
        "🎰 **CASINO BET88**\n"
        f"{line()}\n\n"

        "🎲 **CASINO**\n"
        "`!tx tai 100` • `!tx xiu 100`\n"
        "`!bc cua 100` • `!bc tom 100`\n"
        "`!xd chan 100` • `!xd le 100`\n"
        "`!quay 100`\n\n"

        "💰 **TÀI KHOẢN**\n"
        "`!vi` • `!gui 100` • `!rut 100`\n"
        "`!chuyen @user 100`\n"
        "`!diemdanh` • `!bxh`\n\n"

        "🛒 **CỬA HÀNG**\n"
        "`!cuahang` • `!muan vip`\n"
        "`!muan daigia` • `!muan typhu`\n\n"

        "🎟️ **CODE**\n"
        "`!nhapcode CODE`\n\n"

        "🛡️ **ADMIN**\n"
        "`!taocode tiền lượt`\n"
        "`!settien @user số_tiền`\n"
        "`!kick @user` • `!ban @user`\n"
        "`!khoamom @user` • `!reset tien @user`\n\n"

        f"{line()}\n"
        "💡 Dùng đúng cú pháp để tránh lỗi."
    )

    await ctx.send(menu_text)


# ================= ĐIỂM DANH =================

@bot.command(name="diemdanh")
async def diemdanh_cmd(ctx):

    cd = check_spam(ctx.author.id, "diemdanh", 2.0)

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
        f"🎁 **ĐIỂM DANH THÀNH CÔNG**\n"
        f"{line()}\n"
        f"👤 Người nhận: {ctx.author.mention}\n"
        f"💰 Phần thưởng: `+{reward:,}$`\n"
        f"{line()}"
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

    res = (
        "💳 **THÔNG TIN TÀI KHOẢN**\n"
        f"{line()}\n"
        f"👤 Chủ tài khoản: "
        f"**{target.name.upper()}_{tag_id:04d}**\n"
        f"🏅 Hạng thẻ: **{u['hang']}**\n"
        f"🐓 Gà chiến: **{u['ga']}**\n"
        f"💵 Tiền mặt: `{u['cash']:,}$`\n"
        f"🏦 Két sắt: `{u['bank']:,}$`\n"
        f"{line()}"
    )

    await ctx.send(res)


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
            "❌ Cú pháp: `!quay [tiền]`\n"
            "Ví dụ: `!quay 100`"
        )

    u = get_user(
        ctx.author.id,
        ctx.author.name
    )

    if u["cash"] < bet:
        return await ctx.send(
            f"❌ Bạn không đủ tiền mặt!\n"
            f"💵 Ví còn `{u['cash']:,}$`."
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
        "🎰 **MÁY SLOT BET88**\n"
        f"{line()}\n"
        "🟠 Trạng thái: **Đang quay...**\n\n"
        f"`[ {s1} ] [ ❓ ] [ ❓ ]`\n"
        f"{line()}"
    )

    await asyncio.sleep(0.6)

    await msg.edit(
        content=(
            "🎰 **MÁY SLOT BET88**\n"
            f"{line()}\n"
            "🟠 Trạng thái: **Đang quay...**\n\n"
            f"`[ {s1} ] [ {s2} ] [ ❓ ]`\n"
            f"{line()}"
        )
    )

    await asyncio.sleep(0.6)

    win = (
        s1 == s2 == s3
    )

    if win:

        reward = bet * 4

        u["cash"] += bet + reward

        res = (
            "🎰 **MÁY SLOT BET88**\n"
            f"{line()}\n"
            f"🟢 KẾT QUẢ: "
            f"`[ {s1} ] [ {s2} ] [ {s3} ]`\n\n"
            "✨ **NỔ HŨ THÀNH CÔNG!**\n"
            f"💰 Nhận `+{reward:,}$`\n"
            f"{line()}"
        )

    else:

        res = (
            "🎰 **MÁY SLOT BET88**\n"
            f"{line()}\n"
            f"🔴 KẾT QUẢ: "
            f"`[ {s1} ] [ {s2} ] [ {s3} ]`\n\n"
            "💸 **TRẬT HỦ - MẤT TRẮNG!**\n"
            f"💰 `-{bet:,}$`\n"
            f"{line()}"
        )

    await msg.edit(
        content=res
    )


# ================= TÀI XỈU =================

@bot.command(
    name="tx",
    aliases=["taixiu"]
)
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

    # ===== MỞ PHIÊN =====

    if not choice:

        if tx_session["active"]:

            return await ctx.send(
                "⚠️ **SÒNG TÀI XỈU ĐANG MỞ!**\n"
                f"{line()}\n"
                "Hãy nhanh tay đặt cược."
            )

        tx_session["active"] = True
        tx_session["bets"] = {}
        tx_session["total_tai"] = 0
        tx_session["total_xiu"] = 0

        msg = await ctx.send(
            "🎲 **SÒNG TÀI XỈU BET88**\n"
            f"{line()}\n"
            f"👤 Người mở bát: **{ctx.author.name}**\n\n"
            "📝 Cú pháp:\n"
            "`!tx tai số_tiền`\n"
            "`!tx xiu số_tiền`\n\n"
            "⏱️ Thời gian đặt cược: **30 giây**\n"
            f"{line()}"
        )

        tx_session["msg"] = msg

        # ===== ĐẾM NGƯỢC =====

        for remaining in [20, 10]:

            await asyncio.sleep(10)

            if not tx_session["active"]:
                return

            try:

                await msg.edit(
                    content=(
                        "🎲 **SÒNG TÀI XỈU BET88**\n"
                        f"{line()}\n"
                        f"⏱️ Còn lại: **{remaining} giây**\n\n"
                        f"💰 Tổng Tài: "
                        f"`{tx_session['total_tai']:,}$`\n"
                        f"💰 Tổng Xỉu: "
                        f"`{tx_session['total_xiu']:,}$`\n\n"
                        "🎯 `!tx tai số_tiền`\n"
                        "🎯 `!tx xiu số_tiền`\n"
                        f"{line()}"
                    )
                )

            except Exception:
                pass

        await asyncio.sleep(10)

        if not tx_session["active"]:
            return

        tx_session["active"] = False

        try:

            await msg.edit(
                content=(
                    "🎲 **NHÀ CÁI ĐANG XÓC BÁT...**\n"
                    f"{line()}\n\n"
                    "🎲 `[ ? ]` `[ ? ]` `[ ? ]`\n\n"
                    f"{line()}"
                )
            )

        except Exception:
            pass

        await asyncio.sleep(2.0)

        # ===== XÚC XẮC =====

        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        d3 = random.randint(1, 6)

        total = d1 + d2 + d3

        kq = (
            "tai"
            if total >= 11
            else "xiu"
        )

        kq_text = (
            "TÀI"
            if kq == "tai"
            else "XỈU"
        )

        thang_list = []
        thua_list = []

        for uid, data in tx_session["bets"].items():

            p_u = get_user(uid)

            p_bet = data["amount"]
            p_choice = data["choice"]
            p_name = data["name"]

            if p_choice == kq:

                p_u["cash"] += p_bet * 2

                thang_list.append(
                    f"🟢 {p_name}: "
                    f"+`{p_bet:,}$`"
                )

            else:

                thua_list.append(
                    f"🔴 {p_name}: "
                    f"-`{p_bet:,}$`"
                )

        thang_str = (
            "\n".join(thang_list)
            if thang_list
            else "Không có"
        )

        thua_str = (
            "\n".join(thua_list)
            if thua_list
            else "Không có"
        )

        final_res = (
            "🎲 **KẾT QUẢ TÀI XỈU**\n"
            f"{line()}\n"
            f"🎲 Xúc xắc: "
            f"`[ {d1} ] [ {d2} ] [ {d3} ]`\n"
            f"🎯 Tổng điểm: **{total}**\n"
            f"🏆 Kết quả: **{kq_text}**\n\n"

            "🟢 **THẮNG**\n"
            f"{thang_str}\n\n"

            "🔴 **THUA**\n"
            f"{thua_str}\n"
            f"{line()}"
        )

        try:

            await msg.edit(
                content=final_res
            )

        except Exception:

            await ctx.send(
                final_res
            )

        tx_session["bets"] = {}

        return

    # ===== ĐẶT CƯỢC =====

    choice = choice.lower()

    if choice not in ["tai", "xiu"]:

        return await ctx.send(
            "❌ Cú pháp:\n"
            "`!tx tai số_tiền`\n"
            "`!tx xiu số_tiền`"
        )

    if not tx_session["active"]:

        return await ctx.send(
            "❌ Hiện tại chưa có phiên "
            "Tài Xỉu nào!\n"
            "Gõ `!tx` để mở phiên."
        )

    if not bet or bet <= 0:

        return await ctx.send(
            "❌ Số tiền cược không hợp lệ!"
        )

    if user_id in tx_session["bets"]:

        return await ctx.send(
            "❌ Bạn đã cược trong phiên này rồi!"
        )

    if u["cash"] < bet:

        return await ctx.send(
            f"❌ Bạn không đủ tiền mặt!\n"
            f"💵 Ví còn `{u['cash']:,}$`."
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
        "🎯 **ĐẶT CƯỢC THÀNH CÔNG**\n"
        f"{line()}\n"
        f"👤 {ctx.author.mention}\n"
        f"🎯 Cửa: **{choice.upper()}**\n"
        f"💰 Tiền cược: `{bet:,}$`\n"
        f"{line()}"
    )


# ================= XÓC ĐĨA =================

@bot.command(
    name="xd",
    aliases=["xocdia"]
)
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
            "❌ Cú pháp:\n"
            "`!xd chan 100`\n"
            "`!xd le 100`"
        )

    u = get_user(
        ctx.author.id,
        ctx.author.name
    )

    if u["cash"] < bet:

        return await ctx.send(
            f"❌ Bạn không đủ tiền!\n"
            f"💵 Ví còn `{u['cash']:,}$`."
        )

    u["cash"] -= bet

    msg = await ctx.send(
        "🪙 **XÓC ĐĨA BET88**\n"
        f"{line()}\n"
        "🟠 Trạng thái: **Đang xóc đĩa...**\n"
        f"{line()}"
    )

    await asyncio.sleep(0.8)

    await msg.edit(
        content=(
            "🪙 **XÓC ĐĨA BET88**\n"
            f"{line()}\n"
            "🟠 Đặt bát xuống bàn...\n"
            f"{line()}"
        )
    )

    await asyncio.sleep(0.8)

    reds = random.randint(
        0,
        4
    )

    board = (
        "🔴" * reds
        + "⚪" * (4 - reds)
    )

    is_chan = (
        reds % 2 == 0
    )

    kq_name = (
        "CHẴN"
        if is_chan
        else "LẺ"
    )

    win = (
        (
            choice.lower() == "chan"
            and is_chan
        )
        or
        (
            choice.lower() == "le"
            and not is_chan
        )
    )

    if win:

        u["cash"] += bet * 2

        res = (
            "🪙 **XÓC ĐĨA BET88**\n"
            f"{line()}\n"
            f"🔴 Mặt đĩa: {board}\n"
            f"🎯 Kết quả: **{kq_name}**\n"
            f"🔴 Số đỏ: **{reds}**\n\n"
            f"🟢 **THẮNG!** "
            f"Nhận `+{bet:,}$`\n"
            f"{line()}"
        )

    else:

        res = (
            "🪙 **XÓC ĐĨA BET88**\n"
            f"{line()}\n"
            f"🔴 Mặt đĩa: {board}\n"
            f"🎯 Kết quả: **{kq_name}**\n"
            f"🔴 Số đỏ: **{reds}**\n\n"
            f"🔴 **THUA SẠCH!** "
            f"`-{bet:,}$`\n"
            f"{line()}"
        )

    await msg.edit(
        content=res
    )


# ================= BẦU CUA =================

@bot.command(
    name="bc",
    aliases=["baucua"]
)
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
            "❌ Cú pháp:\n"
            "`!bc ca 100`\n"
            "`!bc tom 100`\n"
            "`!bc cua 100`\n"
            "`!bc bau 100`\n"
            "`!bc ga 100`\n"
            "`!bc nai 100`"
        )

    choice = choice.lower()

    u = get_user(
        ctx.author.id,
        ctx.author.name
    )

    if u["cash"] < bet:

        return await ctx.send(
            f"❌ Bạn không đủ tiền!\n"
            f"💵 Ví còn `{u['cash']:,}$`."
        )

    u["cash"] -= bet

    msg = await ctx.send(
        "🎲 **BẦU CUA BET88**\n"
        f"{line()}\n"
        "🟠 Trạng thái: **Đang lắc hột...**\n"
        f"{line()}"
    )

    await asyncio.sleep(0.7)

    keys = list(
        animals.keys()
    )

    d1 = random.choice(keys)
    d2 = random.choice(keys)
    d3 = random.choice(keys)

    matches = [
        d1,
        d2,
        d3
    ].count(choice)

    if matches > 0:

        reward = bet * matches

        u["cash"] += bet + reward

        res = (
            "🎲 **BẦU CUA BET88**\n"
            f"{line()}\n"
            f"🎲 Kết quả: "
            f"`[ {animals[d1]} ] "
            f"[ {animals[d2]} ] "
            f"[ {animals[d3]} ]`\n\n"
            f"🟢 **TRÚNG {matches} CON!**\n"
            f"💰 Nhận `+{reward:,}$`\n"
            f"{line()}"
        )

    else:

        res = (
            "🎲 **BẦU CUA BET88**\n"
            f"{line()}\n"
            f"🎲 Kết quả: "
            f"`[ {animals[d1]} ] "
            f"[ {animals[d2]} ] "
            f"[ {animals[d3]} ]`\n\n"
            "🔴 **MẤT SẠCH!**\n"
            f"💸 `-{bet:,}$`\n"
            f"{line()}"
        )

    await msg.edit(
        content=res
    )


# ================= CHẠY BOT =================

token = os.getenv("TOKEN_BOT")

if not token:
    print("❌ Không tìm thấy TOKEN_BOT!")
else:
    bot.run(token)
