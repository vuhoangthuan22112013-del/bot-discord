import os, random, asyncio, discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

users = {}
TX = {"active": False, "bets": {}}

ORANGE, GREEN, RED, BLUE = 0xF39C12, 0x2ECC71, 0xE74C3C, 0x3498DB

def user(m):
    if m.id not in users:
        users[m.id] = {
            "cash": 4899, "bank": 0, "role": "Không có",
            "loan": 0, "debt": False
        }
    return users[m.id]

def money(n):
    return f"{n:,}$"

def em(title, text, color=BLUE):
    return discord.Embed(title=title, description=text, color=color)

def blocked(m):
    return user(m)["debt"]

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
async def trogiup(ctx):
    e = em(
        "🎰 CASINO BET88",
        "⚔️ **CASINO**\n"
        "`!tx tai 1000` • `!tx xiu 1000`\n"
        "`!bc cua 1000`\n"
        "`!xd chan 1000` • `!xd le 1000`\n"
        "`!quay 1000`\n\n"

        "🏦 **TÀI KHOẢN**\n"
        "`!vi` • `!gui 1000` • `!rut 1000`\n"
        "`!chuyen @user 1000`\n"
        "`!vay 50000` • `!trano 50000`\n"
        "`!bxh`\n\n"

        "🛒 **CỬA HÀNG**\n"
        "`!cuahang`\n"
        "`!muan vip`\n"
        "`!muan daigia`\n"
        "`!muan typhu`\n\n"

        "👑 **ADMIN**\n"
        "`!taocode số_tiền số_lượt`",
        BLUE
    )
    await ctx.send(embed=e)

# ================= VÍ =================

@bot.command(name="vi", aliases=["money", "bal"])
async def vi(ctx, member: discord.Member = None):
    member = member or ctx.author
    u = user(member)

    debt = "⚠️ **CON NỢ**" if u["debt"] else "✅ Không nợ"

    e = em(
        f"💳 VÍ CỦA {member.display_name}",
        f"💵 **Tiền mặt:** `{money(u['cash'])}`\n"
        f"🏦 **Ngân hàng:** `{money(u['bank'])}`\n"
        f"👑 **Role:** `{u['role']}`\n"
        f"💸 **Trạng thái:** {debt}",
        BLUE
    )
    await ctx.send(embed=e)

# ================= GỬI =================

@bot.command(name="gui")
async def gui(ctx, amount: int = None):
    if not amount or amount <= 0:
        return await ctx.send("❌ Dùng: `!gui số_tiền`")

    u = user(ctx.author)
    if amount > u["cash"]:
        return await ctx.send("❌ Không đủ tiền mặt.")

    u["cash"] -= amount
    u["bank"] += amount

    await ctx.send(embed=em(
        "🏦 GỬI NGÂN HÀNG",
        f"Đã gửi `{money(amount)}` vào ngân hàng.\n"
        "💰 Tiền sẽ được cộng lãi theo hệ thống.",
        GREEN
    ))

# ================= RÚT =================

@bot.command(name="rut")
async def rut(ctx, amount: int = None):
    if not amount or amount <= 0:
        return await ctx.send("❌ Dùng: `!rut số_tiền`")

    u = user(ctx.author)
    if amount > u["bank"]:
        return await ctx.send("❌ Ngân hàng không đủ tiền.")

    u["bank"] -= amount
    u["cash"] += amount

    await ctx.send(embed=em(
        "💵 RÚT TIỀN",
        f"Bạn đã rút `{money(amount)}`.",
        GREEN
    ))

# ================= CHUYỂN =================

@bot.command(name="chuyen")
async def chuyen(ctx, member: discord.Member = None, amount: int = None):
    if not member or not amount:
        return await ctx.send("❌ Dùng: `!chuyen @user 1000`")

    if amount < 1 or amount > 10_000_000:
        return await ctx.send("❌ Chỉ được chuyển 1$ - 10.000.000$.")

    if member.id == ctx.author.id:
        return await ctx.send("❌ Không thể chuyển cho chính mình.")

    a, b = user(ctx.author), user(member)

    if a["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền.")

    a["cash"] -= amount
    b["cash"] += amount

    await ctx.send(embed=em(
        "💸 CHUYỂN TIỀN",
        f"{ctx.author.mention} → {member.mention}\n"
        f"💰 Số tiền: `{money(amount)}`",
        GREEN
    ))

# ================= VAY =================

@bot.command(name="vay")
async def vay(ctx, amount: int = None):
    if not amount or amount < 1000 or amount > 50000:
        return await ctx.send("❌ Chỉ được vay từ 1.000$ đến 50.000$.")

    u = user(ctx.author)

    if u["debt"]:
        return await ctx.send("❌ Bạn đang là **CON NỢ**, hãy trả khoản vay trước.")

    if u["loan"] > 0:
        return await ctx.send("❌ Bạn đang có khoản vay.")

    u["loan"] = amount
    u["debt"] = False
    u["cash"] += amount

    await ctx.send(embed=em(
        "🏦 KHOẢN VAY",
        f"💰 Bạn đã vay **{money(amount)}**.\n\n"
        "⏰ Thời hạn: **1 giờ**.\n"
        "⚠️ Sau 1 giờ chưa trả → **CON NỢ** và không được chơi.",
        ORANGE
    ))

    async def check():
        await asyncio.sleep(3600)
        if u["loan"] > 0:
            u["debt"] = True

    asyncio.create_task(check())

# ================= TRẢ NỢ =================

@bot.command(name="trano")
async def trano(ctx, amount: int = None):
    if not amount or amount <= 0:
        return await ctx.send("❌ Dùng: `!trano số_tiền`")

    u = user(ctx.author)

    if u["loan"] <= 0:
        return await ctx.send("❌ Bạn không có khoản vay.")

    if amount != u["loan"]:
        return await ctx.send(
            f"❌ Bạn phải trả đúng `{money(u['loan'])}`."
        )

    if u["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền để trả nợ.")

    u["cash"] -= amount
    u["loan"] = 0
    u["debt"] = False

    await ctx.send(embed=em(
        "✅ ĐÃ TRẢ NỢ",
        f"{ctx.author.mention} đã trả `{money(amount)}`.\n"
        "🎉 Bạn đã được phép chơi lại.",
        GREEN
    ))

# ================= BXH =================

@bot.command(name="bxh")
async def bxh(ctx):
    data = sorted(
        users.items(),
        key=lambda x: x[1]["cash"] + x[1]["bank"],
        reverse=True
    )[:5]

    text = ""

    for i, (uid, u) in enumerate(data, 1):
        m = ctx.guild.get_member(uid)
        name = m.display_name if m else f"User {uid}"
        total = u["cash"] + u["bank"]
        text += f"**{i}.** {name} — `{money(total)}`\n"

    if not text:
        text = "Chưa có dữ liệu."

    await ctx.send(embed=em(
        "🏆 TOP 5 GIÀU NHẤT",
        text,
        ORANGE
    ))

# ================= SLOT =================

@bot.command(name="quay")
async def quay(ctx, amount: int = None):
    if blocked(ctx.author):
        return await ctx.send("❌ Bạn đang là **CON NỢ**, hãy trả nợ trước.")

    if not amount or amount <= 0:
        return await ctx.send("❌ Dùng: `!quay số_tiền`")

    u = user(ctx.author)

    if amount > u["cash"]:
        return await ctx.send("❌ Bạn không đủ tiền.")

    u["cash"] -= amount

    icons = ["🍒", "🍋", "🔔", "⭐", "💎"]
    a, b, c = [random.choice(icons) for _ in range(3)]

    msg = await ctx.send(embed=em(
        "🎰 SLOT",
        "🎰 **ĐANG QUAY...**\n\n"
        "⬜ ⬜ ⬜",
        ORANGE
    ))

    await asyncio.sleep(.5)
    await msg.edit(embed=em(
        "🎰 SLOT",
        f"🎰 **ĐANG QUAY...**\n\n"
        f"🟨 {a} 🟨",
        ORANGE
    ))

    await asyncio.sleep(.5)
    await msg.edit(embed=em(
        "🎰 SLOT",
        f"🎰 **ĐANG QUAY...**\n\n"
        f"🟨 {a} {b} 🟨",
        ORANGE
    ))

    await asyncio.sleep(.5)
    await msg.edit(embed=em(
        "🎰 SLOT",
        f"🎰 **KẾT QUẢ**\n\n"
        f"🟨 {a}   {b}   {c} 🟨",
        ORANGE
    ))

    if a == b == c:
        reward = amount * 5
        u["cash"] += reward
        result = f"🎉 **JACKPOT x5!**\n💰 Nhận `{money(reward)}`"
        color = GREEN

    elif a == b or a == c or b == c:
        reward = int(amount * 1.5)
        u["cash"] += reward
        result = f"🟢 **2 hình giống nhau x1.5!**\n💰 Nhận `{money(reward)}`"
        color = GREEN

    else:
        result = f"🔴 **THUA!**\n💸 Mất `{money(amount)}`"
        color = RED

    await asyncio.sleep(.4)
    await msg.edit(embed=em(
        "🎰 SLOT",
        f"🟨 {a}   {b}   {c} 🟨\n\n{result}",
        color
    ))

# ================= XÓC ĐĨA =================

@bot.command(name="xd")
async def xd(ctx, choice: str = None, amount: int = None):
    if blocked(ctx.author):
        return await ctx.send("❌ Bạn đang là **CON NỢ**, hãy trả nợ trước.")

    if choice not in ("chan", "le") or not amount:
        return await ctx.send("❌ Dùng: `!xd chan 1000` hoặc `!xd le 1000`")

    if amount < 100 or amount > 10_000_000:
        return await ctx.send("❌ Cược 100$ - 10.000.000$.")

    u = user(ctx.author)

    if u["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền.")

    u["cash"] -= amount

    msg = await ctx.send(embed=em(
        "🪙 XÓC ĐĨA",
        "🟠 **Xóc... Xóc... Xóc...**",
        ORANGE
    ))

    await asyncio.sleep(2)

    coins = [random.randint(0, 1) for _ in range(4)]
    red = sum(coins)
    result = "chan" if red % 2 == 0 else "le"
    text = "CHẴN" if result == "chan" else "LẺ"
    board = " ".join("🔴" if x else "⚪" for x in coins)

    win = choice == result

    if win:
        u["cash"] += amount * 2

    await msg.edit(embed=em(
        "🪙 XÓC ĐĨA",
        f"🔴 **{board}**\n\n"
        f"🎯 Kết quả: **{text}**\n"
        f"🔴 Số đỏ: **{red}**\n\n"
        + (
            f"🎉 **THẮNG x2!**\n💰 Nhận `{money(amount * 2)}`"
            if win else
            f"🔴 **THUA!**\n💸 Mất `{money(amount)}`"
        ),
        GREEN if win else RED
    ))

# ================= BẦU CUA =================

@bot.command(name="bc")
async def bc(ctx, choice: str = None, amount: int = None):
    if blocked(ctx.author):
        return await ctx.send("❌ Bạn đang là **CON NỢ**, hãy trả nợ trước.")

    icons = {
        "ca": "🐟", "tom": "🦐", "cua": "🦀",
        "bau": "🥒", "ga": "🐓", "nai": "🦌"
    }

    if choice not in icons or not amount:
        return await ctx.send(
            "❌ Dùng: `!bc ca/tom/cua/bau/ga/nai 1000`"
        )

    if amount < 100 or amount > 10_000_000:
        return await ctx.send("❌ Cược 100$ - 10.000.000$.")

    u = user(ctx.author)

    if u["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền.")

    u["cash"] -= amount

    msg = await ctx.send(embed=em(
        "🎲 BẦU CUA",
        "🟠 **ĐANG QUAY...**",
        ORANGE
    ))

    await asyncio.sleep(.6)
    r = [random.choice(list(icons)) for _ in range(3)]

    await msg.edit(embed=em(
        "🎲 BẦU CUA",
        f"🟨 {icons[r[0]]}   {icons[r[1]]}   {icons[r[2]]}",
        ORANGE
    ))

    count = r.count(choice)

    if count:
        reward = amount * (count + 1)
        u["cash"] += reward
        result = (
            f"🎉 **TRÚNG {count} CON x{count + 1}!**\n"
            f"💰 Nhận `{money(reward)}`"
        )
        color = GREEN
    else:
        result = f"🔴 **THUA!**\n💸 Mất `{money(amount)}`"
        color = RED

    await msg.edit(embed=em(
        "🎲 BẦU CUA",
        f"🟨 {icons[r[0]]}   {icons[r[1]]}   {icons[r[2]]}\n\n"
        f"{result}",
        color
    ))

# ================= TÀI XỈU =================

@bot.command(name="tx")
async def tx(ctx, choice: str = None, amount: int = None):
    if blocked(ctx.author):
        return await ctx.send("❌ Bạn đang là **CON NỢ**, hãy trả nợ trước.")

    if choice not in ("tai", "xiu"):
        return await ctx.send("❌ Dùng: `!tx tai 1000` hoặc `!tx xiu 1000`")

    if not amount or amount < 100 or amount > 10_000_000:
        return await ctx.send("❌ Cược 100$ - 10.000.000$.")

    u = user(ctx.author)

    if u["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền.")

    if ctx.author.id in TX["bets"]:
        return await ctx.send("❌ Bạn đã cược trong phiên này.")

    u["cash"] -= amount
    TX["bets"][ctx.author.id] = {
        "choice": choice,
        "amount": amount,
        "name": ctx.author.display_name
    }

    if not TX["active"]:
        TX["active"] = True

        msg = await ctx.send(embed=em(
            "🎲 TÀI XỈU",
            "🟠 **ĐANG NHẬN CƯỢC**\n\n"
            "⏱️ Thời gian: **30 giây**\n"
            "👥 Người đã cược: **1**",
            ORANGE
        ))

        await asyncio.sleep(30)

        if not TX["active"]:
            return

        TX["active"] = False

        d = [random.randint(1, 6) for _ in range(3)]
        total = sum(d)
        result = "tai" if total >= 11 else "xiu"

        text = (
            f"🎲 **{d[0]} + {d[1]} + {d[2]} = {total}**\n"
            f"🎯 Kết quả: **{result.upper()}**\n\n"
        )

        for uid, bet in TX["bets"].items():
            if bet["choice"] == result:
                reward = bet["amount"] * 2
                users[uid]["cash"] += reward
                text += f"🟢 {bet['name']} +`{money(reward)}`\n"
            else:
                text += f"🔴 {bet['name']} -`{money(bet['amount'])}`\n"

        TX["bets"] = {}

        await msg.edit(embed=em(
            "🎲 KẾT QUẢ TÀI XỈU",
            text,
            GREEN
        ))

    else:
        await ctx.send(embed=em(
            "🎲 ĐẶT CƯỢC",
            f"{ctx.author.mention}\n"
            f"🎯 **{choice.upper()}**\n"
            f"💰 `{money(amount)}`",
            ORANGE
        ))

# ================= SHOP =================

@bot.command(name="cuahang")
async def cuahang(ctx):
    await ctx.send(embed=em(
        "🛒 CỬA HÀNG ROLE",
        "💛 **VIP** — `10.000.000$`\n"
        "`!muan vip`\n\n"
        "💙 **ĐẠI GIA** — `5.000.000$`\n"
        "`!muan daigia`\n\n"
        "💜 **TỶ PHÚ** — `1.000.000.000$`\n"
        "`!muan typhu`",
        BLUE
    ))

# ================= MUA ROLE =================

@bot.command(name="muan")
async def muan(ctx, name: str = None):
    prices = {
        "vip": (10_000_000, "VIP"),
        "daigia": (5_000_000, "Đại Gia"),
        "typhu": (1_000_000_000, "Tỷ Phú")
    }

    if name not in prices:
        return await ctx.send("❌ `!muan vip/daigia/typhu`")

    price, role_name = prices[name]
    u = user(ctx.author)

    if u["cash"] < price:
        return await ctx.send("❌ Không đủ tiền.")

    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if not role:
        return await ctx.send(f"❌ Chưa có role **{role_name}**.")

    if role >= ctx.guild.me.top_role:
        return await ctx.send("❌ Role cao hơn role của bot.")

    try:
        await ctx.author.add_roles(role)
    except discord.Forbidden:
        return await ctx.send("❌ Bot không có quyền gán role.")

    u["cash"] -= price
    u["role"] = role_name

    await ctx.send(embed=em(
        "👑 MUA ROLE THÀNH CÔNG",
        f"🎉 {ctx.author.mention}\n"
        f"👑 Role: **{role_name}**\n"
        f"💰 Giá: `{money(price)}`",
        GREEN
    ))

# ================= ADMIN TẠO CODE =================

@bot.command(name="taocode")
@commands.has_permissions(administrator=True)
async def taocode(ctx, amount: int = None, uses: int = None):
    if not amount or not uses or amount <= 0 or uses <= 0:
        return await ctx.send("❌ Dùng: `!taocode 10000 5`")

    code = "BET" + "".join(
        random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789")
        for _ in range(8)
    )

    if not hasattr(bot, "codes"):
        bot.codes = {}

    bot.codes[code] = {
        "amount": amount,
        "uses": uses
    }

    try:
        await ctx.author.send(embed=em(
            "🎁 CODE TIỀN",
            f"🔑 Code: `{code}`\n"
            f"💰 Giá trị: `{money(amount)}`\n"
            f"🔢 Lượt nhập: `{uses}`",
            GREEN
        ))
        await ctx.send("✅ Đã gửi code riêng vào DM của bạn.")
    except discord.Forbidden:
        await ctx.send("❌ Không thể gửi DM cho bạn.")

@bot.command(name="nhapcode")
async def nhapcode(ctx, code: str = None):
    if not code or not hasattr(bot, "codes"):
        return await ctx.send("❌ Code không tồn tại.")

    data = bot.codes.get(code.upper())

    if not data or data["uses"] <= 0:
        return await ctx.send("❌ Code không tồn tại hoặc đã hết lượt.")

    u = user(ctx.author)
    u["cash"] += data["amount"]
    data["uses"] -= 1

    if data["uses"] <= 0:
        del bot.codes[code.upper()]

    await ctx.send(embed=em(
        "🎁 NHẬP CODE",
        f"🎉 Bạn nhận được `{money(data['amount'])}`!",
        GREEN
    ))

# ================= LỖI =================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.MissingPermissions):
        return await ctx.send("❌ Bạn không có quyền Admin.")

    print("ERROR:", error)

# ================= TOKEN =================

TOKEN = os.getenv("TOKEN_BOT")

if not TOKEN:
    print("❌ Chưa đặt TOKEN_BOT!")
else:
    bot.run(TOKEN)
