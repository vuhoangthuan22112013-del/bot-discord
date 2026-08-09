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

def get_user(uid):
    if uid not in users:
        users[uid] = {
            "cash": 10000,
            "bank": 0,
            "last_daily": 0,         # Thời gian điểm danh gần nhất
            "last_interest": time.time()  # Thời gian tính lãi ngân hàng
        }
    return users[uid]

@bot.event
async def on_ready():
    print(f"✅ BOT ONLINE THÀNH CÔNG: {bot.user}")

# --- MENU TRỢ GIÚP ---
@bot.command(name="menu", aliases=["trogiup"])
async def menu_cmd(ctx):
    embed = discord.Embed(
        title="🎰 CASINO BET88 UY TÍN 🎰",
        description="Chào mừng bạn đến với hệ thống giải trí đổi thưởng!",
        color=0xFFD700
    )
    embed.add_field(
        name="⚔️ ĐỐI KHÁNG PVP",
        value="`!thachdau @User [tiền]` (hoặc `!danhbai`)",
        inline=False
    )
    embed.add_field(
        name="🎲 CASINO SOLO",
        value="`!tx [tai/xiu] [tiền]`\n`!coinflip [ngua/up] [tiền]`\n`!quay [tiền]`\n`!bc [bau/cua/tom/ca/ga/nai] [tiền]`\n`!xd [chan/le] [tiền]`",
        inline=False
    )
    embed.add_field(
        name="🏛️ HỆ THỐNG & NGÂN HÀNG",
        value="`!vi`, `!gui [tiền]`, `!rut [tiền]`, `!nhanlai`, `!chuyen @User [tiền]`, `!diemdanh`, `!bxh`, `!nhapcode [code]`",
        inline=False
    )
    embed.set_footer(text="Lãi ngân hàng 2%/ngày (!nhanlai) | Điểm danh 12h/lần!")
    await ctx.send(embed=embed)

# --- HỆ THỐNG VÍ & NGÂN HÀNG (LÃI 2%/NGÀY) ---
@bot.command(name="vi", aliases=["money", "bal"])
async def check_vi(ctx):
    u = get_user(ctx.author.id)
    await ctx.send(f"💰 **Tài sản của {ctx.author.name}:**\n- Tiền mặt: `{u['cash']:,}` $\n- Ngân hàng: `{u['bank']:,}` $ (Lãi 2%/ngày)")

@bot.command(name="gui", aliases=["guitien"])
async def gui_tien(ctx, amount: str = None):
    u = get_user(ctx.author.id)
    if not amount:
        return await ctx.send("❌ Cú pháp: `!gui 5000` hoặc `!gui all`")
    val = u["cash"] if amount.lower() == "all" else int(amount) if amount.isdigit() else 0
    if val <= 0 or u["cash"] < val:
        return await ctx.send("❌ Số tiền không hợp lệ hoặc bạn không đủ tiền mặt!")
    u["cash"] -= val
    u["bank"] += val
    await ctx.send(f"🏦 Bạn đã gửi thành công `{val:,}` $ vào ngân hàng!")

@bot.command(name="rut", aliases=["ruttien"])
async def rut_tien(ctx, amount: str = None):
    u = get_user(ctx.author.id)
    if not amount:
        return await ctx.send("❌ Cú pháp: `!rut 5000` hoặc `!rut all`")
    val = u["bank"] if amount.lower() == "all" else int(amount) if amount.isdigit() else 0
    if val <= 0 or u["bank"] < val:
        return await ctx.send("❌ Số tiền không hợp lệ hoặc bạn không đủ tiền ngân hàng!")
    u["bank"] -= val
    u["cash"] += val
    await ctx.send(f"💵 Bạn đã rút thành công `{val:,}` $ về ví tiền mặt!")

# TỰ ĐỘNG CỘNG LÃI NGÂN HÀNG 2%/NGÀY
@bot.command(name="nhanlai", aliases=["lai"])
async def nhan_lai(ctx):
    u = get_user(ctx.author.id)
    if u["bank"] <= 0:
        return await ctx.send("❌ Bạn không có tiền trong ngân hàng để nhận lãi!")
    
    now = time.time()
    elapsed = now - u.get("last_interest", now)
    days = elapsed / 86400  # 86400 giây = 24 giờ
    
    if days < 1:
        hours_left = int((86400 - elapsed) // 3600)
        mins_left = int(((86400 - elapsed) % 3600) // 60)
        return await ctx.send(f"⏳ Chưa đủ 24h để nhận lãi! Vui lòng chờ thêm **{hours_left} giờ {mins_left} phút**.")
    
    lai = int(u["bank"] * 0.02 * int(days))
    if lai < 1:
        lai = 1
    u["bank"] += lai
    u["last_interest"] = now
    await ctx.send(f"📈 Bạn đã nhận thành công `{lai:,}` $ tiền lãi ngân hàng (2%/ngày)!")

# --- ĐIỂM DANH (12 TIẾNG / LẦN, THƯỞNG 1,000 - 3,000 $) ---
@bot.command(name="diemdanh", aliases=["daily"])
async def diem_danh(ctx):
    u = get_user(ctx.author.id)
    now = time.time()
    cooldown = 12 * 3600  # 12 tiếng tính theo giây (43200s)
    
    if now - u["last_daily"] < cooldown:
        remaining = cooldown - (now - u["last_daily"])
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        return await ctx.send(f"⏳ **{ctx.author.name}**, bạn đã điểm danh rồi! Vui lòng quay lại sau **{hours} giờ {minutes} phút** nữa.")
    
    reward = random.randint(1000, 3000)
    u["cash"] += reward
    u["last_daily"] = now
    await ctx.send(f"🎉 **{ctx.author.name}** đã điểm danh thành công và nhận được `{reward:,}` $!")

# --- CHUYỂN TIỀN & BXH & CODE ---
@bot.command(name="chuyen", aliases=["chuyentien"])
async def chuyen_tien(ctx, member: discord.Member = None, amount: int = None):
    if not member or not amount or amount <= 0:
        return await ctx.send("❌ Cú pháp: `!chuyen @User [số_tiền]`")
    u1 = get_user(ctx.author.id)
    if u1["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền mặt!")
    u2 = get_user(member.id)
    u1["cash"] -= amount
    u2["cash"] += amount
    await ctx.send(f"💸 **{ctx.author.name}** đã chuyển `{amount:,}` $ cho **{member.name}**!")

@bot.command(name="bxh", aliases=["top"])
async def bang_xep_hang(ctx):
    if not users:
        return await ctx.send("Chưa có dữ liệu người chơi!")
    sorted_users = sorted(users.items(), key=lambda x: x[1]["cash"] + x[1]["bank"], reverse=True)[:5]
    msg = "🏆 **BẢNG XẾP HẠNG ĐẠI GIA** 🏆\n"
    for i, (uid, data) in enumerate(sorted_users, 1):
        total = data["cash"] + data["bank"]
        user_obj = bot.get_user(uid)
        name = user_obj.name if user_obj else f"User {uid}"
        msg += f"**#{i} {name}**: `{total:,}` $\n"
    await ctx.send(msg)

@bot.command(name="nhapcode", aliases=["code"])
async def nhap_code(ctx, code: str = None):
    if not code:
        return await ctx.send("❌ Cú pháp: `!nhapcode BET88`")
    if code.upper() in ["BET88", "CASINO", "VIP"]:
        u = get_user(ctx.author.id)
        u["cash"] += 50000
        await ctx.send(f"🎁 **{ctx.author.name}** nhập code thành công, nhận `50,000` $!")
    else:
        await ctx.send("❌ Mã code không tồn tại!")

# --- GAME SOLO ---
@bot.command(name="tx", aliases=["taixiu"])
async def tai_xiu(ctx, lua_chon: str = None, bet: int = None):
    if not lua_chon or not bet or lua_chon.lower() not in ["tai", "xiu"] or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!tx [tai/xiu] [tiền_cược]`")
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền mặt!")
    
    d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
    tong = d1 + d2 + d3
    ket_qua = "tai" if tong >= 11 else "xiu"
    
    msg = f"🎲 Xúc xắc: `{d1}` - `{d2}` - `{d3}` $\rightarrow$ Tổng: **{tong}** ({ket_qua.upper()})\n"
    if lua_chon.lower() == ket_qua:
        u["cash"] += bet
        msg += f"🎉 **Thắng!** Nhận `+{bet:,}` $"
    else:
        u["cash"] -= bet
        msg += f"💸 **Thua!** Mất `-{bet:,}` $"
    await ctx.send(msg)

@bot.command(name="coinflip", aliases=["cf"])
async def coin_flip(ctx, lua_chon: str = None, bet: int = None):
    if not lua_chon or not bet or lua_chon.lower() not in ["ngua", "up"] or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!coinflip [ngua/up] [tiền_cược]`")
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền mặt!")
    
    kq = random.choice(["ngua", "up"])
    if lua_chon.lower() == kq:
        u["cash"] += bet
        await ctx.send(f"🪙 Ra **{kq.upper()}**! 🎉 Thắng `+{bet:,}` $!")
    else:
        u["cash"] -= bet
        await ctx.send(f"🪙 Ra **{kq.upper()}**! 💸 Thua `-{bet:,}` $!")

# 1. VÒNG QUAY !quay (HIỆU ỨNG RA TỪNG CÁI & TỶ LỆ TRÚNG 36%)
@bot.command(name="quay")
async def quay_so(ctx, bet: int = None):
    if not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!quay [tiền_cược]`")
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền mặt!")
    
    symbols = ["🍒", "🍋", "🔔", "💎", "7️⃣"]
    
    # Quyết định thắng hay thua theo tỷ lệ 36%
    is_win = random.random() < 0.36
    if is_win:
        # Nếu thắng: Chọn 2 hoặc 3 biểu tượng giống nhau
        if random.random() < 0.2: # 20% trong số thắng là Jackpot (3 con giống)
            sym = random.choice(symbols)
            r1, r2, r3 = sym, sym, sym
        else: # 80% trong số thắng là 2 con giống
            sym = random.choice(symbols)
            other = random.choice([s for s in symbols if s != sym])
            res_list = [sym, sym, other]
            random.shuffle(res_list)
            r1, r2, r3 = res_list
    else:
        # Nếu thua: 3 biểu tượng khác nhau hoàn toàn
        r1, r2, r3 = random.sample(symbols, 3)

    # Gửi tin nhắn ban đầu với hiệu ứng quay từng con
    msg = await ctx.send("🎰 Vòng quay: [ ❓ | ❓ | ❓ ]")
    await asyncio.sleep(1)
    
    await msg.edit(content=f"🎰 Vòng quay: [ {r1} | ❓ | ❓ ]")
    await asyncio.sleep(1)
    
    await msg.edit(content=f"🎰 Vòng quay: [ {r1} | {r2} | ❓ ]")
    await asyncio.sleep(1)

    cnt = Counter([r1, r2, r3])
    max_freq = max(cnt.values())
    
    if max_freq == 3:
        thuong = bet * 5
        u["cash"] += (thuong - bet)
        res_text = f"🎰 Vòng quay: [ {r1} | {r2} | {r3} ]\n🔥 **JACKPOT x5!** Nhận `+{thuong:,}` $"
    elif max_freq == 2:
        thuong = int(bet * 2)
        u["cash"] += (thuong - bet)
        res_text = f"🎰 Vòng quay: [ {r1} | {r2} | {r3} ]\n🎉 **Trúng 2 con (x2)!** Nhận `+{thuong:,}` $"
    else:
        u["cash"] -= bet
        res_text = f"🎰 Vòng quay: [ {r1} | {r2} | {r3} ]\n💸 **Chúc bạn may mắn lần sau!** Mất `-{bet:,}` $"
        
    await msg.edit(content=res_text)

# 2. BẦU CUA !bc
@bot.command(name="bc", aliases=["baucua"])
async def bau_cua(ctx, choice: str = None, bet: int = None):
    animals = {"bau": "🥒 Bầu", "cua": "🦀 Cua", "tom": "🦐 Tôm", "ca": "🐟 Cá", "ga": "🐓 Gà", "nai": "🦌 Nai"}
    if not choice or choice.lower() not in animals or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!bc [bau/cua/tom/ca/ga/nai] [tiền_cược]`")
    
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền mặt!")
    
    c = choice.lower()
    keys = list(animals.keys())
    d1, d2, d3 = random.choice(keys), random.choice(keys), random.choice(keys)
    
    matches = [d1, d2, d3].count(c)
    msg = f"🎲 Kết quả: **{animals[d1]} | {animals[d2]} | {animals[d3]}**\n"
    
    if matches == 3:
        win = int(bet * 2.5)
        u["cash"] += win
        msg += f"🔥 Trúng **3 con (x2,5)**! Nhận `+{win:,}` $!"
    elif matches == 2:
        win = int(bet * 2)
        u["cash"] += win
        msg += f"🎉 Trúng **2 con (x2)**! Nhận `+{win:,}` $!"
    elif matches == 1:
        win = int(bet * 1.5)
        u["cash"] += int(win)
        msg += f"✨ Trúng **1 con (x1,5)**! Nhận `+{win:,}` $!"
    else:
        u["cash"] -= bet
        msg += f"💸 Tróc vảy! Mất `-{bet:,}` $!"
    await ctx.send(msg)

# 3. XÓC ĐĨA !xd (GIAO DIỆN CHUẨN TỪNG BƯỚC NHƯ ẢNH)
@bot.command(name="xd", aliases=["xocdia"])
async def xoc_dia(ctx, choice: str = None, bet: int = None):
    if not choice or choice.lower() not in ["chan", "le"] or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!xd [chan/le] [tiền_cược]`")
    
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền mặt!")
    
    # Tạo Embed thông báo đang xóc đĩa
    embed_loading = discord.Embed(
        title="🪙 XÓC ĐĨA BET88",
        description="🍴 *Xóc... xóc... xóc...*",
        color=0xE67E22
    )
    msg = await ctx.send(embed=embed_loading)
    
    # Chờ 2 giây lắc đĩa (tránh bị đứng)
    await asyncio.sleep(2)
    
    dots = [random.choice([0, 1]) for _ in range(4)]
    red_count = sum(dots)
    ket_qua = "chan" if red_count % 2 == 0 else "le"
    
    board = "🔴" * red_count + "⚪" * (4 - red_count)
    
    if choice.lower() == ket_qua:
        u["cash"] += bet
        res_desc = f"皿 Bát mở: [ {board} ] (Đỏ: **{red_count}** $\rightarrow$ **{ket_qua.upper()}**)\n\n🎉 **Thắng!** Bạn nhận `+{bet:,}` $"
        color = 0x2ECC71
    else:
        u["cash"] -= bet
        res_desc = f"皿 Bát mở: [ {board} ] (Đỏ: **{red_count}** $\rightarrow$ **{ket_qua.upper()}**)\n\n💸 **Thua!** Bạn mất `-{bet:,}` $"
        color = 0xE74C3C

    embed_result = discord.Embed(
        title="🪙 XÓC ĐĨA BET88 - KẾT QUẢ",
        description=res_desc,
        color=color
    )
    await msg.edit(embed=embed_result)

# --- THÁCH ĐẤU PVP ---
@bot.command(name="thachdau", aliases=["danhbai"])
async def thach_dau(ctx, member: discord.Member = None, bet: int = None):
    if not member or member.id == ctx.author.id or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!thachdau @User [tiền_cược]`")
    
    u1 = get_user(ctx.author.id)
    u2 = get_user(member.id)
    
    if u1["cash"] < bet or u2["cash"] < bet:
        return await ctx.send("❌ Một trong hai người không đủ tiền mặt để thách đấu!")
    
    winner = random.choice([ctx.author, member])
    loser = member if winner == ctx.author else ctx.author
    
    get_user(winner.id)["cash"] += bet
    get_user(loser.id)["cash"] -= bet
    
    await ctx.send(
        f"⚔️ **QUYẾT ĐẤU PVP** ({bet:,} $)\n"
        f"🏆 **{winner.name}** chiến thắng và hốt `+{bet:,}` $ từ **{loser.name}**!"
    )

token = os.getenv("BOT_TOKEN")
bot.run(token)
    
