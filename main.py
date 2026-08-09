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

# Hệ thống chống spam kiểm tra thời gian thực
cooldowns = {}

def check_spam(user_id, cmd_name, limit_seconds=1.5):
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
            "cash": 5003, # Khởi tạo mức tiền chuẩn
            "bank": 0,
        }
    return users[uid]

@bot.event
async def on_ready():
    print(f"✅ BOT ĐÃ CẬP NHẬT VÀ SẴN SÀNG: {bot.user}")

# --- MENU TRỢ GIÚP (!menu) ĐÃ CẬP NHẬT ---
@bot.command(name="menu", aliases=["trogiup"])
async def menu_cmd(ctx):
    cd = check_spam(ctx.author.id, "menu", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    msg = (
        "🎰 **CASINO BET88 UY TÍN** 🎰\n"
        "Chào mừng bạn đến với hệ thống giải trí đổi thưởng!\n\n"
        "🎲 **TRÒ CHƠI**\n"
        "`!tx [tai/xiu] [tiền]` (Đánh Tài Xỉu trực tiếp)\n"
        "`!roulette [xanh/do/den] [tiền]` (Quay Roulette)\n"
        "`!quay [tiền]` (Máy Slot)\n"
        "`!bc [ca/tom/cua/bau/ga/nai] [tiền]` (Bầu Cua)\n"
        "`!xd [chan/le] [tiền]` (Xóc Đĩa)\n\n"
        "🏛️ **HỆ THỐNG**\n"
        "`!vi` hoặc `!vi @User` | `!diemdanh`"
    )
    await ctx.send(msg)

# --- LỆNH TÀI XỈU NHANH (!tx [tai/xiu] [tiền]) ---
@bot.command(name="tx", aliases=["taixiu"])
async def taixiu_cmd(ctx, choice: str = None, bet: int = None):
    cd = check_spam(ctx.author.id, "tx", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    if not choice or choice.lower() not in ["tai", "xiu"] or not bet or bet <= 0:
        return await ctx.send(f"❌ Cú pháp: `!tx [tai/xiu] [tiền]`")
        
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt!")

    msg = await ctx.send(f"🎲 **TÀI XỈU BET88**\n📳 *Đang lắc xúc xắc...*")
    await asyncio.sleep(0.6)
    
    d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
    tong = d1 + d2 + d3
    ket_qua = "tai" if tong >= 11 else "xiu"
    
    res_text = f"🎲 **TÀI XỈU BET88 - KẾT QUẢ**\n`[ {d1} ] - [ {d2} ] - [ {d3} ]`\n➔ **{tong} Điểm ({ket_qua.upper()})**"
    
    if choice.lower() == ket_qua:
        u["cash"] += bet
        res_text += f"\n🎉 **Thắng!** Nhận `+{bet:,} $`"
    else:
        u["cash"] -= bet
        res_text += f"\n💸 **Thua!** Mất `-{bet:,} $`"
        
    await msg.edit(content=res_text)

# --- LỆNH ROULETTE (!roulette [xanh/do/den] [tiền]) ---
@bot.command(name="roulette", aliases=["rl"])
async def roulette_cmd(ctx, color_choice: str = None, bet: int = None):
    cd = check_spam(ctx.author.id, "roulette", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    valid_colors = {"do": ("🔴", 1.5, 50), "den": ("⚫", 2.0, 25), "xanh": ("🟢", 3.0, 10)}
    
    if not color_choice or color_choice.lower() not in valid_colors or not bet or bet <= 0:
        return await ctx.send(f"❌ Cú pháp: `!roulette [xanh/do/den] [tiền]`\n*(Tỷ lệ: Đỏ x1.5 [50%] | Đen x2 [25%] | Xanh x3 [10%])*")
        
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt!")

    choice = color_choice.lower()
    
    # Hiệu ứng xoay roulette trực quan
    msg = await ctx.send(f"🎡 **ROULETTE BET88**\n🔄 *Bánh xe đang quay: `[ 🔴 | 🟢 | ⚫ ]`*")
    await asyncio.sleep(0.5)
    await msg.edit(content=f"🎡 **ROULETTE BET88**\n🔄 *Đang dừng lại: `[ ⚫ | 🔴 | 🟢 ]`*")
    await asyncio.sleep(0.5)

    # Quay chuẩn xác theo tỷ lệ yêu cầu
    rand_val = random.randint(1, 100)
    if rand_val <= 10:
        result_color = "xanh"
    elif rand_val <= 35: # 25% cho đen
        result_color = "den"
    elif rand_val <= 85: # 50% cho đỏ
        result_color = "do"
    else:
        result_color = "do" if random.random() > 0.5 else "den"

    emoji, multiplier, _ = valid_colors[result_color]
    res_text = f"🎡 **ROULETTE BET88 - KẾT QUẢ**\n🎯 Ô trúng: **{emoji} {result_color.upper()}**"
    
    if choice == result_color:
        win = int(bet * multiplier)
        u["cash"] += (win - bet)
        res_text += f"\n🎉 **TRÚNG ROULETTE!** Nhận `+{win:,} $` (x{multiplier})"
    else:
        u["cash"] -= bet
        res_text += f"\n💸 **TRẬT LẤT!** Mất `-{bet:,} $`"
        
    await msg.edit(content=res_text)

# --- CÁC LỆNH KHÁC (VÍ, SLOT, XÓC ĐĨA, BẦU CUA, ĐIỂM DANH) ---
@bot.command(name="vi", aliases=["money", "bal"])
async def vi_cmd(ctx, member: discord.Member = None):
    cd = check_spam(ctx.author.id, "vi", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    target = member if member else ctx.author
    u = get_user(target.id)
    
    msg = (
        f"💳 Tài sản của {target.name}_{target.id[:4]}4617:\n"
        f"• Tiền mặt: `{u['cash']:,} $`\n"
        f"• Ngân hàng: `0 $ (Lãi 2%/ngày)`"
    )
    await ctx.send(msg)

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

@bot.command(name="diemdanh", aliases=["daily"])
async def diemdanh_cmd(ctx):
    cd = check_spam(ctx.author.id, "diemdanh", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    u = get_user(ctx.author.id)
    rw = random.randint(1000, 3000)
    u["cash"] += rw
    await ctx.send(f"🎁 **{ctx.author.name}** Điểm danh thành công! Nhận `+{rw:,} $`")

token = os.getenv("BOT_TOKEN")
bot.run(token)
        
