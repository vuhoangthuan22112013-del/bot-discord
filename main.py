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
    "msg": None
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
    print(f"✅ BOT ĐÃ SẴN SÀNG: {bot.user}")

# --- LỆNH ĐIỂM DANH ---
@bot.command(name="diemdanh")
async def diemdanh_cmd(ctx):
    user_id = ctx.author.id
    now = time.time()
    cooldown_time = 12 * 3600

    if user_id in diemdanh_cooldowns:
        elapsed = now - diemdanh_cooldowns[user_id]
        if elapsed < cooldown_time:
            remaining = int(cooldown_time - elapsed)
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            return await ctx.send(f"⚠️ {ctx.author.mention} Bạn đã điểm danh rồi! Đợi **{hours} giờ {minutes} phút** nữa nhé!")

    diemdanh_cooldowns[user_id] = now
    reward = random.randint(1000, 3000)
    u = get_user(user_id, ctx.author.name)
    u["cash"] += reward

    await ctx.send(f"🎁 {ctx.author.mention} Điểm danh thành công! Nhận `+{reward:,}$`")

# --- LỆNH !MENU ---
@bot.command(name="menu", aliases=["help", "giup"])
async def menu_cmd(ctx):
    cd = check_spam(ctx.author.id, "menu", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Từ từ thôi! Đợi **{cd}**s!")

    embed = discord.Embed(
        title="🎰 CASINO BET88 UY TÍN 🎰",
        description="Chào mừng bạn đến với hệ thống giải trí đổi thưởng!",
        color=0xFFD700
    )
    embed.add_field(name="🎲 TÀI XỈU", value="`!tx` (Mở phiên)\n`!tx [tai/xiu] [tiền]` (Đặt cược)", inline=False)
    embed.add_field(name="🎰 CASINO & GAME", value="`!quay [tiền]` (Slot)\n`!bc [ca/tom/cua/bau/ga/nai] [tiền]` (Bầu Cua)\n`!xd [chan/le] [tiền]` (Xóc Đĩa)", inline=False)
    embed.add_field(name="💳 HỆ THỐNG TÀI CHÍNH", value="`!vi` (Xem số dư)\n`!gui [tiền/all]` (Gửi két)\n`!rut [tiền/all]` (Rút két)\n`!chuyen @User [tiền]`", inline=False)
    await ctx.send(embed=embed)

# --- LỆNH !VI ---
@bot.command(name="vi", aliases=["money", "bal"])
async def vi_cmd(ctx, member: discord.Member = None):
    cd = check_spam(ctx.author.id, "vi", 1.0)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Từ từ thôi! Đợi **{cd}**s!")

    target = member if member else ctx.author
    u = get_user(target.id, target.name)
    tag_id = target.id % 10000
    
    embed = discord.Embed(
        title=f"💳 TÀI KHOẢN: {target.name.upper()}_{tag_id:04d}",
        color=0xFFD700
    )
    embed.add_field(name="Hạng thẻ", value=f"👤 {u['hang']}", inline=False)
    embed.add_field(name="Gà chiến", value=f"{u['ga']}", inline=False)
    embed.add_field(name="💵 Tiền mặt", value=f"`{u['cash']:,}$`", inline=False)
    embed.add_field(name="🏦 Kết sắt", value=f"`{u['bank']:,}$`", inline=False)
    
    await ctx.send(embed=embed)

# --- LỆNH GỬI / RÚT / CHUYỂN ---
@bot.command(name="gui")
async def gui_cmd(ctx, amount: str = None):
    u = get_user(ctx.author.id, ctx.author.name)
    if not amount: return await ctx.send("❌ Cú pháp: `!gui [số_tiền hoặc all]`")
    val = u["cash"] if amount.lower() == "all" else int(amount)
    if val <= 0 or u["cash"] < val: return await ctx.send("❌ Không đủ tiền mặt trong ví!")
    u["cash"] -= val
    u["bank"] += val
    await ctx.send(f"🏦 Đã gửi `{val:,}$` vào két sắt thành công!")

@bot.command(name="rut")
async def rut_cmd(ctx, amount: str = None):
    u = get_user(ctx.author.id, ctx.author.name)
    if not amount: return await ctx.send("❌ Cú pháp: `!rut [số_tiền hoặc all]`")
    val = u["bank"] if amount.lower() == "all" else int(amount)
    if val <= 0 or u["bank"] < val: return await ctx.send("❌ Két sắt không đủ tiền!")
    u["bank"] -= val
    u["cash"] += val
    await ctx.send(f"💸 Đã rút `{val:,}$` về ví!")

@bot.command(name="chuyen")
async def chuyen_cmd(ctx, member: discord.Member = None, amount: int = None):
    if not member or not amount or amount <= 0:
        return await ctx.send("❌ Cú pháp: `!chuyen @User [tiền]`")
    u_sender = get_user(ctx.author.id, ctx.author.name)
    if u_sender["cash"] < amount: return await ctx.send("❌ Tiền mặt không đủ để chuyển!")
    u_receiver = get_user(member.id, member.name)
    u_sender["cash"] -= amount
    u_receiver["cash"] += amount
    await ctx.send(f"🤝 Chuyển thành công `{amount:,}$` cho **{member.name}**!")

# --- LỆNH TÀI XỈU (!tx) ---
@bot.command(name="tx", aliases=["taixiu"])
async def taixiu_cmd(ctx, choice: str = None, bet: int = None):
    global tx_session
    u = get_user(ctx.author.id, ctx.author.name)

    # 1. Nếu chỉ gõ !tx -> Mở phiên
    if not choice and not bet:
        if tx_session["active"]:
            return await ctx.send("⚠️ Đang có một phiên Tài Xỉu diễn ra!")
        
        tx_session["active"] = True
        msg = await ctx.send(
            f"🔴 **SÒNG TÀI XỈU BET88** 🔴\n"
            f"💬 `{ctx.author.name}` đã mở bát!\n"
            f"Gõ `!tx <tai/xiu> <tiền>` để theo!\n"
            f"(Cước Max: 10,000,000$/ván)\n\n"
            f"⏱️ Thời gian: **30 giây**\n"
            f"Tổng Tài: 0$ | Tổng Xỉu: 0$"
        )
        tx_session["msg"] = msg

        times = [25, 20, 15, 10, 5]
        for t in times:
            await asyncio.sleep(5.0)
            if not tx_session["active"]: return
            try:
                await msg.edit(content=
                    f"🔴 **SÒNG TÀI XỈU BET88** 🔴\n"
                    f"💬 `{ctx.author.name}` đã mở bát!\n"
                    f"Gõ `!tx <tai/xiu> <tiền>` để theo!\n"
                    f"(Cước Max: 10,000,000$/ván)\n\n"
                    f"⏱️ Thời gian: **{t} giây**\n"
                    f"Tổng Tài: 0$ | Tổng Xỉu: 0$"
                )
            except: pass

        await asyncio.sleep(5.0)
        if not tx_session["active"]: return

        # Kết quả ngẫu nhiên
        d1, d2, d3 = random.randint(1,6), random.randint(1,6), random.randint(1,6)
        total = d1 + d2 + d3
        kq = "tai" if total >= 11 else "xiu"
        kq_text = "TÀI" if kq == "tai" else "XỈU"

        tx_session["active"] = False
        res = (
            f"👑 **MỞ BÁT BET88**\n"
            f"Kết Quả\n`[ {d1} ]` - `[ {d2} ]` - `[ {d3} ]`\n\n"
            f"➔ **{total} ĐIỂM ({kq_text})**\n"
            f"✨ **THẮNG**\nKhông có\n\n💸 **THUA**\nKhông có"
        )
        try: await msg.edit(content=res)
        except: await ctx.send(res)
        return

    # 2. Xử lý đặt cược !tx [tai/xiu] [tiền]
    if not choice or choice.lower() not in ["tai", "xiu"] or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!tx [tai/xiu] [tiền]`")

    if not tx_session["active"]:
        return await ctx.send("❌ Chưa có phiên Tài Xỉu nào mở! Hãy gõ `!tx` để mở phiên trước.")

    # KIỂM TRA SỐ DƯ NGHIÊM NGẶT
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt! Ví bạn chỉ có `{u['cash']:,}$`, cần ít nhất `{bet:,}$`.")

    u["cash"] -= bet
    await ctx.send(f"✅ `{ctx.author.name}` đã đặt thành công `{bet:,}$` vào cửa **{choice.upper()}**!")

# --- LỆNH QUAY SLOT (!quay) ---
@bot.command(name="quay")
async def quay_cmd(ctx, bet: int = 100):
    cd = check_spam(ctx.author.id, "quay", 1.0)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Từ từ thôi! Đợi **{cd}**s!")

    u = get_user(ctx.author.id, ctx.author.name)
    
    # KIỂM TRA SỐ DƯ NGHIÊM NGẶT
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt để quay! Ví hiện tại chỉ còn `{u['cash']:,}$`.")

    u["cash"] -= bet
    await ctx.send(
        f"🎰 **MÁY SLOT BET88**\n"
        f"KẾT QUẢ\n"
        f"`[ 🍋 ] [ 🔔 ] [ 🍒 ]`\n"
        f"Thông báo\n"
        f"💸 **TRẬT HỦ (MẤT TRẮNG)!** `-{bet:,}$`"
    )

# --- LỆNH XÓC ĐĨA (!xd) ---
@bot.command(name="xd", aliases=["xocdia"])
async def xocdia_cmd(ctx, choice: str = None, bet: int = None):
    if not choice or choice.lower() not in ["chan", "le"] or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!xd [chan/le] [tiền]`")
    
    u = get_user(ctx.author.id, ctx.author.name)
    
    # KIỂM TRA SỐ DƯ NGHIÊM NGẶT
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt! Ví hiện tại chỉ còn `{u['cash']:,}$`.")

    msg = await ctx.send(f"🪙 **XÓC ĐĨA BET88**\n4 Đồng xu\n*Xóc... xóc... xóc...*")
    await asyncio.sleep(2.0)
    
    u["cash"] -= bet
    res = (
        f"🪙 **XÓC ĐĨA BET88**\n"
        f"4 Đồng xu\n🔴🔴⚪⚪\n"
        f"Kết quả\n➔ **CHẮN (0 Đỏ)**\n"
        f"💸 **CÁI ĂN SẠCH!** `-{bet:,}$`"
    )
    await msg.edit(content=res)

# --- LỆNH BẦU CUA (!bc) ---
@bot.command(name="bc", aliases=["baucua"])
async def baucua_cmd(ctx, choice: str = None, bet: int = None):
    animals = {"ca": "🐟", "tom": "🦐", "cua": "🦀", "bau": "🥒", "ga": "🐓", "nai": "🦌"}
    if not choice or choice.lower() not in animals or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!bc [ca/tom/cua/bau/ga/nai] [tiền]`")
        
    u = get_user(ctx.author.id, ctx.author.name)
    
    # KIỂM TRA SỐ DƯ NGHIÊM NGẶT
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt! Ví hiện tại chỉ còn `{u['cash']:,}$`.")

    msg = await ctx.send(f"🎲 **BẦU CUA BET88**\nTrạng thái\n*Đang úp...*")
    await asyncio.sleep(1.5)
    
    u["cash"] -= bet
    res = (
        f"🎲 **BẦU CUA BET88**\n"
        f"MỞ BÁT\n"
        f"`[ 🐟 ] [ 🥒 ] [ 🐟 ]`\n"
        f"Tổng kết\n"
        f"💸 **MẤT SẠCH!** `-{bet:,}$`"
    )
    await msg.edit(content=res)

token = os.getenv("BOT_TOKEN")
bot.run(token)
            
