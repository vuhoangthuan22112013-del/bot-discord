import os,random,time,asyncio,discord
from discord.ext import commands

TOKEN=os.getenv("TOKEN_BOT")
START=2000
users={};codes={};spam={};loans={}
tx={"active":False,"bets":{},"msg":None,"channel":None,"end":0}

bot=commands.Bot(command_prefix="!",intents=discord.Intents.all(),help_command=None)

def U(m):
    if m.id not in users:
        users[m.id]={"cash":START,"bank":0,"daily":"","muted":False,"interest":time.time()}
    return users[m.id]

def fm(n): return f"{n:,}$"
def E(t,d,c=0x3498DB): return discord.Embed(title=t,description=d,color=c)
def adm(ctx): return ctx.author.guild_permissions.administrator

def interest(u):
    now=time.time()
    days=int((now-u["interest"])/86400)
    if days>0:
        if u["bank"]>0:u["bank"]=int(u["bank"]*(1.02**days))
        u["interest"]+=days*86400

def block(ctx):
    u=U(ctx.author);interest(u)
    if u["muted"]:
        asyncio.create_task(ctx.send("🔇 Bạn đang bị khóa mõm."))
        return True
    if ctx.author.id in loans and time.time()>loans[ctx.author.id]["due"]:
        asyncio.create_task(ctx.send("🔴 **CON NỢ!** Dùng `!trano số_tiền`."))
        return True
    return False

@bot.check
async def anti_spam(ctx):
    if ctx.author.bot:return False
    n=time.time()
    if n-spam.get(ctx.author.id,0)<1.2:return False
    spam[ctx.author.id]=n
    return True

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online,activity=discord.Game("!trogiup | Casino"))
    print("BOT ONLINE:",bot.user)

@bot.command()
async def trogiup(ctx):
    s=("## 🎰 CASINO\n"
       "`!tx tai 100` • `!tx xiu 100`\n"
       "`!bc cua 100` • `!xd chan 100`\n"
       "`!xd le 100` • `!quay 100`\n\n"
       "## 💰 TÀI KHOẢN\n"
       "`!vi` • `!chuyen @user 100`\n"
       "`!gui 100` • `!rut 100`\n"
       "`!diemdanh` • `!bxh`\n"
       "`!vay 1000` • `!trano 1000`\n\n"
       "## 🎟️ CODE\n`!nhapcode CODE`")
    if adm(ctx):
        s+=("\n\n## 🛡️ ADMIN\n"
            "`!taocode tiền lượt`\n`!thuongcode tiền lượt`\n"
            "`!settien @user tiền`\n`!reset tien @user`\n"
            "`!kick @user` • `!ban @user`\n"
            "`!khoamom @user` • `!unkhoamom @user`")
    await ctx.send(embed=E("📖 HƯỚNG DẪN CASINO",s))

@bot.command()
async def vi(ctx,m:discord.Member=None):
    m=m or ctx.author;u=U(m);interest(u)
    loan=loans.get(m.id,{}).get("amount",0)
    st="🔴 CON NỢ" if m.id in loans and time.time()>loans[m.id]["due"] else "🟢 Bình thường"
    await ctx.send(embed=E(
        f"💳 VÍ CỦA {m.display_name}",
        f"💵 **Tiền mặt:** {fm(u['cash'])}\n"
        f"🏦 **Ngân hàng:** {fm(u['bank'])}\n"
        f"💸 **Khoản vay:** {fm(loan)}\n"
        f"📌 **Trạng thái:** {st}"
    ))

@bot.command()
async def chuyen(ctx,m:discord.Member=None,amount:int=None):
    if not m or not amount or amount<=0:
        return await ctx.send("❌ `!chuyen @user số_tiền`")
    u=U(ctx.author)
    if amount>u["cash"]:return await ctx.send("❌ Không đủ tiền.")
    if m.id==ctx.author.id:return await ctx.send("❌ Không thể chuyển cho chính mình.")
    u["cash"]-=amount;U(m)["cash"]+=amount
    await ctx.send(f"💸 {ctx.author.mention} → {m.mention}: **{fm(amount)}**")

@bot.command()
async def gui(ctx,amount:int=None):
    if not amount or amount<=0:return await ctx.send("❌ `!gui số_tiền`")
    u=U(ctx.author);interest(u)
    if amount>u["cash"]:return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=amount;u["bank"]+=amount
    await ctx.send(embed=E("🏦 GỬI NGÂN HÀNG",
        f"💵 Gửi: **{fm(amount)}**\n"
        f"🏦 Số dư: **{fm(u['bank'])}**\n"
        "📈 Lãi suất: **2%/ngày**",0x2ECC71))

@bot.command()
async def rut(ctx,amount:int=None):
    if not amount or amount<=0:return await ctx.send("❌ `!rut số_tiền`")
    u=U(ctx.author);interest(u)
    if amount>u["bank"]:return await ctx.send("❌ Ngân hàng không đủ tiền.")
    u["bank"]-=amount;u["cash"]+=amount
    await ctx.send(f"🏦➡️💵 Đã rút **{fm(amount)}**.")

@bot.command()
async def diemdanh(ctx):
    u=U(ctx.author);d=time.strftime("%Y-%m-%d")
    if u["daily"]==d:return await ctx.send("⏰ Hôm nay đã điểm danh.")
    n=random.randint(1000,3000);u["cash"]+=n;u["daily"]=d
    await ctx.send(embed=E("🎁 ĐIỂM DANH",
        f"🎉 Nhận **{fm(n)}**\n💰 Số dư: **{fm(u['cash'])}**",0x2ECC71))

@bot.command()
async def bxh(ctx):
    arr=sorted(users.items(),key=lambda x:x[1]["cash"]+x[1]["bank"],reverse=True)[:5]
    s=""
    for i,(uid,u) in enumerate(arr,1):
        m=ctx.guild.get_member(uid)
        s+=f"**{i}.** {m.display_name if m else uid} — `{fm(u['cash']+u['bank'])}`\n"
    await ctx.send(embed=E("🏆 TOP 5 GIÀU NHẤT",s,0xF1C40F))

@bot.command()
async def vay(ctx,amount:int=None):
    if not amount or not 1000<=amount<=50000:return await ctx.send("❌ Vay từ **1.000$ đến 50.000$**.")
    if ctx.author.id in loans:return await ctx.send("❌ Bạn đang có khoản vay.")
    U(ctx.author)["cash"]+=amount
    loans[ctx.author.id]={"amount":amount,"due":time.time()+3600}
    await ctx.send(f"💳 Vay thành công **{fm(amount)}**. Hạn **1 giờ**.")

@bot.command()
async def trano(ctx,amount:int=None):
    if ctx.author.id not in loans:return await ctx.send("❌ Bạn không có nợ.")
    d=loans[ctx.author.id]["amount"];u=U(ctx.author)
    if amount!=d:return await ctx.send(f"❌ Phải trả đúng **{fm(d)}**.")
    if u["cash"]<d:return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=d;del loans[ctx.author.id]
    await ctx.send("✅ Đã trả nợ. Bạn được chơi lại.")

@bot.command()
async def quay(ctx,amount:int=None):
    if block(ctx):return
    if not amount or amount<1:return await ctx.send("❌ `!quay số_tiền`")
    u=U(ctx.author)
    if amount>u["cash"]:return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=amount
    s=["🍒","🍋","⭐","🔔","💎"]
    a,b,c=[random.choice(s) for _ in range(3)]
    msg=await ctx.send(embed=E("🎰 MÁY SLOT NỔ HŨ","【 ○ 】 【 ○ 】 【 ○ 】",0xF1C40F))
    await asyncio.sleep(.7)
    win=amount*5 if a==b==c else amount*2 if len({a,b,c})<3 else 0
    if win:u["cash"]+=win
    await msg.edit(embed=E("🎰 MÁY SLOT NỔ HŨ",
        f"【 {a} 】 【 {b} 】 【 {c} 】\n\n"+
        (f"🟢 **THẮNG!** +{fm(win)}" if win else f"🔴 **TRẬT HỦ!** -{fm(amount)}"),
        0x2ECC71 if win else 0xE74C3C))

@bot.command()
async def bc(ctx,choice=None,amount:int=None):
    if block(ctx):return
    icons={"ca":"🐟","tom":"🦐","cua":"🦀","bau":"🥒","ga":"🐓","nai":"🦌"}
    if choice not in icons or not amount:return await ctx.send("❌ `!bc ca/tom/cua/bau/ga/nai số_tiền`")
    u=U(ctx.author)
    if amount>u["cash"]:return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=amount;r=[random.choice(list(icons)) for _ in range(3)]
    n=r.count(choice);win=amount*(n+1) if n else 0
    if win:u["cash"]+=win
    board=" ".join(f"【 {icons[x]} 】" for x in r)
    await ctx.send(embed=E("🎲 BẦU CUA",f"{board}\n\n"+
        (f"🟢 **TRÚNG {n} CON!** +{fm(win)}" if win else f"🔴 **TRẬT!** -{fm(amount)}"),
        0x2ECC71 if win else 0xE74C3C))

@bot.command()
async def xd(ctx,choice=None,amount:int=None):
    if block(ctx):return
    if choice not in ("chan","le") or not amount:return await ctx.send("❌ `!xd chan 100` hoặc `!xd le 100`")
    u=U(ctx.author)
    if amount<100 or amount>u["cash"]:return await ctx.send("❌ Cược không hợp lệ.")
    u["cash"]-=amount
    msg=await ctx.send(embed=E("🪙 XÓC ĐĨA","🔴 ⚪ 🔴 🔴\n\n🥣 **Xóc... Xóc... Xóc...**",0xF1C40F))
    await asyncio.sleep(1.5)
    b=[random.randint(0,1) for _ in range(4)];n=sum(b)
    r="chan" if n%2==0 else "le";win=amount*2 if choice==r else 0
    if win:u["cash"]+=win
    board=" ".join("🔴" if x else "⚪" for x in b)
    await msg.edit(embed=E("🪙 XÓC ĐĨA",
        f"{board}\n\n🎯 **Kết quả: {r.upper()}**\n🔴 **Số đỏ: {n}**\n\n"+
        (f"🟢 **THẮNG x2!**\n💰 Nhận {fm(win)}" if win else f"🔴 **THUA!**\n💸 Mất {fm(amount)}"),
        0x2ECC71 if win else 0xE74C3C))

# =========================
# TÀI XỈU 30 GIÂY
# =========================

@bot.command()
async def tx(ctx,choice=None,amount:int=None):
    if block(ctx):return
    if choice not in ("tai","xiu") or not amount:
        return await ctx.send("❌ `!tx tai 100` hoặc `!tx xiu 100`")
    u=U(ctx.author)
    if amount<100 or amount>10000000:return await ctx.send("❌ Cược từ 100$ đến 10,000,000$.")
    if amount>u["cash"]:return await ctx.send("❌ Không đủ tiền.")

    if not tx["active"]:
        tx["active"]=True;tx["bets"]={};tx["channel"]=ctx.channel;tx["end"]=time.time()+30
        tx["msg"]=await ctx.send(embed=E(
            "🎲 SÒNG TÀI XỈU 30S 🎲",
            "📌 **Gõ `!tx <tai/xiu> <tiền>` để tham gia**\n"
            "💰 Tối đa **10,000,000$/ván**\n\n"
            "⏱️ **Thời gian: 30 giây**\n"
            "🔴 **Tổng Tài:** 0$\n"
            "🔵 **Tổng Xỉu:** 0$",0xF1C40F))
        asyncio.create_task(tx_timer())
        asyncio.create_task(tx_finish())

    if ctx.author.id in tx["bets"]:
        return await ctx.send("❌ **Bạn đã đặt cược rồi!** Mỗi phiên chỉ được cược 1 lần.")

    u["cash"]-=amount
    tx["bets"][ctx.author.id]=(choice,amount)
    await ctx.send(f"✅ {ctx.author.mention} đặt **{choice.upper()} {fm(amount)}**.")

async def tx_timer():
    while tx["active"]:
        left=max(0,int(tx["end"]-time.time()))
        if left<=0:break
        tai=sum(a for c,a in tx["bets"].values() if c=="tai")
        xiu=sum(a for c,a in tx["bets"].values() if c=="xiu")
        try:
            await tx["msg"].edit(embed=E(
                "🎲 SÒNG TÀI XỈU 30S 🎲",
                "📌 **Gõ `!tx <tai/xiu> <tiền>` để tham gia**\n"
                "💰 Tối đa **10,000,000$/ván**\n\n"
                f"⏱️ **Thời gian: {left} giây**\n"
                f"🔴 **Tổng Tài:** {fm(tai)}\n"
                f"🔵 **Tổng Xỉu:** {fm(xiu)}",0xF1C40F))
        except:pass
        await asyncio.sleep(1)

async def tx_finish():
    await asyncio.sleep(max(0,tx["end"]-time.time()))
    if not tx["active"]:return
    d=[random.randint(1,6) for _ in range(3)]
    total=sum(d);result="tai" if total>=11 else "xiu"
    name="TÀI 🔴" if result=="tai" else "XỈU 🔵"
    s=(f"🎲 **XÚC XẮC:** 【{d[0]}】 【{d[1]}】 【{d[2]}】\n"
       f"🎯 **{total} → {name}**\n\n")
    for uid,(c,a) in tx["bets"].items():
        if c==result:
            w=a*2;users[uid]["cash"]+=w;s+=f"🟢 <@{uid}> **+{fm(w)}**\n"
        else:s+=f"🔴 <@{uid}> **-{fm(a)}**\n"
    try:await tx["msg"].edit(embed=E("🎲 KẾT QUẢ TÀI XỈU 🎲",s,0x2ECC71))
    except:await tx["channel"].send(embed=E("🎲 KẾT QUẢ TÀI XỈU 🎲",s,0x2ECC71))
    tx["active"]=False;tx["bets"]={};tx["msg"]=None

@bot.command()
async def taocode(ctx,amount:int=None,uses:int=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if not amount or not uses:return await ctx.send("❌ `!taocode tiền lượt`")
    code="CASINO"+str(random.randint(100000,999999));codes[code]=[amount,uses]
    try:
        await ctx.author.send(f"🎟️ CODE: `{code}`\n💰 {fm(amount)}\n🎫 {uses} lượt")
        await ctx.send("✅ Code đã gửi DM.")
    except:await ctx.send(f"⚠️ Code: `{code}`")

@bot.command()
async def thuongcode(ctx,amount:int=None,uses:int=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if not amount or not uses:return await ctx.send("❌ `!thuongcode tiền lượt`")
    code="THUONG"+str(random.randint(100000,999999));codes[code]=[amount,uses]
    await ctx.send(embed=E("🎁 THƯỞNG CODE",f"🔑 `{code}`\n💰 {fm(amount)}\n🎫 {uses} lượt"))

@bot.command()
async def nhapcode(ctx,code=None):
    if not code or code.upper() not in codes:return await ctx.send("❌ Code không tồn tại.")
    code=code.upper();a,n=codes[code]
    if n<=0:return await ctx.send("❌ Code hết lượt.")
    U(ctx.author)["cash"]+=a;codes[code][1]-=1
    await ctx.send(f"🎟️ Nhận **{fm(a)}**. Còn **{n-1} lượt**.")

@bot.command()
async def settien(ctx,m:discord.Member=None,amount:int=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if not m or amount is None:return await ctx.send("❌ `!settien @user tiền`")
    U(m)["cash"]=max(0,amount);await ctx.send(f"🛡️ {m.mention} → **{fm(amount)}**")

@bot.command()
async def reset(ctx,what=None,m:discord.Member=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if what!="tien" or not m:return await ctx.send("❌ `!reset tien @user`")
    U(m)["cash"]=START;U(m)["bank"]=0;await ctx.send(f"♻️ Reset {m.mention}.")

@bot.command()
async def kick(ctx,m:discord.Member=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if not m:return await ctx.send("❌ `!kick @user`")
    await m.kick();await ctx.send(f"👢 Đã kick {m.mention}")

@bot.command()
async def ban(ctx,m:discord.Member=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if not m:return await ctx.send("❌ `!ban @user`")
    await m.ban();await ctx.send(f"🔨 Đã ban {m.mention}")

@bot.command()
async def khoamom(ctx,m:discord.Member=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if not m:return await ctx.send("❌ `!khoamom @user`")
    U(m)["muted"]=True;await ctx.send(f"🔇 {m.mention} đã bị khóa mõm.")

@bot.command()
async def unkhoamom(ctx,m:discord.Member=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if not m:return await ctx.send("❌ `!unkhoamom @user`")
    U(m)["muted"]=False;await ctx.send(f"🔊 {m.mention} đã được mở khóa.")

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error,commands.CommandNotFound):return
    if isinstance(error,commands.CommandOnCooldown):return
    if isinstance(error,commands.MissingRequiredArgument):
        return await ctx.send("❌ Thiếu thông tin. Gõ `!trogiup`.")
    if isinstance(error,commands.BadArgument):
        return await ctx.send("❌ Sai cú pháp.")
    print("ERROR:",error)

if not TOKEN:
    print("❌ Không tìm thấy TOKEN_BOT!")
else:
    print("🚀 BOT ĐANG CHẠY...")
    bot.run(TOKEN)
