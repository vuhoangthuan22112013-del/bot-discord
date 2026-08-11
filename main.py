import os,asyncio,random,time,secrets,discord
from discord.ext import commands

I=discord.Intents.default();I.message_content=True
bot=commands.Bot(command_prefix="!",intents=I,help_command=None)
U={};C={};TX={"on":0,"bets":{},"tai":0,"xiu":0,"msg":None};P={}
RATE=36
B={"ca":"🐟","tom":"🦐","cua":"🦀","bau":"🍐","ga":"🐓","nai":"🦌"}

def u(i,n="Người chơi"):
 if i not in U:U[i]={"name":n,"cash":4899,"bank":0,"debt":0,"rate":RATE,"vip":0,"bad":0,"locked":0}
 return U[i]

def M(n):return f"{int(n):,}$"
def E(t,d,c=0x3498DB):return discord.Embed(title=t,description=d,color=c)
def A(c):return c.author.guild_permissions.administrator

async def lock(c):
 x=u(c.author.id,c.author.name)
 if x["locked"]:
  await c.send(f"🚫 **Bạn đang là Con Nợ và đã quá hạn!**\n💸 Nợ: `{M(x['debt'])}`")
  return True
 return False

@bot.event
async def on_ready():
 await bot.change_presence(activity=discord.Game("!trogiup | Casino"))
 print("ONLINE",bot.user)

@bot.command(name="trogiup",aliases=["help"])
async def help(c):
 await c.send(embed=E("🎰 CASINO BET",
"""`!tx tai 1000` / `!tx xiu 1000`
`!bc cua 1000`  `!xd chan 1000`
`!quay 1000`  `!tuxi bao 1000`

`!vi` `!gui 1000` `!rut 1000`
`!diemdanh` `!chuyen @user 1000`

🏦 `!vaybot 50000` → `!trano bot 50000`
🤝 `!vay @user 50000`
✅ `!okchovay` / `!khongchovay`
💵 `!trano @user 50000`

👑 ADMIN:
`!taocode` `!thuongcode`
`!nhapcode CODE`
`!tyle` `!settien` `!resettien`"""))

@bot.command()
async def vi(c,m:discord.Member=None):
 m=m or c.author;x=u(m.id,m.name)
 await c.send(embed=E("💳 TÀI KHOẢN",
f"👤 **{'🟡 '+m.name if x['vip'] else m.name}**\n"
f"🏷️ Hạng: {'👑 Vương miện VIP' if x['vip'] else 'Người chơi Thường'}\n"
f"💵 Ví: `{M(x['cash'])}`\n"
f"🏦 Két: `{M(x['bank'])}`\n"
f"💸 Nợ: `{M(x['debt'])}`\n"
f"🎯 Tỷ lệ may mắn: **{x['rate']:.1f}%**",
0xFFD700 if x["vip"] else 0x3498DB))

@bot.command()
async def gui(c,n:int=None):
 x=u(c.author.id,c.author.name)
 if not n or n<=0:return await c.send("❌ `!gui 1000`")
 if x["cash"]<n:return await c.send("❌ Không đủ tiền!")
 x["cash"]-=n;x["bank"]+=n
 await c.send(f"🏦 Gửi `{M(n)}` thành công!")

@bot.command()
async def rut(c,n:int=None):
 x=u(c.author.id,c.author.name)
 if not n or n<=0:return await c.send("❌ `!rut 1000`")
 if x["bank"]<n:return await c.send("❌ Két không đủ!")
 x["bank"]-=n;x["cash"]+=n
 await c.send(f"🏦 Rút `{M(n)}` thành công!")

@bot.command()
async def chuyen(c,m:discord.Member=None,n:int=None):
 if not m or not n or n<=0:return await c.send("❌ `!chuyen @user 1000`")
 a=u(c.author.id,c.author.name);b=u(m.id,m.name)
 if a["cash"]<n:return await c.send("❌ Không đủ tiền!")
 a["cash"]-=n;b["cash"]+=n
 await c.send(f"💸 {c.author.mention} → {m.mention}: `{M(n)}`")

@bot.command()
async def diemdanh(c):
 x=u(c.author.id,c.author.name)
 w=43200-(time.time()-x.get("dd",0))
 if w>0:return await c.send(f"⏳ Đợi **{int(w):,} giây**.")
 x["dd"]=time.time();x["cash"]+=2593
 await c.send(embed=E("🎁 ĐIỂM DANH","💰 **+2,593$**",0x2ECC71))

# ================= TX =================

@bot.command()
async def tx(c,ch=None,n:int=None):
 if await lock(c):return
 if ch not in("tai","xiu") or not n or n<=0:
  return await c.send("❌ `!tx tai 1000`")
 if n>10000000:
  return await c.send("❌ Tối đa **10,000,000$/ván**!")
 x=u(c.author.id,c.author.name)
 if x["cash"]<n:return await c.send("❌ Không đủ tiền!")
 if c.author.id in TX["bets"]:return await c.send("❌ Bạn đã cược!")

 if not TX["on"]:
  TX.update(on=1,bets={},tai=0,xiu=0)
  TX["msg"]=await c.send(embed=E(
   "🎲 SÒNG TÀI XỈU",
   "**Tối đa 10,000,000$/ván**\n\n"
   "⏱️ **Thời gian: 30 giây**\n\n"
   "💰 Tổng Tài: `0$` | Tổng Xỉu: `0$`",
   0xFFD700))
  asyncio.create_task(txround())

 x["cash"]-=n
 TX["bets"][c.author.id]={"name":c.author.name,"choice":ch,"amount":n}
 TX[ch]+=n

 await TX["msg"].edit(embed=E(
  "🎲 SÒNG TÀI XỈU",
  "**Tối đa 10,000,000$/ván**\n\n"
  "⏱️ **Đang nhận cược...**\n\n"
  f"💰 Tổng Tài: `{M(TX['tai'])}` | Tổng Xỉu: `{M(TX['xiu'])}`",
  0xFFD700))

async def txround():
 await asyncio.sleep(30)
 d=[random.randint(1,6) for _ in range(3)]
 r="tai" if sum(d)>=11 else"xiu"
 w=[];l=[]

 for i,b in TX["bets"].items():
  x=u(i)
  ok=b["choice"]==r and random.random()<=x["rate"]/100
  if ok:
   p=b["amount"]*2;x["cash"]+=p
   w.append(f"• {b['name']} +`{M(p)}`")
  else:l.append(f"• {b['name']} -`{M(b['amount'])}`")

 await TX["msg"].edit(embed=E(
  "🎲 KẾT QUẢ",
  f"`[ {d[0]} | {d[1]} | {d[2]} ]`\n\n"
  f"🏆 **{sum(d)} điểm — {r.upper()}**\n\n"
  f"🎉 **THẮNG**\n{chr(10).join(w) or 'Không có'}\n\n"
  f"💸 **THUA**\n{chr(10).join(l) or 'Không có'}",
  0x2ECC71 if w else 0xE74C3C))

 TX.update(on=0,bets={},tai=0,xiu=0,msg=None)

# ================= GAME =================

@bot.command()
async def bc(c,ch=None,n:int=None):
 if await lock(c):return
 if ch not in B or not n or n<=0:
  return await c.send("❌ `!bc cua 1000`")

 x=u(c.author.id,c.author.name)
 if x["cash"]<n:return await c.send("❌ Không đủ tiền!")

 x["cash"]-=n

 m=await c.send(embed=E(
  "🦀 BẦU CUA",
  "# **Lắc... Lắc... Lắc...**",
  0xFFD700))

 await asyncio.sleep(1.3)

 await m.edit(embed=E(
  "🦀 BẦU CUA",
  "# **Hé bát...**",
  0xF1C40F))

 await asyncio.sleep(.8)

 r=[random.choice(list(B)) for _ in range(3)]
 k=r.count(ch)

 if k:
  p=n*(k+1)
  x["cash"]+=p
  t=f"🎉 **THẮNG +{M(p)} vào ví**"
  co=0x2ECC71
 else:
  t=f"💸 **THUA -{M(n)}**"
  co=0xE74C3C

 await m.edit(embed=E(
  "🦀 BẦU CUA",
  f"# **[ {B[r[0]]} | {B[r[1]]} | {B[r[2]]} ]**\n\n"
  f"{t}\n💵 Ví: `{M(x['cash'])}`",
  co))

@bot.command()
async def xd(c,ch=None,n:int=None):
 if await lock(c):return
 if ch not in("chan","le") or not n or n<=0:
  return await c.send("❌ `!xd chan 1000`")

 x=u(c.author.id,c.author.name)
 if x["cash"]<n:return await c.send("❌ Không đủ tiền!")

 x["cash"]-=n

 m=await c.send(embed=E(
  "🪙 XÓC ĐĨA",
  "# **Xóc... Xóc... Xóc...**\n\n"
  "# **[ ⚪ | ⚪ | ⚪ | ⚪ ]**",
  0xFFD700))

 await asyncio.sleep(1.3)

 q=random.randint(0,4)
 a=["⚪"]*4

 for z in random.sample(range(4),q):
  a[z]="🔴"

 r="chan" if q%2==0 else"le"
 ok=r==ch and random.random()<=x["rate"]/100

 if ok:
  p=n*2;x["cash"]+=p
  t=f"🎉 **THẮNG +{M(p)} vào ví**"
  co=0x2ECC71
 else:
  t=f"💸 **THUA -{M(n)}**"
  co=0xE74C3C

 await m.edit(embed=E(
  "🪙 XÓC ĐĨA",
  f"# **[ {' | '.join(a)} ]**\n\n"
  f"🎯 **{r.upper()}**\n{t}\n"
  f"💵 Ví: `{M(x['cash'])}`",
  co))

@bot.command()
async def quay(c,n:int=None):
 if await lock(c):return
 if not n or n<=0:return await c.send("❌ `!quay 1000`")

 x=u(c.author.id,c.author.name)
 if x["cash"]<n:return await c.send("❌ Không đủ tiền!")

 x["cash"]-=n

 m=await c.send(embed=E(
  "🎰 SLOT",
  "# **Quay... Quay... Quay...**",
  0xFFD700))

 await asyncio.sleep(1.3)

 s=[random.choice(["🍒","🍋","🔔","⭐","💎","7️⃣"]) for _ in range(3)]
 same=max(s.count(z) for z in set(s))
 ok=same>=2 and random.random()<=x["rate"]/100

 if ok:
  p=n*(5 if same==3 else 2)
  x["cash"]+=p
  t=f"🎉 **THẮNG +{M(p)} vào ví**"
  co=0x2ECC71
 else:
  t=f"💸 **THUA -{M(n)}**"
  co=0xE74C3C

 await m.edit(embed=E(
  "🎰 SLOT",
  f"# **[ {' | '.join(s)} ]**\n\n"
  f"{t}\n💵 Ví: `{M(x['cash'])}`",
  co))

@bot.command()
async def tuxi(c,ch=None,n:int=None):
 if await lock(c):return
 if ch not in("bao","bua","keo") or not n or n<=0:
  return await c.send("❌ `!tuxi bao 1000`")

 x=u(c.author.id,c.author.name)
 if x["cash"]<n:return await c.send("❌ Không đủ tiền!")

 b=random.choice(["bao","bua","keo"])
 ok=(ch,b)in[("bao","keo"),("bua","bao"),("keo","bua")] and random.random()<=x["rate"]/100

 x["cash"]-=n

 if ok:
  x["cash"]+=n*2
  t=f"🎉 **THẮNG +{M(n*2)}**"
  co=0x2ECC71
 elif ch==b:
  x["cash"]+=n
  t="🤝 **HÒA — hoàn tiền**"
  co=0xF1C40F
 else:
  t=f"💸 **THUA -{M(n)}**"
  co=0xE74C3C

 await c.send(embed=E(
  "✊ TÙ XÌ",
  f"👤 **Bạn:** `{ch.upper()}`   ⚔️ **VS**   🤖 **Bot:** `{b.upper()}`\n\n"
  f"{t}\n💵 Ví: `{M(x['cash'])}`",
  co))

# ================= VAY BOT =================

@bot.command()
async def vaybot(c,n:int=None):
 if not n or not 1<=n<=50000:
  return await c.send("❌ `!vaybot 1-50000`")

 x=u(c.author.id,c.author.name)

 if x["debt"]:
  return await c.send("❌ Bạn đang có nợ!")

 x["cash"]+=n
 x["debt"]=n
 x["loan"]="bot"
 x["lt"]=time.time()

 asyncio.create_task(botloan(c.author.id))

 await c.send(embed=E(
  "🏦 VAY BOT",
  f"💰 Nhận: `{M(n)}`\n⏱️ Hạn: **1 giờ**",
  0xF1C40F))

async def botloan(i):
 await asyncio.sleep(3600)
 x=u(i)

 if x["debt"]>0:
  x["rate"]=max(0,x["rate"]-.5)
  x["bad"]=1
  take=x["cash"]//2
  x["cash"]-=take

  await notify(
   i,
   f"⚠️ **Vay BOT quá hạn!**\n"
   f"💸 Thu 1/2 ví: `{M(take)}`\n"
   f"🎯 May mắn -0,5%.")

# ================= VAY NGƯỜI =================

@bot.command()
async def vay(c,m:discord.Member=None,n:int=None):
 if not m or not n or not 1<=n<=100000000:
  return await c.send("❌ `!vay @user 1-100000000`")

 x=u(c.author.id,c.author.name)
 l=u(m.id,m.name)

 if x["debt"]:
  return await c.send("❌ Bạn đang có nợ!")

 if l["cash"]<n:
  return await c.send("❌ Người cho vay không đủ tiền!")

 P[c.author.id]={
  "borrow":c.author.id,
  "lender":m.id,
  "amount":n
 }

 await c.send(
  f"🤝 {c.author.mention} muốn vay {m.mention} "
  f"**{M(n)}**\n\n"
  f"✅ `!okchovay`\n❌ `!khongchovay`")

@bot.command()
async def okchovay(c):
 v=None

 for k,z in list(P.items()):
  if z["lender"]==c.author.id:
   v=P.pop(k)
   break

 if not v:return await c.send("❌ Không có yêu cầu!")

 a=u(v["borrow"])
 l=u(v["lender"])

 if l["cash"]<v["amount"]:
  return await c.send("❌ Không đủ tiền!")

 l["cash"]-=v["amount"]
 a["cash"]+=v["amount"]
 a["debt"]=v["amount"]
 a["loan"]="player"
 a["lt"]=time.time()

 asyncio.create_task(
  playerloan(v["borrow"],v["lender"]))

 await c.send("✅ **Đã chấp nhận khoản vay!**")

@bot.command()
async def khongchovay(c):
 for k,z in list(P.items()):
  if z["lender"]==c.author.id:
   P.pop(k)
   return await c.send("❌ Đã từ chối.")
 await c.send("❌ Không có yêu cầu!")

async def playerloan(i,lender):
 await asyncio.sleep(3600)
 x=u(i)

 if x["debt"]>0:
  x["rate"]=max(0,x["rate"]-1)
  x["bad"]=1
  await notify(
   i,
   "⚠️ **Vay người chơi quá hạn!**\n"
   "🚨 Nợ xấu, may mắn -1%.")

async def notify(i,text):
 for g in bot.guilds:
  m=g.get_member(i)

  if m:
   r=discord.utils.find(
    lambda z:z.name.lower()=="nợ xấu",
    g.roles)

   if r:
    try:await m.add_roles(r)
    except:pass

   try:await m.send(text)
   except:pass

# ================= TRẢ NỢ =================

@bot.command()
async def trano(c,m=None,n:int=None):
 x=u(c.author.id,c.author.name)

 if not n or n<=0:
  return await c.send(
   "❌ `!trano bot 50000` hoặc "
   "`!trano @user 50000`")

 if x["debt"]<=0:
  return await c.send("❌ Bạn không có nợ!")

 if n>x["debt"] or x["cash"]<n:
  return await c.send(
   "❌ Số tiền trả không hợp lệ/không đủ ví!")

 if m=="bot":
  rec=None
 else:
  if not isinstance(m,discord.Member):
   return await c.send("❌ `!trano @user 50000`")
  rec=u(m.id,m.name)

 x["cash"]-=n

 if rec:
  rec["cash"]+=n

 x["debt"]-=n

 if x["debt"]==0:
  x["rate"]=RATE
  x["bad"]=0
  x["locked"]=0

  r=discord.utils.find(
   lambda z:z.name.lower()=="nợ xấu",
   c.guild.roles)

  if r:
   try:await c.author.remove_roles(r)
   except:pass

 await c.send(embed=E(
  "✅ TRẢ NỢ",
  f"💵 Đã trả: `{M(n)}`\n"
  f"💸 Còn nợ: `{M(x['debt'])}`\n"
  f"🎯 May mắn: **{x['rate']:.1f}%**",
  0x2ECC71))

# ================= ADMIN =================

@bot.command()
async def tyle(c,n:int=None):
 global RATE

 if not A(c):
  return await c.send("⛔ Chỉ Admin!")

 if n is None or not 0<=n<=100:
  return await c.send("❌ `!tyle 0-100`")

 RATE=n

 for x in U.values():
  x["rate"]=max(0,n-(1 if x["bad"] else 0))

 await c.send(
  f"⚙️ **Tỷ lệ server: {n}%**")

@bot.command()
async def settien(c,m:discord.Member=None,n:int=None):
 if not A(c):return await c.send("⛔ Chỉ Admin!")

 if not m or n is None:
  return await c.send("❌ `!settien @user 10000`")

 u(m.id,m.name)["cash"]=max(0,n)

 await c.send(embed=E(
  "💰 SET TIỀN",
  f"👤 {m.mention}\n💵 `{M(n)}`",
  0x2ECC71))

@bot.command()
async def resettien(c,m:discord.Member=None):
 if not A(c):return await c.send("⛔ Chỉ Admin!")

 if not m:
  return await c.send("❌ `!resettien @user`")

 x=u(m.id,m.name)
 x["cash"]=4899
 x["bank"]=0

 await c.send(embed=E(
  "🔄 RESET TIỀN",
  f"👤 {m.mention}\n💵 `{M(4899)}`",
  0xF1C40F))

# ================= CODE =================

def code():
 return "BET-"+secrets.token_hex(3).upper()

@bot.command()
async def taocode(c,n:int=None,k:int=1):
 if not A(c):return await c.send("⛔ Chỉ Admin!")

 if not n or k<1:
  return await c.send("❌ `!taocode 10000 5`")

 z=code()
 C[z]={"money":n,"uses":k,"used":set()}

 await c.send(embed=E(
  "🔐 TẠO CODE",
  f"🎁 `{z}`\n"
  f"💰 `{M(n)}`\n"
  f"👥 `{k}` lượt",
  0x2ECC71))

@bot.command()
async def thuongcode(c,n:int=None,k:int=1):
 if not A(c):return await c.send("⛔ Chỉ Admin!")

 if not n or k<1:
  return await c.send("❌ `!thuongcode 10000 5`")

 z=code()
 C[z]={"money":n,"uses":k,"used":set()}

 await c.send(embed=E(
  "🎁 CODE THƯỞNG",
  f"🔐 `{z}`\n"
  f"💰 `{M(n)}`\n"
  f"👥 `{k}` lượt",
  0xFFD700))

@bot.command()
async def nhapcode(c,z=None):
 z=(z or "").upper()

 if z not in C:
  return await c.send("❌ Code không tồn tại!")

 q=C[z]

 if c.author.id in q["used"] or len(q["used"])>=q["uses"]:
  return await c.send("❌ Code hết lượt!")

 q["used"].add(c.author.id)

 x=u(c.author.id,c.author.name)
 x["cash"]+=q["money"]

 await c.send(
  f"🎁 **+{M(q['money'])}** vào ví!\n"
  f"💵 Ví: `{M(x['cash'])}`")

token=os.getenv("TOKEN_BOT")

if token:
 bot.run(token)
else:
 print("❌ Chưa có TOKEN_BOT!")
