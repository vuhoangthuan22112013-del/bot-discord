import os,random,asyncio,time,discord
from discord.ext import commands

TOKEN=os.getenv("TOKEN_BOT")
START=2000
users={}
codes={}
spam={}
TX={"on":False,"bets":{}}

intents=discord.Intents.all()
bot=commands.Bot(command_prefix="!",intents=intents,help_command=None)

def U(m):
    if m.id not in users:
        users[m.id]={"cash":START,"bank":0,"role":"Không có","loan":0,
        "due":0,"daily":0,"muted":False}
    return users[m.id]

def money(n): return f"{n:,}$"

def E(t,d="",c=0x3498DB):
    return discord.Embed(title=t,description=d,color=c)

def adm(ctx): return ctx.author.guild_permissions.administrator

def blocked(ctx):
    u=U(ctx.author)
    if u["muted"]:
        return True
    if u["loan"] and time.time()>u["due"]:
        asyncio.create_task(ctx.send(
            "🔴 **CON NỢ!** Bạn không được chơi.\n"
            "Dùng `!trano số_tiền` để trả nợ."
        ))
        return True
    return False

# ================= SPAM =================

@bot.check
async def anti_spam(ctx):
    if ctx.author.guild_permissions.administrator:
        return True
    now=time.time()
    old=spam.get(ctx.author.id,0)
    if now-old<1:
        return False
    spam[ctx.author.id]=now
    return True

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error,commands.CommandOnCooldown):
        return
    if isinstance(error,commands.CheckFailure):
        return
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send("❌ Thiếu thông tin. Gõ `!trogiup`.")
    elif isinstance(error,commands.BadArgument):
        await ctx.send("❌ Sai cú pháp.")

# ================= READY =================

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino")
    )
    print("BOT ONLINE:",bot.user)

# ================= HELP =================

@bot.command(name="trogiup")
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
        "## 🎟️ CODE\n"
        "`!nhapcode CODE`\n\n"
        "## 🛒 SHOP\n"
        "`!cuahang` • `!muan vip`\n"
        "`!muan daigia` • `!muan typhu`"
    )
    if adm(ctx):
        t+=(
            "\n\n## 🛡️ ADMIN\n"
            "`!taocode tiền lượt`\n"
            "`!thuongcode tiền lượt`\n"
            "`!settien @user tiền`\n"
            "`!kick @user` • `!ban @user`\n"
            "`!khoamom @user`\n"
            "`!reset tien @user`"
        )
    await ctx.send(embed=E("🎰 CASINO BET88",t))

# ================= VI =================

@bot.command()
async def vi(ctx,m:discord.Member=None):
    m=m or ctx.author
    u=U(m)
    status="CON NỢ" if u["loan"] and time.time()>u["due"] else "Bình thường"
    await ctx.send(embed=E(
        f"💳 VÍ CỦA {m.display_name}",
        f"💵 **Tiền mặt:** `{money(u['cash'])}`\n"
        f"🏦 **Ngân hàng:** `{money(u['bank'])}`\n"
        f"👑 **Role:** `{u['role']}`\n"
        f"💸 **Vay:** `{money(u['loan'])}`\n"
        f"📌 **Trạng thái:** `{status}`"
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
        f"🟢 Đã gửi **{money(amount)}**.",
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
        f"🟢 Đã rút **{money(amount)}**.",
        0x2ECC71))

@bot.command()
async def chuyen(ctx,m:discord.Member=None,amount:int=None):
    if not m or not amount:
        return await ctx.send("❌ `!chuyen @user số_tiền`")
    if not 1<=amount<=10_000_000:
        return await ctx.send("❌ Từ 1$ đến 10.000.000$.")
    if m.id==ctx.author.id:
        return await ctx.send("❌ Không thể chuyển cho chính mình.")
    a,b=U(ctx.author),U(m)
    if a["cash"]<amount:
        return await ctx.send("❌ Không đủ tiền.")
    a["cash"]-=amount
    b["cash"]+=amount
    await ctx.send(embed=E(
        "💸 CHUYỂN TIỀN",
        f"{ctx.author.mention} ➜ {m.mention}\n"
        f"💰 **{money(amount)}**",0x2ECC71))

# ================= VAY =================

@bot.command()
async def vay(ctx,amount:int=None):
    if not amount or not 1000<=amount<=50000:
        return await ctx.send("❌ Vay từ **1.000$ - 50.000$**.")
    u=U(ctx.author)
    if u["loan"]:
        return await ctx.send("❌ Bạn đang có khoản vay.")
    u["loan"]=amount
    u["cash"]+=amount
    u["due"]=time.time()+3600
    await ctx.send(embed=E(
        "💳 VAY TIỀN",
        f"🟢 Đã vay **{money(amount)}**.\n"
        "⏰ Thời hạn: **1 giờ**\n"
        "🔴 Quá hạn sẽ thành **CON NỢ**.\n"
        "🚫 Không được chơi cho đến khi trả nợ.\n\n"
        f"`!trano {amount}`",
        0xF39C12))

@bot.command()
async def trano(ctx,amount:int=None):
    u=U(ctx.author)
    if not u["loan"]:
        return await ctx.send("❌ Bạn không có khoản vay.")
    if amount!=u["loan"]:
        return await ctx.send(f"❌ Trả đúng **{money(u['loan'])}**.")
    if u["cash"]<amount:
        return await ctx.send("❌ Không đủ tiền trả.")
    u["cash"]-=amount
    u["loan"]=0
    u["due"]=0
    await ctx.send(embed=E(
        "✅ ĐÃ TRẢ NỢ",
        f"{ctx.author.mention} đã trả **{money(amount)}**.\n"
        "🟢 Đã được phép chơi lại!",
        0x2ECC71))

# ================= DAILY =================

@bot.command()
async def diemdanh(ctx):
    u=U(ctx.author)
    day=time.strftime("%Y-%m-%d")
    if u["daily"]==day:
        return await ctx.send("❌ Hôm nay đã điểm danh.")
    n=random.randint(1000,3000)
    u["cash"]+=n
    u["daily"]=day
    await ctx.send(embed=E(
        "🎁 ĐIỂM DANH",
        f"💰 Nhận **{money(n)}**\n"
        f"💵 Số dư: **{money(u['cash'])}**",
        0x2ECC71))

# ================= BXH =================

@bot.command()
async def bxh(ctx):
    arr=sorted(
        users.items(),
        key=lambda x:x[1]["cash"]+x[1]["bank"],
        reverse=True
    )[:5]
    text=""
    for i,(uid,u) in enumerate(arr,1):
        m=ctx.guild.get_member(uid)
        n=m.display_name if m else f"User {uid}"
        text+=f"**{i}.** {n} — `{money(u['cash']+u['bank'])}`\n"
    await ctx.send(embed=E("🏆 TOP 5 GIÀU NHẤT",text,0xF1C40F))

# ================= QUAY =================

@bot.command()
async def quay(ctx,amount:int=None):
    if blocked(ctx): return
    if not amount or amount<1:
        return await ctx.send("❌ `!quay số_tiền`")
    u=U(ctx.author)
    if amount>u["cash"]:
        return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=amount
    s=["🍒","🍋","⭐","🔔","💎"]
    a,b,c=[random.choice(s) for _ in range(3)]

    msg=await ctx.send(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        "🔵 **[ ❓ ] [ ❓ ] [ ❓ ]**",
        0xF39C12))
    await asyncio.sleep(.5)
    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        f"🔵 **[ {a} ] [ ❓ ] [ ❓ ]**",
        0xF39C12))
    await asyncio.sleep(.5)
    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        f"🔵 **[ {a} ] [ {b} ] [ ❓ ]**",
        0xF39C12))
    await asyncio.sleep(.5)

    if a==b==c:
        win=amount*5
        u["cash"]+=win
        r=f"🟢 **JACKPOT x5!** +{money(win)}"
        col=0x2ECC71
    elif a==b or a==c or b==c:
        win=amount*3//2
        u["cash"]+=win
        r=f"🟢 **2 GIỐNG NHAU x1.5!** +{money(win)}"
        col=0x2ECC71
    else:
        r=f"🔴 **THUA!** -{money(amount)}"
        col=0xE74C3C

    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        f"🔵 **[ {a} ] [ {b} ] [ {c} ]**\n\n{r}",
        col))

# ================= BẦU CUA =================

@bot.command()
async def bc(ctx,choice:str=None,amount:int=None):
    if blocked(ctx): return
    icons={
        "ca":"🐟","tom":"🦐","cua":"🦀",
        "bau":"🥒","ga":"🐓","nai":"🦌"
    }
    if choice not in icons or not amount or amount<1:
        return await ctx.send("❌ `!bc cua 100`")
    u=U(ctx.author)
    if amount>u["cash"]:
        return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=amount
    r=[random.choice(list(icons)) for _ in range(3)]

    msg=await ctx.send(embed=E(
        "🎲 BẦU CUA",
        "🔵 **●  ●  ●**\n\n"
        "⏳ **Đang lắc...**",
        0xF39C12))
    await asyncio.sleep(1)

    board="  ".join(f"【{icons[x]}】" for x in r)
    count=r.count(choice)

    if count:
        win=amount*(count+1)
        u["cash"]+=win
        text=f"{board}\n\n🟢 **TRÚNG {count} CON! x{count+1}**\n💰 +{money(win)}"
        col=0x2ECC71
    else:
        text=f"{board}\n\n🔴 **THUA!**\n💸 -{money(amount)}"
        col=0xE74C3C

    await msg.edit(embed=E("🎲 BẦU CUA",text,col))

# ================= XÓC ĐĨA =================

@bot.command()
async def xd(ctx,choice:str=None,amount:int=None):
    if blocked(ctx): return
    if choice not in ["chan","le"] or not amount or amount<1:
        return await ctx.send("❌ `!xd chan 100`")
    u=U(ctx.author)
    if amount>u["cash"]:
        return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=amount

    msg=await ctx.send(embed=E(
        "🪙 XÓC ĐĨA",
        "🥣 **Xóc... Xóc... Xóc...**",
        0xF39C12))
    await asyncio.sleep(1.5)

    balls=[random.randint(0,1) for _ in range(4)]
    n=sum(balls)
    result="chan" if n%2==0 else "le"
    board="  ".join("🔴" if x else "⚪" for x in balls)

    if choice==result:
        u["cash"]+=amount*2
        r=f"{board}\n\n🟢 **{result.upper()} x2!** +{money(amount*2)}"
        col=0x2ECC71
    else:
        r=f"{board}\n\n🔴 **{result.upper()}** -{money(amount)}"
        col=0xE74C3C

    await msg.edit(embed=E("🪙 XÓC ĐĨA",r,col))

# ================= TÀI XỈU =================

@bot.command()
async def tx(ctx,choice:str=None,amount:int=None):
    if blocked(ctx): return
    if choice not in ["tai","xiu"]:
        return await ctx.send("❌ `!tx tai 100`")
    if not amount or not 100<=amount<=10_000_000:
        return await ctx.send("❌ Cược 100$ - 10.000.000$.")
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
            "🔵 **● ĐANG NHẬN CƯỢC ●**\n\n"
            "⏱️ **30 GIÂY**\n"
            "👥 Người cược: **1**",
            0xF39C12))

        for left in [20,10]:
            await asyncio.sleep(10)
            if not TX["on"]: return
            await msg.edit(embed=E(
                "🎲 TÀI XỈU",
                f"🔵 **● ĐANG NHẬN CƯỢC ●**\n\n"
                f"⏱️ Còn **{left} giây**\n"
                f"👥 **{len(TX['bets'])} người**",
                0xF39C12))

        await asyncio.sleep(10)
        TX["on"]=False

        d=[random.randint(1,6) for _ in range(3)]
        total=sum(d)
        result="tai" if total>=11 else "xiu"
        text=f"🎲 **{d[0]}  {d[1]}  {d[2]}**\n\n"
        text+=f"🎯 **{total} → {result.upper()}**\n\n"

        for uid,(ch,bet) in TX["bets"].items():
            pl=users[uid]
            if ch==result:
                win=bet*2
                pl["cash"]+=win
                text+=f"🟢 <@{uid}> +{money(win)}\n"
            else:
                text+=f"🔴 <@{uid}> -{money(bet)}\n"

        TX["bets"]={}
        await msg.edit(embed=E(
            "🎲 KẾT QUẢ TÀI XỈU",
            text,0x2ECC71))
        return

    if ctx.author.id in TX["bets"]:
        return await ctx.send("❌ Bạn đã cược rồi.")
    u["cash"]-=amount
    TX["bets"][ctx.author.id]=(choice,amount)
    await ctx.send(embed=E(
        "🎯 ĐẶT CƯỢC",
        f"{ctx.author.mention}\n"
        f"💰 **{money(amount)}** → **{choice.upper()}**",
        0x3498DB))

# ================= CODE =================

@bot.command()
async def taocode(ctx,amount:int=None,uses:int=None):
    if not adm(ctx):
        return await ctx.send("❌ Chỉ Admin.")
    if not amount or not uses:
        return await ctx.send("❌ `!taocode tiền lượt`")

    code="CASINO"+str(random.randint(100000,999999))
    codes[code]=[amount,uses]

    try:
        await ctx.author.send(
            f"🎟️ **CODE ADMIN**\n\n"
            f"🔑 `{code}`\n"
            f"💰 **{money(amount)}**\n"
            f"🎫 **{uses} lượt**"
        )
        await ctx.send("✅ Code đã được gửi riêng cho bạn.")
    except discord.Forbidden:
        await ctx.send(f"❌ Không gửi DM được: `{code}`")

# CODE HIỆN TRỰC TIẾP TRONG KÊNH

@bot.command()
async def thuongcode(ctx,amount:int=None,uses:int=None):
    if not adm(ctx):
        return await ctx.send("❌ Chỉ Admin.")
    if not amount or not uses or amount<1 or uses<1:
        return await ctx.send("❌ `!thuongcode số_tiền số_lượt`")

    code="THUONG"+str(random.randint(100000,999999))
    while code in codes:
        code="THUONG"+str(random.randint(100000,999999))

    codes[code]=[amount,uses]

    e=E(
        "🎁 CODE THƯỞNG",
        f"🔑 **CODE:** `{code}`\n"
        f"💰 **Tiền:** `{money(amount)}`\n"
        f"🎫 **Lượt nhập:** `{uses}`\n\n"
        f"📌 Nhập bằng: `!nhapcode {code}`",
        0x3498DB
    )
    e.set_footer(text="🎁 CASINO REWARD • Code dành cho thành viên")
    await ctx.send(embed=e)

@bot.command()
async def nhapcode(ctx,code:str=None):
    if not code:
        return await ctx.send("❌ `!nhapcode CODE`")
    code=code.upper()
    if code not in codes:
        return await ctx.send("❌ Code không tồn tại.")
    amount,uses=codes[code]
    if uses<=0:
        return await ctx.send("❌ Code đã hết lượt.")

    U(ctx.author)["cash"]+=amount
    codes[code][1]-=1

    await ctx.send(embed=E(
        "🎟️ NHẬP CODE THÀNH CÔNG",
        f"🟢 Nhận **{money(amount)}**\n"
        f"🎫 Còn **{uses-1} lượt**",
        0x2ECC71))

# ================= ADMIN =================

@bot.command()
async def settien(ctx,m:discord.Member=None,amount:int=None):
    if not adm(ctx): return await ctx.send("❌ Chỉ Admin.")
    if not m or amount is None:
        return await ctx.send("❌ `!settien @user tiền`")
    U(m)["cash"]=amount
    await ctx.send(f"✅ {m.mention} → **{money(amount)}**")

@bot.command()
async def kick(ctx,m:discord.Member=None):
    if not adm(ctx): return await ctx.send("❌ Chỉ Admin.")
    if not m: return
    await m.kick()
    await ctx.send(f"👢 Đã kick {m.mention}.")

@bot.command()
async def ban(ctx,m:discord.Member=None):
    if not adm(ctx): return await ctx.send("❌ Chỉ Admin.")
    if not m: return
    await m.ban()
    await ctx.send(f"🔨 Đã ban {m.mention}.")

@bot.command()
async def khoamom(ctx,m:discord.Member=None):
    if not adm(ctx): return await ctx.send("❌ Chỉ Admin.")
    if not m: return
    u=U(m)
    u["muted"]=not u["muted"]
    await ctx.send(
        f"🔇 {m.mention} "
        f"{'đã bị khóa.' if u['muted'] else 'đã được mở khóa.'}")

@bot.command()
async def reset(ctx,what:str=None,m:discord.Member=None):
    if not adm(ctx): return await ctx.send("❌ Chỉ Admin.")
    if what!="tien" or not m:
        return await ctx.send("❌ `!reset tien @user`")
    u=U(m)
    u["cash"]=START
    u["bank"]=0
    await ctx.send(
        f"♻️ {m.mention} đã về **{money(START)}**.")

# ================= SHOP =================

@bot.command()
async def cuahang(ctx):
    await ctx.send(embed=E(
        "🛒 CỬA HÀNG ROLE",
        "💛 **VIP** — `10.000.000$`\n`!muan vip`\n\n"
        "💙 **ĐẠI GIA** — `5.000.000$`\n`!muan daigia`\n\n"
        "💜 **TỶ PHÚ** — `1.000.000.000$`\n`!muan typhu`",
        0x3498DB))

@bot.command()
async def muan(ctx,name:str=None):
    prices={
        "vip":10_000_000,
        "daigia":5_000_000,
        "typhu":1_000_000_000
    }
    names={
        "vip":"VIP",
        "daigia":"Đại Gia",
        "typhu":"Tỷ Phú"
    }
    if name not in prices:
        return await ctx.send("❌ `!muan vip/daigia/typhu`")

    u=U(ctx.author)
    p=prices[name]
    role=discord.utils.get(ctx.guild.roles,name=names[name])

    if u["cash"]<p:
        return await ctx.send("❌ Không đủ tiền.")
    if not role:
        return await ctx.send("❌ Server chưa có role.")
    if role>=ctx.guild.me.top_role:
        return await ctx.send("❌ Role cao hơn bot.")

    u["cash"]-=p
    u["role"]=names[name]
    await ctx.author.add_roles(role)

    await ctx.send(embed=E(
        "👑 MUA ROLE THÀNH CÔNG",
        f"{ctx.author.mention}\n"
        f"👑 **{names[name]}**\n"
        f"💰 **{money(p)}**",
        0x2ECC71))

# ================= START =================

if not TOKEN:
    print("❌ Không tìm thấy TOKEN_BOT!")
else:
    bot.run(TOKEN)
