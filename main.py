import os
import asyncio
import random
import time
import discord
from discord.ext import commands
from collections import Counter

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
users = {}
cooldowns = {}

def check_spam(user_id, cmd_name, limit_seconds=2.0):
    now = time.time()
    key = f"{user_id}_{cmd_name}"
    if key in cooldowns:
        diff = now - cooldowns[key]
        if diff < limit_seconds:
            return round(limit_seconds - diff, 1)
    cooldowns[key] = now
    return 0.0

def get_user(uid):
    if uid not in users:
        users[uid] = {
            "cash": 5003,
            "bank": 0,
        }
    return users[uid]

@bot.event
async def on_ready():
    print(f"✅ BOT ĐÃ SẴN SÀNG: {bot.user}")

# --- LỆNH MENU GIAO DIỆN KHUNG VUÔNG VIỀN VÀNG (!menu) ---
@bot.command(name="menu", aliases=["help", "giup"])
async def menu_cmd(ctx):
    cd = check_spam(ctx.author.id, "menu", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    # Tạo khung Embed hình vuông có sọc màu vàng bên trái (mã màu: 0xFFD700)
    embed = discord.Embed(
        title="🎰 HỆ THỐNG GAME & NGÂN HÀNG BET88",
        description="Dưới đây là danh sách các lệnh bạn có thể sử dụng:",
        color=0xFFD700 # Màu vàng
    )
    
    embed.add_field(
        name="🎲 TRÒ CHƠI",
        value=(
            "• `!tx [tai/xiu] [tiền]` (Đánh Tài Xỉu)\n"
            "• `!quay [tiền]` (Máy Slot)\n"
            "• `!bc [ca/tom/cua/bau/ga/nai] [tiền]` (Bầu Cua)\n"
            "• `!xd [chan/le] [tiền]` (Xóc Đĩa)"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🏦 HỆ THỐNG TÀI CHÍNH",
        value=(
            "• `!vi` hoặc `!vi @User` (Xem số dư)\n"
            "• `!gui [tiền/all]` (Gửi tiền vào két)\n"
            "• `!rut [tiền/all]` (Rút tiền từ két)\n"
            "• `!chuyen @User [tiền]` (Chuyển tiền mặt)"
        ),
        inline=False
    )
    
    embed.set_footer(text="Gõ lệnh trực tiếp vào kênh chat để bắt đầu!")
    await ctx.send(embed=embed)

# --- LỆNH XEM VÍ (!vi) ---
@bot.command(name="vi", aliases=["money", "bal"])
async def vi_cmd(ctx, member: discord.Member = None):
    cd = check_spam(ctx.author.id, "vi", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    target = member if member else ctx.author
    u = get_user(target.id)
    
    msg = (
        f"💳 Tài sản của {target.name}:\n"
        f"• Tiền mặt: `{u['cash']:,} $`\n"
        f"• Ngân hàng: `{u['bank']:,} $ (Lãi 2%/ngày)`"
    )
    await ctx.send(msg)

# --- LỆNH GỬI TIỀN (!gui) ---
@bot.command(name="gui")
async def gui_cmd(ctx, amount: str = None):
    cd = check_spam(ctx.author.id, "gui", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    u = get_user(ctx.author.id)
    if not amount:
        return await ctx.send("❌ Cú pháp: `!gui [số_tiền hoặc all]`")
    
    if amount.lower() == "all":
        val = u["cash"]
    else:
        try:
            val = int(amount)
        except ValueError:
            return await ctx.send("❌ Số tiền không hợp lệ!")
            
    if val <= 0 or u["cash"] < val:
        return await ctx.send("❌ Bạn không đủ tiền mặt để gửi!")
        
    u["cash"] -= val
    u["bank"] += val
    await ctx.send(f"🏦 Đã gửi thành công `{val:,} $` vào két sắt ngân hàng!")

# --- LỆNH RÚT TIỀN (!rut) ---
@bot.command(name="rut")
async def rut_cmd(ctx, amount: str = None):
    cd = check_spam(ctx.author.id, "rut", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    u = get_user(ctx.author.id)
    if not amount:
        return await ctx.send("❌ Cú pháp: `!rut [số_tiền hoặc all]`")
    
    if amount.lower() == "all":
        val = u["bank"]
    else:
        try:
            val = int(amount)
        except ValueError:
            return await ctx.send("❌ Số tiền không hợp lệ!")
            
    if val <= 0 or u["bank"] < val:
        return await ctx.send("❌ Số dư két sắt không đủ!")
        
    u["bank"] -= val
    u["cash"] += val
    await ctx.send(f"💸 Đã rút thành công `{val:,} $` từ két sắt về ví!")

# --- LỆNH CHUYỂN TIỀN (!chuyen) ---
@bot.command(name="chuyen", aliases=["pay", "give"])
async def chuyen_cmd(ctx, member: discord.Member = None, amount: int = None):
    cd = check_spam(ctx.author.id, "chuyen", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    if not member or not amount or amount <= 0:
        return await ctx.send("❌ Cú pháp: `!chuyen @User [tiền]`")
    if member.id == ctx.author.id:
        return await ctx.send("❌ Không thể tự chuyển tiền cho chính mình!")
        
    u_sender = get_user(ctx.author.id)
    if u_sender["cash"] < amount:
        return await ctx.send("❌ Tiền mặt của bạn không đủ để chuyển!")
        
    u_receiver = get_user(member.id)
    u_sender["cash"] -= amount
    u_receiver["cash"] += amount
    await ctx.send(f"🤝 **{ctx.author.name}** đã chuyển thành công `{amount:,} $` cho **{member.name}**!")

# --- LỆNH TÀI XỈU (!tx) ---
@bot.command(name="tx", aliases=["taixiu"])
async def taixiu_cmd(ctx, choice: str = None, bet: int = None):
    cd = check_spam(ctx.author.id, "tx", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    if not choice or choice.lower() not in ["tai", "xiu"] or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!tx [tai/xiu] [tiền]`")
        
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền mặt!")

    msg = await ctx.send(f"🎲 **TÀI XỈU BET88**\n📳 *Đang lắc xí ngầu...*")
    await asyncio.sleep(1.0)
    
    d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
    total = d1 + d2 + d3
    ket_qua = "tai" if total >= 11 else "xiu"
    
    res_text = f"🎲 **TÀI XỈU BET88 - KẾT QUẢ**\n🎯 Xí ngầu: `[ {d1} ] [ {d2} ] [ {d3} ]` (Tổng: **{total}** - **{ket_qua.upper()}**)"
    
    if choice.lower() == ket_qua:
        u["cash"] += bet
        res_text += f"\n🎉 **Thắng!** Nhận `+{bet:,} $`"
    else:
        u["cash"] -= bet
        res_text += f"\n💸 **Thua!** Mất `-{bet:,} $`"
        
    await msg.edit(content=res_text)

# --- LỆNH QUAY SLOT (!quay) ---
@bot.command(name="quay")
async def quay_cmd(ctx, bet: int = None):
    cd = check_spam(ctx.author.id, "quay", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    if not bet or bet <= 0:
        return await ctx.send(f"❌ Cú pháp: `!quay [tiền_cược]`")
    
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt!")

    symbols = ["💎", "🔔", "🍋", "🍒"]
    msg = await ctx.send(f"🎰 Vòng quay: `[ ? ] [ ? ] [ ? ]`")
    
    await asyncio.sleep(0.5)
    await msg.edit(content=f"🎰 Vòng quay: `[ 💎 ] [ ? ] [ ? ]`")
    
    await asyncio.sleep(0.5)
    is_win = random.random() < 0.4
    
    if is_win:
        s = random.choice(symbols)
        r1, r2, r3 = s, s, random.choice(symbols)
    else:
        r1, r2, r3 = random.sample(symbols, 3)
        
    cnt = Counter([r1, r2, r3])
    max_f = max(cnt.values())
    
    if max_f >= 2:
        win = bet * max_f
        u["cash"] += (win - bet)
        await msg.edit(content=f"🎰 Vòng quay: `[ {r1} ] [ {r2} ] [ {r3} ]`\n✨ **Trúng {max_f} con (x{max_f})!** Nhận `+{win:,} $`")
    else:
        u["cash"] -= bet
        await msg.edit(content=f"🎰 Vòng quay: `[ {r1} ] [ {r2} ] [ {r3} ]`\n😢 **Chúc bạn may mắn lần sau!** Mất `-{bet:,} $`")

# --- LỆNH XÓC ĐĨA (!xd) ---
@bot.command(name="xd", aliases=["xocdia"])
async def xocdia_cmd(ctx, choice: str = None, bet: int = None):
    cd = check_spam(ctx.author.id, "xd", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    if not choice or choice.lower() not in ["chan", "le"] or not bet or bet <= 0:
        return await ctx.send(f"❌ Cú pháp: `!xd [chan/le] [tiền]`")
        
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt!")

    msg = await ctx.send(f"🪙 **XÓC ĐĨA BET88**\n📳 *Xóc... xóc... xóc...*")
    await asyncio.sleep(0.8)
    
    red_count = random.randint(0, 4)
    ket_qua = "chan" if red_count % 2 == 0 else "le"
    board = "🔴" * red_count + "⚪" * (4 - red_count)
    
    res_text = f"🪙 **XÓC ĐĨA BET88 - KẾT QUẢ**\n📊 Bát mở: `{board}` (Đỏ: {red_count} ➔ **{ket_qua.upper()}**)"
    
    if choice.lower() == ket_qua:
        u["cash"] += bet
        res_text += f"\n🎉 **Thắng!** Ăn được `+{bet:,} $`"
    else:
        u["cash"] -= bet
        res_text += f"\n💸 **Thua!** Bạn mất `-{bet:,} $`"
        
    await msg.edit(content=res_text)

# --- LỆNH BẦU CUA (!bc) ---
@bot.command(name="bc", aliases=["baucua"])
async def baucua_cmd(ctx, choice: str = None, bet: int = None):
    cd = check_spam(ctx.author.id, "bc", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    animals = {"ca": "🐟", "tom": "🦐", "cua": "🦀", "bau": "🥒", "ga": "🐓", "nai": "🦌"}
    if not choice or choice.lower() not in animals or not bet or bet <= 0:
        return await ctx.send(f"❌ Cú pháp: `!bc [ca/tom/cua/bau/ga/nai] [tiền]`")
        
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt!")

    msg = await ctx.send(f"🎲 **BẦU CUA BET88**\n📳 *Đang úp bát...*")
    await asyncio.sleep(0.8)
    
    keys = list(animals.keys())
    d1, d2, d3 = random.choice(keys), random.choice(keys), random.choice(keys)
    matches = [d1, d2, d3].count(choice.lower())
    
    res_text = f"🎲 **BẦU CUA BET88 - KẾT QUẢ**\n🎯 Kết quả: `{animals[d1]} {d1.capitalize()} | {animals[d2]} {d2.capitalize()} | {animals[d3]} {d3.capitalize()}`"
    
    if matches > 0:
        win = int(bet * matches * 1.5)
        u["cash"] += win
        res_text += f"\n✨ **Trúng {matches} con (x1.5)!** Nhận `+{win:,} $`"
    else:
        u["cash"] -= bet
        res_text += f"\n😢 **Tróc vẩy!** Mất `-{bet:,} $`"
        
    await msg.edit(content=res_text)

token = os.getenv("BOT_TOKEN")
bot.run(token)
            
