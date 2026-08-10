import os, random, asyncio, time, string, discord
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

users = {}
codes = {}
TX = {"active": False, "bets": {}, "msg": None}

ORANGE = 0xF39C12
GREEN = 0x2ECC71
RED = 0xE74C3C
BLUE = 0x3498DB

def fmt(n):
    return f"{n:,}$"

def E(title, text, color):
    return discord.Embed(title=title, description=text, color=color)

def user(m):
    if m.id not in users:
        users[m.id] = {
            "cash": 4899,
            "bank": 0,
            "role": "Không có",
            "debt": 0,
            "loan_time": 0
        }
    return users[m.id]

def no_debt(m):
    u = user(m)
    if u["debt"] > 0 and time.time() >= u["loan_time"]:
        return False
    return True

def can_play(m):
    u = user(m)
    if u["debt"] > 0 and time.time() >= u["loan_time"]:
        return False
    return True

async def blocked(ctx):
    if not can_play(ctx.author):
        await ctx.send(
            E(
                "🚫 CON NỢ",
                f"{ctx.author.mention}\n"
                f"Bạn đang có khoản nợ `{fmt(user(ctx.author)['debt'])}`.\n\n"
                "⚠️ Bạn không thể chơi Casino.\n"
                "Hãy dùng `!trano số_tiền` để trả nợ.",
                RED
            )
        )
        return True
    return False

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino")
    )
    print("BOT ONLINE:", bot.user)

@tasks.loop(seconds=10)
async def check_debt():
    for uid, u in users.items():
        if u["debt"] > 0 and time.time() >= u["loan_time"]:
            for g in bot.guilds:
                m = g.get_member(uid)
                if m:
                    try:
                        if not m.display_name.startswith("Con Nợ"):
                            await m.edit(nick=f"Con Nợ | {m.name}")
                    except:
                        pass

@bot.event
async def setup_hook():
    check_debt.start()

# ================= HELP =================

@bot.command(name="trogiup")
async def trogiup(ctx):
    t = (
        "# 🎰 CASINO BET88\n\n"
        "## 🎲 CASINO\n"
        "`!tx tai 1000` `!tx xiu 1000`\n"
        "`!quay 1000`\n"
        "`!bc cua 1000`\n"
        "`!xd chan 1000` `!xd le 1000`\n\n"

        "## 💰 TÀI KHOẢN\n"
        "`!vi` `!gui 1000` `!rut 1000`\n"
        "`!chuyen @user 1000`\n"
        "`!vay 50000` `!trano 50000`\n"
        "`!bxh`\n\n"

        "## 🛒 CỬA HÀNG\n"
        "`!cuahang`\n"
        "`!muan vip`\n"
        "`!muan daigia`\n"
        "`!muan typhu`\n\n"

        "## 🎁 MÃ QUÀ\n"
        "`!nhapcode MA`\n\n"

        "## 👑 ADMIN\n"
        "`!taocode số_tiền số_lượt`"
    )
    await ctx.send(E("📖 HƯỚNG DẪN LỆNH", t, BLUE))

# ================= VI =================

@bot.command(name="vi", aliases=["bal","money"])
async def vi(ctx, member: discord.Member = None):
    m = member or ctx.author
    u = user(m)
    await ctx.send(E(
        f"💳 VÍ CỦA {m.display_name}",
        f"💵 **Tiền mặt:** `{fmt(u['cash'])}`\n"
        f"🏦 **Ngân hàng:** `{fmt(u['bank'])}`\n"
        f"👑 **Role:** `{u['role']}`\n"
        f"💸 **Nợ:** `{fmt(u['debt'])}`",
        BLUE
    ))

# ================= GUI =================

@bot.command(name="gui")
async def gui(ctx, amount: int = 0):
    u = user(ctx.author)
    if amount <= 0:
        return await ctx.send("❌ `!gui số_tiền`")
    if amount > u["cash"]:
        return await ctx.send("❌ Không đủ tiền mặt.")
    u["cash"] -= amount
    u["bank"] += amount
    await ctx.send(E(
        "🏦 GỬI NGÂN HÀNG",
        f"Đã gửi `{fmt(amount)}` vào ngân hàng.",
        GREEN
    ))

# ================= RUT =================

@bot.command(name="rut")
async def rut(ctx, amount: int = 0):
    u = user(ctx.author)
    if amount <= 0:
        return await ctx.send("❌ `!rut số_tiền`")
    if amount > u["bank"]:
        return await ctx.send("❌ Ngân hàng không đủ tiền.")
    u["bank"] -= amount
    u["cash"] += amount
    await ctx.send(E(
        "💵 RÚT TIỀN",
        f"Đã rút `{fmt(amount)}`.",
        GREEN
    ))

# ================= CHUYEN =================

@bot.command(name="chuyen")
async def chuyen(ctx, member: discord.Member = None, amount: int = 0):
    if not member or amount < 1 or amount > 10_000_000:
        return await ctx.send(
            "❌ `!chuyen @người 1-10000000`"
        )
    if member.id == ctx.author.id:
        return await ctx.send("❌ Không thể chuyển cho chính mình.")

    a = user(ctx.author)
    b = user(member)

    if a["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền.")

    a["cash"] -= amount
    b["cash"] += amount

    await ctx.send(
        f"💸 {ctx.author.mention} chuyển `{fmt(amount)}` "
        f"cho {member.mention}."
    )

# ================= VAY =================

@bot.command(name="vay")
async def vay(ctx, amount: int = 0):
    u = user(ctx.author)

    if u["debt"] > 0:
        return await ctx.send(
            "❌ Bạn đang có khoản vay chưa trả."
        )

    if amount < 1000 or amount > 50000:
        return await ctx.send(
            "❌ Chỉ được vay từ `1.000$` đến `50.000$`."
        )

    u["cash"] += amount
    u["debt"] = amount
    u["loan_time"] = time.time() + 3600

    await ctx.send(E(
        "💰 VAY TIỀN THÀNH CÔNG",
        f"{ctx.author.mention}\n\n"
        f"💵 Đã vay: **`{fmt(amount)}`**\n"
        f"⏰ Thời hạn: **1 giờ**\n\n"
        f"⚠️ Sau 1 giờ chưa trả, bạn sẽ thành **Con Nợ** "
        f"và không được chơi Casino.\n\n"
        f"Trả bằng: `!trano {amount}`",
        GREEN
    ))

@bot.command(name="trano")
async def trano(ctx, amount: int = 0):
    u = user(ctx.author)

    if u["debt"] <= 0:
        return await ctx.send("❌ Bạn không có khoản nợ.")

    if amount != u["debt"]:
        return await ctx.send(
            f"❌ Hãy trả đúng số nợ: `{fmt(u['debt'])}`"
        )

    if u["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền mặt để trả nợ.")

    u["cash"] -= amount
    u["debt"] = 0
    u["loan_time"] = 0

    try:
        if ctx.author.display_name.startswith("Con Nợ"):
            await ctx.author.edit(nick=None)
    except:
        pass

    await ctx.send(E(
        "✅ ĐÃ TRẢ NỢ",
        f"{ctx.author.mention}\n"
        f"Đã trả `{fmt(amount)}`.\n\n"
        "🎉 Bạn đã hết nợ và có thể chơi lại.",
        GREEN
    ))

# ================= BXH =================

@bot.command(name="bxh")
async def bxh(ctx):
    arr = sorted(
        users.items(),
        key=lambda x: x[1]["cash"] + x[1]["bank"],
        reverse=True
    )[:5]

    text = "# 🏆 TOP 5 GIÀU NHẤT\n\n"

    for i, (uid, u) in enumerate(arr, 1):
        m = ctx.guild.get_member(uid)
        name = m.display_name if m else u.get("name", "Unknown")
        total = u["cash"] + u["bank"]
        text += f"**#{i}** {name} — `{fmt(total)}`\n"

    await ctx.send(E("🏆 BẢNG XẾP HẠNG", text, BLUE))

# ================= QUAY =================

@bot.command(name="quay")
async def quay(ctx, amount: int = 0):
    if await blocked(ctx):
        return

    u = user(ctx.author)

    if amount <= 0:
        return await ctx.send("❌ `!quay số_tiền`")
    if u["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền.")

    u["cash"] -= amount

    s = ["🍒","🍋","🔔","⭐","💎"]
    a, b, c = [random.choice(s) for _ in range(3)]

    msg = await ctx.send(E(
        "🎰 SLOT",
        "# 🟠 ĐANG QUAY\n\n"
        f"## `{a}   ?   ?`",
        ORANGE
    ))

    await asyncio.sleep(.7)
    await msg.edit(embed=E(
        "🎰 SLOT",
        "# 🟠 ĐANG QUAY\n\n"
        f"## `{a}   {b}   ?`",
        ORANGE
    ))

    await asyncio.sleep(.7)
    await msg.edit(embed=E(
        "🎰 SLOT",
        "# 🟠 ĐANG QUAY\n\n"
        f"## `{a}   {b}   {c}`",
        ORANGE
    ))

    await asyncio.sleep(.5)

    same = len({a,b,c})

    if same == 1:
        reward = amount * 5
        u["cash"] += reward
        title = "💎 JACKPOT x5!"
        color = GREEN
        text = f"## `{a}   {b}   {c}`\n\n🟢 Nhận `{fmt(reward)}`"
    elif same == 2:
        reward = int(amount * 1.5)
        u["cash"] += reward
        title = "🎰 2 HÌNH GIỐNG NHAU x1.5"
        color = GREEN
        text = f"## `{a}   {b}   {c}`\n\n🟢 Nhận `{fmt(reward)}`"
    else:
        title = "💥 SLOT THUA"
        color = RED
        text = f"## `{a}   {b}   {c}`\n\n🔴 Mất `{fmt(amount)}`"

    await msg.edit(embed=E(title, text, color))

# ================= XOC DIA =================

@bot.command(name="xd")
async def xd(ctx, choice: str = None, amount: int = 0):
    if await blocked(ctx):
        return

    if choice not in ["chan","le"] or amount <= 0:
        return await ctx.send(
            "❌ `!xd chan 1000` hoặc `!xd le 1000`"
        )

    u = user(ctx.author)

    if u["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền.")

    u["cash"] -= amount

    msg = await ctx.send(E(
        "🪙 XÓC ĐĨA",
        "# 🟠 Xóc... Xóc... Xóc...",
        ORANGE
    ))

    await asyncio.sleep(2)

    coins = [random.randint(0,1) for _ in range(4)]
    red = sum(coins)

    result = "chan" if red in [2,4] else "le"
    name = "CHẴN" if result == "chan" else "LẺ"

    board = "  ".join(
        "🔴" if x else "⚪" for x in coins
    )

    win = choice == result

    if win:
        u["cash"] += amount * 2
        color = GREEN
        result_text = f"🟢 **THẮNG x2!** +`{fmt(amount)}`"
    else:
        color = RED
        result_text = f"🔴 **THUA!** -`{fmt(amount)}`"

    await msg.edit(embed=E(
        "🪙 XÓC ĐĨA",
        f"## {board}\n\n"
        f"### Kết quả: **{name}**\n"
        f"Số đỏ: **{red}**\n\n"
        f"{result_text}",
        color
    ))

# ================= BAU CUA =================

@bot.command(name="bc")
async def bc(ctx, choice: str = None, amount: int = 0):
    if await blocked(ctx):
        return

    animals = {
        "ca":"🐟",
        "tom":"🦐",
        "cua":"🦀",
        "bau":"🥒",
        "ga":"🐓",
        "nai":"🦌"
    }

    if choice not in animals or amount <= 0:
        return await ctx.send(
            "❌ `!bc ca/tom/cua/bau/ga/nai số_tiền`"
        )

    u = user(ctx.author)

    if u["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền.")

    u["cash"] -= amount

    r = [random.choice(list(animals)) for _ in range(3)]

    msg = await ctx.send(E(
        "🎲 BẦU CUA",
        "# 🟠 ĐANG QUAY\n\n## `[ ? ]`",
        ORANGE
    ))

    await asyncio.sleep(.7)

    await msg.edit(embed=E(
        "🎲 BẦU CUA",
        f"# 🟠 ĐANG QUAY\n\n## `[ {animals[r[0]]} ]`",
        ORANGE
    ))

    await asyncio.sleep(.7)

    await msg.edit(embed=E(
        "🎲 BẦU CUA",
        f"# 🟠 ĐANG QUAY\n\n"
        f"## `[ {animals[r[0]]} ] [ {animals[r[1]]} ]`",
        ORANGE
    ))

    await asyncio.sleep(.7)

    await msg.edit(embed=E(
        "🎲 BẦU CUA",
        f"# 🟠 ĐANG QUAY\n\n"
        f"## `[ {animals[r[0]]} ] [ {animals[r[1]]} ] "
        f"[ {animals[r[2]]} ]`",
        ORANGE
    ))

    count = r.count(choice)

    if count:
        reward = amount * (count + 1)
        u["cash"] += reward

        await msg.edit(embed=E(
            "🎲 BẦU CUA",
            f"## `{animals[r[0]]} {animals[r[1]]} {animals[r[2]]}`\n\n"
            f"🟢 **TRÚNG {count} CON — x{count+1}**\n"
            f"Nhận `{fmt(reward)}`",
            GREEN
        ))
    else:
        await msg.edit(embed=E(
            "🎲 BẦU CUA",
            f"## `{animals[r[0]]} {animals[r[1]]} {animals[r[2]]}`\n\n"
            f"🔴 **THUA!**\nMất `{fmt(amount)}`",
            RED
        ))

# ================= TAI XIU =================

@bot.command(name="tx")
async def tx(ctx, choice: str = None, amount: int = 0):
    global TX

    if await blocked(ctx):
        return

    if choice not in ["tai","xiu"]:
        return await ctx.send(
            "❌ `!tx tai 1000` hoặc `!tx xiu 1000`"
        )

    if amount < 100 or amount > 10_000_000:
        return await ctx.send(
            "❌ Cược từ `100$` đến `10.000.000$`."
        )

    u = user(ctx.author)

    if u["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền.")

    if TX["active"]:
        if ctx.author.id in TX["bets"]:
            return await ctx.send(
                "❌ Bạn đã cược rồi. Mỗi người chỉ được cược 1 lần."
            )

        u["cash"] -= amount
        TX["bets"][ctx.author.id] = {
            "choice": choice,
            "amount": amount,
            "name": ctx.author.display_name
        }

        return await ctx.send(E(
            "🎲 ĐẶT TÀI XỈU",
            f"{ctx.author.mention}\n"
            f"💰 `{fmt(amount)}` — **{choice.upper()}**",
            ORANGE
        ))

    TX["active"] = True
    TX["bets"] = {}

    u["cash"] -= amount
    TX["bets"][ctx.author.id] = {
        "choice": choice,
        "amount": amount,
        "name": ctx.author.display_name
    }

    msg = await ctx.send(E(
        "🎲 TÀI XỈU",
        "# 🟠 PHIÊN ĐÃ MỞ\n\n"
        f"{ctx.author.mention} cược `{fmt(amount)}` "
        f"**{choice.upper()}**\n\n"
        "⏱️ Còn **30 giây**\n"
        "Mỗi người chỉ được cược **1 lần**.",
        ORANGE
    ))

    TX["msg"] = msg

    for sec in [20,10]:
        await asyncio.sleep(10)
        if not TX["active"]:
            return

        await msg.edit(embed=E(
            "🎲 TÀI XỈU",
            f"# 🟠 ĐANG NHẬN CƯỢC\n\n"
            f"## ⏱️ Còn {sec} giây\n\n"
            f"👥 Đã cược: **{len(TX['bets'])} người**",
            ORANGE
        ))

    await asyncio.sleep(10)

    if not TX["active"]:
        return

    TX["active"] = False

    d = [random.randint(1,6) for _ in range(3)]
    total = sum(d)
    result = "tai" if total >= 11 else "xiu"

    text = (
        f"# 🎲 `{d[0]}  {d[1]}  {d[2]}`\n\n"
        f"## {total} ĐIỂM → **{result.upper()}**\n\n"
    )

    win = False

    for uid, bet in TX["bets"].items():
        p = users[uid]

        if bet["choice"] == result:
            reward = bet["amount"] * 2
            p["cash"] += reward
            text += (
                f"🟢 **{bet['name']}** +`{fmt(reward)}`\n"
            )
            win = True
        else:
            text += (
                f"🔴 **{bet['name']}** -`{fmt(bet['amount'])}`\n"
            )

    TX["bets"] = {}

    await msg.edit(embed=E(
        "🎲 KẾT QUẢ TÀI XỈU",
        text,
        GREEN if win else RED
    ))

# ================= SHOP =================

@bot.command(name="cuahang")
async def cuahang(ctx):
    await ctx.send(E(
        "🛒 CỬA HÀNG ROLE",
        "💛 **VIP** — `10.000.000$`\n"
        "`!muan vip`\n\n"
        "💙 **ĐẠI GIA** — `5.000.000$`\n"
        "`!muan daigia`\n\n"
        "💜 **TỶ PHÚ** — `1.000.000.000$`\n"
        "`!muan typhu`",
        BLUE
    ))

@bot.command(name="muan")
async def muan(ctx, name: str = None):
    price = {
        "vip":10_000_000,
        "daigia":5_000_000,
        "typhu":1_000_000_000
    }

    display = {
        "vip":"VIP",
        "daigia":"Đại Gia",
        "typhu":"Tỷ Phú"
    }

    if name not in price:
        return await ctx.send(
            "❌ `!muan vip`, `!muan daigia` hoặc `!muan typhu`"
        )

    u = user(ctx.author)

    if u["cash"] < price[name]:
        return await ctx.send("❌ Không đủ tiền.")

    role = discord.utils.get(
        ctx.guild.roles,
        name=display[name]
    )

    if not role:
        return await ctx.send(
            f"❌ Server chưa có role `{display[name]}`."
        )

    if role >= ctx.guild.me.top_role:
        return await ctx.send("❌ Bot không thể gán role này.")

    u["cash"] -= price[name]
    u["role"] = display[name]

    try:
        await ctx.author.add_roles(role)
    except discord.Forbidden:
        return await ctx.send("❌ Bot thiếu quyền Manage Roles.")

    await ctx.send(E(
        "👑 MUA ROLE THÀNH CÔNG",
        f"{ctx.author.mention}\n"
        f"Đã mua **{display[name]}**.\n"
        f"Giá: `{fmt(price[name])}`",
        GREEN
    ))

# ================= TAO CODE ADMIN =================

@bot.command(name="taocode")
@commands.has_permissions(administrator=True)
async def taocode(ctx, amount: int = 0, uses: int = 0):
    if amount <= 0 or uses <= 0:
        return await ctx.send(
            "❌ Dùng: `!taocode số_tiền số_lượt`\n"
            "Ví dụ: `!taocode 50000 10`"
        )

    code = "".join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=8
        )
    )

    codes[code] = {
        "amount": amount,
        "uses": uses
    }

    try:
        await ctx.author.send(
            f"🎁 **MÃ QUÀ BET88**\n\n"
            f"🔑 Mã: `{code}`\n"
            f"💰 Tiền: `{fmt(amount)}`\n"
            f"👥 Lượt nhập: **{uses}**\n\n"
            f"Dùng: `!nhapcode {code}`"
        )

        await ctx.send(
            f"✅ Đã tạo mã `{code}` và **gửi riêng vào DM** cho bạn."
        )

    except discord.Forbidden:
        await ctx.send(
            "❌ Không thể gửi DM. Hãy bật nhận tin nhắn riêng."
        )

@taocode.error
async def taocode_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Chỉ Admin mới dùng được lệnh này.")

# ================= NHAP CODE =================

@bot.command(name="nhapcode")
async def nhapcode(ctx, code: str = None):
    if not code:
        return await ctx.send("❌ `!nhapcode MÃ`")

    code = code.upper()

    if code not in codes:
        return await ctx.send("❌ Mã không tồn tại hoặc đã hết.")

    c = codes[code]
    u = user(ctx.author)

    u["cash"] += c["amount"]
    c["uses"] -= 1

    if c["uses"] <= 0:
        del codes[code]

    await ctx.send(E(
        "🎁 NHẬP CODE THÀNH CÔNG",
        f"{ctx.author.mention}\n"
        f"Nhận được `{fmt(c['amount'])}`.",
        GREEN
    ))

# ================= TOKEN =================

TOKEN = os.getenv("TOKEN_BOT")

if not TOKEN:
    print("❌ Không tìm thấy TOKEN_BOT!")
else:
    bot.run(TOKEN)
