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
            "last_daily": 0,
            "last_interest": time.time()
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
        name="🎲 TÀI XỈU PHIÊN (30S)",
        value="`!tx` : Mở phiên Tài Xỉu 30 giây\n`!dat [tai/xiu] [tiền]` : Đặt cược (chỉ 1 lần/phiên)",
        inline=False
    )
    embed.add_field(
        name="🎰 CASINO SOLO",
        value="`!coinflip [ngua/up] [tiền]`\n`!quay [tiền]`\n`!bc [bau/cua/tom/ca/ga/nai] [tiền]`\n`!xd [chan/le] [tiền]`\n`!thachdau @User [tiền]`",
        inline=False
    )
    embed.add_field(
        name="🏛️ HỆ THỐNG & NGÂN HÀNG",
        value="`!vi`, `!gui [tiền]`, `!rut [tiền]`, `!nhanlai`, `!chuyen @User [tiền]`, `!diemdanh`, `!bxh`, `!nhapcode [code]`",
        inline=False
    )
    embed.set_footer(text="Lãi ngân hàng 2%/ngày (!nhanlai) | Điểm danh 12h/lần!")
    await ctx.send(embed=embed)

# --- TÀI XỈU PHIÊN 30 GIÂY ---
@bot.command(name="tx", aliases=["taixiu"])
async def start_taixiu(ctx):
    global tx_session
    if tx_session["active"]:
        return await ctx.send(f"⏳ Phiên Tài Xỉu đang diễn ra! Còn **{tx_session['time_left']}s**. Nhanh tay gõ `!dat [tai/xiu] [tiền]`!")
    
    # Bắt đầu phiên mới
    tx_session["active"] = True
    tx_session["bets"] = {}
    tx_session["time_left"] = 30
    
    embed = discord.Embed(
        title="🎲 PHIÊN TÀI XỈU MỚI ĐÃ BẮT ĐẦU! (30 GIÂY)",
        description="Hãy cược bằng lệnh: `!dat [tai/xiu] [số_tiền]`\n*(Lưu ý: Mỗi người chỉ được đặt 1 lần trong phiên)*",
        color=0x3498DB
    )
    embed.set_footer(text="Thời gian còn lại: 30 giây")
    msg = await ctx.send(embed=embed)
    
    # Đếm ngược 30 giây
    for i in range(30, 0, -5):
        tx_session["time_left"] = i
        embed.set_footer(text=f"⏳ Thời gian còn lại: {i} giây...")
        await msg.edit(embed=embed)
        await asyncio.sleep(5)
    
    # Hết giờ -> Chốt phiên và quay số
    tx_session["active"] = False
    
    d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
    tong = d1 + d2 + d3
    ket_qua = "tai" if tong >= 11 else "xiu"
    
    res_embed = discord.Embed(
        title=f"🎲 KẾT QUẢ TÀI XỈU: {d1} - {d2} - {d3} ➔ Tổng: {tong} ({ket_qua.upper()})",
        color=0xE74C3C if ket_qua == "tai" else 0x2ECC71
    )
    
    if not tx_session["bets"]:
        res_embed.description = "❌ Không có ai tham gia đặt cược trong phiên này!"
    else:
        list_win = []
        list_lose = []
        for uid, data in tx_session["bets"].items():
            u = get_user(uid)
            choice = data["choice"]
            bet = data["bet"]
            name = data["name"]
            
            if choice == ket_qua:
                u["cash"] += bet
                list_win.append(f"🎉 **{name}**: +`{bet:,}` $ ({choice.upper()})")
            else:
                u["cash"] -= bet
                list_lose.append(f"💸 **{name}**: -`{bet:,}` $ ({choice.upper()})")
        
        desc = ""
        if list_win:
            desc += "**THẮNG CƯỢC:**\n" + "\n".join(list_win) + "\n\n"
        if list_lose:
            desc += "**THUA CƯỢC:**\n" + "\n".join(list_lose)
        res_embed.description = desc

    await ctx.send(embed=res_embed)

@bot.command(name="dat", aliases=["cuoc"])
async def dat_cuoc(ctx, choice: str = None, bet: int = None):
    global tx_session
    if not tx_session["active"]:
        return await ctx.send("❌ Hiện chưa có phiên Tài Xỉu nào! Gõ `!tx` để mở phiên mới.")
    
    uid = ctx.author.id
    if uid in tx_session["bets"]:
        return await ctx.send(f"❌ **{ctx.author.name}**, bạn đã đặt cược phiên này rồi (không được đặt 2 lần)!")
    
    if not choice or choice.lower() not in ["tai", "xiu"] or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp cược: `!dat [tai/xiu] [số_tiền]` (Ví dụ: `!dat tai 1000`)")
    
    u = get_user(uid)
    if u["cash"] < bet:
        return await ctx.send(f"❌ **{ctx.author.name}**, bạn không đủ tiền mặt (hiện có `{u['cash']:,}` $)! ")
    
    # Lưu cược
    tx_session["bets"][uid] = {
        "choice": choice.lower(),
        "bet": bet,
        "name": ctx.author.name
    }
    
    await ctx.send(f"✅ **{ctx.author.name}** đã cược thành công **{bet:,} $** vào **{choice.upper()}**!")

# --- HỆ THỐNG VÍ & NGÂN HÀNG ---
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

@bot.command(name="nhanlai", aliases=["lai"])
async def nhan_lai(ctx):
    u = get_user(ctx.author.id)
    if u["bank"] <= 0:
        return await ctx.send("❌ Bạn không có tiền trong ngân hàng để nhận lãi!")
    
    now = time.time()
    elapsed = now - u.get("last_interest", now)
    days = elapsed / 86400
    
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

@bot.command(name="diemdanh", aliases=["daily"])
async def diem_danh(ctx):
    u = get_user(ctx.author.id)
    now = time.time()
    cooldown = 12 * 3600
    
    if now - u["last_daily"] < cooldown:
        remaining = cooldown - (now - u["last_daily"])
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        return await ctx.send(f"⏳ **{ctx.author.name}**, bạn đã điểm danh rồi! Vui lòng quay lại sau **{hours} giờ {minutes} phút** nữa.")
    
    reward = random.randint(1000, 3000)
    u["cash"] += reward
    u["last_daily"] = now
    await ctx.send(f"🎉 **{ctx.author.name}** đã điểm danh thành công và nhận được `{reward:,}` $!")

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

# --- GAME SOLO KHÁC ---
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

@bot.command(name="quay")
async def quay_so(ctx, bet: int = None):
    if not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!quay [tiền_cược]`")
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền mặt!")
    
    symbols = ["🍒", "🍋", "🔔", "💎", "7️⃣"]
    is_win = random.random() < 0.36
    if is_win:
        if random.random() < 0.2:
            sym = random.choice(symbols)
            r1, r2, r3 = sym, sym, sym
        else:
            sym = random.choice(symbols)
            other = random.choice([s for s in symbols if s != sym])
            res_list = [sym, sym, other]
            random.shuffle(res_list)
            r1, r2, r3 = res_list
    else:
        r1, r2, r3 = random.sample(symbols, 3)

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

@bot.command(name="xd", aliases=["xocdia"])
async def xoc_dia(ctx, choice: str = None, bet: int = None):
    if not choice or choice.lower() not in ["chan", "le"] or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!xd [chan/le] [tiền_cược]`")
    
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền mặt!")
    
    embed_loading = discord.Embed(
        title="🪙 XÓC ĐĨA BET88",
        description="🍴 *Xóc... xóc... xóc...*",
        color=0xE67E22
    )
    msg = await ctx.send(embed=embed_loading)
    await asyncio.sleep(2)
    
    dots = [random.choice([0, 1]) for _ in range(4)]
    red_count = sum(dots)
    ket_qua = "chan" if red_count % 2 == 0 else "le"
    
    board = "🔴" * red_count + "⚪" * (4 - red_count)
    
    if choice.lower() == ket_qua:
        u["cash"] += bet
        res_desc = f"皿 Bát mở: [ {board} ] (Đỏ: **{red_count}** ➔ **{ket_qua.upper()}**)\n\n🎉 **Thắng!** Bạn nhận `+{bet:,}` $"
        color = 0x2ECC71
    else:
        u["cash"] -= bet
        res_desc = f"皿 Bát mở: [ {board} ] (Đỏ: **{red_count}** ➔ **{ket_qua.upper()}**)\n\n💸 **Thua!** Bạn mất `-{bet:,}` $"
        color = 0xE74C3C

    embed_result = discord.Embed(
        title="🪙 XÓC ĐĨA BET88 - KẾT QUẢ",
        description=res_desc,
        color=color
    )
    await msg.edit(embed=embed_result)

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
    
