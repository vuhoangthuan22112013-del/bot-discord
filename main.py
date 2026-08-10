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
        users[m.id]={"cash":START,"bank":0,"daily":0,"muted":False}
    return users[m.id]

def fm(n): return f"{n:,}$"
def E(t,d,c=0x3498DB): return discord.Embed(title=t,description=d,color=c)
def adm(ctx): return ctx.author.guild_permissions.administrator

def block(ctx):
    u=U(ctx.author)
    if u["muted"]:
        asyncio.create_task(ctx.send("🔇 Bạn đang bị khóa mõm."))
        return True
    if ctx.author.id in loans and time.time()>loans[ctx.author.id]["due"]:
        asyncio.create_task(ctx.send(
            "🔴 **CON NỢ!** Bạn không được chơi.\n"
            "💳 Hãy dùng `!trano số_tiền` để trả nợ."
        ))
        return True
    return False

@bot.check
async def anti_spam(ctx):
    if ctx.author.bot:return False
    now=time.time()
    old=spam.get(ctx.author.id,0)
    if now-old<1.2:
        return False
    spam[ctx.author.id]=now
    return True

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino")
    )
    print("BOT ONLINE:",bot.user)

@bot.command()
async def trogiup(ctx):
    t=(
        "## 🎰 GAME\n"
        "`!quay 100` • `!bc cua 100`\n"
        "`!xd chan 100` • `!tx tai 100`\n\n"
        "## 💰 TÀI KHOẢN\n"
        "`!vi` • `!vay 1000` • `!trano 1000`\n"
        "`!diemdanh` • `!bxh`\n\n"
        "## 🎟️ CODE\n"
        "`!nhapcode CODE`\n\n"
        "## 🛡️ ADMIN\n"
        "`!taocode tiền lượt`\n"
        "`!thuongcode tiền lượt`\n"
        "`!settien @user tiền`\n"
        "`!reset tien @user`\n"
        "`!kick @user` • `!ban @user`\n"
        "`!khoamom @user`"
    )
    await ctx.send(embed=E("📖 HƯỚNG DẪN CASINO",t))

@bot.command()
async def vi(ctx,m:discord.Member=None):
    m=m or ctx.author
    u=U(m)
    loan=loans.get(m.id,{}).get("amount",0)
    status="🔴 CON NỢ" if m.id in loans and time.time()>loans[m.id]["due"] else "🟢 Bình thường"
    await ctx.send(embed=E(
        f"💳 VÍ CỦA {m.display_name}",
        f"💵 Tiền: **{fm(u['cash'])}**\n"
        f"🏦 Ngân hàng: **{fm(u['bank'])}**\n"
        f"💸 Khoản vay: **{fm(loan)}**\n"
        f"📌 Trạng thái: **{status}**"
    ))

@bot.command()
async def diemdanh(ctx):
    u=U(ctx.author)
    today=time.strftime("%Y-%m-%d")
    if u["daily"]==today:
        return await ctx.send("⏰ Hôm nay bạn đã điểm danh rồi.")
    n=random.randint(1000,3000)
    u["cash"]+=n
    u["daily"]=today
    await ctx.send(embed=E(
        "🎁 ĐIỂM DANH",
        f"🎉 Bạn nhận **{fm(n)}**!\n"
        f"💰 Số dư: **{fm(u['cash'])}**",0x2ECC71))

@bot.command()
async def bxh(ctx):
    arr=sorted(users.items(),
        key=lambda x:x[1]["cash"]+x[1]["bank"],reverse=True)[:5]
    s=""
    for i,(uid,u) in enumerate(arr,1):
        m=ctx.guild.get_member(uid)
        n=m.display_name if m else str(uid)
        s+=f"**{i}.** {n} — 💰 `{fm(u['cash']+u['bank'])}`\n"
    await ctx.send(embed=E("🏆 TOP 5 GIÀU NHẤT",s,0xF1C40F))

@bot.command()
async def vay(ctx,amount:int=None):
    if not amount or not 1000<=amount<=50000:
        return await ctx.send("❌ Chỉ được vay **1.000$ - 50.000$**.")
    if ctx.author.id in loans:
        return await ctx.send("❌ Bạn đang có khoản vay.")
    U(ctx.author)["cash"]+=amount
    loans[ctx.author.id]={
        "amount":amount,
        "due":time.time()+3600
    }
    await ctx.send(embed=E(
        "💳 VAY TIỀN THÀNH CÔNG",
        f"✅ Bạn đã vay **{fm(amount)}**.\n"
        "⏰ Thời hạn: **1 giờ**.\n"
        "⚠️ Quá hạn sẽ thành **CON NỢ** và không được chơi.\n\n"
        f"💡 Trả bằng `!trano {amount}`",0xF39C12))

@bot.command()
async def trano(ctx,amount:int=None):
    if ctx.author.id not in loans:
        return await ctx.send("❌ Bạn không có khoản nợ.")
    d=loans[ctx.author.id]["amount"]
    if amount!=d:
        return await ctx.send(f"❌ Phải trả đúng **{fm(d)}**.")
    u=U(ctx.author)
    if u["cash"]<d:
        return await ctx.send("❌ Bạn không đủ tiền.")
    u["cash"]-=d
    del loans[ctx.author.id]
    await ctx.send(embed=E(
        "✅ ĐÃ TRẢ NỢ",
        f"{ctx.author.mention} đã trả **{fm(d)}**.\n"
        "🟢 Bạn được phép chơi lại!",0x2ECC71))

@bot.command()
async def quay(ctx,amount:int=None):
    if block(ctx):return
    if not amount or amount<1:return await ctx.send("❌ `!quay số_tiền`")
    u=U(ctx.author)
    if amount>u["cash"]:return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=amount
    s=["🍒","🍋","⭐","🔔","💎"]
    a,b,c=[random.choice(s) for _ in range(3)]

    msg=await ctx.send(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        "🔵 **【 ○ 】 【 ○ 】 【 ○ 】**",0xF39C12))
    await asyncio.sleep(.5)
    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        f"🔵 **【 {a} 】 【 ○ 】 【 ○ 】**",0xF39C12))
    await asyncio.sleep(.5)
    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        f"🔵 **【 {a} 】 【 {b} 】 【 ○ 】**",0xF39C12))
    await asyncio.sleep(.5)

    if a==b==c:
        win=amount*5;u["cash"]+=win
        r=f"🟢 **JACKPOT x5!**\n💰 +{fm(win)}";co=0x2ECC71
    elif len({a,b,c})<3:
        win=amount*2;u["cash"]+=win
        r=f"🟢 **2 HÌNH GIỐNG NHAU x2!**\n💰 +{fm(win)}";co=0x2ECC71
    else:
        r=f"🔴 **THUA!**\n💸 -{fm(amount)}";co=0xE74C3C

    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        f"🔵 **【 {a} 】 【 {b} 】 【 {c} 】**\n\n{r}",co))

@bot.command()
async def bc(ctx,choice:str=None,amount:int=None):
    if block(ctx):return
    icons={"ca":"🐟","tom":"🦐","cua":"🦀",
           "bau":"🥒","ga":"🐓","nai":"🦌"}
    if choice not in icons or not amount or amount<1:
        return await ctx.send("❌ `!bc ca/tom/cua/bau/ga/nai số_tiền`")
    u=U(ctx.author)
    if amount>u["cash"]:return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=amount
    r=[random.choice(list(icons)) for _ in range(3)]

    msg=await ctx.send(embed=E(
        "🎲 BẦU CUA",
        "🔵 **◯   ◯   ◯**",0xF39C12))
    await asyncio.sleep(.7)

    board="  ".join(f"【 {icons[x]} 】" for x in r)
    n=r.count(choice)
    if n:
        win=amount*(n+1);u["cash"]+=win
        text=f"{board}\n\n🟢 **TRÚNG {n} CON! x{n+1}**\n💰 +{fm(win)}"
        co=0x2ECC71
    else:
        text=f"{board}\n\n🔴 **THUA!**\n💸 -{fm(amount)}"
        co=0xE74C3C
    await msg.edit(embed=E("🎲 BẦU CUA",text,co))

@bot.command()
async def xd(ctx,choice:str=None,amount:int=None):
    if block(ctx):return
    if choice not in ("chan","le") or not amount or amount<1:
        return await ctx.send("❌ `!xd chan 100` hoặc `!xd le 100`")
    u=U(ctx.author)
    if amount>u["cash"]:return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=amount

    msg=await ctx.send(embed=E(
        "🪙 XÓC ĐĨA","🥣 **Xóc... Xóc... Xóc...**",0xF39C12))
    await asyncio.sleep(1.5)

    balls=[random.randint(0,1) for _ in range(4)]
    n=sum(balls)
    result="chan" if n%2==0 else "le"
    board="  ".join("🔴" if x else "⚪" for x in balls)

    if choice==result:
        win=amount*2;u["cash"]+=win
        r=f"{board}\n\n🎯 **{result.upper()}**\n🟢 **THẮNG x2!**\n💰 +{fm(win)}"
        co=0x2ECC71
    else:
        r=f"{board}\n\n🎯 **{result.upper()}**\n🔴 **THUA!**\n💸 -{fm(amount)}"
        co=0xE74C3C
    await msg.edit(embed=E("🪙 XÓC ĐĨA",r,co))

@bot.command()
async def tx(ctx,choice:str=None,amount:int=None):
    if block(ctx):return
    if choice not in ("tai","xiu") or not amount:
        return await ctx.send("❌ `!tx tai 100` hoặc `!tx xiu 100`")
    u=U(ctx.author)
    if amount<100 or amount>10000000:return await ctx.send("❌ Cược không hợp lệ.")
    if amount>u["cash"]:return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=amount
    msg=await ctx.send(embed=E(
        "🎲 TÀI XỈU",
        "🔵 **◯   ◯   ◯**\n\n⏳ Đang lắc...",0xF39C12))
    await asyncio.sleep(1.5)
    d=[random.randint(1,6) for _ in range(3)]
    total=sum(d)
    result="tai" if total>=11 else "xiu"
    if choice==result:
        win=amount*2;u["cash"]+=win
        r=f"🎲 **{d[0]} {d[1]} {d[2]}**\n"
        r+=f"🎯 **{total} → {result.upper()}**\n🟢 +{fm(win)}"
        co=0x2ECC71
    else:
        r=f"🎲 **{d[0]} {d[1]} {d[2]}**\n"
        r+=f"🎯 **{total} → {result.upper()}**\n🔴 -{fm(amount)}"
        co=0xE74C3C
    await msg.edit(embed=E("🎲 KẾT QUẢ TÀI XỈU",r,co))

@bot.command()
async def taocode(ctx,amount:int=None,uses:int=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if not amount or not uses:return await ctx.send("❌ `!taocode tiền lượt`")
    code="CASINO"+str(random.randint(100000,999999))
    codes[code]=[amount,uses]
    try:
        await ctx.author.send(
            f"🎟️ CODE ADMIN\n\n🔑 `{code}`\n"
            f"💰 {fm(amount)}\n🎫 {uses} lượt")
        await ctx.send("✅ Code đã được gửi riêng vào DM.")
    except:
        await ctx.send(f"⚠️ Không gửi DM được: `{code}`")

@bot.command()
async def thuongcode(ctx,amount:int=None,uses:int=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if not amount or not uses:
        return await ctx.send("❌ `!thuongcode tiền lượt`")
    code="THUONG"+str(random.randint(100000,999999))
    codes[code]=[amount,uses]
    await ctx.send(embed=E(
        "🎁 🎟️ THƯỞNG CODE",
        f"🔑 **CODE:** `{code}`\n"
        f"💰 **Tiền:** `{fm(amount)}`\n"
        f"🎫 **Lượt nhập:** `{uses}`\n\n"
        f"📌 Nhập: `!nhapcode {code}`",0x3498DB))

@bot.command()
async def nhapcode(ctx,code:str=None):
    if not code:return await ctx.send("❌ Nhập code.")
    code=code.upper()
    if code not in codes:return await ctx.send("❌ Code không tồn tại.")
    amount,uses=codes[code]
    if uses<=0:return await ctx.send("❌ Code hết lượt.")
    U(ctx.author)["cash"]+=amount
    codes[code][1]-=1
    await ctx.send(embed=E(
        "🎟️ NHẬP CODE THÀNH CÔNG",
        f"💰 Nhận **{fm(amount)}**\n"
        f"🎫 Còn **{uses-1} lượt**",0x2ECC71))

@bot.command()
async def settien(ctx,m:discord.Member=None,amount:int=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if not m or amount is None:return await ctx.send("❌ `!settien @user tiền`")
    U(m)["cash"]=max(0,amount)
    await ctx.send(f"🛡️ Đã set tiền {m.mention} → **{fm(amount)}**.")

@bot.command()
async def reset(ctx,what:str=None,m:discord.Member=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if what!="tien" or not m:return await ctx.send("❌ `!reset tien @user`")
    U(m)["cash"]=START
    U(m)["bank"]=0
    await ctx.send(f"♻️ {m.mention} đã được reset về **{fm(START)}**.")

@bot.command()
async def kick(ctx,m:discord.Member=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if not m:return await ctx.send("❌ `!kick @user`")
    await m.kick()
    await ctx.send(f"👢 Đã kick {m.mention}.")

@bot.command()
async def ban(ctx,m:discord.Member=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if not m:return await ctx.send("❌ `!ban @user`")
    await m.ban()
    await ctx.send(f"🔨 Đã ban {m.mention}.")

@bot.command()
async def khoamom(ctx,m:discord.Member=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if not m:return await ctx.send("❌ `!khoamom @user`")
    u=U(m);u["muted"]=not u["muted"]
    await ctx.send(f"🔇 {m.mention} {'đã bị khóa.' if u['muted'] else 'đã được mở khóa.'}")

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error,commands.CommandNotFound):return
    if isinstance(error,commands.MissingRequiredArgument):
        return await ctx.send("❌ Thiếu thông tin. Gõ `!trogiup`.")
    if isinstance(error,commands.BadArgument):
        return await ctx.send("❌ Sai cú pháp.")
    if isinstance(error,commands.CommandOnCooldown):
        return
    print("ERROR:",error)

if not TOKEN:
    print("❌ Không tìm thấy biến TOKEN_BOT!")
else:
    bot.run(TOKEN)
