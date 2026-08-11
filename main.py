import os,asyncio,random,secrets,time,discord
from discord.ext import commands

I=discord.Intents.default()
I.message_content=True
bot=commands.Bot(command_prefix="!",intents=I,help_command=None)

U,C,LOANS={}, {}, {}
RATE=36
BOT_LOAN_MAX=100000
B,G,R,O,Y=0x3498DB,0x2ECC71,0xE74C3C,0xF1C40F,0xFFD700

TX={"on":0,"bets":{},"tai":0,"xiu":0,"msg":None}

def E(t,d,c=B):
    return discord.Embed(title=t,description=d,color=c)

def user(i,n="Người chơi"):
    if i not in U:
        U[i]={"name":n,"cash":4899,"bank":0,"debt":0,
              "vip":0,"dd":0,"rate":RATE,"bad":0}
    U[i]["name"]=n
    return U[i]

def money(n): return f"{int(n):,}$"
def adm(c): return c.author.guild_permissions.administrator

async def blocked(c):
    u=user(c.author.id,c.author.name)
    if u["debt"]>0:
        await c.send(f"🚫 **Bạn đang nợ {money(u['debt'])}!**\n💡 Hãy trả nợ trước.")
        return True
    return False

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("!trogiup • Casino"))
    print("ONLINE:",bot.user)

# ===== HELP =====

@bot.command(name="trogiup",aliases=["help"])
async def help(c):
    await c.send(embed=E("🎰 CASINO BET88",
"""🎲 **TRÒ CHƠI**
`!tx tai 1000` • `!tx xiu 1000`
`!bc cua 1000`
`!xd chan 1000`
`!quay 1000`
`!tuxi bao 1000`

💳 **TÀI CHÍNH**
`!vi`
`!gui 1000`
`!rut 1000`
`!chuyen @User 1000`
`!vay 100000`
`!vay @User 1000`
`!trano @User 1000`

🎁 **KHÁC**
`!diemdanh`
`!bxh`
`!muarole Vip`
`!nhapcode CODE`

👑 **ADMIN**
`!settien @User 10000`
`!resettien @User`
`!tyle 36`
`!taocode 1000 5`
`!thuongcode 1000 5`"""))

# ===== VI =====

@bot.command()
async def vi(c,m:discord.Member=None):
    m=m or c.author
    u=user(m.id,m.name)
    hang="👑 **Vương miện VIP**" if u["vip"] else "👤 Người chơi Thường"
    await c.send(embed=E(
        f"💳 TÀI KHOẢN: {m.name.upper()}",
        f"""🏷️ **Hạng**
{hang}

💵 **Tiền mặt**
`{money(u["cash"])}`

🏦 **Két sắt**
`{money(u["bank"])}`

💸 **Nợ**
`{money(u["debt"])}`

🎯 **Tỷ lệ thắng**
`{u["rate"]}%`

✨ Chúc bạn may mắn!""",
        Y if u["vip"] else B))

# ===== BANK =====

@bot.command()
async def gui(c,n:int=None):
    u=user(c.author.id,c.author.name)
    if not n or n<=0:return await c.send("❌ `!gui 1000`")
    if u["cash"]<n:return await c.send("❌ Tiền mặt không đủ!")
    u["cash"]-=n;u["bank"]+=n
    await c.send(f"🏦 **GỬI TIỀN**\n💵 +`{money(n)}` vào két sắt.")

@bot.command()
async def rut(c,n:int=None):
    u=user(c.author.id,c.author.name)
    if not n or n<=0:return await c.send("❌ `!rut 1000`")
    if u["bank"]<n:return await c.send("❌ Két sắt không đủ!")
    u["bank"]-=n;u["cash"]+=n
    await c.send(f"🏦 **RÚT TIỀN**\n💵 +`{money(n)}` vào tiền mặt.")

@bot.command()
async def chuyen(c,m:discord.Member=None,n:int=None):
    if not m or not n or n<=0:return await c.send("❌ `!chuyen @User 1000`")
    if m.id==c.author.id:return await c.send("❌ Không thể chuyển cho chính mình!")
    a=user(c.author.id,c.author.name);b=user(m.id,m.name)
    if a["cash"]<n:return await c.send("❌ Không đủ tiền!")
    a["cash"]-=n;b["cash"]+=n
    await c.send(embed=E("💸 CHUYỂN TIỀN",
        f"{c.author.mention} ➜ {m.mention}\n💰 `{money(n)}`",G))

# ===== DIEM DANH / BXH =====

@bot.command()
async def diemdanh(c):
    u=user(c.author.id,c.author.name)
    w=43200-(time.time()-u["dd"])
    if w>0:return await c.send(f"⌛ Đã điểm danh! Còn **{int(w):,} giây**.")
    u["dd"]=time.time();u["cash"]+=2593
    await c.send(embed=E("🎁 ĐIỂM DANH","💰 **+2,593$** vào tiền mặt!",G))

@bot.command()
async def bxh(c):
    x=sorted(U.values(),key=lambda z:z["cash"]+z["bank"],reverse=True)[:5]
    s="\n".join(f"**{i}.** {z['name']} — `{money(z['cash']+z['bank'])}`"
                for i,z in enumerate(x,1))
    await c.send(embed=E("🏆 TOP 5",s or "Chưa có dữ liệu."))

# ===== TX =====

@bot.command()
async def tx(c,ch=None,bet:int=None):
    if await blocked(c):return
    if ch not in ("tai","xiu") or not bet or bet<=0:
        return await c.send("❌ `!tx tai 1000` hoặc `!tx xiu 1000`")
    if bet>10000000:return await c.send("❌ Tối đa **10,000,000$/ván**!")
    u=user(c.author.id,c.author.name);i=c.author.id
    if u["cash"]<bet:return await c.send("❌ Không đủ tiền!")
    if i in TX["bets"]:return await c.send("❌ Bạn đã cược ván này!")

    if not TX["on"]:
        TX.update(on=1,bets={},tai=0,xiu=0)
        TX["msg"]=await c.send(embed=E(
            "🎲 🎲 SÒNG TÀI XỈU 🎲 🎲",
            "⏱️ **30 GIÂY**\n\n"
            "🎯 Cược: `!tx tai/xiu số_tiền`\n\n"
            "🔵 **TÀI:** `0$`\n"
            "🔴 **XỈU:** `0$`",O))
        asyncio.create_task(txround())

    u["cash"]-=bet
    TX["bets"][i]={"name":c.author.name,"choice":ch,"amount":bet}
    TX[ch]+=bet

    await TX["msg"].edit(embed=E(
        "🎲 🎲 SÒNG TÀI XỈU 🎲 🎲",
        "⏱️ **ĐANG NHẬN CƯỢC...**\n\n"
        f"🔵 **TÀI:** `{money(TX['tai'])}`\n"
        f"🔴 **XỈU:** `{money(TX['xiu'])}`",O))
    try:await c.message.delete()
    except:pass

async def txround():
    await asyncio.sleep(30)
    d=[random.randint(1,6) for _ in range(3)]
    total=sum(d);res="tai" if total>=11 else "xiu"
    win=[];lose=[]
    for i,b in TX["bets"].items():
        u=user(i)
        ok=random.randint(1,100)<=u["rate"]
        if b["choice"]==res and ok:
            p=b["amount"]*2
            if u["vip"]:p=int(p*1.5)
            u["cash"]+=p
            win.append(f"• {b['name']} `+{money(p)}`")
        else:lose.append(f"• {b['name']} `-{money(b['amount'])}`")

    await TX["msg"].edit(embed=E(
        "🎲 KẾT QUẢ TÀI XỈU",
        f"🎲 **[ {d[0]} ] [ {d[1]} ] [ {d[2]} ]**\n\n"
        f"💥 **{total} ĐIỂM — {res.upper()}**\n\n"
        f"🎉 **THẮNG**\n{chr(10).join(win) or 'Không có'}\n\n"
        f"💸 **THUA**\n{chr(10).join(lose) or 'Không có'}",
        G if win else R))
    TX.update(on=0,bets={},tai=0,xiu=0,msg=None)

# ===== BC =====

@bot.command()
async def bc(c,ch=None,bet:int=None):
    if await blocked(c):return
    a={"ca":"🐟","tom":"🦐","cua":"🦀","bau":"🍐","ga":"🐓","nai":"🦌"}
    if ch not in a or not bet or bet<=0:return await c.send("❌ `!bc cua 1000`")
    u=user(c.author.id,c.author.name)
    if u["cash"]<bet:return await c.send("❌ Không đủ tiền!")
    u["cash"]-=bet

    m=await c.send(embed=E("🦀 🎲 BẦU CUA 🎲",
        "\n# 🦀\n# **LẮC... LẮC... LẮC...**",O))
    await asyncio.sleep(1.2)

    await m.edit(embed=E("🦀 🎲 BẦU CUA 🎲",
        "\n# 🥁\n# **HÉ BÁT...**",O))
    await asyncio.sleep(.8)

    r=[random.choice(list(a)) for _ in range(3)]
    n=r.count(ch)
    if n:
        p=bet*(n+1)*(3//2 if u["vip"] else 1)
        u["cash"]+=p;txt=f"🎉 **THẮNG +{money(p)}**";co=G
    else:txt=f"💸 **THUA -{money(bet)}**";co=R

    await m.edit(embed=E("🦀 🎲 BẦU CUA 🎲",
        f"# {' '.join(a[x] for x in r)}\n\n{txt}\n\n💵 Ví: `{money(u['cash'])}`",co))

# ===== XD =====

@bot.command()
async def xd(c,ch=None,bet:int=None):
    if await blocked(c):return
    if ch not in ("chan","le") or not bet or bet<=0:
        return await c.send("❌ `!xd chan 1000` hoặc `!xd le 1000`")
    u=user(c.author.id,c.author.name)
    if u["cash"]<bet:return await c.send("❌ Không đủ tiền!")
    u["cash"]-=bet

    m=await c.send(embed=E("🪙 🎲 XÓC ĐĨA 🎲",
        "\n# 🪙\n# **XÓC... XÓC... XÓC...**",O))
    await asyncio.sleep(1.2)

    await m.edit(embed=E("🪙 🎲 XÓC ĐĨA 🎲",
        "\n# 🥁\n# **MỞ ĐĨA...**",O))
    await asyncio.sleep(.8)

    n=random.randint(0,4)
    r="chan" if n%2==0 else "le"
    cups=["⚪"]*4
    for i in random.sample(range(4),n):cups[i]="🔴"
    win=r==ch and random.randint(1,100)<=u["rate"]

    if win:
        p=bet*2*(3//2 if u["vip"] else 1);u["cash"]+=p
        txt=f"🎉 **THẮNG +{money(p)}**";co=G
    else:txt=f"💸 **THUA -{money(bet)}**";co=R

    await m.edit(embed=E("🪙 🎲 XÓC ĐĨA 🎲",
        f"# {' '.join(cups)}\n\n🎯 **{r.upper()}**\n\n{txt}\n💵 Ví: `{money(u['cash'])}`",co))

# ===== QUAY =====

@bot.command()
async def quay(c,bet:int=None):
    if await blocked(c):return
    if not bet or bet<=0:return await c.send("❌ `!quay 1000`")
    u=user(c.author.id,c.author.name)
    if u["cash"]<bet:return await c.send("❌ Không đủ tiền!")
    u["cash"]-=bet

    m=await c.send(embed=E("🎰 🎰 MÁY SLOT 🎰 🎰",
        "\n# 🎰\n# **QUAY... QUAY... QUAY...**",O))
    await asyncio.sleep(1.3)

    s=[random.choice(["🍒","🍋","🔔","⭐","💎","7️⃣"]) for _ in range(3)]
    same=max(s.count(x) for x in set(s))
    win=random.randint(1,100)<=u["rate"]

    if same==3 and win:
        p=bet*5*(3//2 if u["vip"] else 1);u["cash"]+=p
        txt=f"🎉 **NỔ HŨ +{money(p)}**";co=G
    elif same==2 and win:
        p=bet*2*(3//2 if u["vip"] else 1);u["cash"]+=p
        txt=f"🎉 **THẮNG +{money(p)}**";co=G
    else:txt=f"💸 **THUA -{money(bet)}**";co=R

    await m.edit(embed=E("🎰 🎰 MÁY SLOT 🎰 🎰",
        f"# {' '.join(s)}\n\n{txt}\n💵 Ví: `{money(u['cash'])}`",co))

# ===== TUXI =====

@bot.command()
async def tuxi(c,ch=None,bet:int=None):
    if await blocked(c):return
    if ch not in ("bao","bua","keo") or not bet or bet<=0:
        return await c.send("❌ `!tuxi bao 1000` • `!tuxi bua 1000` • `!tuxi keo 1000`")
    u=user(c.author.id,c.author.name)
    if u["cash"]<bet:return await c.send("❌ Không đủ tiền!")

    icon={"bao":"🖐️","bua":"✊","keo":"✌️"}
    botc=random.choice(list(icon))
    u["cash"]-=bet

    m=await c.send(embed=E("✊ ⚔️ KÉO BÚA BAO ⚔️",
        f"👤 **Bạn:** ❔\n\n🤖 **Bot:** ❔",O))
    await asyncio.sleep(1)

    if ch==botc:result="draw"
    elif (ch,botc) in [("bao","bua"),("bua","keo"),("keo","bao")]:result="win"
    else:result="lose"

    if result=="win":
        u["cash"]+=bet*2;txt=f"🎉 **BẠN THẮNG +{money(bet)}**";co=G
    elif result=="draw":
        u["cash"]+=bet;txt="🤝 **HÒA — hoàn tiền**";co=O
    else:txt=f"💸 **BẠN THUA -{money(bet)}**";co=R

    await m.edit(embed=E("✊ ⚔️ KÉO BÚA BAO ⚔️",
        f"👤 **Bạn:** {icon[ch]}\n\n🤖 **Bot:** {icon[botc]}\n\n{txt}\n💵 Ví: `{money(u['cash'])}`",co))

# ===== VAY BOT / VAY NGƯỜI =====

@bot.command()
async def vay(c,m=None,n:int=None):
    u=user(c.author.id,c.author.name)

    # !vay 100000
    if m and str(m).isdigit() and n is None:
        n=int(m)
        if u["debt"]>0:return await c.send("❌ Bạn đang có khoản nợ!")
        if n<1 or n>BOT_LOAN_MAX:
            return await c.send("❌ Bot chỉ cho vay **1 - 100,000$**.")
        u["cash"]+=n;u["debt"]=n
        await c.send(embed=E("🏦 KHOẢN VAY BOT",
            f"💰 Nhận: `{money(n)}`\n"
            f"💸 Nợ: `{money(n)}`\n"
            f"⏱️ Hạn: **1 giờ**\n"
            f"⚠️ Quá hạn → Nợ xấu -5%",O))
        return

    # !vay @user 1000
    if not isinstance(m,discord.Member) or not n or n<=0:
        return await c.send("❌ `!vay 100000` hoặc `!vay @User 1000`")

    if m.id==c.author.id:return await c.send("❌ Không thể vay chính mình!")
    lender=user(m.id,m.name)
    if u["debt"]>0:return await c.send("❌ Bạn đang có khoản nợ!")
    if lender["cash"]<n:return await c.send("❌ Người cho vay không đủ tiền!")

    lender["cash"]-=n;u["cash"]+=n
    u["debt"]=n

    lid=str(c.author.id)+"_"+str(time.time())
    LOANS[lid]={"b":c.author.id,"l":m.id,"amount":n,"bad":0}
    asyncio.create_task(loan_timer(lid))

    await c.send(embed=E("💰 VAY NGƯỜI CHƠI",
        f"👤 **Người vay:** {c.author.mention}\n"
        f"💰 **Cho vay:** {m.mention}\n"
        f"💵 **Gốc:** `{money(n)}`\n"
        f"📈 **Lãi:** 2% / 5 phút\n"
        f"⏱️ **Quá 1 giờ:** Nợ xấu -5%",O))

async def loan_timer(lid):
    for _ in range(12):
        await asyncio.sleep(300)
        x=LOANS.get(lid)
        if not x:return
        b=user(x["b"])
        if b["debt"]<=0:
            LOANS.pop(lid,None);return
        b["debt"]=int(b["debt"]*1.02)

    x=LOANS.get(lid)
    if not x:return
    b=user(x["b"]);b["bad"]=1;b["rate"]=max(0,b["rate"]-5)

@bot.command()
async def trano(c,m:discord.Member=None,n:int=None):
    if not m or not n or n<=0:return await c.send("❌ `!trano @User 1000`")
    b=user(c.author.id,c.author.name);l=user(m.id,m.name)

    if b["debt"]<=0:return await c.send("❌ Bạn không có nợ!")
    if b["cash"]<n:return await c.send("❌ Tiền mặt không đủ!")
    if n<b["debt"]:return await c.send(f"❌ Cần trả đủ `{money(b['debt'])}`!")

    b["cash"]-=n;l["cash"]+=n;b["debt"]=0

    if b["bad"]:
        b["rate"]=min(RATE,b["rate"]+5);b["bad"]=0

    for k in list(LOANS):
        if LOANS[k]["b"]==c.author.id:LOANS.pop(k)

    role=discord.utils.find(lambda x:x.name.lower()=="nợ xấu",c.guild.roles)
    if role and role in c.author.roles:
        try:await c.author.remove_roles(role)
        except:pass

    await c.send(embed=E("✅ TRẢ NỢ",
        f"💰 Đã trả: `{money(n)}`\n"
        f"🎯 Tỷ lệ hiện tại: **{b['rate']}%**",G))

# ===== CODE =====

def newcode():return "BET-"+secrets.token_hex(3).upper()

@bot.command()
async def taocode(c,n:int=None,uses:int=None):
    if not adm(c):return await c.send("⛔ Chỉ Admin!")
    if not n or not uses:return await c.send("❌ `!taocode 1000 5`")
    x=newcode();C[x]={"money":n,"uses":uses,"used":set()}
    await c.send(embed=E("🎁 TẠO CODE",
        f"🔐 `{x}`\n💰 `{money(n)}`\n👥 {uses} lượt",G))

@bot.command()
async def thuongcode(c,n:int=None,uses:int=None):
    if not adm(c):return await c.send("⛔ Chỉ Admin!")
    if not n or not uses:return await c.send("❌ `!thuongcode 1000 5`")
    x=newcode();C[x]={"money":n,"uses":uses,"used":set()}
    await c.send(embed=E("🎁 CODE THƯỞNG",
        f"🔐 `{x}`\n💰 `{money(n)}`\n👥 {uses} lượt",G))

@bot.command()
async def nhapcode(c,x=None):
    x=(x or "").upper()
    if x not in C:return await c.send("❌ Code không tồn tại!")
    z=C[x]
    if c.author.id in z["used"] or len(z["used"])>=z["uses"]:
        return await c.send("❌ Code hết lượt!")
    z["used"].add(c.author.id);user(c.author.id,c.author.name)["cash"]+=z["money"]
    await c.send(f"🎁 **+{money(z['money'])}** vào tiền mặt!")

# ===== ADMIN =====

@bot.command()
async def settien(c,m:discord.Member=None,n:int=None):
    if not adm(c):return await c.send("⛔ Chỉ Admin!")
    if not m or n is None:return await c.send("❌ `!settien @User 10000`")
    user(m.id,m.name)["cash"]=max(0,n)
    await c.send(embed=E("💰 SET TIỀN",
        f"👤 {m.mention}\n💵 Tiền mặt mới: `{money(n)}`",G))

@bot.command()
async def resettien(c,m:discord.Member=None):
    if not adm(c):return await c.send("⛔ Chỉ Admin!")
    if not m:return await c.send("❌ `!resettien @User`")
    u=user(m.id,m.name);u.update(cash=4899,bank=0,debt=0,rate=RATE,bad=0)
    await c.send(embed=E("🔄 RESET TÀI KHOẢN",
        f"👤 {m.mention}\n💵 Ví: `4,899$`\n🏦 Bank: `0$`\n🎯 Tỷ lệ: `{RATE}%`",O))

@bot.command()
async def tyle(c,n:int=None):
    global RATE
    if not adm(c):return await c.send("⛔ Chỉ Admin!")
    if n is None or not 0<=n<=100:return await c.send("❌ `!tyle 0-100`")
    RATE=n
    for u in U.values():
        u["rate"]=max(0,n-(5 if u["bad"] else 0))
    await c.send(embed=E("⚙️ TỶ LỆ SERVER",
        f"🎯 Tỷ lệ server: **{n}%**\n👥 Người chơi mới cũng nhận **{n}%**",O))

# ===== VIP =====

@bot.command()
async def muarole(c,r=None):
    if (r or "").lower()!="vip":return await c.send("❌ `!muarole Vip`")
    u=user(c.author.id,c.author.name)
    if u["vip"]:return await c.send("💛 Bạn đã là VIP!")
    if u["cash"]<30000000:return await c.send("❌ VIP giá **30,000,000$**!")
    role=discord.utils.find(lambda x:x.name.lower()=="vip",c.guild.roles)
    if not role:return await c.send("❌ Chưa có role `Vip`!")
    if role>=c.guild.me.top_role:return await c.send("❌ Kéo role Vip xuống dưới Bot!")
    u["cash"]-=30000000;u["vip"]=1
    try:await c.author.add_roles(role)
    except:return await c.send("❌ Bot thiếu quyền quản lý role!")
    await c.send(embed=E("👑 VIP",
        f"🎉 {c.author.mention} đã lên **Vương miện VIP**!\n\n"
        f"💰 Giá: `30,000,000$`\n"
        f"✨ Thưởng game: **x1.5**",Y))

# ===== TOKEN =====

token=os.getenv("TOKEN_BOT")
if token:bot.run(token)
else:print("❌ Chưa có TOKEN_BOT!")
