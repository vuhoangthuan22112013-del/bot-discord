import os, random, asyncio, time, discord
from discord.ext import commands
from collections import defaultdict

TOKEN = os.getenv("TOKEN_BOT")
OWNER_ID = truong456xza_04617
START = 2000
PREFIX = "!"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX,intents=intents,help_command=None)

users={}
codes={}
spam=defaultdict(list)
TX={"on":False,"bets":{}}

def U(m):
    if m.id not in users:
        users[m.id]={"cash":START,"bank":0,"role":"Không có",
                     "loan":0,"due":0,"daily":0,"muted":False}
    return users[m.id]

def money(n):
    return f"{n:,}$"

def E(title,text="",color=0x3498DB):
    return discord.Embed(title=title,description=text,color=color)

def isadmin(ctx):
    return ctx.author.id==OWNER_ID

def blocked(ctx):
    u=U(ctx.author)
    if u["muted"]:
        return True
    if u["loan"] and time.time()>u["due"]:
        asyncio.create_task(ctx.send(
            "🔴 **CON NỢ!** Hãy dùng `!trano số_tiền`."
        ))
        return True
    return False

async def spamcheck(ctx):
    now=time.time()
    a=spam[ctx.author.id]
    a[:]=[x for x in a if now-x<5]
    if len(a)>=5:
        try:
            await ctx.send("🛑 Bạn đang thao tác quá nhanh! Chờ một chút.")
        except:
            pass
        return False
    a.append(now)
    return True

@bot.check
async def global_check(ctx):
    return await spamcheck(ctx)

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

@bot.command()
async def trogiup(ctx):
    t=(
        "## 🎰 GAME\n"
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
        "`!taocode tiền lượt`\n"
        "`!thuongcode tiền lượt`\n"
        "`!settien @user tiền`\n"
        "`!kick @user` • `!ban @user`\n"
        "`!khoamom @user`\n"
        "`!reset tien @user`"
    )
    await ctx.send(embed=E("🎰 CASINO BET88",t))

@bot.command()
async def vi(ctx,m:discord.Member=None):
    m=m or ctx.author
    u=U(m)
    await ctx.send(embed=E(
        f"💳 VÍ CỦA {m.display_name}",
        f"💵 **Tiền mặt:** `{money(u['cash'])}`\n"
        f"🏦 **Ngân hàng:** `{money(u['bank'])}`\n"
        f"👑 **Role:** `{u['role']}`\n"
        f"💸 **Khoản vay:** `{money(u['loan'])}`"
    ))

@bot.command()
async def gui(ctx,amount:int=None):
    if not amount or amount<1:
        return await ctx.send("❌ `!gui số_tiền`")
    u=U(ctx.author)
    if amount>u["cash"]:
        return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=amount
    u["bank"]+=amount
    await ctx.send(embed=E(
        "🏦 NGÂN HÀNG",
        f"Đã gửi **{money(amount)}**.",
        0x2ECC71))

@bot.command()
async def rut(ctx,amount:int=None):
    if not amount or amount<1:
        return await ctx.send("❌ `!rut số_tiền`")
    u=U(ctx.author)
    if amount>u["bank"]:
        return await ctx.send("❌ Ngân hàng không đủ tiền.")
    u["bank"]-=amount
    u["cash"]+=amount
    await ctx.send(embed=E(
        "💵 RÚT TIỀN",
        f"Đã rút **{money(amount)}**.",
        0x2ECC71))

@bot.command()
async def chuyen(ctx,m:discord.Member=None,amount:int=None):
    if not m or not amount:
        return await ctx.send("❌ `!chuyen @user số_tiền`")
    if amount<1 or amount>10000000:
        return await ctx.send("❌ Tối đa 10.000.000$.")
    if m.id==ctx.author.id:
        return await ctx.send("❌ Không thể chuyển cho chính mình.")
    a,b=U(ctx.author),U(m)
    if a["cash"]<amount:
        return await ctx.send("❌ Không đủ tiền.")
    a["cash"]-=amount
    b["cash"]+=amount
    await ctx.send(embed=E(
        "💸 CHUYỂN TIỀN",
        f"{ctx.author.mention} → {m.mention}\n"
        f"💰 **{money(amount)}**",
        0x2ECC71))

@bot.command()
async def diemdanh(ctx):
    u=U(ctx.author)
    today=time.strftime("%Y-%m-%d")
    if u["daily"]==today:
        return await ctx.send("⏰ Hôm nay bạn đã điểm danh.")
    n=random.randint(1000,3000)
    u["cash"]+=n
    u["daily"]=today
    await ctx.send(embed=E(
        "🎁 ĐIỂM DANH",
        f"💰 Nhận **{money(n)}**\n"
        f"💵 Số dư: **{money(u['cash'])}**",
        0x2ECC71))

@bot.command()
async def bxh(ctx):
    arr=sorted(
        users.items(),
        key=lambda x:x[1]["cash"]+x[1]["bank"],
        reverse=True
    )[:10]
    text=""
    for i,(uid,u) in enumerate(arr,1):
        m=ctx.guild.get_member(uid)
        n=m.display_name if m else str(uid)
        total=u["cash"]+u["bank"]
        text+=f"**{i}.** {n} — `{money(total)}`\n"
    await ctx.send(embed=E(
        "🏆 TOP GIÀU NHẤT",
        text or "Chưa có dữ liệu.",
        0xF1C40F))

@bot.command()
async def vay(ctx,amount:int=None):
    if not amount or amount<1000 or amount>50000:
        return await ctx.send("❌ Vay từ 1.000$ đến 50.000$.")
    u=U(ctx.author)
    if u["loan"]:
        return await ctx.send("❌ Bạn đang có khoản vay.")
    u["loan"]=amount
    u["cash"]+=amount
    u["due"]=time.time()+3600
    await ctx.send(embed=E(
        "💸 VAY TIỀN",
        f"💰 Vay: **{money(amount)}**\n"
        "⏰ Thời hạn: **1 giờ**\n"
        f"Trả: `!trano {amount}`",
        0xF39C12))

@bot.command()
async def trano(ctx,amount:int=None):
    u=U(ctx.author)
    if not u["loan"]:
        return await ctx.send("❌ Bạn không có khoản vay.")
    if amount!=u["loan"]:
        return await ctx.send(
            f"❌ Phải trả **{money(u['loan'])}**.")
    if u["cash"]<amount:
        return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=amount
    u["loan"]=0
    u["due"]=0
    await ctx.send(embed=E(
        "✅ ĐÃ TRẢ NỢ",
        f"Đã trả **{money(amount)}**.\n"
        "🟢 Bạn được chơi lại!",
        0x2ECC71))

@bot.command()
async def quay(ctx,amount:int=None):
    if blocked(ctx):
        return
    if not amount or amount<1:
        return await ctx.send("❌ `!quay số_tiền`")
    u=U(ctx.author)
    if amount>u["cash"]:
        return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=amount
    s=["🍒","🍋","⭐","🔔","💎"]
    a,b,c=random.choices(s,k=3)

    msg=await ctx.send(embed=E(
        "🎰 777 SLOT",
        "⚪ **[ ❓ ] [ ❓ ] [ ❓ ]**",
        0xF39C12))

    await asyncio.sleep(.5)
    await msg.edit(embed=E(
        "🎰 777 SLOT",
        f"⚪ **[ {a} ] [ ❓ ] [ ❓ ]**",
        0xF39C12))

    await asyncio.sleep(.5)
    await msg.edit(embed=E(
        "🎰 777 SLOT",
        f"⚪ **[ {a} ] [ {b} ] [ ❓ ]**",
        0xF39C12))

    await asyncio.sleep(.5)

    if a==b==c:
        win=amount*5
        u["cash"]+=win
        result=f"🟢 **THẮNG JACKPOT x5!**\n💰 Nhận **{money(win)}**"
        col=0x2ECC71
    elif a==b or a==c or b==c:
        win=amount*3//2
        u["cash"]+=win
        result=f"🟢 **THẮNG x1.5!**\n💰 Nhận **{money(win)}**"
        col=0x2ECC71
    else:
        result=f"🔴 **THUA!**\n💸 Mất **{money(amount)}**"
        col=0xE74C3C

    await msg.edit(embed=E(
        "🎰 777 SLOT",
        f"⚪ **[ {a} ] [ {b} ] [ {c} ]**\n\n{result}",
        col))

@bot.command()
async def xd(ctx,choice:str=None,amount:int=None):
    if blocked(ctx):
        return
    if choice not in ["chan","le"] or not amount or amount<1:
        return await ctx.send(
            "❌ `!xd chan 100` hoặc `!xd le 100`")

    u=U(ctx.author)
    if amount>u["cash"]:
        return await ctx.send("❌ Bạn không đủ tiền.")

    u["cash"]-=amount

    msg=await ctx.send(embed=E(
        "🪙 XÓC ĐĨA",
        "🥣 **Xóc... Xóc... Xóc...**",
        0xF39C12))

    await asyncio.sleep(1.5)

    balls=[random.randint(0,1) for _ in range(4)]
    n=sum(balls)
    result="chan" if n%2==0 else "le"

    board=" ".join(
        "🔴" if x else "⚪"
        for x in balls
    )

    if choice==result:
        win=amount*2
        u["cash"]+=win
        result_text=(
            f"🎯 **Kết quả: {result.upper()}**\n"
            f"🔴 **Số đỏ: {n}**\n\n"
            f"🟢 **THẮNG x2!**\n"
            f"💰 Nhận **{money(win)}**"
        )
        col=0x2ECC71
    else:
        result_text=(
            f"🎯 **Kết quả: {result.upper()}**\n"
            f"🔴 **Số đỏ: {n}**\n\n"
            f"🔴 **THUA!**\n"
            f"💸 Mất **{money(amount)}**"
        )
        col=0xE74C3C

    await msg.edit(embed=E(
        "🪙 XÓC ĐĨA",
        f"{board}\n\n{result_text}",
        col))

@bot.command()
async def bc(ctx,choice:str=None,amount:int=None):
    if blocked(ctx):
        return

    icons={
        "ca":"🐟","tom":"🦐","cua":"🦀",
        "bau":"🥒","ga":"🐓","nai":"🦌"
    }

    if choice not in icons or not amount or amount<1:
        return await ctx.send(
            "❌ `!bc ca/tom/cua/bau/ga/nai số_tiền`")

    u=U(ctx.author)

    if amount>u["cash"]:
        return await ctx.send("❌ Không đủ tiền.")

    u["cash"]-=amount

    msg=await ctx.send(embed=E(
        "🎲 BẦU CUA",
        "🔵 **Đang lắc...**\n\n"
        "⚪  ⚪  ⚪",
        0xF39C12))

    await asyncio.sleep(1)

    r=random.choices(list(icons),k=3)
    board="  ".join(icons[x] for x in r)
    count=r.count(choice)

    if count:
        win=amount*(count+1)
        u["cash"]+=win
        text=(
            f"{board}\n\n"
            f"🟢 **TRÚNG {count} CON! x{count+1}**\n"
            f"💰 Nhận **{money(win)}**"
        )
        col=0x2ECC71
    else:
        text=(
            f"{board}\n\n"
            "🔴 **THUA!**\n"
            f"💸 Mất **{money(amount)}**"
        )
        col=0xE74C3C

    await msg.edit(embed=E("🎲 BẦU CUA",text,col))

@bot.command()
async def tx(ctx,choice:str=None,amount:int=None):
    if blocked(ctx):
        return

    if choice not in ["tai","xiu"]:
        return await ctx.send(
            "❌ `!tx tai 100` hoặc `!tx xiu 100`")

    if not amount or amount<100:
        return await ctx.send("❌ Cược tối thiểu 100$.")

    u=U(ctx.author)

    if amount>u["cash"]:
        return await ctx.send("❌ Không đủ tiền.")

    if not TX["on"]:
        TX["on"]=True
        TX["bets"]={}
        u["cash"]-=amount
        TX["bets"][ctx.author.id]=(choice,amount)

        msg=await ctx.send(embed=E(
            "🎲 TÀI XỈU",
            "🔵 **ĐANG NHẬN CƯỢC**\n\n"
            "⚪ Còn **30 giây**\n"
            f"👥 **1 người**",
            0xF39C12))

        for left in [20,10]:
            await asyncio.sleep(10)
            if not TX["on"]:
                return
            await msg.edit(embed=E(
                "🎲 TÀI XỈU",
                "🔵 **ĐANG NHẬN CƯỢC**\n\n"
                f"⚪ Còn **{left} giây**\n"
                f"👥 **{len(TX['bets'])} người**",
                0xF39C12))

        await asyncio.sleep(10)

        if not TX["on"]:
            return

        TX["on"]=False

        d=[random.randint(1,6) for _ in range(3)]
        total=sum(d)
        result="tai" if total>=11 else "xiu"

        text=(
            f"🎲 **{d[0]}  {d[1]}  {d[2]}**\n\n"
            f"🎯 **{total} điểm → {result.upper()}**\n\n"
        )

        for uid,(ch,bet) in TX["bets"].items():
            pl=users.get(uid)
            if not pl:
                continue

            if ch==result:
                win=bet*2
                pl["cash"]+=win
                text+=f"🟢 <@{uid}> +{money(win)}\n"
            else:
                text+=f"🔴 <@{uid}> -{money(bet)}\n"

        TX["bets"]={}

        await msg.edit(embed=E(
            "🎲 KẾT QUẢ TÀI XỈU",
            text,
            0x2ECC71))
        return

    if ctx.author.id in TX["bets"]:
        return await ctx.send("❌ Bạn đã cược rồi.")

    u["cash"]-=amount
    TX["bets"][ctx.author.id]=(choice,amount)

    await ctx.send(embed=E(
        "🎯 ĐẶT CƯỢC",
        f"{ctx.author.mention}\n"
        f"Cược **{money(amount)}** vào **{choice.upper()}**.",
        0xF39C12))

@bot.command()
async def taocode(ctx,amount:int=None,uses:int=None):
    if not isadmin(ctx):
        return await ctx.send("⛔ Bạn không có quyền Admin.")

    if not amount or not uses or amount<1 or uses<1:
        return await ctx.send("❌ `!taocode tiền lượt`")

    code="CASINO"+str(random.randint(100000,999999))
    while code in codes:
        code="CASINO"+str(random.randint(100000,999999))

    codes[code]={
        "money":amount,
        "uses":uses,
        "used":set()
    }

    try:
        await ctx.author.send(embed=E(
            "🎟️ CODE ADMIN",
            f"🔑 **Code:** `{code}`\n"
            f"💰 **Tiền:** `{money(amount)}`\n"
            f"🎫 **Lượt:** `{uses}`",
            0x3498DB))
        await ctx.send("✅ Code đã gửi vào DM của bạn.")
    except discord.Forbidden:
        await ctx.send(
            f"❌ Không gửi DM được.\nCode: `{code}`")

@bot.command()
async def thuongcode(ctx,amount:int=None,uses:int=None):
    if not isadmin(ctx):
        return await ctx.send("⛔ Bạn không có quyền Admin.")

    if not amount or not uses or amount<1 or uses<1:
        return await ctx.send("❌ `!thuongcode tiền lượt`")

    code="THUONG"+str(random.randint(100000,999999))
    while code in codes:
        code="THUONG"+str(random.randint(100000,999999))

    codes[code]={
        "money":amount,
        "uses":uses,
        "used":set()
    }

    await ctx.send(embed=E(
        "🎁 CODE THƯỞNG",
        f"🔑 **CODE:** `{code}`\n"
        f"💰 **Tiền thưởng:** `{money(amount)}`\n"
        f"🎫 **Lượt nhập:** `{uses}`\n\n"
        f"📌 Nhập: `!nhapcode {code}`",
        0x3498DB))

@bot.command()
async def nhapcode(ctx,code:str=None):
    if not code:
        return await ctx.send("❌ `!nhapcode CODE`")

    code=code.upper()

    if code not in codes:
        return await ctx.send("❌ Code không tồn tại.")

    c=codes[code]
    uid=ctx.author.id

    if uid in c["used"]:
        return await ctx.send("❌ Bạn đã dùng code này.")

    if c["uses"]<=0:
        return await ctx.send("❌ Code đã hết lượt.")

    c["used"].add(uid)
    c["uses"]-=1
    U(ctx.author)["cash"]+=c["money"]

    await ctx.send(embed=E(
        "🎟️ NHẬP CODE THÀNH CÔNG",
        f"💰 Nhận **{money(c['money'])}**\n"
        f"🎫 Còn **{c['uses']} lượt**",
        0x2ECC71))

@bot.command()
async def settien(ctx,m:discord.Member=None,amount:int=None):
    if not isadmin(ctx):
        return await ctx.send("⛔ Bạn không có quyền Admin.")

    if not m or amount is None:
        return await ctx.send("❌ `!settien @user tiền`")

    if amount<0:
        return await ctx.send("❌ Số tiền không hợp lệ.")

    U(m)["cash"]=amount

    await ctx.send(embed=E(
        "🛡️ SET TIỀN",
        f"{m.mention} → **{money(amount)}**",
        0x3498DB))

@bot.command()
async def reset(ctx,what:str=None,m:discord.Member=None):
    if not isadmin(ctx):
        return await ctx.send("⛔ Bạn không có quyền Admin.")

    if what!="tien" or not m:
        return await ctx.send("❌ `!reset tien @user`")

    U(m)["cash"]=START
    U(m)["bank"]=0

    await ctx.send(
        f"♻️ Đã reset {m.mention} về **{money(START)}**.")

@bot.command()
async def kick(ctx,m:discord.Member=None):
    if not isadmin(ctx):
        return await ctx.send("⛔ Bạn không có quyền Admin.")

    if not m:
        return await ctx.send("❌ `!kick @user`")

    try:
        await m.kick(reason="Casino Admin")
        await ctx.send(f"👢 Đã kick {m.mention}.")
    except discord.Forbidden:
        await ctx.send("❌ Bot không đủ quyền.")

@bot.command()
async def ban(ctx,m:discord.Member=None):
    if not isadmin(ctx):
        return await ctx.send("⛔ Bạn không có quyền Admin.")

    if not m:
        return await ctx.send("❌ `!ban @user`")

    try:
        await m.ban(reason="Casino Admin")
        await ctx.send(f"🔨 Đã ban {m.mention}.")
    except discord.Forbidden:
        await ctx.send("❌ Bot không đủ quyền.")

@bot.command()
async def khoamom(ctx,m:discord.Member=None):
    if not isadmin(ctx):
        return await ctx.send("⛔ Bạn không có quyền Admin.")

    if not m:
        return await ctx.send("❌ `!khoamom @user`")

    u=U(m)
    u["muted"]=not u["muted"]

    await ctx.send(
        f"🔇 {m.mention} đã "
        f"{'bị khóa mõm.' if u['muted'] else 'được mở khóa.'}")

@bot.command()
async def cuahang(ctx):
    await ctx.send(embed=E(
        "🛒 CỬA HÀNG",
        "💛 **VIP** — 10.000.000$\n"
        "`!muan vip`\n\n"
        "💙 **ĐẠI GIA** — 5.000.000$\n"
        "`!muan daigia`\n\n"
        "💜 **TỶ PHÚ** — 1.000.000.000$\n"
        "`!muan typhu`",
        0xF1C40F))

@bot.command()
async def muan(ctx,name:str=None):
    prices={
        "vip":10000000,
        "daigia":5000000,
        "typhu":1000000000
    }

    names={
        "vip":"VIP",
        "daigia":"Đại Gia",
        "typhu":"Tỷ Phú"
    }

    if name not in prices:
        return await ctx.send(
            "❌ `!muan vip/daigia/typhu`")

    u=U(ctx.author)
    p=prices[name]

    if u["cash"]<p:
        return await ctx.send("❌ Không đủ tiền.")

    role=discord.utils.get(
        ctx.guild.roles,
        name=names[name]
    )

    if not role:
        return await ctx.send(
            f"❌ Server chưa có role **{names[name]}**.")

    if role>=ctx.guild.me.top_role:
        return await ctx.send(
            "❌ Role này cao hơn role của bot.")

    try:
        await ctx.author.add_roles(role)
    except discord.Forbidden:
        return await ctx.send(
            "❌ Bot không có quyền cấp role.")

    u["cash"]-=p
    u["role"]=names[name]

    await ctx.send(embed=E(
        "👑 MUA ROLE THÀNH CÔNG",
        f"{ctx.author.mention}\n"
        f"👑 **{names[name]}**\n"
        f"💰 Giá: **{money(p)}**",
        0x2ECC71))

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error,commands.CommandNotFound):
        return

    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(
            "❌ Thiếu thông tin. Gõ `!trogiup`.")

    elif isinstance(error,commands.BadArgument):
        await ctx.send(
            "❌ Sai cú pháp. Gõ `!trogiup`.")

    elif isinstance(error,commands.CheckFailure):
        return

    else:
        print("ERROR:",repr(error))

if not TOKEN:
    print("❌ Không tìm thấy biến TOKEN_BOT!")
else:
    try:
        bot.run(TOKEN)
    except Exception as e:
        print("❌ BOT ERROR:",e)
