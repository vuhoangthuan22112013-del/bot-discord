import os
import asyncio
import random
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

# Tắt lệnh help mặc định của Discord để không bị đụng độ lỗi
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
        description="Chào mừng bạn đến với hệ thống giải trí!",
        color=0xFFD700
    )
    embed.add_field(
        name="⚔️ ĐỐI KHÁNG (PVP)",
        value="`!danhbai`, `!thachdau`, `!dagapvp`, `!tuxipvp @User`",
        inline=False
    )
    embed.add_field(
        name="🎲 CASINO (SOLO)",
        value="`!tx [tai/xiu] [tiền]`, `!daga`, `!tuxi`, `!bc`, `!xd`, `!bai`, `!rl`, `!quay`, `!duangua`, `!coinflip [ngua/up] [tiền]`",
        inline=False
    )
    embed.add_field(
        name="🏛️ HỆ THỐNG",
        value="`!vi`, `!gui [tiền]`, `!rut [tiền]`, `!chuyen @User [tiền]`, `!diemdanh`, `!bxh`, `!nhapcode [code]`",
        inline=False
    )
    embed.set_footer(text="Gõ !diemdanh để nhận xu miễn phí mỗi ngày!")
    await ctx.send(embed=embed)

# --- HỆ THỐNG VI / TÀI KHOẢN ---
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
        msg += f"🎉 **Thắng lớn!** Bạn nhận được `+{bet:,}` $"
    else:
        u["cash"] -= bet
        msg += f"💸 **Thua rồi!** Bạn mất `-{bet:,}` $"
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
        await ctx.send(f"🪙 Đồng xu ra **{kq.upper()}**! 🎉 Bạn thắng `+{bet:,}` $!")
    else:
        u["cash"] -= bet
        await ctx.send(f"🪙 Đồng xu ra **{kq.upper()}**! 💸 Bạn thua `-{bet:,}` $!")

@bot.command(name="daga", aliases=["bc", "xd", "bai", "rl", "quay", "duangua", "tuxi"])
async def game_funny(ctx):
    u = get_user(ctx.author.id)
    reward = random.choice([-2000, 5000, 10000, 20000])
    u["cash"] += reward
    if reward > 0:
        await ctx.send(f"🎮 **{ctx.author.name}** chơi minigame may mắn và thắng `+{reward:,}` $!")
    else:
        await ctx.send(f"🎮 **{ctx.author.name}** xui xẻo bị thua `-{abs(reward):,}` $!")

# --- ĐỐI KHÁNG PVP ---
@bot.command(name="danhbai", aliases=["thachdau", "dagapvp", "tuxipvp"])
async def pvp_game(ctx, member: discord.Member = None):
    if not member or member.id == ctx.author.id:
        return await ctx.send("❌ Bạn phải tag 1 người khác để chơi PVP! Ví dụ: `!danhbai @User`")
    
    win = random.choice([ctx.author, member])
    await ctx.send(f"⚔️ Trận quyết đấu gay cấn giữa **{ctx.author.name}** và **{member.name}**!\n🏆 Kết quả: **{win.name}** đã chiến thắng rực rỡ!")

# Kích hoạt Token an toàn
token = os.getenv("BOT_TOKEN")
bot.run(token)
                  
