import os, random, asyncio, json, time, discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

FILE = "data.json"
START = 2000
users = {}
TX = {"on": False, "bets": {}}
loans = {}

def load():
    global users, loans
    try:
        with open(FILE, "r", encoding="utf8") as f:
            x = json.load(f)
            users, loans = x.get("users", {}), x.get("loans", {})
    except:
        users, loans = {}, {}

def save():
    with open(FILE, "w", encoding="utf8") as f:
        json.dump({"users": users, "loans": loans}, f)

def U(m):
    i = str(m.id)
    if i not in users:
        users[i] = {"cash": START, "bank": 0, "role": "Không có", "day": ""}
    return users[i]

def money(n):
    return f"{int(n):,}$"

def E(title, text, color=0x3498DB):
    return discord.Embed(title=title, description=text, color=color)

def admin(ctx):
    return ctx.author.guild_permissions.administrator

load()

# ================= READY =================

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino")
    )
    print("BOT ONLINE:", bot.user)

# ================= HELP =================

@bot.command(name="trogiup")
async def help_cmd(ctx):
    await ctx.send(embed=E(
        "🎰 CASINO BET88",
        "━━━━━━━━━━━━━━━━━━\n"
        "🎲 **TÀI XỈU**\n"
        "`!tx tai 1000` • `!tx xiu 1000`\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🎯 **BẦU CUA**\n"
        "`!bc cua 1000`\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🪙 **XÓC ĐĨA**\n"
        "`!xd chan 1000` • `!xd le 1000`\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🎰 **SLOT**\n"
        "`!quay 1000`\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💰 **TÀI KHOẢN**\n"
        "`!vi` `!gui 1000` `!rut 1000`\n"
        "`!chuyen @user 1000`\n"
        "`!vay 1000` `!trano 1000`\n"
        "`!diemdanh` `!bxh`\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🛒 **ROLE**\n"
        "`!cuahang` `!muan vip`\n"
        "`!muan daigia` `!muan typhu`\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "👑 **ADMIN**\n"
        "`!kick @user`\n"
        "`!ban @user`\n"
        "`!khoamom @user`\n"
        "`!reset tien @user`\n"
        "`!taocode số_tiền số_lượt`\n"
        "━━━━━━━━━━━━━━━━━━",
        0x5865F2
    ))

# ================= VÍ =================

@bot.command(name="vi")
async def vi(ctx):
    u = U(ctx.author)
    await ctx.send(embed=E(
        f"💳 VÍ CỦA {ctx.author.display_name}",
        f"💵 Tiền mặt: **{money(u['cash'])}**\n"
        f"🏦 Ngân hàng: **{money(u['bank'])}**\n"
        f"👑 Role: **{u['role']}**",
        0x3498DB
    ))

# ================= NGÂN HÀNG =================

@bot.command(name="gui")
async def gui(ctx, amount: int = 0):
    u = U(ctx.author)
    if amount <= 0 or amount > u["cash"]:
        return await ctx.send("❌ Số tiền không hợp lệ hoặc không đủ tiền.")
    u["cash"] -= amount
    u["bank"] += amount
    save()
    await ctx.send(embed=E(
        "🏦 GỬI NGÂN HÀNG",
        f"Đã gửi **{money(amount)}**.\n"
        f"🏦 Số dư: **{money(u['bank'])}**",
        0x2ECC71
    ))

@bot.command(name="rut")
async def rut(ctx, amount: int = 0):
    u = U(ctx.author)
    if amount <= 0 or amount > u["bank"]:
        return await ctx.send("❌ Số tiền không hợp lệ hoặc ngân hàng không đủ.")
    u["bank"] -= amount
    u["cash"] += amount
    save()
    await ctx.send(embed=E(
        "💵 RÚT TIỀN",
        f"Bạn đã rút **{money(amount)}**.",
        0x2ECC71
    ))

# ================= CHUYỂN =================

@bot.command(name="chuyen")
async def chuyen(ctx, member: discord.Member = None, amount: int = 0):
    if not member or amount < 1 or amount > 10000000:
        return await ctx.send("❌ `!chuyen @user 1-10000000`")
    if member.id == ctx.author.id:
        return await ctx.send("❌ Không thể chuyển cho chính mình.")
    a, b = U(ctx.author), U(member)
    if a["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền.")
    a["cash"] -= amount
    b["cash"] += amount
    save()
    await ctx.send(embed=E(
        "💸 CHUYỂN TIỀN",
        f"{ctx.author.mention} → {member.mention}\n"
        f"💰 **{money(amount)}**",
        0x2ECC71
    ))

# ================= ĐIỂM DANH =================

@bot.command(name="diemdanh")
async def diemdanh(ctx):
    u = U(ctx.author)
    today = time.strftime("%Y-%m-%d")
    if u["day"] == today:
        return await ctx.send("❌ Hôm nay bạn đã điểm danh rồi.")
    reward = random.randint(1000, 3000)
    u["cash"] += reward
    u["day"] = today
    save()
    await ctx.send(embed=E(
        "🎁 ĐIỂM DANH HÀNG NGÀY",
        f"🎉 {ctx.author.mention}\n"
        f"💰 Nhận được **{money(reward)}**!",
        0x2ECC71
    ))

# ================= BXH =================

@bot.command(name="bxh")
async def bxh(ctx):
    arr = []
    for uid, u in users.items():
        total = u["cash"] + u["bank"]
        member = ctx.guild.get_member(int(uid))
        name = member.display_name if member else "Người chơi"
        arr.append((total, name))
    arr.sort(reverse=True)

    text = ""
    for i, (money_total, name) in enumerate(arr[:5], 1):
        text += f"**{i}.** {name} — 💰 **{money(money_total)}**\n"

    await ctx.send(embed=E(
        "🏆 TOP 5 GIÀU NHẤT",
        text or "Chưa có dữ liệu.",
        0xF1C40F
    ))

# ================= VAY =================

@bot.command(name="vay")
async def vay(ctx, amount: int = 0):
    if amount < 1000 or amount > 50000:
        return await ctx.send("❌ Chỉ được vay từ **1.000$ đến 50.000$**.")

    uid = str(ctx.author.id)
    u = U(ctx.author)

    if uid in loans:
        return await ctx.send("❌ Bạn đang có khoản vay chưa trả.")

    loans[uid] = {
        "amount": amount,
        "time": time.time()
    }
    u["cash"] += amount
    save()

    await ctx.send(embed=E(
        "🏦 KHOẢN VAY",
        f"💰 Bạn đã vay **{money(amount)}**.\n\n"
        "⏰ Thời hạn: **1 giờ**.\n"
        "⚠️ Sau 1 giờ chưa trả sẽ thành **CON NỢ** "
        "và không được chơi.",
        0xF39C12
    ))

    await asyncio.sleep(3600)

    if uid in loans:
        u = U(ctx.author)
        u["role"] = "Con Nợ"
        save()

@bot.command(name="trano")
async def trano(ctx, amount: int = 0):
    uid = str(ctx.author.id)

    if uid not in loans:
        return await ctx.send("❌ Bạn không có khoản vay.")

    debt = loans[uid]["amount"]
    if amount != debt:
        return await ctx.send(f"❌ Bạn phải trả đúng **{money(debt)}**.")

    u = U(ctx.author)
    if u["cash"] < debt:
        return await ctx.send("❌ Bạn không đủ tiền trả nợ.")

    u["cash"] -= debt
    if u["role"] == "Con Nợ":
        u["role"] = "Không có"

    del loans[uid]
    save()

    await ctx.send(embed=E(
        "✅ ĐÃ TRẢ NỢ",
        f"{ctx.author.mention} đã trả đủ **{money(debt)}**.\n"
        "🎉 Bạn đã được phép chơi lại.",
        0x2ECC71
    ))

# ================= CHECK NỢ =================

def no_debt(ctx):
    uid = str(ctx.author.id)
    u = U(ctx.author)
    return uid not in loans and u["role"] != "Con Nợ"

# ================= SLOT =================

@bot.command(name="quay")
async def quay(ctx, amount: int = 0):
    if amount <= 0:
        return await ctx.send("❌ `!quay số_tiền`")
    if not no_debt(ctx):
        return await ctx.send("🚫 Bạn đang là **CON NỢ**, hãy trả nợ trước.")
    u = U(ctx.author)
    if amount > u["cash"]:
        return await ctx.send("❌ Không đủ tiền.")

    u["cash"] -= amount
    icons = ["🍒", "🍋", "🔔", "⭐", "💎"]
    a, b, c = [random.choice(icons) for _ in range(3)]

    msg = await ctx.send(embed=E(
        "🎰 SLOT",
        "🟧  ▫️   ▫️   ▫️\n\n"
        "🎰 **ĐANG QUAY...**",
        0xF39C12
    ))

    await asyncio.sleep(.7)
    await msg.edit(embed=E(
        "🎰 SLOT",
        f"🟧  **{a}   ▫️   ▫️**\n\n"
        "🎰 **ĐANG QUAY...**",
        0xF39C12
    ))

    await asyncio.sleep(.7)
    await msg.edit(embed=E(
        "🎰 SLOT",
        f"🟧  **{a}   {b}   ▫️**\n\n"
        "🎰 **ĐANG QUAY...**",
        0xF39C12
    ))

    await asyncio.sleep(.7)

    if a == b == c:
        reward = amount * 5
        u["cash"] += reward
        result = f"🟢 **JACKPOT x5!**\n💰 Nhận **{money(reward)}**"
        color = 0x2ECC71
    elif a == b or a == c or b == c:
        reward = int(amount * 1.5)
        u["cash"] += reward
        result = f"🟢 **2 HÌNH GIỐNG NHAU x1.5!**\n💰 Nhận **{money(reward)}**"
        color = 0x2ECC71
    else:
        result = f"🔴 **THUA!**\n💸 Mất **{money(amount)}**"
        color = 0xE74C3C

    save()
    await msg.edit(embed=E(
        "🎰 SLOT",
        f"╔══════════════╗\n"
        f"║   **{a}  {b}  {c}**   ║\n"
        f"╚══════════════╝\n\n{result}",
        color
    ))

# ================= BẦU CUA =================

@bot.command(name="bc")
async def bc(ctx, choice: str = None, amount: int = 0):
    icons = {
        "ca": "🐟", "tom": "🦐", "cua": "🦀",
        "bau": "🥒", "ga": "🐓", "nai": "🦌"
    }

    if choice not in icons or amount <= 0:
        return await ctx.send("❌ `!bc ca/tom/cua/bau/ga/nai số_tiền`")
    if not no_debt(ctx):
        return await ctx.send("🚫 Bạn đang là **CON NỢ**, hãy trả nợ trước.")

    u = U(ctx.author)
    if amount > u["cash"]:
        return await ctx.send("❌ Không đủ tiền.")

    u["cash"] -= amount
    result = [random.choice(list(icons)) for _ in range(3)]

    msg = await ctx.send(embed=E(
        "🎲 BẦU CUA",
        "╔══════════════╗\n"
        "║  🟨   🟨   🟨  ║\n"
        "╚══════════════╝\n\n"
        "🎲 **ĐANG LẮC...**",
        0xF39C12
    ))

    await asyncio.sleep(1)

    shown = "   ".join(icons[x] for x in result)

    count = result.count(choice)

    if count:
        reward = amount * (count + 1)
        u["cash"] += reward
        text = f"🟢 **TRÚNG {count} LẦN! x{count+1}**\n💰 Nhận **{money(reward)}**"
        color = 0x2ECC71
    else:
        text = f"🔴 **THUA!**\n💸 Mất **{money(amount)}**"
        color = 0xE74C3C

    save()

    await msg.edit(embed=E(
        "🎲 BẦU CUA",
        f"╔══════════════════╗\n"
        f"║  **{shown}**  ║\n"
        f"╚══════════════════╝\n\n"
        f"🎯 Cửa: **{icons[choice]} {choice.upper()}**\n\n"
        f"{text}",
        color
    ))

# ================= XÓC ĐĨA =================

@bot.command(name="xd")
async def xd(ctx, choice: str = None, amount: int = 0):
    if choice not in ["chan", "le"] or amount <= 0:
        return await ctx.send("❌ `!xd chan 1000` hoặc `!xd le 1000`")
    if not no_debt(ctx):
        return await ctx.send("🚫 Bạn đang là **CON NỢ**.")

    u = U(ctx.author)
    if amount > u["cash"]:
        return await ctx.send("❌ Không đủ tiền.")

    u["cash"] -= amount

    msg = await ctx.send(embed=E(
        "🪙 XÓC ĐĨA",
        "🟧 **Xóc... Xóc... Xóc...**",
        0xF39C12
    ))

    await asyncio.sleep(2)

    balls = [random.randint(0, 1) for _ in range(4)]
    red = sum(balls)
    result = "chan" if red % 2 == 0 else "le"
    win = choice == result

    board = " ".join("🔴" if x else "⚪" for x in balls)

    if win:
        u["cash"] += amount * 2
        text = f"🟢 **THẮNG x2!**\n💰 Nhận **{money(amount*2)}**"
        color = 0x2ECC71
    else:
        text = f"🔴 **THUA!**\n💸 Mất **{money(amount)}**"
        color = 0xE74C3C

    save()

    await msg.edit(embed=E(
        "🪙 XÓC ĐĨA",
        f"╔══════════════╗\n"
        f"║  **{board}**  ║\n"
        f"╚══════════════╝\n\n"
        f"🎯 Kết quả: **{result.upper()}**\n"
        f"🔴 Số đỏ: **{red}**\n\n{text}",
        color
    ))

# ================= TÀI XỈU =================

@bot.command(name="tx")
async def tx(ctx, choice: str = None, amount: int = 0):
    global TX

    if choice not in ["tai", "xiu"]:
        return await ctx.send("❌ `!tx tai 1000` hoặc `!tx xiu 1000`")
    if amount < 100 or amount > 10000000:
        return await ctx.send("❌ Cược từ **100$ → 10.000.000$**.")
    if not no_debt(ctx):
        return await ctx.send("🚫 Bạn đang là **CON NỢ**.")

    u = U(ctx.author)
    if u["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền.")

    if ctx.author.id in TX["bets"]:
        return await ctx.send("❌ Bạn đã cược trong phiên này.")

    if not TX["on"]:
        TX["on"] = True
        TX["bets"] = {}
        msg = await ctx.send(embed=E(
            "🎲 TÀI XỈU",
            "🟠 **ĐANG NHẬN CƯỢC**\n\n"
            "⏱️ **30 GIÂY**\n"
            "👥 Người chơi: **0**",
            0xF39C12
        ))
        TX["msg"] = msg

        asyncio.create_task(tx_end(msg))

    u["cash"] -= amount
    TX["bets"][ctx.author.id] = {
        "choice": choice,
        "amount": amount,
        "name": ctx.author.display_name
    }
    save()

    await ctx.send(f"✅ {ctx.author.mention} cược **{money(amount)} {choice.upper()}**.")

async def tx_end(msg):
    await asyncio.sleep(30)

    if not TX["on"]:
        return

    d = [random.randint(1, 6) for _ in range(3)]
    total = sum(d)
    result = "tai" if total >= 11 else "xiu"

    text = (
        f"🎲 **{d[0]} • {d[1]} • {d[2]}**\n\n"
        f"💥 Tổng: **{total}**\n"
        f"🎯 Kết quả: **{result.upper()}**\n\n"
    )

    for uid, bet in TX["bets"].items():
        if bet["choice"] == result:
            reward = bet["amount"] * 2
            users[str(uid)]["cash"] += reward
            text += f"🟢 {bet['name']} +**{money(reward)}**\n"
        else:
            text += f"🔴 {bet['name']} -**{money(bet['amount'])}**\n"

    TX["on"] = False
    TX["bets"] = {}
    save()

    await msg.edit(embed=E("🎲 KẾT QUẢ TÀI XỈU", text, 0x2ECC71))

# ================= SHOP =================

@bot.command(name="cuahang")
async def shop(ctx):
    await ctx.send(embed=E(
        "🛒 CỬA HÀNG ROLE",
        "💛 **VIP** — 10.000.000$\n"
        "`!muan vip`\n\n"
        "💙 **ĐẠI GIA** — 5.000.000$\n"
        "`!muan daigia`\n\n"
        "💜 **TỶ PHÚ** — 1.000.000.000$\n"
        "`!muan typhu`",
        0xF1C40F
    ))

@bot.command(name="muan")
async def muan(ctx, name: str = None):
    price = {
        "vip": 10000000,
        "daigia": 5000000,
        "typhu": 1000000000
    }
    role_name = {
        "vip": "VIP",
        "daigia": "Đại Gia",
        "typhu": "Tỷ Phú"
    }

    if name not in price:
        return await ctx.send("❌ `!muan vip/daigia/typhu`")

    u = U(ctx.author)
    if u["cash"] < price[name]:
        return await ctx.send("❌ Không đủ tiền.")

    role = discord.utils.get(ctx.guild.roles, name=role_name[name])
    if not role:
        return await ctx.send(f"❌ Chưa có role **{role_name[name]}**.")

    if role >= ctx.guild.me.top_role:
        return await ctx.send("❌ Role cao hơn role của bot.")

    u["cash"] -= price[name]
    u["role"] = role_name[name]
    await ctx.author.add_roles(role)
    save()

    await ctx.send(embed=E(
        "👑 MUA ROLE THÀNH CÔNG",
        f"🎉 {ctx.author.mention}\n"
        f"Role: **{role_name[name]}**\n"
        f"Giá: **{money(price[name])}**",
        0x2ECC71
    ))

# ================= ADMIN =================

@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None):
    if not member:
        return await ctx.send("❌ `!kick @user`")
    await member.kick(reason=f"Kick bởi {ctx.author}")
    await ctx.send(f"👢 Đã kick {member.mention}.")

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None):
    if not member:
        return await ctx.send("❌ `!ban @user`")
    await member.ban(reason=f"Ban bởi {ctx.author}")
    await ctx.send(f"🔨 Đã ban {member.mention}.")

@bot.command(name="khoamom")
@commands.has_permissions(manage_messages=True)
async def khoamom(ctx, member: discord.Member = None):
    if not member:
        return await ctx.send("❌ `!khoamom @user`")

    overwrite = ctx.channel.overwrites_for(member)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(member, overwrite=overwrite)
    await ctx.send(f"🔇 Đã khóa chat của {member.mention} trong kênh này.")

@bot.command(name="reset")
@commands.has_permissions(administrator=True)
async def reset(ctx, kind: str = None, member: discord.Member = None):
    if kind != "tien" or not member:
        return await ctx.send("❌ `!reset tien @user`")

    u = U(member)
    u["cash"] = START
    u["bank"] = 0
    save()

    await ctx.send(
        f"♻️ Đã reset tiền của {member.mention} về **{money(START)}**."
    )

@bot.command(name="taocode")
@commands.has_permissions(administrator=True)
async def taocode(ctx, amount: int = 0, uses: int = 0):
    if amount <= 0 or uses <= 0:
        return await ctx.send("❌ `!taocode số_tiền số_lượt`")

    code = "BET" + str(random.randint(100000, 999999))

    try:
        await ctx.author.send(embed=E(
            "🎁 CODE TIỀN",
            f"🔑 Code: **`{code}`**\n"
            f"💰 Giá trị: **{money(amount)}**\n"
            f"🔢 Lượt dùng: **{uses}**",
            0xF1C40F
        ))
        await ctx.send("✅ Code đã được gửi riêng vào DM của bạn.")
    except:
        await ctx.send("❌ Không thể gửi DM cho bạn.")

# ================= ERROR =================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        return await ctx.send("❌ Bạn không có quyền dùng lệnh này.")
    if isinstance(error, commands.MemberNotFound):
        return await ctx.send("❌ Không tìm thấy người chơi.")
    if isinstance(error, commands.BadArgument):
        return await ctx.send("❌ Sai cú pháp lệnh.")
    if isinstance(error, commands.CommandNotFound):
        return
    print("ERROR:", error)

# ================= TOKEN =================

TOKEN = os.getenv("TOKEN_BOT")

if not TOKEN:
    print("❌ Chưa có TOKEN_BOT trong Environment Variables!")
else:
    bot.run(TOKEN)
