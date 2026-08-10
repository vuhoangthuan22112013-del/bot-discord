import os, asyncio, random, time, discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

users, cooldowns, diemdanh_cooldowns = {}, {}, {}
DEFAULT_MONEY = 4899

BLUE, ORANGE, GREEN, RED = 0x3498DB, 0xF1C40F, 0x2ECC71, 0xE74C3C

tx = {"active": False, "msg": None, "bets": {}, "tai": 0, "xiu": 0}

# code = {"money": tiền, "uses": số lượt còn lại}
gift_codes = {}


def emb(title, text, color):
    return discord.Embed(title=title, description=text, color=color)


def spam(uid, cmd, sec=1.5):
    now = time.time()
    key = f"{uid}_{cmd}"
    left = sec - (now - cooldowns.get(key, 0))
    if left > 0:
        return round(left, 1)
    cooldowns[key] = now
    return 0


def user(uid, name="Thành viên"):
    if uid not in users:
        users[uid] = {
            "name": name, "cash": DEFAULT_MONEY, "bank": 0,
            "hang": "Người chơi Thường", "ga": "Gà Công Nghiệp 🐥"
        }
    users[uid]["name"] = name
    return users[uid]


def admin(ctx):
    return ctx.author.guild_permissions.administrator


@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="!trogiup | Casino Bet88")
    )
    print(f"✅ BOT ĐÃ ONLINE: {bot.user}")


# ================= TRO GIÚP =================

@bot.command(name="trogiup", aliases=["help"])
async def trogiup(ctx):
    e = emb(
        "🎰 CASINO BET88 - TRỢ GIÚP",
        "**⚔️ PVP**\n"
        "`!danhbai` `!thachdau` `!dagapvp` `!tuxipvp @User`\n\n"
        "**🎲 CASINO**\n"
        "`!tx` `!bc` `!xd` `!quay` `!daga` `!tuxi`\n"
        "`!bai` `!rl` `!duangua` `!coinflip`\n\n"
        "**🏛️ HỆ THỐNG**\n"
        "`!vi` `!gui` `!rut` `!chuyen`\n"
        "`!diemdanh` `!bxh` `!nhapcode`\n\n"
        "**👑 ADMIN**\n"
        "`!taocode <tiền> <lượt>`\n"
        "`!settien @User <tiền>`\n"
        "`!resettien @User`",
        BLUE
    )
    e.set_footer(text="🎁 Chúc bạn may mắn tại Casino Bet88!")
    await ctx.send(embed=e)


# ================= VÍ =================

@bot.command(name="vi", aliases=["money", "bal"])
async def vi(ctx, member: discord.Member = None):
    target = member or ctx.author
    u = user(target.id, target.name)

    e = emb(
        "💳 THÔNG TIN TÀI KHOẢN",
        f"👤 **Chủ tài khoản:** {target.name}\n\n"
        f"🏷️ **Hạng:** {u['hang']}\n"
        f"🐓 **Gà:** {u['ga']}\n\n"
        f"💵 **Tiền mặt:** `{u['cash']:,}$`\n"
        f"🏦 **Ngân hàng:** `{u['bank']:,}$`\n"
        f"📈 **Lãi ngân hàng:** `2% / ngày`",
        BLUE
    )
    await ctx.send(embed=e)


# ================= ĐIỂM DANH =================

@bot.command(name="diemdanh")
async def diemdanh(ctx):
    if spam(ctx.author.id, "dd", 2):
        return

    now = time.time()
    uid = ctx.author.id

    if now - diemdanh_cooldowns.get(uid, 0) < 43200:
        return await ctx.send("⚠️ Bạn đã điểm danh trong 12 giờ qua!")

    diemdanh_cooldowns[uid] = now
    reward = 2593
    u = user(uid, ctx.author.name)
    u["cash"] += reward

    await ctx.send(embed=emb(
        "🎁 ĐIỂM DANH THÀNH CÔNG",
        f"💰 Nhận **+{reward:,}$** vào ví!",
        GREEN
    ))


# ================= GỬI / RÚT / CHUYỂN =================

@bot.command(name="gui")
async def gui(ctx, amount: int = None):
    if not amount or amount <= 0:
        return await ctx.send("❌ Dùng: `!gui <số tiền>`")

    u = user(ctx.author.id, ctx.author.name)
    if u["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền!")

    u["cash"] -= amount
    u["bank"] += amount

    await ctx.send(embed=emb(
        "🏦 GỬI TIỀN",
        f"💰 Đã gửi: **{amount:,}$**\n"
        f"🏦 Ngân hàng: **{u['bank']:,}$**\n"
        f"📈 Lãi: **2%/ngày**",
        BLUE
    ))


@bot.command(name="rut")
async def rut(ctx, amount: int = None):
    if not amount or amount <= 0:
        return await ctx.send("❌ Dùng: `!rut <số tiền>`")

    u = user(ctx.author.id, ctx.author.name)
    if u["bank"] < amount:
        return await ctx.send("❌ Ngân hàng không đủ tiền!")

    u["bank"] -= amount
    u["cash"] += amount

    await ctx.send(embed=emb(
        "🏦 RÚT TIỀN",
        f"💰 Đã rút: **{amount:,}$**\n"
        f"💵 Tiền mặt: **{u['cash']:,}$**",
        BLUE
    ))


@bot.command(name="chuyen")
async def chuyen(ctx, member: discord.Member = None, amount: int = None):
    if not member or not amount or amount <= 0:
        return await ctx.send("❌ Dùng: `!chuyen @User <tiền>`")

    if member.id == ctx.author.id or member.bot:
        return await ctx.send("❌ Người nhận không hợp lệ!")

    a = user(ctx.author.id, ctx.author.name)
    b = user(member.id, member.name)

    if a["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền!")

    a["cash"] -= amount
    b["cash"] += amount

    await ctx.send(embed=emb(
        "💸 CHUYỂN TIỀN",
        f"👤 {ctx.author.mention} ➜ {member.mention}\n"
        f"💰 Số tiền: **{amount:,}$**\n"
        f"💵 Bạn còn: **{a['cash']:,}$**",
        BLUE
    ))


# ================= BXH =================

@bot.command(name="bxh")
async def bxh(ctx):
    rank = sorted(
        users.values(),
        key=lambda x: x["cash"] + x["bank"],
        reverse=True
    )[:5]

    if not rank:
        return await ctx.send("❌ Chưa có người chơi!")

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    text = ""

    for i, u in enumerate(rank):
        total = u["cash"] + u["bank"]
        text += f"{medals[i]} **{u['name']}** — `{total:,}$`\n"

    await ctx.send(embed=emb(
        "🏆 TOP 5 NGƯỜI GIÀU NHẤT",
        text,
        BLUE
    ))


# ================= NHẬP CODE =================

@bot.command(name="nhapcode")
async def nhapcode(ctx, code: str = None):
    if not code:
        return await ctx.send("❌ Dùng: `!nhapcode <code>`")

    code = code.upper()

    if code not in gift_codes:
        return await ctx.send("❌ Code không tồn tại!")

    data = gift_codes[code]

    if data["uses"] <= 0:
        return await ctx.send("❌ Code đã hết lượt!")

    u = user(ctx.author.id, ctx.author.name)
    u["cash"] += data["money"]
    data["uses"] -= 1

    await ctx.send(embed=emb(
        "🎁 NHẬP CODE THÀNH CÔNG",
        f"🎟️ Code: `{code}`\n"
        f"💰 Nhận: **+{data['money']:,}$**\n"
        f"👥 Còn: **{data['uses']} lượt**",
        GREEN
    ))


# ================= ADMIN =================

@bot.command(name="taocode")
async def taocode(ctx, money: int = None, uses: int = None):
    if not admin(ctx):
        return await ctx.send("❌ Bạn không có quyền Admin!")

    if not money or not uses or money <= 0 or uses <= 0:
        return await ctx.send("❌ Dùng: `!taocode <tiền> <lượt>`")

    code = "BET" + str(random.randint(100000, 999999))

    while code in gift_codes:
        code = "BET" + str(random.randint(100000, 999999))

    gift_codes[code] = {
        "money": money,
        "uses": uses
    }

    try:
        await ctx.author.send(
            f"🎁 **CODE BET88**\n\n"
            f"🎟️ `{code}`\n"
            f"💰 Giá trị: `{money:,}$`\n"
            f"👥 Số lượt: `{uses}`"
        )
        await ctx.send("✅ Code đã được gửi riêng vào DM của bạn!")
    except discord.Forbidden:
        await ctx.send(
            f"⚠️ Không gửi được DM. Code của bạn là: `{code}`"
        )


@bot.command(name="settien")
async def settien(ctx, member: discord.Member = None, amount: int = None):
    if not admin(ctx):
        return await ctx.send("❌ Bạn không có quyền Admin!")

    if not member or amount is None or amount < 0:
        return await ctx.send("❌ Dùng: `!settien @User <tiền>`")

    u = user(member.id, member.name)
    u["cash"] = amount

    await ctx.send(embed=emb(
        "👑 ADMIN - ĐẶT TIỀN",
        f"👤 {member.mention}\n"
        f"💰 Tiền mới: **{amount:,}$**",
        GREEN
    ))


@bot.command(name="resettien")
async def resettien(ctx, member: discord.Member = None):
    if not admin(ctx):
        return await ctx.send("❌ Bạn không có quyền Admin!")

    if not member:
        return await ctx.send("❌ Dùng: `!resettien @User`")

    u = user(member.id, member.name)
    u["cash"] = DEFAULT_MONEY

    await ctx.send(embed=emb(
        "👑 ADMIN - RESET TIỀN",
        f"👤 {member.mention}\n"
        f"💰 Đã đưa về **{DEFAULT_MONEY:,}$**",
        BLUE
    ))


# ================= SLOT =================

@bot.command(name="quay")
async def quay(ctx, bet: int = None):
    if spam(ctx.author.id, "quay"):
        return

    if not bet or bet <= 0:
        return await ctx.send("❌ Dùng: `!quay <tiền>`")

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"] -= bet

    s = [random.choice(["🍋", "🔔", "🍒", "⭐", "💎"]) for _ in range(3)]

    msg = await ctx.send(embed=emb(
        "🎰 MÁY SLOT BET88",
        f"🟠 **ĐANG QUAY...**\n\n`[ {s[0]} ] [ ❔ ] [ ❔ ]`",
        ORANGE
    ))

    await asyncio.sleep(.7)

    await msg.edit(embed=emb(
        "🎰 MÁY SLOT BET88",
        f"🟠 **ĐANG QUAY...**\n\n`[ {s[0]} ] [ {s[1]} ] [ ❔ ]`",
        ORANGE
    ))

    await asyncio.sleep(.7)

    if s[0] == s[1] == s[2]:
        reward = bet * 4
        u["cash"] += bet + reward
        e = emb(
            "🎰 MÁY SLOT BET88",
            f"`[ {s[0]} ] [ {s[1]} ] [ {s[2]} ]`\n\n"
            f"✨ **NỔ HŨ! +{reward:,}$**",
            GREEN
        )
    else:
        e = emb(
            "🎰 MÁY SLOT BET88",
            f"`[ {s[0]} ] [ {s[1]} ] [ {s[2]} ]`\n\n"
            f"💸 **THUA -{bet:,}$**",
            RED
        )

    await msg.edit(embed=e)


# ================= TÀI XỈU =================

@bot.command(name="tx", aliases=["taixiu"])
async def tx_cmd(ctx, choice: str = None, bet: int = None):
    if not choice:
        return await ctx.send("❌ Dùng: `!tx tai 100` hoặc `!tx xiu 100`")

    choice = choice.lower()

    if choice not in ("tai", "xiu") or not bet or bet <= 0:
        return await ctx.send("❌ Dùng: `!tx tai 100` hoặc `!tx xiu 100`")

    u = user(ctx.author.id, ctx.author.name)
    uid = ctx.author.id

    if u["cash"] < bet:
        return await ctx.send("❌ Không đủ tiền!")

    # Tự mở phiên nếu chưa có
    if not tx["active"]:
        tx["active"] = True
        tx["bets"] = {}
        tx["tai"] = tx["xiu"] = 0

        tx["msg"] = await ctx.send(embed=emb(
            "🎲 SÒNG TÀI XỈU 30S",
            "🟠 **PHIÊN MỚI ĐÃ MỞ!**\n\n"
            "`!tx tai <tiền>` hoặc `!tx xiu <tiền>`\n\n"
            "⏱️ Còn **30 giây**",
            ORANGE
        ))

        asyncio.create_task(tx_round())

    # Nếu cược lại thì hoàn tiền cũ
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

    if choice == "tai":
        tx["tai"] += bet
    else:
        tx["xiu"] += bet

    # Xóa tin nhắn lệnh
    try:
        await ctx.message.delete()
    except:
        pass

    # Cập nhật phiên
    await update_tx()


async def update_tx():
    if not tx["msg"]:
        return

    try:
        await tx["msg"].edit(embed=emb(
            "🎲 SÒNG TÀI XỈU",
            f"🟠 **ĐANG NHẬN CƯỢC**\n\n"
            f"🔴 **TÀI:** `{tx['tai']:,}$`\n"
            f"🔵 **XỈU:** `{tx['xiu']:,}$`\n\n"
            "⏱️ Mọi người tiếp tục đặt cược!",
            ORANGE
        ))
    except:
        pass


async def tx_round():
    await asyncio.sleep(30)

    if not tx["active"]:
        return

    tx["active"] = False

    msg = tx["msg"]

    await msg.edit(embed=emb(
        "🎲 NHÀ CÁI ĐANG XÓC BÁT...",
        "🟠 **ĐANG XÓC...**\n\n`[ ❔ ] - [ ❔ ] - [ ❔ ]`",
        ORANGE
    ))

    await asyncio.sleep(2)

    d = [random.randint(1, 6) for _ in range(3)]
    total = sum(d)
    result = "tai" if total >= 11 else "xiu"

    winners, losers = [], []

    for uid, b in tx["bets"].items():
        u = user(uid, b["name"])

        if b["choice"] == result:
            u["cash"] += b["amount"] * 2
            winners.append(f"• {b['name']} +{b['amount']:,}$")
        else:
            losers.append(f"• {b['name']} -{b['amount']:,}$")

    result_name = "TÀI 🔴" if result == "tai" else "XỈU 🔵"

    text = (
        f"`[ {d[0]} ] - [ {d[1]} ] - [ {d[2]} ]`\n"
        f"🎯 **{total} điểm — {result_name}**\n\n"
        f"🎉 **THẮNG**\n"
        f"{chr(10).join(winners) or 'Không có'}\n\n"
        f"💸 **THUA**\n"
        f"{chr(10).join(losers) or 'Không có'}"
    )

    await msg.edit(embed=emb(
        "🎲 KẾT QUẢ TÀI XỈU",
        text,
        GREEN if winners else RED
    ))

    tx["bets"] = {}
    tx["msg"] = None


# ================= XÓC ĐĨA =================

@bot.command(name="xd", aliases=["xocdia"])
async def xd(ctx, choice: str = None, bet: int = None):
    if spam(ctx.author.id, "xd"):
        return

    if choice not in ("chan", "le") or not bet or bet <= 0:
        return await ctx.send("❌ Dùng: `!xd chan 100` hoặc `!xd le 100`")

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"] -= bet

    msg = await ctx.send(embed=emb(
        "🪙 XÓC ĐĨA BET88",
        "🟠 **ĐANG XÓC ĐĨA...**",
        ORANGE
    ))

    await asyncio.sleep(1)

    reds = random.randint(0, 4)
    even = reds % 2 == 0
    win = (choice == "chan") == even
    board = "🔴" * reds + "⚪" * (4 - reds)
    result = "CHẴN" if even else "LẺ"

    if win:
        u["cash"] += bet * 2
        e = emb(
            "🪙 XÓC ĐĨA BET88",
            f"{board}\n🎯 **{result} - {reds} Đỏ**\n\n"
            f"🎉 **THẮNG +{bet:,}$**",
            GREEN
        )
    else:
        e = emb(
            "🪙 XÓC ĐĨA BET88",
            f"{board}\n🎯 **{result} - {reds} Đỏ**\n\n"
            f"💸 **THUA -{bet:,}$**",
            RED
        )

    await msg.edit(embed=e)


# ================= BẦU CUA =================

@bot.command(name="bc", aliases=["baucua"])
async def bc(ctx, choice: str = None, bet: int = None):
    animals = {
        "ca": "🐟", "tom": "🦐", "cua": "🦀",
        "bau": "🥒", "ga": "🐓", "nai": "🦌"
    }

    if choice not in animals or not bet or bet <= 0:
        return await ctx.send("❌ Dùng: `!bc ca 100`")

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"] -= bet

    msg = await ctx.send(embed=emb(
        "🎲 BẦU CUA BET88",
        "🟠 **ĐANG LẮC HỘT...**",
        ORANGE
    ))

    await asyncio.sleep(1)

    r = [random.choice(list(animals)) for _ in range(3)]
    matches = r.count(choice)

    if matches:
        reward = bet * matches
        u["cash"] += bet + reward
        color = GREEN
        result = f"🎉 **TRÚNG {matches} CON! +{reward:,}$**"
    else:
        color = RED
        result = f"💸 **THUA -{bet:,}$**"

    e = emb(
        "🎲 BẦU CUA BET88",
        f"`[ {animals[r[0]]} ] [ {animals[r[1]]} ] [ {animals[r[2]]} ]`\n\n"
        + result,
        color
    )

    await msg.edit(embed=e)


# ================= CHẠY =================

token = os.getenv("TOKEN_BOT")

if not token:
    print("❌ Chưa có TOKEN_BOT!")
else:
    bot.run(token)
