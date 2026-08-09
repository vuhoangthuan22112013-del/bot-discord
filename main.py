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
            "cash": 5003, # Khởi tạo mức tiền giống trong video mẫu
            "bank": 0,
        }
    return users[uid]

@bot.event
async def on_ready():
    print(f"✅ BOT ĐÃ SẴN SÀNG: {bot.user}")

# --- LỆNH XEM VÍ (!vi) ---
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
    
    # Hiệu ứng quay giống hệt video
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
    
    res_text = f"🎲 **BẦU CUA BET88 - KẾT QUẢ**\n🎯 Kết quả: `{animals[d1]} {d2.capitalize()} | {animals[d2]} {d2.capitalize()} | {animals[d3]} {d3.capitalize()}`"
    
    if matches > 0:
        win = int(bet * matches * 1.5)
        u["cash"] += win
        res_getText = f"\n✨ **Trúng {matches} con (x1.5)!** Nhận `+{win:,} $`"
        res_text += res_getText
    else:
        u["cash"] -= bet
        res_text += f"\n😢 **Tróc vẩy!** Mất `-{bet:,} $`"
        
    await msg.edit(content=res_text)

token = os.getenv("BOT_TOKEN")
bot.run(token)
            
