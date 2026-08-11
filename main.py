import os,asyncio,random,time,secrets,discord
from discord.ext import commands

I=discord.Intents.default();I.message_content=True
bot=commands.Bot(command_prefix="!",intents=I,help_command=None)
U={};TX={"on":0,"bets":{},"tai":0,"xiu":0,"msg":None};LOANS={};PENDING={}
RATE=36
B={"ca":"🐟","tom":"🦐","cua":"🦀","bau":"🍐","ga":"🐓","nai":"🦌"}
S=["🍒","🍋","🔔","⭐","💎","7️⃣"]

def u(i,n="Người chơi"):
 if i not in U: U[i]={"name":n,"cash":4899,"bank":0,"debt":0,"rate":RATE,"vip":0,"bad":0}
 return U[i]
def money(n): return f"{int(n):,}$"
def E(t,d,c=0x3498DB): return discord.Embed(title=t,description=d,color=c)
def adm(c): return c.author.guild_permissions.administrator

async def lock(c):
 x=u(c.author.id,c.author.name)
 if x["debt"]>0 and x.get("locked"):
  await c.send(f"🚫 **Bạn đang bị khóa chơi do quá hạn nợ!**\n💸 Nợ: `{money(x['debt'])}`")
  return True
 return False

@bot.event
async def on_ready():
 await bot.change_presence(activity=discord.Game("!trogiup | Casino"))
 print("ONLINE",bot.user)

@bot.command(name="trogiup",aliases=["help"])
async def help(c):
 await c.send(embed=E("🎰 CASINO",
 """🎲 `!tx tai 1000` / `!tx xiu 1000`
🦀 `!bc cua 1000`
🪙 `!xd chan 1000`
🎰 `!quay 1000`
✂️ `!tuxi bao 1000`

💳 `!vi` `!gui 1000` `!rut 1000`
💸 `!chuyen @user 1000`
🎁 `!diemdanh`

💰 `!vay 50000` → vay BOT
🤝 `!vay @user 50000` → vay người chơi
✅ `!okchovay` / ❌ `!khongchovay`
💵 `!trano 50000`
💵 `!trano @user 50000`

👑 Admin: `!settien` `!resettien` `!tyle`"""))

@bot.command()
async def vi(c,m:discord.Member=None):
 m=m or c.author;x=u(m.id,m.name)
 await c.send(embed=E("💳 TÀI KHOẢN",
 f"👤 **{m.name}**\n\n"
 f"🏷️ Hạng: {'👑 Vương miện VIP' if x['vip'] else '👤 Người chơi Thường'}\n"
 f"💵 Tiền mặt: `{money(x['cash'])}`\n"
 f"🏦 Két sắt: `{money(x['bank'])}`\n"
 f"💸 Nợ: `{money(x['debt'])}`\n"
 f"🎯 Tỷ lệ may mắn: **{x['rate']:.1f}%**",
 0xFFD700 if x["vip"] else 0x3498DB))

@bot.command()
async def gui(c,n:int=None):
 x=u(c.author.id,c.author.name)
 if not n or n<=0:return await c.send("❌ `!gui 1000`")
 if x["cash"]<n:return await c.send("❌ Không đủ tiền!")
 x["cash"]-=n;x["bank"]+=n
 await c.send(f"🏦 Gửi thành công `{money(n)}`!")

@bot.command()
async def rut(c,n:int=None):
 x=u(c.author.id,c.author.name)
 if not n or n<=0:return await c.send("❌ `!rut 1000`")
 if x["bank"]<n:return await c.send("❌ Két không đủ!")
 x["bank"]-=n;x["cash"]+=n
 await c.send(f"🏦 Rút thành công `{money(n)}`!")

@bot.command()
async def chuyen(c,m:discord.Member=None,n:int=None):
 if not m or not n or n<=0:return await c.send("❌ `!chuyen @user 1000`")
 if m.id==c.author.id:return await c.send("❌ Không thể chuyển cho chính mình!")
 a=u(c.author.id,c.author.name);b=u(m.id,m.name)
 if a["cash"]<n:return await c.send("❌ Không đủ tiền!")
 a["cash"]-=n;b["cash"]+=n
 await c.send(f"✅ {c.author.mention} → {m.mention}: **{money(n)}**")

@bot.command()
async def diemdanh(c):
 x=u(c.author.id,c.author.name);now=time.time()
 if now-x.get("dd",0)<43200:
  return await c.send("⏳ Bạn đã điểm danh rồi!")
 x["dd"]=now;x["cash"]+=2593
 await c.send(embed=E("🎁 ĐIỂM DANH","💰 **+2,593$ vào ví**",0x2ECC71))

# ---------- TX ----------
@bot.command()
async def tx(c,ch=None,n:int=None):
 if await lock(c):return
 if ch not in ("tai","xiu") or not n or n<=0:return await c.send("❌ `!tx tai 1000`")
 if n>10000000:return await c.send("❌ Tối đa **10,000,000$/ván**!")
 x=u(c.author.id,c.author.name);i=c.author.id
 if x["cash"]<n:return await c.send("❌ Không đủ tiền!")
 if i in TX["bets"]:return await c.send("❌ Bạn đã cược ván này!")

 if not TX["on"]:
  TX.update(on=1,bets={},tai=0,xiu=0)
  TX["msg"]=await c.send(embed=E(
   "🎲 SÒNG TÀI XỈU 30S 🎲",
   "Anh em gõ `!tx <tai/xiu> <tiền>`\n"
   "💰 **Tối đa 10,000,000$/ván**\n\n"
   "⏱️ **Thời gian: 30 giây**\n\n"
   "💵 Tổng Tài: `0$` | Tổng Xỉu: `0$`",0xFFD700))
  asyncio.create_task(txround())

 x["cash"]-=n;TX["bets"][i]={"name":c.author.name,"choice":ch,"amount":n};TX[ch]+=n
 await TX["msg"].edit(embed=E(
  "🎲 SÒNG TÀI XỈU 30S 🎲",
  "Anh em gõ `!tx <tai/xiu> <tiền>`\n"
  "💰 **Tối đa 10,000,000$/ván**\n\n"
  "⏱️ **Đang nhận cược...**\n\n"
  f"💵 Tổng Tài: `{money(TX['tai'])}` | Tổng Xỉu: `{money(TX['xiu'])}`",0xFFD700))

async def txround():
 await asyncio.sleep(30)
 d=[random.randint(1,6) for _ in range(3)];r="tai" if sum(d)>=11 else "xiu"
 w=[];l=[]
 for i,b in TX["bets"].items():
  x=u(i);win=b["choice"]==r and random.random()<x["rate"]/100
  if win:
   p=b["amount"]*2;x["cash"]+=p;w.append(f"• {b['name']} `+{money(p)}`")
  else:l.append(f"• {b['name']} `-{money(b['amount'])}`")
 await TX["msg"].edit(embed=E(
  "🎲 KẾT QUẢ TÀI XỈU",
  f"🎲 Xúc xắc\n`[ {d[0]} ] - [ {d[1]} ] - [ {d[2]} ]`\n\n"
  f"➡️ **{sum(d)} điểm ({r.upper()})**\n\n"
  f"🎉 **NGƯỜI THẮNG**\n{chr(10).join(w) or 'Không có'}\n\n"
  f"💸 **NGƯỜI THUA**\n{chr(10).join(l) or 'Không có'}",0x2ECC71 if w else 0xE74C3C))
 TX.update(on=0,bets={},tai=0,xiu=0,msg=None)

# ---------- GAME ----------
@bot.command()
async def bc(c,ch=None,n:int=None):
 if await lock(c):return
 if ch not in B or not n or n<=0:return await c.send("❌ `!bc cua 1000`")
 x=u(c.author.id,c.author.name)
 if x["cash"]<n:return await c.send("❌ Không đủ tiền!")
 x["cash"]-=n
 m=await c.send(embed=E("🦀 BẦU CUA","🎲\n\n# **Lắc... Lắc... Lắc...**",0xFFD700))
 await asyncio.sleep(1.5)
 await m.edit(embed=E("🦀 BẦU CUA","🥁\n\n# **HÉ BÁT...**",0xF1C40F));await asyncio.sleep(1)
 r=[random.choice(list(B)) for _ in range(3)];k=r.count(ch)
 if k:p=n*(k+1);x["cash"]+=p;txt=f"🎉 **THẮNG +{money(p)} vào ví**";co=0x2ECC71
 else:txt=f"💸 **THUA -{money(n)}**";co=0xE74C3C
 await m.edit(embed=E("🦀 BẦU CUA",
 f"# **[ {B[r[0]]} | {B[r[1]]} | {B[r[2]]} ]**\n\n{txt}\n💵 Ví: `{money(x['cash'])}`",co))

@bot.command()
async def xd(c,ch=None,n:int=None):
 if await lock(c):return
 if ch not in ("chan","le") or not n or n<=0:return await c.send("❌ `!xd chan 1000`")
 x=u(c.author.id,c.author.name)
 if x["cash"]<n:return await c.send("❌ Không đủ tiền!")
 x["cash"]-=n
 m=await c.send(embed=E("🪙 XÓC ĐĨA","# **Xóc... Xóc... Xóc...**",0xFFD700));await asyncio.sleep(1.5)
 q=random.randint(0,4);r="chan" if q%2==0 else "le"
 balls=["⚪"]*4
 for z in random.sample(range(4),q):balls[z]="🔴"
 win=r==ch and random.random()<x["rate"]/100
 if win:p=n*2;x["cash"]+=p;txt=f"🎉 **THẮNG +{money(p)} vào ví**";co=0x2ECC71
 else:txt=f"💸 **THUA -{money(n)}**";co=0xE74C3C
 await m.edit(embed=E("🪙 XÓC ĐĨA",
 f"# **[ {' | '.join(balls)} ]**\n\n🎯 **{r.upper()}**\n\n{txt}\n💵 Ví: `{money(x['cash'])}`",co))

@bot.command()
async def quay(c,n:int=None):
 if await lock(c):return
 if not n or n<=0:return await c.send("❌ `!quay 1000`")
 x=u(c.author.id,c.author.name)
 if x["cash"]<n:return await c.send("❌ Không đủ tiền!")
 x["cash"]-=n
 m=await c.send(embed=E("🎰 MÁY SLOT","# **Quay... Quay... Quay...**",0xFFD700));await asyncio.sleep(1.5)
 s=[random.choice(S) for _ in range(3)];same=max(s.count(z) for z in set(s))
 win=random.random()<x["rate"]/100 and same>=2
 if win:p=n*(5 if same==3 else 2);x["cash"]+=p;txt=f"🎉 **THẮNG +{money(p)} vào ví**";co=0x2ECC71
 else:txt=f"💸 **THUA -{money(n)}**";co=0xE74C3C
 await m.edit(embed=E("🎰 MÁY SLOT",
 f"# **[ {' | '.join(s)} ]**\n\n{txt}\n💵 Ví: `{money(x['cash'])}`",co))

@bot.command()
async def tuxi(c,ch=None,n:int=None):
 if await lock(c):return
 if ch not in ("bao","bua","keo") or not n or n<=0:return await c.send("❌ `!tuxi bao 1000`")
 x=u(c.author.id,c.author.name)
 if x["cash"]<n:return await c.send("❌ Không đủ tiền!")
 botc=random.choice(["bao","bua","keo"]);win=(ch,botc) in [("bao","keo"),("bua","bao"),("keo","bua")]
 x["cash"]-=n
 if win:x["cash"]+=n*2;txt=f"🎉 **THẮNG +{money(n*2)}**";co=0x2ECC71
 else:txt=f"💸 **THUA -{money(n)}**";co=0xE74C3C
 await c.send(embed=E("✊ TÙ XÌ",
 f"👤 **Bạn:** `{ch.upper()}`\n⚔️ **VS**\n🤖 **Bot:** `{botc.upper()}`\n\n{txt}\n💵 Ví: `{money(x['cash'])}`",co))

# ---------- VAY ----------
@bot.command()
async def vay(c,m=None,n:int=None):
 x=u(c.author.id,c.author.name)
 if m and m.startswith("<@"):
  try:member=await commands.MemberConverter().convert(c,m)
  except:return await c.send("❌ Không tìm thấy người cho vay!")
  if member.id==c.author.id:return await c.send("❌ Không thể vay chính mình!")
  if not n or not 1<=n<=100000000:return await c.send("❌ Vay người chơi: **1–100,000,000$**")
  if x["debt"]:return await c.send("❌ Bạn đang có nợ!")
  lender=u(member.id,member.name)
  if lender["cash"]<n:return await c.send("❌ Người cho vay không đủ tiền!")
  key=f"{c.author.id}:{member.id}"
  PENDING[key]={"borrower":c.author.id,"lender":member.id,"amount":n,"time":time.time(),"player":1}
  await c.send(embed=E("🤝 YÊU CẦU VAY",
   f"{c.author.mention} muốn vay {member.mention}\n💰 **{money(n)}**\n\n"
   f"✅ {member.mention} gõ `!okchovay`\n❌ Gõ `!khongchovay`",0xF1C40F))
 else:
  if not n or not 1<=n<=50000:return await c.send("❌ Vay bot: **1–50,000$**")
  if x["debt"]:return await c.send("❌ Bạn đang có nợ!")
  x["cash"]+=n;x["debt"]=n;x["loan_bot"]=1;x["loan_time"]=time.time();x["locked"]=False
  asyncio.create_task(botloan(x,c.author.id))
  await c.send(embed=E("🏦 VAY BOT",f"💰 Nhận: `{money(n)}`\n⏱️ Hạn: **1 giờ**\n💸 Quá hạn sẽ bị xử lý nợ.",0xF1C40F))

@bot.command()
async def okchovay(c):
 key=None
 for k,v in PENDING.items():
  if v["lender"]==c.author.id:key=k;break
 if not key:return await c.send("❌ Không có yêu cầu vay.")
 v=PENDING.pop(key);a=u(v["borrower"]);b=u(v["lender"])
 if b["cash"]<v["amount"]:return await c.send("❌ Bạn không đủ tiền!")
 b["cash"]-=v["amount"];a["cash"]+=v["amount"];a["debt"]=v["amount"];a["loan_time"]=time.time();a["loan_bot"]=0;a["lender"]=b["name"]
 asyncio.create_task(playerloan(v["borrower"],key))
 await c.send("✅ Đã chấp nhận khoản vay!")

@bot.command()
async def khongchovay(c):
 for k,v in list(PENDING.items()):
  if v["lender"]==c.author.id:
   PENDING.pop(k);return await c.send("❌ Đã từ chối khoản vay.")
 await c.send("❌ Không có yêu cầu vay.")

async def botloan(i,uid):
 await asyncio.sleep(3600);x=u(uid)
 if x["debt"]<=0:return
 x["rate"]=max(0,x["rate"]-0.5)
 take=x["cash"]//2;x["cash"]-=take
 x["locked"]=False;x["bad"]=1
 await send_user(uid,f"⚠️ **Khoản vay BOT đã quá hạn!**\n💸 Đã thu `{money(take)}`.\n🎯 May mắn giảm **0,5%**.")

async def playerloan(uid,key):
 await asyncio.sleep(3600);x=u(uid)
 if x["debt"]<=0:return
 x["rate"]=max(0,x["rate"]-1);x["bad"]=1
 # role sẽ được thêm khi có guild/message tiếp theo
 await send_user(uid,"⚠️ **Khoản vay đã quá hạn!**\n🚨 Bạn bị **Nợ xấu** và may mắn giảm **1%**.")

async def send_user(uid,text):
 for g in bot.guilds:
  m=g.get_member(uid)
  if m:
   role=discord.utils.find(lambda r:r.name.lower()=="nợ xấu",g.roles)
   if role:
    try:await m.add_roles(role)
    except:pass
   try:await m.send(text)
   except:pass
   break

@bot.command()
async def trano(c,m=None,n:int=None):
 x=u(c.author.id,c.author.name)
 if not n or n<=0:return await c.send("❌ `!trano 50000` hoặc `!trano @user 50000`")
 if x["debt"]<=0:return await c.send("❌ Bạn không có nợ!")
 if n>x["debt"]:return await c.send("❌ Số tiền trả vượt quá nợ!")
 if x["cash"]<n:return await c.send("❌ Ví không đủ tiền!")
 x["cash"]-=n
 if m and m.startswith("<@"):
  try:member=await commands.MemberConverter().convert(c,m)
  except:return await c.send("❌ Không tìm thấy người nhận!")
  u(member.id,member.name)["cash"]+=n
 x["debt"]-=n
 if x["debt"]==0:
  x["rate"]=RATE;x["bad"]=0;x["locked"]=False
  if x.get("loan_bot"):x.pop("loan_bot",None)
  role=discord.utils.find(lambda r:r.name.lower()=="nợ xấu",c.guild.roles)
  if role:
   try:await c.author.remove_roles(role)
   except:pass
 await c.send(embed=E("✅ TRẢ NỢ",f"💵 Đã trả: `{money(n)}`\n💸 Nợ còn: `{money(x['debt'])}`\n🎯 May mắn: **{x['rate']:.1f}%**",0x2ECC71))

# ---------- ADMIN ----------
@bot.command()
async def tyle(c,n:int=None):
 global RATE
 if not adm(c):return await c.send("⛔ Chỉ Admin!")
 if n is None or not 0<=n<=100:return await c.send("❌ `!tyle 0-100`")
 RATE=n
 for x in U.values():x["rate"]=max(0,n-(1 if x["bad"] else 0)-(0.5 if x.get("loan_bot") and x["bad"] else 0))
 await c.send(f"⚙️ Tỷ lệ server: **{n}%**")

@bot.command()
async def settien(c,m:discord.Member=None,n:int=None):
 if not adm(c):return await c.send("⛔ Chỉ Admin!")
 if not m or n is None:return await c.send("❌ `!settien @user 10000`")
 u(m.id,m.name)["cash"]=max(0,n)
 await c.send(f"💰 {m.mention} → `{money(n)}`")

@bot.command()
async def resettien(c,m:discord.Member=None):
 if not adm(c):return await c.send("⛔ Chỉ Admin!")
 if not m:return await c.send("❌ `!resettien @user`")
 x=u(m.id,m.name);x["cash"]=4899;x["bank"]=0
 await c.send(f"🔄 {m.mention} đã reset về `4,899$`")

token=os.getenv("TOKEN_BOT")
if not token:print("❌ Chưa có TOKEN_BOT!")
else:bot.run(token)
