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

@bot.event
async def on_ready():
    print(f"✅ BOT ĐÃ SẴN SÀNG HOẠT ĐỘNG: {bot.user}")

@bot.command(name="diemdanh")
async def diemdanh_cmd(ctx):
    cd = check_spam(ctx.author.id, "diemdanh", 2.0)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi! Đợi **{cd}** giây nữa!")

    user_id = ctx.author.id
    now = time.time()
    if user_id in diemdanh_cooldowns and now - diemdanh_cooldowns[user_id] < 12 * 3600:
        return await ctx.send(f"⚠️ {ctx.author.mention} Bạn đã điểm danh trong 12 giờ qua rồi!")

    diemdanh_cooldowns[user_id] = now
    reward = 2593
    u = get_user(user_id, ctx.author.name)
    u["cash"] += reward
    await ctx.send(f"🎁 {ctx.author.mention} Điểm danh! `+{reward:,}$`")

@bot.command(name="vi", aliases=["money", "bal"])
async def vi_cmd(ctx, member: discord.Member = None):
    target = member if member else ctx.author
    u = get_user(target.id, target.name)
    tag_id = target.id % 10000
    
    res = (
        f"┌─────────────────────────┐\n"
        f"💳 **TÀI KHOẢN: {target.name.upper()}_{tag_id:04d}**\n"
        f"Hạng thẻ\n👤 {u['hang']}\n"
        f"Gà chiến\n{u['ga']}\n"
        f"💵 Tiền mặt\n`{u['cash']:,}$`\n"
        f"🏦 Két sắt\n`{u['bank']:,}$`\n"
        f"└─────────────────────────┘"
    )
    await ctx.send(res)

# --- LỆNH QUAY SLOT (!quay) - HIỆN TỪNG Ô MỘT ---
@bot.command(name="quay")
async def quay_cmd(ctx, bet: int = None):
    cd = check_spam(ctx.author.id, "quay", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi! Đợi **{cd}** giây nữa!")

    if not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!quay [tiền]` (Ví dụ: `!quay 100`)")

    u = get_user(ctx.author.id, ctx.author.name)
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt! Ví chỉ còn `{u['cash']:,}$`.")

    u["cash"] -= bet
    slots = ["🍋", "🔔", "🍒", "⭐", "💎"]
    
    s1 = random.choice(slots)
    s2 = random.choice(slots)
    s3 = random.choice(slots)

    # Bước 1: Hiện ô đầu tiên
    msg = await ctx.send(
        f"┌─────────────────────────┐\n"
        f"🎰 **MÁY SLOT BET88**\n"
        f"Máy đang quay...\n"
        f"`[ {s1} ] [ ? ] [ ? ]`\n"
        f"└─────────────────────────┘"
    )
    await asyncio.sleep(0.6)

    # Bước 2: Hiện tiếp ô thứ 2
    await msg.edit(content=
        f"┌─────────────────────────┐\n"
        f"🎰 **MÁY SLOT BET88**\n"
        f"Máy đang quay...\n"
        f"`[ {s1} ] [ {s2} ] [ ? ]`\n"
        f"└─────────────────────────┘"
    )
    await asyncio.sleep(0.6)

    # Bước 3: Hiện nốt ô thứ 3 và kết quả
    win = (s1 == s2 == s3)
    if win:
        reward = bet * 4
        u["cash"] += bet + reward
        res = (
            f"┌─────────────────────────┐\n"
            f"🎰 **MÁY SLOT BET88**\n"
            f"KẾT QUẢ\n"
            f"`[ {s1} ] [ {s2} ] [ {s3} ]`\n"
            f"Thông báo\n"
            f"✨ **NỔ HŨ!** Nhận `+{reward:,}$`\n"
            f"└─────────────────────────┘"
        )
    else:
        res = (
            f"┌─────────────────────────┐\n"
            f"🎰 **MÁY SLOT BET88**\n"
            f"KẾT QUẢ\n"
            f"`[ {s1} ] [ {s2} ] [ {s3} ]`\n"
            f"Thông báo\n"
            f"💸 **TRẬT HỦ (MẤT TRẮNG)!** `-{bet:,}$`\n"
            f"└─────────────────────────┘"
        )

    await msg.edit(content=res)

# --- LỆNH TÀI XỈU (!tx) ---
@bot.command(name="tx", aliases=["taixiu"])
async def taixiu_cmd(ctx, choice: str = None, bet: int = None):
    global tx_session
    user_id = ctx.author.id
    u = get_user(user_id, ctx.author.name)

    if not choice:
        if tx_session["active"]:
            return await ctx.send("⚠️ Sòng Tài Xỉu đang mở phiên rồi! Hãy nhanh tay đặt cược.")

        tx_session["active"] = True
        tx_session["bets"] = {}
        tx_session["total_tai"] = 0
        tx_session["total_xiu"] = 0

        msg = await ctx.send(
            f"┌─────────────────────────┐\n"
            f"🔴 **SÒNG TÀI XỈU BET88** 🔴\n"
            f"**{ctx.author.name}** đã mở bát!\n"
            f"Gõ `!tx <tai/xiu> <tiền>` để theo!\n"
            f"(Cược Max: 10,000,000$/ván)\n"
            f"⏱️ Thời gian: **30 giây**\n"
            f"└─────────────────────────┘"
        )
        tx_session["msg"] = msg

        for remaining in [20, 10]:
            await asyncio.sleep(10)
            if not tx_session["active"]: return
            try:
                await msg.edit(content=
                    f"┌─────────────────────────┐\n"
                    f"🔴 **SÒNG TÀI XỈU BET88** 🔴\n"
                    f"Gõ `!tx <tai/xiu> <tiền>` để theo!\n"
                    f"(Cược Max: 10,000,000$/ván)\n"
                    f"⏱️ Thời gian: **{remaining} giây**\n"
                    f"💰 Tổng Tài: `{tx_session['total_tai']:,}$` | Tổng Xỉu: `{tx_session['total_xiu']:,}$`\n"
                    f"└─────────────────────────┘"
                )
            except: pass

        await asyncio.sleep(10)
        if not tx_session["active"]: return

        tx_session["active"] = False
        try:
            await msg.edit(content=
                f"┌─────────────────────────┐\n"
                f"🎲 **NHÀ CÁI BET88 ĐANG XÓC BÁT...**\n"
                f"💰 Tài: `{tx_session['total_tai']:,}$` | `[ ? ]` `[ ? ]` `[ ? ]`\n"
                f"└─────────────────────────┘"
            )
        except: pass

        await asyncio.sleep(2.0)

        d1, d2, d3 = random.randint(1,6), random.randint(1,6), random.randint(1,6)
        total = d1 + d2 + d3
        kq = "tai" if total >= 11 else "xiu"
        kq_text = "TÀI" if kq == "tai" else "XỈU"

        thang_list, thua_list = [], []
        for uid, data in tx_session["bets"].items():
            p_u = get_user(uid)
            p_bet = data["amount"]
            p_choice = data["choice"]
            p_name = data["name"]

            if p_choice == kq:
                p_u["cash"] += p_bet * 2
                thang_list.append(f"• {p_name}: +`{p_bet:,}$`")
            else:
                thua_list.append(f"• {p_name}: -`{p_bet:,}$`")

        thang_str = "\n".join(thang_list) if thang_list else "Không có"
        thua_str = "\n".join(thua_list) if thua_list else "Không có"

        final_res = (
            f"┌─────────────────────────┐\n"
            f"🟢 **MỞ BÁT BET88**\n"
            f"Kết Quả\n"
            f"`[ {d1} ]` - `[ {d2} ]` - `[ {d3} ]`\n\n"
            f"➔ **{total} ĐIỂM ({kq_text})**\n"
            f"✨ **THẮNG**\n{thang_str}\n\n"
            f"💸 **THUA**\n{thua_str}\n"
            f"└─────────────────────────┘"
        )
        try:
            await msg.edit(content=final_res)
        except:
            await ctx.send(final_res)
        return

    choice = choice.lower()
    if choice not in ["tai", "xiu"]:
        return await ctx.send("❌ Cú pháp: `!tx [tai/xiu] [tiền]`")

    if not tx_session["active"]:
        return await ctx.send("❌ Hiện tại chưa có phiên Tài Xỉu nào! Hãy gõ `!tx` để mở phiên.")

    if not bet or bet <= 0:
        return await ctx.send("❌ Số tiền cược không hợp lệ!")

    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt! Ví chỉ còn `{u['cash']:,}$`.")

    u["cash"] -= bet
    if choice == "tai":
        tx_session["total_tai"] += bet
    else:
        tx_session["total_xiu"] += bet

    tx_session["bets"][user_id] = {"name": ctx.author.name, "choice": choice, "amount": bet}
    await ctx.send(f"✅ {ctx.author.mention} Đã đặt thành công `{bet:,}$` vào cửa **{choice.upper()}**!")

# --- LỆNH XÓC ĐĨA (!xd) ---
@bot.command(name="xd", aliases=["xocdia"])
async def xocdia_cmd(ctx, choice: str = None, bet: int = None):
    cd = check_spam(ctx.author.id, "xd", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi! Đợi **{cd}** giây nữa!")

    if not choice or choice.lower() not in ["chan", "le"] or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!xd [chan/le] [tiền]`")

    u = get_user(ctx.author.id, ctx.author.name)
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền! Ví còn `{u['cash']:,}$`.")

    u["cash"] -= bet
    msg = await ctx.send(
        f"┌─────────────────────────┐\n"
        f"🪙 **XÓC ĐĨA BET88**\n"
        f"4 Đồng xu\n"
        f"*Xóc... xóc... xóc...*\n"
        f"└─────────────────────────┘"
    )
    await asyncio.sleep(0.8)
    
    await msg.edit(content=
        f"┌─────────────────────────┐\n"
        f"🪙 **XÓC ĐĨA BET88**\n"
        f"4 Đồng xu\n"
        f"*Đặt bát xuống bàn...*\n"
        f"└─────────────────────────┘"
    )
    await asyncio.sleep(0.8)
    
    reds = random.randint(0, 4)
    board = "🔴" * reds + "⚪" * (4 - reds)
    is_chan = (reds % 2 == 0)
    kq_name = "CHẴN" if is_chan else "LẺ"
    win = ((choice.lower() == "chan" and is_chan) or (choice.lower() == "le" and not is_chan))

    if win:
        u["cash"] += bet * 2
        res = (
            f"┌─────────────────────────┐\n"
            f"🪙 **XÓC ĐĨA BET88**\n"
            f"4 Đồng xu\n"
            f"{board}\n"
            f"Kết quả\n"
            f"➔ **{kq_name} ({reds} Đỏ)**\n"
            f"✨ **THẮNG!** Nhận `+{bet:,}$`\n"
            f"└─────────────────────────┘"
        )
    else:
        res = (
            f"┌─────────────────────────┐\n"
            f"🪙 **XÓC ĐĨA BET88**\n"
            f"4 Đồng xu\n"
            f"{board}\n"
            f"Kết quả\n"
            f"➔ **{kq_name} ({reds} Đỏ)**\n"
            f"💸 **CÁI ĂN SẠCH!** `-{bet:,}$`\n"
            f"└─────────────────────────┘"
        )
    await msg.edit(content=res)

# --- LỆNH BẦU CUA (!bc) - HIỆN "TỪ TỪ HÉ BÁT..." ---
@bot.command(name="bc", aliases=["baucua"])
async def baucua_cmd(ctx, choice: str = None, bet: int = None):
    cd = check_spam(ctx.author.id, "bc", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi! Đợi **{cd}** giây nữa!")

    animals = {"ca": "🐟", "tom": "🦐", "cua": "🦀", "bau": "🥒", "ga": "🐓", "nai": "🦌"}
    if not choice or choice.lower() not in animals or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!bc [ca/tom/cua/bau/ga/nai] [tiền]`")

    u = get_user(ctx.author.id, ctx.author.name)
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền! Ví còn `{u['cash']:,}$`.")

    u["cash"] -= bet
    
    msg = await ctx.send(
        f"┌─────────────────────────┐\n"
        f"🎲 **BẦU CUA BET88**\n"
        f"Trạng thái\n"
        f"`[ ? ] [ ? ] [ ? ]`\n"
        f"└─────────────────────────┘"
    )
    await asyncio.sleep(0.7)

    await msg.edit(content=
        f"┌─────────────────────────┐\n"
        f"🎲 **BẦU CUA BET88**\n"
        f"Trạng thái\n"
        f"Từ từ hé bát...\n"
        f"└─────────────────────────┘"
    )
    await asyncio.sleep(0.8)

    keys = list(animals.keys())
    d1, d2, d3 = random.choice(keys), random.choice(keys), random.choice(keys)
    matches = [d1, d2, d3].count(choice.lower())

    if matches > 0:
        reward = bet * matches
        u["cash"] += bet + reward
        res = (
            f"┌─────────────────────────┐\n"
            f"🎲 **BẦU CUA BET88**\n"
            f"MỞ BÁT\n"
            f"`[ {animals[d1]} ] [ {animals[d2]} ] [ {animals[d3]} ]`\n"
            f"Tổng kết\n"
            f"✨ **TRÚNG {matches} CON!** `+{reward:,}$`\n"
            f"└─────────────────────────┘"
        )
    else:
        res = (
            f"┌─────────────────────────┐\n"
            f"🎲 **BẦU CUA BET88**\n"
            f"MỞ BÁT\n"
            f"`[ {animals[d1]} ] [ {animals[d2]} ] [ {animals[d3]} ]`\n"
            f"Tổng kết\n"
            f"💸 **MẤT SẠCH!** `-{bet:,}$`\n"
            f"└─────────────────────────┘"
        )
    await msg.edit(content=res)

# Sử dụng TOKEN_BOT đúng theo yêu cầu của bạn
token = os.getenv("TOKEN_BOT")
bot.run(token)
    
