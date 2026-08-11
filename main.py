import os, random, asyncio
from datetime import datetime, timedelta
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN_BOT")
if not TOKEN:
    raise RuntimeError("Thiếu TOKEN_BOT trên Render.")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

users = {}
loans = {}
codes = {}
claims = {}
tx = {"open": False, "bets": {}}

def user(uid):
    if uid not in users:
        users[uid] = {"money": 7500, "bank": 0, "luck": 100}
    return users[uid]

def cash(n):
    return f"{n:,}$"

def card(title, text):
    e = discord.Embed(title=title, description=text)
    e.set_footer(text="💎 BET88")
    return e

def result_text(bet, won, payout=0):
    if won:
        return (
            f"💰 **Số tiền cược:** `{cash(bet)}`\n"
            f"🎉 **Số tiền thắng:** `+{cash(payout)}`\n"
            f"👛 **Ví:** `{cash(payout)}`\n\n"
            f"💎 **Bạn đã thắng nhà cái BET88! 🎉**"
        )
    return (
        f"💰 **Số tiền cược:** `{cash(bet)}`\n"
        f"🎉 **Số tiền thắng:** `0$`\n"
        f"👛 **Ví:** `{{WALLET}}`\n\n"
        f"💀 **Cảm ơn đã tin tưởng nhà cái BET88 💀**"
    )

def outcome(x, bet, won, payout=0):
    if won:
        x["money"] += payout
        return (
            f"💰 **Số tiền cược:** `{cash(bet)}`\n"
            f"🎉 **Số tiền thắng:** `+{cash(payout)}`\n"
            f"👛 **Ví:** `{cash(x['money'])}`\n\n"
            f"💎 **Bạn đã thắng nhà cái BET88! 🎉**"
        )
    return (
        f"💰 **Số tiền cược:** `{cash(bet)}`\n"
        f"🎉 **Số tiền thắng:** `0$`\n"
        f"👛 **Ví:** `{cash(x['money'])}`\n\n"
        f"💀 **Cảm ơn đã tin tưởng nhà cái BET88 💀**"
    )

async def play_effect(ctx, title, text, wait=2):
    await ctx.send(embed=card(title, text))
    await asyncio.sleep(wait)

def admin_check(ctx):
    return ctx.guild and ctx.author.guild_permissions.administrator

@bot.event
async def on_ready():
    print(f"BET88 ONLINE: {bot.user}")

@bot.command()
async def trogiup(ctx):
    await ctx.send(embed=card("💎 BET88 | MENU",
"""🎰 **TRÒ CHƠI**
`!tx tai 1000` • `!tx xiu 1000`
`!bc 1000`
`!xd chan 1000` • `!xd le 1000`
`!quay 1000`
`!tuxi bao 1000`

💰 **TÀI KHOẢN**
`!vi` • `!diemdanh`
`!gui 1000` • `!rut 1000`
`!chuyen @user 1000`

🎁 **CODE**
`!taocode CODE 5000`
`!thuongcode CODE`

🏦 **VAY**
`!vaybot 50000`
`!vay @user 50000`
`!trano`

👑 **ADMIN**
`!settien @user 100000`
`!resettien @user`
`!tyle`"""))

@bot.command()
async def vi(ctx):
    x = user(ctx.author.id)
    await ctx.send(embed=card("💳 TÀI KHOẢN",
        f"👤 {ctx.author.mention}\n\n"
        f"💰 Ví: `{cash(x['money'])}`\n"
        f"🏦 Ngân hàng: `{cash(x['bank'])}`\n"
        f"🍀 May mắn: `{x['luck']}%`"))

@bot.command()
async def diemdanh(ctx):
    uid = ctx.author.id
    now = datetime.utcnow()
    if uid in claims and now - claims[uid] < timedelta(hours=24):
        left = timedelta(hours=24) - (now - claims[uid])
        return await ctx.send(f"⏳ Còn `{int(left.total_seconds()/3600)} giờ` nữa.")
    x = user(uid)
    x["money"] += 2500
    claims[uid] = now
    await ctx.send(embed=card("🎁 ĐIỂM DANH",
        f"✨ **ĐIỂM DANH THÀNH CÔNG**\n\n"
        f"🎁 Nhận: `+2,500$`\n👛 Ví: `{cash(x['money'])}`"))

@bot.command()
async def gui(ctx, amount: int):
    x = user(ctx.author.id)
    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Số tiền không hợp lệ.")
    x["money"] -= amount
    x["bank"] += amount
    await ctx.send(embed=card("🏦 GỬI TIỀN",
        f"💰 Gửi: `{cash(amount)}`\n👛 Ví: `{cash(x['money'])}`\n🏦 Ngân hàng: `{cash(x['bank'])}`"))

@bot.command()
async def rut(ctx, amount: int):
    x = user(ctx.author.id)
    if amount <= 0 or amount > x["bank"]:
        return await ctx.send("❌ Ngân hàng không đủ tiền.")
    x["bank"] -= amount
    x["money"] += amount
    await ctx.send(embed=card("💸 RÚT TIỀN",
        f"💰 Rút: `{cash(amount)}`\n👛 Ví: `{cash(x['money'])}`\n🏦 Ngân hàng: `{cash(x['bank'])}`"))

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
        f"👤 Người nhận: {member.mention}\n"
        f"💰 Số tiền: `{cash(amount)}`\n👛 Ví còn: `{cash(x['money'])}`"))

# ================= TÀI XỈU =================

@bot.command()
async def tx(ctx, *args):
    if not args:
        if tx["open"]:
            return await ctx.send(embed=card("🎲 SÒNG TÀI XỈU",
                "🔥 **TÀI**\n❄️ **XỈU**\n\n"
                "Anh em gõ `!tx tai <tiền>` hoặc `!tx xiu <tiền>`"))
        return await ctx.send("⚠️ Chưa có sòng. Gõ `!tx tai 1000` để mở.")

    if len(args) != 2 or args[0].lower() not in ("tai", "xiu"):
        return await ctx.send("❌ Dùng `!tx tai 1000` hoặc `!tx xiu 1000`.")

    choice = args[0].lower()
    try:
        amount = int(args[1])
    except ValueError:
        return await ctx.send("❌ Số tiền không hợp lệ.")

    x = user(ctx.author.id)
    if amount <= 0 or amount > 10_000_000:
        return await ctx.send("❌ Tối đa 10,000,000$/ván.")
    if amount > x["money"]:
        return await ctx.send("❌ Không đủ tiền.")
    if ctx.author.id in tx["bets"]:
        return await ctx.send("⚠️ Bạn đã cược ván này.")

    if not tx["open"]:
        tx["open"] = True
        tx["bets"] = {}
        await ctx.send(embed=card("🎲 TÀI XỈU | 🔵 ĐANG MỞ",
            "🎯 Anh em gõ `!tx tai <tiền>` hoặc `!tx xiu <tiền>`\n\n"
            "💰 Tối đa: `10,000,000$/ván`\n"
            "⏱️ Thời gian: **30 giây**"))
        asyncio.create_task(finish_tx(ctx.channel))

    x["money"] -= amount
    tx["bets"][ctx.author.id] = {"choice": choice, "amount": amount,
                                 "name": ctx.author.mention}
    await ctx.send(embed=card("🎯 ĐẶT CƯỢC",
        f"👤 {ctx.author.mention}\n"
        f"🎯 Theo kèo: **{choice.upper()}**\n"
        f"💰 Tiền cược: `{cash(amount)}`"))

async def finish_tx(channel):
    await asyncio.sleep(30)
    if not tx["open"]:
        return

    dice = [random.randint(1, 6) for _ in range(3)]
    total = sum(dice)
    result = "tai" if total >= 11 else "xiu"

    await channel.send(embed=card("📢 THÔNG BÁO",
        f"[ **{dice[0]}** ] - [ **{dice[1]}** ] - [ **{dice[2]}** ]\n\n"
        f"💥 Tổng: **{total}**\n"
        f"🎯 Kết quả: **{result.upper()}**"))

    for uid, bet in list(tx["bets"].items()):
        x = user(uid)
        won = bet["choice"] == result
        text = outcome(x, bet["amount"], won, bet["amount"] * 2)
        await channel.send(embed=card(
            "🎉 BẠN THẮNG" if won else "💀 BẠN THUA",
            f"👤 {bet['name']}\n\n{text}"))

    tx["open"], tx["bets"] = False, {}

# ================= BẦU CUA =================

@bot.command()
async def bc(ctx, amount: int):
    x = user(ctx.author.id)
    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Không đủ tiền.")
    x["money"] -= amount

    await play_effect(ctx, "🦀 BẦU CUA | 🟠 ĐANG LẮC",
        f"💰 **Cục:** `{cash(amount)}`\n\n"
        "🦀 **Lắc...Lắc...Lắc rồi Hé bát...**")

    faces = ["🍐", "🦀", "🦌", "🦐", "🐓", "🐟"]
    r = random.choices(faces, k=3)
    # Bản test: trùng càng nhiều càng thắng lớn.
    target = random.choice(faces)
    hits = r.count(target)
    won = hits > 0
    payout = amount * (hits + 1) if won else 0
    text = outcome(x, amount, won, payout)

    await ctx.send(embed=card(
        "🦀 BẦU CUA | 🟢 KẾT QUẢ" if won else "🦀 BẦU CUA | 🔴 KẾT QUẢ",
        f"📢 **THÔNG BÁO**\n\n"
        f"[ {r[0]} ] | [ {r[1]} ] | [ {r[2]} ]\n\n{text}"))

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

    await play_effect(ctx, "🪙 XÓC ĐĨA | 🟠 ĐANG XÓC",
        f"💰 **Cục:** `{cash(amount)}`\n\n"
        "🪙 **Xóc...Xóc...Xóc**")

    balls = [random.choice(["🔴", "⚪"]) for _ in range(4)]
    result = "chan" if balls.count("🔴") % 2 == 0 else "le"
    won = choice == result
    text = outcome(x, amount, won, amount * 2)

    await ctx.send(embed=card(
        "🪙 XÓC ĐĨA | 🟢 KẾT QUẢ" if won else "🪙 XÓC ĐĨA | 🔴 KẾT QUẢ",
        f"📢 **THÔNG BÁO**\n\n"
        f"[ {balls[0]} ] | [ {balls[1]} ] | [ {balls[2]} ] | [ {balls[3]} ]\n\n"
        f"💥 Kết quả: **{result.upper()}**\n\n{text}"))

# ================= QUAY =================

@bot.command()
async def quay(ctx, amount: int):
    x = user(ctx.author.id)
    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Không đủ tiền.")
    x["money"] -= amount

    await play_effect(ctx, "🎰 QUAY | 🟠 ĐANG QUAY",
        f"💰 **Cục:** `{cash(amount)}`\n\n"
        "🎰 **Đang quay...**", 2)

    icons = ["🍒", "7️⃣", "🍋", "💎"]
    r = random.choices(icons, k=3)
    won = r[0] == r[1] == r[2]
    payout = amount * 5 if won else 0
    text = outcome(x, amount, won, payout)

    await ctx.send(embed=card(
        "🎰 QUAY | 🟢 JACKPOT" if won else "🎰 QUAY | 🔴 KẾT QUẢ",
        f"📢 **THÔNG BÁO**\n\n"
        f"[ {r[0]} ] | [ {r[1]} ] | [ {r[2]} ]\n\n{text}"))

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
    beats = {"keo": "bao", "bua": "keo", "bao": "bua"}

    if choice == botc:
        x["money"] += amount
        text = (f"💰 **Số tiền cược:** `{cash(amount)}`\n"
                f"🎉 **Số tiền thắng:** `0$`\n"
                f"👛 **Ví:** `{cash(x['money'])}`\n\n"
                f"🤝 **HÒA!**")
    else:
        won = beats[choice] == botc
        text = outcome(x, amount, won, amount * 2)

    await ctx.send(embed=card("✊ TÙ XÌ | 📢 THÔNG BÁO",
        f"👤 **Bạn:** {names[choice]}    🤖 **Bot:** {names[botc]}\n\n{text}"))

# ================= CODE =================

@bot.command()
async def taocode(ctx, code: str, amount: int):
    if not admin_check(ctx):
        return await ctx.send("❌ Bạn không có quyền.")
    if amount <= 0:
        return await ctx.send("❌ Số tiền không hợp lệ.")
    code = code.upper()
    if code in codes:
        return await ctx.send("❌ Code đã tồn tại.")
    codes[code] = {"amount": amount, "uses": {}, "type": "money"}
    await ctx.send(embed=card("🎁 TẠO CODE",
        f"🔑 Code: `{code}`\n💰 Giá trị: `{cash(amount)}`\n"
        f"👥 Mỗi người dùng: **1 lần**"))

@bot.command()
async def thuongcode(ctx, code: str):
    code = code.upper()
    if code not in codes:
        return await ctx.send("❌ Code không tồn tại.")
    c = codes[code]
    uid = ctx.author.id
    if uid in c["uses"]:
        return await ctx.send("❌ Bạn đã dùng code này.")
    x = user(uid)
    x["money"] += c["amount"]
    c["uses"][uid] = True
    await ctx.send(embed=card("🎁 NHẬN THƯỞNG CODE",
        f"🔑 Code: `{code}`\n"
        f"🎁 Nhận: `+{cash(c['amount'])}`\n"
        f"👛 Ví: `{cash(x['money'])}`"))

# ================= VAY =================

@bot.command()
async def vaybot(ctx, amount: int):
    uid = ctx.author.id
    if not 0 < amount <= 50000:
        return await ctx.send("❌ Bot cho vay 1$–50,000$.")
    if uid in loans:
        return await ctx.send("❌ Bạn đang có khoản vay.")
    user(uid)["money"] += amount
    loans[uid] = {"bot": True, "amount": amount}
    await ctx.send(embed=card("🏦 VAY BOT",
        f"💰 Khoản vay: `{cash(amount)}`\n⏱️ Hạn: **1 giờ**\n\n`!trano` để trả."))

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
    loans[member.id] = {"bot": False, "amount": amount, "lender": ctx.author.id}
    await ctx.send(embed=card("🤝 VAY NGƯỜI CHƠI",
        f"👤 Người vay: {member.mention}\n"
        f"💰 Khoản vay: `{cash(amount)}`\n⏱️ Hạn: **1 giờ**"))

@bot.command()
async def trano(ctx):
    uid = ctx.author.id
    if uid not in loans:
        return await ctx.send("❌ Bạn không có khoản nợ.")
    loan = loans[uid]
    x = user(uid)
    amount = loan["amount"]
    if amount > x["money"]:
        return await ctx.send(f"❌ Cần `{cash(amount)}`.")
    x["money"] -= amount
    if not loan["bot"]:
        user(loan["lender"])["money"] += amount
    del loans[uid]
    await ctx.send(embed=card("💵 TRẢ NỢ",
        f"✅ Đã trả: `{cash(amount)}`\n👛 Ví: `{cash(x['money'])}`"))

# ================= ADMIN =================

@bot.command()
async def settien(ctx, member: discord.Member, amount: int):
    if not admin_check(ctx):
        return await ctx.send("❌ Bạn không có quyền.")
    if amount < 0:
        return await ctx.send("❌ Số tiền không hợp lệ.")
    user(member.id)["money"] = amount
    await ctx.send(f"💰 {member.mention} → `{cash(amount)}`")

@bot.command()
async def resettien(ctx, member: discord.Member):
    if not admin_check(ctx):
        return await ctx.send("❌ Bạn không có quyền.")
    users[member.id] = {"money": 7500, "bank": 0, "luck": 100}
    await ctx.send(f"🔄 Đã reset {member.mention}.")

@bot.command()
async def tyle(ctx):
    await ctx.send(embed=card("📊 TỶ LỆ BET88",
"""🎲 **TÀI XỈU:** 1:1
🦀 **BẦU CUA:** Theo mặt
🪙 **XÓC ĐĨA:** 1:1
🎰 **QUAY:** Jackpot x5
✊ **TÙ XÌ:** 1:1

💎 Chúc anh em may mắn!"""))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.CheckFailure):
        return await ctx.send("❌ Bạn không có quyền.")
    if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
        return await ctx.send("❌ Sai cú pháp. Dùng `!trogiup`.")
    print("ERROR:", repr(error))

bot.run(TOKEN)
