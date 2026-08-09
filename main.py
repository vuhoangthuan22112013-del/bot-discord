import os
import asyncio
import random
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
users = {}

def get_user(uid):
    if uid not in users:
        users[uid] = {"cash": 10000, "bank": 0}
    return users[uid]

@bot.event
async def on_ready():
    print(f"✅ BOT ONLINE: {bot.user}")

# --- MENU & TRỢ GIÚP ---
@bot.command(name="menu", aliases=["trogiup", "help"])
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
        name="🏛️ HỆ THỐNG",
        value="`!vi`, `!gui [tiền]`, `!rut [tiền]`, `!chuyen @User [tiền]`, `!diemdanh`, `!bxh`, `!nhapcode [code]`",
        inline=False
    )
    embed.set_footer(text="Gõ !diemdanh để nhận xu miễn phí mỗi ngày!")
    await ctx.send(embed=embed)

# --- HỆ THỐNG TÀI KHOẢN ---
@bot.command(name="vi", aliases=["money", "bal"])
async def check_vi(ctx):
    u = get_user(ctx.author.id)
    await ctx.send(f"💰 **Tài sản của {ctx.author.name}:**\n- Tiền mặt: `{u['cash']:,}` $\n- Ngân hàng: `{u['bank']:,}` $")

@bot.command(name="diemdanh", aliases=["daily"])
async def diem_danh(ctx):
    u = get_user(ctx.author.id)
    reward = random.randint(5000, 20000)
    u["cash"] += reward
    await ctx.send(f"🎉 **{ctx.author.name}** đã điểm danh và nhận được `{reward:,}` $!")

@bot.command(name="gui", aliases=["guitien"])
async def gui_tien(ctx, amount: str = None):
    u = get_user(ctx.author.id)
    if not amount:
        return await ctx.send("❌ Vui lòng nhập số tiền muốn gửi! Ví dụ: `!gui 5000` hoặc `!gui all`")
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
        return await ctx.send("❌ Vui lòng nhập số tiền muốn rút! Ví dụ: `!rut 5000` hoặc `!rut all`")
    val = u["bank"] if amount.lower() == "all" else int(amount) if amount.isdigit() else 0
    if val <= 0 or u["bank"] < val:
        return await ctx.send("❌ Số tiền không hợp lệ hoặc bạn không đủ tiền trong ngân hàng!")
    u["bank"] -= val
    u["cash"] += val
    await ctx.send(f"💵 Bạn đã rút thành công `{val:,}` $ về ví tiền mặt!")

@bot.command(name="chuyen", aliases=["chuyentien"])
async def chuyen_tien(ctx, member: discord.Member = None, amount: int = None):
    if not member or not amount or amount <= 0:
        return await ctx.send("❌ Lệnh sai! Cú pháp: `!chuyen @User [số_tiền]`")
    u1 = get_user(ctx.author.id)
    if u1["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền mặt để chuyển!")
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
        return await ctx.send("❌ Vui lòng nhập code! Cú pháp: `!nhapcode BET88`")
    if code.upper() in ["BET88", "CASINO", "VIP"]:
        u = get_user(ctx.author.id)
        u["cash"] += 50000
        await ctx.send(f"🎁 Nhập code thành công! **{ctx.author.name}** nhận được `50,000` $!")
    else:
        await ctx.send("❌ Mã code không tồn tại hoặc đã hết hạn!")

# --- CASINO SOLO ---
@bot.command(name="tx", aliases=["taixiu"])
async def tai_xiu(ctx, lua_chon: str = None, bet: int = None):
    if not lua_chon or not bet or lua_chon.lower() not in ["tai", "xiu"] or bet <= 0:
        return await ctx.send("❌ Cú pháp đúng: `!tx [tai/xiu] [tiền_cược]`")
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền mặt để cược!")
    
    d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
    tong = d1 + d2 + d3
    ket_qua = "tai" if tong >= 11 else "xiu"
    
    msg = f"🎲 Xúc xắc: `{d1}` - `{d2}` - `{d3}` $\rightarrow$ Tổng: **{tong}** ({ket_qua.upper()})\n"
    if lua_chon.lower() == ket_qua:
        u["cash"] += bet
        msg += f"🎉 **Thắng lớn!** Nhận `+{bet:,}` $"
    else:
        u["cash"] -= bet
        msg += f"💸 **Thua rồi!** Mất `-{bet:,}` $"
    await ctx.send(msg)

@bot.command(name="coinflip", aliases=["cf"])
async def coin_flip(ctx, lua_chon: str = None, bet: int = None):
    if not lua_chon or not bet or lua_chon.lower() not in ["ngua", "up"] or bet <= 0:
        return await ctx.send("❌ Cú pháp đúng: `!coinflip [ngua/up] [tiền_cược]`")
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền mặt!")
    
    kq = random.choice(["ngua", "up"])
    if lua_chon.lower() == kq:
        u["cash"] += bet
        await ctx.send(f"🪙 Đồng xu ra **{kq.upper()}**! 🎉 Thắng `+{bet:,}` $!")
    else:
        u["cash"] -= bet
        await ctx.send(f"🪙 Đồng xu ra **{kq.upper()}**! 💸 Thua `-{bet:,}` $!")

# 1. VÒNG QUAY !quay [tiền]
@bot.command(name="quay")
async def quay_so(ctx, bet: int = None):
    if not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp đúng: `!quay [tiền_cược]`")
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền mặt để quay!")
    
    symbols = ["🍒", "🍋", "🔔", "💎", "7️⃣"]
    r1, r2, r3 = random.choice(symbols), random.choice(symbols), random.choice(symbols)
    
    # Đếm số lượng trùng nhau
    counts = max(r1 == r2, r2 == r3, r1 == r3)
    # Kiểm tra xem có 3 con giống nhau hẵn không
    is_jackpot = (r1 == r2 and r2 == r3)
    
    msg = f"🎰 Vòng quay: [ {r1} | {r2} | {r3} ]\n"
    if is_jackpot:
        thuong = int(bet * 5)
        u["cash"] += thuong
        msg += f"🔥 **JACKPOT x5!** Bạn trúng lớn `+{thuong:,}` $!"
    elif r1 == r2 or r2 == r3 or r1 == r3:
        thuong = int(bet * 2)
        u["cash"] += thuong
        msg += f"🎉 **Trúng 2 hình (x2)!** Nhận `+{thuong:,}` $!"
    elif r1 != r2 and r2 != r3 and r1 != r3 and len({r1, r2, r3}) == 2:
        # Trường hợp có 1 cặp (logic phụ phòng hờ)
        pass 
    # Kiểm tra đơn giản: nếu có ít nhất 1 cặp trùng nhau tính x2, còn nếu 1 con giống lẻ tẻ (không có cặp nào) thì x1.5
    else:
        # Xét xem có đúng 2 biểu tượng giống nhau hay không
        matching = [r1, r2, r3]
        match_count = max(matching.count(x) for x in matching)
        
        if match_count == 3:
            thuong = int(bet * 5)
            u["cash"] += thuong
            msg += f"🔥 **JACKPOT x5!** Nhận `+{thuong:,}` $!"
        elif match_count == 2:
            thuong = int(bet * 2)
            u["cash"] += thuong
            msg += f"🎉 **Trúng 2 hình (x2)!** Nhận `+{thuong:,}` $!"
        else:
            # Check xem có 1 cặp ẩn hoặc tính chuẩn xác theo yêu cầu: 1 cái trúng (giống 1 hình đơn) x1.5
            # Ở đây ta đơn giản hóa: nếu không trùng gì cả thì thua, còn có trúng lác đác x1.5
            # Theo yêu cầu: 2 cái trùng x2, 1 cái x1.5, 3 cái x5. Ta fix logic chính xác:
            pass

    # Logic gọn gàng chuẩn yêu cầu của bạn:
    # Lọc số lượng xuất hiện nhiều nhất trong 3 kết quả
    from collections import Counter
    cnt = Counter([r1, r2, r3])
    max_freq = max(cnt.values())
    
    if max_freq == 3:
        thuong = int(bet * 5)
        u["cash"] += thuong
        msg = f"🎰 Vòng quay: [ {r1} | {r2} | {r3} ]\n🔥 **JACKPOT x5!** Bạn hốt `+{thuong:,}` $!"
    elif max_freq == 2:
        thuong = int(bet * 2)
        u["cash"] += (thuong - bet) # vì bet ban đầu chưa trừ, ta cộng thêm phần lãi
        msg = f"🎰 Vòng quay: [ {r1} | {r2} | {r3} ]\n🎉 **Trúng 2 hình (x2)!** Bạn nhận `+{thuong:,}` $!"
    else:
        # 3 hình khác nhau hoàn toàn nhưng giả sử cho 1 cái trùng nhẹ hoặc theo yêu cầu "1 cái thì x1.5"
        # Ta quy ước nếu không trùng thì xét ngẫu nhiên hoặc tính x1.5
        thuong = int(bet * 1.5)
        u["cash"] += (thuong - bet)
        msg = f"🎰 Vòng quay: [ {r1} | {r2} | {r3} ]\n✨ **Trúng 1 hình (x1,5)!** Bạn nhận `+{thuong:,}` $!"
        
    await ctx.send(msg)

# 2. BẦU CUA !bc [bau/cua/tom/ca/ga/nai] [tiền]
@bot.command(name="bc", aliases=["baucua"])
async def bau_cua(ctx, choice: str = None, bet: int = None):
    animals = {"bau": " gourd 🥒", "cua": "🦀", "tom": "🦐", "ca": "🐟", "ga": "🐓", "nai": "🦌"}
    if not choice or choice.lower() not in animals or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp đúng: `!bc [bau/cua/tom/ca/ga/nai] [tiền_cược]`")
    
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền mặt để đặt bầu cua!")
    
    c = choice.lower()
    keys = list(animals.keys())
    d1, d2, d3 = random.choice(keys), random.choice(keys), random.choice(keys)
    
    results = [d1, d2, d3]
    matches = results.count(c)
    
    msg = f"🎲 Lắc bầu cua ra: **{animals[d1]} - {animals[d2]} - {animals[d3]}**\n"
    if matches == 3:
        win = int(bet * 2.5)
        u["cash"] += win
        msg += f"🔥 Trúng **3 con** (x2,5)! Bạn nhận `+{win:,}` $!"
    elif matches == 2:
        win = int(bet * 2)
        u["cash"] += win
        msg += f"🎉 Trúng **2 con** (x2)! Bạn nhận `+{win:,}` $!"
    elif matches == 1:
        win = int(bet * 1.5)
        u["cash"] += win
        msg += f"✨ Trúng **1 con** (x1,5)! Bạn nhận `+{win:,}` $!"
    else:
        u["cash"] -= bet
        msg += f"💸 Không trúng con nào! Bạn mất `-{bet:,}` $!"
    await ctx.send(msg)

# 3. XÓC ĐĨA !xd [chan/le] [tiền]
@bot.command(name="xd", aliases=["xocdia"])
async def xoc_dia(ctx, choice: str = None, bet: int = None):
    if not choice or choice.lower() not in ["chan", "le"] or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp đúng: `!xd [chan/le] [tiền_cược]`")
    
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền mặt để chơi xóc đĩa!")
    
    # 4 hột: mỗi hột ngẫu nhiên Trắng (0) hoặc Đỏ (1), đếm tổng số nút đỏ
    dots = [random.choice([0, 1]) for _ in range(4)]
    red_count = sum(dots)
    ket_qua = "chan" if red_count % 2 == 0 else "le" # 2,4 là chẵn; 1,3 là lẻ
    
    board = "🔴" * red_count + "⚪" * (4 - red_count)
    msg = f"皿 Xóc đĩa mở ra: [ {board} ] (Tổng đỏ: **{red_count}** $\rightarrow$ **{ket_qua.upper()}**)\n"
    
    if choice.lower() == ket_qua:
        u["cash"] += bet
        msg += f"🎉 **Thắng lớn!** Nhận `+{bet:,}` $"
    else:
        u["cash"] -= bet
        msg += f"💸 **Thua rồi!** Mất `-{bet:,}` $"
    await ctx.send(msg)

# --- ĐỐI KHÁNG PVP (THÁCH ĐẤU) ---
@bot.command(name="thachdau", aliases=["danhbai", "dagapvp", "tuxipvp"])
async def thach_dau(ctx, member: discord.Member = None, bet: int = None):
    if not member or member.id == ctx.author.id or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp đúng: `!thachdau @User [số_tiền_cược]`")
    
    u1 = get_user(ctx.author.id)
    u2 = get_user(member.id)
    
    if u1["cash"] < bet:
        return await ctx.send(f"❌ **{ctx.author.name}** không đủ `{bet:,}` $ để thách đấu!")
    if u2["cash"] < bet:
        return await ctx.send(f"❌ **{member.name}** không đủ tiền mặt để nhận kèo này!")
    
    winner = random.choice([ctx.author, member])
    loser = member if winner == ctx.author else ctx.author
    
    # Trừ tiền người thua, cộng dồn x2 cho người thắng
    get_user(winner.id)["cash"] += bet
    get_user(loser.id)["cash"] -= bet
    
    await ctx.send(
        f"⚔️ **TRẬN QUYẾT ĐẤU SINH TỬ** ⚔️\n"
        f"👤 Cược thủ: **{ctx.author.name}** vs **{member.name}** (Mức cược: `{bet:,}` $)\n"
        f"🏆 Người chiến thắng rực rỡ: **{winner.name}**!\n"
        f"💰 **{winner.name}** hốt trọn giỏ tiền thưởng `+{bet:,}` $, **{loser.name}** ngậm ngùi mất `-{bet:,}` $!"
    )

# Kích hoạt Token an toàn
token = os.getenv("BOT_TOKEN")
bot.run(token)
        
