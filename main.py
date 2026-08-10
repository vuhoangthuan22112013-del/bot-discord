import discord, os, random, time, asyncio
from discord.ext import commands

TOKEN = os.getenv("BOT_TOKEN")
PREFIX = "!"
START = 2000

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

users = {}
codes = {}
last_daily = {}
debts = {}
banned = set()
muted = set()

def user(uid):
    if uid not in users:
        users[uid] = START
    return users[uid]

def money(uid):
    return user(uid)

def fmt(n):
    return f"{n:,}$"

def name(ctx):
    return ctx.author.display_name

def blocked(uid):
    if uid in banned:
        return True
    if uid in debts and time.time() >= debts[uid]["due"]:
        return True
    return False

async def checkplay(ctx):
    uid = ctx.author.id
    if uid in banned:
        await ctx.send("⛔ Bạn đã bị cấm sử dụng bot.")
        return False
    if uid in muted:
        await ctx.send("🔇 Bạn đang bị khóa chat.")
        return False
    if uid in debts:
        d = debts[uid]
        if time.time() >= d["due"]:
            d["overdue"] = True
            await ctx.send("💳 Bạn đang là **CON NỢ**!\n❌ Trả nợ bằng `!trano` rồi mới được chơi.")
            return False
    return True

def embed(title, desc="", color=0x5865F2):
    return discord.Embed(title=title, description=desc, color=color)

@bot.event
async def on_ready():
    print(f"BOT ONLINE: {bot.user}")
    try:
        await bot.tree.sync()
    except:
        pass

@bot.command()
async def vi(ctx):
    e = embed(
        f"💳 VÍ CỦA {name(ctx)}",
        f"💵 **Tiền mặt:** `{fmt(money(ctx.author.id))}`\n"
        f"🏦 **Ngân hàng:** `0$`\n"
        f"👑 **Trạng thái:** `{'CON NỢ' if blocked(ctx.author.id) else 'Bình thường'}`",
        0x3498DB
    )
    await ctx.send(embed=e)

@bot.command()
async def diemdanh(ctx):
    uid = ctx.author.id
    today = time.strftime("%Y-%m-%d")
    if last_daily.get(uid) == today:
        await ctx.send("⏰ Hôm nay bạn đã điểm danh rồi!")
        return
    n = random.randint(1000, 3000)
    users[uid] = money(uid) + n
    last_daily[uid] = today
    await ctx.send(embed=embed(
        "📅 ĐIỂM DANH THÀNH CÔNG",
        f"🎁 Bạn nhận được **{fmt(n)}**!\n💰 Số dư: **{fmt(money(uid))}**",
        0x2ECC71
    ))

@bot.command()
async def bxh(ctx):
    top = sorted(users.items(), key=lambda x:x[1], reverse=True)[:5]
    text = ""
    for i,(uid,b) in enumerate(top,1):
        u = bot.get_user(uid)
        text += f"**{i}.** {u.display_name if u else uid} — 💰 `{fmt(b)}`\n"
    await ctx.send(embed=embed("🏆 TOP 5 GIÀU NHẤT", text or "Chưa có dữ liệu.", 0xF1C40F))

@bot.command()
async def quay(ctx, amount: int):
    if not await checkplay(ctx): return
    uid = ctx.author.id
    if amount <= 0 or money(uid) < amount:
        await ctx.send("❌ Bạn không đủ tiền.")
        return
    users[uid] -= amount
    icons = ["🍒","🍋","⭐","🔔","🍉","💎"]
    a,b,c = random.choices(icons,k=3)

    e = embed("🎰 777 SLOT", f"**[ {a} ]   [ {b} ]   [ {c} ]**")
    msg = await ctx.send(embed=e)
    await asyncio.sleep(.7)

    same = len({a,b,c})
    if a == b == c:
        win = amount * 5
        users[uid] += win
        result = f"🟢 **JACKPOT x5!**\n💰 Nhận **{fmt(win)}**"
        color = 0x2ECC71
    elif same == 2:
        win = amount * 3 // 2
        users[uid] += win
        result = f"🟢 **2 HÌNH GIỐNG NHAU x1.5!**\n💰 Nhận **{fmt(win)}**"
        color = 0x2ECC71
    else:
        result = f"🔴 **THUA!**\n💸 Mất **{fmt(amount)}**"
        color = 0xE74C3C

    await msg.edit(embed=embed("🎰 777 SLOT", f"**[ {a} ]   [ {b} ]   [ {c} ]**\n\n{result}", color))

@bot.command()
async def bc(ctx, amount: int):
    if not await checkplay(ctx): return
    uid = ctx.author.id
    if amount <= 0 or money(uid) < amount:
        await ctx.send("❌ Bạn không đủ tiền.")
        return
    users[uid] -= amount
    icons = ["🦀","🦌","🐟","🐓","🍐","🦐"]
    roll = random.choices(icons,k=3)

    e = embed("🎲 BẦU CUA", "🎲 **Đang lắc...**")
    msg = await ctx.send(embed=e)
    await asyncio.sleep(.7)

    pick = random.choice(icons)
    count = roll.count(pick)

    if count:
        win = amount * count
        users[uid] += win
        result = f"🟢 **TRÚNG {count} CON! x{count}**\n💰 Nhận **{fmt(win)}**"
        color = 0x2ECC71
    else:
        result = f"🔴 **THUA!**\n💸 Mất **{fmt(amount)}**"
        color = 0xE74C3C

    await msg.edit(embed=embed(
        "🎲 BẦU CUA",
        f"**{roll[0]}   {roll[1]}   {roll[2]}**\n\n🎯 Chọn: **{pick}**\n{result}",
        color
    ))

@bot.command()
async def vay(ctx, amount: int):
    uid = ctx.author.id
    if amount < 1000 or amount > 50000:
        await ctx.send("❌ Chỉ được vay từ **1.000$ đến 50.000$**.")
        return
    if uid in debts:
        await ctx.send("❌ Bạn đang có khoản vay. Hãy trả bằng `!trano`.")
        return
    users[uid] = money(uid) + amount
    debts[uid] = {
        "amount": amount,
        "due": time.time() + 3600,
        "overdue": False
    }
    await ctx.send(embed=embed(
        "💳 KHOẢN VAY",
        f"✅ Bạn đã vay **{fmt(amount)}**.\n"
        f"⏰ Thời hạn: **1 giờ**.\n"
        f"⚠️ Quá hạn sẽ thành **CON NỢ** và không được chơi.\n"
        f"💡 Trả bằng: `!trano {amount}`",
        0xE67E22
    ))

@bot.command()
async def trano(ctx, amount: int):
    uid = ctx.author.id
    if uid not in debts:
        await ctx.send("❌ Bạn không có khoản nợ.")
        return
    debt = debts[uid]["amount"]
    if amount != debt:
        await ctx.send(f"❌ Bạn phải trả đúng **{fmt(debt)}**.")
        return
    if money(uid) < amount:
        await ctx.send("❌ Bạn không đủ tiền để trả nợ.")
        return
    users[uid] -= amount
    del debts[uid]
    await ctx.send(embed=embed(
        "✅ ĐÃ TRẢ NỢ",
        f"💳 Bạn đã trả **{fmt(amount)}**.\n"
        f"🟢 Trạng thái: **Đã trả nợ**\n"
        f"💰 Còn lại: **{fmt(money(uid))}**",
        0x2ECC71
    ))

@bot.command()
async def nhapcode(ctx, code: str):
    code = code.upper()
    if code not in codes:
        await ctx.send("❌ Code không tồn tại hoặc đã hết lượt.")
        return
    c = codes[code]
    uid = ctx.author.id
    if uid in c["used"]:
        await ctx.send("❌ Bạn đã nhập code này rồi.")
        return
    if c["left"] <= 0:
        await ctx.send("❌ Code đã hết lượt nhập.")
        return

    c["used"].add(uid)
    c["left"] -= 1
    users[uid] = money(uid) + c["money"]

    await ctx.send(embed=embed(
        "🎟️ NHẬP CODE THÀNH CÔNG",
        f"🔑 Code: `{code}`\n"
        f"💰 Nhận: **{fmt(c['money'])}**\n"
        f"🎫 Lượt còn: **{c['left']}**",
        0x2ECC71
    ))

@bot.command()
@commands.has_permissions(administrator=True)
async def thuongcode(ctx, amount: int, lượt: int):
    if amount <= 0 or lượt <= 0:
        await ctx.send("❌ Số tiền và lượt phải lớn hơn 0.")
        return

    code = "CODE" + str(random.randint(100000,999999))
    while code in codes:
        code = "CODE" + str(random.randint(100000,999999))

    codes[code] = {
        "money": amount,
        "left": lượt,
        "used": set()
    }

    await ctx.send(embed=embed(
        "🎁 CODE THƯỞNG ĐÃ TẠO",
        f"🔑 **CODE:** `{code}`\n"
        f"💰 **Tiền thưởng:** `{fmt(amount)}`\n"
        f"🎫 **Lượt nhập:** `{lượt}`\n\n"
        f"📌 Người chơi dùng: `!nhapcode {code}`",
        0xF1C40F
    ))

@bot.command()
@commands.has_permissions(administrator=True)
async def settien(ctx, member: discord.Member, amount: int):
    if amount < 0:
        await ctx.send("❌ Số tiền không hợp lệ.")
        return
    users[member.id] = amount
    await ctx.send(f"✅ Đã set tiền của **{member.display_name}** thành **{fmt(amount)}**.")

@bot.command()
@commands.has_permissions(administrator=True)
async def resettien(ctx, member: discord.Member):
    users[member.id] = START
    await ctx.send(f"♻️ Đã reset tiền của **{member.display_name}** về **{fmt(START)}**.")

@bot.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member):
    try:
        await member.kick(reason="Admin kick")
        await ctx.send(f"👢 Đã kick **{member.display_name}**.")
    except:
        await ctx.send("❌ Không thể kick người này.")

@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member):
    try:
        await member.ban(reason="Admin ban")
        banned.add(member.id)
        await ctx.send(f"🔨 Đã ban **{member.display_name}**.")
    except:
        await ctx.send("❌ Không thể ban người này.")

@bot.command()
@commands.has_permissions(administrator=True)
async def khoamom(ctx, member: discord.Member):
    if member.id in muted:
        muted.remove(member.id)
        await ctx.send(f"🔊 Đã mở khóa chat cho **{member.display_name}**.")
    else:
        muted.add(member.id)
        await ctx.send(f"🔇 Đã khóa chat **{member.display_name}**.")

@bot.command()
async def trogiup(ctx):
    e = embed("📖 HƯỚNG DẪN BOT CỜ BẠC", color=0x5865F2)
    e.add_field(
        name="🎰 GAME",
        value="`!quay 1000` • `!bc 1000`",
        inline=False
    )
    e.add_field(
        name="💳 TÀI KHOẢN",
        value="`!vi` • `!vay 1000` • `!trano 1000`\n`!diemdanh` • `!bxh`",
        inline=False
    )
    e.add_field(
        name="🎁 CODE",
        value="`!nhapcode CODE`",
        inline=False
    )
    e.add_field(
        name="🛒 CỬA HÀNG",
        value="`!cuahang` • `!mua vip`",
        inline=False
    )
    if ctx.author.guild_permissions.administrator:
        e.add_field(
            name="🛡️ ADMIN",
            value="`!thuongcode tiền lượt`\n"
                  "`!settien @user tiền`\n"
                  "`!resettien @user`\n"
                  "`!kick @user` • `!ban @user`\n"
                  "`!khoamom @user`",
            inline=False
        )
    await ctx.send(embed=e)

@bot.command()
async def cuahang(ctx):
    await ctx.send(embed=embed(
        "🛒 CỬA HÀNG",
        "👑 `!mua vip` — Mua VIP\n"
        "💎 `!mua daigia` — Gói đại gia\n"
        "🔥 `!mua typhu` — Gói tỷ phú",
        0x9B59B6
    ))

@bot.command()
async def mua(ctx, item: str):
    prices = {"vip":5000, "daigia":20000, "typhu":50000}
    item = item.lower()
    if item not in prices:
        await ctx.send("❌ Sản phẩm không tồn tại.")
        return
    p = prices[item]
    if money(ctx.author.id) < p:
        await ctx.send("❌ Bạn không đủ tiền.")
        return
    users[ctx.author.id] -= p
    await ctx.send(embed=embed(
        "🛒 MUA HÀNG",
        f"✅ Bạn đã mua **{item.upper()}**!\n💸 Giá: **{fmt(p)}**",
        0x2ECC71
    ))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Thiếu thông tin. Gõ `!trogiup` để xem cách dùng.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Sai cú pháp. Ví dụ: `!quay 1000` hoặc `!settien @user 50000`.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("⛔ Bạn không có quyền Admin.")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        print("ERROR:", error)

bot.run(TOKEN)
