import os,asyncio,random,secrets,time,discord
from discord.ext import commands

I=discord.Intents.default();I.message_content=True
bot=commands.Bot(command_prefix="!",intents=I,help_command=None)
U={};C={};WIN_RATE=50
TX={"on":0,"bets":{},"tai":0,"xiu":0,"msg":None}
B,O,G,R,Y=0x3498DB,0xF1C40F,0x2ECC71,0xE74C3C,0xFFD700

def E(t,d,c=B):return discord.Embed(title=t,description=d,color=c)
def user(i,n="User"):
 if i not in U:
  U[i]={"name":n,"cash":4899,"bank":0,"debt":0,"vip":0,"dd":0,"rate":WIN_RATE}
 return U[i]
def adm(c):return c.author.guild_permissions.administrator
def M(n):return f"{int(n):,}$"

async def debt(c):
 u=user(c.author.id,c.author.name)
 if u["debt"]>0:
  await c.send(f"🚫 Bạn đang nợ **{M(u['debt'])}**!")
  return 1

def win(u,bet,m=2):
 p=int(bet*m*(1.5 if u["vip"] else 1))
 u["cash"]+=p
 return p

@bot.event
async def on_ready():
 await bot.change_presence(activity=discord.Game("!trogiup | Casino"))
 print("ONLINE",bot.user)

@bot.command(name="trogiup",aliases=["help"])
async def help(c):
 await c.send(embed=E("💎 BET88 | MENU","""🎰 **CASINO**

🎲 `!tx tai 1000` | `!tx xiu 1000`

🦀 `!bc cua 1000`

🪙 `!xd chan 1000` | `!xd le 1000`

🎰 `!quay 1000`

✊ `!tuxi bua 1000` | `keo` | `bao`

💳 **HỆ THỐNG**

💳 `!vi`
🏦 `!gui 1000`
💵 `!rut 1000`
💸 `!chuyen @user 1000`
🎁 `!diemdanh`
🏆 `!bxh`

🤝 **VAY NỢ**

`!vayno @user 1000`
`!trano @user 1000`

👑 **ADMIN**

`!taocode`
`!thuongcode`
`!nhapcode`
`!settien @user 10000`
`!resettien @user`
`!tyle 0-100`
`!muarole Vip`"""))

@bot.command()
async def vi(c,m:discord.Member=None):
 m=m or c.author
 u=user(m.id,m.name)
 await c.send(embed=E(
  "💳 TÀI KHOẢN",
  f"👤 **{m.name}**\n\n"
  f"💰 Ví: `{M(u['cash'])}`\n\n"
  f"🏦 Ngân hàng: `{M(u['bank'])}`\n\n"
  f"💸 Nợ: `{M(u['debt'])}`\n\n"
  f"🎯 Tỷ lệ thắng: `{u['rate']}%`",
  Y if u["vip"] else B
 ))

@bot.command()
async def gui(c,n:int=None):
 u=user(c.author.id,c.author.name)

 if not n or n<=0 or u["cash"]<n:
  return await c.send("❌ `!gui 1000` hoặc không đủ tiền!")

 u["cash"]-=n
 u["bank"]+=n

 await c.send(embed=E(
  "🏦 GỬI NGÂN HÀNG",
  f"💰 Gửi: `{M(n)}`\n\n"
  f"📈 Lãi suất: **2%/ngày**\n\n"
  f"💳 Ví: `{M(u['cash'])}`\n\n"
  f"🏦 Bank: `{M(u['bank'])}`",
  G
 ))

@bot.command()
async def rut(c,n:int=None):
 u=user(c.author.id,c.author.name)

 if not n or n<=0 or u["bank"]<n:
  return await c.send("❌ `!rut 1000` hoặc Bank không đủ!")

 u["bank"]-=n
 u["cash"]+=n

 await c.send(embed=E(
  "💵 RÚT NGÂN HÀNG",
  f"💰 Rút: `{M(n)}`\n\n"
  f"💳 Ví: `{M(u['cash'])}`\n\n"
  f"🏦 Bank: `{M(u['bank'])}`",
  G
 ))

@bot.command()
async def chuyen(c,m:discord.Member=None,n:int=None):
 if not m or not n or n<=0:
  return await c.send("❌ `!chuyen @User 1000`")

 a=user(c.author.id,c.author.name)
 b=user(m.id,m.name)

 if m.id==c.author.id or a["cash"]<n:
  return await c.send("❌ Không hợp lệ hoặc không đủ tiền!")

 a["cash"]-=n
 b["cash"]+=n

 await c.send(embed=E(
  "💸 CHUYỂN TIỀN",
  f"👤 Gửi: {c.author.mention}\n\n"
  f"👤 Nhận: {m.mention}\n\n"
  f"💰 Tiền: `{M(n)}`\n\n"
  f"💳 Ví: `{M(a['cash'])}`",
  G
 ))

@bot.command()
async def diemdanh(c):
 u=user(c.author.id,c.author.name)
 w=43200-(time.time()-u["dd"])

 if w>0:
  return await c.send(f"⌛ Đã điểm danh! Còn **{int(w)} giây**.")

 u["dd"]=time.time()
 u["cash"]+=2593

 await c.send(embed=E(
  "🎁 ĐIỂM DANH",
  f"✨ Thành công!\n\n"
  f"🎁 Nhận: `+2,593$`\n\n"
  f"💳 Ví: `{M(u['cash'])}`",
  G
 ))

@bot.command()
async def bxh(c):
 x=sorted(
  U.values(),
  key=lambda u:u["cash"]+u["bank"],
  reverse=True
 )[:5]

 text="\n".join(
  f"**{i}.** {u['name']} — `{M(u['cash']+u['bank'])}`"
  for i,u in enumerate(x,1)
 ) or "Chưa có người chơi."

 await c.send(embed=E("🏆 TOP 5",text))

@bot.command()
async def tx(c,ch=None,bet:int=None):
 if await debt(c):
  return

 if ch not in("tai","xiu") or not bet or bet<=0:
  return await c.send(
   "❌ `!tx tai 1000` hoặc `!tx xiu 1000`"
  )

 u=user(c.author.id,c.author.name)
 i=c.author.id

 if bet>10000000 or u["cash"]<bet:
  return await c.send("❌ Không đủ tiền hoặc quá giới hạn!")

 if i in TX["bets"]:
  return await c.send("❌ Bạn đã cược ván này!")

 if not TX["on"]:
  TX.update(on=1,bets={},tai=0,xiu=0)

  TX["msg"]=await c.send(embed=E(
   "🎲 SÒNG TÀI XỈU 30S 🎲",
   "Anh em Gõ `!tx <tai/xiu> <tiền>` để theo kèo !\n\n"
   "💰 Tối đa: `10,000,000$/ván`\n"
   "⏱️ Thời gian: `30 giây`\n\n"
   "💰 Tổng Tài: `0$` | Tổng Xỉu: `0$`",
   O
  ))

  asyncio.create_task(txround())

 u["cash"]-=bet

 TX["bets"][i]={
  "name":c.author.name,
  "choice":ch,
  "amount":bet
 }

 TX[ch]+=bet

 await TX["msg"].edit(embed=E(
  "🎲 SÒNG TÀI XỈU 30S 🎲",
  "Anh em Gõ `!tx <tai/xiu> <tiền>` để theo kèo !\n\n"
  "💰 Tối đa: `10,000,000$/ván`\n"
  "⏱️ Đang nhận cược...\n\n"
  f"💰 Tổng Tài: `{M(TX['tai'])}` | "
  f"Tổng Xỉu: `{M(TX['xiu'])}`",
  O
 ))

 try:
  await c.message.delete()
 except:
  pass

async def txround():
 await asyncio.sleep(30)

 d=[random.randint(1,6) for _ in range(3)]
 s=sum(d)
 r="tai" if s>=11 else"xiu"

 w=[]
 l=[]

 for i,b in TX["bets"].items():
  u=user(i)

  if b["choice"]==r and random.randint(1,100)<=u["rate"]:
   w.append(
    f"• {b['name']} `+{M(win(u,b['amount']))}`"
   )
  else:
   l.append(
    f"• {b['name']} `-{M(b['amount'])}`"
   )

 await TX["msg"].edit(embed=E(
  "🎲 KẾT QUẢ TÀI XỈU",
  f"🎲 Xúc xắc\n\n"
  f"[ {d[0]} ]  -  [ {d[1]} ]  -  [ {d[2]} ]\n\n"
  f"Kết quả: **{s} điểm ({r.upper()})**\n\n"
  f"🎉 **THẮNG**\n"
  f"{chr(10).join(w)or'Không có'}\n\n"
  f"💸 **THUA**\n"
  f"{chr(10).join(l)or'Không có'}",
  G if w else R
 ))

 TX.update(
  on=0,
  bets={},
  tai=0,
  xiu=0,
  msg=None
 )

@bot.command()
async def bc(c,ch=None,bet:int=None):
 a={
  "ca":"🐟",
  "tom":"🦐",
  "cua":"🦀",
  "bau":"🍐",
  "ga":"🐓",
  "nai":"🦌"
 }

 if ch not in a or not bet:
  return await c.send("❌ `!bc cua 1000`")

 if await debt(c):
  return

 u=user(c.author.id,c.author.name)

 if u["cash"]<bet:
  return await c.send("❌ Không đủ tiền!")

 u["cash"]-=bet

 m=await c.send(embed=E(
  "🦀 Lắc... Lắc... Lắc...",
  "🦀 Lắc... Lắc... Lắc...",
  O
 ))

 await asyncio.sleep(1.2)

 r=[random.choice(list(a))for _ in range(3)]
 n=r.count(ch)

 p=win(u,bet,n+1)if n else 0

 await m.edit(embed=E(
  "🦀 BẦU CUA",
  f"📢 THÔNG BÁO\n\n"
  f"[ {' | '.join(a[x]for x in r)} ]\n\n"
  f"Kết quả: **{' | '.join(a[x]for x in r)}**\n\n"
  f"Bạn chọn: **{a[ch]} {ch.upper()}**\n\n"
  f"{'🏆 BẠN THẮNG!'if n else'💸 BẠN THUA!'}\n\n"
  f"💰 Tiền cược: `{M(bet)}`\n\n"
  f"🎉 Tiền thắng: `+{M(p)}`\n\n"
  f"💳 Ví: `{M(u['cash'])}`",
  G if n else R
 ))

@bot.command()
async def xd(c,ch=None,bet:int=None):
 if ch not in("chan","le")or not bet:
  return await c.send(
   "❌ `!xd chan 1000` hoặc `!xd le 1000`"
  )

 if await debt(c):
  return

 u=user(c.author.id,c.author.name)

 if u["cash"]<bet:
  return await c.send("❌ Không đủ tiền!")

 u["cash"]-=bet

 m=await c.send(embed=E(
  "🪙 Xóc... Xóc... Xóc...",
  "🪙 Xóc... Xóc... Xóc...",
  O
 ))

 await asyncio.sleep(1.2)

 n=random.randint(0,4)
 cups=["⚪"]*4

 for i in random.sample(range(4),n):
  cups[i]="🔴"

 r="chan"if n%2==0 else"le"

 ok=(
  r==ch and
  random.randint(1,100)<=u["rate"]
 )

 p=win(u,bet)if ok else 0

 await m.edit(embed=E(
  "🪙 XÓC ĐĨA",
  f"📢 THÔNG BÁO\n\n"
  f"[ {' | '.join(cups)} ]\n\n"
  f"Kết quả: **{r.upper()}**\n\n"
  f"Bạn chọn: **{ch.upper()}**\n\n"
  f"{'🏆 BẠN THẮNG!'if ok else'💸 BẠN THUA!'}\n\n"
  f"💰 Tiền cược: `{M(bet)}`\n\n"
  f"🎉 Tiền thắng: `+{M(p)}`\n\n"
  f"💳 Ví: `{M(u['cash'])}`",
  G if ok else R
 ))

@bot.command()
async def quay(c,bet:int=None):
 if await debt(c):
  return

 u=user(c.author.id,c.author.name)

 if not bet or bet<=0 or u["cash"]<bet:
  return await c.send(
   "❌ `!quay 1000` hoặc không đủ tiền!"
  )

 u["cash"]-=bet

 m=await c.send(embed=E(
  "🎰 Đang quay...",
  "🎰 Đang quay...",
  O
 ))

 await asyncio.sleep(1.3)

 s=[
  random.choice(["🍒","🍋","🔔","⭐","💎","7️⃣"])
  for _ in range(3)
 ]

 same=max(s.count(x)for x in set(s))

 ok=(
  same>=2 and
  random.randint(1,100)<=u["rate"]
 )

 p=win(
  u,
  bet,
  5 if same==3 else 2
 )if ok else 0

 await m.edit(embed=E(
  "🎰 QUAY",
  f"📢 THÔNG BÁO\n\n"
  f"[ {' | '.join(s)} ]\n\n"
  f"Kết quả: **"
  f"{'NỔ HŨ'if same==3 else'THẮNG'if ok else'THUA'}**\n\n"
  f"{'🏆 BẠN THẮNG!'if ok else'💸 BẠN THUA!'}\n\n"
  f"💰 Tiền cược: `{M(bet)}`\n\n"
  f"🎉 Tiền thắng: `+{M(p)}`\n\n"
  f"💳 Ví: `{M(u['cash'])}`",
  G if ok else R
 ))

@bot.command()
async def tuxi(c,ch=None,bet:int=None):
 if ch not in("bua","keo","bao")or not bet:
  return await c.send(
   "❌ `!tuxi bua 1000` | `keo` | `bao`"
  )

 if await debt(c):
  return

 u=user(c.author.id,c.author.name)
 botc=random.choice(["bua","keo","bao"])

 if u["cash"]<bet:
  return await c.send("❌ Không đủ tiền!")

 ico={
  "bua":"🪨 BÚA",
  "keo":"✌️ KÉO",
  "bao":"✋ BAO"
 }

 ok=(ch,botc)in[
  ("bua","keo"),
  ("keo","bao"),
  ("bao","bua")
 ]

 draw=ch==botc

 u["cash"]-=bet

 if draw:
  u["cash"]+=bet
  p=0
 else:
  p=win(u,bet)if ok else 0

 await c.send(embed=E(
  "✊ TÙ XÌ",
  f"📢 THÔNG BÁO\n\n"
  f"👤 Bạn: {ico[ch]}    🤖 Bot: {ico[botc]}\n\n"
  f"Kết quả: **"
  f"{'HÒA'if draw else'BẠN THẮNG'if ok else'BOT THẮNG'}**\n\n"
  f"Bạn chọn: **{ico[ch]}**\n\n"
  f"{'🤝 HÒA!'if draw else'🏆 BẠN THẮNG!'if ok else'💸 BẠN THUA!'}\n\n"
  f"💰 Tiền cược: `{M(bet)}`\n\n"
  f"🎉 Tiền thắng: `+{M(p)}`\n\n"
  f"💳 Ví: `{M(u['cash'])}`",
  G if ok else O if draw else R
 ))

def code():
 return"BET-"+secrets.token_hex(3).upper()

@bot.command()
async def taocode(c,n:int=None,uses:int=None):
 if not adm(c):
  return await c.send("⛔ Chỉ Admin!")

 if not n or not uses:
  return await c.send("❌ `!taocode 1000 1`")

 x=code()

 C[x]={
  "money":n,
  "uses":uses,
  "used":set()
 }

 try:
  await c.author.send(
   f"🔐 `{x}` | 💰 `{M(n)}` | 👥 `{uses}`"
  )
 except:
  pass

 await c.send("✅ Code đã gửi DM!")

@bot.command()
async def thuongcode(c,n:int=None,uses:int=None):
 if not adm(c):
  return await c.send("⛔ Chỉ Admin!")

 if not n or not uses:
  return await c.send("❌ `!thuongcode 1000 5`")

 x=code()

 C[x]={
  "money":n,
  "uses":uses,
  "used":set()
 }

 await c.send(embed=E(
  "🎁 PHẦN THƯỞNG CODE",
  f"🔐 Mã: `{x}`\n\n"
  f"💰 Tiền: `{M(n)}`\n\n"
  f"👥 Lượt: `{uses}`",
  G
 ))

@bot.command()
async def nhapcode(c,x=None):
 z=C.get((x or"").upper())

 if not z or c.author.id in z["used"]or len(z["used"])>=z["uses"]:
  return await c.send(
   "❌ Code không tồn tại hoặc hết lượt!"
  )

 z["used"].add(c.author.id)

 user(
  c.author.id,
  c.author.name
 )["cash"]+=z["money"]

 await c.send(
  f"🎁 **+{M(z['money'])} vào ví!**"
 )

@bot.command()
async def settien(c,m:discord.Member=None,n:int=None):
 if not adm(c):
  return await c.send("⛔ Chỉ Admin!")

 if not m or n is None:
  return await c.send(
   "❌ `!settien @User 10000`"
  )

 user(m.id,m.name)["cash"]=max(0,n)

 await c.send(embed=E(
  "💰 SET TIỀN",
  f"👤 {m.mention}\n\n"
  f"💵 Ví mới: `{M(n)}`",
  G
 ))

@bot.command()
async def resettien(c,m:discord.Member=None):
 if not adm(c):
  return await c.send("⛔ Chỉ Admin!")

 if not m:
  return await c.send(
   "❌ `!resettien @User`"
  )

 u=user(m.id,m.name)
 u["cash"]=4899
 u["bank"]=0

 await c.send(embed=E(
  "🔄 RESET TIỀN",
  f"👤 {m.mention}\n\n"
  f"💵 Ví: `4,899$`\n\n"
  f"🏦 Bank: `0$`",
  O
 ))

@bot.command()
async def tyle(c,n:int=None):
 global WIN_RATE

 if not adm(c):
  return await c.send("⛔ Chỉ Admin!")

 if n is None or not 0<=n<=100:
  return await c.send(
   "❌ `!tyle 0` đến `!tyle 100`"
  )

 WIN_RATE=n

 for u in U.values():
  u["rate"]=n

 await c.send(embed=E(
  "📊 TỶ LỆ THẮNG",
  f"🎯 Hệ thống: **{n}%**\n\n"
  f"{'🟢 AUTO THẮNG'if n==100 else'🔴 AUTO THUA'if n==0 else'🟡 XÁC SUẤT '+str(n)+'%'}",
  O
 ))

@bot.command()
async def muarole(c,r=None):
 if(r or"").lower()!="vip":
  return await c.send(
   "❌ `!muarole Vip`"
  )

 u=user(c.author.id,c.author.name)

 role=discord.utils.find(
  lambda x:x.name.lower()=="vip",
  c.guild.roles
 )

 if u["vip"] or u["cash"]<30000000 or not role:
  return await c.send(
   "❌ Đã có VIP, thiếu tiền hoặc chưa có role Vip!"
  )

 u["cash"]-=30000000
 u["vip"]=1

 try:
  await c.author.add_roles(role)
 except:
  return await c.send("❌ Bot thiếu quyền!")

 await c.send(embed=E(
  "👑 MUA VIP",
  f"🎉 {c.author.mention} đã thành **VIP!**\n\n"
  f"💰 Giá: `30,000,000$`\n\n"
  f"💵 Thưởng: **x1.5**",
  Y
 ))

@bot.command()
async def vayno(c,m:discord.Member=None,n:int=None):
 if not m or not n or n<=0 or m.id==c.author.id:
  return await c.send(
   "❌ `!vayno @User 1000`"
  )

 b=user(c.author.id,c.author.name)
 l=user(m.id,m.name)

 if b["debt"] or l["cash"]<n:
  return await c.send(
   "❌ Không thể vay hoặc người cho vay thiếu tiền!"
  )

 l["cash"]-=n
 b["cash"]+=n
 b["debt"]=n

 await c.send(embed=E(
  "🤝 KHOẢN VAY",
  f"👤 Người vay: {c.author.mention}\n\n"
  f"🤝 Người cho vay: {m.mention}\n\n"
  f"💰 Số tiền: `{M(n)}`\n\n"
  f"⏱️ Hạn: **1 giờ**",
  O
 ))

@bot.command()
async def trano(c,m:discord.Member=None,n:int=None):
 if not m or not n:
  return await c.send(
   "❌ `!trano @User 1000`"
  )

 b=user(c.author.id,c.author.name)
 l=user(m.id,m.name)

 if b["debt"]<=0 or n!=b["debt"] or b["cash"]<n:
  return await c.send(
   "❌ Phải trả đủ nợ và ví đủ tiền!"
  )

 b["cash"]-=n
 l["cash"]+=n
 b["debt"]=0
 b["rate"]=WIN_RATE

 await c.send(embed=E(
  "💵 TRẢ NỢ",
  f"👤 Người trả: {c.author.mention}\n\n"
  f"👤 Người nhận: {m.mention}\n\n"
  f"💰 Đã trả: `{M(n)}`\n\n"
  f"🎯 Tỷ lệ thắng: `{b['rate']}%`",
  G
 ))

token=os.getenv("TOKEN_BOT")

if token:
 bot.run(token)
else:
 print("❌ Chưa có TOKEN_BOT!")
