import os, asyncio, random, secrets, time, discord
from discord.ext import commands

I = discord.Intents.default()
I.message_content = True
bot = commands.Bot(command_prefix="!", intents=I, help_command=None)

U, C = {}, {}
DEFAULT = 4899
BLUE, ORANGE, GREEN, RED = 0x3498DB, 0xF1C40F, 0x2ECC71, 0xE74C3C

TX = {
    "on": False,
    "bets": {},
    "tai": 0,
    "xiu": 0,
    "msg": None
}

def E(t, d, c=BLUE):
    return discord.Embed(title=t, description=d, color=c)

def user(i, n="Thành viên"):
    if i not in U:
        U[i] = {
            "name": n,
            "cash": DEFAULT,
            "bank": 0,
            "hang": "Người chơi Thường",
            "ga": "Gà Công Nghiệp 🐥",
            "debt": 0,
            "due": 0
        }
    return U[i]

def admin(ctx):
    return ctx.author.guild_permissions.administrator

async def blocked(ctx):
    u = user(ctx.author.id, ctx.author.name)

    if u["debt"] > 0:
        if time.time() > u["due"]:
            await ctx.send(embed=E(
                "🚫 CON NỢ",
                f"💳 Nợ: **{u['debt']:,}$**\n\n"
                f"🚫 Bạn không thể chơi casino.\n"
                f"💡 Dùng `!trano {u['debt']}` để trả nợ.",
                RED
            ))
            return True

    return False

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Game("!trogiup | Casino Bet88")
    )
    print("BOT ONLINE:", bot.user)

# ================= HELP =================

@bot.command(name="trogiup", aliases=["help"])
async def help(ctx):
    await ctx.send(embed=E(
        "🎰 CASINO BET88",
        "**🎲 CASINO**\n"
        "`!tx tai 1000` `!tx xiu 1000`\n"
        "`!bc cua 1000` `!xd chan 1000` `!quay 1000`\n\n"
        "**💰 TIỀN**\n"
        "`!vi` `!gui 1000` `!rut 1000`\n"
        "`!chuyen @User 100`\n"
        "`!diemdanh` `!bxh`\n\n"
        "**🏦 VAY TIỀN**\n"
        "`!vay 1000`\n"
        "`!trano 1000`\n"
        "`!no`\n\n"
        "**👑 ADMIN**\n"
        "`!taocode 10000 1`\n"
        "`!thuongcode 10000 10`\n"
        "`!settien @User 10000`\n"
        "`!resettien @User`"
    ))

# ================= VÍ =================

@bot.command(name="vi", aliases=["bal", "money"])
async def vi(ctx, m: discord.Member = None):
    m = m or ctx.author
    u = user(m.id, m.name)

    debt = ""
    if u["debt"] > 0:
        debt = f"\n\n💳 **Khoản nợ:** `{u['debt']:,}$`"

    await ctx.send(embed=E(
        f"💳 TÀI KHOẢN: {m.name.upper()}",
        f"**🏷️ Hạng thẻ**\n"
        f"👤 {u['hang']}\n\n"
        f"**🐓 Gà chiến**\n"
        f"{u['ga']}\n\n"
        f"**💵 Tiền mặt**\n"
        f"`{u['cash']:,}$`\n\n"
        f"**🏦 Két sắt**\n"
        f"`{u['bank']:,}$`"
        f"{debt}",
        BLUE
    ))

# ================= ĐIỂM DANH =================

@bot.command(name="diemdanh")
async def dd(ctx):
    u = user(ctx.author.id, ctx.author.name)
    now = time.time()

    if now - u.get("dd", 0) < 43200:
        left = int((43200 - (now - u.get("dd", 0))) / 3600)
        return await ctx.send(
            f"⏳ Bạn đã điểm danh. Còn khoảng **{left} giờ**!"
        )

    u["dd"] = now
    u["cash"] += 2593

    await ctx.send(embed=E(
        "🎁 ĐIỂM DANH",
        f"💰 Nhận **+2,593$**\n"
        f"💵 Ví: `{u['cash']:,}$`",
        GREEN
    ))

# ================= GỬI / RÚT =================

@bot.command()
async def gui(ctx, n: int = None):
    u = user(ctx.author.id, ctx.author.name)

    if not n or n <= 0 or u["cash"] < n:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"] -= n
    u["bank"] += n

    await ctx.send(embed=E(
        "🏦 GỬI TIỀN",
        f"💰 Gửi: `{n:,}$`\n"
        f"🏦 Bank: `{u['bank']:,}$`",
        GREEN
    ))

@bot.command()
async def rut(ctx, n: int = None):
    u = user(ctx.author.id, ctx.author.name)

    if not n or n <= 0 or u["bank"] < n:
        return await ctx.send("❌ Bank không đủ!")

    u["bank"] -= n
    u["cash"] += n

    await ctx.send(embed=E(
        "🏦 RÚT TIỀN",
        f"💰 Rút: `{n:,}$`\n"
        f"💵 Ví: `{u['cash']:,}$`",
        GREEN
    ))

# ================= CHUYỂN =================

@bot.command()
async def chuyen(ctx, m: discord.Member = None, n: int = None):
    if not m or not n or n <= 0 or m.bot or m.id == ctx.author.id:
        return await ctx.send("❌ `!chuyen @User 100`")

    a = user(ctx.author.id, ctx.author.name)
    b = user(m.id, m.name)

    if a["cash"] < n:
        return await ctx.send("❌ Không đủ tiền!")

    a["cash"] -= n
    b["cash"] += n

    await ctx.send(embed=E(
        "💸 CHUYỂN TIỀN",
        f"{ctx.author.mention} → {m.mention}\n"
        f"💰 `{n:,}$`",
        GREEN
    ))

# ================= BXH =================

@bot.command(name="bxh")
async def bxh(ctx):
    x = sorted(
        U.values(),
        key=lambda u: u["cash"] + u["bank"],
        reverse=True
    )[:5]

    s = "\n".join(
        f"{i+1}. **{u['name']}** — `{u['cash']+u['bank']:,}$`"
        for i, u in enumerate(x)
    )

    await ctx.send(embed=E("🏆 TOP 5 GIÀU NHẤT", s))

# ================= VAY =================

@bot.command(name="vay")
async def vay(ctx, n: int = None):
    u = user(ctx.author.id, ctx.author.name)

    if u["debt"] > 0:
        return await ctx.send("🚫 Bạn đang có khoản nợ!")

    if not n or n < 1000 or n > 100000:
        return await ctx.send(
            "❌ Số tiền vay từ **1,000$ - 100,000$**!"
        )

    u["cash"] += n
    u["debt"] = n
    u["due"] = time.time() + 3600

    await ctx.send(embed=E(
        "💰 VAY TIỀN",
        f"🏦 Đã vay: **{n:,}$**\n"
        f"💵 Ví: `{u['cash']:,}$`\n"
        f"⏰ Thời hạn: **1 giờ**",
        ORANGE
    ))

@bot.command(name="no")
async def no(ctx):
    u = user(ctx.author.id, ctx.author.name)

    if not u["debt"]:
        return await ctx.send("✅ Bạn không có khoản nợ.")

    left = max(0, int(u["due"] - time.time()))
    h = left // 3600
    m = (left % 3600) // 60

    await ctx.send(embed=E(
        "💳 KHOẢN NỢ",
        f"💰 Nợ: **{u['debt']:,}$**\n"
        f"⏰ Còn: **{h} giờ {m} phút**\n\n"
        f"💡 `!trano {u['debt']}`",
        RED if left == 0 else ORANGE
    ))

@bot.command(name="trano")
async def trano(ctx, n: int = None):
    u = user(ctx.author.id, ctx.author.name)

    if u["debt"] <= 0:
        return await ctx.send("✅ Bạn không có khoản nợ.")

    if not n or n <= 0:
        return await ctx.send(
            f"❌ `!trano {u['debt']}`"
        )

    n = min(n, u["debt"])

    if u["cash"] < n:
        return await ctx.send("❌ Ví không đủ tiền!")

    u["cash"] -= n
    u["debt"] -= n

    if u["debt"] == 0:
        u["due"] = 0

    await ctx.send(embed=E(
        "💳 TRẢ NỢ",
        f"💰 Đã trả: **{n:,}$**\n"
        f"💳 Còn nợ: `{u['debt']:,}$`\n"
        f"💵 Ví: `{u['cash']:,}$`",
        GREEN if u["debt"] == 0 else ORANGE
    ))

# ================= CODE =================

def newcode():
    return "BET-" + secrets.token_hex(3).upper()

@bot.command()
async def taocode(ctx, n: int = None, uses: int = None):
    if not admin(ctx):
        return await ctx.send("⛔ Chỉ Admin!")

    if not n or not uses:
        return await ctx.send("❌ `!taocode tiền lượt`")

    c = newcode()

    C[c] = {
        "money": n,
        "uses": uses,
        "used": set()
    }

    try:
        await ctx.author.send(embed=E(
            "🔐 CODE ADMIN",
            f"🎟️ `{c}`\n"
            f"💰 `{n:,}$`\n"
            f"🔢 `{uses}` lượt"
        ))
        await ctx.send("✅ Code đã gửi DM.")
    except:
        await ctx.send(f"🔐 Code: `{c}`")

@bot.command()
async def thuongcode(ctx, n: int = None, uses: int = None):
    if not admin(ctx):
        return await ctx.send("⛔ Chỉ Admin!")

    if not n or not uses:
        return await ctx.send("❌ `!thuongcode tiền lượt`")

    c = newcode()

    C[c] = {
        "money": n,
        "uses": uses,
        "used": set()
    }

    await ctx.send(embed=E(
        "🎁 CODE THƯỞNG",
        f"🎟️ **{c}**\n"
        f"💰 **{n:,}$**\n"
        f"👥 **{uses} lượt**\n\n"
        f"`!nhapcode {c}`",
        GREEN
    ))

@bot.command()
async def nhapcode(ctx, c=None):
    if not c or c.upper() not in C:
        return await ctx.send("❌ Code không tồn tại!")

    data = C[c.upper()]
    i = ctx.author.id

    if i in data["used"]:
        return await ctx.send("❌ Bạn đã dùng code!")

    if len(data["used"]) >= data["uses"]:
        return await ctx.send("❌ Code hết lượt!")

    data["used"].add(i)
    user(i, ctx.author.name)["cash"] += data["money"]

    await ctx.send(embed=E(
        "🎁 NHẬP CODE THÀNH CÔNG",
        f"💰 Nhận **+{data['money']:,}$**",
        GREEN
    ))

@bot.command()
async def settien(ctx, m: discord.Member = None, n: int = None):
    if not admin(ctx):
        return await ctx.send("⛔ Chỉ Admin!")

    if not m or n is None:
        return await ctx.send("❌ `!settien @User tiền`")

    user(m.id, m.name)["cash"] = max(0, n)

    await ctx.send(
        f"✅ {m.mention}: `{n:,}$`"
    )

@bot.command(name="resettien")
async def reset(ctx, m: discord.Member = None):
    if not admin(ctx):
        return await ctx.send("⛔ Chỉ Admin!")

    if not m:
        return await ctx.send("❌ `!resettien @User`")

    user(m.id, m.name)["cash"] = DEFAULT

    await ctx.send(
        f"🔄 {m.mention} → `{DEFAULT:,}$`"
    )

# ================= TÀI XỈU =================

@bot.command()
async def tx(ctx, choice=None, bet: int = None):
    if await blocked(ctx):
        return

    if (
        not choice
        or choice.lower() not in ("tai", "xiu")
        or not bet
        or bet <= 0
    ):
        return await ctx.send(
            "❌ `!tx tai 1000` hoặc `!tx xiu 1000`"
        )

    choice = choice.lower()
    u = user(ctx.author.id, ctx.author.name)
    i = ctx.author.id

    if bet > 10_000_000:
        return await ctx.send(
            "❌ Cược max **10,000,000$**!"
        )

    if i in TX["bets"]:
        return await ctx.send(
            "❌ Bạn đã cược ván này!"
        )

    if u["cash"] < bet:
        return await ctx.send("❌ Không đủ tiền!")

    # MỞ PHIÊN
    if not TX["on"]:
        TX.update(
            on=True,
            bets={},
            tai=0,
            xiu=0
        )

        TX["msg"] = await ctx.send(embed=E(
            "🎲 SÒNG TÀI XỈU 30S 🎲",
            "Gõ `!tx <tai/xiu> <tiền>`\n"
            "💰 Tối đa **10,000,000$/ván**\n\n"
            "⏱️ **Thời gian: 30 giây**\n\n"
            "💰 Tổng Tài: `0$` | Tổng Xỉu: `0$`",
            ORANGE
        ))

        asyncio.create_task(txround())

    u["cash"] -= bet

    TX["bets"][i] = {
        "name": ctx.author.name,
        "choice": choice,
        "amount": bet
    }

    TX[choice] += bet

    await TX["msg"].edit(
        embed=E(
            "🎲 SÒNG TÀI XỈU 30S 🎲",
            "Gõ `!tx <tai/xiu> <tiền>`\n"
            "💰 Tối đa **10,000,000$/ván**\n\n"
            "⏱️ **Đang nhận cược...**\n\n"
            f"💰 Tổng Tài: `{TX['tai']:,}$` | "
            f"Tổng Xỉu: `{TX['xiu']:,}$`",
            ORANGE
        )
    )

    try:
        await ctx.message.delete()
    except:
        pass

async def txround():
    await asyncio.sleep(30)

    if not TX["on"]:
        return

    TX["on"] = False
    m = TX["msg"]

    await m.edit(
        embed=E(
            "🎲 KẾT QUẢ TÀI XỈU",
            "🥣 **XÓC... XÓC... XÓC...**\n\n"
            "`[ ❔ | ❔ | ❔ ]`",
            ORANGE
        )
    )

    await asyncio.sleep(2)

    d = [
        random.randint(1, 6),
        random.randint(1, 6),
        random.randint(1, 6)
    ]

    total = sum(d)
    r = "tai" if total >= 11 else "xiu"

    win = []
    lose = []

    for i, b in TX["bets"].items():
        if b["choice"] == r:
            user(i)["cash"] += b["amount"] * 2
            win.append(
                f"• {b['name']} `+{b['amount']*2:,}$ vào ví`"
            )
        else:
            lose.append(
                f"• {b['name']} `-{b['amount']:,}$`"
            )

    await m.edit(
        embed=E(
            "🎲 KẾT QUẢ TÀI XỈU",
            f"**Xúc xắc**\n"
            f"`[ {d[0]} | {d[1]} | {d[2]} ]`\n\n"
            f"➡️ **{total} điểm "
            f"({'TÀI 🔴' if r == 'tai' else 'XỈU 🔵'})**\n\n"
            f"🎉 **THẮNG**\n"
            f"{chr(10).join(win) if win else 'Không có'}\n\n"
            f"💸 **THUA**\n"
            f"{chr(10).join(lose) if lose else 'Không có'}",
            GREEN if win else RED
        )
    )

    TX.update(
        bets={},
        tai=0,
        xiu=0,
        msg=None
    )

# ================= BẦU CUA =================

@bot.command()
async def bc(ctx, choice=None, bet: int = None):
    if await blocked(ctx):
        return

    icons = {
        "ca": "🐟",
        "tom": "🦐",
        "cua": "🦀",
        "bau": "🍐",
        "ga": "🐓",
        "nai": "🦌"
    }

    if (
        not choice
        or choice.lower() not in icons
        or not bet
        or bet <= 0
    ):
        return await ctx.send(
            "❌ `!bc bau 1000`\n"
            "`ca/tom/cua/bau/ga/nai`"
        )

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"] -= bet
    choice = choice.lower()

    m = await ctx.send(
        embed=E(
            "🦀 BẦU CUA TÔM CÁ",
            "🟠 **LẮC... LẮC... LẮC...**\n\n"
            "`[ ❔ | ❔ | ❔ ]`",
            ORANGE
        )
    )

    await asyncio.sleep(1.5)

    r = [
        random.choice(list(icons)),
        random.choice(list(icons)),
        random.choice(list(icons))
    ]

    n = r.count(choice)

    if n:
        u["cash"] += bet * (n + 1)

    result_icons = (
        f"**{icons[r[0]]}  |  {icons[r[1]]}  |  {icons[r[2]]}**"
    )

    if n:
        result = (
            f"🎉 **THẮNG +{bet*n:,}$ VÀO VÍ**\n"
            f"💵 Ví: `{u['cash']:,}$`"
        )
    else:
        result = (
            f"💸 **TRẬT LẮT! -{bet:,}$**\n"
            f"💵 Ví: `{u['cash']:,}$`"
        )

    await m.edit(
        embed=E(
            "🦀 BẦU CUA TÔM CÁ",
            f"**KẾT QUẢ**\n\n"
            f"{result_icons}\n\n"
            f"**TỔNG KẾT**\n"
            f"{result}",
            GREEN if n else RED
        )
    )

# ================= XÓC ĐĨA =================

@bot.command()
async def xd(ctx, choice=None, bet: int = None):
    if await blocked(ctx):
        return

    if (
        not choice
        or choice.lower() not in ("chan", "le")
        or not bet
        or bet <= 0
    ):
        return await ctx.send(
            "❌ `!xd chan 1000` hoặc `!xd le 1000`"
        )

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"] -= bet
    choice = choice.lower()

    m = await ctx.send(
        embed=E(
            "🪙 XÓC ĐĨA",
            "🟠 **XÓC... XÓC... XÓC...**\n\n"
            "`[ ⚪ | ⚪ | ⚪ | ⚪ ]`",
            ORANGE
        )
    )

    await asyncio.sleep(1.5)

    n = random.randint(0, 4)
    r = "chan" if n % 2 == 0 else "le"
    win = r == choice

    if win:
        u["cash"] += bet * 2

    balls = " | ".join(
        "🔴" if i < n else "⚪"
        for i in range(4)
    )

    if win:
        result = (
            f"🎉 **THẮNG**\n"
            f"💰 **+{bet*2:,}$ VÀO VÍ**\n"
            f"💵 Ví: `{u['cash']:,}$`"
        )
    else:
        result = (
            f"💸 **THUA**\n"
            f"💰 **-{bet:,}$**\n"
            f"💵 Ví: `{u['cash']:,}$`"
        )

    await m.edit(
        embed=E(
            "🪙 XÓC ĐĨA",
            f"**KẾT QUẢ**\n\n"
            f"**{balls}**\n\n"
            f"🎯 **{r.upper()}**\n\n"
            f"{result}",
            GREEN if win else RED
        )
    )

# ================= SLOT =================

@bot.command()
async def quay(ctx, bet: int = None):
    if await blocked(ctx):
        return

    if not bet or bet <= 0:
        return await ctx.send("❌ `!quay 1000`")

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"] -= bet

    m = await ctx.send(
        embed=E(
            "🎰 MÁY SLOT NỔ HŨ",
            "🟠 **QUAY... QUAY... QUAY...**\n\n"
            "`[ ❔ | ❔ | ❔ ]`",
            ORANGE
        )
    )

    await asyncio.sleep(1)

    s = [
        random.choice(
            ["🍒", "🍋", "🔔", "⭐", "💎", "7️⃣"]
        )
        for _ in range(3)
    ]

    win = s[0] == s[1] == s[2]

    if win:
        u["cash"] += bet * 5

    result_icons = (
        f"**{s[0]}  |  {s[1]}  |  {s[2]}**"
    )

    if win:
        result = (
            f"🎉 **NỔ HŨ!**\n"
            f"💰 **+{bet*5:,}$ VÀO VÍ**\n"
            f"💵 Ví: `{u['cash']:,}$`"
        )
    else:
        result = (
            f"💸 **TRẬT HŨ!**\n"
            f"💰 **-{bet:,}$**\n"
            f"💵 Ví: `{u['cash']:,}$`"
        )

    await m.edit(
        embed=E(
            "🎰 MÁY SLOT NỔ HŨ",
            f"**KẾT QUẢ**\n\n"
            f"{result_icons}\n\n"
            f"**THÔNG BÁO**\n"
            f"{result}",
            GREEN if win else RED
        )
    )

# ================= RUN =================

token = os.getenv("TOKEN_BOT")

if not token:
    print("❌ Chưa có TOKEN_BOT!")
else:
    bot.run(token)
