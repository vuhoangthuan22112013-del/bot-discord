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

# Biến quản lý phiên Tài Xỉu chung
tx_session = {
    "active": False,
    "msg": None,
    "bets": {}, # {user_id: {"name": str, "choice": str, "amount": int}}
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

# --- LỆNH ĐIỂM DANH ---
@bot.command(name="diemdanh")
async def diemdanh_cmd(ctx):
    cd = check_spam(ctx.author.id, "diemdanh", 2.0)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Từ từ thôi! Đợi **{cd}**s nữa!")

    user_id = ctx.author.id
    now = time.time()
    if user_id in diemdanh_cooldowns and now - diemdanh_cooldowns[user_id] < 12 * 3600:
        return await ctx.send(f"⚠️ {ctx.author.mention} Bạn đã điểm danh trong 12 giờ qua rồi!")

    diemdanh_cooldowns[user_id] = now
    reward = random.randint(1000, 3000)
    u = get_user(user_id, ctx.author.name)
    u["cash"] += reward
    await ctx.send(f"🎁 {ctx.author.mention} Điểm danh thành công! Nhận `+{reward:,}$`")

# --- LỆNH !VI ---
@bot.command(name="vi", aliases=["money", "bal"])
async def vi_cmd(ctx, member: discord.Member = None):
    cd = check_spam(ctx.author.id, "vi", 1.0)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Từ từ thôi! Đợi **{cd}**s!")

    target = member if member else ctx.author
    u = get_user(target.id, target.name)
    tag_id = target.id % 10000
    
    res = (
        f"💳 **TÀI KHOẢN: {target.name.upper()}_{tag_id:04d}**\n"
        f"Hạng thẻ\n👤 {u['hang']}\n"
        f"Gà chiến\n{u['ga']}\n"
        f"💵 Tiền mặt\n`{u['cash']:,}$`\n"
        f"🏦 Két sắt\n`{u['bank']:,}$`"
    )
    await ctx.send(res)

# --- LỆNH QUAY SLOT (!quay) - HIỆU ỨNG TỪ TỪ Y HỆT VIDEO ---
@bot.command(name="quay")
async def quay_cmd(ctx, bet: int = None):
    cd = check_spam(ctx.author.id, "quay", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Đợi **{cd}**s nữa!")

    if not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!quay [tiền]` (Ví dụ: `!quay 100`)")

    u = get_user(ctx.author.id, ctx.author.name)
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt! Ví chỉ còn `{u['cash']:,}$`.")

    u["cash"] -= bet
    slots = ["🍋", "🔔", "🍒", "⭐", "💎"]
    
    # Bước 1: Hiển thị trạng thái đang quay
    msg = await ctx.send(
        f"🎰 **MÁY SLOT BET88**\n"
        f"Máy đang quay...\n"
        f"`[ {random.choice(slots)} ] [ {random.choice(slots)} ] [ {random.choice(slots)} ]`"
    )
    await asyncio.sleep(0.8)

    # Bước 2: Ra kết quả cuối cùng
    s1, s2, s3 = random.choice(slots), random.choice(slots), random.choice(slots)
    win = (s1 == s2 == s3)

    if win:
        reward = bet * 4
        u["cash"] += bet + reward
        res = (
            f"🎰 **MÁY SLOT BET88**\n"
            f"KẾT QUẢ\n"
            f"`[ {s1} ] [ {s2} ] [ {s3} ]`\n"
            f"Thông báo\n"
            f"✨ **NỔ HŨ!** Nhận `+{reward:,}$`"
        )
    else:
        res = (
            f"🎰 **MÁY SLOT BET88**\n"
            f"KẾT QUẢ\n"
            f"`[ {s1} ] [ {s2} ] [ {s3} ]`\n"
            f"Thông báo\n"
            f"💸 **TRẬT HỦ (MẤT TRẮNG)!** `-{bet:,}$`"
        )

    await msg.edit(content=res)

# --- LỆNH TÀI XỈU (!tx) - ĐỢI 30 GIÂY VÀ CHUẨN GIAO DIỆN VIDEO ---
@bot.command(name="tx", aliases=["taixiu"])
async def taixiu_cmd(ctx, choice: str = None, bet: int = None):
    global tx_session
    user_id = ctx.author.id
    u = get_user(user_id, ctx.author.name)

    # Nếu người chơi gõ lệnh !tx đơn thuần để mở phiên mới
    if not choice:
        if tx_session["active"]:
            return await ctx.send("⚠️ Sông Tài Xỉu đang mở phiên rồi! Hãy nhanh tay đặt cược.")

        tx_session["active"] = True
        tx_session["bets"] = {}
        tx_session["total_tai"] = 0
        tx_session["total_xiu"] = 0

        msg = await ctx.send(
            f"🔴 **SÒNG TÀI XỈU BET88** 🔴\n"
            f"**{ctx.author.name}** đã mở bát!\n"
            f"Gõ `!tx <tai/xiu> <tiền>` để theo! (Tối đa 10,000,000$/ván)\n\n"
            f"⏱️ Thời gian: **30 giây**"
        )
        tx_session["msg"] = msg

        # Đếm ngược từ 30 về 0 (cập nhật mô phỏng thời gian giống video)
        for remaining in [20, 10]:
            await asyncio.sleep(10)
            if not tx_session["active"]: return
            try:
                await msg.edit(content=
                    f"🔴 **SÒNG TÀI XỈU BET88** 🔴\n"
                    f"Gõ `!tx <tai/xiu> <tiền>` (Tối đa 10,000,000$/ván)\n\n"
                    f"⏱️ Thời gian: **{remaining} giây**\n"
                    f"Tổng Tài: `{tx_session['total_tai']:,}$` | Tổng Xỉu: `{tx_session['total_xiu']:,}$`"
                )
            except: pass

        await asyncio.sleep(10)
        if not tx_session["active"]: return

        # Đóng phiên, tiến hành lắc bát
        tx_session["active"] = False
        try:
            await msg.edit(content=f"🎲 **NHÀ CÁI BET88 ĐANG XÓC BÁT...**\n💰 Tài: `{tx_session['total_tai']:,}$` | Tổng Xỉu: `{tx_session['total_xiu']:,}$`")
        except: pass

        await asyncio.sleep(2.0)

        d1, d2, d3 = random.randint(1,6), random.randint(1,6), random.randint(1,6)
        total = d1 + d2 + d3
        kq = "tai" if total >= 11 else "xiu"
        kq_text = "TÀI" if kq == "tai" else "XỈU"

        thang_list = []
        thua_list = []

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
            f"🟢 **MỞ BÁT BET88**\n"
            f"Kết Quả\n"
            f"`[ {d1} ]` - `[ {d2} ]` - `[ {d3} ]`\n\n"
            f"➔ **{total} ĐIỂM ({kq_text})**\n"
            f"✨ **THẮNG**\n{thang_str}\n\n"
            f"💸 **THUA**\n{thua_str}"
        )
        try:
            await msg.edit(content=final_res)
        except:
            await ctx.send(final_res)
        return

    # Nếu người chơi đặt cược: !tx tai 1
    choice = choice.lower()
    if choice not in ["tai", "xiu"]:
        return await ctx.send("❌ Cú pháp: `!tx [tai/xiu] [tiền]`")

    if not tx_session["active"]:
        return await ctx.send("❌ Hiện tại chưa có phiên Tài Xỉu nào! Hãy gõ `!tx` để mở phiên mới.")

    if not bet or bet <= 0:
        return await ctx.send("❌ Số tiền cược không hợp lệ!")

    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt! Ví chỉ còn `{u['cash']:,}$`.")

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
    await ctx.send(f"✅ {ctx.author.mention} Đã đặt thành công `{bet:,}$` vào cửa **{choice.upper()}**!")

# --- LỆNH XÓC ĐĨA (!xd) ---
@bot.command(name="xd", aliases=["xocdia"])
async def xocdia_cmd(ctx, choice: str = None, bet: int = None):
    cd = check_spam(ctx.author.id, "xd", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Đợi **{cd}**s!")

    if not choice or choice.lower() not in ["chan", "le"] or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!xd [chan/le] [tiền]` (Ví dụ: `!xd chan 2`)")

    u = get_user(ctx.author.id, ctx.author.name)
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt! Ví chỉ còn `{u['cash']:,}$`.")

    u["cash"] -= bet
    msg = await ctx.send(f"🪙 **XÓC ĐĨA BET88**\n4 Đồng xu\n*Xóc... xóc... xóc...*")
    await asyncio.sleep(1.2)
    
    reds = random.randint(0, 4)
    board = "🔴" * reds + "⚪" * (4 - reds)
    is_chan = (reds % 2 == 0)
    kq_name = "CHẴN" if is_chan else "LẺ"
    win = ((choice.lower() == "chan" and is_chan) or (choice.lower() == "le" and not is_chan))

    if win:
        u["cash"] += bet * 2
        res = (
            f"🪙 **XÓC ĐĨA BET88**\n"
            f"4 Đồng xu\n{board}\n"
            f"Kết quả\n➔ **{kq_name} ({reds} Đỏ)**\n"
            f"✨ **THẮNG!** Nhận `+{bet:,}$`"
        )
    else:
        res = (
            f"🪙 **XÓC ĐĨA BET88**\n"
            f"4 Đồng xu\n{board}\n"
            f"Kết quả\n➔ **{kq_name} ({reds} Đỏ)**\n"
            f"💸 **CÁI ĂN SẠCH!** `-{bet:,}$`"
        )
    await msg.edit(content=res)

# --- LỆNH BẦU CUA (!bc) ---
@bot.command(name="bc", aliases=["baucua"])
async def baucua_cmd(ctx, choice: str = None, bet: int = None):
    cd = check_spam(ctx.author.id, "bc", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Đợi **{cd}**s!")

    animals = {"ca": "🐟", "tom": "🦐", "cua": "🦀", "bau": "🥒", "ga": "🐓", "nai": "🦌"}
    if not choice or choice.lower() not in animals or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!bc [ca/tom/cua/bau/ga/nai] [tiền]`")

    u = get_user(ctx.author.id, ctx.author.name)
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt! Ví chỉ còn `{u['cash']:,}$`.")

    u["cash"] -= bet
    msg = await ctx.send(f"🎲 **BẦU CUA BET88**\nTrạng thái\n*Đang úp bát...*")
    await asyncio.sleep(1.0)

    keys = list(animals.keys())
    d1, d2, d3 = random.choice(keys), random.choice(keys), random.choice(keys)
    matches = [d1, d2, d3].count(choice.lower())

    if matches > 0:
        reward = bet * matches
        u["cash"] += bet + reward
        res = (
            f"🎲 **BẦU CUA BET88**\n"
            f"MỞ BÁT\n"
            f"`[ {animals[d1]} ] [ {animals[d2]} ] [ {animals[d3]} ]`\n"
            f"Tổng kết\n"
            f"✨ **TRÚNG {matches} CON!** Nhận `+{reward:,}$`"
        )
    else:
        res = (
            f"🎲 **BẦU CUA BET88**\n"
            f"MỞ BÁT\n"
            f"`[ {animals[d1]} ] [ {animals[d2]} ] [ {animals[d3]} ]`\n"
            f"Tổng kết\n"
            f"💸 **MẤT SẠCH!** `-{bet:,}$`"
        )
    await msg.edit(content=res)

token = os.getenv("BOT_TOKEN")
bot.run(token)
        
