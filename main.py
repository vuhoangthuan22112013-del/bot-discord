import os, asyncio, random, secrets, time, discord
from discord.ext import commands

I = discord.Intents.default()
I.message_content = True
bot = commands.Bot(command_prefix="!", intents=I, help_command=None)

U, C = {}, {}
RATE = {}  # tỷ lệ thắng theo server
BLUE, ORANGE, GREEN, RED, YELLOW = 0x3498DB, 0xF1C40F, 0x2ECC71, 0xE74C3C, 0xF1C40F

TX = {"on": 0, "bets": {}, "tai": 0, "xiu": 0, "msg": None}

def E(t, d, c=BLUE):
    return discord.Embed(title=t, description=d, color=c)

def user(i, n="Thành viên"):
    if i not in U:
        U[i] = {"name": n, "cash": 4899, "bank": 0, "vip": 0, "dd": 0}
    U[i]["name"] = n
    return U[i]

def adm(c):
    return c.author.guild_permissions.administrator

async def blocked(c):
    return False

def winrate(gid):
    return RATE.get(gid, 50)

# ================= BOT =================

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("!trogiup | Casino"))
    print("ONLINE:", bot.user)

# ================= TROGIUP =================

@bot.command(name="trogiup", aliases=["help"])
async def trogiup(c):
    await c.send(embed=E(
        "🎰 CASINO BET88",
        "🎲 **TÀI XỈU**\n"
        "`!tx tai 1000` `!tx xiu 1000`\n\n"
        "🦀 **BẦU CUA**\n"
        "`!bc cua 1000`\n\n"
        "🪙 **XÓC ĐĨA**\n"
        "`!xd chan 1000` `!xd le 1000`\n\n"
        "🎰 **MÁY SLOT**\n"
        "`!quay 1000`\n\n"
        "💳 **TÀI KHOẢN**\n"
        "`!vi` `!gui` `!rut` `!chuyen @User 100`\n\n"
        "🎁 **TIỆN ÍCH**\n"
        "`!diemdanh` `!bxh` `!muarole Vip`\n\n"
        "👑 **ADMIN**\n"
        "`!taocode` `!thuongcode` `!settien` `!resettien` `!tyle 0-100`"
    ))

# ================= VI =================

@bot.command()
async def vi(c, m: discord.Member = None):
    m = m or c.author
    u = user(m.id, m.name)

    if u["vip"]:
        hang = "👑 **Vương miện VIP**"
        ten = f"🟡 **{m.name}**"
    else:
        hang = "🐥 Người chơi Thường"
        ten = f"👤 **{m.name}**"

    await c.send(embed=E(
        "💳 TÀI KHOẢN",
        f"{ten}\n"
        f"🏷️ Hạng: {hang}\n\n"
        f"💵 Ví: `{u['cash']:,}$`\n"
        f"🏦 Bank: `{u['bank']:,}$`"
    ))

# ================= BANK =================

@bot.command()
async def gui(c, n: int = None):
    u = user(c.author.id, c.author.name)
    if not n or n <= 0 or u["cash"] < n:
        return await c.send("❌ Không đủ tiền!")
    u["cash"] -= n
    u["bank"] += n
    await c.send(f"🏦 Gửi `{n:,}$` thành công!")

@bot.command()
async def rut(c, n: int = None):
    u = user(c.author.id, c.author.name)
    if not n or n <= 0 or u["bank"] < n:
        return await c.send("❌ Bank không đủ!")
    u["bank"] -= n
    u["cash"] += n
    await c.send(f"🏦 Rút `{n:,}$` thành công!")

@bot.command()
async def chuyen(c, m: discord.Member = None, n: int = None):
    if not m or not n or n <= 0:
        return await c.send("❌ `!chuyen @User 100`")

    a = user(c.author.id, c.author.name)
    b = user(m.id, m.name)

    if a["cash"] < n:
        return await c.send("❌ Không đủ tiền!")

    a["cash"] -= n
    b["cash"] += n
    await c.send(f"💸 {c.author.mention} → {m.mention}: `{n:,}$`")

# ================= DIEM DANH =================

@bot.command()
async def diemdanh(c):
    u = user(c.author.id, c.author.name)
    now = time.time()
    left = int(43200 - (now - u["dd"]))

    if left > 0:
        return await c.send(
            f"⏳ **Mày đã điểm danh rồi!**\n"
            f"🕐 Đợi thêm **{left:,} giây** nữa."
        )

    u["dd"] = now
    u["cash"] += 2593

    await c.send(embed=E(
        "🎁 ĐIỂM DANH",
        "💰 **+2,593$ vào ví**",
        GREEN
    ))

# ================= BXH =================

@bot.command()
async def bxh(c):
    x = sorted(
        U.values(),
        key=lambda z: z["cash"] + z["bank"],
        reverse=True
    )[:5]

    text = ""
    for i, u in enumerate(x, 1):
        text += f"\n**{i}.** {u['name']} — `{u['cash']+u['bank']:,}$`"

    await c.send(embed=E("🏆 TOP 5", text))

# ================= TAI XIU =================

@bot.command()
async def tx(c, ch=None, bet: int = None):

    if ch not in ("tai", "xiu") or not bet or bet <= 0:
        return await c.send("❌ `!tx tai 1000`")

    if bet > 10_000_000:
        return await c.send("❌ Max **10,000,000$/ván**!")

    u = user(c.author.id, c.author.name)
    uid = c.author.id

    if u["cash"] < bet:
        return await c.send("❌ Không đủ tiền!")

    if uid in TX["bets"]:
        return await c.send("❌ Bạn đã cược ván này!")

    # MỞ PHIÊN
    if not TX["on"]:
        TX.update(on=1, bets={}, tai=0, xiu=0)

        TX["msg"] = await c.send(embed=E(
            "🎲 SÒNG TÀI XỈU 30S 🎲",
            "Gõ `!tx <tai/xiu> <tiền>` "
            "(Tối đa **10,000,000$/ván**)\n\n"
            "⏱️ **Thời gian: 30 giây**\n\n"
            "💵 Tổng Tài: `0$` | Tổng Xỉu: `0$`",
            ORANGE
        ))

        asyncio.create_task(txround())

    u["cash"] -= bet

    TX["bets"][uid] = {
        "name": c.author.name,
        "choice": ch,
        "amount": bet
    }

    TX[ch] += bet

    await TX["msg"].edit(embed=E(
        "🎲 SÒNG TÀI XỈU 30S 🎲",
        "Gõ `!tx <tai/xiu> <tiền>` "
        "(Tối đa **10,000,000$/ván**)\n\n"
        "⏱️ **Đang nhận cược...**\n\n"
        f"💵 Tổng Tài: `{TX['tai']:,}$` | "
        f"Tổng Xỉu: `{TX['xiu']:,}$`",
        ORANGE
    ))

    try:
        await c.message.delete()
    except:
        pass


async def txround():
    await asyncio.sleep(30)

    d = [random.randint(1, 6) for _ in range(3)]
    total = sum(d)
    result = "tai" if total >= 11 else "xiu"

    w, l = [], []

    for uid, b in TX["bets"].items():
        u = user(uid)

        # Tỷ lệ thắng
        force = random.randint(1, 100) <= 50

        # tỷ lệ server sẽ được lấy từ RATE nếu có
        # mặc định 50%
        gid = 0
        rate = 50

        # TX dùng kết quả thật nếu không ép
        if b["choice"] == result:
            won = True
        else:
            won = False

        if rate >= 100:
            won = True
        elif rate <= 0:
            won = False
        elif force and random.randint(1, 100) <= rate:
            won = True

        if won:
            p = b["amount"] * 2
            if u["vip"]:
                p = int(p * 1.5)

            u["cash"] += p
            w.append(f"• {b['name']} `+{p:,}$`")
        else:
            l.append(f"• {b['name']} `-{b['amount']:,}$`")

    await TX["msg"].edit(embed=E(
        "🎲 KẾT QUẢ TÀI XỈU",
        f"🎲 **Xúc xắc**\n"
        f"`[ {d[0]} ] - [ {d[1]} ] - [ {d[2]} ]`\n\n"
        f"➡️ **{total} điểm ({result.upper()})**\n\n"
        f"🎉 **THẮNG**\n"
        f"{chr(10).join(w) or 'Không có'}\n\n"
        f"💸 **THUA**\n"
        f"{chr(10).join(l) or 'Không có'}",
        GREEN if w else RED
    ))

    TX.update(on=0, bets={}, tai=0, xiu=0, msg=None)

# ================= BAU CUA =================

@bot.command()
async def bc(c, ch=None, bet: int = None):

    icons = {
        "ca": "🐟",
        "tom": "🦐",
        "cua": "🦀",
        "bau": "🍐",
        "ga": "🐓",
        "nai": "🦌"
    }

    if ch not in icons or not bet or bet <= 0:
        return await c.send("❌ `!bc cua 1000`")

    u = user(c.author.id, c.author.name)

    if u["cash"] < bet:
        return await c.send("❌ Không đủ tiền!")

    u["cash"] -= bet

    m = await c.send(embed=E(
        "🦀 BẦU CUA",
        "🎲 **LẮC... LẮC... LẮC...**",
        ORANGE
    ))

    await asyncio.sleep(1.2)

    await m.edit(embed=E(
        "🦀 BẦU CUA",
        "🎲 **LẮC... LẮC... LẮC...**\n\n"
        "🥣 **HÉ BÁT...**",
        ORANGE
    ))

    await asyncio.sleep(1.2)

    r = [random.choice(list(icons)) for _ in range(3)]
    n = r.count(ch)

    won = n > 0

    if RATE.get(c.guild.id, 50) >= 100:
        won = True
    elif RATE.get(c.guild.id, 50) <= 0:
        won = False
    elif random.randint(1, 100) > RATE.get(c.guild.id, 50):
        won = n > 0

    if won:
        p = bet * (n + 1)
        if u["vip"]:
            p = int(p * 1.5)
        u["cash"] += p
        result = f"🎉 **THẮNG +{p:,}$**"
        color = GREEN
    else:
        result = f"💸 **THUA -{bet:,}$**"
        color = RED

    await m.edit(embed=E(
        "🦀 BẦU CUA",
        f"`[ {' | '.join(icons[x] for x in r)} ]`\n\n"
        f"{result}\n"
        f"💵 Ví: `{u['cash']:,}$`",
        color
    ))

# ================= XOC DIA =================

@bot.command()
async def xd(c, ch=None, bet: int = None):

    if ch not in ("chan", "le") or not bet or bet <= 0:
        return await c.send("❌ `!xd chan 1000`")

    u = user(c.author.id, c.author.name)

    if u["cash"] < bet:
        return await c.send("❌ Không đủ tiền!")

    u["cash"] -= bet

    m = await c.send(embed=E(
        "🪙 XÓC ĐĨA",
        "🟠 **XÓC... XÓC... XÓC...**",
        ORANGE
    ))

    await asyncio.sleep(1.5)

    n = random.randint(0, 4)
    result = "chan" if n % 2 == 0 else "le"

    await m.edit(embed=E(
        "🪙 XÓC ĐĨA",
        "🟠 **XÓC... XÓC... XÓC...**\n\n"
        "🥣 **ĐANG MỞ ĐĨA...**",
        ORANGE
    ))

    await asyncio.sleep(1)

    won = result == ch
    rate = RATE.get(c.guild.id, 50)

    if rate >= 100:
        won = True
    elif rate <= 0:
        won = False

    if won:
        p = int(bet * 2 * (1.5 if u["vip"] else 1))
        u["cash"] += p
        res = f"🎉 **THẮNG +{p:,}$**"
        co = GREEN
    else:
        res = f"💸 **THUA -{bet:,}$**"
        co = RED

    await m.edit(embed=E(
        "🪙 XÓC ĐĨA",
        f"`[ {'🔴' if n else '⚪'} ]`\n\n"
        f"🎯 **{result.upper()}**\n\n"
        f"{res}\n"
        f"💵 Ví: `{u['cash']:,}$`",
        co
    ))

# ================= QUAY =================

@bot.command()
async def quay(c, bet: int = None):

    if not bet or bet <= 0:
        return await c.send("❌ `!quay 1000`")

    u = user(c.author.id, c.author.name)

    if u["cash"] < bet:
        return await c.send("❌ Không đủ tiền!")

    u["cash"] -= bet

    m = await c.send(embed=E(
        "🎰 MÁY SLOT",
        "🎰 **ĐANG QUAY...**\n\n"
        "`[ ❔ | ❔ | ❔ ]`",
        ORANGE
    ))

    await asyncio.sleep(1.5)

    s = [
        random.choice(["🍒", "🍋", "🔔", "⭐", "💎", "7️⃣"])
        for _ in range(3)
    ]

    same = max(s.count(x) for x in set(s))
    won = same >= 2

    rate = RATE.get(c.guild.id, 50)

    if rate >= 100:
        won = True
    elif rate <= 0:
        won = False

    if won:
        p = bet * (5 if same == 3 else 2)
        if u["vip"]:
            p = int(p * 1.5)

        u["cash"] += p
        res = f"🎉 **THẮNG +{p:,}$**"
        co = GREEN
    else:
        res = f"💸 **THUA -{bet:,}$**"
        co = RED

    await m.edit(embed=E(
        "🎰 MÁY SLOT",
        f"`[ {' | '.join(s)} ]`\n\n"
        f"{res}\n"
        f"💵 Ví: `{u['cash']:,}$`",
        co
    ))

# ================= VIP =================

@bot.command()
async def muarole(c, r=None):

    if (r or "").lower() != "vip":
        return await c.send("❌ `!muarole Vip`")

    u = user(c.author.id, c.author.name)

    if u["vip"]:
        return await c.send("👑 Bạn đã là **Vương miện VIP**!")

    if u["cash"] < 30_000_000:
        return await c.send("❌ VIP giá **30,000,000$**!")

    role = discord.utils.find(
        lambda x: x.name.lower() == "vip",
        c.guild.roles
    )

    if not role:
        return await c.send("❌ Server chưa có role `Vip`!")

    if role >= c.guild.me.top_role:
        return await c.send(
            "❌ Kéo role **Vip** xuống dưới role Bot!"
        )

    # đổi role thành vàng
    try:
        await role.edit(color=discord.Color.gold())
    except:
        pass

    u["cash"] -= 30_000_000
    u["vip"] = 1

    try:
        await c.author.add_roles(role)
    except:
        return await c.send("❌ Bot thiếu quyền quản lý role!")

    await c.send(embed=E(
        "👑 MUA VIP",
        f"🎉 {c.author.mention} đã trở thành **👑 Vương miện VIP**!\n\n"
        "💰 Giá: `30,000,000$`\n"
        "💵 Thưởng game: **x1.5**\n"
        "🟡 Tên: **Màu vàng**",
        YELLOW
    ))

# ================= ADMIN TY LE =================

@bot.command(name="tyle")
async def tyle(c, n: int = None):

    if not adm(c):
        return await c.send("⛔ Chỉ Admin!")

    if n is None or n < 0 or n > 100:
        return await c.send(
            "❌ Dùng: `!tyle 0-100`\n"
            "Ví dụ: `!tyle 70`"
        )

    RATE[c.guild.id] = n

    if n == 0:
        msg = "🚫 **0%** — Không thắng."
    elif n == 100:
        msg = "🔥 **100%** — Đánh là thắng."
    else:
        msg = f"🎯 Tỷ lệ thắng hiện tại: **{n}%**"

    await c.send(embed=E(
        "⚙️ CÀI TỶ LỆ THẮNG",
        msg,
        ORANGE
    ))

# ================= CODE =================

def newcode():
    return "BET-" + secrets.token_hex(3).upper()

@bot.command()
async def thuongcode(c, n: int = None, uses: int = None):

    if not adm(c):
        return await c.send("⛔ Chỉ Admin!")

    if not n or not uses:
        return await c.send("❌ `!thuongcode 1000 5`")

    x = newcode()
    C[x] = {"money": n, "uses": uses, "used": set()}

    await c.send(embed=E(
        "🎁 PHẦN THƯỞNG CODE",
        f"🔐 Mã: `{x}`\n"
        f"💰 Tiền: `{n:,}$`\n"
        f"👥 Lượt: `{uses}`",
        GREEN
    ))

@bot.command()
async def nhapcode(c, x=None):

    x = (x or "").upper()

    if x not in C:
        return await c.send("❌ Code không tồn tại!")

    z = C[x]

    if c.author.id in z["used"]:
        return await c.send("❌ Bạn đã dùng code!")

    if len(z["used"]) >= z["uses"]:
        return await c.send("❌ Code hết lượt!")

    z["used"].add(c.author.id)
    user(c.author.id, c.author.name)["cash"] += z["money"]

    await c.send(f"🎁 **+{z['money']:,}$ vào ví!**")

@bot.command()
async def taocode(c, n: int = None, uses: int = None):

    if not adm(c):
        return await c.send("⛔ Chỉ Admin!")

    if not n or not uses:
        return await c.send("❌ `!taocode 1000 1`")

    x = newcode()
    C[x] = {"money": n, "uses": uses, "used": set()}

    try:
        await c.author.send(
            f"🔐 `{x}` | 💰 `{n:,}$` | 👥 `{uses}` lượt"
        )
    except:
        pass

    await c.send("✅ Code đã gửi DM!")

# ================= ADMIN MONEY =================

@bot.command()
async def settien(c, m: discord.Member = None, n: int = None):

    if not adm(c):
        return await c.send("⛔ Chỉ Admin!")

    if not m or n is None:
        return await c.send("❌ `!settien @User 10000`")

    user(m.id, m.name)["cash"] = max(0, n)

    await c.send(
        f"💰 {m.mention} → Ví: **`{n:,}$`**"
    )

@bot.command()
async def resettien(c, m: discord.Member = None):

    if not adm(c):
        return await c.send("⛔ Chỉ Admin!")

    if not m:
        return await c.send("❌ `!resettien @User`")

    user(m.id, m.name)["cash"] = 4899

    await c.send(
        f"🔄 {m.mention} đã reset về **`4,899$`**"
    )

# ================= START =================

token = os.getenv("TOKEN_BOT")

if token:
    bot.run(token)
else:
    print("❌ Chưa có TOKEN_BOT!")
