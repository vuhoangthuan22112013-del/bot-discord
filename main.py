import os,random,asyncio,time,discord
from discord.ext import commands,tasks

I=discord.Intents.default()
I.message_content=True
I.members=True
bot=commands.Bot(command_prefix="!",intents=I,help_command=None)

U={}; C={}; TX={"on":False,"bets":{}}

BLUE=0x3498DB; GREEN=0x2ECC71; RED=0xE74C3C
ORANGE=0xF39C12; PURPLE=0x9B59B6

def user(m):
    if m.id not in U:
        U[m.id]={"cash":2000,"bank":0,"role":"Không có",
                 "daily":"","debt":0,"deadline":0}
    return U[m.id]

def money(n): return f"{n:,}$"
def E(t,d,c=BLUE):
    return discord.Embed(title=t,description=d,color=c)
def admin(ctx): return ctx.author.guild_permissions.administrator
def blocked(u):
    return "❌ Bạn đang có khoản nợ quá hạn." if u["debt"] and time.time()>=u["deadline"] else None

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino"))
    print("BOT ONLINE:",bot.user)

# HELP
@bot.command(name="trogiup")
async def help(ctx):
    await ctx.send(embed=E("🎰 CASINO",
"""## 🎲 GAME
`!tx tai 1000` / `!tx xiu 1000`
`!bc cua 1000`
`!xd chan 1000` / `!xd le 1000`
`!quay 1000`

## 💰 TÀI KHOẢN
`!vi`
`!gui 1000`
`!rut 1000`
`!chuyen @user 1000`
`!vay 50000`
`!trano 50000`
`!diemdanh`
`!bxh`

## 🛒 ROLE
`!cuahang`
`!muan vip`
`!muan daigia`
`!muan typhu`

## 🎁 CODE
`!nhapcode CODE`

## 👑 ADMIN
`!taocodechomn 50000 10`
`!settien @user 100000`
`!reset tien @user`
`!kick @user`
`!ban @user`
`!khoamom @user`""",BLUE))

# VI
@bot.command(name="vi")
async def vi(ctx,m:discord.Member=None):
    m=m or ctx.author; u=user(m)
    await ctx.send(embed=E(
        f"💳 VÍ {m.display_name}",
        f"💵 Tiền: `{money(u['cash'])}`\n"
        f"🏦 Bank: `{money(u['bank'])}`\n"
        f"💸 Nợ: `{money(u['debt'])}`\n"
        f"👑 Role: **{u['role']}**"))

# GUI
@bot.command(name="gui")
async def gui(ctx,n:int=None):
    if not n or n<=0:return await ctx.send("❌ `!gui số_tiền`")
    u=user(ctx.author)
    if n>u["cash"]:return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=n;u["bank"]+=n
    await ctx.send(embed=E("🏦 GỬI TIỀN",
        f"Đã gửi `{money(n)}`.\nSố dư: `{money(u['bank'])}`",GREEN))

# RUT
@bot.command(name="rut")
async def rut(ctx,n:int=None):
    if not n or n<=0:return await ctx.send("❌ `!rut số_tiền`")
    u=user(ctx.author)
    if n>u["bank"]:return await ctx.send("❌ Bank không đủ.")
    u["bank"]-=n;u["cash"]+=n
    await ctx.send(embed=E("💵 RÚT TIỀN",
        f"Đã rút `{money(n)}`.",GREEN))

# CHUYEN
@bot.command(name="chuyen")
async def chuyen(ctx,m:discord.Member=None,n:int=None):
    if not m or n is None:return await ctx.send("❌ `!chuyen @user số_tiền`")
    if n<1 or n>10_000_000:return await ctx.send("❌ Tối đa 10.000.000$.")
    if m.id==ctx.author.id:return await ctx.send("❌ Không thể chuyển cho mình.")
    a=user(ctx.author);b=user(m)
    if a["cash"]<n:return await ctx.send("❌ Không đủ tiền.")
    a["cash"]-=n;b["cash"]+=n
    await ctx.send(f"💸 {ctx.author.mention} → {m.mention}: `{money(n)}`")

# VAY
@bot.command(name="vay")
async def vay(ctx,n:int=None):
    if not n or n<1000 or n>50000:
        return await ctx.send("❌ Vay từ 1.000$ đến 50.000$.")
    u=user(ctx.author)
    if u["debt"]:return await ctx.send("❌ Bạn đang có khoản vay.")
    u["cash"]+=n;u["debt"]=n;u["deadline"]=time.time()+3600
    await ctx.send(embed=E("🏦 ĐÃ VAY",
        f"💰 Đã vay: **{money(n)}**\n"
        "⏰ Thời hạn: **1 giờ**\n"
        "⚠️ Quá hạn sẽ thành **CON NỢ** và không được chơi.\n"
        f"💸 Trả: `!trano {n}`",ORANGE))

# TRANO
@bot.command(name="trano")
async def trano(ctx,n:int=None):
    u=user(ctx.author)
    if not u["debt"]:return await ctx.send("❌ Bạn không có nợ.")
    if n!=u["debt"]:return await ctx.send(f"❌ Phải trả `{money(u['debt'])}`.")
    if u["cash"]<n:return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=n;u["debt"]=0;u["deadline"]=0
    await ctx.send(embed=E("✅ ĐÃ TRẢ NỢ",
        f"{ctx.author.mention} đã trả `{money(n)}`.\n"
        "🎉 Bạn được chơi lại bình thường!",GREEN))

# DIEM DANH
@bot.command(name="diemdanh")
async def daily(ctx):
    u=user(ctx.author); today=time.strftime("%Y-%m-%d")
    if u["daily"]==today:return await ctx.send("❌ Hôm nay đã điểm danh.")
    n=random.randint(1000,3000);u["cash"]+=n;u["daily"]=today
    await ctx.send(embed=E("📅 ĐIỂM DANH",
        f"🎉 Nhận được `{money(n)}`.",GREEN))

# BXH
@bot.command(name="bxh")
async def bxh(ctx):
    arr=sorted(U.items(),key=lambda x:x[1]["cash"]+x[1]["bank"],reverse=True)
    s=""
    for i,(uid,u) in enumerate(arr[:5],1):
        m=ctx.guild.get_member(uid)
        s+=f"**{i}. {m.display_name if m else uid}** — `{money(u['cash']+u['bank'])}`\n"
    await ctx.send(embed=E("🏆 TOP 5 GIÀU NHẤT",s or "Chưa có dữ liệu.",PURPLE))

# QUAY
@bot.command(name="quay")
async def quay(ctx,n:int=None):
    if not n or n<=0:return await ctx.send("❌ `!quay số_tiền`")
    u=user(ctx.author)
    if blocked(u):return await ctx.send("❌ Bạn là CON NỢ, hãy trả nợ trước.")
    if n>u["cash"]:return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=n
    x=random.choices(["🍒","🍋","🔔","⭐","💎"],k=3)
    msg=await ctx.send(embed=E("7️⃣7️⃣7️⃣","## 🔄　🔄　🔄",ORANGE))
    await asyncio.sleep(.6)
    await msg.edit(embed=E("7️⃣7️⃣7️⃣",f"## {x[0]}　❔　❔",ORANGE))
    await asyncio.sleep(.6)
    await msg.edit(embed=E("7️⃣7️⃣7️⃣",f"## {x[0]}　{x[1]}　❔",ORANGE))
    await asyncio.sleep(.6)
    await msg.edit(embed=E("7️⃣7️⃣7️⃣",f"## {x[0]}　{x[1]}　{x[2]}",ORANGE))
    if x[0]==x[1]==x[2]:
        r=n*5;u["cash"]+=r;t=f"## {x[0]}　{x[1]}　{x[2]}\n\n🟢 **JACKPOT x5**\n💰 `{money(r)}`";c=GREEN
    elif x[0]==x[1] or x[0]==x[2] or x[1]==x[2]:
        r=int(n*1.5);u["cash"]+=r;t=f"## {x[0]}　{x[1]}　{x[2]}\n\n🟢 **2 HÌNH x1.5**\n💰 `{money(r)}`";c=GREEN
    else:t=f"## {x[0]}　{x[1]}　{x[2]}\n\n🔴 **THUA**\n💸 `{money(n)}`";c=RED
    await asyncio.sleep(.4)
    await msg.edit(embed=E("7️⃣7️⃣7️⃣",t,c))

# XOC DIA
@bot.command(name="xd")
async def xd(ctx,ch:str=None,n:int=None):
    if ch not in ["chan","le"] or not n:return await ctx.send("❌ `!xd chan 1000` hoặc `!xd le 1000`")
    u=user(ctx.author)
    if blocked(u):return await ctx.send("❌ Bạn là CON NỢ, hãy trả nợ.")
    if n<100 or n>10_000_000:return await ctx.send("❌ Cược 100$ - 10.000.000$.")
    if n>u["cash"]:return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=n
    msg=await ctx.send(embed=E("🪙 XÓC ĐĨA","## 🟠 Xóc... Xóc... Xóc...",ORANGE))
    await asyncio.sleep(2)
    a=[random.randint(0,1) for _ in range(4)];red=sum(a)
    result="chan" if red%2==0 else "le"
    board="　".join("🔴" if i else "⚪" for i in a)
    if ch==result:
        r=n*2;u["cash"]+=r;t=f"## {board}\n\n🎯 **{result.upper()}**\n🟢 **THẮNG x2**\n💰 `{money(r)}`";c=GREEN
    else:t=f"## {board}\n\n🎯 **{result.upper()}**\n🔴 **THUA**\n💸 `{money(n)}`";c=RED
    await msg.edit(embed=E("🪙 XÓC ĐĨA",t,c))

# BAU CUA
@bot.command(name="bc")
async def bc(ctx,ch:str=None,n:int=None):
    A={"ca":"🐟","tom":"🦐","cua":"🦀","bau":"🥒","ga":"🐓","nai":"🦌"}
    if ch not in A or not n:return await ctx.send("❌ `!bc ca/tom/cua/bau/ga/nai số_tiền`")
    u=user(ctx.author)
    if blocked(u):return await ctx.send("❌ Bạn là CON NỢ, hãy trả nợ.")
    if n<100 or n>10_000_000:return await ctx.send("❌ Cược 100$ - 10.000.000$.")
    if n>u["cash"]:return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=n;x=random.choices(list(A),k=3)
    msg=await ctx.send(embed=E("🎲 BẦU CUA","## 🎲　🎲　🎲",ORANGE))
    await asyncio.sleep(.6)
    await msg.edit(embed=E("🎲 BẦU CUA",f"## {A[x[0]]}　❔　❔",ORANGE))
    await asyncio.sleep(.6)
    await msg.edit(embed=E("🎲 BẦU CUA",f"## {A[x[0]]}　{A[x[1]]}　❔",ORANGE))
    await asyncio.sleep(.6)
    board=f"## {A[x[0]]}　{A[x[1]]}　{A[x[2]]}"
    k=x.count(ch)
    if k:
        r=n*(k+1);u["cash"]+=r;t=f"{board}\n\n🟢 **TRÚNG {k} CON x{k+1}**\n💰 `{money(r)}`";c=GREEN
    else:t=f"{board}\n\n🔴 **THUA**\n💸 `{money(n)}`";c=RED
    await msg.edit(embed=E("🎲 BẦU CUA",t,c))

# TAIXIU
@bot.command(name="tx")
async def tx(ctx,ch:str=None,n:int=None):
    if ch not in ["tai","xiu"] or not n:return await ctx.send("❌ `!tx tai 1000` / `!tx xiu 1000`")
    if n<100 or n>10_000_000:return await ctx.send("❌ Cược 100$ - 10.000.000$.")
    u=user(ctx.author)
    if blocked(u):return await ctx.send("❌ Bạn là CON NỢ, hãy trả nợ.")
    if u["cash"]<n:return await ctx.send("❌ Không đủ tiền.")
    if not TX["on"]:
        TX["on"]=True;TX["bets"]={};first=True
        msg=await ctx.send(embed=E("🎲 TÀI XỈU","## 🟠 PHIÊN 30 GIÂY\n⏱️ Đang nhận cược...",ORANGE))
        u["cash"]-=n;TX["bets"][ctx.author.id]=(ch,n,ctx.author.display_name)
        await asyncio.sleep(30)
        TX["on"]=False
        d=[random.randint(1,6) for _ in range(3)];total=sum(d)
        result="tai" if total>=11 else "xiu"
        s=f"## 🎲 {d[0]}　{d[1]}　{d[2]}\n\n**{total} → {result.upper()}**\n\n"
        for uid,(c,a,name) in TX["bets"].items():
            p=U[uid]
            if c==result:
                r=a*2;p["cash"]+=r;s+=f"🟢 {name} +`{money(r)}`\n"
            else:s+=f"🔴 {name} -`{money(a)}`\n"
        TX["bets"]={}
        await msg.edit(embed=E("🎲 KẾT QUẢ",s,GREEN if result else RED))
    else:
        if ctx.author.id in TX["bets"]:return await ctx.send("❌ Bạn đã cược.")
        u["cash"]-=n;TX["bets"][ctx.author.id]=(ch,n,ctx.author.display_name)
        await ctx.send(f"🎲 {ctx.author.mention} cược `{money(n)}` **{ch.upper()}**")

# SHOP
@bot.command(name="cuahang")
async def shop(ctx):
    await ctx.send(embed=E("🛒 CỬA HÀNG",
        "💛 VIP — `10.000.000$`\n`!muan vip`\n\n"
        "💙 ĐẠI GIA — `5.000.000$`\n`!muan daigia`\n\n"
        "💜 TỶ PHÚ — `1.000.000.000$`\n`!muan typhu`",PURPLE))

@bot.command(name="muan")
async def muan(ctx,r:str=None):
    P={"vip":(10_000_000,"VIP"),"daigia":(5_000_000,"Đại Gia"),"typhu":(1_000_000_000,"Tỷ Phú")}
    if r not in P:return await ctx.send("❌ `!muan vip/daigia/typhu`")
    u=user(ctx.author);price,name=P[r]
    if u["cash"]<price:return await ctx.send("❌ Không đủ tiền.")
    role=discord.utils.get(ctx.guild.roles,name=name)
    if not role:return await ctx.send(f"❌ Chưa có role **{name}**.")
    if role>=ctx.guild.me.top_role:return await ctx.send("❌ Role cao hơn bot.")
    u["cash"]-=price;u["role"]=name
    try:await ctx.author.add_roles(role)
    except discord.Forbidden:return await ctx.send("❌ Bot không có quyền.")
    await ctx.send(embed=E("👑 MUA THÀNH CÔNG",f"Role: **{name}**\nGiá: `{money(price)}`",GREEN))

# TAO CODE
@bot.command(name="taocodechomn")
async def makecode(ctx,n:int=None,uses:int=None):
    if not admin(ctx):return await ctx.send("❌ Chỉ Admin.")
    if not n or not uses or n<=0 or uses<=0:return await ctx.send("❌ `!taocodechomn tiền lượt`")
    code="BET-"+''.join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789",k=8))
    C[code]={"money":n,"uses":uses}
    await ctx.send(embed=E("🎁 CODE THƯỞNG",
        f"## 🎟️ `{code}`\n\n💰 Tiền: `{money(n)}`\n🔢 Lượt: `{uses}`\n\n`!nhapcode {code}`",GREEN))

# NHAP CODE
@bot.command(name="nhapcode")
async def usecode(ctx,code:str=None):
    if not code:return await ctx.send("❌ `!nhapcode CODE`")
    code=code.upper()
    if code not in C:return await ctx.send("❌ Code không tồn tại.")
    d=C[code]
    u=user(ctx.author);u["cash"]+=d["money"];d["uses"]-=1
    if d["uses"]<=0:del C[code]
    await ctx.send(embed=E("🎁 NHẬP CODE",
        f"✅ Nhận `{money(d['money'])}`.",GREEN))

# SET TIỀN
@bot.command(name="settien")
async def settien(ctx,m:discord.Member=None,n:int=None):
    if not admin(ctx):return await ctx.send("❌ Chỉ Admin.")
    if not m or n is None:return await ctx.send("❌ `!settien @user tiền`")
    user(m)["cash"]=max(0,n)
    await ctx.send(f"👑 Đã set tiền {m.mention} = `{money(n)}`")

# RESET
@bot.command(name="reset")
async def reset(ctx,w:str=None,m:discord.Member=None):
    if not admin(ctx):return await ctx.send("❌ Chỉ Admin.")
    if w!="tien" or not m:return await ctx.send("❌ `!reset tien @user`")
    u=user(m);u["cash"]=2000;u["bank"]=0
    await ctx.send(f"🔄 {m.mention} đã reset về `{money(2000)}`.")

# KICK
@bot.command(name="kick")
async def kick(ctx,m:discord.Member=None):
    if not admin(ctx):return await ctx.send("❌ Chỉ Admin.")
    if not m:return await ctx.send("❌ `!kick @user`")
    try:await m.kick();await ctx.send(f"👢 Đã kick {m.mention}.")
    except discord.Forbidden:await ctx.send("❌ Bot không có quyền.")

# BAN
@bot.command(name="ban")
async def ban(ctx,m:discord.Member=None):
    if not admin(ctx):return await ctx.send("❌ Chỉ Admin.")
    if not m:return await ctx.send("❌ `!ban @user`")
    try:await m.ban();await ctx.send(f"🔨 Đã ban {m.mention}.")
    except discord.Forbidden:await ctx.send("❌ Bot không có quyền.")

# KHOA MOM
@bot.command(name="khoamom")
async def mute(ctx,m:discord.Member=None):
    if not admin(ctx):return await ctx.send("❌ Chỉ Admin.")
    if not m:return await ctx.send("❌ `!khoamom @user`")
    for ch in ctx.guild.text_channels:
        try:await ch.set_permissions(m,send_messages=False)
        except:pass
    await ctx.send(f"🔇 Đã khóa mồm {m.mention}.")

# KIEM TRA NO
@tasks.loop(seconds=30)
async def debtcheck():
    now=time.time()
    for u in U.values():
        if u["debt"] and now>=u["deadline"]:
            u["deadline"]=now

@debtcheck.before_loop
async def before_debt():
    await bot.wait_until_ready()

debtcheck.start()

TOKEN=os.getenv("TOKEN_BOT")
if not TOKEN:
    print("❌ Chưa có TOKEN_BOT")
else:
    bot.run(TOKEN)
