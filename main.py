import os, random, asyncio, time, discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

users = {}
codes = {}
TX = {"on": False, "bets": {}}

START = 2000
ADMIN = "ADMIN"

def U(m):
if m.id not in users:
users[m.id] = {
"cash": START, "bank": 0, "role": "Không có",
"loan": 0, "due": 0, "daily": 0, "muted": False
}
return users[m.id]

def money(n):
return f"{n:,}$"

def E(title, text, color=0x3498DB):
return discord.Embed(title=title, description=text, color=color)

def admin(ctx):
return ctx.author.guild_permissions.administrator

def debt(u):
return u["loan"] > 0 and time.time() > u["due"]

def blocked(ctx):
u = U(ctx.author)
if u["muted"]:
return True
if debt(u):
asyncio.create_task(ctx.send(
"🔴 CON NỢ! Bạn đang quá hạn vay và không được chơi.\n"
"Dùng !trano số_tiền để trả nợ."
))
return True
return False

@bot.event
async def on_ready():
await bot.change_presence(
status=discord.Status.online,
activity=discord.Game("!trogiup | Casino")
)
print("BOT ONLINE:", bot.user)

================= HELP =================

@bot.command(name="trogiup")
async def trogiup(ctx):
t = (
"## 🎰 CASINO\n"
"!tx tai 100 • !tx xiu 100\n"
"!bc cua 100 • !bc tom 100\n"
"!xd chan 100 • !xd le 100\n"
"!quay 100\n\n"

"## 💰 TÀI KHOẢN\n"  
    "`!vi` • `!gui 100` • `!rut 100`\n"  
    "`!chuyen @user 100`\n"  
    "`!vay 1000` • `!trano 1000`\n"  
    "`!diemdanh` • `!bxh`\n\n"  

    "## 🛒 CỬA HÀNG\n"  
    "`!cuahang` • `!muan vip`\n"  
    "`!muan daigia` • `!muan typhu`\n\n"  

    "## 🎟️ CODE\n"  
    "`!nhapcode CODE`\n\n"  

    "## 🛡️ ADMIN\n"  
    "`!taocode tiền lượt`\n"  
    "`!settien @user số_tiền`\n"  
    "`!kick @user` • `!ban @user`\n"  
    "`!khoamom @user` • `!reset tien @user`"  
)  
await ctx.send(embed=E("🎰 CASINO BET88", t, 0x3498DB))

================= VÍ =================

@bot.command(name="vi")
async def vi(ctx, m: discord.Member=None):
m = m or ctx.author
u = U(m)
await ctx.send(embed=E(
f"💳 VÍ CỦA {m.display_name}",
f"💵 Tiền mặt: {money(u['cash'])}\n"
f"🏦 Ngân hàng: {money(u['bank'])}\n"
f"👑 Role: {u['role']}\n"
f"💸 Khoản vay: {money(u['loan'])}",
0x3498DB
))

@bot.command()
async def gui(ctx, amount:int=None):
if not amount or amount <= 0:
return await ctx.send("❌ !gui số_tiền")
u=U(ctx.author)
if amount > u["cash"]:
return await ctx.send("❌ Không đủ tiền.")
u["cash"]-=amount; u["bank"]+=amount
await ctx.send(embed=E("🏦 NGÂN HÀNG",
f"Đã gửi {money(amount)} vào ngân hàng.",0x2ECC71))

@bot.command()
async def rut(ctx, amount:int=None):
if not amount or amount<=0:
return await ctx.send("❌ !rut số_tiền")
u=U(ctx.author)
if amount>u["bank"]:
return await ctx.send("❌ Ngân hàng không đủ tiền.")
u["bank"]-=amount; u["cash"]+=amount
await ctx.send(embed=E("💵 RÚT TIỀN",
f"Đã rút {money(amount)}.",0x2ECC71))

@bot.command()
async def chuyen(ctx, m:discord.Member=None, amount:int=None):
if not m or not amount:
return await ctx.send("❌ !chuyen @user số_tiền")
if amount<1 or amount>10_000_000:
return await ctx.send("❌ Chỉ được 1$ - 10.000.000$.")
if m.id==ctx.author.id:
return await ctx.send("❌ Không thể chuyển cho chính mình.")
a,b=U(ctx.author),U(m)
if a["cash"]<amount:
return await ctx.send("❌ Không đủ tiền.")
a["cash"]-=amount; b["cash"]+=amount
await ctx.send(embed=E("💸 CHUYỂN TIỀN",
f"{ctx.author.mention} → {m.mention}\n"
f"💵 {money(amount)}",0x2ECC71))

================= VAY =================

@bot.command()
async def vay(ctx, amount:int=None):
if not amount or not 1000<=amount<=50000:
return await ctx.send("❌ Vay từ 1.000$ đến 50.000$.")
u=U(ctx.author)
if u["loan"]>0:
return await ctx.send("❌ Bạn đang có khoản vay.")
u["loan"]=amount
u["cash"]+=amount
u["due"]=time.time()+3600
await ctx.send(embed=E(
"💸 VAY TIỀN THÀNH CÔNG",
f"💵 Bạn đã vay: {money(amount)}\n"
"⏰ Thời hạn: 1 giờ\n"
"⚠️ Sau 1 giờ không trả sẽ thành CON NỢ và không được chơi.\n\n"
f"Trả bằng: !trano {amount}",0xF39C12))

@bot.command()
async def trano(ctx, amount:int=None):
u=U(ctx.author)
if u["loan"]<=0:
return await ctx.send("❌ Bạn không có khoản vay.")
if not amount or amount!=u["loan"]:
return await ctx.send(f"❌ Cần trả đúng {money(u['loan'])}.")
if u["cash"]<amount:
return await ctx.send("❌ Bạn không đủ tiền trả nợ.")
u["cash"]-=amount
u["loan"]=0; u["due"]=0
await ctx.send(embed=E(
"✅ ĐÃ TRẢ NỢ",
f"{ctx.author.mention} đã trả {money(amount)}.\n"
"🟢 Bạn đã được phép chơi lại!",0x2ECC71))

================= DAILY =================

@bot.command()
async def diemdanh(ctx):
u=U(ctx.author)
now=time.localtime()
today=now.tm_yday
if u["daily"]==today:
return await ctx.send("❌ Hôm nay bạn đã điểm danh rồi.")
reward=random.randint(1000,3000)
u["cash"]+=reward; u["daily"]=today
await ctx.send(embed=E(
"🎁 ĐIỂM DANH",
f"{ctx.author.mention}\n"
f"💰 Nhận {money(reward)}\n"
"⏰ Ngày mai quay lại nhận tiếp!",0x2ECC71))

================= BXH =================

@bot.command()
async def bxh(ctx):
arr=sorted(users.items(),key=lambda x:x[1]["cash"]+x[1]["bank"],reverse=True)[:5]
text=""
for i,(uid,u) in enumerate(arr,1):
m=ctx.guild.get_member(uid)
name=m.display_name if m else f"User {uid}"
total=u["cash"]+u["bank"]
text+=f"{i}. {name} — {money(total)}\n"
await ctx.send(embed=E("🏆 TOP 5 GIÀU NHẤT",text or "Chưa có dữ liệu.",0xF1C40F))

================= QUAY =================

@bot.command()
async def quay(ctx, amount:int=None):
if blocked(ctx): return
if not amount or amount<1:
return await ctx.send("❌ !quay số_tiền")
u=U(ctx.author)
if amount>u["cash"]:
return await ctx.send("❌ Bạn không đủ tiền.")
u["cash"]-=amount
s=["🍒","🍋","⭐","🔔","💎"]
a,b,c=[random.choice(s) for _ in range(3)]

msg=await ctx.send(embed=E(  
    "🎰  7️⃣7️⃣7️⃣  SLOT",  
    "🟨  `[ ❓ ]  [ ❓ ]  [ ❓ ]`",0xF39C12))  

await asyncio.sleep(.5)  
await msg.edit(embed=E(  
    "🎰  7️⃣7️⃣7️⃣  SLOT",  
    f"🟨  `[ {a} ]  [ ❓ ]  [ ❓ ]`",0xF39C12))  

await asyncio.sleep(.5)  
await msg.edit(embed=E(  
    "🎰  7️⃣7️⃣7️⃣  SLOT",  
    f"🟨  `[ {a} ]  [ {b} ]  [ ❓ ]`",0xF39C12))  

await asyncio.sleep(.5)  
await msg.edit(embed=E(  
    "🎰  7️⃣7️⃣7️⃣  SLOT",  
    f"🟨  `[ {a} ]  [ {b} ]  [ {c} ]`",0xF39C12))  

if a==b==c:  
    win=amount*5; u["cash"]+=win  
    result=f"🟢 **JACKPOT x5!**\n💰 Nhận **{money(win)}**"  
    col=0x2ECC71  
elif a==b or a==c or b==c:  
    win=int(amount*1.5); u["cash"]+=win  
    result=f"🟢 **2 HÌNH GIỐNG NHAU x1.5!**\n💰 Nhận **{money(win)}**"  
    col=0x2ECC71  
else:  
    result=f"🔴 **THUA!**\n💸 Mất **{money(amount)}**"  
    col=0xE74C3C  

await msg.edit(embed=E(  
    "🎰  7️⃣7️⃣7️⃣  SLOT",  
    f"`[ {a} ]  [ {b} ]  [ {c} ]`\n\n{result}",col))

================= BẦU CUA =================

@bot.command()
async def bc(ctx, choice:str=None, amount:int=None):
if blocked(ctx): return
icons={"ca":"🐟","tom":"🦐","cua":"🦀","bau":"🥒","ga":"🐓","nai":"🦌"}
if choice not in icons or not amount or amount<1:
return await ctx.send("❌ !bc ca/tom/cua/bau/ga/nai số_tiền")
u=U(ctx.author)
if amount>u["cash"]:
return await ctx.send("❌ Bạn không đủ tiền.")
u["cash"]-=amount

r=[random.choice(list(icons)) for _ in range(3)]  
board="  ".join(f"【 {icons[x]} 】" for x in r)  

msg=await ctx.send(embed=E(  
    "🎲  BẦU CUA",  
    "🟧 **ĐANG LẮC...**\n\n"  
    "【 ❓ 】  【 ❓ 】  【 ❓ 】",0xF39C12))  

await asyncio.sleep(1)  

count=r.count(choice)  
if count:  
    win=amount*(count+1); u["cash"]+=win  
    text=(f"{board}\n\n"  
          f"🟢 **TRÚNG {count} CON! x{count+1}**\n"  
          f"💰 Nhận **{money(win)}**")  
    col=0x2ECC71  
else:  
    text=f"{board}\n\n🔴 **THUA!**\n💸 Mất **{money(amount)}**"  
    col=0xE74C3C  

await msg.edit(embed=E("🎲  BẦU CUA",text,col))

================= XÓC ĐĨA =================

@bot.command()
async def xd(ctx, choice:str=None, amount:int=None):
if blocked(ctx): return
if choice not in ["chan","le"] or not amount or amount<1:
return await ctx.send("❌ !xd chan 100 hoặc !xd le 100")
u=U(ctx.author)
if amount>u["cash"]:
return await ctx.send("❌ Bạn không đủ tiền.")
u["cash"]-=amount

msg=await ctx.send(embed=E(  
    "🪙  XÓC ĐĨA",  
    "🥣 **Xóc... Xóc... Xóc...**",0xF39C12))  
await asyncio.sleep(1.5)  

balls=[random.randint(0,1) for _ in range(4)]  
n=sum(balls)  
result="chan" if n%2==0 else "le"  
board="  ".join("🔴" if x else "⚪" for x in balls)  

if choice==result:  
    u["cash"]+=amount*2  
    text=f"{board}\n\n🎯 Kết quả: **{result.upper()}**\n🔴 Số đỏ: **{n}**\n\n🟢 **THẮNG x2!**\n💰 Nhận **{money(amount*2)}**"  
    col=0x2ECC71  
else:  
    text=f"{board}\n\n🎯 Kết quả: **{result.upper()}**\n🔴 Số đỏ: **{n}**\n\n🔴 **THUA!**\n💸 Mất **{money(amount)}**"  
    col=0xE74C3C  

await msg.edit(embed=E("🪙  XÓC ĐĨA",text,col))

# ================= TÀI XỈU =================

async def tx_ket_thuc(ctx, msg):
    TX["on"] = False

    d = [random.randint(1, 6) for _ in range(3)]
    total = sum(d)
    result = "tai" if total >= 11 else "xiu"

    text = (
        "🎲 **KẾT QUẢ XÚC XẮC**\n\n"
        "╔══════════════════╗\n"
        f"      🎲 **{d[0]}  |  {d[1]}  |  {d[2]}**\n"
        "╚══════════════════╝\n\n"
        f"🎯 Tổng điểm: **{total}**\n"
        f"🏆 Kết quả: **{result.upper()}**\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
    )

    for uid, bet in TX["bets"].items():
        member = ctx.guild.get_member(uid)

        if not member:
            continue

        ch = bet["choice"]
        amount = bet["amount"]
        u = U(member)

        if ch == result:
            win = amount * 2
            u["cash"] += win

            text += (
                f"🟢 {member.mention}\n"
                f"   🎯 Cửa: **{ch.upper()}**\n"
                f"   💰 Thắng: **+{money(win)}**\n\n"
            )
        else:
            text += (
                f"🔴 {member.mention}\n"
                f"   🎯 Cửa: **{ch.upper()}**\n"
                f"   💸 Thua: **-{money(amount)}**\n\n"
            )

    TX["bets"] = {}

    await msg.edit(
        embed=E(
            "🎲 TÀI XỈU — KẾT QUẢ",
            text,
            0x2ECC71 if result in ["tai", "xiu"] else 0xE74C3C
        )
    )


@bot.command()
async def tx(ctx, choice: str = None, amount: int = None):
    if blocked(ctx):
        return

    if choice not in ["tai", "xiu"]:
        return await ctx.send(
            "❌ Dùng: `!tx tai số_tiền` hoặc `!tx xiu số_tiền`"
        )

    if not amount or not 100 <= amount <= 10_000_000:
        return await ctx.send(
            "❌ Số tiền cược: **100$ - 10.000.000$**."
        )

    u = U(ctx.author)

    if u["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền.")

    # ================= MỞ PHIÊN =================

    if not TX["on"]:
        TX["on"] = True
        TX["bets"] = {}

        u["cash"] -= amount

        TX["bets"][ctx.author.id] = {
            "choice": choice,
            "amount": amount
        }

        msg = await ctx.send(
            embed=E(
                "🎲 TÀI XỈU",
                f"👤 {ctx.author.mention}\n\n"
                f"🎯 Cửa cược: **{choice.upper()}**\n"
                f"💰 Tiền cược: **{money(amount)}**\n\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "🟠 **ĐANG NHẬN CƯỢC**\n\n"
                "⏱️ Còn **30 giây**\n"
                f"👥 Người đã cược: **{len(TX['bets'])}**\n\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "🎯 **TÀI** → `!tx tai số_tiền`\n"
                "🎯 **XỈU** → `!tx xiu số_tiền`\n\n"
                "⚠️ Mỗi người chỉ được cược **1 lần**.",
                0xF39C12
            )
        )

        # ================= ĐẾM NGƯỢC =================

        for left in [20, 10]:
            await asyncio.sleep(10)

            if not TX["on"]:
                return

            await msg.edit(
                embed=E(
                    "🎲 TÀI XỈU",
                    "🟠 **ĐANG NHẬN CƯỢC**\n\n"
                    "━━━━━━━━━━━━━━━━━━\n"
                    f"⏱️ Còn **{left} giây**\n"
                    f"👥 Người đã cược: **{len(TX['bets'])}**\n\n"
                    "🎯 **TÀI** → `!tx tai số_tiền`\n"
                    "🎯 **XỈU** → `!tx xiu số_tiền`\n\n"
                    "⚠️ Mỗi người chỉ được cược **1 lần**.",
                    0xF39C12
                )
            )

        await asyncio.sleep(10)

        if not TX["on"]:
            return

        # ================= KẾT QUẢ =================

        await tx_ket_thuc(ctx, msg)
        return

    # ================= PHIÊN ĐANG CHẠY =================

    if ctx.author.id in TX["bets"]:
        return await ctx.send(
            "❌ **Bạn đã cược rồi!**\n"
            "Mỗi người chỉ được cược **1 lần** trong phiên này."
        )

    u["cash"] -= amount

    TX["bets"][ctx.author.id] = {
        "choice": choice,
        "amount": amount
    }

    await ctx.send(
        embed=E(
            "🎯 ĐẶT CƯỢC THÀNH CÔNG",
            f"👤 {ctx.author.mention}\n\n"
            f"🎯 Cửa: **{choice.upper()}**\n"
            f"💰 Cược: **{money(amount)}**\n\n"
            "🟢 Bạn đã tham gia phiên Tài Xỉu.\n"
            "⚠️ Không thể cược thêm lần nữa.",
            0x2ECC71
        )
  )

================= CODE =================

@bot.command()
async def taocode(ctx, amount:int=None, uses:int=None):
if not admin(ctx): return await ctx.send("❌ Chỉ Admin.")
if not amount or not uses or amount<1 or uses<1:
return await ctx.send("❌ !taocode số_tiền số_lượt")
code="CASINO"+str(random.randint(100000,999999))
codes[code]=[amount,uses]
try:
await ctx.author.send(
f"🎟️ CODE CỦA BẠN\n"
f"{code}\n💰 {money(amount)}\n"
f"🔢 {uses} lượt")
await ctx.send("✅ Đã gửi code riêng cho bạn.")
except discord.Forbidden:
await ctx.send(f"❌ Không gửi DM được. Code: {code}")

@bot.command()
async def nhapcode(ctx, code:str=None):
if not code or code not in codes:
return await ctx.send("❌ Code không tồn tại.")
amount,uses=codes[code]
if uses<=0:
return await ctx.send("❌ Code đã hết lượt.")
U(ctx.author)["cash"]+=amount
codes[code][1]-=1
await ctx.send(embed=E(
"🎟️ NHẬP CODE THÀNH CÔNG",
f"💰 Bạn nhận {money(amount)}\n"
f"🔢 Còn {uses-1} lượt",0x2ECC71))

================= ADMIN =================

@bot.command()
async def settien(ctx, m:discord.Member=None, amount:int=None):
if not admin(ctx): return await ctx.send("❌ Chỉ Admin.")
if not m or amount is None:
return await ctx.send("❌ !settien @user số_tiền")
U(m)["cash"]=amount
await ctx.send(embed=E(
"🛡️ SET TIỀN",
f"{m.mention} → {money(amount)}",0x3498DB))

@bot.command()
async def kick(ctx,m:discord.Member=None):
if not admin(ctx): return await ctx.send("❌ Chỉ Admin.")
if not m: return await ctx.send("❌ !kick @user")
await m.kick()
await ctx.send(f"👢 Đã kick {m.mention}.")

@bot.command()
async def ban(ctx,m:discord.Member=None):
if not admin(ctx): return await ctx.send("❌ Chỉ Admin.")
if not m: return await ctx.send("❌ !ban @user")
await m.ban()
await ctx.send(f"🔨 Đã ban {m.mention}.")

@bot.command()
async def khoamom(ctx,m:discord.Member=None):
if not admin(ctx): return await ctx.send("❌ Chỉ Admin.")
if not m: return await ctx.send("❌ !khoamom @user")
u=U(m); u["muted"]=not u["muted"]
await ctx.send(
f"🔇 {m.mention} đã "
f"{'bị khóa mõm.' if u['muted'] else 'được mở khóa.'}")

@bot.command()
async def reset(ctx, what:str=None, m:discord.Member=None):
if not admin(ctx): return await ctx.send("❌ Chỉ Admin.")
if what!="tien" or not m:
return await ctx.send("❌ !reset tien @user")
U(m)["cash"]=START
U(m)["bank"]=0
await ctx.send(
f"♻️ Đã reset tiền của {m.mention} về {money(START)}.")

================= SHOP =================

@bot.command()
async def cuahang(ctx):
await ctx.send(embed=E(
"🛒 CỬA HÀNG ROLE",
"💛 VIP — 10.000.000$\n!muan vip\n\n"
"💙 ĐẠI GIA — 5.000.000$\n!muan daigia\n\n"
"💜 TỶ PHÚ — 1.000.000.000$\n!muan typhu",
0xF1C40F))

@bot.command()
async def muan(ctx,name:str=None):
prices={"vip":10_000_000,"daigia":5_000_000,"typhu":1_000_000_000}
names={"vip":"VIP","daigia":"Đại Gia","typhu":"Tỷ Phú"}
if name not in prices:
return await ctx.send("❌ !muan vip/daigia/typhu")
u=U(ctx.author)
if u["cash"]<prices[name]:
return await ctx.send("❌ Không đủ tiền.")
role=discord.utils.get(ctx.guild.roles,name=names[name])
if not role:
return await ctx.send(f"❌ Chưa có role {names[name]}.")
if role>=ctx.guild.me.top_role:
return await ctx.send("❌ Role cao hơn role bot.")
u["cash"]-=prices[name]
u["role"]=names[name]
try:
await ctx.author.add_roles(role)
except discord.Forbidden:
return await ctx.send("❌ Bot không có quyền gán role.")
await ctx.send(embed=E(
"👑 MUA ROLE THÀNH CÔNG",
f"{ctx.author.mention}\n"
f"Đã mua {names[name]} với giá {money(prices[name])}.",0x2ECC71))

================= START =================

TOKEN=os.getenv("TOKEN_BOT")

if not TOKEN:
print("❌ Không tìm thấy TOKEN_BOT!")
else:
bot.run(TOKEN) làm bản này sửa cái !tx của ảnh 1 sửa giống ảnh 2 nhé
