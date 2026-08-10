import os,asyncio,random,time,secrets,discord
from discord.ext import commands

intents=discord.Intents.default()
intents.message_content=True
bot=commands.Bot(command_prefix="!",intents=intents,help_command=None)

users,codes,cooldowns={}, {}, {}
DEFAULT=4899
BLUE,ORANGE,GREEN,RED=0x3498DB,0xF1C40F,0x2ECC71,0xE74C3C
tx={"active":False,"bets":{},"tai":0,"xiu":0,"msg":None}

def emb(t,d,c):
    return discord.Embed(title=t,description=d,color=c)

def user(i,n="Thành viên"):
    if i not in users:
        users[i]={"name":n,"cash":DEFAULT,"bank":0,
                  "hang":"Người chơi Thường","ga":"Gà Công Nghiệp 🐥"}
    return users[i]

def cd(i,c,s=1.5):
    k=f"{i}_{c}"; now=time.time()
    if k in cooldowns and now-cooldowns[k]<s:return round(s-(now-cooldowns[k]),1)
    cooldowns[k]=now

def admin(ctx):
    return ctx.author.guild_permissions.administrator

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino Bet88"))
    print("✅ BOT ONLINE:",bot.user)

# ================= TRỢ GIÚP =================

@bot.command(name="trogiup",aliases=["help"])
async def trogiup(ctx):
    await ctx.send(embed=emb("🎰 CASINO BET88",
    "**⚔️ PVP**\n`!danhbai` `!thachdau` `!dagapvp` `!tuxipvp @User`\n\n"
    "**🎲 CASINO**\n"
    "`!tx tai 1000` `!bc ca 1000`\n"
    "`!xd chan 1000` `!quay 1000`\n\n"
    "**🏛️ HỆ THỐNG**\n"
    "`!vi` `!gui` `!rut` `!chuyen @User 100`\n"
    "`!diemdanh` `!bxh` `!nhapcode CODE`\n\n"
    "**👑 ADMIN**\n"
    "`!taocode 10000 1`\n"
    "`!thuongcode 10000 10`\n"
    "`!settien @User 10000`\n"
    "`!resettien @User`",BLUE))

# ================= VÍ =================

@bot.command(name="vi",aliases=["money","bal"])
async def vi(ctx,member:discord.Member=None):
    t=member or ctx.author; u=user(t.id,t.name)
    await ctx.send(embed=emb("💳 THÔNG TIN TÀI KHOẢN",
    f"👤 **{t.name.upper()}**\n🏷️ {u['hang']}\n🐓 {u['ga']}\n\n"
    f"💵 **Tiền mặt:** `{u['cash']:,}$`\n"
    f"🏦 **Ngân hàng:** `{u['bank']:,}$`",BLUE))

# ================= ĐIỂM DANH =================

last_dd={}
@bot.command(name="diemdanh")
async def diemdanh(ctx):
    i=ctx.author.id; now=time.time()
    if i in last_dd and now-last_dd[i]<43200:
        return await ctx.send("⚠️ Bạn đã điểm danh rồi!")
    last_dd[i]=now; u=user(i,ctx.author.name); u["cash"]+=2593
    await ctx.send(embed=emb("🎁 ĐIỂM DANH",
    f"💰 **+2,593$**\n💵 Ví: `{u['cash']:,}$`",GREEN))

# ================= BANK =================

@bot.command()
async def gui(ctx,amount:int=None):
    if not amount or amount<=0:return await ctx.send("❌ `!gui số_tiền`")
    u=user(ctx.author.id,ctx.author.name)
    if u["cash"]<amount:return await ctx.send("❌ Không đủ tiền!")
    u["cash"]-=amount;u["bank"]+=amount
    await ctx.send(embed=emb("🏦 GỬI TIỀN",
    f"💰 Gửi `{amount:,}$`\n🏦 Bank `{u['bank']:,}$`",BLUE))

@bot.command()
async def rut(ctx,amount:int=None):
    if not amount or amount<=0:return await ctx.send("❌ `!rut số_tiền`")
    u=user(ctx.author.id,ctx.author.name)
    if u["bank"]<amount:return await ctx.send("❌ Bank không đủ!")
    u["bank"]-=amount;u["cash"]+=amount
    await ctx.send(embed=emb("🏦 RÚT TIỀN",
    f"💰 Rút `{amount:,}$`\n💵 Ví `{u['cash']:,}$`",BLUE))

@bot.command()
async def chuyen(ctx,member:discord.Member=None,amount:int=None):
    if not member or not amount or amount<=0:
        return await ctx.send("❌ `!chuyen @User số_tiền`")
    if member.id==ctx.author.id or member.bot:return await ctx.send("❌ Không thể chuyển!")
    a,b=user(ctx.author.id,ctx.author.name),user(member.id,member.name)
    if a["cash"]<amount:return await ctx.send("❌ Không đủ tiền!")
    a["cash"]-=amount;b["cash"]+=amount
    await ctx.send(embed=emb("💸 CHUYỂN TIỀN",
    f"{ctx.author.mention} ➜ {member.mention}\n💰 `{amount:,}$`",BLUE))

# ================= BXH =================

@bot.command(name="bxh")
async def bxh(ctx):
    top=sorted(users.values(),key=lambda x:x["cash"]+x["bank"],reverse=True)[:5]
    m=["🥇","🥈","🥉","4️⃣","5️⃣"]
    await ctx.send(embed=emb("🏆 TOP 5 GIÀU NHẤT",
    "\n".join(f"{m[i]} **{u['name']}** — `{u['cash']+u['bank']:,}$`"
    for i,u in enumerate(top)),BLUE))

# ================= CODE =================

def newcode():return "BET-"+secrets.token_hex(3).upper()

@bot.command()
async def taocode(ctx,amount:int=None,uses:int=None):
    if not admin(ctx):return await ctx.send("⛔ Chỉ Admin!")
    if not amount or not uses:return await ctx.send("❌ `!taocode tiền lượt`")
    c=newcode();codes[c]={"money":amount,"uses":uses,"used":set()}
    await ctx.author.send(embed=emb("🔐 CODE ADMIN",
    f"🎟️ `{c}`\n💰 `{amount:,}$`\n🔢 `{uses}` lượt",BLUE))
    await ctx.send("✅ Code riêng đã gửi vào DM.")

@bot.command()
async def thuongcode(ctx,amount:int=None,uses:int=None):
    if not admin(ctx):return await ctx.send("⛔ Chỉ Admin!")
    if not amount or not uses:return await ctx.send("❌ `!thuongcode tiền lượt`")
    c=newcode();codes[c]={"money":amount,"uses":uses,"used":set()}
    await ctx.send(embed=emb("🎁 CODE THƯỞNG",
    f"🎟️ **{c}**\n💰 **{amount:,}$**\n👥 **{uses} lượt**\n\n"
    f"Nhập: `!nhapcode {c}`",GREEN))

@bot.command()
async def nhapcode(ctx,code:str=None):
    if not code:return await ctx.send("❌ `!nhapcode CODE`")
    code=code.upper()
    if code not in codes:return await ctx.send("❌ Code không tồn tại!")
    c=codes[code];i=ctx.author.id
    if i in c["used"]:return await ctx.send("❌ Bạn đã dùng code này!")
    if len(c["used"])>=c["uses"]:return await ctx.send("❌ Code hết lượt!")
    c["used"].add(i);u=user(i,ctx.author.name);u["cash"]+=c["money"]
    await ctx.send(embed=emb("🎁 NHẬP CODE THÀNH CÔNG",
    f"🎟️ `{code}`\n💰 **+{c['money']:,}$**",GREEN))

# ================= ADMIN =================

@bot.command()
async def settien(ctx,member:discord.Member=None,amount:int=None):
    if not admin(ctx):return await ctx.send("⛔ Chỉ Admin!")
    if not member or amount is None or amount<0:
        return await ctx.send("❌ `!settien @User số_tiền`")
    user(member.id,member.name)["cash"]=amount
    await ctx.send(f"✅ {member.mention} → `{amount:,}$`")

@bot.command()
async def resettien(ctx,member:discord.Member=None):
    if not admin(ctx):return await ctx.send("⛔ Chỉ Admin!")
    if not member:return await ctx.send("❌ `!resettien @User`")
    user(member.id,member.name)["cash"]=DEFAULT
    await ctx.send(f"🔄 {member.mention} → `{DEFAULT:,}$`")

# ================= SLOT =================

@bot.command()
async def quay(ctx,bet:int=None):
    if cd(ctx.author.id,"quay"):return
    if not bet or bet<=0:return await ctx.send("❌ `!quay số_tiền`")
    u=user(ctx.author.id,ctx.author.name)
    if u["cash"]<bet:return await ctx.send("❌ Không đủ tiền!")
    u["cash"]-=bet

    s=[random.choice(["🍋","🔔","🍒","⭐","💎"]) for _ in range(3)]
    msg=await ctx.send(embed=emb("🎰 **MÁY SLOT BET88**",
    "🎰\n\n🟠 **QUAY... QUAY... QUAY...**\n\n"
    "`[ ❔ ]  [ ❔ ]  [ ❔ ]`",ORANGE))

    await asyncio.sleep(.7)
    await msg.edit(embed=emb("🎰 **MÁY SLOT BET88**",
    "🎰\n\n🟠 **ĐANG QUAY...**\n\n"
    f"`[ {s[0]} ]  [ ❔ ]  [ ❔ ]`",ORANGE))

    await asyncio.sleep(.7)
    await msg.edit(embed=emb("🎰 **MÁY SLOT BET88**",
    "🎰\n\n🟠 **SẮP DỪNG...**\n\n"
    f"`[ {s[0]} ]  [ {s[1]} ]  [ ❔ ]`",ORANGE))

    await asyncio.sleep(.7)
    win=s[0]==s[1]==s[2]
    if win:u["cash"]+=bet*5
    await msg.edit(embed=emb("🎰 **MÁY SLOT BET88**",
    f"🎰\n\n`[ {s[0]} ]  [ {s[1]} ]  [ {s[2]} ]`\n\n"
    +(f"💎 **NỔ HŨ! +{bet*5:,}$**" if win else f"💸 **TRẬT HŨ! -{bet:,}$**"),
    GREEN if win else RED))

# ================= TÀI XỈU =================

@bot.command(name="tx")
async def taixiu(ctx,choice:str=None,bet:int=None):
    if not choice or not bet or choice.lower() not in ("tai","xiu") or bet<=0:
        return await ctx.send("❌ `!tx tai 1000` hoặc `!tx xiu 1000`")

    if bet>10000000:
        return await ctx.send("❌ Cược tối đa **10,000,000$ / ván**!")

    i=ctx.author.id;u=user(i,ctx.author.name)

    if not tx["active"]:
        tx.update(active=True,bets={},tai=0,xiu=0)
        tx["msg"]=await ctx.send(embed=emb("🎲 **SÒNG TÀI XỈU BET88**",
        "🎲\n\n🟠 **ĐANG MỞ PHIÊN...**\n\n"
        "🔴 **TÀI:** `0$`\n"
        "🔵 **XỈU:** `0$`\n\n"
        "💰 **CƯỢC MAX: 10,000,000$**\n"
        "⏱️ **30 GIÂY**",ORANGE))
        asyncio.create_task(tx_round())

    if i in tx["bets"]:
        return await ctx.send("❌ Bạn đã cược **1 lần** trong ván này!")

    if u["cash"]<bet:return await ctx.send("❌ Không đủ tiền!")

    u["cash"]-=bet
    tx["bets"][i]={"name":ctx.author.name,"choice":choice.lower(),"amount":bet}
    tx[choice.lower()]+=bet

    try:await ctx.message.delete()
    except:pass

    e=emb("🎲 **SÒNG TÀI XỈU BET88**",
    "🎲\n\n🟠 **ĐANG NHẬN CƯỢC...**\n\n"
    f"🔴 **TÀI:** `{tx['tai']:,}$`\n"
    f"🔵 **XỈU:** `{tx['xiu']:,}$`\n\n"
    "💰 **CƯỢC MAX: 10,000,000$**\n"
    "⏱️ **30 GIÂY**",ORANGE)
    await tx["msg"].edit(embed=e)

async def tx_round():
    await asyncio.sleep(30)
    if not tx["active"]:return
    tx["active"]=False;msg=tx["msg"]
    await msg.edit(embed=emb("🎲 **TÀI XỈU BET88**",
    "🥣\n\n🟠 **XÓC... XÓC... XÓC...**\n\n"
    "`[ ❔ ]  [ ❔ ]  [ ❔ ]`",ORANGE))
    await asyncio.sleep(2)

    d=[random.randint(1,6) for _ in range(3)]
    total=sum(d);r="tai" if total>=11 else "xiu"
    win=[];lose=[]

    for i,b in tx["bets"].items():
        if b["choice"]==r:
            user(i)["cash"]+=b["amount"]*2
            win.append(f"• **{b['name']}** `+{b['amount']:,}$`")
        else:lose.append(f"• **{b['name']}** `-{b['amount']:,}$`")

    await msg.edit(embed=emb("🎲 **KẾT QUẢ TÀI XỈU**",
    f"🎲\n\n`[ {d[0]} ]  [ {d[1]} ]  [ {d[2]} ]`\n\n"
    f"💥 **{total} ĐIỂM — {'TÀI 🔴' if r=='tai' else 'XỈU 🔵'}**\n\n"
    "🏆 **THẮNG**\n"+("\n".join(win) or "Không có")+
    "\n\n💸 **THUA**\n"+("\n".join(lose) or "Không có"),
    GREEN if win else RED))
    tx.update(active=False,bets={},tai=0,xiu=0,msg=None)

# ================= XÓC ĐĨA =================

@bot.command()
async def xd(ctx,choice:str=None,bet:int=None):
    if not choice or choice.lower() not in ("chan","le") or not bet or bet<=0:
        return await ctx.send("❌ `!xd chan 100` hoặc `!xd le 100`")
    u=user(ctx.author.id,ctx.author.name)
    if u["cash"]<bet:return await ctx.send("❌ Không đủ tiền!")
    u["cash"]-=bet

    msg=await ctx.send(embed=emb("🪙 **XÓC ĐĨA BET88**",
    "🪙\n\n🟠 **XÓC... XÓC... XÓC...**",ORANGE))
    await asyncio.sleep(.8)
    await msg.edit(embed=emb("🪙 **XÓC ĐĨA BET88**",
    "🪙\n\n🟠 **ĐANG XÓC...**",ORANGE))
    await asyncio.sleep(.8)

    n=random.randint(0,4);win=(n%2==0)==(choice.lower()=="chan")
    if win:u["cash"]+=bet*2
    await msg.edit(embed=emb("🪙 **XÓC ĐĨA BET88**",
    f"🪙\n\n`{'🔴'*n+'⚪'*(4-n)}`\n\n"
    f"💥 **{'CHẴN' if n%2==0 else 'LẺ'}**\n\n"+
    (f"🎉 **THẮNG +{bet:,}$**" if win else f"💸 **THUA -{bet:,}$**"),
    GREEN if win else RED))

# ================= BẦU CUA =================

@bot.command()
async def bc(ctx,choice:str=None,bet:int=None):
    a={"ca":"🐟","tom":"🦐","cua":"🦀","bau":"🥒","ga":"🐓","nai":"🦌"}
    if not choice or choice.lower() not in a or not bet or bet<=0:
        return await ctx.send("❌ `!bc ca 100`")
    choice=choice.lower();u=user(ctx.author.id,ctx.author.name)
    if u["cash"]<bet:return await ctx.send("❌ Không đủ tiền!")
    u["cash"]-=bet

    msg=await ctx.send(embed=emb("🎲 **BẦU CUA BET88**",
    "🎲\n\n🟠 **LẮC... LẮC... LẮC...**\n\n"
    "`[ ❔ ]  [ ❔ ]  [ ❔ ]`",ORANGE))
    await asyncio.sleep(.8)
    await msg.edit(embed=emb("🎲 **BẦU CUA BET88**",
    "🎲\n\n🟠 **ĐANG LẮC...**\n\n"
    "`[ ❔ ]  [ ❔ ]  [ ❔ ]`",ORANGE))
    await asyncio.sleep(.8)

    r=[random.choice(list(a)) for _ in range(3)]
    n=r.count(choice)
    if n:u["cash"]+=bet*(n+1)

    await msg.edit(embed=emb("🎲 **BẦU CUA BET88**",
    f"🎲\n\n`[ {a[r[0]]} ]  [ {a[r[1]]} ]  [ {a[r[2]]} ]`\n\n"+
    (f"🎉 **TRÚNG {n} CON! +{bet*n:,}$**"
     if n else f"💸 **KHÔNG TRÚNG! -{bet:,}$**"),
    GREEN if n else RED))

# ================= RUN =================

token=os.getenv("TOKEN_BOT")
if not token:print("❌ Chưa có TOKEN_BOT!")
else:bot.run(token)
