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

# Lưu trữ thời gian cooldown thủ công để chống spam tuyệt đối
cooldowns = {}

def check_cooldown(user_id, command_name, seconds):
    now = time.time()
    key = f"{user_id}_{command_name}"
    if key in cooldowns and now - cooldowns[key] < seconds:
        return round(seconds - (now - cooldowns[key]), 1)
    cooldowns[key] = now
    return 0

# Biến quản lý phiên Tài Xỉu
tx_session = {
    "active": False,
    "bets": {},      # {user_id: {"choice": "tai"/"xiu", "bet": int, "name": str}}
    "time_left": 0
}

def get_user(uid):
    if uid not in users:
        users[uid] = {
            "cash": 10000,
            "bank": 0,
            "last_daily": 0
        }
    return users[uid]

@bot.event
async def on_ready():
    print(f"✅ BOT ONLINE THÀNH CÔNG: {bot.user}")

# --- MENU TRỢ GIÚP ---
@bot.command(name="menu", aliases=["trogiup"])
async def menu_cmd(ctx):
    cd = check_cooldown(ctx.author.id, "menu", 2)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}s** nữa!")

    embed = discord.Embed(
        title="🎰 CASINO BET88 UY TÍN 🎰",
        description="Chào mừng bạn đến với hệ thống giải trí đổi thưởng!",
        color=0xFFD700
    )
    embed.add_field(
        name="🎲 SÒNG TÀI XỈU BET88 🎲",
        value="`!tx` : Mở phiên Tài Xỉu (30 giây)\n`!tx [tai/xiu] [tiền]` : Đặt cược theo phiên",
        inline=False
    )
    embed.add_field(
        name="🎰 CASINO SOLO",
        value="`!quay [tiền]`\n`!bc [bau/cua/tom/ca/ga/nai] [tiền]`\n`!xd [chan/le] [tiền]`",
        inline=False
    )
    embed.add_field(
        name="🏛️ HỆ THỐNG",
        value="`!vi` hoặc `!vi @User` : Xem ví tiền\n`!diemdanh` : Nhận quà mỗi ngày",
        inline=False
    )
    await ctx.send(embed=embed)

# --- SÒNG TÀI XỈU BET88 ---
@bot.command(name="tx", aliases=["taixiu"])
async def taixiu_cmd(ctx, choice: str = None, bet: int = None):
    global tx_session
    
    # 1. Khởi tạo phiên
    if not choice and not bet:
        cd = check_cooldown(ctx.author.id, "tx_mo", 3)
        if cd > 0:
            return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}s** nữa!")

        if tx_session["active"]:
            return await ctx.send(f"⏳ Phiên Tài Xỉu đang diễn ra! Còn **{tx_session['time_left']}s**.")
        
        tx_session["active"] = True
        tx_session["bets"] = {}
        tx_session["time_left"] = 30
        
        embed = discord.Embed(
            title="🎲 SÒNG TÀI XỈU BET88 🎲",
            description=f"**{ctx.author.name}** đã mở bát!\nGõ `!tx <tai/xiu> <tiền>` để theo!\n*(Tối đa 10,000,000$/ván)*",
            color=0xE74C3C
        )
        embed.add_field(name="⏰ Thời gian", value="**30 giây**", inline=False)
        embed.add_field(name="📊 Tổng TÀI / XỈU", value="Tổng TÀI: **0$** | Tổng XỈU: **0$**", inline=False)
        msg = await ctx.send(embed=embed)
        
        for t in [20, 10, 0]:
            await asyncio.sleep(10)
            tx_session["time_left"] = t
            if t > 0:
                tai_val = sum(b["bet"] for b in tx_session["bets"].values() if b["choice"] == "tai")
                xiu_val = sum(b["bet"] for b in tx_session["bets"].values() if b["choice"] == "xiu")
                
                embed.set_field_at(0, name="⏰ Thời gian", value=f"**{t} giây**", inline=False)
                embed.set_field_at(1, name="📊 Tổng TÀI / XỈU", value=f"Tổng TÀI: **{tai_val:,}$** | Tổng XỈU: **{xiu_val:,}$**", inline=False)
                await msg.edit(embed=embed)

        # MỞ BÁT
        tx_session["active"] = False
        d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
        tong = d1 + d2 + d3
        ket_qua = "tai" if tong >= 11 else "xiu"
        
        res_embed = discord.Embed(
            title="🎲 MỞ BÁT BET88",
            description=f"**Kết quả:**\n`[ {d1} ] - [ {d2} ] - [ {d3} ]`\n➔ **{tong} Điểm ({ket_qua.upper()})**",
            color=0x2ECC71
        )
        
        thang_list, thua_list = [], []
        for uid, bdata in tx_session["bets"].items():
            u = get_user(uid)
            if bdata["choice"] == ket_qua:
                u["cash"] += bdata["bet"]
                thang_list.append(f"• **{bdata['name']}** (+{bdata['bet']:,}$)")
            else:
                u["cash"] -= bdata["bet"]
                thua_list.append(f"• **{bdata['name']}** (-{bdata['bet']:,}$)")
                
        res_embed.add_field(name="🎉 THẮNG", value="\n".join(thang_list) if thang_list else "Không có", inline=False)
        res_embed.add_field(name="💸 THUA", value="\n".join(thua_list) if thua_list else "Không có", inline=False)
        return await ctx.send(embed=res_embed)

    # 2. Đặt cược
    if not tx_session["active"]:
        return await ctx.send("❌ Chưa có phiên Tài Xỉu nào! Gõ `!tx` để mở phiên mới.")
    
    uid = ctx.author.id
    if uid in tx_session["bets"]:
        return await ctx.send(f"❌ **{ctx.author.name}**, bạn đã đặt cược ván này rồi!")
        
    if choice.lower() not in ["tai", "xiu"] or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!tx [tai/xiu] [tiền]`")
        
    u = get_user(uid)
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt!")
        
    tx_session["bets"][uid] = {"choice": choice.lower(), "bet": bet, "name": ctx.author.name}
    await ctx.send(f"✅ **{ctx.author.name}** đã cược **{bet:,}$** vào **{choice.upper()}**!")

# --- MÁY SLOT / QUAY ---
@bot.command(name="quay")
async def quay_cmd(ctx, bet: int = None):
    cd = check_cooldown(ctx.author.id, "quay", 2)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}s** nữa!")

    if not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!quay [tiền_cược]`")
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền!")

    symbols = ["🍋", "🍒", "🔔", "💎", "7️⃣"]
    
    embed = discord.Embed(title="🎰 MÁY SLOT BET88", color=0xF1C40F)
    embed.add_field(name="Máy đang quay...", value="`[ 🍋 | 🔔 | 🍋 ]`", inline=False)
    msg = await ctx.send(embed=embed)
    
    await asyncio.sleep(0.8)
    embed.set_field_at(0, name="Máy đang quay...", value="`[ 🔔 | 🔔 | 🍒 ]`", inline=False)
    await msg.edit(embed=embed)
    
    await asyncio.sleep(0.8)
    
    is_win = random.random() < 0.36
    if is_win:
        s = random.choice(symbols)
        r1, r2, r3 = s, s, random.choice(symbols)
    else:
        r1, r2, r3 = random.sample(symbols, 3)
        
    cnt = Counter([r1, r2, r3])
    max_f = max(cnt.values())
    
    res_embed = discord.Embed(title="🎰 MÁY SLOT BET88", color=0x2ECC71 if max_f > 1 else 0xE74C3C)
    res_embed.add_field(name="KẾT QUẢ", value=`[ {r1} | {r2} | {r3} ]`, inline=False)
    
    if max_f == 3:
        win = bet * 5
        u["cash"] += (win - bet)
        res_embed.add_field(name="Thông báo", value=f"🎉 **JACKPOT!** +{win:,}$", inline=False)
    elif max_f == 2:
        win = bet * 2
        u["cash"] += (win - bet)
        res_embed.add_field(name="Thông báo", value=f"✨ **TRÚNG 2 MÓN!** +{win:,}$", inline=False)
    else:
        u["cash"] -= bet
        res_embed.add_field(name="Thông báo", value=f"😭 **TRẮT HŨ (MẤT TRẮNG)!** -{bet:,}$", inline=False)
        
    await msg.edit(embed=res_embed)

# --- BẦU CUA BET88 ---
@bot.command(name="bc", aliases=["baucua"])
async def baucua_cmd(ctx, choice: str = None, bet: int = None):
    cd = check_cooldown(ctx.author.id, "bc", 2)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}s** nữa!")

    animals = {"bau": "🥒", "cua": "🦀", "tom": "🦐", "ca": "🐟", "ga": "🐓", "nai": "🦌"}
    if not choice or choice.lower() not in animals or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!bc [bau/cua/tom/ca/ga/nai] [tiền]`")
        
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền!")

    embed = discord.Embed(title="🎲 BẦU CUA BET88", color=0xE67E22)
    embed.add_field(name="Trạng thái", value="*Bát đang úp...*\n`[ ? ] [ ? ] [ ? ]`", inline=False)
    msg = await ctx.send(embed=embed)
    
    await asyncio.sleep(1)
    embed.set_field_at(0, name="Trạng thái", value="*Từ từ hé bát...*", inline=False)
    await msg.edit(embed=embed)
    
    keys = list(animals.keys())
    d1, d2, d3 = random.choice(keys), random.choice(keys), random.choice(keys)
    matches = [d1, d2, d3].count(choice.lower())
    
    res_embed = discord.Embed(title="🎲 BẦU CUA BET88", color=0x2ECC71 if matches > 0 else 0xE74C3C)
    res_embed.add_field(name="MỞ BÁT", value=f"`[ {animals[d1]} ] [ {animals[d2]} ] [ {animals[d3]} ]`", inline=False)
    
    if matches > 0:
        win = int(bet * (1 + matches * 0.5))
        u["cash"] += win
        res_embed.add_field(name="Tổng kết", value=f"🎉 **TRÚNG {matches} CON!** +{win:,}$", inline=False)
    else:
        u["cash"] -= bet
        res_embed.add_field(name="Tổng kết", value=f"💸 **MẤT SẠCH!** -{bet:,}$", inline=False)
        
    await msg.edit(embed=res_embed)

# --- XÓC ĐĨA BET88 ---
@bot.command(name="xd", aliases=["xocdia"])
async def xocdia_cmd(ctx, choice: str = None, bet: int = None):
    cd = check_cooldown(ctx.author.id, "xd", 2)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}s** nữa!")

    if not choice or choice.lower() not in ["chan", "le"] or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!xd [chan/le] [tiền]`")
        
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền!")

    embed = discord.Embed(title="🪙 XÓC ĐĨA BET88", color=0xE67E22)
    embed.add_field(name="Trạng thái", value="*Xóc... xóc... xóc...*", inline=False)
    msg = await ctx.send(embed=embed)
    
    await asyncio.sleep(1)
    embed.set_field_at(0, name="Trạng thái", value="*Đặt bát xuống bàn...*", inline=False)
    await msg.edit(embed=embed)
    
    red_count = sum([random.choice([0, 1]) for _ in range(4)])
    ket_qua = "chan" if red_count % 2 == 0 else "le"
    board = "🔴" * red_count + "⚪" * (4 - red_count)
    
    res_embed = discord.Embed(title="🪙 XÓC ĐĨA BET88", color=0x2ECC71 if choice.lower() == ket_qua else 0xE74C3C)
    res_embed.add_field(name="4 Đồng xu", value=board, inline=False)
    res_embed.add_field(name="Kết quả", value=f"➔ **{ket_qua.upper()}** ({red_count} Đỏ)", inline=False)
    
    if choice.lower() == ket_qua:
        u["cash"] += bet
        res_embed.add_field(name="Thông báo", value=f"🎉 **THẮNG ĐẬM!** +{bet:,}$", inline=False)
    else:
        u["cash"] -= bet
        res_embed.add_field(name="Thông báo", value=f"💸 **CÁI ĂN SẠCH!** -{bet:,}$", inline=False)
        
    await msg.edit(embed=res_embed)

# --- XEM VÍ (CỦA MÌNH HOẶC CỦA NGƯỜI KHÁC QUA @TAG) ---
@bot.command(name="vi", aliases=["money", "bal"])
async def vi_cmd(ctx, member: discord.Member = None):
    cd = check_cooldown(ctx.author.id, "vi", 2)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}s** nữa!")

    target = member if member else ctx.author
    u = get_user(target.id)
    
    embed = discord.Embed(title=f"💳 TÀI KHOẢN: {target.name.upper()}", color=0x3498DB)
    embed.add_field(name="💵 Tiền mặt", value=f"`{u['cash']:,}$`", inline=False)
    embed.add_field(name="🏦 Két sắt", value=f"`{u['bank']:,}$`", inline=False)
    await ctx.send(embed=embed)

# --- ĐIỂM DANH MỖI NGÀY ---
@bot.command(name="diemdanh", aliases=["daily"])
async def diemdanh_cmd(ctx):
    cd = check_cooldown(ctx.author.id, "diemdanh", 2)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}s** nữa!")

    u = get_user(ctx.author.id)
    now = time.time()
    if now - u["last_daily"] < 43200: # 12 tiếng
        rem = int(43200 - (now - u["last_daily"]))
        return await ctx.send(f"⏳ **{ctx.author.name}**, quay lại sau **{rem//3600}h {(rem%3600)//60}m** nữa nhé!")
    
    rw = random.randint(1000, 3000)
    u["cash"] += rw
    u["last_daily"] = now
    await ctx.send(f"🎁 **{ctx.author.name}** Điểm danh thành công! Nhận ngay `+{rw:,}$`")

token = os.getenv("BOT_TOKEN")
bot.run(token)
    
