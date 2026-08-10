import os, asyncio, random, secrets, time, discord
from discord.ext import commands

I = discord.Intents.default()
I.message_content = True

bot = commands.Bot(command_prefix="!", intents=I, help_command=None)

U, C = {}, {}
BLUE, ORANGE, GREEN, RED, GOLD = 0x3498DB, 0xF1C40F, 0x2ECC71, 0xE74C3C, 0xFFD700

TX = {"on":0, "bets":{}, "tai":0, "xiu":0, "msg":None}
WIN_RATE = 100
LOANS = {}

def E(t,d,c=BLUE):
    return discord.Embed(title=t, description=d, color=c)

def user(i,n="Thành viên"):
    if i not in U:
        U[i] = {
            "name":n, "cash":4899, "bank":0,
            "debt":0, "vip":0, "dd":0,
            "rate":100, "baddebt":0
        }
    return U[i]

def adm(c):
    return c.author.guild_permissions.administrator

def money(n):
    return f"{int(n):,}$"

async def blocked(c):
    u = user(c.author.id,c.author.name)
    if u["debt"] > 0:
        await c.send(
            f"🚫 **Bạn đang có khoản nợ {money(u['debt'])}!**\n"
            f"💡 Hãy trả nợ trước khi chơi."
        )
        return True
    return False

# ================= BOT =================

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Game("!trogiup | Casino")
    )
    print("ONLINE:",bot.user)

# ================= HELP =================

@bot.command(name="trogiup", aliases=["help"])
async def trogiup(c):
    await c.send(embed=E(
        "🎰 CASINO BET88",
        "`!tx tai 1000` `!tx xiu 1000`\n"
        "`!bc cua 1000` `!xd chan 1000`\n"
        "`!quay 1000`\n\n"

        "`!vi` `!gui 1000` `!rut 1000`\n"
        "`!chuyen @User 100` `!diemdanh`\n"
        "`!bxh` `!muarole Vip`\n\n"

        "💰 **VAY NGƯỜI CHƠI**\n"
        "`!vay @User 1000`\n"
        "`!trano @User 1000`\n\n"

        "👑 **ADMIN**\n"
        "`!taocode` `!thuongcode`\n"
        "`!settien` `!resettien`\n"
        "`!tyle 0-100`"
    ))

# ================= VI =================

@bot.command()
async def vi(c,m:discord.Member=None):
    m = m or c.author
    u = user(m.id,m.name)

    hang = (
        "👑 **Vương miện VIP**"
        if u["vip"] else
        "🐥 Người chơi Thường"
    )

    ten = (
        f"🟡 **{m.name}**"
        if u["vip"] else
        f"👤 **{m.name}**"
    )

    await c.send(embed=E(
        "💳 TÀI KHOẢN",
        f"{ten}\n"
        f"🏷️ Hạng: {hang}\n\n"
        f"💵 Ví: `{money(u['cash'])}`\n"
        f"🏦 Bank: `{money(u['bank'])}`\n"
        f"💸 Nợ: `{money(u['debt'])}`\n"
        f"🎯 Tỷ lệ thắng: `{u['rate']}%`\n\n"
        f"✨ **Chúc bạn may mắn!**",
        GOLD if u["vip"] else BLUE
    ))

# ================= GUI / RUT =================

@bot.command()
async def gui(c,n:int=None):
    u = user(c.author.id,c.author.name)

    if not n or n <= 0:
        return await c.send("❌ `!gui 1000`")

    if u["cash"] < n:
        return await c.send("❌ Không đủ tiền!")

    u["cash"] -= n
    u["bank"] += n

    await c.send(f"🏦 Gửi `{money(n)}` thành công!")

@bot.command()
async def rut(c,n:int=None):
    u = user(c.author.id,c.author.name)

    if not n or n <= 0:
        return await c.send("❌ `!rut 1000`")

    if u["bank"] < n:
        return await c.send("❌ Bank không đủ!")

    u["bank"] -= n
    u["cash"] += n

    await c.send(f"🏦 Rút `{money(n)}` thành công!")

# ================= CHUYEN =================

@bot.command()
async def chuyen(c,m:discord.Member=None,n:int=None):
    if not m or not n or n <= 0:
        return await c.send("❌ `!chuyen @User 100`")

    if m.id == c.author.id:
        return await c.send("❌ Không thể chuyển cho chính mình!")

    a = user(c.author.id,c.author.name)
    b = user(m.id,m.name)

    if a["cash"] < n:
        return await c.send("❌ Không đủ tiền!")

    a["cash"] -= n
    b["cash"] += n

    await c.send(
        f"💸 {c.author.mention} → {m.mention}: `{money(n)}`"
    )

# ================= DIEM DANH =================

@bot.command()
async def diemdanh(c):
    u = user(c.author.id,c.author.name)
    now = time.time()

    wait = 43200 - (now - u.get("dd",0))

    if wait > 0:
        s = int(wait)
        await c.send(
            f"⌛ **Mày đã điểm danh rồi!**\n"
            f"🕐 Đợi thêm **{s:,} giây** nữa."
        )
        return

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
        key=lambda z:z["cash"]+z["bank"],
        reverse=True
    )[:5]

    text = ""

    for i,u in enumerate(x,1):
        text += (
            f"\n**{i}.** {u['name']} "
            f"— `{money(u['cash']+u['bank'])}`"
        )

    await c.send(embed=E("🏆 TOP 5",text))

# ================= TAI XIU =================

@bot.command()
async def tx(c,ch=None,bet:int=None):

    if await blocked(c):
        return

    if ch not in ("tai","xiu") or not bet or bet <= 0:
        return await c.send(
            "❌ `!tx tai 1000` hoặc `!tx xiu 1000`"
        )

    if bet > 10_000_000:
        return await c.send(
            "❌ Max **10,000,000$/ván**!"
        )

    u = user(c.author.id,c.author.name)
    i = c.author.id

    if u["cash"] < bet:
        return await c.send("❌ Không đủ tiền!")

    if i in TX["bets"]:
        return await c.send("❌ Bạn đã cược ván này!")

    if not TX["on"]:

        TX.update(
            on=1,
            bets={},
            tai=0,
            xiu=0
        )

        TX["msg"] = await c.send(embed=E(
            "🎲 SÒNG TÀI XỈU 30S 🎲",

            "Gõ `!tx <tai/xiu> <tiền>` "
            "(Tối đa **10,000,000$/ván**)\n\n"
            "⏱️ **Thời gian: 30 giây**\n\n"
            "💰 Tổng Tài: `0$` | Tổng Xỉu: `0$`",

            ORANGE
        ))

        asyncio.create_task(txround())

    u["cash"] -= bet

    TX["bets"][i] = {
        "name":c.author.name,
        "choice":ch,
        "amount":bet
    }

    TX[ch] += bet

    await TX["msg"].edit(embed=E(
        "🎲 SÒNG TÀI XỈU 30S 🎲",

        "Gõ `!tx <tai/xiu> <tiền>` "
        "(Tối đa **10,000,000$/ván**)\n\n"
        "⏱️ **Đang nhận cược...**\n\n"
        f"💰 Tổng Tài: `{money(TX['tai'])}` | "
        f"Tổng Xỉu: `{money(TX['xiu'])}`",

        ORANGE
    ))

    try:
        await c.message.delete()
    except:
        pass

async def txround():

    await asyncio.sleep(30)

    d = [
        random.randint(1,6),
        random.randint(1,6),
        random.randint(1,6)
    ]

    total = sum(d)
    result = "tai" if total >= 11 else "xiu"

    w,l = [],[]

    for i,b in TX["bets"].items():

        u = user(i)

        chance = min(100, max(0,u["rate"]))

        # 0% = không thắng
        forced_win = (
            chance > 0 and
            random.randint(1,100) <= chance
        )

        win = b["choice"] == result and forced_win

        if win:

            p = b["amount"] * 2

            if u["vip"]:
                p = int(p * 1.5)

            u["cash"] += p

            w.append(
                f"• {b['name']} `+{money(p)}`"
            )

        else:

            l.append(
                f"• {b['name']} `-{money(b['amount'])}`"
            )

    await TX["msg"].edit(embed=E(
        "🎲 KẾT QUẢ TÀI XỈU",

        f"🎲 Xúc xắc\n"
        f"`[ {d[0]} ] - [ {d[1]} ] - [ {d[2]} ]`\n\n"
        f"➡️ **{total} điểm ({result.upper()})**\n\n"

        f"🎉 **THẮNG**\n"
        f"{chr(10).join(w) or 'Không có'}\n\n"

        f"💸 **THUA**\n"
        f"{chr(10).join(l) or 'Không có'}",

        GREEN if w else RED
    ))

    TX.update(
        on=0,
        bets={},
        tai=0,
        xiu=0,
        msg=None
    )

# ================= BAU CUA =================

@bot.command()
async def bc(c,ch=None,bet:int=None):

    if await blocked(c):
        return

    a = {
        "ca":"🐟",
        "tom":"🦐",
        "cua":"🦀",
        "bau":"🍐",
        "ga":"🐓",
        "nai":"🦌"
    }

    if ch not in a or not bet or bet <= 0:
        return await c.send("❌ `!bc cua 1000`")

    u = user(c.author.id,c.author.name)

    if u["cash"] < bet:
        return await c.send("❌ Không đủ tiền!")

    u["cash"] -= bet

    m = await c.send(embed=E(
        "🦀 BẦU CUA",
        "🎲 **LẮC... LẮC... LẮC...**\n\n"
        "`[ ❔ | ❔ | ❔ ]`",
        ORANGE
    ))

    await asyncio.sleep(1)

    await m.edit(embed=E(
        "🦀 BẦU CUA",
        "🎲 **LẮC... LẮC... LẮC...**\n\n"
        "🥁 **HÉ BÁT...**\n\n"
        "`[ ❔ | ❔ | ❔ ]`",
        ORANGE
    ))

    await asyncio.sleep(1)

    r = [random.choice(list(a)) for _ in range(3)]
    n = r.count(ch)

    if n:

        p = int(
            bet * (n+1) *
            (1.5 if u["vip"] else 1)
        )

        u["cash"] += p

        res = f"🎉 **THẮNG +{money(p)}**"
        co = GREEN

    else:

        res = f"💸 **THUA -{money(bet)}**"
        co = RED

    await m.edit(embed=E(
        "🦀 BẦU CUA",

        f"`[ {' | '.join(a[x] for x in r)} ]`\n\n"
        f"{res}\n"
        f"💵 Ví: `{money(u['cash'])}`",

        co
    ))

# ================= XD =================

@bot.command()
async def xd(c,ch=None,bet:int=None):

    if await blocked(c):
        return

    if ch not in ("chan","le") or not bet or bet <= 0:
        return await c.send(
            "❌ `!xd chan 1000` hoặc `!xd le 1000`"
        )

    u = user(c.author.id,c.author.name)

    if u["cash"] < bet:
        return await c.send("❌ Không đủ tiền!")

    u["cash"] -= bet

    m = await c.send(embed=E(
        "🪙 XÓC ĐĨA",
        "🟠 **XÓC... XÓC... XÓC...**\n\n"
        "`[ ⚪ | ⚪ | ⚪ | ⚪ ]`",
        ORANGE
    ))

    await asyncio.sleep(1.2)

    n = random.randint(0,4)

    cups = ["⚪"] * 4

    for i in random.sample(range(4),n):
        cups[i] = "🔴"

    r = "chan" if n % 2 == 0 else "le"

    chance = min(100,max(0,u["rate"]))

    win = (
        r == ch and
        chance > 0 and
        random.randint(1,100) <= chance
    )

    if win:

        p = int(
            bet * 2 *
            (1.5 if u["vip"] else 1)
        )

        u["cash"] += p

        res = f"🎉 **THẮNG +{money(p)}**"
        co = GREEN

    else:

        res = f"💸 **THUA -{money(bet)}**"
        co = RED

    await m.edit(embed=E(
        "🪙 XÓC ĐĨA",

        f"`[ {' | '.join(cups)} ]`\n\n"
        f"🎯 **{r.upper()}**\n\n"
        f"{res}\n"
        f"💵 Ví: `{money(u['cash'])}`",

        co
    ))

# ================= QUAY =================

@bot.command()
async def quay(c,bet:int=None):

    if await blocked(c):
        return

    if not bet or bet <= 0:
        return await c.send("❌ `!quay 1000`")

    u = user(c.author.id,c.author.name)

    if u["cash"] < bet:
        return await c.send("❌ Không đủ tiền!")

    u["cash"] -= bet

    m = await c.send(embed=E(
        "🎰 MÁY SLOT",
        "🎰 **ĐANG QUAY...**\n\n"
        "`[ ❔ | ❔ | ❔ ]`",
        ORANGE
    ))

    await asyncio.sleep(1.3)

    s = [
        random.choice(
            ["🍒","🍋","🔔","⭐","💎","7️⃣"]
        )
        for _ in range(3)
    ]

    same = max(s.count(x) for x in set(s))

    chance = min(100,max(0,u["rate"]))

    allowed = (
        chance > 0 and
        random.randint(1,100) <= chance
    )

    if same == 3 and allowed:

        p = int(
            bet * 5 *
            (1.5 if u["vip"] else 1)
        )

        u["cash"] += p

        res = f"🎉 **NỔ HŨ +{money(p)}**"
        co = GREEN

    elif same == 2 and allowed:

        p = int(
            bet * 2 *
            (1.5 if u["vip"] else 1)
        )

        u["cash"] += p

        res = f"🎉 **THẮNG +{money(p)}**"
        co = GREEN

    else:

        res = f"💸 **THUA -{money(bet)}**"
        co = RED

    await m.edit(embed=E(
        "🎰 MÁY SLOT",

        f"`[ {' | '.join(s)} ]`\n\n"
        f"{res}\n"
        f"💵 Ví: `{money(u['cash'])}`",

        co
    ))

# ================= VIP =================

@bot.command()
async def muarole(c,r=None):

    if (r or "").lower() != "vip":
        return await c.send("❌ `!muarole Vip`")

    u = user(c.author.id,c.author.name)

    if u["vip"]:
        return await c.send("💛 Bạn đã là VIP!")

    if u["cash"] < 30_000_000:
        return await c.send(
            "❌ VIP giá **30,000,000$**!"
        )

    role = discord.utils.find(
        lambda x:x.name.lower()=="vip",
        c.guild.roles
    )

    if not role:
        return await c.send(
            "❌ Server chưa có role `Vip`!"
        )

    if role >= c.guild.me.top_role:
        return await c.send(
            "❌ Kéo role Vip xuống dưới role Bot!"
        )

    u["cash"] -= 30_000_000
    u["vip"] = 1

    try:
        await c.author.add_roles(role)
    except:
        return await c.send(
            "❌ Bot thiếu quyền quản lý role!"
        )

    await c.send(embed=E(
        "👑 MUA VIP",

        f"🎉 {c.author.mention} đã trở thành "
        f"👑 **Vương miện VIP!**\n\n"
        f"💰 Giá: `30,000,000$`\n"
        f"💵 Thưởng game: **x1.5**\n"
        f"🟡 Tên: **Màu vàng**",

        GOLD
    ))

# ================= VAY =================

@bot.command()
async def vay(c,m:discord.Member=None,n:int=None):

    if not m or not n or n <= 0:
        return await c.send(
            "❌ Dùng: `!vay @User 1000`"
        )

    if m.id == c.author.id:
        return await c.send(
            "❌ Không thể vay chính mình!"
        )

    borrower = user(c.author.id,c.author.name)
    lender = user(m.id,m.name)

    if borrower["debt"] > 0:
        return await c.send(
            "❌ Bạn đang có khoản vay chưa trả!"
        )

    if lender["cash"] < n:
        return await c.send(
            "❌ Người cho vay không đủ tiền!"
        )

    lender["cash"] -= n
    borrower["cash"] += n
    borrower["debt"] = n

    loan_id = f"{c.author.id}_{m.id}_{int(time.time())}"

    LOANS[loan_id] = {
        "borrower":c.author.id,
        "lender":m.id,
        "amount":n,
        "time":time.time(),
        "bad":False
    }

    asyncio.create_task(
        loan_timer(loan_id)
    )

    await c.send(embed=E(
        "💰 KHOẢN VAY",
        f"👤 Người vay: {c.author.mention}\n"
        f"💰 Người cho vay: {m.mention}\n"
        f"💵 Số tiền: `{money(n)}`\n\n"
        f"⏱️ Thời hạn: **1 giờ**\n"
        f"⚠️ Quá hạn → **Nợ xấu -5% tỷ lệ thắng**",
        ORANGE
    ))

async def loan_timer(loan_id):

    await asyncio.sleep(3600)

    loan = LOANS.get(loan_id)

    if not loan:
        return

    borrower = user(loan["borrower"])

    if borrower["debt"] <= 0:
        return

    borrower["baddebt"] = 1
    borrower["rate"] = max(
        0,
        borrower["rate"] - 5
    )

    loan["bad"] = True

# ================= TRA NO =================

@bot.command()
async def trano(c,m:discord.Member=None,n:int=None):

    if not m or not n or n <= 0:
        return await c.send(
            "❌ Dùng: `!trano @User 1000`"
        )

    borrower = user(c.author.id,c.author.name)
    lender = user(m.id,m.name)

    if borrower["debt"] <= 0:
        return await c.send(
            "❌ Bạn không có khoản nợ!"
        )

    if lender["cash"] < 0:
        return await c.send(
            "❌ Người nhận tiền không hợp lệ!"
        )

    if n != borrower["debt"]:
        return await c.send(
            f"❌ Phải trả đủ **{money(borrower['debt'])}**!"
        )

    if borrower["cash"] < n:
        return await c.send(
            "❌ Ví không đủ tiền trả nợ!"
        )

    borrower["cash"] -= n
    lender["cash"] += n

    borrower["debt"] = 0

    # Nếu đã thành nợ xấu thì khôi phục 5%
    if borrower["baddebt"]:
        borrower["rate"] = min(
            100,
            borrower["rate"] + 5
        )
        borrower["baddebt"] = 0

    for k,v in list(LOANS.items()):
        if (
            v["borrower"] == c.author.id and
            v["lender"] == m.id
        ):
            del LOANS[k]
            break

    # Gỡ role Nợ xấu nếu server có
    role = discord.utils.find(
        lambda x:x.name.lower()=="nợ xấu",
        c.guild.roles
    )

    if role and role in c.author.roles:
        try:
            await c.author.remove_roles(role)
        except:
            pass

    await c.send(embed=E(
        "✅ TRẢ NỢ",
        f"👤 Người trả: {c.author.mention}\n"
        f"💰 Người nhận: {m.mention}\n"
        f"💵 Đã trả: `{money(n)}`\n\n"
        f"🎯 Tỷ lệ thắng hiện tại: **{borrower['rate']}%**",
        GREEN
    ))

# ================= TY LE ADMIN =================

@bot.command()
async def tyle(c,n:int=None):

    global WIN_RATE

    if not adm(c):
        return await c.send(
            "⛔ Chỉ Admin!"
        )

    if n is None or n < 0 or n > 100:
        return await c.send(
            "❌ Dùng `!tyle 0` đến `!tyle 100`"
        )

    WIN_RATE = n

    for u in U.values():
        u["rate"] = max(
            0,
            min(100, n - (5 if u["baddebt"] else 0))
        )

    await c.send(embed=E(
        "⚙️ CÀI TỶ LỆ THẮNG",
        f"🎯 Tỷ lệ hệ thống: **{n}%**\n\n"
        f"{'🚫 Không thắng.' if n==0 else '✅ Đã cập nhật tỷ lệ!'}",
        ORANGE
    ))

# ================= CODE =================

def newcode():
    return "BET-" + secrets.token_hex(3).upper()

@bot.command()
async def thuongcode(c,n:int=None,uses:int=None):

    if not adm(c):
        return await c.send("⛔ Chỉ Admin!")

    if not n or not uses:
        return await c.send(
            "❌ `!thuongcode 1000 5`"
        )

    x = newcode()

    C[x] = {
        "money":n,
        "uses":uses,
        "used":set()
    }

    await c.send(embed=E(
        "🎁 PHẦN THƯỞNG CODE",
        f"🔐 Mã: `{x}`\n"
        f"💰 Tiền: `{money(n)}`\n"
        f"👥 Lượt: `{uses}`",
        GREEN
    ))

@bot.command()
async def nhapcode(c,x=None):

    x = (x or "").upper()

    if x not in C:
        return await c.send(
            "❌ Code không tồn tại!"
        )

    z = C[x]

    if (
        c.author.id in z["used"] or
        len(z["used"]) >= z["uses"]
    ):
        return await c.send(
            "❌ Code hết lượt!"
        )

    z["used"].add(c.author.id)

    user(
        c.author.id,
        c.author.name
    )["cash"] += z["money"]

    await c.send(
        f"🎁 **+{money(z['money'])} vào ví!**"
    )

@bot.command()
async def taocode(c,n:int=None,uses:int=None):

    if not adm(c):
        return await c.send("⛔ Chỉ Admin!")

    if not n or not uses:
        return await c.send(
            "❌ `!taocode 1000 1`"
        )

    x = newcode()

    C[x] = {
        "money":n,
        "uses":uses,
        "used":set()
    }

    try:
        await c.author.send(
            f"🔐 `{x}` | 💰 `{money(n)}` | 👥 `{uses}`"
        )
    except:
        pass

    await c.send("✅ Code đã gửi DM!")

# ================= ADMIN TIEN =================

@bot.command()
async def settien(c,m:discord.Member=None,n:int=None):

    if not adm(c):
        return await c.send("⛔ Chỉ Admin!")

    if not m or n is None:
        return await c.send(
            "❌ `!settien @User 10000`"
        )

    user(m.id,m.name)["cash"] = max(0,n)

    await c.send(embed=E(
        "💰 SET TIỀN",
        f"👤 {m.mention}\n"
        f"💵 Ví mới: `{money(n)}`",
        GREEN
    ))

@bot.command()
async def resettien(c,m:discord.Member=None):

    if not adm(c):
        return await c.send("⛔ Chỉ Admin!")

    if not m:
        return await c.send(
            "❌ `!resettien @User`"
        )

    u = user(m.id,m.name)

    u["cash"] = 4899
    u["bank"] = 0

    await c.send(embed=E(
        "🔄 RESET TIỀN",
        f"👤 {m.mention}\n"
        f"💵 Ví: `4,899$`",
        ORANGE
    ))

# ================= TOKEN =================

token = os.getenv("TOKEN_BOT")

if token:
    bot.run(token)
else:
    print("❌ Chưa có TOKEN_BOT!")
