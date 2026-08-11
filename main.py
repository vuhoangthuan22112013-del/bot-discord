import os, random, asyncio
from datetime import datetime, timedelta
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN_BOT")
if not TOKEN:
    raise RuntimeError("❌ Chưa có TOKEN_BOT trên Render.")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

users, loans, checkin = {}, {}, {}
tx = {"open": False, "bets": {}}
MAX_TX = 10_000_000


def user(uid):
    if uid not in users:
        users[uid] = {"money": 7500, "bank": 0, "luck": 100}
    return users[uid]


def money(n):
    return f"{n:,}$"


def card(title, text):
    e = discord.Embed(title=title, description=text)
    e.set_footer(text="💎 BET88")
    return e


def win(amount, balance):
    return (
        f"💰 Số tiền cược: `{money(amount)}`\n"
        f"🎉 Số tiền thắng: `+{money(amount * 2)}`\n"
        f"👛 Ví: `{money(balance)}`\n\n"
        f"💎 **Bạn đã thắng nhà cái BET88! 🎉**"
    )


def lose(amount, balance):
    return (
        f"💰 Số tiền cược: `{money(amount)}`\n"
        f"🎉 Số tiền thắng: `0$`\n"
        f"👛 Ví: `{money(balance)}`\n\n"
        f"💀 **Cảm ơn đã tin tưởng nhà cái BET88 💀**"
    )


def pay_result(x, amount, ok):
    if ok:
        x["money"] += amount * 2
        return win(amount, x["money"])
    return lose(amount, x["money"])


@bot.event
async def on_ready():
    print(f"✅ BET88 ONLINE: {bot.user}")


# ================= MENU =================

@bot.command()
async def trogiup(ctx):
    await ctx.send(embed=card("💎 BET88 | MENU",
"""🎰 **TRÒ CHƠI**
`!tx tai 1000` / `!tx xiu 1000`
`!bc 1000`
`!xd chan 1000`
`!quay 1000`
`!tuxi bao 1000`

💰 **TÀI KHOẢN**
`!vi` `!diemdanh`
`!gui 1000` `!rut 1000`
`!chuyen @user 1000`

🏦 **VAY**
`!vaybot 50000`
`!vay @user 50000`
`!trano`

👑 **ADMIN**
`!settien @user 100000`
`!resettien @user`
`!tyle`"""))


# ================= VÍ =================

@bot.command()
async def vi(ctx):
    x = user(ctx.author.id)
    await ctx.send(embed=card("💳 TÀI KHOẢN",
f"""👤 {ctx.author.mention}

💰 Ví: `{money(x["money"])}`
🏦 Ngân hàng: `{money(x["bank"])}`
🍀 May mắn: `{x["luck"]}%`"""))


@bot.command()
async def diemdanh(ctx):
    uid = ctx.author.id
    now = datetime.utcnow()

    if uid in checkin and now - checkin[uid] < timedelta(hours=24):
        r = timedelta(hours=24) - (now - checkin[uid])
        return await ctx.send(
            f"⏳ Còn **{int(r.total_seconds() // 3600)} giờ** nữa mới điểm danh."
        )

    x = user(uid)
    x["money"] += 2500
    checkin[uid] = now

    await ctx.send(embed=card("🎁 ĐIỂM DANH",
f"""✨ **ĐIỂM DANH THÀNH CÔNG**

🎁 Nhận: `+2,500$`
👛 Ví: `{money(x["money"])}`"""))


# ================= NGÂN HÀNG =================

@bot.command()
async def gui(ctx, amount: int):
    x = user(ctx.author.id)
    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Số tiền không hợp lệ.")
    x["money"] -= amount
    x["bank"] += amount
    await ctx.send(embed=card("🏦 GỬI TIỀN",
f"💰 Gửi: `{money(amount)}`\n👛 Ví: `{money(x['money'])}`\n🏦 Ngân hàng: `{money(x['bank'])}`"))


@bot.command()
async def rut(ctx, amount: int):
    x = user(ctx.author.id)
    if amount <= 0 or amount > x["bank"]:
        return await ctx.send("❌ Ngân hàng không đủ tiền.")
    x["bank"] -= amount
    x["money"] += amount
    await ctx.send(embed=card("💸 RÚT TIỀN",
f"💰 Rút: `{money(amount)}`\n👛 Ví: `{money(x['money'])}`\n🏦 Ngân hàng: `{money(x['bank'])}`"))


@bot.command()
async def chuyen(ctx, member: discord.Member, amount: int):
    x = user(ctx.author.id)
    if member.bot or member.id == ctx.author.id:
        return await ctx.send("❌ Không thể chuyển cho người này.")
    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Không đủ tiền.")
    x["money"] -= amount
    user(member.id)["money"] += amount
    await ctx.send(embed=card("💱 CHUYỂN TIỀN",
f"👤 Người nhận: {member.mention}\n💰 Số tiền: `{money(amount)}`\n👛 Ví còn: `{money(x['money'])}`"))


# ================= TÀI XỈU =================

@bot.command()
async def tx(ctx, *a):
    if not a:
        if not tx["open"]:
            return await ctx.send("🔴 Sòng đóng. Gõ `!tx tai 1000` để mở.")
        return await ctx.send(embed=card("🎲 SÒNG TÀI XỈU",
"🔥 TÀI đang mở\n❄️ XỈU đang mở\n⏱️ 30 giây"))

    if len(a) != 2 or a[0].lower() not in ("tai", "xiu"):
        return await ctx.send("❌ Dùng: `!tx tai 1000` hoặc `!tx xiu 1000`")

    choice = a[0].lower()
    try:
        amount = int(a[1])
    except:
        return await ctx.send("❌ Số tiền không hợp lệ.")

    x = user(ctx.author.id)

    if amount <= 0 or amount > MAX_TX or amount > x["money"]:
        return await ctx.send("❌ Số tiền cược không hợp lệ.")

    if ctx.author.id in tx["bets"]:
        return await ctx.send("⚠️ Bạn đã cược ván này.")

    if not tx["open"]:
        tx["open"] = True
        tx["bets"] = {}
        await ctx.send(embed=card(
            "🎲 TÀI XỈU | 🔵 ĐANG MỞ",
            "Anh em gõ `!tx tai <tiền>` hoặc `!tx xiu <tiền>`!\n\n"
            "💰 Tối đa: `10,000,000$/ván`\n⏱️ Thời gian: `30 giây`"
        ))
        asyncio.create_task(finish_tx(ctx.channel))

    x["money"] -= amount
    tx["bets"][ctx.author.id] = {"choice": choice, "amount": amount,
                                 "name": ctx.author.mention}

    await ctx.send(embed=card("🎯 ĐÃ NHẬN KÈO",
f"👤 {ctx.author.mention}\n🎯 Theo kèo: **{choice.upper()}**\n💰 Tiền cược: `{money(amount)}`"))


async def finish_tx(channel):
    await asyncio.sleep(30)
    if not tx["open"]:
        return

    dice = [random.randint(1, 6) for _ in range(3)]
    total = sum(dice)
    result = "tai" if total >= 11 else "xiu"

    await channel.send(embed=card("📢 THÔNG BÁO",
f"[ {dice[0]} ] - [ {dice[1]} ] - [ {dice[2]} ]\n\n"
f"💥 **{total} → {result.upper()}**"))

    for uid, b in list(tx["bets"].items()):
        x = user(uid)
        ok = b["choice"] == result

        if ok:
            text = pay_result(x, b["amount"], True)
            title = "🎉 BẠN THẮNG"
        else:
            text = pay_result(x, b["amount"], False)
            title = "💸 BẠN THUA"

        await channel.send(embed=card(
            title,
            f"👤 {b['name']}\n\n{text}"
        ))

    tx["open"] = False
    tx["bets"] = {}


# ================= BẦU CUA =================

@bot.command()
async def bc(ctx, amount: int):
    x = user(ctx.author.id)

    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Không đủ tiền.")

    x["money"] -= amount

    await ctx.send(embed=card(
        "🦀 BẦU CUA | 🟠 ĐANG LẮC",
        f"💰 Cược: `{money(amount)}`\n\n🦀 Lắc... Lắc... Lắc..."
    ))

    await asyncio.sleep(2)

    icons = ["🍐", "🦀", "🦌", "🦐", "🐓", "🐟"]
    r = random.choices(icons, k=3)

    # Có ít nhất 1 con trùng với kết quả cược ngẫu nhiên
    target = random.choice(icons)
    hit = r.count(target)

    if hit:
        prize = amount * (hit + 1)
        x["money"] += prize
        text = (
            f"💰 Số tiền cược: `{money(amount)}`\n"
            f"🎉 Số tiền thắng: `+{money(prize)}`\n"
            f"👛 Ví: `{money(x['money'])}`\n\n"
            f"💎 **Bạn đã thắng nhà cái BET88! 🎉**"
        )
        title = "🦀 BẦU CUA | 🟢 THẮNG"
    else:
        text = lose(amount, x["money"])
        title = "🦀 BẦU CUA | 🔴 THUA"

    await ctx.send(embed=card(
        title,
        f"📢 **THÔNG BÁO**\n\n"
        f"[ {r[0]} ] | [ {r[1]} ] | [ {r[2]} ]\n\n{text}"
    ))


# ================= XÓC ĐĨA =================

@bot.command()
async def xd(ctx, choice: str, amount: int):
    choice = choice.lower()

    if choice not in ("chan", "le"):
        return await ctx.send("❌ Chọn `chan` hoặc `le`.")

    x = user(ctx.author.id)

    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Không đủ tiền.")

    x["money"] -= amount

    await ctx.send(embed=card(
        "🪙 XÓC ĐĨA | 🟠 ĐANG XÓC",
        f"🎯 Cửa: **{choice.upper()}**\n"
        f"💰 Cược: `{money(amount)}`\n\n"
        "🪙 Xóc... Xóc... Xóc..."
    ))

    await asyncio.sleep(2)

    r = [random.choice(["🔴", "⚪"]) for _ in range(4)]
    result = "chan" if r.count("🔴") % 2 == 0 else "le"
    ok = choice == result

    if ok:
        text = pay_result(x, amount, True)
        title = "🪙 XÓC ĐĨA | 🟢 THẮNG"
    else:
        text = pay_result(x, amount, False)
        title = "🪙 XÓC ĐĨA | 🔴 THUA"

    await ctx.send(embed=card(
        title,
        f"📢 **THÔNG BÁO**\n\n"
        f"[ {r[0]} ] | [ {r[1]} ] | [ {r[2]} ] | [ {r[3]} ]\n\n"
        f"💥 Kết quả: **{result.upper()}**\n\n{text}"
    ))


# ================= QUAY =================

@bot.command()
async def quay(ctx, amount: int):
    x = user(ctx.author.id)

    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Không đủ tiền.")

    x["money"] -= amount

    await ctx.send(embed=card(
        "🎰 QUAY | 🟠 ĐANG QUAY",
        f"💰 Cược: `{money(amount)}`\n\n🎰 **Đang quay...**"
    ))

    await asyncio.sleep(2)

    icons = ["🍒", "7️⃣", "🍋", "💎"]
    r = random.choices(icons, k=3)

    if r[0] == r[1] == r[2]:
        prize = amount * 5
        x["money"] += prize
        text = (
            f"💰 Số tiền cược: `{money(amount)}`\n"
            f"🎉 Số tiền thắng: `+{money(prize)}`\n"
            f"👛 Ví: `{money(x['money'])}`\n\n"
            f"💎 **Bạn đã thắng nhà cái BET88! 🎉**"
        )
        title = "🎰 QUAY | 🟢 JACKPOT"
    else:
        text = lose(amount, x["money"])
        title = "🎰 QUAY | 🔴 THUA"

    await ctx.send(embed=card(
        title,
        f"📢 **THÔNG BÁO**\n\n"
        f"[ {r[0]} ] | [ {r[1]} ] | [ {r[2]} ]\n\n{text}"
    ))


# ================= TÙ XÌ =================

@bot.command()
async def tuxi(ctx, choice: str, amount: int):
    choice = choice.lower()

    if choice not in ("bao", "bua", "keo"):
        return await ctx.send("❌ Chọn `bao`, `bua` hoặc `keo`.")

    x = user(ctx.author.id)

    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Không đủ tiền.")

    x["money"] -= amount
    botc = random.choice(["bao", "bua", "keo"])

    names = {"bao": "BAO", "bua": "BÚA", "keo": "KÉO"}

    if choice == botc:
        x["money"] += amount
        text = (
            f"💰 Số tiền cược: `{money(amount)}`\n"
            f"🎉 Số tiền thắng: `0$`\n"
            f"👛 Ví: `{money(x['money'])}`"
        )
        result = "HÒA"
    else:
        beats = {"keo": "bao", "bua": "keo", "bao": "bua"}
        ok = beats[choice] == botc
        result = "BẠN THẮNG 🎉" if ok else "BẠN THUA"
        text = pay_result(x, amount, ok)

    await ctx.send(embed=card(
        "✊ TÙ XÌ | 📢 THÔNG BÁO",
        f"👤 Bạn: **{names[choice]}**     🤖 Bot: **{names[botc]}**\n\n"
        f"💥 **{result}**\n\n{text}"
    ))


# ================= VAY =================

@bot.command()
async def vaybot(ctx, amount: int):
    uid = ctx.author.id

    if not 0 < amount <= 50000:
        return await ctx.send("❌ Vay từ 1$ đến 50,000$.")

    if uid in loans:
        return await ctx.send("❌ Bạn đang có khoản vay.")

    user(uid)["money"] += amount
    loans[uid] = {"bot": True, "amount": amount,
                   "due": datetime.utcnow() + timedelta(hours=1)}

    await ctx.send(embed=card(
        "🏦 VAY BOT",
        f"💰 Khoản vay: `{money(amount)}`\n⏱️ Hạn: **1 giờ**\n\n`!trano` để trả."
    ))


@bot.command()
async def vay(ctx, member: discord.Member, amount: int):
    lender = user(ctx.author.id)

    if member.bot or member.id == ctx.author.id:
        return await ctx.send("❌ Không thể vay người này.")

    if amount <= 0 or amount > lender["money"]:
        return await ctx.send("❌ Người cho vay không đủ tiền.")

    if member.id in loans:
        return await ctx.send("❌ Người này đang có khoản vay.")

    lender["money"] -= amount
    user(member.id)["money"] += amount

    loans[member.id] = {
        "bot": False,
        "amount": amount,
        "lender": ctx.author.id,
        "due": datetime.utcnow() + timedelta(hours=1)
    }

    await ctx.send(embed=card(
        "🤝 VAY NGƯỜI CHƠI",
        f"👤 Người vay: {member.mention}\n"
        f"💰 Khoản vay: `{money(amount)}`\n"
        f"⏱️ Hạn: **1 giờ**"
    ))


@bot.command()
async def trano(ctx):
    uid = ctx.author.id

    if uid not in loans:
        return await ctx.send("❌ Bạn không có khoản nợ.")

    loan = loans[uid]
    x = user(uid)
    amount = loan["amount"]

    if amount > x["money"]:
        return await ctx.send(f"❌ Cần `{money(amount)}`.")

    x["money"] -= amount

    if not loan["bot"]:
        user(loan["lender"])["money"] += amount

    del loans[uid]

    await ctx.send(embed=card(
        "💵 TRẢ NỢ",
        f"✅ Đã trả: `{money(amount)}`\n👛 Ví: `{money(x['money'])}`"
    ))


# ================= ADMIN =================

def admin():
    async def check(ctx):
        return ctx.guild and ctx.author.guild_permissions.administrator
    return commands.check(check)


@bot.command()
@admin()
async def settien(ctx, member: discord.Member, amount: int):
    if amount < 0:
        return await ctx.send("❌ Số tiền không hợp lệ.")
    user(member.id)["money"] = amount
    await ctx.send(f"💰 {member.mention} → `{money(amount)}`")


@bot.command()
@admin()
async def resettien(ctx, member: discord.Member):
    users[member.id] = {"money": 7500, "bank": 0, "luck": 100}
    await ctx.send(f"🔄 Đã reset {member.mention}.")


@bot.command()
@admin()
async def tyle(ctx):
    await ctx.send(embed=card(
        "📊 TỶ LỆ BET88",
        "🎲 Tài Xỉu: **1:1**\n"
        "🦀 Bầu Cua: **theo kết quả**\n"
        "🪙 Xóc Đĩa: **1:1**\n"
        "🎰 Quay: **x5 Jackpot**\n"
        "✊ Tù Xì: **1:1**"
    ))


# ================= LỖI =================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.CheckFailure):
        return await ctx.send("❌ Bạn không có quyền.")

    if isinstance(error, (commands.MissingRequiredArgument,
                          commands.BadArgument)):
        return await ctx.send("❌ Sai cú pháp. Dùng `!trogiup`.")

    print("ERROR:", repr(error))


bot.run(TOKEN)
