import os,random,time,asyncio,discord
from discord.ext import commands

I=discord.Intents.default()
I.message_content=True
bot=commands.Bot(command_prefix="!",intents=I,help_command=None)

U={};P={};RATE=36
B={"cua":"🦀","tom":"🦐","ca":"🐟","bau":"🍐","ga":"🐓","nai":"🦌"}
S=["🍒","🍋","🔔","⭐","💎","7️⃣"]
TX={"on":False,"bets":{},"tai":0,"xiu":0,"msg":None}

def u(i,n="Người chơi"):
    if i not in U:
        U[i]={"name":n,"cash":4899,"bank":0,"debt":0,"rate":36,
              "loan":None,"loan_time":0,"bad":False}
    return U[i]

def fm(n): return f"{int(n):,}$"

def em(t,d,c=0x3498DB):
    return discord.Embed(title=t,description=d,color=c)

def admin(c): return c.author.guild_permissions.administrator

def blocked(x):
    return False

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("!trogiup | Casino"))
    print("BOT ONLINE:",bot.user)

@bot.command(aliases=["help"])
async def trogiup(c):
    await c.send(embed=em("🎰 CASINO",
"""🎲 `!tx tai 1000` / `!tx xiu 1000`
🦀 `!bc cua 1000`
🎰 `!quay 1000`
🪙 `!xd chan 1000`
✂️ `!tuxi bao 1000`

💳 `!vi`  `!gui 1000`  `!rut 1000`
💸 `!chuyen @user 1000`
🎁 `!diemdanh`

💰 `!vay 50000` → BOT
🤝 `!vay @user 50000` → Người chơi
✅ `!okchovay`  ❌ `!khongchovay`
💵 `!trano 50000`
💵 `!trano @user 50000`

👑 Admin: `!settien` `!resettien` `!tyle`"""))

@bot.command()
async def vi(c,m:discord.Member=None):
    m=m or c.author;x=u(m.id,m.name)
    hang="👑 Vương miện VIP" if x.get("vip") else "👤 Người chơi Thường"
    await c.send(embed=em("💳 TÀI KHOẢN",
f"""👤 **{m.name}**

🏷️ Hạng: **{hang}**
💵 Tiền mặt: `{fm(x["cash"])}`
🏦 Két sắt: `{fm(x["bank"])}`
💸 Nợ: `{fm(x["debt"])}`
🎯 Tỷ lệ may mắn: **{x["rate"]:.1f}%**
{"⚠️ **Nợ xấu**" if x["bad"] else ""}""",0xFFD700))

@bot.command()
async def gui(c,n:int=None):
    x=u(c.author.id,c.author.name)
    if not n or n<=0:return await c.send("❌ `!gui 1000`")
    if x["cash"]<n:return await c.send("❌ Không đủ tiền!")
    x["cash"]-=n;x["bank"]+=n
    await c.send(f"🏦 Đã gửi **{fm(n)}** vào két.")

@bot.command()
async def rut(c,n:int=None):
    x=u(c.author.id,c.author.name)
    if not n or n<=0:return await c.send("❌ `!rut 1000`")
    if x["bank"]<n:return await c.send("❌ Két không đủ tiền!")
    x["bank"]-=n;x["cash"]+=n
    await c.send(f"🏦 Đã rút **{fm(n)}**.")

@bot.command()
async def chuyen(c,m:discord.Member=None,n:int=None):
    if not m or not n or n<=0:return await c.send("❌ `!chuyen @user 1000`")
    a=u(c.author.id,c.author.name);b=u(m.id,m.name)
    if a["cash"]<n:return await c.send("❌ Không đủ tiền!")
    a["cash"]-=n;b["cash"]+=n
    await c.send(f"✅ {c.author.mention} → {m.mention}: **{fm(n)}**")

@bot.command()
async def diemdanh(c):
    x=u(c.author.id,c.author.name);now=time.time()
    if now-x.get("dd",0)<43200:return await c.send("⏳ Đã điểm danh rồi!")
    x["dd"]=now;x["cash"]+=2593
    await c.send(embed=em("🎁 ĐIỂM DANH","💰 **+2,593$ vào ví**",0x2ECC71))

# ===== TÀI XỈU =====

@bot.command()
async def tx(c,ch=None,n:int=None):
    if ch not in ("tai","xiu") or not n or n<=0:
        return await c.send("❌ `!tx tai 1000`")
    if n>10000000:return await c.send("❌ Tối đa **10,000,000$/ván**!")
    x=u(c.author.id,c.author.name);i=c.author.id
    if x["cash"]<n:return await c.send("❌ Không đủ tiền!")
    if i in TX["bets"]:return await c.send("❌ Bạn đã cược rồi!")

    if not TX["on"]:
        TX.update(on=True,bets={},tai=0,xiu=0)
        TX["msg"]=await c.send(embed=em("🎲 SÒNG TÀI XỈU 30S 🎲",
"""Gõ `!tx <tai/xiu> <tiền>`
💰 **Tối đa 10,000,000$/ván**

⏱️ **Thời gian: 30 giây**

💵 Tổng Tài: `0$` | Tổng Xỉu: `0$`""",0xFFD700))
        asyncio.create_task(txround())

    x["cash"]-=n
    TX["bets"][i]={"name":c.author.name,"choice":ch,"amount":n}
    TX[ch]+=n

    await TX["msg"].edit(embed=em("🎲 SÒNG TÀI XỈU 30S 🎲",
f"""Gõ `!tx <tai/xiu> <tiền>`
💰 **Tối đa 10,000,000$/ván**

⏱️ **Đang nhận cược...**

💵 Tổng Tài: `{fm(TX["tai"])}` | Tổng Xỉu: `{fm(TX["xiu"])}`""",0xFFD700))

async def txround():
    await asyncio.sleep(30)
    d=[random.randint(1,6) for _ in range(3)]
    total=sum(d);r="tai" if total>=11 else "xiu"
    w=[];l=[]
    for i,b in TX["bets"].items():
        x=u(i)
        if b["choice"]==r:
            p=b["amount"]*2
            x["cash"]+=p
            w.append(f"• {b['name']} `+{fm(p)}`")
        else:l.append(f"• {b['name']} `-{fm(b['amount'])}`")

    if TX["msg"]:
        await TX["msg"].edit(embed=em("🎲 KẾT QUẢ TÀI XỈU",
f"""🎲 Xúc xắc
`[ {d[0]} | {d[1]} | {d[2]} ]`

➡️ **{total} điểm — {r.upper()}**

🎉 **NGƯỜI THẮNG**
{chr(10).join(w) or "Không có"}

💸 **NGƯỜI THUA**
{chr(10).join(l) or "Không có"}""",0x2ECC71 if w else 0xE74C3C))
    TX.update(on=False,bets={},tai=0,xiu=0,msg=None)

# ===== BẦU CUA =====

@bot.command()
async def bc(c,ch=None,n:int=None):
    if ch not in B or not n or n<=0:return await c.send("❌ `!bc cua 1000`")
    x=u(c.author.id,c.author.name)
    if x["cash"]<n:return await c.send("❌ Không đủ tiền!")
    x["cash"]-=n

    m=await c.send(embed=em("🦀 BẦU CUA","🎲 **Đang lắc...**",0xFFD700))
    await asyncio.sleep(1)

    r=[random.choice(list(B)) for _ in range(3)]
    k=r.count(ch)

    if k:
        p=n*(k+1);x["cash"]+=p
        text=f"🎉 **THẮNG +{fm(p)} vào ví**"
        color=0x2ECC71
    else:
        text=f"💸 **THUA -{fm(n)}**"
        color=0xE74C3C

    await m.edit(embed=em("🦀 BẦU CUA",
f"""🎲 KẾT QUẢ

`[ {B[r[0]]} | {B[r[1]]} | {B[r[2]]} ]`

{text}
💵 Ví: `{fm(x["cash"])}`""",color))

# ===== SLOT =====

@bot.command()
async def quay(c,n:int=None):
    if not n or n<=0:return await c.send("❌ `!quay 1000`")
    x=u(c.author.id,c.author.name)
    if x["cash"]<n:return await c.send("❌ Không đủ tiền!")
    x["cash"]-=n

    m=await c.send(embed=em("🎰 MÁY SLOT","🎰 **Đang quay...**",0xFFD700))
    await asyncio.sleep(1)

    r=[random.choice(S) for _ in range(3)]
    same=max(r.count(z) for z in set(r))

    if same==3:
        p=n*5
    elif same==2:
        p=n*2
    else:p=0

    if p:
        x["cash"]+=p
        text=f"🎉 **THẮNG +{fm(p)} vào ví**";color=0x2ECC71
    else:
        text=f"💸 **THUA -{fm(n)}**";color=0xE74C3C

    await m.edit(embed=em("🎰 MÁY SLOT",
f"""🎲 KẾT QUẢ

`[ {r[0]} | {r[1]} | {r[2]} ]`

{text}
💵 Ví: `{fm(x["cash"])}`""",color))

# ===== XÓC ĐĨA =====

@bot.command()
async def xd(c,ch=None,n:int=None):
    if ch not in ("chan","le") or not n or n<=0:
        return await c.send("❌ `!xd chan 1000`")
    x=u(c.author.id,c.author.name)
    if x["cash"]<n:return await c.send("❌ Không đủ tiền!")
    x["cash"]-=n

    m=await c.send(embed=em("🪙 XÓC ĐĨA","🥣 **Đang xóc...**",0xFFD700))
    await asyncio.sleep(1)

    q=random.randint(0,4)
    r="chan" if q%2==0 else "le"
    balls=["🔴"]*4
    for z in random.sample(range(4),q):balls[z]="⚪"

    if r==ch:
        p=n*2;x["cash"]+=p
        text=f"🎉 **THẮNG +{fm(p)} vào ví**";color=0x2ECC71
    else:
        text=f"💸 **THUA -{fm(n)}**";color=0xE74C3C

    await m.edit(embed=em("🪙 XÓC ĐĨA",
f"""🎲 KẾT QUẢ

`[ {' | '.join(balls)} ]`

🎯 **{r.upper()}**

{text}
💵 Ví: `{fm(x["cash"])}`""",color))

# ===== TÙ XÌ =====

@bot.command()
async def tuxi(c,ch=None,n:int=None):
    if ch not in ("bao","bua","keo") or not n or n<=0:
        return await c.send("❌ `!tuxi bao 1000`")
    x=u(c.author.id,c.author.name)
    if x["cash"]<n:return await c.send("❌ Không đủ tiền!")

    botc=random.choice(["bao","bua","keo"])
    x["cash"]-=n

    if ch==botc:
        x["cash"]+=n;text="🤝 **HÒA**";color=0xF1C40F
    elif (ch,botc) in [("bao","bua"),("bua","keo"),("keo","bao")]:
        p=n*2;x["cash"]+=p
        text=f"🎉 **THẮNG +{fm(p)} vào ví**";color=0x2ECC71
    else:
        text=f"💸 **THUA -{fm(n)}**";color=0xE74C3C

    await c.send(embed=em("✊ TÙ XÌ",
f"""👤 **Bạn:** `{ch.upper()}`  ⚔️  🤖 **Bot:** `{botc.upper()}`

{text}

💵 Ví: `{fm(x["cash"])}`""",color))

# ===== VAY =====

@bot.command()
async def vay(c,m=None,n:int=None):
    x=u(c.author.id,c.author.name)

    if x["debt"]>0:return await c.send("❌ Bạn đang có khoản nợ!")

    if m and m.startswith("<@"):
        try:member=await commands.MemberConverter().convert(c,m)
        except:return await c.send("❌ Không tìm thấy người cho vay!")

        if member.id==c.author.id:return await c.send("❌ Không thể vay chính mình!")
        if not n or not 1<=n<=100000000:
            return await c.send("❌ Vay người chơi: **1–100,000,000$**")

        lender=u(member.id,member.name)
        if lender["cash"]<n:return await c.send("❌ Người cho vay không đủ tiền!")

        P[f"{c.author.id}:{member.id}"]={
            "borrow":c.author.id,"lend":member.id,"amount":n}
        await c.send(embed=em("🤝 YÊU CẦU VAY",
f"""{c.author.mention} muốn vay {member.mention}

💰 Số tiền: **{fm(n)}**

{member.mention} gõ:
✅ `!okchovay`
❌ `!khongchovay`""",0xF1C40F))
    else:
        if not n or not 1<=n<=50000:
            return await c.send("❌ Vay BOT: **1–50,000$**")

        x["cash"]+=n;x["debt"]=n;x["loan"]="bot";x["loan_time"]=time.time()
        asyncio.create_task(bot_due(c.author.id))
        await c.send(embed=em("🏦 VAY BOT",
f"""💰 Nhận: **{fm(n)}**
⏱️ Thời hạn: **1 giờ**
💸 Nợ: **{fm(n)}**""",0xF1C40F))

@bot.command()
async def okchovay(c):
    key=next((k for k,v in P.items() if v["lend"]==c.author.id),None)
    if not key:return await c.send("❌ Không có yêu cầu vay!")

    v=P.pop(key);a=u(v["borrow"]);b=u(v["lend"])
    if b["cash"]<v["amount"]:return await c.send("❌ Không đủ tiền!")

    b["cash"]-=v["amount"];a["cash"]+=v["amount"]
    a["debt"]=v["amount"];a["loan"]="player";a["lender"]=b["name"]
    a["loan_time"]=time.time()

    asyncio.create_task(player_due(v["borrow"]))
    await c.send("✅ **Đã chấp nhận khoản vay!**")

@bot.command()
async def khongchovay(c):
    for k,v in list(P.items()):
        if v["lend"]==c.author.id:
            P.pop(k)
            return await c.send("❌ Đã từ chối khoản vay.")
    await c.send("❌ Không có yêu cầu vay.")

async def bot_due(uid):
    await asyncio.sleep(3600)
    x=u(uid)
    if x["debt"]<=0:return
    take=x["cash"]//2
    x["cash"]-=take
    x["rate"]=max(0,x["rate"]-0.5)
    x["bad"]=True
    await notify(uid,f"⚠️ **BOT: khoản vay quá hạn!**\n💸 Thu 50% tiền mặt: `{fm(take)}`\n🎯 May mắn: **{x['rate']:.1f}%**")

async def player_due(uid):
    await asyncio.sleep(3600)
    x=u(uid)
    if x["debt"]<=0:return
    x["rate"]=max(0,x["rate"]-1)
    x["bad"]=True
    await notify(uid,"⚠️ **Khoản vay quá hạn!**\n🚨 Bạn đã bị **Nợ xấu**.\n🎯 May mắn giảm **1%**.\n💸 Lãi: **2% / 10 phút**")

async def notify(uid,text):
    for g in bot.guilds:
        m=g.get_member(uid)
        if m:
            role=discord.utils.find(lambda r:r.name.lower()=="nợ xấu",g.roles)
            if role:
                try: await m.add_roles(role)
                except: pass
            try: await m.send(text)
            except: pass
            return

@bot.command()
async def trano(c,m=None,n:int=None):
    x=u(c.author.id,c.author.name)
    if not n or n<=0:return await c.send("❌ `!trano 50000`")
    if x["debt"]<=0:return await c.send("❌ Bạn không có nợ!")
    if n>x["debt"]:return await c.send("❌ Trả vượt quá số nợ!")
    if x["cash"]<n:return await c.send("❌ Ví không đủ!")

    x["cash"]-=n

    if x["loan"]=="player" and m:
        try:member=await commands.MemberConverter().convert(c,m)
        except:return await c.send("❌ Không tìm thấy người nhận!")
        u(member.id,member.name)["cash"]+=n

    x["debt"]-=n

    if x["debt"]<=0:
        x["debt"]=0;x["loan"]=None;x["rate"]=RATE;x["bad"]=False
        role=discord.utils.find(lambda r:r.name.lower()=="nợ xấu",c.guild.roles)
        if role:
            try:await c.author.remove_roles(role)
            except:pass

    await c.send(embed=em("✅ TRẢ NỢ",
f"""💵 Đã trả: **{fm(n)}**
💸 Nợ còn: **{fm(x["debt"])}**
🎯 May mắn: **{x["rate"]:.1f}%**""",0x2ECC71))

# ===== ADMIN =====

@bot.command()
async def tyle(c,n:int=None):
    global RATE
    if not admin(c):return await c.send("⛔ Chỉ Admin!")
    if n is None or not 0<=n<=100:return await c.send("❌ `!tyle 36`")
    RATE=n
    for x in U.values():
        x["rate"]=n-(1 if x["bad"] and x["loan"]=="player" else 0)
        x["rate"]=max(0,x["rate"])
    await c.send(f"⚙️ Tỷ lệ server: **{n}%**")

@bot.command()
async def settien(c,m:discord.Member=None,n:int=None):
    if not admin(c):return await c.send("⛔ Chỉ Admin!")
    if not m or n is None:return await c.send("❌ `!settien @user 10000`")
    u(m.id,m.name)["cash"]=max(0,n)
    await c.send(f"💰 {m.mention} → **{fm(n)}**")

@bot.command()
async def resettien(c,m:discord.Member=None):
    if not admin(c):return await c.send("⛔ Chỉ Admin!")
    if not m:return await c.send("❌ `!resettien @user`")
    x=u(m.id,m.name)
    x.update(cash=4899,bank=0)
    await c.send(f"🔄 {m.mention} đã reset **4,899$**")

token=os.getenv("TOKEN_BOT")
if not token:
    print("❌ Chưa có TOKEN_BOT!")
else:
    bot.run(token)
