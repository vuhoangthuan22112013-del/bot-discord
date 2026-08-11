import os,asyncio,random,secrets,time,discord
from discord.ext import commands

I=discord.Intents.default();I.message_content=True
bot=commands.Bot(command_prefix="!",intents=I,help_command=None)
U={};C={};LOANS={}
BLUE,ORANGE,GREEN,RED,GOLD=0x3498DB,0xF1C40F,0x2ECC71,0xE74C3C,0xFFD700
WIN_RATE=100
TX={"on":0,"bets":{},"tai":0,"xiu":0,"msg":None}

def E(t,d,c=BLUE):
 e=discord.Embed(title=t,description=d,color=c)
 e.set_footer(text="💎 BET88")
 return e

def user(i,n="Thành viên"):
 if i not in U:
  U[i]={"name":n,"cash":4899,"bank":0,"debt":0,"vip":0,"dd":0,"rate":WIN_RATE,"bad":0}
 return U[i]

def money(n):return f"{int(n):,}$"
def admin(c):return bool(c.guild and c.author.guild_permissions.administrator)

async def blocked(c):
 u=user(c.author.id,c.author.name)
 if u["debt"]>0:
  await c.send(f"🚫 Bạn đang nợ **{money(u['debt'])}**!\n💡 Hãy trả nợ trước khi chơi.")
  return True
 return False

def paytext(u,bet,win,prize):
 if win:
  return f"""🎉 **Bạn đã thắng nhà cái Bet88!** 🤑

💵 Tiền cược: `{money(bet)}`
🏆 Tiền thắng: `{money(prize)}`
💳 Ví: `{money(u['cash'])}`"""
 return f"""💀 **Cảm ơn đã tin tưởng nhà cái Bet88!**

💵 Tiền cược: `{money(bet)}`
🏆 Tiền thắng: `0$`
💳 Ví: `{money(u['cash'])}`"""

@bot.event
async def on_ready():
 await bot.change_presence(activity=discord.Game("!trogiup | Casino"))
 print("ONLINE:",bot.user)

@bot.command(aliases=["help"])
async def trogiup(c):
 await c.send(embed=E("🎰 CASINO BET88",
"""🎲 **TRÒ CHƠI**
`!tx tai 1000` • `!tx xiu 1000`
`!bc cua 1000` • `!xd chan 1000`
`!quay 1000` • `!tuxi bao 1000`

💳 **TÀI KHOẢN**
`!vi` • `!diemdanh` • `!gui 1000` • `!rut 1000`
`!chuyen @User 1000` • `!bxh`

💰 **VAY**
`!vay @User 1000` • `!trano @User 1000`

👑 **ADMIN**
`!tyle 0-100` • `!settien @User 10000`
`!resettien @User`
`!taocode 1000 5` • `!thuongcode 1000 5`
`!nhapcode CODE`"""))

@bot.command()
async def vi(c,m:discord.Member=None):
 m=m or c.author
 u=user(m.id,m.name)
 await c.send(embed=E(
  "💳 TÀI KHOẢN",
  f"""👤 **{m.name}**
🏷️ {'👑 VIP' if u['vip'] else '🐥 Thường'}

💵 Ví: `{money(u['cash'])}`
🏦 Bank: `{money(u['bank'])}`
💸 Nợ: `{money(u['debt'])}`
🎯 Tỷ lệ thắng: `{u['rate']}%`""",
  GOLD if u["vip"] else BLUE
 ))

@bot.command()
async def gui(c,n:int=None):
 u=user(c.author.id,c.author.name)
 if not n or n<=0:return await c.send("❌ `!gui 1000`")
 if n>u["cash"]:return await c.send("❌ Không đủ tiền!")
 u["cash"]-=n;u["bank"]+=n
 await c.send(embed=E("🏦 GỬI TIỀN",
 f"💵 Tiền gửi: `{money(n)}`\n💳 Ví: `{money(u['cash'])}`\n🏦 Bank: `{money(u['bank'])}`",GREEN))

@bot.command()
async def rut(c,n:int=None):
 u=user(c.author.id,c.author.name)
 if not n or n<=0:return await c.send("❌ `!rut 1000`")
 if n>u["bank"]:return await c.send("❌ Bank không đủ!")
 u["bank"]-=n;u["cash"]+=n
 await c.send(embed=E("💸 RÚT TIỀN",
 f"💵 Tiền rút: `{money(n)}`\n💳 Ví: `{money(u['cash'])}`\n🏦 Bank: `{money(u['bank'])}`",GREEN))

@bot.command()
async def chuyen(c,m:discord.Member=None,n:int=None):
 if not m or not n or n<=0:return await c.send("❌ `!chuyen @User 1000`")
 if m.id==c.author.id:return await c.send("❌ Không thể chuyển cho chính mình!")
 a=user(c.author.id,c.author.name)
 b=user(m.id,m.name)
 if n>a["cash"]:return await c.send("❌ Không đủ tiền!")
 a["cash"]-=n;b["cash"]+=n
 await c.send(f"💸 {c.author.mention} → {m.mention}: `{money(n)}`")

@bot.command()
async def diemdanh(c):
 u=user(c.author.id,c.author.name)
 now=time.time()
 w=43200-(now-u["dd"])
 if w>0:return await c.send(f"⌛ Đã điểm danh! Còn **{int(w):,} giây**.")
 u["dd"]=now
 u["cash"]+=2593
 await c.send(embed=E("🎁 ĐIỂM DANH","💰 **+2,593$ vào ví**",GREEN))

@bot.command()
async def bxh(c):
 x=sorted(U.values(),key=lambda z:z["cash"]+z["bank"],reverse=True)[:5]
 text="\n".join(
  f"**{i}.** {u['name']} — `{money(u['cash']+u['bank'])}`"
  for i,u in enumerate(x,1)
 ) or "Chưa có dữ liệu."
 await c.send(embed=E("🏆 TOP 5",text))

# ================= TÀI XỈU =================

@bot.command()
async def tx(c,ch=None,bet:int=None):
 if await blocked(c):return

 if ch not in("tai","xiu") or not bet or bet<=0:
  return await c.send("❌ `!tx tai 1000` hoặc `!tx xiu 1000`")

 if bet>10_000_000:
  return await c.send("❌ Tối đa **10,000,000$/ván**!")

 u=user(c.author.id,c.author.name)
 uid=c.author.id

 if u["cash"]<bet:
  return await c.send("❌ Không đủ tiền!")

 if uid in TX["bets"]:
  return await c.send("❌ Bạn đã cược ván này!")

 if not TX["on"]:
  TX.update(on=1,bets={},tai=0,xiu=0)

  TX["msg"]=await c.send(embed=E(
   "🎲 SÒNG TÀI XỈU 30S 🎲",
   """🔥 **Anh em gõ theo kèo:**
`!tx tai 1000` / `!tx xiu 1000`

⏱️ **Tối đa:** **30 giây**
💰 **Tối đa:** `10,000,000$/ván`

💰 Tài: `0$` - Xỉu: `0$`""",
   ORANGE
  ))

  asyncio.create_task(txround())

 u["cash"]-=bet

 TX["bets"][uid]={
  "name":c.author.name,
  "choice":ch,
  "amount":bet
 }

 TX[ch]+=bet

 await TX["msg"].edit(embed=E(
  "🎲 SÒNG TÀI XỈU 30S 🎲",
  """🔥 **Anh em gõ theo kèo:**
`!tx tai 1000` / `!tx xiu 1000`

⏱️ **Đang nhận cược...**

"""
  f"💰 Tài: `{money(TX['tai'])}` - Xỉu: `{money(TX['xiu'])}`",
  ORANGE
 ))

 try:
  await c.message.delete()
 except:
  pass

async def txround():
 await asyncio.sleep(30)

 d=[random.randint(1,6) for _ in range(3)]
 total=sum(d)
 r="tai" if total>=11 else"xiu"
 lines=[]

 for uid,b in TX["bets"].items():
  u=user(uid)

  win=(
   b["choice"]==r and
   random.randint(1,100)<=max(0,min(100,u["rate"]))
  )

  p=int(
   b["amount"]*2*(1.5 if u["vip"] else 1)
  ) if win else 0

  if win:
   u["cash"]+=p

  lines.append(
   f"**{b['name']}**\n"+
   paytext(u,b["amount"],win,p)
  )

 body=(
  "📢 **THÔNG BÁO**\n\n"
  f"`[ {d[0]} ] - [ {d[1]} ] - [ {d[2]} ]`\n\n"
  f"🎯 **{total} điểm — {r.upper()}**\n\n"+
  ("\n\n".join(lines) if lines else "👥 Không có người chơi.")
 )

 await TX["msg"].edit(embed=E(
  "🎲 KẾT QUẢ TÀI XỈU",
  body,
  GREEN if any("Bạn đã thắng" in x for x in lines) else RED
 ))

 TX.update(on=0,bets={},tai=0,xiu=0,msg=None)

# ================= BẦU CUA =================

@bot.command()
async def bc(c,ch=None,bet:int=None):
 if await blocked(c):return

 a={
  "ca":"🐟",
  "tom":"🦐",
  "cua":"🦀",
  "bau":"🍐",
  "ga":"🐓",
  "nai":"🦌"
 }

 if ch not in a or not bet or bet<=0:
  return await c.send("❌ `!bc cua 1000`")

 u=user(c.author.id,c.author.name)

 if u["cash"]<bet:
  return await c.send("❌ Không đủ tiền!")

 u["cash"]-=bet

 m=await c.send(embed=E(
  "🦀 BẦU CUA | 🟠 ĐANG LẮC",
  "🎲 **LẮC... LẮC... LẮC...**\n\n`[ ❔ | ❔ | ❔ ]`",
  ORANGE
 ))

 await asyncio.sleep(1)

 r=[random.choice(list(a)) for _ in range(3)]
 n=r.count(ch)
 win=n>0

 p=int(
  bet*(n+1)*(1.5 if u["vip"] else 1)
 ) if win else 0

 if win:
  u["cash"]+=p

 await m.edit(embed=E(
  "🦀 BẦU CUA | 🟢 KẾT QUẢ",
  f"`[ {' | '.join(a[x] for x in r)} ]`\n\n"
  f"📢 **THÔNG BÁO**\n\n"
  f"{paytext(u,bet,win,p)}",
  GREEN if win else RED
 ))

# ================= XÓC ĐĨA =================

@bot.command()
async def xd(c,ch=None,bet:int=None):
 if await blocked(c):return

 if ch not in("chan","le") or not bet or bet<=0:
  return await c.send("❌ `!xd chan 1000` hoặc `!xd le 1000`")

 u=user(c.author.id,c.author.name)

 if u["cash"]<bet:
  return await c.send("❌ Không đủ tiền!")

 u["cash"]-=bet

 m=await c.send(embed=E(
  "🪙 XÓC ĐĨA | 🟠 ĐANG XÓC",
  "🪙 **XÓC... XÓC... XÓC...**\n\n`[ ⚪ | ⚪ | ⚪ | ⚪ ]`",
  ORANGE
 ))

 await asyncio.sleep(1.2)

 n=random.randint(0,4)
 cups=["⚪"]*4

 for i in random.sample(range(4),n):
  cups[i]="🔴"

 r="chan" if n%2==0 else"le"

 win=(
  r==ch and
  random.randint(1,100)<=max(0,min(100,u["rate"]))
 )

 p=int(
  bet*2*(1.5 if u["vip"] else 1)
 ) if win else 0

 if win:
  u["cash"]+=p

 await m.edit(embed=E(
  "🪙 XÓC ĐĨA | 🟢 KẾT QUẢ",
  f"`[ {' | '.join(cups)} ]`\n\n"
  f"📢 **THÔNG BÁO**\n\n"
  f"🎯 **{r.upper()}**\n\n"
  f"{paytext(u,bet,win,p)}",
  GREEN if win else RED
 ))

# ================= QUAY =================

@bot.command()
async def quay(c,bet:int=None):
 if await blocked(c):return

 if not bet or bet<=0:
  return await c.send("❌ `!quay 1000`")

 u=user(c.author.id,c.author.name)

 if u["cash"]<bet:
  return await c.send("❌ Không đủ tiền!")

 u["cash"]-=bet

 m=await c.send(embed=E(
  "🎰 MÁY SLOT | 🟠 ĐANG QUAY",
  "🎰 **ĐANG QUAY...**\n\n`[ ❔ | ❔ | ❔ ]`",
  ORANGE
 ))

 await asyncio.sleep(1.3)

 s=[
  random.choice(["🍒","🍋","🔔","⭐","💎","7️⃣"])
  for _ in range(3)
 ]

 same=max(s.count(x) for x in set(s))

 win=(
  same>=2 and
  random.randint(1,100)<=max(0,min(100,u["rate"]))
 )

 p=int(
  bet*(5 if same==3 else 2)*(1.5 if u["vip"] else 1)
 ) if win else 0

 if win:
  u["cash"]+=p

 await m.edit(embed=E(
  "🎰 MÁY SLOT | 🟢 KẾT QUẢ",
  f"`[ {' | '.join(s)} ]`\n\n"
  f"📢 **THÔNG BÁO**\n\n"
  f"{paytext(u,bet,win,p)}",
  GREEN if win else RED
 ))

# ================= TÙ XÌ =================

@bot.command()
async def tuxi(c,ch=None,bet:int=None):
 if await blocked(c):return

 if ch not in("bao","bua","keo") or not bet or bet<=0:
  return await c.send("❌ `!tuxi bao 1000`")

 u=user(c.author.id,c.author.name)

 if u["cash"]<bet:
  return await c.send("❌ Không đủ tiền!")

 u["cash"]-=bet
 b=random.choice(["bao","bua","keo"])

 win=(
  (ch=="bao" and b=="keo") or
  (ch=="bua" and b=="bao") or
  (ch=="keo" and b=="bua")
 )

 p=int(
  bet*2*(1.5 if u["vip"] else 1)
 ) if win else 0

 if win:
  u["cash"]+=p

 await c.send(embed=E(
  "✊ TÙ XÌ",
  f"👤 Bạn: **{ch.upper()}**    🤖 Bot: **{b.upper()}**\n\n"
  f"📢 **THÔNG BÁO**\n\n"
  f"{paytext(u,bet,win,p)}",
  GREEN if win else RED
 ))

# ================= VAY =================

@bot.command()
async def vay(c,m:discord.Member=None,n:int=None):
 if not m or not n or n<=0:
  return await c.send("❌ `!vay @User 1000`")

 if m.id==c.author.id:
  return await c.send("❌ Không thể vay chính mình!")

 b=user(c.author.id,c.author.name)
 l=user(m.id,m.name)

 if b["debt"]>0:
  return await c.send("❌ Bạn đang có khoản vay!")

 if l["cash"]<n:
  return await c.send("❌ Người cho vay không đủ tiền!")

 l["cash"]-=n
 b["cash"]+=n
 b["debt"]=n

 k=f"{c.author.id}_{m.id}_{time.time()}"
 LOANS[k]={"borrower":c.author.id,"lender":m.id}

 asyncio.create_task(loan_timer(k))

 await c.send(embed=E(
  "💰 KHOẢN VAY",
  f"👤 Người vay: {c.author.mention}\n"
  f"💰 Người cho vay: {m.mention}\n"
  f"💵 Số tiền: `{money(n)}`\n"
  f"⏱️ Hạn: **1 giờ**\n"
  f"⚠️ Quá hạn → **Nợ xấu -5% tỷ lệ thắng**",
  ORANGE
 ))

async def loan_timer(k):
 await asyncio.sleep(3600)
 x=LOANS.get(k)

 if x:
  u=user(x["borrower"])
  if u["debt"]>0:
   u["bad"]=1
   u["rate"]=max(0,u["rate"]-5)

@bot.command()
async def trano(c,m:discord.Member=None,n:int=None):
 if not m or not n or n<=0:
  return await c.send("❌ `!trano @User 1000`")

 b=user(c.author.id,c.author.name)
 l=user(m.id,m.name)

 if b["debt"]<=0:
  return await c.send("❌ Bạn không có khoản nợ!")

 if n!=b["debt"]:
  return await c.send(f"❌ Phải trả đủ `{money(b['debt'])}`!")

 if b["cash"]<n:
  return await c.send("❌ Ví không đủ tiền!")

 b["cash"]-=n
 l["cash"]+=n
 b["debt"]=0

 if b["bad"]:
  b["rate"]=min(WIN_RATE,b["rate"]+5)
  b["bad"]=0

 for k in list(LOANS):
  if LOANS[k]["borrower"]==c.author.id and LOANS[k]["lender"]==m.id:
   del LOANS[k]
   break

 await c.send(embed=E(
  "✅ TRẢ NỢ",
  f"👤 Người trả: {c.author.mention}\n"
  f"💰 Người nhận: {m.mention}\n"
  f"💵 Đã trả: `{money(n)}`\n"
  f"🎯 Tỷ lệ thắng: **{b['rate']}%**",
  GREEN
 ))

# ================= CODE =================

def newcode():
 return"BET-"+secrets.token_hex(3).upper()

@bot.command()
async def taocode(c,n:int=None,uses:int=None):
 if not admin(c):return await c.send("⛔ Chỉ Admin!")
 if not n or not uses:return await c.send("❌ `!taocode 1000 5`")

 x=newcode()
 C[x]={"money":n,"uses":uses,"used":set()}

 await c.send(embed=E(
  "🔐 TẠO CODE",
  f"🎟️ Mã: `{x}`\n💰 Tiền: `{money(n)}`\n👥 Lượt: `{uses}`",
  GREEN
 ))

@bot.command()
async def thuongcode(c,n:int=None,uses:int=None):
 if not admin(c):return await c.send("⛔ Chỉ Admin!")
 if not n or not uses:return await c.send("❌ `!thuongcode 1000 5`")

 x=newcode()
 C[x]={"money":n,"uses":uses,"used":set()}

 await c.send(embed=E(
  "🎁 THƯỞNG CODE",
  f"🎟️ Mã: `{x}`\n💰 Tiền: `{money(n)}`\n👥 Lượt: `{uses}`",
  GREEN
 ))

@bot.command()
async def nhapcode(c,x=None):
 z=C.get((x or "").upper())

 if not z:
  return await c.send("❌ Code không tồn tại!")

 if c.author.id in z["used"] or len(z["used"])>=z["uses"]:
  return await c.send("❌ Code hết lượt!")

 z["used"].add(c.author.id)
 u=user(c.author.id,c.author.name)
 u["cash"]+=z["money"]

 await c.send(embed=E(
  "🎁 NHẬN THƯỞNG",
  f"💰 Tiền thưởng: `{money(z['money'])}`\n"
  f"💳 Ví: `{money(u['cash'])}`",
  GREEN
 ))

# ================= ADMIN =================

@bot.command()
async def tyle(c,n:int=None):
 global WIN_RATE

 if not admin(c):
  return await c.send("⛔ Chỉ Admin!")

 if n is None or not 0<=n<=100:
  return await c.send("❌ `!tyle 0-100`")

 WIN_RATE=n

 for u in U.values():
  u["rate"]=max(0,n-5 if u["bad"] else n)

 await c.send(embed=E(
  "⚙️ CÀI TỶ LỆ",
  f"🎯 Hệ thống: **{n}%**\n"
  f"{'🚫 Không thắng.' if n==0 else '✅ Đã cập nhật tỷ lệ!'}",
  ORANGE
 ))

@bot.command()
async def settien(c,m:discord.Member=None,n:int=None):
 if not admin(c):
  return await c.send("⛔ Chỉ Admin!")

 if not m or n is None:
  return await c.send("❌ `!settien @User 10000`")

 user(m.id,m.name)["cash"]=max(0,n)

 await c.send(embed=E(
  "💰 SET TIỀN",
  f"👤 {m.mention}\n💵 Ví: `{money(n)}`",
  GREEN
 ))

@bot.command()
async def resettien(c,m:discord.Member=None):
 if not admin(c):
  return await c.send("⛔ Chỉ Admin!")

 if not m:
  return await c.send("❌ `!resettien @User`")

 u=user(m.id,m.name)
 u.update(cash=4899,bank=0,debt=0)

 await c.send(embed=E(
  "🔄 RESET TIỀN",
  f"👤 {m.mention}\n💵 Ví: `4,899$`",
  ORANGE
 ))

# ================= ERROR =================

@bot.event
async def on_command_error(c,e):
 if isinstance(e,commands.CommandNotFound):
  return

 if isinstance(
  e,
  (commands.MissingRequiredArgument,commands.BadArgument)
 ):
  return await c.send("❌ Sai/thiếu cú pháp. Dùng `!trogiup`.")

 if isinstance(e,commands.CheckFailure):
  return await c.send("⛔ Bạn không có quyền.")

# ================= START =================

bot.run(os.getenv("TOKEN_BOT"))
