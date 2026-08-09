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
            "cash": 2000,
            "bank": 0,
            "hang": "Người chơi Thường",
            "ga": "Gà Công Nghiệp 🐥"
        }
    return users[uid]

@bot.event
async def on_ready():
    print(f"✅ BOT ĐÃ SẴN SÀNG: {bot.user}")

# --- LỆNH MENU ---
@bot.command(name="menu", aliases=["help", "giup"])
async def menu_cmd(ctx):
    cd = check_spam(ctx.author.id, "menu", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    embed = discord.Embed(
        title="🎰 CASINO BET88 UY TÍN 🎰",
        description="Chào mừng bạn đến với hệ thống giải trí đổi thưởng!",
        color=0xFFD700
    )
    
    embed.add_field(
        name="🎲 TÀI XỈU",
        value="`!tx` (Mở phiên) | `!tx [tai/xiu] [tiền]` (Đặt)",
        inline=False
    )
    embed.add_field(
        name="🎰 CASINO & GAME",
        value="• `!quay [tiền]` (Máy Slot)\n• `!bc [ca/tom/cua/bau/ga/nai] [tiền]` (Bầu Cua)\n• `!xd [chan/le] [tiền]` (Xóc Đĩa)",
        inline=False
    )
    embed.add_field(
        name="🏦 HỆ THỐNG TÀI CHÍNH",
        value="• `!vi` (Xem số dư)\n• `!gui [tiền/all]` (Gửi két)\n• `!rut [tiền/all]` (Rút két)\n• `!chuyen @User [tiền]`",
        inline=False
    )
    
    await ctx.send(embed=embed)

# --- LỆNH !VI (GIAO DIỆN CHUẨN ẢNH) ---
@bot.command(name="vi", aliases=["money", "bal"])
async def vi_cmd(ctx, member: discord.Member = None):
    cd = check_spam(ctx.author.id, "vi", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    target = member if member else ctx.author
    u = get_user(target.id)
    
    embed = discord.Embed(
        title=f"💳 TÀI KHOẢN: {target.name.upper()}_{target.id % 10000:04d}",
        color=0xFFD700
    )
    embed.add_field(
        name="Hạng thẻ",
        value=f"👤 {u['hang']}",
        inline=False
    )
    embed.add_field(
        name="Gà chiến",
        value=f"{u['ga']}",
        inline=False
    )
    embed.add_field(
        name="💵 Tiền mặt",
        value=f"`{u['cash']:,}$`",
        inline=False
    )
    embed.add_field(
        name="🏦 Kết sắt",
        value=f"`{u['bank']:,}$`",
        inline=False
    )
    
    await ctx.send(embed=embed)

# --- LỆNH GỬI TIỀN ---
@bot.command(name="gui")
async def gui_cmd(ctx, amount: str = None):
    u = get_user(ctx.author.id)
    if not amount:
        return await ctx.send("❌ Cú pháp: `!gui [số_tiền hoặc all]`")
    val = u["cash"] if amount.lower() == "all" else int(amount)
    if val <= 0 or u["cash"] < val:
        return await ctx.send("❌ Không đủ tiền mặt!")
    u["cash"] -= val
    u["bank"] += val
    await ctx.send(f"🏦 Đã gửi `{val:,}$` vào két sắt thành công!")

# --- LỆNH RÚT TIỀN ---
@bot.command(name="rut")
async def rut_cmd(ctx, amount: str = None):
    u = get_user(ctx.author.id)
    if not amount:
        return await ctx.send("❌ Cú pháp: `!rut [số_tiền hoặc all]`")
    val = u["bank"] if amount.lower() == "all" else int(amount)
    if val <= 0 or u["bank"] < val:
        return await ctx.send("❌ Kết sắt không đủ tiền!")
    u["bank"] -= val
    u["cash"] += val
    await ctx.send(f"💸 Đã rút `{val:,}$` về ví!")

# --- LỆNH CHUYỂN TIỀN ---
@bot.command(name="chuyen")
async def chuyen_cmd(ctx, member: discord.Member = None, amount: int = None):
    if not member or not amount or amount <= 0:
        return await ctx.send("❌ Cú pháp: `!chuyen @User [tiền]`")
    u_sender = get_user(ctx.author.id)
    if u_sender["cash"] < amount:
        return await ctx.send("❌ Tiền mặt không đủ!")
    u_receiver = get_user(member.id)
    u_sender["cash"] -= amount
    u_receiver["cash"] += amount
    await ctx.send(f"🤝 Chuyển thành công `{amount:,}$` cho **{member.name}**!")

# --- LỆNH TÀI XỈU (ĐỢI 30 GIÂY NHƯ VIDEO) ---
@bot.command(name="tx", aliases=["taixiu"])
async def taixiu_cmd(ctx, choice: str = None, bet: int = None):
    cd = check_spam(ctx.author.id, "tx", 2.0)
    if cd > 0:
        return await ctx.send(f"⚠️ Đợi **{cd}**s!")

    u = get_user(ctx.author.id)
    if not choice:
        # Mở phiên đếm ngược 30s
        msg = await ctx.send(
            f"🎲 **SÒNG TÀI XỈU BET88** 🎲\n"
            f"💬 `{ctx.author.name}` đã mở bát!\n"
            f"Gõ `!tx <tai/xiu> <tiền>` để theo!\n"
            f"⏱️ **Thời gian:** 30 giây"
        )
        for i in range(25, 0, -5):
            await asyncio.sleep(5.0)
            try:
                await msg.edit(content=f"🎲 **SÒNG TÀI XỈU BET88** 🎲\n💬 `{ctx.author.name}` đã mở bát!\n⏱️ **Thời gian:** {i} giây")
            except:
                pass
        await asyncio.sleep(5.0)
        
        d1, d2, d3 = random.randint(1,6), random.randint(1,6), random.randint(1,6)
        total = d1 + d2 + d3
        kq = "XỈU" if total <= 10 else "TÀI"
        await ctx.send(f"🎲 **MỞ BÁT BET88**\nKết Quả: `[ {d1} ]` - `[ {d2} ]` - `[ {d3} ]`\n➔ **{total} Điểm ({kq})**")
        return

    if choice.lower() not in ["tai", "xiu"] or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!tx [tai/xiu] [tiền]`")
    if u["cash"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền mặt!")

    # Đánh trực tiếp
    msg = await ctx.send(f"🎲 **NHÀ CÁI BET88 ĐANG XÓC BÁT...**\n🎲 Tái: `[ ? ] [ ? ] [ ? ]`")
    await asyncio.sleep(2.0)
    d1, d2, d3 = random.randint(1,6), random.randint(1,6), random.randint(1,6)
    total = d1 + d2 + d3
    kq = "tai" if total >= 11 else "xiu"
    
    res = f"🎲 **MỞ BÁT BET88**\nKết Quả\n`[ {d1} ]` - `[ {d2} ]` - `[ {d3} ]`\n➔ **{total} Điểm ({kq.upper()})**"
    if choice.lower() == kq:
        u["cash"] += bet
        res += f"\n✨ **THẮNG!** Nhận `+{bet:,}$`"
    else:
        u["cash"] -= bet
        res += f"\n💸 **THUA!** Mất `-{bet:,}$`"
    await msg.edit(content=res)

# --- LỆNH QUAY SLOT (HIỆU ỨNG NHƯ VIDEO) ---
@bot.command(name="quay")
async def quay_cmd(ctx, bet: int = 100):
    cd = check_spam(ctx.author.id, "quay", 1.0)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ tới! Đợi **{cd}**s nữa!")

    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt!")

    msg = await ctx.send(f"🎰 **MÁY SLOT BET88**\nKẾT QUẢ\n`[ 🍋 ] [ 🔔 ] [ 🍒 ]`\nThông báo\n💸 **TRẬT HỦ (MẤT TRẮNG)!** `-{bet}$`")
    u["cash"] -= bet

# --- LỆNH XÓC ĐĨA (HIỆU ỨNG NHƯ VIDEO) ---
@bot.command(name="xd", aliases=["xocdia"])
async def xocdia_cmd(ctx, choice: str = None, bet: int = None):
    if not choice or choice.lower() not in ["chan", "le"] or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!xd [chan/le] [tiền]`")
    
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send("❌ Không đủ tiền mặt!")

    msg = await ctx.send(f"🪙 **XÓC ĐĨA BET88**\n*Xóc... xóc... xóc...*")
    await asyncio.sleep(1.5)
    
    red_count = random.randint(0, 4)
    kq = "chan" if red_count % 2 == 0 else "le"
    board = "🔴" * red_count + "⚪" * (4 - red_count)
    
    res = f"🪙 **XÓC ĐĨA BET88**\n4 Đồng xu\n{board}\nKết quả\n➔ **{kq.upper()}** ({red_count} Đỏ)"
    if choice.lower() == kq:
        u["cash"] += bet
        res += f"\n🎉 **THẮNG!** Nhận `+{bet:,}$`"
    else:
        u["cash"] -= bet
        res += f"\n💸 **CÁI ĂN SẠCH!** Mất `-{bet:,}$`"
    await msg.edit(content=res)

# --- LỆNH BẦU CUA (HIỆU ỨNG NHƯ VIDEO) ---
@bot.command(name="bc", aliases=["baucua"])
async def baucua_cmd(ctx, choice: str = None, bet: int = None):
    animals = {"ca": "🐟", "tom": "🦐", "cua": "🦀", "bau": "🥒", "ga": "🐓", "nai": "🦌"}
    if not choice or choice.lower() not in animals or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!bc [ca/tom/cua/bau/ga/nai] [tiền]`")
        
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send("❌ Không đủ tiền mặt!")

    msg = await ctx.send(f"🎲 **BẦU CUA BET88**\nTrạng thái\n*Đang úp...*")
    await asyncio.sleep(1.5)
    
    keys = list(animals.keys())
    d1, d2, d3 = random.choice(keys), random.choice(keys), random.choice(keys)
    matches = [d1, d2, d3].count(choice.lower())
    
    res = f"🎲 **BẦU CUA BET88**\nMỞ BÁT\n`[ {animals[d1]} ] [ {animals[d2]} ] [ {animals[d3]} ]`"
    if matches > 0:
        win = bet * matches
        u["cash"] += win
        res += f"\n✨ **TRÚNG {matches} CON!** Nhận `+{win:,}$`"
    else:
        u["cash"] -= bet
        res += f"\n💸 **MẤT SẠCH!** Trừ `-{bet:,}$`"
    await msg.edit(content=res)

token = os.getenv("BOT_TOKEN")
bot.run(token)
    
