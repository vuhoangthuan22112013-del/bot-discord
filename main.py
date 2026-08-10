import os
import json
import random
import asyncio
import time
import discord
from discord.ext import commands
PREFIX = "!"
TOKEN_NAME = "TOKEN_BOT"
DATA_FILE = "casino_data.json"
START = 2000
MIN_BET = 100
MAX_BET = 10_000_000
LOAN_MIN = 1000
LOAN_MAX = 50000
LOAN_TIME = 3600
COLORS = {
    "blue": 0x3498DB,
    "green": 0x2ECC71,
    "red": 0xE74C3C,
    "yellow": 0xF1C40F,
    "orange": 0xF39C12,
    "purple": 0x9B59B6,
}
intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)
users = {}
codes = {}
TX = {
    "on": False,
    "bets": {},
    "channel": None,
    "message": None,
    "task": None,
}
def load_data():
    global users, codes
    if not os.path.exists(DATA_FILE):
        users, codes = {}, {}
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        users = {int(k): v for k, v in data.get("users", {}).items()}
        codes = data.get("codes", {})
    except Exception as e:
        print("LOAD ERROR:", e)
        users, codes = {}, {}
def save_data():
    try:
        data = {
            "users": {str(k): v for k, v in users.items()},
            "codes": codes
        }
        tmp = DATA_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, DATA_FILE)
    except Exception as e:
        print("SAVE ERROR:", e)
load_data()
def U(member):
    if member is None:
        return None
    uid = member.id
    if uid not in users:
        users[uid] = {
            "cash": START,
            "bank": 0,
            "role": "Không có",
            "loan": 0,
            "due": 0,
            "daily": "",
            "muted": False
        }
        save_data()
    u = users[uid]
    u.setdefault("cash", START)
    u.setdefault("bank", 0)
    u.setdefault("role", "Không có")
    u.setdefault("loan", 0)
    u.setdefault("due", 0)
    u.setdefault("daily", "")
    u.setdefault("muted", False)
    return u
def money(n):
    return f"{int(n):,}$"
def total(u):
    return int(u["cash"]) + int(u["bank"])
def today():
    return time.strftime("%Y-%m-%d", time.localtime())
def overdue(u):
    return u["loan"] > 0 and time.time() > u["due"]
def E(title, text="", color=COLORS["blue"]):
    e = discord.Embed(
        title=title,
        description=text,
        color=color,
        timestamp=discord.utils.utcnow()
    )
    e.set_footer(text="🎰 CASINO BET88")
    return e
async def err(ctx, text):
    await ctx.send(embed=E("❌ KHÔNG THỂ THỰC HIỆN", text, COLORS["red"]))
def admin(ctx):
    return ctx.author.guild_permissions.administrator
def blocked(ctx):
    u = U(ctx.author)
    if u["muted"]:
        asyncio.create_task(err(
            ctx,
            "🔇 Tài khoản của bạn đang bị khóa chơi."
        ))
        return True
    if overdue(u):
        asyncio.create_task(err(
            ctx,
            f"🔴 Bạn đang quá hạn khoản vay **{money(u['loan'])}**.\n"
            f"Dùng `{PREFIX}trano {u['loan']}` để trả nợ."
        ))
        return True
    return False
def valid_bet(amount):
    return isinstance(amount, int) and MIN_BET <= amount <= MAX_BET
@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | 🎰 Casino")
    )
    print("=" * 50)
    print("BOT ONLINE:", bot.user)
    print("SERVERS:", len(bot.guilds))
    print("=" * 50)
@bot.event
async def on_disconnect():
    save_data()
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await err(ctx, "Bạn nhập thiếu thông tin cho lệnh.")
        return
    if isinstance(error, commands.BadArgument):
        await err(ctx, "Sai định dạng. Ví dụ: `!tx tai 100`.")
        return
    if isinstance(error, commands.CommandOnCooldown):
        await err(ctx, f"Vui lòng chờ **{error.retry_after:.1f} giây**.")
        return
    print("COMMAND ERROR:", repr(error))
    try:
        await err(ctx, "Bot gặp lỗi khi xử lý lệnh.")
    except Exception:
        pass
@bot.command(name="trogiup", aliases=["help"])
async def trogiup(ctx):
    text = (
        "## 🎰 TRÒ CHƠI\n"
        "`!tx tai 100` • `!tx xiu 100`\n"
        "`!bc cua 100` • `!bc tom 100`\n"
        "`!xd chan 100` • `!xd le 100`\n"
        "`!quay 100`\n\n"
        "## 💰 TÀI KHOẢN\n"
        "`!vi` • `!gui 100` • `!rut 100`\n"
        "`!chuyen @user 100`\n"
        "`!vay 1000` • `!trano 1000`\n"
        "`!diemdanh` • `!bxh`\n\n"
        "## 🛒 CỬA HÀNG\n"
        "`!cuahang` • `!muan vip`\n"
        "`!muan daigia` • `!muan typhu`\n\n"
        "## 🎟️ CODE\n"
        "`!nhapcode CODE`\n\n"
        "## 🛡️ ADMIN\n"
        "`!taocode 1000 10`\n"
        "`!settien @user 5000`\n"
        "`!kick @user` • `!ban @user`\n"
        "`!khoamom @user` • `!reset tien @user`"
    )
    await ctx.send(embed=E(
        "🎰 CASINO BET88 — TRUNG TÂM LỆNH",
        text
    ))
@bot.command(name="vi")
async def vi(ctx, member: discord.Member = None):
    member = member or ctx.author
    u = U(member)
    extra = ""
    if u["loan"] > 0:
        if overdue(u):
            extra = "\n🔴 **Khoản vay đã quá hạn.**"
        else:
            left = max(0, int(u["due"] - time.time()))
            extra = f"\n⏰ Còn: **{left // 60} phút {left % 60} giây**"
    text = (
        f"👤 {member.mention}\n\n"
        f"💵 Tiền mặt: **{money(u['cash'])}**\n"
        f"🏦 Ngân hàng: **{money(u['bank'])}**\n"
        f"💰 Tổng tài sản: **{money(total(u))}**\n"
        f"👑 Role: **{u['role']}**\n"
        f"💸 Khoản vay: **{money(u['loan'])}**"
        f"{extra}"
    )
    await ctx.send(embed=E(
        f"💳 VÍ CỦA {member.display_name}",
        text
    ))
@bot.command()
async def gui(ctx, amount: int = None):
    if amount is None or amount <= 0:
        return await err(ctx, "`!gui số_tiền`")
    u = U(ctx.author)
    if amount > u["cash"]:
        return await err(ctx, "Không đủ tiền mặt.")
    u["cash"] -= amount
    u["bank"] += amount
    save_data()
    await ctx.send(embed=E(
        "🏦 GỬI TIỀN THÀNH CÔNG",
        f"Đã gửi **{money(amount)}**.\n"
        f"Số dư ngân hàng: **{money(u['bank'])}**",
        COLORS["green"]
    ))
@bot.command()
async def rut(ctx, amount: int = None):
    if amount is None or amount <= 0:
        return await err(ctx, "`!rut số_tiền`")
    u = U(ctx.author)
    if amount > u["bank"]:
        return await err(ctx, "Ngân hàng không đủ tiền.")
    u["bank"] -= amount
    u["cash"] += amount
    save_data()
    await ctx.send(embed=E(
        "💵 RÚT TIỀN THÀNH CÔNG",
        f"Đã rút **{money(amount)}**.\n"
        f"Tiền mặt: **{money(u['cash'])}**",
        COLORS["green"]
    ))
@bot.command()
async def chuyen(ctx, member: discord.Member = None, amount: int = None):
    if member is None or amount is None:
        return await err(ctx, "`!chuyen @user số_tiền`")
    if amount < 1 or amount > 10_000_000:
        return await err(ctx, "Chỉ được chuyển 1$ - 10.000.000$.")
    if member.id == ctx.author.id:
        return await err(ctx, "Không thể chuyển cho chính mình.")
    if member.bot:
        return await err(ctx, "Không thể chuyển cho bot.")
    a, b = U(ctx.author), U(member)
    if a["cash"] < amount:
        return await err(ctx, "Không đủ tiền mặt.")
    a["cash"] -= amount
    b["cash"] += amount
    save_data()
    await ctx.send(embed=E(
        "💸 CHUYỂN TIỀN THÀNH CÔNG",
        f"{ctx.author.mention} → {member.mention}\n"
        f"💰 **{money(amount)}**",
        COLORS["green"]
    ))
@bot.command()
async def vay(ctx, amount: int = None):
    if amount is None:
        return await err(ctx, "`!vay 1000`")
    if not LOAN_MIN <= amount <= LOAN_MAX:
        return await err(ctx, "Vay từ 1.000$ đến 50.000$.")
    u = U(ctx.author)
    if u["loan"] > 0:
        return await err(ctx, "Bạn đang có khoản vay.")
    u["loan"] = amount
    u["cash"] += amount
    u["due"] = time.time() + LOAN_TIME
    save_data()
    await ctx.send(embed=E(
        "💸 VAY TIỀN THÀNH CÔNG",
        f"💰 Đã vay: **{money(amount)}**\n"
        "⏰ Thời hạn: **1 giờ**\n"
        "⚠️ Quá hạn sẽ không được chơi.\n"
        f"Trả bằng: `{PREFIX}trano {amount}`",
        COLORS["orange"]
    ))
@bot.command()
async def trano(ctx, amount: int = None):
    u = U(ctx.author)
    if u["loan"] <= 0:
        return await err(ctx, "Bạn không có khoản vay.")
    if amount != u["loan"]:
        return await err(ctx, f"Cần trả đúng **{money(u['loan'])}**.")
    if u["cash"] < amount:
        return await err(ctx, "Bạn không đủ tiền mặt.")
    u["cash"] -= amount
    u["loan"] = 0
    u["due"] = 0
    save_data()
    await ctx.send(embed=E(
        "✅ ĐÃ TRẢ NỢ",
        f"Đã trả **{money(amount)}**.\n"
        "🟢 Bạn đã được phép chơi lại.",
        COLORS["green"]
    ))
@bot.command()
async def diemdanh(ctx):
    u = U(ctx.author)
    if u["daily"] == today():
        return await err(ctx, "Hôm nay bạn đã điểm danh.")
    reward = random.randint(1000, 3000)
    u["cash"] += reward
    u["daily"] = today()
    save_data()
    await ctx.send(embed=E(
        "🎁 ĐIỂM DANH THÀNH CÔNG",
        f"💰 Nhận **{money(reward)}**\n"
        f"💵 Số dư: **{money(u['cash'])}**",
        COLORS["green"]
    ))
@bot.command()
async def bxh(ctx):
    ranking = sorted(
        users.items(),
        key=lambda x: total(x[1]),
        reverse=True
    )[:10]
    if not ranking:
        return await err(ctx, "Chưa có dữ liệu.")
    lines = []
    medals = ["🥇", "🥈", "🥉"]
    for i, (uid, u) in enumerate(ranking, 1):
        m = ctx.guild.get_member(uid)
        name = m.display_name if m else f"User {uid}"
        icon = medals[i - 1] if i <= 3 else f"**{i}.**"
        lines.append(f"{icon} **{name}** — `{money(total(u))}`")
    await ctx.send(embed=E(
        "🏆 TOP 10 GIÀU NHẤT",
        "\n".join(lines),
        COLORS["yellow"]
    ))
SLOTS = ["🍒", "🍋", "⭐", "🔔", "💎"]
@bot.command()
async def quay(ctx, amount: int = None):
    if blocked(ctx):
        return
    if amount is None or amount < 1:
        return await err(ctx, "`!quay số_tiền`")
    if amount > MAX_BET:
        return await err(ctx, f"Cược tối đa **{money(MAX_BET)}**.")
    u = U(ctx.author)
    if amount > u["cash"]:
        return await err(ctx, "Bạn không đủ tiền.")
    u["cash"] -= amount
    msg = await ctx.send(embed=E(
        "🎰 7️⃣7️⃣7️⃣ SLOT",
        "╔══════════════╗\n"
        "   ❓  |  ❓  |  ❓\n"
        "╚══════════════╝\n\n"
        "🎰 **ĐANG QUAY...**",
        COLORS["orange"]
    ))
    a, b, c = [random.choice(SLOTS) for _ in range(3)]
    await asyncio.sleep(.45)
    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣ SLOT",
        f"╔══════════════╗\n"
        f"   {a}  |  ❓  |  ❓\n"
        "╚══════════════╝",
        COLORS["orange"]
    ))
    await asyncio.sleep(.45)
    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣ SLOT",
        f"╔══════════════╗\n"
        f"   {a}  |  {b}  |  ❓\n"
        "╚══════════════╝",
        COLORS["orange"]
    ))
    await asyncio.sleep(.45)
    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣ SLOT",
        f"╔══════════════╗\n"
        f"   {a}  |  {b}  |  {c}\n"
        "╚══════════════╝",
        COLORS["orange"]
    ))
    if a == b == c:
        win = amount * 5
        u["cash"] += win
        result = f"🎉 **JACKPOT x5!**\n💰 +{money(win)}"
        color = COLORS["green"]
    elif a == b or a == c or b == c:
        win = int(amount * 1.5)
        u["cash"] += win
        result = f"✨ **2 HÌNH GIỐNG NHAU x1.5!**\n💰 +{money(win)}"
        color = COLORS["green"]
    else:
        result = f"💥 **THUA!**\n💸 -{money(amount)}"
        color = COLORS["red"]
    save_data()
    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣ SLOT — KẾT QUẢ",
        f"╔══════════════╗\n"
        f"   {a}  |  {b}  |  {c}\n"
        "╚══════════════╝\n\n"
        f"{result}\n\n"
        f"💵 Số dư: **{money(u['cash'])}**",
        color
    ))
BC = {
    "ca": "🐟",
    "tom": "🦐",
    "cua": "🦀",
    "bau": "🥒",
    "ga": "🐓",
    "nai": "🦌"
}
@bot.command()
async def bc(ctx, choice: str = None, amount: int = None):
    if blocked(ctx):
        return
    if choice is None or choice.lower() not in BC:
        return await err(ctx, "`!bc ca/tom/cua/bau/ga/nai 100`")
    choice = choice.lower()
    if amount is None or amount < 1:
        return await err(ctx, "`!bc cua 100`")
    if amount > MAX_BET:
        return await err(ctx, f"Cược tối đa **{money(MAX_BET)}**.")
    u = U(ctx.author)
    if amount > u["cash"]:
        return await err(ctx, "Bạn không đủ tiền.")
    u["cash"] -= amount
    msg = await ctx.send(embed=E(
        "🎲 BẦU CUA",
        "╔══════════════════╗\n"
        "   ❓  |  ❓  |  ❓\n"
        "╚══════════════════╝\n\n"
        "🥣 **ĐANG LẮC...**",
        COLORS["orange"]
    ))
    await asyncio.sleep(1)
    r = [random.choice(list(BC)) for _ in range(3)]
    board = "  |  ".join(BC[x] for x in r)
    count = r.count(choice)
    if count:
        win = amount * (count + 1)
        u["cash"] += win
        result = f"🟢 **TRÚNG {count} CON! x{count + 1}**\n💰 +{money(win)}"
        color = COLORS["green"]
    else:
        result = f"🔴 **THUA!**\n💸 -{money(amount)}"
        color = COLORS["red"]
    save_data()
    await msg.edit(embed=E(
        "🎲 BẦU CUA — KẾT QUẢ",
        f"╔══════════════════╗\n"
        f"   {board}\n"
        "╚══════════════════╝\n\n"
        f"🎯 Bạn chọn: **{choice.upper()}**\n\n"
        f"{result}\n\n"
        f"💵 Số dư: **{money(u['cash'])}**",
        color
    ))
@bot.command()
async def xd(ctx, choice: str = None, amount: int = None):
    if blocked(ctx):
        return
    if choice not in ["chan", "le"]:
        return await err(ctx, "`!xd chan 100` hoặc `!xd le 100`")
    if amount is None or amount < 1:
        return await err(ctx, "`!xd chan 100`")
    if amount > MAX_BET:
        return await err(ctx, f"Cược tối đa **{money(MAX_BET)}**.")
    u = U(ctx.author)
    if amount > u["cash"]:
        return await err(ctx, "Bạn không đủ tiền.")
    u["cash"] -= amount
    msg = await ctx.send(embed=E(
        "🪙 XÓC ĐĨA",
        "╔══════════════════╗\n"
        "       🥣\n"
        "   🔴 🔴 🔴 🔴\n"
        "╚══════════════════╝\n\n"
        "🥣 **ĐANG XÓC...**",
        COLORS["orange"]
    ))
    await asyncio.sleep(1.4)
    balls = [random.randint(0, 1) for _ in range(4)]
    n = sum(balls)
    result = "chan" if n % 2 == 0 else "le"
    board = "  ".join("🔴" if x else "⚪" for x in balls)
    if choice == result:
        win = amount * 2
        u["cash"] += win
        result_text = f"🟢 **THẮNG x2!**\n💰 +{money(win)}"
        color = COLORS["green"]
    else:
        result_text = f"🔴 **THUA!**\n💸 -{money(amount)}"
        color = COLORS["red"]
    save_data()
    await msg.edit(embed=E(
        "🪙 XÓC ĐĨA — KẾT QUẢ",
        f"╔══════════════════╗\n"
        f"   {board}\n"
        "╚══════════════════╝\n\n"
        f"🔴 Số đỏ: **{n}**\n"
        f"🎯 Kết quả: **{result.upper()}**\n"
        f"🎲 Bạn chọn: **{choice.upper()}**\n\n"
        f"{result_text}\n\n"
        f"💵 Số dư: **{money(u['cash'])}**",
        color
    ))
async def tx_display(msg, left):
    await msg.edit(embed=E(
        "🎲 TÀI XỈU — ĐANG NHẬN CƯỢC",
        "╔══════════════════════╗\n"
        "        🎲 TÀI XỈU\n"
        "╚══════════════════════╝\n\n"
        f"⏳ Còn **{left} giây**\n"
        f"👥 Người chơi: **{len(TX['bets'])}**\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔴 TÀI → `!tx tai số_tiền`\n"
        "🔵 XỈU → `!tx xiu số_tiền`\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "⚠️ Mỗi người chỉ được cược 1 lần.",
        COLORS["orange"]
    ))
async def tx_finish(ctx, msg):
    if not TX["on"]:
        return
    TX["on"] = False
    d = [random.randint(1, 6) for _ in range(3)]
    total_dice = sum(d)
    result = "tai" if total_dice >= 11 else "xiu"
    icon = "🔴" if result == "tai" else "🔵"
    lines = [
        "╔══════════════════════╗",
        f"       🎲 {d[0]}  |  {d[1]}  |  {d[2]}",
        "╚══════════════════════╝",
        "",
        f"🎯 Tổng điểm: **{total_dice}**",
        f"{icon} Kết quả: **{result.upper()}**",
        "",
        "━━━━━━━━━━━━━━━━━━━━"
    ]
    winners = 0
    losers = 0
    for uid, bet in list(TX["bets"].items()):
        member = ctx.guild.get_member(uid)
        if member is None:
            continue
        u = U(member)
        if bet["choice"] == result:
            win = bet["amount"] * 2
            u["cash"] += win
            winners += 1
            lines += [
                f"🟢 {member.mention}",
                f"   🎯 {bet['choice'].upper()} • 💰 +{money(win)}",
                ""
            ]
        else:
            losers += 1
            lines += [
                f"🔴 {member.mention}",
                f"   🎯 {bet['choice'].upper()} • 💸 -{money(bet['amount'])}",
                ""
            ]
    lines += [
        "━━━━━━━━━━━━━━━━━━━━",
        f"🟢 Người thắng: **{winners}**",
        f"🔴 Người thua: **{losers}**"
    ]
    TX["bets"] = {}
    TX["channel"] = None
    TX["message"] = None
    TX["task"] = None
    save_data()
    await msg.edit(embed=E(
        "🎲 TÀI XỈU — KẾT QUẢ",
        "\n".join(lines),
        COLORS["green"] if result == "tai" else COLORS["blue"]
    ))
async def tx_timer(ctx, msg):
    try:
        for left in [20, 10]:
            await asyncio.sleep(10)
            if not TX["on"]:
                return
            await tx_display(msg, left)
        await asyncio.sleep(10)
        if TX["on"]:
            await tx_finish(ctx, msg)
    except asyncio.CancelledError:
        return
    except Exception as e:
        print("TX ERROR:", e)
        TX["on"] = False
        TX["bets"] = {}
        TX["channel"] = None
        TX["message"] = None
        TX["task"] = None
@bot.command()
async def tx(ctx, choice: str = None, amount: int = None):
    if blocked(ctx):
        return
    if choice is None:
        return await err(ctx, "`!tx tai 100` hoặc `!tx xiu 100`")
    choice = choice.lower().strip()
    if choice not in ["tai", "xiu"]:
        return await err(ctx, "Chỉ được chọn **tai** hoặc **xiu**.")
    if not valid_bet(amount):
        return await err(
            ctx,
            f"Cược từ **{money(MIN_BET)}** đến **{money(MAX_BET)}**."
        )
    u = U(ctx.author)
    if u["cash"] < amount:
        return await err(ctx, "Bạn không đủ tiền.")
    if not TX["on"]:
        TX["on"] = True
        TX["bets"] = {}
        TX["channel"] = ctx.channel.id
        u["cash"] -= amount
        TX["bets"][ctx.author.id] = {
            "choice": choice,
            "amount": amount
        }
        save_data()
        msg = await ctx.send(embed=E(
            "🎲 TÀI XỈU — PHIÊN MỚI",
            "╔══════════════════════╗\n"
            "        🎲 TÀI XỈU\n"
            "╚══════════════════════╝\n\n"
            f"👤 Người mở: {ctx.author.mention}\n"
            f"🎯 Cửa: **{choice.upper()}**\n"
            f"💰 Cược: **{money(amount)}**\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🟠 **ĐANG NHẬN CƯỢC**\n"
            "⏳ **Còn 30 giây**\n"
            "👥 Người chơi: **1**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔴 TÀI → `!tx tai số_tiền`\n"
            "🔵 XỈU → `!tx xiu số_tiền`\n\n"
            "⚠️ Mỗi người chỉ được cược 1 lần.",
            COLORS["orange"]
        ))
        TX["message"] = msg.id
        TX["task"] = asyncio.create_task(tx_timer(ctx, msg))
        return
    if TX["channel"] != ctx.channel.id:
        return await err(ctx, "Phiên Tài Xỉu đang chạy ở kênh khác.")
    if ctx.author.id in TX["bets"]:
        return await err(ctx, "Bạn đã cược trong phiên này rồi.")
    u["cash"] -= amount
    TX["bets"][ctx.author.id] = {
        "choice": choice,
        "amount": amount
    }
    save_data()
    await ctx.send(embed=E(
        "🎯 ĐẶT CƯỢC THÀNH CÔNG",
        f"👤 {ctx.author.mention}\n"
        f"🎯 Cửa: **{choice.upper()}**\n"
        f"💰 Cược: **{money(amount)}**\n\n"
        f"👥 Người chơi: **{len(TX['bets'])}**",
        COLORS["green"]
    ))
@bot.command()
async def taocode(ctx, amount: int = None, uses: int = None):
    if not admin(ctx):
        return await err(ctx, "Chỉ Admin.")
    if amount is None or uses is None:
        return await err(ctx, "`!taocode số_tiền số_lượt`")
    if amount < 1 or uses < 1:
        return await err(ctx, "Số tiền và lượt phải lớn hơn 0.")
    code = "CASINO" + str(random.randint(100000, 999999))
    while code in codes:
        code = "CASINO" + str(random.randint(100000, 999999))
    codes[code] = {
        "amount": amount,
        "uses": uses
    }
    save_data()
    try:
        await ctx.author.send(embed=E(
            "🎟️ CODE CASINO",
            f"🔐 `{code}`\n"
            f"💰 **{money(amount)}**\n"
            f"🔢 **{uses} lượt**",
            COLORS["green"]
        ))
        await ctx.send(embed=E(
            "✅ TẠO CODE",
            "Code đã được gửi qua DM.",
            COLORS["green"]
        ))
    except discord.Forbidden:
        await ctx.send(embed=E(
            "⚠️ KHÔNG GỬI ĐƯỢC DM",
            f"Code: `{code}`\n"
            f"💰 {money(amount)}\n"
            f"🔢 {uses} lượt",
            COLORS["orange"]
        ))
@bot.command()
async def nhapcode(ctx, code: str = None):
    if not code:
        return await err(ctx, "`!nhapcode CODE`")
    code = code.upper().strip()
    if code not in codes:
        return await err(ctx, "Code không tồn tại.")
    data = codes[code]
    if isinstance(data, list):
        amount, uses = int(data[0]), int(data[1])
    else:
        amount, uses = int(data["amount"]), int(data["uses"])
    if uses <= 0:
        return await err(ctx, "Code đã hết lượt.")
    u = U(ctx.author)
    u["cash"] += amount
    if isinstance(data, list):
        codes[code][1] -= 1
    else:
        codes[code]["uses"] -= 1
    save_data()
    await ctx.send(embed=E(
        "🎟️ NHẬP CODE THÀNH CÔNG",
        f"💰 Nhận: **{money(amount)}**\n"
        f"🔢 Còn: **{uses - 1} lượt**\n"
        f"💵 Số dư: **{money(u['cash'])}**",
        COLORS["green"]
    ))
@bot.command()
async def settien(ctx, member: discord.Member = None, amount: int = None):
    if not admin(ctx):
        return await err(ctx, "Chỉ Admin.")
    if member is None or amount is None:
        return await err(ctx, "`!settien @user số_tiền`")
    if amount < 0:
        return await err(ctx, "Không được đặt tiền âm.")
    U(member)["cash"] = amount
    save_data()
    await ctx.send(embed=E(
        "🛡️ SET TIỀN",
        f"{member.mention} → **{money(amount)}**",
        COLORS["green"]
    ))
@bot.command()
async def kick(ctx, member: discord.Member = None):
    if not admin(ctx):
        return await err(ctx, "Chỉ Admin.")
    if member is None:
        return await err(ctx, "`!kick @user`")
    try:
        await member.kick(reason=f"Casino bot - {ctx.author}")
        await ctx.send(embed=E(
            "👢 KICK THÀNH CÔNG",
            f"Đã kick {member.mention}.",
            COLORS["green"]
        ))
    except discord.Forbidden:
        await err(ctx, "Bot không có quyền kick người này.")
@bot.command()
async def ban(ctx, member: discord.Member = None):
    if not admin(ctx):
        return await err(ctx, "Chỉ Admin.")
    if member is None:
        return await err(ctx, "`!ban @user`")
    try:
        await member.ban(reason=f"Casino bot - {ctx.author}")
        await ctx.send(embed=E(
            "🔨 BAN THÀNH CÔNG",
            f"Đã ban {member.mention}.",
            COLORS["green"]
        ))
    except discord.Forbidden:
        await err(ctx, "Bot không có quyền ban người này.")
@bot.command()
async def khoamom(ctx, member: discord.Member = None):
    if not admin(ctx):
        return await err(ctx, "Chỉ Admin.")
    if member is None:
        return await err(ctx, "`!khoamom @user`")
    u = U(member)
    u["muted"] = not u["muted"]
    save_data()
    if u["muted"]:
        await ctx.send(embed=E(
            "🔇 KHÓA TÀI KHOẢN",
            f"{member.mention} đã bị khóa chơi.",
            COLORS["orange"]
        ))
    else:
        await ctx.send(embed=E(
            "🔊 MỞ KHÓA",
            f"{member.mention} đã được mở khóa.",
            COLORS["green"]
        ))
@bot.command()
async def reset(ctx, what: str = None, member: discord.Member = None):
    if not admin(ctx):
        return await err(ctx, "Chỉ Admin.")
    if what != "tien" or member is None:
        return await err(ctx, "`!reset tien @user`")
    u = U(member)
    u["cash"] = START
    u["bank"] = 0
    save_data()
    await ctx.send(embed=E(
        "♻️ RESET TIỀN",
        f"{member.mention}\n"
        f"💵 Tiền mặt: **{money(START)}**\n"
        "🏦 Ngân hàng: **0$**",
        COLORS["green"]
    ))
SHOP = {
    "vip": ("VIP", 10_000_000, "💛"),
    "daigia": ("Đại Gia", 5_000_000, "💙"),
    "typhu": ("Tỷ Phú", 1_000_000_000, "💜")
}
@bot.command()
async def cuahang(ctx):
    text = (
        "## 🛒 CỬA HÀNG ROLE\n\n"
        "💛 **VIP** — `10.000.000$`\n"
        "`!muan vip`\n\n"
        "💙 **ĐẠI GIA** — `5.000.000$`\n"
        "`!muan daigia`\n\n"
        "💜 **TỶ PHÚ** — `1.000.000.000$`\n"
        "`!muan typhu`"
    )
    await ctx.send(embed=E(
        "🛒 CỬA HÀNG CASINO",
        text,
        COLORS["yellow"]
    ))
@bot.command()
async def muan(ctx, name: str = None):
    if not name or name.lower() not in SHOP:
        return await err(ctx, "`!muan vip/daigia/typhu`")
    name = name.lower()
    role_name, price, emoji = SHOP[name]
    u = U(ctx.author)
    if u["cash"] < price:
        return await err(ctx, "Không đủ tiền.")
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role is None:
        return await err(ctx, f"Chưa có role **{role_name}**.")
    if role >= ctx.guild.me.top_role:
        return await err(ctx, "Role cao hơn role bot.")
    if role in ctx.author.roles:
        return await err(ctx, "Bạn đã có role này.")
    try:
        await ctx.author.add_roles(role, reason="Casino shop")
    except discord.Forbidden:
        return await err(ctx, "Bot không có quyền gán role.")
    u["cash"] -= price
    u["role"] = role_name
    save_data()
    await ctx.send(embed=E(
        "👑 MUA ROLE THÀNH CÔNG",
        f"{ctx.author.mention}\n"
        f"{emoji} **{role_name}**\n"
        f"💰 Giá: **{money(price)}**\n"
        f"💵 Còn: **{money(u['cash'])}**",
        COLORS["green"]
    ))
@bot.command()
async def botinfo(ctx):
    await ctx.send(embed=E(
        "🤖 THÔNG TIN BOT",
        f"🤖 Bot: **{bot.user}**\n"
        f"🌐 Server: **{len(bot.guilds)}**\n"
        f"👥 Người chơi: **{len(users)}**\n"
        f"🎲 Tài Xỉu: **{'ĐANG CHẠY' if TX['on'] else 'ĐANG CHỜ'}**\n"
        f"💾 Database: **{DATA_FILE}**",
        COLORS["purple"]
    ))
TOKEN = os.getenv(TOKEN_BOT)
if not TOKEN:
    print("❌ Không tìm thấy TOKEN_BOT!")
else:
    bot.run(TOKEN)
    
