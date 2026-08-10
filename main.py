import os, asyncio, random, time, secrets, discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

users, codes, cooldowns, last_dd = {}, {}, {}, {}
DEFAULT = 4899
BLUE, ORANGE, GREEN, RED = 0x3498DB, 0xF1C40F, 0x2ECC71, 0xE74C3C

tx = {"active": False, "bets": {}, "tai": 0, "xiu": 0, "msg": None}


def emb(title, text, color):
    return discord.Embed(title=title, description=text, color=color)


def user(uid, name="Thành viên"):
    if uid not in users:
        users[uid] = {
            "name": name, "cash": DEFAULT, "bank": 0,
            "hang": "Người chơi Thường", "ga": "Gà Công Nghiệp 🐥"
        }
    return users[uid]


def cd(uid, cmd, sec=1.5):
    k, now = f"{uid}_{cmd}", time.time()
    if k in cooldowns and now - cooldowns[k] < sec:
        return round(sec - (now - cooldowns[k]), 1)
    cooldowns[k] = now
    return 0


def admin(ctx):
    return ctx.author.guild_permissions.administrator


@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino Bet88")
    )
    print(f"✅ BOT ONLINE: {bot.user}")


# ================= TRO GIUP =================

@bot.command(name="trogiup", aliases=["help"])
async def trogiup(ctx):
    if cd(ctx.author.id, "help"):
        return

    await ctx.send(embed=emb(
        "🎰 CASINO BET88",
        "**⚔️ PVP**\n"
        "`!danhbai` `!thachdau` `!dagapvp` `!tuxipvp @User`\n\n"

        "**🎲 CASINO**\n"
        "`!tx` `!bc ca 100` `!xd chan 100` `!quay 100`\n\n"

        "**🏛️ HỆ THỐNG**\n"
        "`!vi` `!gui` `!rut` `!chuyen @User 100`\n"
        "`!diemdanh` `!bxh` `!nhapcode CODE`\n\n"

        "**👑 ADMIN**\n"
        "`!taocode 10000 1`\n"
        "`!thuongcode 10000 10`\n"
        "`!settien @User 10000`\n"
        "`!resettien @User`",
        BLUE
    ))


# ================= VI =================

@bot.command(name="vi", aliases=["money", "bal"])
async def vi(ctx, member: discord.Member = None):
    t = member or ctx.author
    u = user(t.id, t.name)

    await ctx.send(embed=emb(
        "💳 THÔNG TIN TÀI KHOẢN",
        f"👤 **{t.name.upper()}**\n"
        f"🏷️ Hạng: {u['hang']}\n"
        f"🐓 Gà: {u['ga']}\n\n"
        f"💵 Tiền mặt: `{u['cash']:,}$`\n"
        f"🏦 Ngân hàng: `{u['bank']:,}$`",
        BLUE
    ))


# ================= DIEM DANH =================

@bot.command(name="diemdanh")
async def diemdanh(ctx):
    uid, now = ctx.author.id, time.time()

    if uid in last_dd and now - last_dd[uid] < 43200:
        return await ctx.send("⚠️ Bạn đã điểm danh rồi!")

    last_dd[uid] = now
    u = user(uid, ctx.author.name)
    u["cash"] += 2593

    await ctx.send(embed=emb(
        "🎁 ĐIỂM DANH",
        f"💰 Nhận **+2,593$**\n"
        f"💵 Ví: `{u['cash']:,}$`",
        GREEN
    ))


# ================= BANK =================

@bot.command(name="gui")
async def gui(ctx, amount: int = None):
    if not amount or amount <= 0:
        return await ctx.send("❌ `!gui số_tiền`")

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"] -= amount
    u["bank"] += amount

    await ctx.send(embed=emb(
        "🏦 GỬI TIỀN",
        f"💰 Gửi: `{amount:,}$`\n"
        f"🏦 Bank: `{u['bank']:,}$`\n"
        f"📈 Lãi: **2%/ngày**",
        BLUE
    ))


@bot.command(name="rut")
async def rut(ctx, amount: int = None):
    if not amount or amount <= 0:
        return await ctx.send("❌ `!rut số_tiền`")

    u = user(ctx.author.id, ctx.author.name)

    if u["bank"] < amount:
        return await ctx.send("❌ Bank không đủ!")

    u["bank"] -= amount
    u["cash"] += amount

    await ctx.send(embed=emb(
        "🏦 RÚT TIỀN",
        f"💰 Rút: `{amount:,}$`\n"
        f"💵 Ví: `{u['cash']:,}$`",
        BLUE
    ))


@bot.command(name="chuyen")
async def chuyen(ctx, member: discord.Member = None, amount: int = None):
    if not member or not amount or amount <= 0:
        return await ctx.send("❌ `!chuyen @User số_tiền`")

    if member.id == ctx.author.id or member.bot:
        return await ctx.send("❌ Không thể chuyển!")

    a = user(ctx.author.id, ctx.author.name)
    b = user(member.id, member.name)

    if a["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền!")

    a["cash"] -= amount
    b["cash"] += amount

    await ctx.send(embed=emb(
        "💸 CHUYỂN TIỀN",
        f"👤 {ctx.author.mention} → {member.mention}\n"
        f"💰 `{amount:,}$`",
        BLUE
    ))


# ================= BXH =================

@bot.command(name="bxh")
async def bxh(ctx):
    top = sorted(
        users.values(),
        key=lambda x: x["cash"] + x["bank"],
        reverse=True
    )[:5]

    if not top:
        return await ctx.send("❌ Chưa có người chơi.")

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    text = ""

    for i, u in enumerate(top):
        text += (
            f"{medals[i]} **{u['name']}** — "
            f"`{u['cash'] + u['bank']:,}$`\n"
        )

    await ctx.send(embed=emb("🏆 TOP 5 GIÀU NHẤT", text, BLUE))


# ================= CODE =================

def newcode():
    return "BET-" + secrets.token_hex(3).upper()


@bot.command(name="taocode")
async def taocode(ctx, amount: int = None, uses: int = None):
    if not admin(ctx):
        return await ctx.send("⛔ Chỉ Admin!")

    if not amount or not uses or amount <= 0 or uses <= 0:
        return await ctx.send("❌ `!taocode số_tiền số_lượt`")

    code = newcode()
    codes[code] = {
        "money": amount,
        "uses": uses,
        "used": set()
    }

    try:
        await ctx.author.send(embed=emb(
            "🔐 CODE RIÊNG CỦA ADMIN",
            f"🎟️ Code: `{code}`\n"
            f"💰 Tiền: `{amount:,}$`\n"
            f"🔢 Lượt: `{uses}`",
            BLUE
        ))
        await ctx.send("✅ Đã gửi code riêng vào DM của bạn.")
    except discord.Forbidden:
        await ctx.send(f"🔐 Code: `{code}`")


@bot.command(name="thuongcode")
async def thuongcode(ctx, amount: int = None, uses: int = None):
    if not admin(ctx):
        return await ctx.send("⛔ Chỉ Admin!")

    if not amount or not uses or amount <= 0 or uses <= 0:
        return await ctx.send("❌ `!thuongcode số_tiền số_lượt`")

    code = newcode()
    codes[code] = {
        "money": amount,
        "uses": uses,
        "used": set()
    }

    await ctx.send(embed=emb(
        "🎁 CODE THƯỞNG",
        f"🎟️ **CODE:** `{code}`\n"
        f"💰 **Thưởng:** `{amount:,}$`\n"
        f"👥 **Số lượt:** `{uses}`\n\n"
        f"👉 Nhập: `!nhapcode {code}`",
        GREEN
    ))


@bot.command(name="nhapcode")
async def nhapcode(ctx, code: str = None):
    if not code:
        return await ctx.send("❌ `!nhapcode CODE`")

    code = code.upper()

    if code not in codes:
        return await ctx.send("❌ Code không tồn tại!")

    c = codes[code]
    uid = ctx.author.id

    if uid in c["used"]:
        return await ctx.send("❌ Bạn đã dùng code này!")

    if len(c["used"]) >= c["uses"]:
        return await ctx.send("❌ Code đã hết lượt!")

    c["used"].add(uid)

    u = user(uid, ctx.author.name)
    u["cash"] += c["money"]

    await ctx.send(embed=emb(
        "🎁 NHẬP CODE THÀNH CÔNG",
        f"🎟️ `{code}`\n"
        f"💰 Nhận **+{c['money']:,}$**",
        GREEN
    ))


# ================= ADMIN TIEN =================

@bot.command(name="settien")
async def settien(ctx, member: discord.Member = None, amount: int = None):
    if not admin(ctx):
        return await ctx.send("⛔ Chỉ Admin!")

    if not member or amount is None or amount < 0:
        return await ctx.send("❌ `!settien @User số_tiền`")

    user(member.id, member.name)["cash"] = amount

    await ctx.send(
        f"✅ {member.mention} → `{amount:,}$`"
    )


@bot.command(name="resettien", aliases=["reset"])
async def resettien(ctx, member: discord.Member = None):
    if not admin(ctx):
        return await ctx.send("⛔ Chỉ Admin!")

    if not member:
        return await ctx.send("❌ `!resettien @User`")

    user(member.id, member.name)["cash"] = DEFAULT

    await ctx.send(
        f"🔄 {member.mention} → `{DEFAULT:,}$`"
    )


# ================= SLOT =================

@bot.command(name="quay")
async def quay(ctx, bet: int = None):
    if cd(ctx.author.id, "quay"):
        return

    if not bet or bet <= 0:
        return await ctx.send("❌ `!quay số_tiền`")

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"] -= bet

    icons = ["🍋", "🔔", "🍒", "⭐", "💎", "7️⃣"]
    s = [random.choice(icons) for _ in range(3)]

    msg = await ctx.send(embed=emb(
        "🎰 QUAY MAY MẮN",
        "🎰 **ĐANG QUAY...**\n\n"
        "`[ ❔ ]   [ ❔ ]   [ ❔ ]`\n\n"
        "🎲 **KẾT QUẢ**",
        ORANGE
    ))

    await asyncio.sleep(.7)

    await msg.edit(embed=emb(
        "🎰 QUAY MAY MẮN",
        "🎰 **ĐANG QUAY...**\n\n"
        f"`[ {s[0]} ]   [ ❔ ]   [ ❔ ]`\n\n"
        "🎲 **KẾT QUẢ**",
        ORANGE
    ))

    await asyncio.sleep(.7)

    win = s[0] == s[1] == s[2]

    if win:
        gain = bet * 5
        u["cash"] += gain
        text = (
            f"`[ {s[0]} ]   [ {s[1]} ]   [ {s[2]} ]`\n\n"
            "🎉 **NỔ HŨ!**\n"
            f"💰 **+{gain:,}$**\n\n"
            "🎲 **KẾT QUẢ**"
        )
    else:
        text = (
            f"`[ {s[0]} ]   [ {s[1]} ]   [ {s[2]} ]`\n\n"
            "💸 **KHÔNG TRÚNG!**\n"
            f"💰 **-{bet:,}$**\n\n"
            "🎲 **KẾT QUẢ**"
        )

    await msg.edit(embed=emb(
        "🎰 QUAY MAY MẮN",
        text,
        GREEN if win else RED
    ))


# ================= TAI XIU =================

@bot.command(name="tx")
async def taixiu(ctx, choice: str = None, bet: int = None):
    uid = ctx.author.id
    u = user(uid, ctx.author.name)

    # !tx = mở phiên
    if choice is None:
        if tx["active"]:
            return await ctx.send(embed=emb(
                "🎲 TÀI XỈU",
                "🟠 **ĐANG NHẬN CƯỢC...**\n\n"
                f"🔴 **TÀI:** `{tx['tai']:,}$`\n"
                f"🔵 **XỈU:** `{tx['xiu']:,}$`\n\n"
                "💰 **CƯỢC MAX: 10,000,000$**\n\n"
                "`!tx tai số_tiền`\n"
                "`!tx xiu số_tiền`",
                ORANGE
            ))

        tx.update(
            active=True,
            bets={},
            tai=0,
            xiu=0
        )

        tx["msg"] = await ctx.send(embed=emb(
            "🎲 TÀI XỈU",
            "⏱️ **THỜI GIAN: 30 GIÂY**\n\n"
            "🔴 **TÀI:** `0$`\n"
            "🔵 **XỈU:** `0$`\n\n"
            "💰 **CƯỢC MAX: 10,000,000$**\n\n"
            "🎯 `!tx tai số_tiền`\n"
            "🎯 `!tx xiu số_tiền`",
            ORANGE
        ))

        asyncio.create_task(tx_round())
        return

    choice = choice.lower()

    if choice not in ("tai", "xiu"):
        return await ctx.send("❌ Chọn `tai` hoặc `xiu`!")

    if not bet or bet <= 0:
        return await ctx.send("❌ Ví dụ: `!tx tai 1000`")

    if bet > 10000000:
        return await ctx.send("❌ **Cược tối đa 10,000,000$!**")

    if not tx["active"]:
        return await ctx.send("❌ **Chưa có phiên Tài Xỉu!**")

    if uid in tx["bets"]:
        return await ctx.send(
            "❌ Bạn chỉ được cược **1 lần / ván**!"
        )

    if u["cash"] < bet:
        return await ctx.send("❌ **Không đủ tiền!**")

    u["cash"] -= bet

    tx["bets"][uid] = {
        "name": ctx.author.name,
        "choice": choice,
        "amount": bet
    }

    tx[choice] += bet

    # Xóa tin nhắn cược
    try:
        await ctx.message.delete()
    except:
        pass

    await tx["msg"].edit(embed=emb(
        "🎲 TÀI XỈU",
        "🟠 **ĐANG NHẬN CƯỢC...**\n\n"
        f"🔴 **TÀI:** `{tx['tai']:,}$`\n"
        f"🔵 **XỈU:** `{tx['xiu']:,}$`\n\n"
        "💰 **CƯỢC MAX: 10,000,000$**\n"
        "🎯 Mỗi người **1 lần cược**",
        ORANGE
    ))


async def tx_round():
    await asyncio.sleep(30)

    if not tx["active"]:
        return

    tx["active"] = False
    msg = tx["msg"]

    await msg.edit(embed=emb(
        "🎲 TÀI XỈU",
        "🥣 **ĐANG XÓC BÁT...**\n\n"
        "🎲 `[ ❔ ]   [ ❔ ]   [ ❔ ]`\n\n"
        "⏳ **CHỜ KẾT QUẢ...**",
        ORANGE
    ))

    await asyncio.sleep(2)

    d = [random.randint(1, 6) for _ in range(3)]
    total = sum(d)
    result = "tai" if total >= 11 else "xiu"

    win, lose = [], []

    for uid, b in tx["bets"].items():
        if b["choice"] == result:
            user(uid)["cash"] += b["amount"] * 2
            win.append(
                f"• **{b['name']}** `+{b['amount']:,}$`"
            )
        else:
            lose.append(
                f"• **{b['name']}** `-{b['amount']:,}$`"
            )

    result_name = "TÀI 🔴" if result == "tai" else "XỈU 🔵"

    text = (
        f"🎲 `[ {d[0]} ]   [ {d[1]} ]   [ {d[2]} ]`\n\n"
        f"💥 **{total} ĐIỂM — {result_name}**\n\n"
        "🏆 **THẮNG**\n"
        + ("\n".join(win) or "Không có") +
        "\n\n💸 **THUA**\n"
        + ("\n".join(lose) or "Không có")
    )

    await msg.edit(embed=emb(
        "🎲 KẾT QUẢ TÀI XỈU",
        text,
        GREEN if win else RED
    ))

    tx.update(
        active=False,
        bets={},
        tai=0,
        xiu=0,
        msg=None
    )


# ================= XOC DIA =================

@bot.command(name="xd")
async def xd(ctx, choice: str = None, bet: int = None):
    if not choice or choice.lower() not in ("chan", "le"):
        return await ctx.send(
            "❌ `!xd chan 100` hoặc `!xd le 100`"
        )

    if not bet or bet <= 0:
        return await ctx.send(
            "❌ `!xd chan 100` hoặc `!xd le 100`"
        )

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"] -= bet

    msg = await ctx.send(embed=emb(
        "🪙 XÓC ĐĨA",
        "🟠 **XÓC...**\n\n"
        "🥣 `[ ❔ ] [ ❔ ] [ ❔ ] [ ❔ ]`",
        ORANGE
    ))

    await asyncio.sleep(.6)

    await msg.edit(embed=emb(
        "🪙 XÓC ĐĨA",
        "🟠 **XÓC... XÓC...**\n\n"
        "🥣 `[ 🔴 ] [ ❔ ] [ ❔ ] [ ❔ ]`",
        ORANGE
    ))

    await asyncio.sleep(.8)

    n = random.randint(0, 4)
    win = (n % 2 == 0) == (choice.lower() == "chan")
    result = "CHẴN" if n % 2 == 0 else "LẺ"

    if win:
        u["cash"] += bet * 2

    await msg.edit(embed=emb(
        "🪙 XÓC ĐĨA",
        f"🥣 `{('🔴' * n) + ('⚪' * (4-n))}`\n\n"
        f"📊 **{result} — {n} ĐỎ**\n\n"
        + (
            f"🎉 **THẮNG +{bet:,}$**"
            if win else
            f"💸 **THUA -{bet:,}$**"
        ),
        GREEN if win else RED
    ))


# ================= BAU CUA =================

@bot.command(name="bc")
async def bc(ctx, choice: str = None, bet: int = None):
    animals = {
        "ca": "🐟",
        "tom": "🦐",
        "cua": "🦀",
        "bau": "🥒",
        "ga": "🐓",
        "nai": "🦌"
    }

    if choice not in animals or not bet or bet <= 0:
        return await ctx.send(
            "❌ `!bc ca 100`\n"
            "`ca tom cua bau ga nai`"
        )

    u = user(ctx.author.id, ctx.author.name)

    if u["cash"] < bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"] -= bet

    msg = await ctx.send(embed=emb(
        "🦀 BẦU CUA CÁ TÔM",
        "🟠 **LẮC...**\n\n"
        "🎲 `[ ❔ ]   [ ❔ ]   [ ❔ ]`\n\n"
        "📋 **KẾT QUẢ**",
        ORANGE
    ))

    await asyncio.sleep(.6)

    await msg.edit(embed=emb(
        "🦀 BẦU CUA CÁ TÔM",
        "🟠 **LẮC... LẮC...**\n\n"
        "🎲 `[ ❔ ]   [ ❔ ]   [ ❔ ]`\n\n"
        "📋 **KẾT QUẢ**",
        ORANGE
    ))

    await asyncio.sleep(.8)

    r = [random.choice(list(animals)) for _ in range(3)]
    n = r.count(choice)

    if n:
        u["cash"] += bet * (n + 1)

    result = (
        f"🎲 `[ {animals[r[0]]} ]   "
        f"[ {animals[r[1]]} ]   [ {animals[r[2]]} ]`\n\n"
        f"📋 **KẾT QUẢ**\n"
        f"🎯 Trúng **{n} con**\n\n"
    )

    if n:
        result += f"🎉 **THẮNG +{bet*n:,}$**"
    else:
        result += f"💸 **THUA -{bet:,}$**"

    await msg.edit(embed=emb(
        "🦀 BẦU CUA CÁ TÔM",
        result,
        GREEN if n else RED
    ))


# ================= RUN =================

token = os.getenv("TOKEN_BOT")

if not token:
    print("❌ Chưa có TOKEN_BOT!")
else:
    bot.run(token)
