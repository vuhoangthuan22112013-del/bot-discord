import os,asyncio,random,secrets,time,discord
from discord.ext import commands

I=discord.Intents.default();I.message_content=True
bot=commands.Bot(command_prefix="!",intents=I,help_command=None)

U={};C={};LOAN={};RATE=100
TX={"on":0,"bets":{},"tai":0,"xiu":0,"msg":None}
BLUE=0x3498DB;ORANGE=0xF1C40F;GREEN=0x2ECC71;RED=0xE74C3C;GOLD=0xFFD700

def E(t,d,c=BLUE):return discord.Embed(title=t,description=d,color=c)
def money(n):return f"{int(n):,}$"
def user(i,n="Thành viên"):
    if i not in U:U[i]={"name":n,"cash":4899,"bank":0,"debt":0,"vip":0,"dd":0,"rate":RATE,"bad":0}
    return U[i]
def adm(c):return c.author.guild_permissions.administrator
async def block(c):
    if user(c.author.id,c.author.name)["debt"]>0:
        await c.send("🚫 Bạn đang có nợ! Hãy trả nợ trước.");return True
    return False

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("!trogiup | Casino"))
    print("ONLINE",bot.user)

# ===== HỆ THỐNG =====
@bot.command(name="trogiup",aliases=["help"])
async def help(c):
    await c.send(embed=E("🎰 CASINO BET88",
    "**🎰 TRÒ CHƠI**\n"
    "`!tx tai 1000` `!tx xiu 1000`\n"
    "`!bc cua 1000` `!xd chan 1000`\n"
    "`!quay 1000` `!tuxi bao 1000`\n\n"
    "**💳 HỆ THỐNG**\n"
    "`!vi` `!gui 1000` `!rut 1000`\n"
    "`!chuyen @User 100` `!diemdanh`\n"
    "`!bxh` `!nhapcode CODE` `!muarole Vip`\n\n"
    "**💰 VAY / TRẢ NỢ**\n"
    "`!vay @User 1000` `!trano @User 1000`\n\n"
    "**👑 ADMIN**\n"
    "`!taocode` `!thuongcode`\n"
    "`!settien` `!resettien` `!tyle 0-100`"))

@bot.command()
async def vi(c,m:discord.Member=None):
    m=m or c.author;u=user(m.id,m.name)
    await c.send(embed=E("💳 TÀI KHOẢN",
    f"{'🟡' if u['vip'] else '👤'} **{m.name}**\n"
    f"🏷️ Hạng: {'👑 **Vương miện VIP**' if u['vip'] else '🐥 Người chơi Thường'}\n\n"
    f"💵 Ví: `{money(u['cash'])}`\n🏦 Bank: `{money(u['bank'])}`\n"
    f"💸 Nợ: `{money(u['debt'])}`\n🎯 Tỷ lệ thắng: `{u['rate']}%`",
    GOLD if u["vip"] else BLUE))

@bot.command()
async def gui(c,n:int=None):
    u=user(c.author.id,c.author.name)
    if not n or n<=0 or u["cash"]<n:return await c.send("❌ Không đủ tiền!")
    u["cash"]-=n;u["bank"]+=n;await c.send(f"🏦 Gửi `{money(n)}` thành công!")

@bot.command()
async def rut(c,n:int=None):
    u=user(c.author.id,c.author.name)
    if not n or n<=0 or u["bank"]<n:return await c.send("❌ Bank không đủ!")
    u["bank"]-=n;u["cash"]+=n;await c.send(f"🏦 Rút `{money(n)}` thành công!")

@bot.command()
async def chuyen(c,m:discord.Member=None,n:int=None):
    if not m or not n or n<=0:return await c.send("❌ `!chuyen @User 100`")
    a,b=user(c.author.id,c.author.name),user(m.id,m.name)
    if a["cash"]<n:return await c.send("❌ Không đủ tiền!")
    a["cash"]-=n;b["cash"]+=n;await c.send(f"💸 {c.author.mention} → {m.mention}: `{money(n)}`")

@bot.command()
async def diemdanh(c):
    u=user(c.author.id,c.author.name);w=43200-(time.time()-u["dd"])
    if w>0:return await c.send(f"⌛ **Mày đã điểm danh rồi!**\n🕐 Đợi **{int(w):,} giây** nữa.")
    u["dd"]=time.time();u["cash"]+=2593
    await c.send(embed=E("🎁 ĐIỂM DANH","💰 **+2,593$ vào ví**",GREEN))

@bot.command()
async def bxh(c):
    x=sorted(U.values(),key=lambda z:z["cash"]+z["bank"],reverse=True)[:5]
    await c.send(embed=E("🏆 TOP 5","\n".join(f"**{i}.** {u['name']} — `{money(u['cash']+u['bank'])}`" for i,u in enumerate(x,1))))

# ===== TỶ LỆ =====
def win(u):
    return u["rate"]>0 and random.randint(1,100)<=u["rate"]

@bot.command()
async def tyle(c,n:int=None):
    global RATE
    if not adm(c):return await c.send("⛔ Chỉ Admin!")
    if n is None or not 0<=n<=100:return await c.send("❌ `!tyle 0` đến `!tyle 100`")
    RATE=n
    for u in U.values():u["rate"]=max(0,n-5 if u["bad"] else n)
    await c.send(f"⚙️ Tỷ lệ hệ thống: **{n}%**")

# ===== TÀI XỈU =====
@bot.command()
async def tx(c,ch=None,bet:int=None):
    if await block(c):return
    if ch not in ("tai","xiu") or not bet or bet<=0:return await c.send("❌ `!tx tai 1000`")
    if bet>10_000_000:return await c.send("❌ Max **10,000,000$/ván**!")
    u=user(c.author.id,c.author.name)
    if u["cash"]<bet:return await c.send("❌ Không đủ tiền!")
    if c.author.id in TX["bets"]:return await c.send("❌ Bạn đã cược!")
    if not TX["on"]:
        TX.update(on=1,bets={},tai=0,xiu=0)
        TX["msg"]=await c.send(embed=E("🎲 SÒNG TÀI XỈU 30S",
        "🎯 `!tx tai/xiu số tiền`\n\n⏱️ **30 giây**\n💰 **Max 10,000,000$/ván**\n\n💵 Tài: `0$` | Xỉu: `0$`",ORANGE))
        asyncio.create_task(txround())
    u["cash"]-=bet;TX["bets"][c.author.id]={"name":c.author.name,"choice":ch,"amount":bet};TX[ch]+=bet
    await TX["msg"].edit(embed=E("🎲 SÒNG TÀI XỈU 30S",
    f"⏱️ **Đang nhận cược...**\n💵 Tài: `{money(TX['tai'])}` | Xỉu: `{money(TX['xiu'])}`",ORANGE))

async def txround():
    await asyncio.sleep(30)
    d=[random.randint(1,6) for _ in range(3)];r="tai" if sum(d)>=11 else "xiu";w=[];l=[]
    for i,b in TX["bets"].items():
        u=user(i);ok=b["choice"]==r and win(u)
        if ok:
            p=int(b["amount"]*2*(1.5 if u["vip"] else 1));u["cash"]+=p;w.append(f"• {b['name']} +`{money(p)}`")
        else:l.append(f"• {b['name']} -`{money(b['amount'])}`")
    await TX["msg"].edit(embed=E("🎲 KẾT QUẢ",
    f"`[ {d[0]} | {d[1]} | {d[2]} ]` → **{sum(d)} {r.upper()}**\n\n"
    f"🎉 **THẮNG**\n{chr(10).join(w) or 'Không có'}\n\n💸 **THUA**\n{chr(10).join(l) or 'Không có'}",GREEN if w else RED))
    TX.update(on=0,bets={},tai=0,xiu=0,msg=None)

# ===== BẦU CUA =====
@bot.command()
async def bc(c,ch=None,bet:int=None):
    if await block(c):return
    A={"ca":"🐟","tom":"🦐","cua":"🦀","bau":"🍐","ga":"🐓","nai":"🦌"}
    if ch not in A or not bet or bet<=0:return await c.send("❌ `!bc cua 1000`")
    u=user(c.author.id,c.author.name)
    if u["cash"]<bet:return await c.send("❌ Không đủ tiền!")
    u["cash"]-=bet;m=await c.send(embed=E("🦀 BẦU CUA","🎲 **LẮC... LẮC... LẮC...**",ORANGE))
    await asyncio.sleep(1.2)
    await m.edit(embed=E("🦀 BẦU CUA","🥁 **HÉ BÁT...**",ORANGE));await asyncio.sleep(1)
    r=[random.choice(list(A)) for _ in range(3)]
    # hiện từng con
    for i in range(1,4):
        await m.edit(embed=E("🦀 BẦU CUA",f"`[ {' | '.join(A[x] if j<i else '❔' for j,x in enumerate(r))} ]`",ORANGE))
        await asyncio.sleep(.6)
    n=r.count(ch)
    if n:
        p=int(bet*(n+1)*(1.5 if u["vip"] else 1));u["cash"]+=p;txt=f"🎉 **THẮNG +{money(p)}**";co=GREEN
    else:txt=f"💸 **THUA -{money(bet)}**";co=RED
    await m.edit(embed=E("🦀 BẦU CUA",f"`[ {' | '.join(A[x] for x in r)} ]`\n\n{txt}\n💵 `{money(u['cash'])}`",co))

# ===== XÓC ĐĨA =====
@bot.command()
async def xd(c,ch=None,bet:int=None):
    if await block(c):return
    if ch not in ("chan","le") or not bet or bet<=0:return await c.send("❌ `!xd chan 1000`")
    u=user(c.author.id,c.author.name)
    if u["cash"]<bet:return await c.send("❌ Không đủ tiền!")
    u["cash"]-=bet;m=await c.send(embed=E("🪙 XÓC ĐĨA","🟠 **XÓC... XÓC... XÓC...**\n\n`[ ⚪ | ⚪ | ⚪ | ⚪ ]`",ORANGE))
    await asyncio.sleep(1.2);n=random.randint(0,4);cups=["⚪"]*4
    for i in random.sample(range(4),n):cups[i]="🔴"
    await m.edit(embed=E("🪙 XÓC ĐĨA","🟠 **MỞ ĐĨA...**\n\n`[ "+" | ".join(cups)+" ]`",ORANGE));await asyncio.sleep(1)
    r="chan" if n%2==0 else "le";ok=r==ch and win(u)
    if ok:p=int(bet*2*(1.5 if u["vip"] else 1));u["cash"]+=p;txt=f"🎉 **THẮNG +{money(p)}**";co=GREEN
    else:txt=f"💸 **THUA -{money(bet)}**";co=RED
    await m.edit(embed=E("🪙 XÓC ĐĨA",f"`[ {' | '.join(cups)} ]`\n🎯 **{r.upper()}**\n\n{txt}\n💵 `{money(u['cash'])}`",co))

# ===== SLOT =====
@bot.command()
async def quay(c,bet:int=None):
    if await block(c):return
    if not bet or bet<=0:return await c.send("❌ `!quay 1000`")
    u=user(c.author.id,c.author.name)
    if u["cash"]<bet:return await c.send("❌ Không đủ tiền!")
    u["cash"]-=bet;m=await c.send(embed=E("🎰 MÁY SLOT","🎰 **ĐANG QUAY...**\n\n`[ ❔ | ❔ | ❔ ]`",ORANGE))
    await asyncio.sleep(.8)
    s=[random.choice(["🍒","🍋","🔔","⭐","💎","7️⃣"]) for _ in range(3)]
    for i in range(1,4):
        await m.edit(embed=E("🎰 MÁY SLOT",f"`[ {' | '.join(s[j] if j<i else '❔' for j in range(3))} ]`",ORANGE));await asyncio.sleep(.5)
    same=max(s.count(x) for x in set(s));ok=same>=2 and win(u)
    if ok:
        p=int(bet*(5 if same==3 else 2)*(1.5 if u["vip"] else 1));u["cash"]+=p;txt=f"🎉 **THẮNG +{money(p)}**";co=GREEN
    else:txt=f"💸 **THUA -{money(bet)}**";co=RED
    await m.edit(embed=E("🎰 MÁY SLOT",f"`[ {' | '.join(s)} ]`\n\n{txt}\n💵 `{money(u['cash'])}`",co))

# ===== TÚ XÌ =====
@bot.command()
async def tuxi(c,ch=None,bet:int=None):
    if await block(c):return
    if ch not in ("bao","bua","keo") or not bet or bet<=0:return await c.send("❌ `!tuxi bao 1000`")
    u=user(c.author.id,c.author.name)
    if u["cash"]<bet:return await c.send("❌ Không đủ tiền!")
    u["cash"]-=bet;m=await c.send(embed=E("✊ TÚ XÌ","✊ **CHUẨN BỊ...**\n\n❔ vs ❔",ORANGE));await asyncio.sleep(1)
    r=random.choice(["bao","bua","keo"])
    await m.edit(embed=E("✊ TÚ XÌ","✊ **OẲN TÙ TÌ...**\n\n✊ vs ❔",ORANGE));await asyncio.sleep(1)
    winmap={"bao":"keo","bua":"bao","keo":"bua"};ok=winmap[ch]==r and win(u)
    if ok:u["cash"]+=bet*2;txt=f"🎉 **THẮNG +{money(bet*2)}**";co=GREEN
    elif ch==r:u["cash"]+=bet;txt="🤝 **HÒA!**";co=ORANGE
    else:txt=f"💸 **THUA -{money(bet)}**";co=RED
    em={"bao":"🖐️","bua":"✊","keo":"✌️"}
    await m.edit(embed=E("✊ TÚ XÌ",f"{em[ch]} **vs** {em[r]}\n\n{txt}\n💵 `{money(u['cash'])}`",co))

# ===== VIP =====
@bot.command()
async def muarole(c,r=None):
    if (r or "").lower()!="vip":return await c.send("❌ `!muarole Vip`")
    u=user(c.author.id,c.author.name)
    if u["vip"]:return await c.send("💛 Bạn đã là VIP!")
    if u["cash"]<30_000_000:return await c.send("❌ VIP giá **30,000,000$**!")
    role=discord.utils.find(lambda x:x.name.lower()=="vip",c.guild.roles)
    if not role:return await c.send("❌ Chưa có role `Vip`!")
    if role>=c.guild.me.top_role:return await c.send("❌ Kéo role Vip xuống dưới Bot!")
    u["cash"]-=30_000_000;u["vip"]=1
    await c.author.add_roles(role)
    await c.send(embed=E("👑 MUA VIP",f"🎉 {c.author.mention} **Vương miện VIP**\n💰 `30,000,000$`\n🟡 Tên VIP màu vàng",GOLD))

# ===== ADMIN CODE =====
def newcode():return "BET-"+secrets.token_hex(3).upper()

@bot.command()
async def thuongcode(c,n:int=None,uses:int=None):
    if not adm(c):return await c.send("⛔ Chỉ Admin!")
    if not n or not uses:return await c.send("❌ `!thuongcode 1000 5`")
    x=newcode();C[x]={"money":n,"uses":uses,"used":set()}
    await c.send(embed=E("🎁 CODE",f"🔐 `{x}`\n💰 `{money(n)}`\n👥 `{uses}` lượt",GREEN))

@bot.command()
async def taocode(c,n:int=None,uses:int=None):
    if not adm(c):return await c.send("⛔ Chỉ Admin!")
    if not n or not uses:return await c.send("❌ `!taocode 1000 1`")
    x=newcode();C[x]={"money":n,"uses":uses,"used":set()}
    await c.author.send(f"🔐 `{x}` | 💰 `{money(n)}` | 👥 `{uses}`")
    await c.send("✅ Code đã gửi DM!")

@bot.command()
async def nhapcode(c,x=None):
    x=(x or "").upper()
    if x not in C:return await c.send("❌ Code không tồn tại!")
    z=C[x]
    if c.author.id in z["used"] or len(z["used"])>=z["uses"]:return await c.send("❌ Code hết lượt!")
    z["used"].add(c.author.id);user(c.author.id,c.author.name)["cash"]+=z["money"]
    await c.send(f"🎁 **+{money(z['money'])} vào ví!**")

@bot.command()
async def settien(c,m:discord.Member=None,n:int=None):
    if not adm(c):return await c.send("⛔ Chỉ Admin!")
    if not m or n is None:return await c.send("❌ `!settien @User 10000`")
    user(m.id,m.name)["cash"]=max(0,n);await c.send(f"💰 {m.mention} → `{money(n)}`")

@bot.command()
async def resettien(c,m:discord.Member=None):
    if not adm(c):return await c.send("⛔ Chỉ Admin!")
    if not m:return await c.send("❌ `!resettien @User`")
    u=user(m.id,m.name);u["cash"]=4899;u["bank"]=0
    await c.send(f"🔄 {m.mention} đã reset về `{money(4899)}`")

# ===== TOKEN =====
token=os.getenv("TOKEN_BOT")
if token:bot.run(token)
else:print("❌ Chưa có TOKEN_BOT!")
