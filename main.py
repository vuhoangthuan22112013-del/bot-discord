import os,random,time,asyncio,discord
from discord.ext import commands

TOKEN=os.getenv("TOKEN_BOT")
START=2000
users={}
codes={}
spam={}
loans={}

intents=discord.Intents.all()
bot=commands.Bot(command_prefix="!",intents=intents,help_command=None)

def U(m):
    if m.id not in users:
        users[m.id]={
            "cash":START,"bank":0,
            "daily":"","muted":False
        }
    return users[m.id]

def fm(n):
    return f"{n:,}$"

def E(t,d,c=0x3498DB):
    return discord.Embed(title=t,description=d,color=c)

def adm(ctx):
    return ctx.author.guild_permissions.administrator

def block(ctx):
    u=U(ctx.author)

    if u["muted"]:
        asyncio.create_task(ctx.send(
            "🔇 **Bạn đang bị khóa mõm!**"
        ))
        return True

    if ctx.author.id in loans:
        if time.time()>loans[ctx.author.id]["due"]:
            asyncio.create_task(ctx.send(
                "🔴 **CON NỢ!**\n"
                "Bạn không được chơi game.\n"
                "💳 Dùng `!trano số_tiền` để trả nợ."
            ))
            return True

    return False

# ================= CHỐNG SPAM =================

@bot.check
async def anti_spam(ctx):
    if ctx.author.bot:
        return False

    now=time.time()
    uid=ctx.author.id
    last=spam.get(uid,0)

    if now-last<1.5:
        return False

    spam[uid]=now
    return True

# ================= ONLINE =================

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino")
    )

    print("================================")
    print("BOT ONLINE:",bot.user)
    print("ID:",bot.user.id)
    print("================================")

# ================= HELP =================

@bot.command()
async def trogiup(ctx):

    t=(
        "## 🎰 GAME\n"
        "`!quay 100` • `!bc cua 100`\n"
        "`!xd chan 100` • `!xd le 100`\n"
        "`!tx tai 100` • `!tx xiu 100`\n\n"

        "## 💰 TÀI KHOẢN\n"
        "`!vi`\n"
        "`!vay 1000` • `!trano 1000`\n"
        "`!diemdanh` • `!bxh`\n\n"

        "## 🎟️ CODE\n"
        "`!nhapcode CODE`\n"
    )

    if adm(ctx):
        t+=(
            "\n## 🛡️ ADMIN\n"
            "`!taocode tiền lượt`\n"
            "`!thuongcode tiền lượt`\n"
            "`!settien @user tiền`\n"
            "`!reset tien @user`\n"
            "`!kick @user`\n"
            "`!ban @user`\n"
            "`!khoamom @user`\n"
            "`!unkhoamom @user`"
        )

    await ctx.send(
        embed=E("📖 HƯỚNG DẪN CASINO",t)
    )

# ================= VÍ =================

@bot.command()
async def vi(ctx,m:discord.Member=None):
    m=m or ctx.author
    u=U(m)

    loan=loans.get(
        m.id,{}
    ).get("amount",0)

    status="🟢 Bình thường"

    if m.id in loans:
        if time.time()>loans[m.id]["due"]:
            status="🔴 CON NỢ"

    await ctx.send(embed=E(
        f"💳 VÍ CỦA {m.display_name}",
        f"💵 Tiền: **{fm(u['cash'])}**\n"
        f"🏦 Ngân hàng: **{fm(u['bank'])}**\n"
        f"💸 Khoản vay: **{fm(loan)}**\n"
        f"📌 Trạng thái: **{status}**"
    ))

# ================= DAILY =================

@bot.command()
async def diemdanh(ctx):
    u=U(ctx.author)
    today=time.strftime("%Y-%m-%d")

    if u["daily"]==today:
        return await ctx.send(
            "⏰ Hôm nay bạn đã điểm danh rồi."
        )

    n=random.randint(1000,3000)

    u["cash"]+=n
    u["daily"]=today

    await ctx.send(embed=E(
        "🎁 ĐIỂM DANH",
        f"🎉 Bạn nhận **{fm(n)}**!\n"
        f"💰 Số dư: **{fm(u['cash'])}**",
        0x2ECC71
    ))

# ================= BXH =================

@bot.command()
async def bxh(ctx):

    arr=sorted(
        users.items(),
        key=lambda x:x[1]["cash"]+x[1]["bank"],
        reverse=True
    )[:5]

    s=""

    for i,(uid,u) in enumerate(arr,1):
        m=ctx.guild.get_member(uid)
        n=m.display_name if m else str(uid)

        total=u["cash"]+u["bank"]

        s+=(
            f"**{i}.** {n} "
            f"— 💰 `{fm(total)}`\n"
        )

    await ctx.send(embed=E(
        "🏆 TOP 5 GIÀU NHẤT",
        s or "Chưa có dữ liệu.",
        0xF1C40F
    ))

# ================= VAY =================

@bot.command()
async def vay(ctx,amount:int=None):

    if not amount or not 1000<=amount<=50000:
        return await ctx.send(
            "❌ Chỉ được vay **1.000$ - 50.000$**."
        )

    if ctx.author.id in loans:
        return await ctx.send(
            "❌ Bạn đang có khoản vay."
        )

    U(ctx.author)["cash"]+=amount

    loans[ctx.author.id]={
        "amount":amount,
        "due":time.time()+3600
    }

    await ctx.send(embed=E(
        "💳 VAY TIỀN THÀNH CÔNG",
        f"✅ Bạn đã vay **{fm(amount)}**.\n"
        "⏰ Thời hạn: **1 giờ**.\n"
        "⚠️ Quá hạn sẽ thành **CON NỢ**.\n\n"
        f"💡 Trả bằng `!trano {amount}`",
        0xF39C12
    ))

# ================= TRẢ NỢ =================

@bot.command()
async def trano(ctx,amount:int=None):

    if ctx.author.id not in loans:
        return await ctx.send(
            "❌ Bạn không có khoản nợ."
        )

    d=loans[ctx.author.id]["amount"]

    if amount!=d:
        return await ctx.send(
            f"❌ Phải trả đúng **{fm(d)}**."
        )

    u=U(ctx.author)

    if u["cash"]<d:
        return await ctx.send(
            "❌ Bạn không đủ tiền."
        )

    u["cash"]-=d

    del loans[ctx.author.id]

    await ctx.send(embed=E(
        "✅ ĐÃ TRẢ NỢ",
        f"{ctx.author.mention} đã trả "
        f"**{fm(d)}**.\n"
        "🟢 Bạn được phép chơi lại!",
        0x2ECC71
    ))

# ================= SLOT =================

@bot.command()
async def quay(ctx,amount:int=None):

    if block(ctx):
        return

    if not amount or amount<1:
        return await ctx.send(
            "❌ `!quay số_tiền`"
        )

    u=U(ctx.author)

    if amount>u["cash"]:
        return await ctx.send(
            "❌ Không đủ tiền."
        )

    u["cash"]-=amount

    icons=[
        "🍒","🍋","⭐",
        "🔔","💎"
    ]

    a,b,c=[
        random.choice(icons)
        for _ in range(3)
    ]

    msg=await ctx.send(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        "🔵 **【 ○ 】 【 ○ 】 【 ○ 】**",
        0xF39C12
    ))

    await asyncio.sleep(.5)

    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        f"🔵 **【 {a} 】 【 ○ 】 【 ○ 】**",
        0xF39C12
    ))

    await asyncio.sleep(.5)

    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        f"🔵 **【 {a} 】 【 {b} 】 【 ○ 】**",
        0xF39C12
    ))

    await asyncio.sleep(.5)

    if a==b==c:

        win=amount*5
        u["cash"]+=win

        result=(
            "🟢 **JACKPOT x5!**\n"
            f"💰 +{fm(win)}"
        )

        color=0x2ECC71

    elif len({a,b,c})<3:

        win=amount*2
        u["cash"]+=win

        result=(
            "🟢 **2 HÌNH GIỐNG NHAU x2!**\n"
            f"💰 +{fm(win)}"
        )

        color=0x2ECC71

    else:

        result=(
            "🔴 **THUA!**\n"
            f"💸 -{fm(amount)}"
        )

        color=0xE74C3C

    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        f"🔵 **【 {a} 】 【 {b} 】 【 {c} 】**\n\n"
        f"{result}",
        color
    ))

# ================= BẦU CUA =================

@bot.command()
async def bc(ctx,choice:str=None,amount:int=None):

    if block(ctx):
        return

    icons={
        "ca":"🐟",
        "tom":"🦐",
        "cua":"🦀",
        "bau":"🥒",
        "ga":"🐓",
        "nai":"🦌"
    }

    if choice not in icons or not amount or amount<1:
        return await ctx.send(
            "❌ `!bc ca/tom/cua/bau/ga/nai số_tiền`"
        )

    u=U(ctx.author)

    if amount>u["cash"]:
        return await ctx.send(
            "❌ Không đủ tiền."
        )

    u["cash"]-=amount

    r=[
        random.choice(list(icons))
        for _ in range(3)
    ]

    msg=await ctx.send(embed=E(
        "🎲 BẦU CUA",
        "🔵 **◯   ◯   ◯**",
        0xF39C12
    ))

    await asyncio.sleep(.7)

    board="  ".join(
        f"【 {icons[x]} 】"
        for x in r
    )

    n=r.count(choice)

    if n:

        win=amount*(n+1)
        u["cash"]+=win

        text=(
            f"{board}\n\n"
            f"🟢 **TRÚNG {n} CON! x{n+1}**\n"
            f"💰 +{fm(win)}"
        )

        color=0x2ECC71

    else:

        text=(
            f"{board}\n\n"
            "🔴 **THUA!**\n"
            f"💸 -{fm(amount)}"
        )

        color=0xE74C3C

    await msg.edit(
        embed=E(
            "🎲 BẦU CUA",
            text,
            color
        )
    )

# ================= XÓC ĐĨA =================

@bot.command()
async def xd(ctx,choice:str=None,amount:int=None):

    if block(ctx):
        return

    if choice not in ("chan","le") \
       or not amount or amount<1:

        return await ctx.send(
            "❌ `!xd chan 100` hoặc "
            "`!xd le 100`"
        )

    u=U(ctx.author)

    if amount>u["cash"]:
        return await ctx.send(
            "❌ Bạn không đủ tiền."
        )

    u["cash"]-=amount

    # Màn hình xóc
    msg=await ctx.send(embed=E(
        "🪙 XÓC ĐĨA",
        "🥣 **Xóc... Xóc... Xóc...**",
        0xF39C12
    ))

    await asyncio.sleep(1.5)

    # 4 viên
    balls=[
        random.randint(0,1)
        for _ in range(4)
    ]

    red=balls.count(1)

    # Chẵn / lẻ
    if red%2==0:
        result="CHAN"
        result_key="chan"
    else:
        result="LE"
        result_key="le"

    # Bảng giống ảnh
    board="  ".join(
        "🔴" if x else "⚪"
        for x in balls
    )

    # THẮNG
    if choice==result_key:

        win=amount*2
        u["cash"]+=win

        text=(
            f"{board}\n\n"
            f"🎯 Kết quả: **{result}**\n"
            f"🔴 Số đỏ: **{red}**\n\n"
            "🟢 **THẮNG x2!**\n"
            f"💰 Nhận **{fm(win)}**"
        )

        color=0x2ECC71

    # THUA
    else:

        text=(
            f"{board}\n\n"
            f"🎯 Kết quả: **{result}**\n"
            f"🔴 Số đỏ: **{red}**\n\n"
            "🔴 **THUA!**\n"
            f"💸 Mất **{fm(amount)}**"
        )

        color=0xE74C3C

    await msg.edit(
        embed=E(
            "🪙 XÓC ĐĨA",
            text,
            color
        )
    )

# ================= TÀI XỈU =================

@bot.command()
async def tx(ctx,choice:str=None,amount:int=None):

    if block(ctx):
        return

    if choice not in ("tai","xiu") or not amount:
        return await ctx.send(
            "❌ `!tx tai 100` hoặc `!tx xiu 100`"
        )

    if amount<100 or amount>10000000:
        return await ctx.send(
            "❌ Cược không hợp lệ."
        )

    u=U(ctx.author)

    if amount>u["cash"]:
        return await ctx.send(
            "❌ Không đủ tiền."
        )

    u["cash"]-=amount

    msg=await ctx.send(embed=E(
        "🎲 TÀI XỈU",
        "🔵 **◯   ◯   ◯**\n\n"
        "⏳ Đang lắc...",
        0xF39C12
    ))

    await asyncio.sleep(1.5)

    d=[
        random.randint(1,6)
        for _ in range(3)
    ]

    total=sum(d)

    result=(
        "tai"
        if total>=11
        else "xiu"
    )

    if choice==result:

        win=amount*2
        u["cash"]+=win

        text=(
            f"🎲 **{d[0]} {d[1]} {d[2]}**\n"
            f"🎯 **{total} → {result.upper()}**\n"
            f"🟢 +{fm(win)}"
        )

        color=0x2ECC71

    else:

        text=(
            f"🎲 **{d[0]} {d[1]} {d[2]}**\n"
            f"🎯 **{total} → {result.upper()}**\n"
            f"🔴 -{fm(amount)}"
        )

        color=0xE74C3C

    await msg.edit(
        embed=E(
            "🎲 KẾT QUẢ TÀI XỈU",
            text,
            color
        )
    )

# ================= CODE ADMIN =================

@bot.command()
async def taocode(ctx,amount:int=None,uses:int=None):

    if not adm(ctx):
        return await ctx.send(
            "⛔ Chỉ Admin."
        )

    if not amount or not uses:
        return await ctx.send(
            "❌ `!taocode tiền lượt`"
        )

    code="CASINO"+str(
        random.randint(100000,999999)
    )

    codes[code]=[amount,uses]

    try:
        await ctx.author.send(
            "🎟️ **CODE ADMIN**\n\n"
            f"🔑 `{code}`\n"
            f"💰 {fm(amount)}\n"
            f"🎫 {uses} lượt"
        )

        await ctx.send(
            "✅ Code đã được gửi riêng vào DM."
        )

    except:
        await ctx.send(
            f"⚠️ Không gửi DM được: `{code}`"
        )

# ================= THƯỞNG CODE =================

@bot.command()
async def thuongcode(ctx,amount:int=None,uses:int=None):

    if not adm(ctx):
        return await ctx.send(
            "⛔ Chỉ Admin."
        )

    if not amount or not uses:
        return await ctx.send(
            "❌ `!thuongcode tiền lượt`"
        )

    code="THUONG"+str(
        random.randint(100000,999999)
    )

    codes[code]=[amount,uses]

    await ctx.send(embed=E(
        "🎁 🎟️ THƯỞNG CODE",
        f"🔑 **CODE:** `{code}`\n"
        f"💰 **Tiền:** `{fm(amount)}`\n"
        f"🎫 **Lượt nhập:** `{uses}`\n\n"
        f"📌 Nhập: `!nhapcode {code}`",
        0x3498DB
    ))

# ================= NHẬP CODE =================

@bot.command()
async def nhapcode(ctx,code:str=None):

    if not code:
        return await ctx.send(
            "❌ Nhập code."
        )

    code=code.upper()

    if code not in codes:
        return await ctx.send(
            "❌ Code không tồn tại."
        )

    amount,uses=codes[code]

    if uses<=0:
        return await ctx.send(
            "❌ Code hết lượt."
        )

    U(ctx.author)["cash"]+=amount

    codes[code][1]-=1

    await ctx.send(embed=E(
        "🎟️ NHẬP CODE THÀNH CÔNG",
        f"💰 Nhận **{fm(amount)}**\n"
        f"🎫 Còn **{uses-1} lượt**",
        0x2ECC71
    ))

# ================= ADMIN TIỀN =================

@bot.command()
async def settien(ctx,m:discord.Member=None,amount:int=None):

    if not adm(ctx):
        return await ctx.send(
            "⛔ Chỉ Admin."
        )

    if not m or amount is None:
        return await ctx.send(
            "❌ `!settien @user tiền`"
        )

    U(m)["cash"]=max(0,amount)

    await ctx.send(
        f"🛡️ Đã set tiền {m.mention} "
        f"→ **{fm(amount)}**."
    )

@bot.command()
async def reset(ctx,what:str=None,m:discord.Member=None):

    if not adm(ctx):
        return await ctx.send(
            "⛔ Chỉ Admin."
        )

    if what!="tien" or not m:
        return await ctx.send(
            "❌ `!reset tien @user`"
        )

    U(m)["cash"]=START
    U(m)["bank"]=0

    await ctx.send(
        f"♻️ {m.mention} đã reset "
        f"về **{fm(START)}**."
    )

# ================= KICK =================

@bot.command()
async def kick(ctx,m:discord.Member=None):

    if not adm(ctx):
        return await ctx.send(
            "⛔ Chỉ Admin."
        )

    if not m:
        return await ctx.send(
            "❌ `!kick @user`"
        )

    await m.kick()

    await ctx.send(
        f"👢 Đã kick {m.mention}."
    )

# ================= BAN =================

@bot.command()
async def ban(ctx,m:discord.Member=None):

    if not adm(ctx):
        return await ctx.send(
            "⛔ Chỉ Admin."
        )

    if not m:
        return await ctx.send(
            "❌ `!ban @user`"
        )

    await m.ban()

    await ctx.send(
        f"🔨 Đã ban {m.mention}."
    )

# ================= KHÓA =================

@bot.command()
async def khoamom(ctx,m:discord.Member=None):

    if not adm(ctx):
        return await ctx.send(
            "⛔ Chỉ Admin."
        )

    if not m:
        return await ctx.send(
            "❌ `!khoamom @user`"
        )

    u=U(m)
    u["muted"]=True

    await ctx.send(embed=E(
        "🔇 ĐÃ KHÓA",
        f"👤 {m.mention}\n\n"
        "❌ Không được chơi bot.\n"
        "❌ Không được dùng lệnh bot.\n\n"
        f"🔓 Dùng `!unkhoamom {m.mention}` "
        "để mở lại.",
        0xE74C3C
    ))

# ================= MỞ KHÓA =================

@bot.command()
async def unkhoamom(ctx,m:discord.Member=None):

    if not adm(ctx):
        return await ctx.send(
            "⛔ Chỉ Admin."
        )

    if not m:
        return await ctx.send(
            "❌ `!unkhoamom @user`"
        )

    u=U(m)
    u["muted"]=False

    await ctx.send(embed=E(
        "🔊 ĐÃ MỞ KHÓA",
        f"👤 {m.mention}\n\n"
        "🟢 Đã được chơi lại.\n"
        "🟢 Đã dùng bot lại.\n"
        "🟢 Đã nói chuyện bình thường.",
        0x2ECC71
    ))

# ================= LỖI =================

@bot.event
async def on_command_error(ctx,error):

    if isinstance(
        error,
        commands.CommandNotFound
    ):
        return

    if isinstance(
        error,
        commands.CommandOnCooldown
    ):
        return

    if isinstance(
        error,
        commands.MissingRequiredArgument
    ):
        return await ctx.send(
            "❌ Thiếu thông tin. "
            "Gõ `!trogiup`."
        )

    if isinstance(
        error,
        commands.BadArgument
    ):
        return await ctx.send(
            "❌ Sai cú pháp."
        )

    print("ERROR:",error)

# ================= START BOT =================

if not TOKEN:

    print(
        "❌ KHÔNG TÌM THẤY TOKEN_BOT!"
    )

else:

    print("🚀 Đang khởi động bot...")

    bot.run(TOKEN)
