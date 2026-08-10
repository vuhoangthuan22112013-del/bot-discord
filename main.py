import os, asyncio, random, time, discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

users = {}
cooldowns = {}
diemdanh = {}
codes = {}

BLUE, ORANGE, GREEN, RED = 0x3498DB, 0xF1C40F, 0x2ECC71, 0xE74C3C

tx = {"active": False, "bets": {}, "tai": 0, "xiu": 0}


def embed(title, text, color=BLUE):
    return discord.Embed(title=title, description=text, color=color)


def user(uid, name):
    if uid not in users:
        users[uid] = {
            "name": name, "cash": 4899, "bank": 0,
            "last_interest": time.time()
        }
    users[uid]["name"] = name
    return users[uid]


def interest(u):
    now = time.time()
    days = int((now - u.get("last_interest", now)) / 86400)
    if days > 0:
        u["bank"] = int(u["bank"] * (1.02 ** days))
        u["last_interest"] += days * 86400


def cd(uid, cmd, sec=1.5):
    key = f"{uid}_{cmd}"
    now = time.time()
    if key in cooldowns and now - cooldowns[key] < sec:
        return round(sec - (now - cooldowns[key]), 1)
    cooldowns[key] = now
    return 0


@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino Bet88")
    )
    print(f"✅ ONLINE: {bot.user}")


# =========================
# TRỢ GIÚP
# =========================

@bot.command(name="trogiup", aliases=["help"])
async def help_cmd(ctx):
    e = embed(
        "🎰 CASINO BET88 - TRỢ GIÚP",
        "⚔️ **ĐỐI KHÁNG (PVP)**\n"
        "`!danhbai` `!thachdau` `!dagapvp` `!tuxipvp @User`\n\n"
        "🎲 **CASINO (SOLO)**\n"
        "`!tx` `!daga` `!tuxi` `!bc` `!xd`\n"
        "`!bai` `!rl` `!quay` `!duangua` `!coinflip`\n\n"
        "🏛️ **HỆ THỐNG**\n"
        "`!vi` `!gui` `!rut` `!chuyen`\n"
        "`!diemdanh` `!bxh` `!nhapcode`",
        BLUE
    )
    e.set_footer(text="🎁 Chúc bạn may mắn tại Casino Bet88!")
    await ctx.send(embed=e)


# =========================
# VÍ
# =========================

@bot.command(name="vi", aliases=["money", "bal"])
async def vi(ctx, member: discord.Member = None):
    target = member or ctx.author
    u = user(target.id, target.name)
    interest(u)

    e = embed(
        "💳 THÔNG TIN TÀI KHOẢN",
        f"👤 **Chủ tài khoản:** {target.name.upper()}\n\n"
        f"🏷️ **Hạng thẻ:** Người chơi Thường\n"
        f"🐓 **Gà chiến:** Gà Công Nghiệp 🐥\n\n"
        f"💵 **Tiền mặt:** `{u['cash']:,}$`\n"
        f"🏦 **Két sắt:** `{u['bank']:,}$`\n"
        f"📈 **Lãi ngân hàng:** `2% / ngày`",
        BLUE
    )
    await ctx.send(embed=e)


# =========================
# NGÂN HÀNG
# =========================

@bot.command(name="gui")
async def gui(ctx, amount: int = None):
    u = user(ctx.author.id, ctx.author.name)
    interest(u)

    if not amount or amount <= 0:
        return await ctx.send("❌ Dùng: `!gui 1000`")

    if u["cash"] < amount:
        return await ctx.send(f"❌ Ví chỉ còn `{u['cash']:,}$`.")

    u["cash"] -= amount
    u["bank"] += amount

    await ctx.send(embed=embed(
        "🏦 GỬI TIỀN NGÂN HÀNG",
        f"👤 {ctx.author.mention}\n\n"
        f"💵 Đã gửi: **{amount:,}$**\n"
        f"🏦 Ngân hàng: **{u['bank']:,}$**\n"
        f"📈 Lãi suất: **2% / ngày**",
        BLUE
    ))


@bot.command(name="rut")
async def rut(ctx, amount: int = None):
    u = user(ctx.author.id, ctx.author.name)
    interest(u)

    if not amount or amount <= 0:
        return await ctx.send("❌ Dùng: `!rut 1000`")

    if u["bank"] < amount:
        return await ctx.send(f"❌ Bank chỉ có `{u['bank']:,}$`.")

    u["bank"] -= amount
    u["cash"] += amount

    await ctx.send(embed=embed(
        "🏦 RÚT TIỀN",
        f"👤 {ctx.author.mention}\n\n"
        f"💵 Đã rút: **{amount:,}$**\n"
        f"💰 Tiền mặt: **{u['cash']:,}$**\n"
        f"🏦 Ngân hàng: **{u['bank']:,}$**",
        BLUE
    ))


@bot.command(name="chuyen")
async def chuyen(ctx, member: discord.Member = None, amount: int = None):
    if not member or not amount or amount <= 0:
        return await ctx.send("❌ Dùng: `!chuyen @User 1000`")

    if member.id == ctx.author.id:
        return await ctx.send("❌ Không thể chuyển cho chính mình!")

    if member.bot:
        return await ctx.send("❌ Không thể chuyển cho bot!")

    a = user(ctx.author.id, ctx.author.name)
    b = user(member.id, member.name)
    interest(a)
    interest(b)

    if a["cash"] < amount:
        return await ctx.send(f"❌ Ví chỉ còn `{a['cash']:,}$`.")

    a["cash"] -= amount
    b["cash"] += amount

    await ctx.send(embed=embed(
        "💸 CHUYỂN TIỀN",
        f"👤 Người gửi: {ctx.author.mention}\n"
        f"👤 Người nhận: {member.mention}\n\n"
        f"💰 Số tiền: **{amount:,}$**\n"
        f"💵 Ví còn: **{a['cash']:,}$**",
        BLUE
    ))


# =========================
# BXH
# =========================

@bot.command(name="bxh")
async def bxh(ctx):
    if not users:
        return await ctx.send("❌ Chưa có người chơi.")

    data = []
    for uid, u in users.items():
        interest(u)
        data.append((u["name"], u["cash"] + u["bank"], u["cash"], u["bank"]))

    data.sort(key=lambda x: x[1], reverse=True)

    medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    text = ""

    for i, (name, total, cash, bank) in enumerate(data[:5]):
        text += (
            f"{medal[i]} **{name}**\n"
            f"💰 Tổng: `{total:,}$` | "
            f"💵 Ví: `{cash:,}$` | 🏦 Bank: `{bank:,}$`\n\n"
        )

    await ctx.send(embed=embed(
        "🏆 TOP 5 NGƯỜI GIÀU NHẤT",
        text,
        BLUE
    ))


# =========================
# ĐIỂM DANH
# =========================

@bot.command(name="diemdanh")
async def diem_cmd(ctx):
    uid = ctx.author.id
    now = time.time()

    if uid in diemdanh and now - diemdanh[uid] < 43200:
        return await ctx.send("⚠️ Bạn đã điểm danh trong 12 giờ qua!")

    diemdanh[uid] = now
    u = user(uid, ctx.author.name)

    reward = 2593
    u["cash"] += reward

    await ctx.send(embed=embed(
        "🎁 ĐIỂM DANH THÀNH CÔNG",
        f"👤 {ctx.author.mention}\n"
        f"💰 Nhận được: **+{reward:,}$**\n"
        f"💵 Ví: `{u['cash']:,}$`",
        GREEN
    ))


# =========================
# NHẬP CODE
# =========================

@bot.command(name="nhapcode")
async def nhapcode(ctx, code: str = None):
    if not code:
        return await ctx.send("❌ Dùng: `!nhapcode CODE`")

    code = code.upper()
    if code not in codes:
        return await ctx.send("❌ Code không tồn tại hoặc đã hết!")

    used = codes[code].setdefault("used", set())

    if ctx.author.id in used:
        return await ctx.send("❌ Bạn đã dùng code này rồi!")

    reward = codes[code]["money"]
    used.add(ctx.author.id)

    u = user(ctx.author.id, ctx.author.name)
    u["cash"] += reward

    await ctx.send(embed=embed(
        "🎁 NHẬP CODE THÀNH CÔNG",
        f"🎟️ Code: `{code}`\n"
        f"💰 Phần thưởng: **+{reward:,}$**\n"
        f"💵 Ví: `{u['cash']:,}$`",
        GREEN
    ))


# ADMIN TẠO CODE
@bot.command(name="taocode")
@commands.has_permissions(administrator=True)
async def taocode(ctx, code: str = None, money: int = None):
    if not code or not money or money <= 0:
        return await ctx.send("❌ Dùng: `!taocode BET88 10000`")

    code = code.upper()
    codes[code] = {"money": money, "used": set()}

    await ctx.send(
        f"✅ Đã tạo code `{code}` → **{money:,}$**"
    )


# =========================
# SLOT
# =========================

@bot.command(name="quay")
async def quay(ctx, bet: int = None):
    if cd(ctx.author.id, "quay"):
        return await ctx.send("⚠️ Chờ một chút!")

    if not bet or bet <= 0:
        return await ctx.send("❌ Dùng: `!quay 100`")

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"] -= bet
    s = ["🍋", "🔔", "🍒", "⭐", "💎"]

    a, b, c = random.choice(s), random.choice(s), random.choice(s)

    e = embed(
        "🎰 MÁY SLOT BET88",
        f"🟠 **ĐANG QUAY...**\n\n`[ {a} ] [ ❔ ] [ ❔ ]`",
        ORANGE
    )

    msg = await ctx.send(embed=e)
    await asyncio.sleep(.6)

    e.description = f"🟠 **ĐANG QUAY...**\n\n`[ {a} ] [ {b} ] [ ❔ ]`"
    await msg.edit(embed=e)
    await asyncio.sleep(.7)

    if a == b == c:
        reward = bet * 4
        u["cash"] += bet + reward
        e = embed(
            "🎰 MÁY SLOT BET88",
            f"`[ {a} ] [ {b} ] [ {c} ]`\n\n"
            f"✨ **NỔ HŨ!**\n💰 Nhận **+{reward:,}$**",
            GREEN
        )
    else:
        e = embed(
            "🎰 MÁY SLOT BET88",
            f"`[ {a} ] [ {b} ] [ {c} ]`\n\n"
            f"💸 **TRẬT HŨ!**\nMất **-{bet:,}$**",
            RED
        )

    await msg.edit(embed=e)


# =========================
# TÀI XỈU
# =========================

@bot.command(name="tx", aliases=["taixiu"])
async def taixiu(ctx, choice: str = None, bet: int = None):
    uid = ctx.author.id
    u = user(uid, ctx.author.name)

    if not choice:
        if tx["active"]:
            return await ctx.send("⚠️ Sòng đang mở!")

        tx.update(active=True, bets={}, tai=0, xiu=0)

        e = embed(
            "🎲 SÒNG TÀI XỈU 30S 🎲",
            "Gõ `!tx tai 100` hoặc `!tx xiu 100`\n\n"
            "⏱️ **30 giây**\n\n"
            "🔴 **TÀI:** `0$` | 🔵 **XỈU:** `0$`",
            ORANGE
        )

        msg = await ctx.send(embed=e)

        for left in [20, 10]:
            await asyncio.sleep(10)
            if not tx["active"]:
                return

            e.description = (
                "Gõ `!tx tai 100` hoặc `!tx xiu 100`\n\n"
                f"⏱️ **{left} giây**\n\n"
                f"🔴 **TÀI:** `{tx['tai']:,}$` | "
                f"🔵 **XỈU:** `{tx['xiu']:,}$`"
            )
            await msg.edit(embed=e)

        tx["active"] = False

        e = embed(
            "🎲 NHÀ CÁI ĐANG XÓC BÁT...",
            "🥣 **Đang xóc...**\n\n`[ ❔ ] - [ ❔ ] - [ ❔ ]`",
            ORANGE
        )
        await msg.edit(embed=e)
        await asyncio.sleep(2)

        dice = [random.randint(1, 6) for _ in range(3)]
        total = sum(dice)
        result = "tai" if total >= 11 else "xiu"

        winners, losers = [], []

        for pid, betdata in tx["bets"].items():
            p = user(pid, betdata["name"])
            amount = betdata["amount"]

            if betdata["choice"] == result:
                p["cash"] += amount * 2
                winners.append(f"• {betdata['name']} `+{amount:,}$`")
            else:
                losers.append(f"• {betdata['name']} `-{amount:,}$`")

        color = GREEN if winners else RED

        e = embed(
            "🎲 KẾT QUẢ TÀI XỈU 🎲",
            f"Xúc xắc\n"
            f"`[ {dice[0]} ] - [ {dice[1]} ] - [ {dice[2]} ]` "
            f"→ **{total} điểm ({'TÀI 🔴' if result == 'tai' else 'XỈU 🔵'})**\n\n"
            f"🎉 **THẮNG**\n"
            f"```{chr(10).join(winners) or 'Không có'}```\n"
            f"💸 **THUA**\n"
            f"```{chr(10).join(losers) or 'Không có'}```",
            color
        )

        await msg.edit(embed=e)
        return

    choice = choice.lower()

    if choice not in ("tai", "xiu"):
        return await ctx.send("❌ Dùng `!tx tai 100` hoặc `!tx xiu 100`")

    if not tx["active"]:
        return await ctx.send("❌ Chưa có phiên Tài Xỉu!")

    if not bet or bet <= 0 or bet > 10000000:
        return await ctx.send("❌ Cược từ 1$ đến 10,000,000$.")

    if u["cash"] < bet:
        return await ctx.send("❌ Không đủ tiền!")

    # Cược lại: hoàn tiền cược cũ
    if uid in tx["bets"]:
        old = tx["bets"][uid]
        u["cash"] += old["amount"]

        if old["choice"] == "tai":
            tx["tai"] -= old["amount"]
        else:
            tx["xiu"] -= old["amount"]

    u["cash"] -= bet

    tx["bets"][uid] = {
        "name": ctx.author.name,
        "choice": choice,
        "amount": bet
    }

    tx[choice] += bet

    await ctx.send(embed=embed(
        "🎲 ĐẶT CƯỢC THÀNH CÔNG",
        f"👤 {ctx.author.mention}\n"
        f"🎯 Cửa: **{choice.upper()}**\n"
        f"💰 Cược: **{bet:,}$**",
        GREEN
    ))


# =========================
# XÓC ĐĨA
# =========================

@bot.command(name="xd", aliases=["xocdia"])
async def xocdia(ctx, choice: str = None, bet: int = None):
    if not choice or choice.lower() not in ("chan", "le") or not bet or bet <= 0:
        return await ctx.send("❌ Dùng `!xd chan 100` hoặc `!xd le 100`")

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"] -= bet

    e = embed("🪙 XÓC ĐĨA BET88", "🟠 **ĐANG XÓC ĐĨA...**", ORANGE)
    msg = await ctx.send(embed=e)

    await asyncio.sleep(.8)
    e.description = "🥣 **ĐẶT BÁT XUỐNG...**"
    await msg.edit(embed=e)
    await asyncio.sleep(.8)

    red = random.randint(0, 4)
    result = "chan" if red % 2 == 0 else "le"
    board = "🔴" * red + "⚪" * (4 - red)

    if result == choice.lower():
        u["cash"] += bet * 2
        e = embed(
            "🪙 XÓC ĐĨA BET88",
            f"🥣 **Kết quả:** {board}\n"
            f"📊 **{result.upper()} - {red} Đỏ**\n\n"
            f"🎉 **THẮNG!**\n💰 Nhận **+{bet:,}$**",
            GREEN
        )
    else:
        e = embed(
            "🪙 XÓC ĐĨA BET88",
            f"🥣 **Kết quả:** {board}\n"
            f"📊 **{result.upper()} - {red} Đỏ**\n\n"
            f"💸 **THUA!**\nMất **-{bet:,}$**",
            RED
        )

    await msg.edit(embed=e)


# =========================
# BẦU CUA
# =========================

@bot.command(name="bc", aliases=["baucua"])
async def baucua(ctx, choice: str = None, bet: int = None):
    animals = {
        "ca": "🐟", "tom": "🦐", "cua": "🦀",
        "bau": "🥒", "ga": "🐓", "nai": "🦌"
    }

    if not choice or choice.lower() not in animals or not bet or bet <= 0:
        return await ctx.send("❌ Dùng `!bc ca 100`")

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"] -= bet

    e = embed("🎲 BẦU CUA BET88", "🟠 **ĐANG LẮC HỘT...**", ORANGE)
    msg = await ctx.send(embed=e)

    await asyncio.sleep(.7)
    e.description = "🥣 **ĐANG MỞ BÁT...**"
    await msg.edit(embed=e)
    await asyncio.sleep(.7)

    r = [random.choice(list(animals)) for _ in range(3)]
    matches = r.count(choice.lower())

    display = f"`[ {animals[r[0]]} ] [ {animals[r[1]]} ] [ {animals[r[2]]} ]`"

    if matches:
        reward = bet * matches
        u["cash"] += bet + reward
        e = embed(
            "🎲 BẦU CUA BET88",
            f"{display}\n\n"
            f"🎉 **TRÚNG {matches} CON!**\n"
            f"💰 Nhận **+{reward:,}$**",
            GREEN
        )
    else:
        e = embed(
            "🎲 BẦU CUA BET88",
            f"{display}\n\n"
            f"💸 **KHÔNG TRÚNG!**\nMất **-{bet:,}$**",
            RED
        )

    await msg.edit(embed=e)


# =========================
# CHẠY BOT
# =========================

token = os.getenv("TOKEN_BOT")

if not token:
    print("❌ Chưa có TOKEN_BOT!")
else:
    bot.run(token)
