import os,asyncio,random,secrets,time,discord
from discord.ext import commands

I=discord.Intents.default();I.message_content=True
bot=commands.Bot(command_prefix="!",intents=I,help_command=None)

U={};C={};LOAN={};BANK_RATE=.02
TX={"on":0,"bets":{},"tai":0,"xiu":0,"msg":None}

BLUE=0x3498DB;ORANGE=0xF1C40F;GREEN=0x2ECC71;RED=0xE74C3C;GOLD=0xFFD700

def E(t,d,c=BLUE):
    return discord.Embed(title=t,description=d,color=c)

def user(i,n="Thành viên"):
    if i not in U:
        U[i]={"name":n,"cash":4899,"bank":0,"vip":0,"dd":0,"rate":100,"debt":0,"bad":0}
    return U[i]

def money(n): return f"{int(n):,}$"
def adm(c): return c.author.guild_permissions.administrator

async def blocked(c):
    u=user(c.author.id,c.author.name)
    if u["debt"]:
        await c.send(f"🚫 Bạn đang nợ **{money(u['debt'])}**!\n💡 Hãy trả nợ trước.")
        return True
    return False

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("!trogiup | BET88"))
    print("ONLINE:",bot.user)

# ===== MENU =====
@bot.command(aliases=["help"])
async def trogiup(c):
    await c.send(embed=E("🎰 BET88 | MENU",
"""🎲 `!tx tai 1000` `!tx xiu 1000`
🦀 `!bc cua 1000`  🪙 `!xd chan 1000`
🎰 `!quay 1000`     ✊ `!tuxi bua 1000`

💳 `!vi`  🎁 `!diemdanh`
🏦 `!gui 1000`  💵 `!rut 1000`
💸 `!chuyen @User 1000`

🤝 `!vayno @User 1000`
💵 `!trano @User 1000`

👑 `!taocode` `!thuongcode`
💰 `!settien @User 10000`
🔄 `!resettien @User`
⚙️ `!tyle 0-100`"""))

# ===== VI =====
@bot.command()
async def vi(c):
    u=user(c.author.id,c.author.name)
    lai=int(u["bank"]*BANK_RATE)
    await c.send(embed=E("💳 TÀI KHOẢN",
f"""👤 {c.author.mention}
🏷️ {'👑 VIP' if u['vip'] else '🐥 Người chơi Thường'}

💰 Ví: `{money(u['cash'])}`
🏦 Ngân hàng: `{money(u['bank'])}`
📈 Lãi suất: `2%/ngày`
💵 Lãi dự kiến: `+{money(lai)}`
💸 Nợ: `{money(u['debt'])}`
🎯 Tỷ lệ thắng: `{u['rate']}%`""",GOLD if u["vip"] else BLUE))

# ===== BANK =====
@bot.command()
async def gui(c,n:int=None):
    u=user(c.author.id,c.author.name)
    if not n or n<=0 or n>u["cash"]: return await c.send("❌ Số tiền không hợp lệ!")
    u["cash"]-=n;u["bank"]+=n
    await c.send(embed=E("🏦 GỬI TIỀN",
f"""💰 Số tiền gửi: `{money(n)}`

💳 Ví: `{money(u['cash'])}`
🏦 Ngân hàng: `{money(u['bank'])}`

📈 Lãi suất: **2%/ngày**
✅ Giao dịch thành công!""",GREEN))

@bot.command()
async def rut(c,n:int=None):
    u=user(c.author.id,c.author.name)
    if not n or n<=0 or n>u["bank"]: return await c.send("❌ Bank không đủ tiền!")
    u["bank"]-=n;u["cash"]+=n
    await c.send(embed=E("💵 RÚT TIỀN",
f"""💰 Số tiền rút: `{money(n)}`

💳 Ví: `{money(u['cash'])}`
🏦 Ngân hàng: `{money(u['bank'])}`

✅ Giao dịch thành công!""",GREEN))

# ===== CHUYEN =====
@bot.command()
async def chuyen(c,m:discord.Member=None,n:int=None):
    if not m or not n or n<=0:return await c.send("❌ `!chuyen @User 1000`")
    a=user(c.author.id,c.author.name);b=user(m.id,m.name)
    if m.id==c.author.id or n>a["cash"]:return await c.send("❌ Không thể chuyển/không đủ tiền!")
    a["cash"]-=n;b["cash"]+=n
    await c.send(embed=E("💸 CHUYỂN TIỀN",
f"""👤 Người gửi: {c.author.mention}
👤 Người nhận: {m.mention}

💰 Số tiền: `{money(n)}`
💳 Ví còn: `{money(a['cash'])}`

✅ Chuyển thành công!""",GREEN))

# ===== DIEM DANH =====
@bot.command()
async def diemdanh(c):
    u=user(c.author.id,c.author.name);now=time.time()
    if now-u["dd"]<43200:return await c.send("⌛ Bạn đã điểm danh! Hãy quay lại sau.")
    u["dd"]=now;u["cash"]+=2593
    await c.send(embed=E("🎁 ĐIỂM DANH",
f"""✨ Điểm danh thành công!

🎁 Phần thưởng: `+2,593$`
💳 Ví: `{money(u['cash'])}`""",GREEN))

# ===== TX =====
@bot.command()
async def tx(c,ch=None,bet:int=None):
    if ch not in ("tai","xiu") or not bet or bet<=0:return await c.send("❌ `!tx tai 1000` hoặc `!tx xiu 1000`")
    if await blocked(c):return
    u=user(c.author.id,c.author.name);i=c.author.id
    if u["cash"]<bet:return await c.send("❌ Không đủ tiền!")
    if i in TX["bets"]:return await c.send("❌ Bạn đã cược!")
    if not TX["on"]:
        TX.update(on=1,bets={},tai=0,xiu=0)
        TX["msg"]=await c.send(embed=E("🎲 SÒNG TÀI XỈU 30S 🎲",
"""📢 Anh em Gõ `!tx <tai/xiu> <tiền>` để theo kèo !

💰 Cược tối đa: `10,000,000$/ván`
⏱️ Thời gian: `30 giây`

💰 Tổng Tài: `0$` | Tổng Xỉu: `0$`""",ORANGE))
        asyncio.create_task(txround())
    u["cash"]-=bet;TX["bets"][i]={"name":c.author.name,"choice":ch,"amount":bet};TX[ch]+=bet
    await TX["msg"].edit(embed=E("🎲 SÒNG TÀI XỈU 30S 🎲",
f"""📢 Anh em Gõ `!tx <tai/xiu> <tiền>` để theo kèo !

💰 Cược tối đa: `10,000,000$/ván`
⏱️ Thời gian: `30 giây`

💰 Tổng Tài: `{money(TX['tai'])}` | Tổng Xỉu: `{money(TX['xiu'])}`""",ORANGE))

async def txround():
    await asyncio.sleep(30)
    d=[random.randint(1,6) for _ in range(3)];total=sum(d);r="tai" if total>=11 else "xiu";w=[];l=[]
    for i,b in TX["bets"].items():
        u=user(i)
        if b["choice"]==r and random.randint(1,100)<=u["rate"]:
            p=int(b["amount"]*2*(1.5 if u["vip"] else 1));u["cash"]+=p;w.append(f"• {b['name']} `+{money(p)}`")
        else:l.append(f"• {b['name']} `-{money(b['amount'])}`")
    await TX["msg"].edit(embed=E("🎲 KẾT QUẢ TÀI XỈU",
f"""📢 THÔNG BÁO

🎲 Xúc xắc
`[ {d[0]} ] - [ {d[1]} ] - [ {d[2]} ]`

➡️ **{total} điểm ({r.upper()})**

🎉 **THẮNG**
{chr(10).join(w) or 'Không có'}

💸 **THUA**
{chr(10).join(l) or 'Không có'}""",GREEN if w else RED))
    TX.update(on=0,bets={},tai=0,xiu=0,msg=None)

# ===== GAME =====
async def game(c,title,bet,rolling,make):
    if await blocked(c):return
    u=user(c.author.id,c.author.name)
    if not bet or bet<=0 or bet>u["cash"]:return await c.send("❌ Tiền cược không hợp lệ!")
    u["cash"]-=bet
    m=await c.send(embed=E(title,rolling,ORANGE))
    await asyncio.sleep(1.3)
    text,p=make(u,bet)
    await m.edit(embed=E(title,text,GREEN if p else RED))

@bot.command()
async def bc(c,ch=None,bet:int=None):
    a={"ca":"🐟","tom":"🦐","cua":"🦀","bau":"🍐","ga":"🐓","nai":"🦌"}
    if ch not in a:return await c.send("❌ `!bc cua 1000`")
    def f(u,b):
        r=[random.choice(list(a)) for _ in range(3)];n=r.count(ch);p=int(b*(n+1)*(1.5 if u["vip"] else 1)) if n else 0
        if p:u["cash"]+=p
        return f"""📢 THÔNG BÁO

`[ {' | '.join(a[x] for x in r)} ]`

📢 Kết quả: {'🎉 THẮNG!' if p else '💀 THUA!'}

💰 Tiền cược: {money(b)}

🏆 Tiền thắng: {money(p)}

💳 Ví: {money(u['cash'])}""",p
    await game(c,"🦀 BẦU CUA",bet,"🟠 Lắc... Lắc... Lắc...",f)

@bot.command()
async def xd(c,ch=None,bet:int=None):
    if ch not in ("chan","le"):return await c.send("❌ `!xd chan 1000`")
    def f(u,b):
        n=random.randint(0,4);q=["⚪"]*4
        for i in random.sample(range(4),n):q[i]="🔴"
        r="chan" if n%2==0 else "le";p=int(b*2*(1.5 if u["vip"] else 1)) if r==ch and random.randint(1,100)<=u["rate"] else 0
        if p:u["cash"]+=p
        return f"""📢 THÔNG BÁO

`[ {' | '.join(q)} ]`

📢 Kết quả: **{r.upper()}** — {'🎉 THẮNG!' if p else '💀 THUA!'}

💰 Tiền cược: {money(b)}

🏆 Tiền thắng: {money(p)}

💳 Ví: {money(u['cash'])}""",p
    await game(c,"🪙 XÓC ĐĨA",bet,"🟠 Xóc... Xóc... Xóc...",f)

@bot.command()
async def quay(c,bet:int=None):
    def f(u,b):
        s=[random.choice(["🍒","🍋","🔔","⭐","💎","7️⃣"]) for _ in range(3)];same=max(s.count(x) for x in set(s));p=int(b*(5 if same==3 else 2)*(1.5 if u["vip"] else 1)) if same>=2 and random.randint(1,100)<=u["rate"] else 0
        if p:u["cash"]+=p
        return f"""📢 THÔNG BÁO

`[ {' | '.join(s)} ]`

📢 Kết quả: {'🎉 THẮNG!' if p else '💀 THUA!'}

💰 Tiền cược: {money(b)}

🏆 Tiền thắng: {money(p)}

💳 Ví: {money(u['cash'])}""",p
    await game(c,"🎰 QUAY",bet,"🟠 Đang quay...",f)

@bot.command()
async def tuxi(c,ch=None,bet:int=None):
    if ch not in ("bao","bua","keo"):return await c.send("❌ `!tuxi bua 1000`")
    def f(u,b):
        botc=random.choice(["bao","bua","keo"]);win=(ch,botc) in [("bua","keo"),("keo","bao"),("bao","bua")];p=b*2 if win else 0
        if p:u["cash"]+=p
        icon={"bao":"🖐️","bua":"✊","keo":"✌️"}
        return f"""📢 THÔNG BÁO

👤 Bạn: {icon[ch]} {ch.upper()}
🤖 Bot: {icon[botc]} {botc.upper()}

📢 Kết quả: {'🎉 BẠN THẮNG!' if p else '💀 BẠN THUA!'}

💰 Tiền cược: {money(b)}

🏆 Tiền thắng: {money(p)}

💳 Ví: {money(u['cash'])}""",p
    await game(c,"✊ TÙ XÌ",bet,"🟠 Chuẩn bị...",f)

# ===== VAY =====
@bot.command()
async def vayno(c,m:discord.Member=None,n:int=None):
    if not m or not n or n<=0:return await c.send("❌ `!vayno @User 1000`")
    a=user(c.author.id,c.author.name);b=user(m.id,m.name)
    if a["debt"] or b["cash"]<n:return await c.send("❌ Không thể vay!")
    b["cash"]-=n;a["cash"]+=n;a["debt"]=n;LOAN[c.author.id]=m.id
    await c.send(embed=E("💰 KHOẢN VAY",
f"""👤 Người vay: {c.author.mention}
🤝 Người cho vay: {m.mention}

💵 Khoản vay: `{money(n)}`
⏱️ Thời hạn: **1 giờ**

⚠️ Quá hạn → Nợ xấu -5% tỷ lệ thắng""",ORANGE))

@bot.command()
async def trano(c,m:discord.Member=None):
    if not m:return await c.send("❌ `!trano @User`")
    a=user(c.author.id,c.author.name);b=user(m.id,m.name)
    if a["debt"]<=0 or a["cash"]<a["debt"]:return await c.send("❌ Không đủ tiền trả nợ!")
    n=a["debt"];a["cash"]-=n;b["cash"]+=n;a["debt"]=0;a["bad"]=0
    await c.send(embed=E("💵 TRẢ NỢ",
f"""👤 Người trả: {c.author.mention}
🤝 Người nhận: {m.mention}

💰 Số tiền trả: `{money(n)}`
💳 Ví còn: `{money(a['cash'])}`

✅ Đã thanh toán khoản vay!""",GREEN))

# ===== ADMIN =====
@bot.command()
async def tyle(c,n:int=None):
    if not adm(c):return await c.send("⛔ Chỉ Admin!")
    if n is None or not 0<=n<=100:return await c.send("❌ `!tyle 0-100`")
    for u in U.values():u["rate"]=n
    await c.send(embed=E("⚙️ CÀI TỶ LỆ THẮNG",f"🎯 Tỷ lệ hệ thống: **{n}%**\n\n✅ Đã cập nhật!",ORANGE))

@bot.command()
async def settien(c,m:discord.Member=None,n:int=None):
    if not adm(c):return await c.send("⛔ Chỉ Admin!")
    if not m or n is None:return await c.send("❌ `!settien @User 10000`")
    user(m.id,m.name)["cash"]=max(0,n)
    await c.send(embed=E("💰 SET TIỀN",f"👤 {m.mention}\n💳 Ví mới: `{money(n)}`",GREEN))

@bot.command()
async def resettien(c,m:discord.Member=None):
    if not adm(c):return await c.send("⛔ Chỉ Admin!")
    if not m:return await c.send("❌ `!resettien @User`")
    U[m.id]={"name":m.name,"cash":4899,"bank":0,"vip":0,"dd":0,"rate":100,"debt":0,"bad":0}
    await c.send(embed=E("🔄 RESET TIỀN",f"👤 {m.mention}\n💳 Ví: `4,899$`",ORANGE))

# ===== CODE =====
def code():return "BET-"+secrets.token_hex(3).upper()

@bot.command()
async def thuongcode(c,n:int=None,uses:int=None):
    if not adm(c):return await c.send("⛔ Chỉ Admin!")
    if not n or not uses:return await c.send("❌ `!thuongcode 1000 5`")
    x=code();C[x]={"money":n,"uses":uses,"used":set()}
    await c.send(embed=E("🎁 PHẦN THƯỞNG CODE",f"🔐 Mã: `{x}`\n💰 Tiền: `{money(n)}`\n👥 Lượt: `{uses}`",GREEN))

@bot.command()
async def taocode(c,n:int=None,uses:int=None):
    if not adm(c):return await c.send("⛔ Chỉ Admin!")
    if not n or not uses:return await c.send("❌ `!taocode 1000 1`")
    x=code();C[x]={"money":n,"uses":uses,"used":set()}
    try:await c.author.send(f"🔐 `{x}` | 💰 `{money(n)}` | 👥 `{uses}`")
    except:pass
    await c.send("✅ Code đã gửi DM!")

@bot.command()
async def nhapcode(c,x=None):
    x=(x or "").upper()
    if x not in C:return await c.send("❌ Code không tồn tại!")
    z=C[x]
    if c.author.id in z["used"] or len(z["used"])>=z["uses"]:return await c.send("❌ Code hết lượt!")
    z["used"].add(c.author.id);user(c.author.id,c.author.name)["cash"]+=z["money"]
    await c.send(f"🎁 **+{money(z['money'])} vào ví!**")

bot.run(os.getenv("TOKEN_BOT"))
