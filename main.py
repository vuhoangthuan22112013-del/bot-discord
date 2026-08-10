import os, asyncio, random, secrets, time, discord
from discord.ext import commands

I = discord.Intents.default()
I.message_content = True
bot = commands.Bot(command_prefix="!", intents=I, help_command=None)

U, C = {}, {}
DEFAULT = 4899
BLUE, ORANGE, GREEN, RED = 0x3498DB, 0xF1C40F, 0x2ECC71, 0xE74C3C

TX = {"on": False, "bets": {}, "tai": 0, "xiu": 0, "msg": None}

def E(t, d, c=BLUE):
    return discord.Embed(title=t, description=d, color=c)

def user(i, n="Thành viên"):
    if i not in U:
        U[i] = {
            "name": n, "cash": DEFAULT, "bank": 0,
            "hang": "Người chơi Thường",
            "ga": "Gà Công Nghiệp 🐥",
            "debt": 0, "due": 0, "dd": 0
        }
    return U[i]

def admin(ctx):
    return ctx.author.guild_permissions.administrator

async def blocked(ctx):
    u = user(ctx.author.id, ctx.author.name)
    if u["debt"] > 0 and time.time() > u["due"]:
        await ctx.send(embed=E(
            "🚫 CON NỢ",
            f"💳 Nợ: **{u['debt']:,}$**\n\n"
            "🚫 Không thể chơi casino khi chưa trả hết nợ.\n"
            f"💡 `!trano {u['debt']}`",
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
        "`!bc bau 1000` `!xd chan 1000` `!quay 1000`\n\n"
        "**💰 HỆ THỐNG**\n"
        "`!vi` `!gui 1000` `!rut 1000`\n"
        "`!chuyen @User 100` `!diemdanh` `!bxh`\n\n"
        "**🏦 VAY**\n"
        "`!vay 1000` `!no` `!trano 1000`\n\n"
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

    debt = (
        f"\n\n💳 **Khoản nợ:** `{u['debt']:,}$`"
        if u["debt"] else ""
    )

    await ctx.send(embed=E(
        f"💳 TÀI KHOẢN: {m.name.upper()}",
        f"🏷️ **Hạng thẻ**\n"
        f"👤 {u['hang']}\n\n"
        f"🐓 **Gà chiến**\n"
        f"{u['ga']}\n\n"
        f"💵 **Tiền mặt**\n"
        f"`{u['cash']:,}$`\n\n"
        f"🏦 **Két sắt**\n"
        f"`{u['bank']:,}$`"
        f"{debt}",
        BLUE
    ))

# ================= ĐIỂM DANH =================

@bot.command(name="diemdanh")
async def dd(ctx):
    u = user(ctx.author.id, ctx.author.name)
    now = time.time()

    if now - u["dd"] < 43200:
        left = int((43200 - (now - u["dd"])) / 3600)
        return await ctx.send(
            f"⏳ Đã điểm danh. Còn khoảng **{left} giờ**!"
        )

    u["dd"] = now
    u["cash"] += 2593

    await ctx.send(embed=E(
        "🎁 ĐIỂM DANH",
        f"💰 Nhận **+2,593$**\n"
        f"💵 Ví: `{u['cash']:,}$`",
        GREEN
    ))

# ================= TIỀN =================

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

@bot.command(name="bxh")
async def bxh(ctx):
    x = sorted(
        U.values(),
        key=lambda u: u["cash"] + u["bank"],
        reverse=True
    )[:5]

    s = "\n".join(
        f"{i+1}. **{u['name']}** — "
        f"`{u['cash'] + u['bank']:,}$`"
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
            "❌ Vay từ **1,000$ - 100,000$**!"
        )

    u["cash"] += n
    u["debt"] = n
    u["due"] = time.time() + 3600

    await ctx.send(embed=E(
        "💰 VAY TIỀN",
        f"🏦 Đã vay: **{n:,}$**\n"
        f"💵 Ví: `{u['cash']:,}$`\n"
        f"⏰ Thời hạn trả: **1 giờ**\n\n"
        "⚠️ Quá hạn sẽ bị khóa casino.",
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
        return await ctx.send(f"❌ `!trano {u['debt']}`")

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
    C[c] = {"money": n, "uses": uses, "used": set()}

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
    C[c] = {"money": n, "uses": uses, "used": set()}

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

    await ctx.send(f"✅ {m.mention}: `{n:,}$`")

@bot.command(name="resettien")
async def reset(ctx, m: discord.Member = None):
    if not admin(ctx):
        return await ctx.send("⛔ Chỉ Admin!")

    if not m:
        return await ctx.send("❌ `!resettien @User`")

    user(m.id, m.name)["cash"] = DEFAULT

    await ctx.send(f"🔄 {m.mention} → `{DEFAULT:,}$`")

# ================= TÀI XỈU =================

@bot.command()
async def tx(ctx, choice=None, bet: int = None):
    if await blocked(ctx):
        return

    if not choice or choice.lower() not in ("tai", "xiu") or not bet or bet <= 0:
        return await ctx.send("❌ `!tx tai 1000` hoặc `!tx xiu 1000`")

    choice = choice.lower()
    u = user(ctx.author.id, ctx.author.name)
    i = ctx.author.id

    if bet > 10_000_000:
        return await ctx.send("❌ Max **10,000,000$**!")

    if i in TX["bets"]:
        return await ctx.send("❌ Bạn đã cược ván này!")

    if u["cash"] < bet:
        return await ctx.send("❌ Không đủ tiền!")

    if not TX["on"]:
        TX.update(on=True, bets={}, tai=0, xiu=0)

        TX["msg"] = await ctx.send(embed=E(
            "🎲 SÒNG TÀI XỈU 30S 🎲",
            "🔴 **TÀI**\n"
            "`Đang nhận cược...`\n\n"
            "🔵 **XỈU**\n"
            "`Đang nhận cược...`\n\n"
            "⏱️ **30 giây**\n"
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

    await TX["msg"].edit(embed=E(
        "🎲 SÒNG TÀI XỈU 30S 🎲",
        "🔴 **TÀI** — đang nhận cược\n"
        "🔵 **XỈU** — đang nhận cược\n\n"
        "⏱️ **Đang mở phiên...**\n\n"
        f"💰 Tổng Tài: `{TX['tai']:,}$`\n"
        f"💰 Tổng Xỉu: `{TX['xiu']:,}$`",
        ORANGE
    ))

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

    await m.edit(embed=E(
        "🎲 KẾT QUẢ TÀI XỈU",
        "🥣 **XÓC... XÓC... XÓC...**\n\n"
        "`[ ❔ | ❔ | ❔ ]`",
        ORANGE
    ))

    await asyncio.sleep(2)

    d = [random.randint(1, 6) for _ in range(3)]
    total = sum(d)
    r = "tai" if total >= 11 else "xiu"

    win, lose = [], []

    for i, b in TX["bets"].items():
        if b["choice"] == r:
            money = b["amount"] * 2
            user(i)["cash"] += money
            win.append(
                f"• **{b['name']}** `+{money:,}$ vào ví`"
            )
        else:
            lose.append(
                f"• **{b['name']}** `-{b['amount']:,}$`"
            )

    await m.edit(embed=E(
        "🎲 KẾT QUẢ TÀI XỈU",
        f"`[ {d[0]} | {d[1]} | {d[2]} ]`\n\n"
        f"💥 **{total} — "
        f"{'TÀI 🔴' if r == 'tai' else 'XỈU 🔵'}**\n\n"
        "🎉 **THẮNG**\n"
        f"{chr(10).join(win) if win else 'Không có'}\n\n"
        "💸 **THUA**\n"
        f"{chr(10).join(lose) if lose else 'Không có'}",
        GREEN if win else RED
    ))

    TX.update(bets={}, tai=0, xiu=0, msg=None)

# ================= BẦU CUA =================

@bot.command()
async def bc(ctx, choice=None, bet: int = None):
    if await blocked(ctx):
        return

    icons = {
        "bau": "🍐",
        "cua": "🦀",
        "ca": "🐟",
        "tom": "🦐",
        "ga": "🐓",
        "nai": "🦌"
    }

    if not choice or choice.lower() not in icons or not bet or bet <= 0:
        return await ctx.send("❌ `!bc bau 1000`")

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < bet:
        return await ctx.send("❌ Không đủ tiền!")

    choice = choice.lower()
    u["cash"] -= bet

    m = await ctx.send(embed=E(
        "🦀 BẦU CUA CÁ TÔM",
        "🟠 **LẮC... LẮC... LẮC...**\n\n"
        "`[ ❔ | ❔ | ❔ ]`",
        ORANGE
    ))

    await asyncio.sleep(1.5)

    result = [random.choice(list(icons)) for _ in range(3)]
    count = result.count(choice)

    if count:
        money = bet * 2
        u["cash"] += money
        status = (
            "🎉 **THẮNG**\n"
            f"💰 **+{money:,}$ VÀO VÍ**"
        )
        color = GREEN
    else:
        status = (
            "💸 **THUA**\n"
            f"🔻 **-{bet:,}$**"
        )
        color = RED

    show = " | ".join(icons[x] for x in result)

    await m.edit(embed=E(
        "🦀 BẦU CUA CÁ TÔM",
        "**KẾT QUẢ**\n\n"
        f"`[ {show} ]`\n\n"
        f"{status}\n"
        f"💵 **Ví: `{u['cash']:,}$`**",
        color
    ))

# ================= XÓC ĐĨA 4 CỤC =================

@bot.command()
async def xd(ctx, choice=None, bet: int = None):
    if await blocked(ctx):
        return

    if not choice or choice.lower() not in ("chan", "le") or not bet or bet <= 0:
        return await ctx.send(
            "❌ `!xd chan 1000` hoặc `!xd le 1000`"
        )

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < bet:
        return await ctx.send("❌ Không đủ tiền!")

    choice = choice.lower()
    u["cash"] -= bet

    # CHỈ HIỆN XÓC TRƯỚC
    m = await ctx.send(embed=E(
        "🪙 XÓC ĐĨA",
        "🟠 **XÓC... XÓC... XÓC...**",
        ORANGE
    ))

    await asyncio.sleep(1.5)

    # ĐÚNG 4 CỤC
    balls = [
        random.choice(["🔴", "⚪"]),
        random.choice(["🔴", "⚪"]),
        random.choice(["🔴", "⚪"]),
        random.choice(["🔴", "⚪"])
    ]

    red = balls.count("🔴")

    result = "chan" if red % 2 == 0 else "le"
    win = result == choice

    if win:
        money = bet * 2
        u["cash"] += money

        status = (
            "🎉 **THẮNG**\n"
            f"💰 **+{money:,}$ VÀO VÍ**"
        )
        color = GREEN
    else:
        status = (
            "💸 **THUA**\n"
            f"🔻 **-{bet:,}$**"
        )
        color = RED

    show = " | ".join(balls)

    await m.edit(embed=E(
        "🪙 XÓC ĐĨA",
        "**KẾT QUẢ**\n\n"
        f"`[ {show} ]`\n\n"
        f"🎯 **{result.upper()}**\n\n"
        f"{status}\n"
        f"💵 **Ví: `{u['cash']:,}$`**",
        color
    ))

# ================= QUAY =================

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

    m = await ctx.send(embed=E(
        "🎰 MÁY SLOT NỔ HŨ",
        "🎰 **QUAY... QUAY... QUAY...**\n\n"
        "`[ ❔ | ❔ | ❔ ]`",
        ORANGE
    ))

    await asyncio.sleep(1.5)

    slots = ["🍒", "🍋", "🔔", "⭐", "💎", "7️⃣"]
    result = [random.choice(slots) for _ in range(3)]

    win = result[0] == result[1] == result[2]

    if win:
        money = bet * 2
        u["cash"] += money

        status = (
            "🎉 **THẮNG!**\n"
            f"💰 **+{money:,}$ VÀO VÍ**"
        )
        color = GREEN
    else:
        status = (
            "💸 **THUA**\n"
            f"🔻 **-{bet:,}$**"
        )
        color = RED

    show = " | ".join(result)

    await m.edit(embed=E(
        "🎰 MÁY SLOT NỔ HŨ",
        "**KẾT QUẢ**\n\n"
        f"`[ {show} ]`\n\n"
        f"{status}\n"
        f"💵 **Ví: `{u['cash']:,}$`**",
        color
    ))

# ================= RUN =================

token = os.getenv("TOKEN_BOT")

if not token:
    print("❌ Chưa có TOKEN_BOT!")
else:
    bot.run(token)
