import os,asyncio,random,time,secrets,discord
from discord.ext import commands

I=discord.Intents.default();I.message_content=True
bot=commands.Bot(command_prefix="!",intents=I,help_command=None)

users,codes,cool={}, {},{}
DEFAULT=4899
BLUE,ORANGE,GREEN,RED=0x3498DB,0xF1C40F,0x2ECC71,0xE74C3C
tx={"active":False,"bets":{},"tai":0,"xiu":0,"msg":None}

def E(t,d,c):return discord.Embed(title=t,description=d,color=c)

def U(i,n="Thành viên"):
    if i not in users:
        users[i]={"name":n,"cash":DEFAULT,"bank":0,
                  "hang":"Người chơi Thường","ga":"Gà Công Nghiệp 🐥"}
    return users[i]

def CD(i,x,s=1.5):
    k=f"{i}{x}";n=time.time()
    if k in cool and n-cool[k]<s:return 1
    cool[k]=n

def ADM(c):return c.author.guild_permissions.administrator

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("!trogiup | Casino Bet88"))
    print("BOT ONLINE:",bot.user)

# ============ HELP ============
@bot.command(name="trogiup",aliases=["help"])
async def help(c):
    await c.send(embed=E("🎰 CASINO BET88",
"""**🎲 CASINO**
`!tx tai 100` `!tx xiu 100`
`!bc cua 100` `!quay 100` `!xd chan 100`

**💰 HỆ THỐNG**
`!vi` `!gui 100` `!rut 100`
`!chuyen @user 100` `!diemdanh` `!bxh`
`!nhapcode CODE`

**👑 ADMIN**
`!taocode 10000 1`
`!thuongcode 10000 10`
`!settien @user 10000`
`!resettien @user`""",BLUE))

# ============ VI ============
@bot.command(name="vi",aliases=["money","bal"])
async def vi(c,m:discord.Member=None):
    m=m or c.author;u=U(m.id,m.name)
    await c.send(embed=E("💳 THÔNG TIN TÀI KHOẢN",
        f"👤 **{m.name.upper()}**\n🏷️ {u['hang']}\n🐓 {u['ga']}\n\n"
        f"💵 Tiền mặt: `{u['cash']:,}$`\n🏦 Ngân hàng: `{u['bank']:,}$`",BLUE))

# ============ DIEM DANH ============
dd={}
@bot.command()
async def diemdanh(c):
    i=c.author.id;n=time.time()
    if i in dd and n-dd[i]<43200:return await c.send("⚠️ Bạn đã điểm danh!")
    dd[i]=n;u=U(i,c.author.name);u["cash"]+=2593
    await c.send(embed=E("🎁 ĐIỂM DANH",f"💰 **+2,593$**\n💵 Ví: `{u['cash']:,}$`",GREEN))

# ============ BANK ============
@bot.command()
async def gui(c,a:int=None):
    u=U(c.author.id,c.author.name)
    if not a or a<=0 or u["cash"]<a:return await c.send("❌ `!gui số_tiền`")
    u["cash"]-=a;u["bank"]+=a
    await c.send(embed=E("🏦 GỬI TIỀN",f"💰 `{a:,}$`\n🏦 `{u['bank']:,}$`",BLUE))

@bot.command()
async def rut(c,a:int=None):
    u=U(c.author.id,c.author.name)
    if not a or a<=0 or u["bank"]<a:return await c.send("❌ `!rut số_tiền`")
    u["bank"]-=a;u["cash"]+=a
    await c.send(embed=E("🏦 RÚT TIỀN",f"💰 `{a:,}$`\n💵 `{u['cash']:,}$`",BLUE))

@bot.command()
async def chuyen(c,m:discord.Member=None,a:int=None):
    if not m or not a or a<=0:return await c.send("❌ `!chuyen @User số_tiền`")
    x,y=U(c.author.id,c.author.name),U(m.id,m.name)
    if m.bot or m.id==c.author.id or x["cash"]<a:return await c.send("❌ Không thể chuyển!")
    x["cash"]-=a;y["cash"]+=a
    await c.send(f"💸 {c.author.mention} → {m.mention} **{a:,}$**")

# ============ BXH ============
@bot.command()
async def bxh(c):
    z=sorted(users.values(),key=lambda x:x["cash"]+x["bank"],reverse=True)[:5]
    await c.send(embed=E("🏆 TOP 5", "\n".join(
        f"{['🥇','🥈','🥉','4️⃣','5️⃣'][i]} **{x['name']}** — `{x['cash']+x['bank']:,}$`"
        for i,x in enumerate(z)),BLUE))

# ============ CODE ============
def NC():return "BET-"+secrets.token_hex(3).upper()

@bot.command()
async def taocode(c,a:int=None,n:int=None):
    if not ADM(c):return await c.send("⛔ Chỉ Admin!")
    if not a or not n:return await c.send("❌ `!taocode tiền lượt`")
    x=NC();codes[x]={"money":a,"uses":n,"used":set()}
    await c.author.send(embed=E("🔐 CODE ADMIN",
        f"🎟️ `{x}`\n💰 `{a:,}$`\n🔢 `{n}` lượt",BLUE))
    await c.send("✅ Code đã gửi riêng vào DM.")

@bot.command()
async def thuongcode(c,a:int=None,n:int=None):
    if not ADM(c):return await c.send("⛔ Chỉ Admin!")
    if not a or not n:return await c.send("❌ `!thuongcode tiền lượt`")
    x=NC();codes[x]={"money":a,"uses":n,"used":set()}
    await c.send(embed=E("🎁 CODE THƯỞNG",
        f"🎟️ **{x}**\n💰 **{a:,}$**\n👥 **{n} lượt**\n\n`!nhapcode {x}`",GREEN))

@bot.command()
async def nhapcode(c,x=None):
    if not x or x.upper() not in codes:return await c.send("❌ Code không tồn tại!")
    x=x.upper();z=codes[x];i=c.author.id
    if i in z["used"]:return await c.send("❌ Bạn đã dùng code này!")
    if len(z["used"])>=z["uses"]:return await c.send("❌ Code hết lượt!")
    z["used"].add(i);U(i,c.author.name)["cash"]+=z["money"]
    await c.send(f"🎁 Nhận **+{z['money']:,}$** thành công!")

# ============ ADMIN ============
@bot.command()
async def settien(c,m:discord.Member=None,a:int=None):
    if not ADM(c):return await c.send("⛔ Chỉ Admin!")
    if not m or a is None or a<0:return await c.send("❌ `!settien @User tiền`")
    U(m.id,m.name)["cash"]=a
    await c.send(f"✅ {m.mention} → `{a:,}$`")

@bot.command()
async def resettien(c,m:discord.Member=None):
    if not ADM(c):return await c.send("⛔ Chỉ Admin!")
    if not m:return await c.send("❌ `!resettien @User`")
    U(m.id,m.name)["cash"]=DEFAULT
    await c.send(f"🔄 {m.mention} → `{DEFAULT:,}$`")

# ============ SLOT ============
@bot.command()
async def quay(c,a:int=None):
    if not a or a<=0:return await c.send("❌ `!quay 100`")
    u=U(c.author.id,c.author.name)
    if u["cash"]<a:return await c.send("❌ Không đủ tiền!")
    u["cash"]-=a
    s=[random.choice(["💎","🍒","🔔","⭐","7️⃣"]) for _ in range(3)]
    m=await c.send(embed=E("🎰 MÁY SLOT NỔ HŨ",
        "⏳ **ĐANG QUAY...**\n\n`[ ❔ ] [ ❔ ] [ ❔ ]`",ORANGE))
    await asyncio.sleep(1)
    w=s[0]==s[1]==s[2]
    if w:u["cash"]+=a*5
    d=f"`[ {s[0]} ] [ {s[1]} ] [ {s[2]} ]`\n\n"
    d+=f"🎉 **NỔ HŨ! +{a*5:,}$**" if w else f"💸 **TRẬT HŨ! -{a:,}$**"
    await m.edit(embed=E("🎰 MÁY SLOT NỔ HŨ",d,GREEN if w else RED))

# ============ BAU CUA ============
@bot.command()
async def bc(c,x=None,a:int=None):
    A={"ca":"🐟","tom":"🦐","cua":"🦀","bau":"🥒","ga":"🐓","nai":"🦌"}
    if x not in A or not a:return await c.send("❌ `!bc cua 100`")
    u=U(c.author.id,c.author.name)
    if u["cash"]<a:return await c.send("❌ Không đủ tiền!")
    u["cash"]-=a
    m=await c.send(embed=E("🦀 BẦU CUA TÔM CÁ",
        "🥣 **ĐANG LẮC HỘT...**\n\n`[ ❔ ] [ ❔ ] [ ❔ ]`",ORANGE))
    await asyncio.sleep(1)
    r=[random.choice(list(A)) for _ in range(3)];n=r.count(x)
    if n:u["cash"]+=a*(n+1)
    d=f"**KẾT QUẢ**\n`[ {A[r[0]]} ] [ {A[r[1]]} ] [ {A[r[2]]} ]`\n\n"
    d+=f"🎉 **TRÚNG {n} CON! +{a*n:,}$**" if n else f"💸 **TRẬT LẤT! -{a:,}$**"
    await m.edit(embed=E("🦀 BẦU CUA TÔM CÁ",d,GREEN if n else RED))

# ============ TAIXIU ============
@bot.command()
async def tx(c,x=None,a:int=None):
    if not x:
        if not tx["active"]:return await c.send("❌ `!tx tai 100` để mở phiên!")
        return await c.send(embed=E("🎲 SÒNG TÀI XỈU 30S",
            f"Gõ `!tx <tai/xiu> <tiền>`\n\n⏱️ **30 giây**\n"
            f"🔴 Tài: `{tx['tai']:,}$`\n🔵 Xỉu: `{tx['xiu']:,}$`",ORANGE))
    x=x.lower()
    if x not in ("tai","xiu") or not a or a<=0:return await c.send("❌ `!tx tai 100`")
    i=c.author.id;u=U(i,c.author.name)
    if not tx["active"]:
        tx.update(active=True,bets={},tai=0,xiu=0)
        tx["msg"]=await c.send(embed=E("🎲 SÒNG TÀI XỈU 30S 🎲",
            "Gõ `!tx tai <tiền>` hoặc `!tx xiu <tiền>`\n\n"
            "⏱️ **Thời gian: 30 giây**\n\n"
            "🔴 Tài: `0$`\n🔵 Xỉu: `0$`",ORANGE))
        asyncio.create_task(txround())
    if i in tx["bets"]:return await c.send("❌ Bạn đã cược rồi! **1 lần/ván**.")
    if u["cash"]<a:return await c.send("❌ Không đủ tiền!")
    u["cash"]-=a;tx["bets"][i]={"name":c.author.name,"choice":x,"amount":a};tx[x]+=a
    try:await c.message.delete()
    except:pass

async def txround():
    await asyncio.sleep(30)
    if not tx["active"]:return
    tx["active"]=False;m=tx["msg"]
    await m.edit(embed=E("🎲 ĐANG XÓC BÁT","🥣 **ĐANG XÓC...**\n\n`[ ❔ ] [ ❔ ] [ ❔ ]`",ORANGE))
    await asyncio.sleep(1.5)
    d=[random.randint(1,6) for _ in range(3)];t=sum(d)
    r="tai" if t>=11 else "xiu";w=[];l=[]
    for i,b in tx["bets"].items():
        if b["choice"]==r:
            U(i)["cash"]+=b["amount"]*2;w.append(f"• {b['name']} `+{b['amount']:,}$`")
        else:l.append(f"• {b['name']} `-{b['amount']:,}$`")
    R="🔴 **TÀI**" if r=="tai" else "🔵 **XỈU**"
    d=(f"**XÚC XẮC**\n`[ {d[0]} ] [ {d[1]} ] [ {d[2]} ]`\n"
       f"→ **{t} điểm — {R}**\n\n🎉 **THẮNG**\n{chr(10).join(w) or 'Không có'}"
       f"\n\n💸 **THUA**\n{chr(10).join(l) or 'Không có'}")
    await m.edit(embed=E("🎲 KẾT QUẢ TÀI XỈU",d,GREEN if w else RED))
    tx.update(active=False,bets={},tai=0,xiu=0,msg=None)

# ============ XD ============
@bot.command()
async def xd(c,x=None,a:int=None):
    if x not in ("chan","le") or not a:return await c.send("❌ `!xd chan 100`")
    u=U(c.author.id,c.author.name)
    if u["cash"]<a:return await c.send("❌ Không đủ tiền!")
    u["cash"]-=a
    m=await c.send(embed=E("🪙 XÓC ĐĨA","🟠 **ĐANG XÓC...**\n\n`[ ⚪ ⚪ ⚪ ⚪ ]`",ORANGE))
    await asyncio.sleep(1.2)
    n=random.randint(0,4);r="chan" if n%2==0 else "le";w=r==x
    if w:u["cash"]+=a*2
    d=f"`[ {'🔴'*n+'⚪'*(4-n)} ]` → **{'CHẴN' if r=='chan' else 'LẺ'}**\n\n"
    d+=f"🎉 **THẮNG +{a:,}$**" if w else f"💸 **THUA -{a:,}$**"
    await m.edit(embed=E("🪙 XÓC ĐĨA",d,GREEN if w else RED))

# ============ RUN ============
token=os.getenv("TOKEN_BOT")
if token:bot.run(token)
else:print("❌ Chưa có TOKEN_BOT!")
