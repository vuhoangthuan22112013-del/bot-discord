import os,asyncio,random,secrets,time,discord
from discord.ext import commands

I=discord.Intents.default()
I.message_content=True
bot=commands.Bot(command_prefix="!",intents=I,help_command=None)

U,C,LOANS={}, {}, {}
BLUE,ORANGE,GREEN,RED,GOLD=0x3498DB,0xF1C40F,0x2ECC71,0xE74C3C,0xFFD700
TX={"on":0,"bets":{},"tai":0,"xiu":0,"msg":None}
RATE=100

def E(t,d,c=BLUE): return discord.Embed(title=t,description=d,color=c)
def M(n): return f"{int(n):,}$"

def user(i,n="Thành viên"):
    if i not in U:
        U[i]={"name":n,"cash":4899,"bank":0,"debt":0,
              "vip":0,"dd":0,"rate":RATE,"bad":0}
    return U[i]

def adm(c): return c.author.guild_permissions.administrator

async def blocked(c):
    u=user(c.author.id,c.author.name)
    if u["debt"]>0:
        await c.send(f"🚫 Bạn đang nợ **{M(u['debt'])}**!")
        return True
    return False

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("!trogiup | Casino"))
    print("ONLINE:",bot.user)

# ================= HELP =================

@bot.command(name="trogiup",aliases=["help"])
async def trogiup(c):
    await c.send(embed=E("🎰 CASINO BET88",
"""🎲 **GAME**
`!tx tai 1000` `!tx xiu 1000`
`!bc cua 1000`
`!xd chan 1000` `!xd le 1000`
`!quay 1000`
`!tuxi bao 1000` `!tuxi bua 1000` `!tuxi keo 1000`

💳 **TÀI KHOẢN**
`!vi`
`!gui 1000` `!rut 1000`
`!chuyen @User 100`
`!diemdanh` `!bxh`

💰 **VAY**
`!vay 100000` → Vay Bot
`!trabot` → Trả Bot
`!vay @User 1000` → Vay người chơi
`!trano @User` → Trả người chơi

👑 **VIP**
`!muarole Vip`

🎁 **CODE**
`!nhapcode CODE`

⚙️ **ADMIN**
`!taocode`
`!thuongcode`
`!settien`
`!resettien`
`!tyle 0-100`"""))

# ================= VI =================

@bot.command()
async def vi(c,m:discord.Member=None):
    m=m or c.author
    u=user(m.id,m.name)
    vip=u["vip"]
    ten=f"🟡 **{m.name}**" if vip else f"👤 **{m.name}**"
    hang="👑 **Vương miện VIP**" if vip else "🐥 Người chơi Thường"
    await c.send(embed=E("💳 TÀI KHOẢN",
        f"{ten}\n🏷️ Hạng: {hang}\n\n"
        f"💵 Ví: `{M(u['cash'])}`\n"
        f"🏦 Bank: `{M(u['bank'])}`\n"
        f"💸 Nợ: `{M(u['debt'])}`\n"
        f"🎯 Tỷ lệ thắng: `{u['rate']}%`\n\n"
        "✨ **Chúc bạn may mắn!**",
        GOLD if vip else BLUE))

# ================= MONEY =================

@bot.command()
async def gui(c,n:int=None):
    u=user(c.author.id,c.author.name)
    if not n or n<=0:return await c.send("❌ `!gui 1000`")
    if u["cash"]<n:return await c.send("❌ Không đủ tiền!")
    u["cash"]-=n;u["bank"]+=n
    await c.send(f"🏦 Gửi `{M(n)}` thành công!")

@bot.command()
async def rut(c,n:int=None):
    u=user(c.author.id,c.author.name)
    if not n or n<=0:return await c.send("❌ `!rut 1000`")
    if u["bank"]<n:return await c.send("❌ Bank không đủ!")
    u["bank"]-=n;u["cash"]+=n
    await c.send(f"🏦 Rút `{M(n)}` thành công!")

@bot.command()
async def chuyen(c,m:discord.Member=None,n:int=None):
    if not m or not n or n<=0:return await c.send("❌ `!chuyen @User 100`")
    if m.id==c.author.id:return await c.send("❌ Không thể chuyển cho chính mình!")
    a,b=user(c.author.id,c.author.name),user(m.id,m.name)
    if a["cash"]<n:return await c.send("❌ Không đủ tiền!")
    a["cash"]-=n;b["cash"]+=n
    await c.send(f"💸 {c.author.mention} → {m.mention}: `{M(n)}`")

# ================= DIEM DANH =================

@bot.command()
async def diemdanh(c):
    u=user(c.author.id,c.author.name)
    wait=43200-(time.time()-u["dd"])
    if wait>0:
        await c.send(
            f"⌛ **Mày đã điểm danh rồi!**\n"
            f"🕐 Đợi thêm **{int(wait):,} giây** nữa.")
        return
    u["dd"]=time.time();u["cash"]+=2593
    await c.send(embed=E("🎁 ĐIỂM DANH",
        "💰 **+2,593$ vào ví**",GREEN))

# ================= BXH =================

@bot.command()
async def bxh(c):
    x=sorted(U.values(),key=lambda z:z["cash"]+z["bank"],reverse=True)[:5]
    s="\n".join(f"**{i}.** {u['name']} — `{M(u['cash']+u['bank'])}`"
                for i,u in enumerate(x,1))
    await c.send(embed=E("🏆 TOP 5",s or "Chưa có dữ liệu"))

# ================= TX =================

@bot.command()
async def tx(c,ch=None,bet:int=None):
    if await blocked(c):return
    if ch not in ("tai","xiu") or not bet or bet<=0:
        return await c.send("❌ `!tx tai 1000`")
    if bet>10_000_000:
        return await c.send("❌ Max **10,000,000$/ván**!")
    u=user(c.author.id,c.author.name);i=c.author.id
    if u["cash"]<bet:return await c.send("❌ Không đủ tiền!")
    if i in TX["bets"]:return await c.send("❌ Bạn đã cược ván này!")

    if not TX["on"]:
        TX.update(on=1,bets={},tai=0,xiu=0)
        TX["msg"]=await c.send(embed=E(
            "🎲 **SÒNG TÀI XỈU 30S** 🎲",
            "💰 **Cược tối đa: 10,000,000$/ván**\n\n"
            "⏱️ **Thời gian: 30 giây**\n\n"
            "💵 Tài: `0$` | Xỉu: `0$`",ORANGE))
        asyncio.create_task(txround())

    u["cash"]-=bet
    TX["bets"][i]={"name":c.author.name,"choice":ch,"amount":bet}
    TX[ch]+=bet

    await TX["msg"].edit(embed=E(
        "🎲 **SÒNG TÀI XỈU 30S** 🎲",
        "💰 **Cược tối đa: 10,000,000$/ván**\n\n"
        "⏱️ **Đang nhận cược...**\n\n"
        f"💵 Tài: `{M(TX['tai'])}` | Xỉu: `{M(TX['xiu'])}`",
        ORANGE))
    try:await c.message.delete()
    except:pass

async def txround():
    await asyncio.sleep(30)
    d=[random.randint(1,6) for _ in range(3)]
    total=sum(d);result="tai" if total>=11 else "xiu"
    w=[];l=[]

    for i,b in TX["bets"].items():
        u=user(i)
        win=b["choice"]==result and random.randint(1,100)<=u["rate"]
        if win:
            p=b["amount"]*2
            if u["vip"]:p=int(p*1.5)
            u["cash"]+=p
            w.append(f"• {b['name']} `+{M(p)}`")
        else:l.append(f"• {b['name']} `-{M(b['amount'])}`")

    await TX["msg"].edit(embed=E(
        "🎲 **KẾT QUẢ TÀI XỈU**",
        f"`[ {d[0]} ] - [ {d[1]} ] - [ {d[2]} ]`\n\n"
        f"➡️ **{total} ĐIỂM — {result.upper()}**\n\n"
        f"🎉 **THẮNG**\n{chr(10).join(w) or 'Không có'}\n\n"
        f"💸 **THUA**\n{chr(10).join(l) or 'Không có'}",
        GREEN if w else RED))
    TX.update(on=0,bets={},tai=0,xiu=0,msg=None)

# ================= BC =================

@bot.command()
async def bc(c,ch=None,bet:int=None):
    if await blocked(c):return
    a={"ca":"🐟","tom":"🦐","cua":"🦀","bau":"🍐","ga":"🐓","nai":"🦌"}
    if ch not in a or not bet or bet<=0:
        return await c.send("❌ `!bc cua 1000`")
    u=user(c.author.id,c.author.name)
    if u["cash"]<bet:return await c.send("❌ Không đủ tiền!")
    u["cash"]-=bet

    m=await c.send(embed=E("🦀 **BẦU CUA**",
        "🎲 **LẮC... LẮC... LẮC...**",ORANGE))
    await asyncio.sleep(1)

    await m.edit(embed=E("🦀 **BẦU CUA**",
        "🥁 **HÉ BÁT...**",ORANGE))
    await asyncio.sleep(1)

    r=[random.choice(list(a)) for _ in range(3)]
    n=r.count(ch)

    if n:
        p=int(bet*(n+1)*(1.5 if u["vip"] else 1))
        u["cash"]+=p;res=f"🎉 **THẮNG +{M(p)}**";co=GREEN
    else:
        res=f"💸 **THUA -{M(bet)}**";co=RED

    await m.edit(embed=E("🦀 **BẦU CUA**",
        f"`[ {' | '.join(a[x] for x in r)} ]`\n\n"
        f"{res}\n💵 Ví: `{M(u['cash'])}`",co))

# ================= XD =================

@bot.command()
async def xd(c,ch=None,bet:int=None):
    if await blocked(c):return
    if ch not in ("chan","le") or not bet or bet<=0:
        return await c.send("❌ `!xd chan 1000`")
    u=user(c.author.id,c.author.name)
    if u["cash"]<bet:return await c.send("❌ Không đủ tiền!")
    u["cash"]-=bet

    m=await c.send(embed=E("🪙 **XÓC ĐĨA**",
        "🟠 **XÓC... XÓC... XÓC...**",ORANGE))
    await asyncio.sleep(1.2)

    n=random.randint(0,4)
    cups=["⚪"]*4
    for i in random.sample(range(4),n):cups[i]="🔴"
    r="chan" if n%2==0 else "le"
    win=r==ch and random.randint(1,100)<=u["rate"]

    if win:
        p=int(bet*2*(1.5 if u["vip"] else 1))
        u["cash"]+=p;res=f"🎉 **THẮNG +{M(p)}**";co=GREEN
    else:res=f"💸 **THUA -{M(bet)}**";co=RED

    await m.edit(embed=E("🪙 **XÓC ĐĨA**",
        f"`[ {' | '.join(cups)} ]`\n\n"
        f"🎯 **{r.upper()}**\n\n{res}\n"
        f"💵 Ví: `{M(u['cash'])}`",co))

# ================= QUAY =================

@bot.command()
async def quay(c,bet:int=None):
    if await blocked(c):return
    if not bet or bet<=0:return await c.send("❌ `!quay 1000`")
    u=user(c.author.id,c.author.name)
    if u["cash"]<bet:return await c.send("❌ Không đủ tiền!")
    u["cash"]-=bet

    m=await c.send(embed=E("🎰 **MÁY SLOT**",
        "🎰 **ĐANG QUAY...**",ORANGE))
    await asyncio.sleep(1.3)

    s=[random.choice(["🍒","🍋","🔔","⭐","💎","7️⃣"]) for _ in range(3)]
    same=max(s.count(x) for x in set(s))
    win=random.randint(1,100)<=u["rate"]

    if same==3 and win:
        p=int(bet*5*(1.5 if u["vip"] else 1))
        u["cash"]+=p;res=f"🎉 **NỔ HŨ +{M(p)}**";co=GREEN
    elif same==2 and win:
        p=int(bet*2*(1.5 if u["vip"] else 1))
        u["cash"]+=p;res=f"🎉 **THẮNG +{M(p)}**";co=GREEN
    else:res=f"💸 **THUA -{M(bet)}**";co=RED

    await m.edit(embed=E("🎰 **MÁY SLOT**",
        f"`[ {' | '.join(s)} ]`\n\n{res}\n"
        f"💵 Ví: `{M(u['cash'])}`",co))

# ================= TUXI =================

@bot.command()
async def tuxi(c,ch=None,bet:int=None):
    if await blocked(c):return
    if ch not in ("bao","bua","keo") or not bet or bet<=0:
        return await c.send("❌ `!tuxi bao 1000`")
    u=user(c.author.id,c.author.name)
    if u["cash"]<bet:return await c.send("❌ Không đủ tiền!")
    u["cash"]-=bet

    m=await c.send(embed=E("✊ **OẲN TÙ TÌ**","✊ **ĐANG CHƠI...**",ORANGE))
    await asyncio.sleep(1)

    a={"bao":"✋","bua":"✊","keo":"✌️"}
    r=random.choice(list(a))
    win=r==ch
    if win:
        p=bet*2;u["cash"]+=p
        res=f"🎉 **THẮNG +{M(p)}**";co=GREEN
    else:
        res=f"💸 **THUA -{M(bet)}**";co=RED

    await m.edit(embed=E("✊ **OẲN TÙ TÌ**",
        f"{a[ch]} VS {a[r]}\n\n{res}\n"
        f"💵 Ví: `{M(u['cash'])}`",co))

# ================= VIP =================

@bot.command()
async def muarole(c,r=None):
    if (r or "").lower()!="vip":
        return await c.send("❌ `!muarole Vip`")
    u=user(c.author.id,c.author.name)
    if u["vip"]:return await c.send("💛 Bạn đã là VIP!")
    if u["cash"]<30_000_000:return await c.send("❌ VIP giá **30,000,000$**!")

    role=discord.utils.find(lambda x:x.name.lower()=="vip",c.guild.roles)
    if not role:return await c.send("❌ Chưa có role `Vip`!")
    if role>=c.guild.me.top_role:return await c.send("❌ Kéo role Vip xuống dưới role Bot!")

    try:
        await c.author.add_roles(role)
    except:
        return await c.send("❌ Bot thiếu quyền quản lý role!")

    u["cash"]-=30_000_000;u["vip"]=1
    await c.send(embed=E("👑 **MUA VIP**",
        f"🎉 {c.author.mention} đã trở thành **👑 Vương miện VIP**!\n\n"
        "💰 Giá: `30,000,000$`\n"
        "💵 Thưởng game: **x1.5**\n"
        "🟡 Tên VIP: **Màu vàng**",GOLD))

# ================= VAY =================

@bot.command()
async def vay(c,m=None,n:int=None):
    u=user(c.author.id,c.author.name)

    # !vay 100000
    if isinstance(m,str) and m.isdigit() and n is None:
        n=int(m)
        if n<1 or n>100_000:
            return await c.send("❌ Vay Bot từ **1$ → 100,000$**!")
        if u["debt"]>0:
            return await c.send("❌ Bạn đang có khoản nợ!")
        u["cash"]+=n
        u["debt"]=n
        return await c.send(embed=E("🏦 **VAY TIỀN BOT**",
            f"💰 Nhận: **{M(n)}**\n"
            f"💸 Nợ: **{M(n)}**\n"
            "⚠️ Trả bằng `!trabot`",ORANGE))

    # !vay @User 1000
    if not isinstance(m,discord.Member) or not n or n<=0:
        return await c.send(
            "❌ `!vay 100000` → Vay Bot\n"
            "`!vay @User 1000` → Vay người chơi")

    if m.id==c.author.id:return await c.send("❌ Không vay chính mình!")
    if u["debt"]>0:return await c.send("❌ Bạn đang có khoản nợ!")

    lender=user(m.id,m.name)
    if lender["cash"]<n:return await c.send("❌ Người cho vay không đủ tiền!")

    lender["cash"]-=n
    u["cash"]+=n
    u["debt"]=n

    k=f"{c.author.id}-{m.id}-{time.time()}"
    LOANS[k]={"a":c.author.id,"b":m.id,"time":time.time(),"bad":0}
    asyncio.create_task(loan_timer(k))

    await c.send(embed=E("💰 **VAY NGƯỜI CHƠI**",
        f"👤 Người vay: {c.author.mention}\n"
        f"💰 Người cho vay: {m.mention}\n"
        f"💵 Gốc: **{M(n)}**\n"
        "📈 Lãi: **2% / 5 phút**\n"
        "⏱️ Sau 1 giờ → **Nợ xấu -5% tỷ lệ**",ORANGE))

async def loan_timer(k):
    while k in LOANS:
        await asyncio.sleep(300)
        x=LOANS.get(k)
        if not x:return
        u=user(x["a"])
        if u["debt"]<=0:
            LOANS.pop(k,None)
            return
        u["debt"]+=max(1,int(u["debt"]*.02))

        if time.time()-x["time"]>=3600 and not x["bad"]:
            x["bad"]=1
            u["bad"]=1
            u["rate"]=max(0,RATE-5)
            for g in bot.guilds:
                role=discord.utils.find(
                    lambda r:r.name.lower()=="nợ xấu",g.roles)
                mem=g.get_member(x["a"])
                if role and mem:
                    try:await mem.add_roles(role)
                    except:pass

@bot.command()
async def trabot(c):
    u=user(c.author.id,c.author.name)
    if u["debt"]<=0:return await c.send("❌ Bạn không có nợ Bot!")
    if u["cash"]<u["debt"]:return await c.send("❌ Ví không đủ tiền!")

    n=u["debt"];u["cash"]-=n;u["debt"]=0
    await c.send(embed=E("🏦 **TRẢ NỢ BOT**",
        f"💰 Đã trả: **{M(n)}**\n✅ Hết nợ!",GREEN))

@bot.command()
async def trano(c,m:discord.Member=None,n:int=None):
    if not m:return await c.send("❌ `!trano @User`")
    a=user(c.author.id,c.author.name)
    b=user(m.id,m.name)

    if a["debt"]<=0:return await c.send("❌ Bạn không có nợ!")
    if not n:n=a["debt"]
    if n!=a["debt"]:
        return await c.send(f"❌ Phải trả đủ **{M(a['debt'])}**!")
    if a["cash"]<n:return await c.send("❌ Ví không đủ tiền!")

    a["cash"]-=n;b["cash"]+=n;a["debt"]=0;a["bad"]=0
    a["rate"]=RATE

    for k in list(LOANS):
        if LOANS[k]["a"]==c.author.id:
            LOANS.pop(k,None)

    role=discord.utils.find(
        lambda r:r.name.lower()=="nợ xấu",c.guild.roles)
    if role:
        try:await c.author.remove_roles(role)
        except:pass

    await c.send(embed=E("✅ **TRẢ NỢ**",
        f"👤 Người nhận: {m.mention}\n"
        f"💰 Đã trả: **{M(n)}**\n"
        f"🎯 Tỷ lệ: **{a['rate']}%**",GREEN))

# ================= ADMIN TY LE =================

@bot.command()
async def tyle(c,n:int=None):
    global RATE
    if not adm(c):return await c.send("⛔ Chỉ Admin!")
    if n is None or n<0 or n>100:
        return await c.send("❌ `!tyle 0` đến `!tyle 100`")

    RATE=n
    for u in U.values():
        u["rate"]=max(0,n-5 if u["bad"] else n)

    await c.send(embed=E("⚙️ **TỶ LỆ THẮNG**",
        f"🎯 Hệ thống: **{n}%**\n"
        f"{'🚫 Không thể thắng' if n==0 else '✅ Đã cập nhật!'}",ORANGE))

# ================= CODE =================

def newcode():return "BET-"+secrets.token_hex(3).upper()

@bot.command()
async def nhapcode(c,x=None):
    x=(x or "").upper()
    if x not in C:return await c.send("❌ Code không tồn tại!")
    z=C[x]
    if c.author.id in z["used"] or len(z["used"])>=z["uses"]:
        return await c.send("❌ Code hết lượt!")
    z["used"].add(c.author.id)
    user(c.author.id,c.author.name)["cash"]+=z["money"]
    await c.send(f"🎁 **+{M(z['money'])} vào ví!**")

@bot.command()
async def thuongcode(c,n:int=None,uses:int=None):
    if not adm(c):return await c.send("⛔ Chỉ Admin!")
    if not n or not uses:return await c.send("❌ `!thuongcode 1000 5`")
    x=newcode();C[x]={"money":n,"uses":uses,"used":set()}
    await c.send(embed=E("🎁 **CODE THƯỞNG**",
        f"🔐 `{x}`\n💰 `{M(n)}`\n👥 `{uses}` lượt",GREEN))

@bot.command()
async def taocode(c,n:int=None,uses:int=None):
    if not adm(c):return await c.send("⛔ Chỉ Admin!")
    if not n or not uses:return await c.send("❌ `!taocode 1000 1`")
    x=newcode();C[x]={"money":n,"uses":uses,"used":set()}
    try:await c.author.send(f"🔐 `{x}` | 💰 `{M(n)}` | 👥 `{uses}`")
    except:pass
    await c.send("✅ Code đã gửi DM!")

# ================= ADMIN MONEY =================

@bot.command()
async def settien(c,m:discord.Member=None,n:int=None):
    if not adm(c):return await c.send("⛔ Chỉ Admin!")
    if not m or n is None:return await c.send("❌ `!settien @User 10000`")
    user(m.id,m.name)["cash"]=max(0,n)
    await c.send(embed=E("💰 **SET TIỀN**",
        f"👤 {m.mention}\n💵 Ví mới: **{M(n)}**",GREEN))

@bot.command()
async def resettien(c,m:discord.Member=None):
    if not adm(c):return await c.send("⛔ Chỉ Admin!")
    if not m:return await c.send("❌ `!resettien @User`")
    u=user(m.id,m.name);u["cash"]=4899;u["bank"]=0
    await c.send(embed=E("🔄 **RESET TIỀN**",
        f"👤 {m.mention}\n💵 Ví: **4,899$**\n🧹 Đã reset!",ORANGE))

# ================= TOKEN =================

token=os.getenv("TOKEN_BOT")
if token:
    bot.run(token)
else:
    print("❌ Chưa có TOKEN_BOT!")
