import os,asyncio,random,time,secrets,discord
from discord.ext import commands

intents=discord.Intents.default()
intents.message_content=True
bot=commands.Bot(command_prefix="!",intents=intents,help_command=None)

users,codes={},{}
cooldowns={}
DEFAULT=4899
BLUE,ORANGE,GREEN,RED=0x3498DB,0xF1C40F,0x2ECC71,0xE74C3C
tx={"active":False,"bets":{},"tai":0,"xiu":0,"msg":None}
last_dd={}

def emb(t,d,c): return discord.Embed(title=t,description=d,color=c)

def user(i,n="Thành viên"):
    if i not in users:
        users[i]={"name":n,"cash":DEFAULT,"bank":0,
                  "hang":"Người chơi Thường","ga":"Gà Công Nghiệp 🐥"}
    return users[i]

def cd(i,c,s=1.5):
    k=f"{i}_{c}"; now=time.time()
    if k in cooldowns and now-cooldowns[k]<s:return 1
    cooldowns[k]=now

def admin(ctx): return ctx.author.guild_permissions.administrator

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino Bet88"))
    print("✅ BOT ONLINE:",bot.user)

# ================= HELP =================

@bot.command(name="trogiup",aliases=["help"])
async def trogiup(ctx):
    if cd(ctx.author.id,"help"):return
    x=("**🎲 CASINO**\n"
       "`!tx tai 100` `!tx xiu 100`\n"
       "`!bc cua 100` `!xd chan 100` `!quay 100`\n\n"
       "**💰 TÀI KHOẢN**\n"
       "`!vi` `!gui` `!rut` `!chuyen @User 100`\n"
       "`!diemdanh` `!bxh` `!nhapcode CODE`\n\n"
       "**👑 ADMIN**\n"
       "`!taocode 10000 1`\n"
       "`!thuongcode 10000 10`\n"
       "`!settien @User 10000`\n"
       "`!resettien @User`")
    await ctx.send(embed=emb("🎰 CASINO BET88",x,BLUE))

# ================= VI =================

@bot.command(name="vi",aliases=["money","bal"])
async def vi(ctx,member:discord.Member=None):
    t=member or ctx.author;u=user(t.id,t.name)
    await ctx.send(embed=emb("💳 TÀI KHOẢN",
        f"👤 **{t.name.upper()}**\n"
        f"🏷️ {u['hang']} | 🐓 {u['ga']}\n\n"
        f"💵 Ví: `{u['cash']:,}$`\n"
        f"🏦 Bank: `{u['bank']:,}$`",BLUE))

@bot.command(name="diemdanh")
async def diemdanh(ctx):
    i=ctx.author.id;n=time.time()
    if i in last_dd and n-last_dd[i]<43200:
        return await ctx.send("⚠️ Bạn đã điểm danh rồi!")
    last_dd[i]=n;u=user(i,ctx.author.name);u["cash"]+=2593
    await ctx.send(embed=emb("🎁 ĐIỂM DANH",
        f"💰 **+2,593$**\n💵 Ví: `{u['cash']:,}$`",GREEN))

# ================= BANK =================

@bot.command(name="gui")
async def gui(ctx,a:int=None):
    u=user(ctx.author.id,ctx.author.name)
    if not a or a<=0:return await ctx.send("❌ `!gui số_tiền`")
    if u["cash"]<a:return await ctx.send("❌ Không đủ tiền!")
    u["cash"]-=a;u["bank"]+=a
    await ctx.send(embed=emb("🏦 GỬI TIỀN",
        f"💰 Gửi `{a:,}$`\n🏦 Bank `{u['bank']:,}$`",BLUE))

@bot.command(name="rut")
async def rut(ctx,a:int=None):
    u=user(ctx.author.id,ctx.author.name)
    if not a or a<=0:return await ctx.send("❌ `!rut số_tiền`")
    if u["bank"]<a:return await ctx.send("❌ Bank không đủ!")
    u["bank"]-=a;u["cash"]+=a
    await ctx.send(embed=emb("🏦 RÚT TIỀN",
        f"💰 Rút `{a:,}$`\n💵 Ví `{u['cash']:,}$`",BLUE))

@bot.command(name="chuyen")
async def chuyen(ctx,m:discord.Member=None,a:int=None):
    if not m or not a or a<=0:return await ctx.send("❌ `!chuyen @User số_tiền`")
    if m.id==ctx.author.id or m.bot:return await ctx.send("❌ Không thể chuyển!")
    x,y=user(ctx.author.id,ctx.author.name),user(m.id,m.name)
    if x["cash"]<a:return await ctx.send("❌ Không đủ tiền!")
    x["cash"]-=a;y["cash"]+=a
    await ctx.send(embed=emb("💸 CHUYỂN TIỀN",
        f"{ctx.author.mention} ➜ {m.mention}\n💰 `{a:,}$`",BLUE))

# ================= BXH =================

@bot.command(name="bxh")
async def bxh(ctx):
    top=sorted(users.values(),key=lambda x:x["cash"]+x["bank"],reverse=True)[:5]
    medals=["🥇","🥈","🥉","4️⃣","5️⃣"]
    s="\n".join(f"{medals[i]} **{u['name']}** — `{u['cash']+u['bank']:,}$`"
                for i,u in enumerate(top))
    await ctx.send(embed=emb("🏆 TOP 5",s or "Chưa có người chơi.",BLUE))

# ================= CODE =================

def newcode():return "BET-"+secrets.token_hex(3).upper()

async def makecode(ctx,a,n):
    if not admin(ctx):return await ctx.send("⛔ Chỉ Admin!")
    if a<=0 or n<=0:return await ctx.send("❌ Số tiền/lượt không hợp lệ!")
    c=newcode();codes[c]={"money":a,"uses":n,"used":set()};return c

@bot.command(name="taocode")
async def taocode(ctx,a:int=None,n:int=None):
    if a is None or n is None:return await ctx.send("❌ `!taocode tiền lượt`")
    c=await makecode(ctx,a,n)
    if not isinstance(c,str):return
    await ctx.author.send(embed=emb("🔐 CODE ADMIN",
        f"🎟️ `{c}`\n💰 `{a:,}$` | 🔢 `{n}` lượt",BLUE))
    await ctx.send("✅ Code đã gửi vào DM.")

@bot.command(name="thuongcode")
async def thuongcode(ctx,a:int=None,n:int=None):
    if a is None or n is None:return await ctx.send("❌ `!thuongcode tiền lượt`")
    c=await makecode(ctx,a,n)
    if not isinstance(c,str):return
    await ctx.send(embed=emb("🎁 CODE THƯỞNG",
        f"🎟️ **`{c}`**\n💰 `{a:,}$`\n👥 `{n}` lượt\n\n"
        f"Nhập: `!nhapcode {c}`",GREEN))

@bot.command(name="nhapcode")
async def nhapcode(ctx,c:str=None):
    if not c:return await ctx.send("❌ `!nhapcode CODE`")
    c=c.upper()
    if c not in codes:return await ctx.send("❌ Code không tồn tại!")
    x=codes[c];i=ctx.author.id
    if i in x["used"]:return await ctx.send("❌ Bạn đã dùng code!")
    if len(x["used"])>=x["uses"]:return await ctx.send("❌ Code hết lượt!")
    x["used"].add(i);user(i,ctx.author.name)["cash"]+=x["money"]
    await ctx.send(embed=emb("🎁 NHẬP CODE",
        f"🎟️ `{c}`\n💰 **+{x['money']:,}$**",GREEN))

# ================= ADMIN =================

@bot.command(name="settien")
async def settien(ctx,m:discord.Member=None,a:int=None):
    if not admin(ctx):return await ctx.send("⛔ Chỉ Admin!")
    if not m or a is None or a<0:return await ctx.send("❌ `!settien @User tiền`")
    user(m.id,m.name)["cash"]=a
    await ctx.send(f"✅ {m.mention} ➜ `{a:,}$`")

@bot.command(name="resettien")
async def resettien(ctx,m:discord.Member=None):
    if not admin(ctx):return await ctx.send("⛔ Chỉ Admin!")
    if not m:return await ctx.send("❌ `!resettien @User`")
    user(m.id,m.name)["cash"]=DEFAULT
    await ctx.send(f"🔄 {m.mention} ➜ `{DEFAULT:,}$`")

# ================= SLOT =================

@bot.command(name="quay")
async def quay(ctx,bet:int=None):
    if cd(ctx.author.id,"quay"):return
    if not bet or bet<=0:return await ctx.send("❌ `!quay 100`")
    u=user(ctx.author.id,ctx.author.name)
    if u["cash"]<bet:return await ctx.send("❌ Không đủ tiền!")
    u["cash"]-=bet
    s=[random.choice(["🍒","💎","⭐","🔔","🍋"]) for _ in range(3)]
    msg=await ctx.send(embed=emb("🎰 MÁY SLOT",
        f"🎯 Cược `{bet:,}$`\n\n🟠 **ĐANG QUAY...**\n\n"
        "`[ ❔ ] [ ❔ ] [ ❔ ]`",ORANGE))
    await asyncio.sleep(1.2)
    win=s[0]==s[1]==s[2]
    if win:
        gain=bet*5;u["cash"]+=gain
        r=f"🎉 **JACKPOT +{gain:,}$**";co=GREEN
    else:r=f"💸 **THUA -{bet:,}$**";co=RED
    await msg.edit(embed=emb("🎰 MÁY SLOT",
        f"🎯 Cược `{bet:,}$`\n\n`[ {s[0]} ] [ {s[1]} ] [ {s[2]} ]`\n\n{r}",co))

# ================= TAIXIU =================

@bot.command(name="tx")
async def taixiu(ctx,ch:str=None,bet:int=None):
    if not ch:
        if not tx["active"]:return await ctx.send("❌ `!tx tai 100` để mở phiên!")
        return await ctx.send(embed=emb("🎲 TÀI XỈU",
            f"🟢 **TÀI:** `{tx['tai']:,}$`\n🔵 **XỈU:** `{tx['xiu']:,}$`\n\n"
            "🟠 Đang nhận cược...",ORANGE))
    ch=ch.lower()
    if ch not in ("tai","xiu") or not bet or bet<=0:
        return await ctx.send("❌ `!tx tai 100` hoặc `!tx xiu 100`")
    i=ctx.author.id;u=user(i,ctx.author.name)

    if not tx["active"]:
        tx.update(active=True,bets={},tai=0,xiu=0)
        tx["msg"]=await ctx.send(embed=emb("🎲 TÀI XỈU • 30S",
            "🟠 **ĐANG NHẬN CƯỢC**\n\n"
            "🔴 `!tx tai số_tiền`\n"
            "🔵 `!tx xiu số_tiền`",ORANGE))
        asyncio.create_task(tx_round())

    if i in tx["bets"]:return await ctx.send("❌ Bạn đã cược rồi! **1 lần/ván**.")
    if u["cash"]<bet:return await ctx.send("❌ Không đủ tiền!")
    u["cash"]-=bet
    tx["bets"][i]={"name":ctx.author.name,"choice":ch,"amount":bet}
    tx[ch]+=bet
    try:await ctx.message.delete()
    except:pass

async def tx_round():
    await asyncio.sleep(30)
    if not tx["active"]:return
    tx["active"]=False;m=tx["msg"]
    await m.edit(embed=emb("🎲 XÓC BÁT","🟠 **ĐANG XÓC...**\n\n`[ ❔ ] [ ❔ ] [ ❔ ]`",ORANGE))
    await asyncio.sleep(2)
    d=[random.randint(1,6) for _ in range(3)];total=sum(d)
    result="tai" if total>=11 else "xiu";win=[];lose=[]
    for i,b in tx["bets"].items():
        if b["choice"]==result:
            user(i)["cash"]+=b["amount"]*2
            win.append(f"• {b['name']} `+{b['amount']:,}$`")
        else:lose.append(f"• {b['name']} `-{b['amount']:,}$`")
    rr="🔴 TÀI" if result=="tai" else "🔵 XỈU"
    await m.edit(embed=emb("🎲 KẾT QUẢ TÀI XỈU",
        f"`[ {d[0]} ] [ {d[1]} ] [ {d[2]} ]`\n"
        f"→ **{total} điểm • {rr}**\n\n"
        f"🟢 **THẮNG**\n{chr(10).join(win) or 'Không có'}\n\n"
        f"🔴 **THUA**\n{chr(10).join(lose) or 'Không có'}",
        GREEN if win else RED))
    tx.update(bets={},tai=0,xiu=0,msg=None)

# ================= XOCDIA =================

@bot.command(name="xd")
async def xd(ctx,ch:str=None,bet:int=None):
    ch=(ch or "").lower()
    if ch not in ("chan","le") or not bet or bet<=0:
        return await ctx.send("❌ `!xd chan 100` hoặc `!xd le 100`")
    u=user(ctx.author.id,ctx.author.name)
    if u["cash"]<bet:return await ctx.send("❌ Không đủ tiền!")
    u["cash"]-=bet
    m=await ctx.send(embed=emb("🪙 XÓC ĐĨA",
        f"🎯 Cược **{ch.upper()}** `{bet:,}$`\n\n"
        "🟠 **ĐANG XÓC...**\n\n`[ ⚪ ⚪ ⚪ ⚪ ]`",ORANGE))
    await asyncio.sleep(1.2)
    n=random.randint(0,4);r="chan" if n%2==0 else "le";win=r==ch
    if win:u["cash"]+=bet*2
    balls="🔴"*n+"⚪"*(4-n)
    await m.edit(embed=emb("🪙 XÓC ĐĨA",
        f"🎯 Cược **{ch.upper()}** `{bet:,}$`\n\n"
        f"`[ {balls} ]` → **{r.upper()}**\n\n"
        +(f"🎉 **THẮNG +{bet:,}$**" if win else f"💸 **THUA -{bet:,}$**"),
        GREEN if win else RED))

# ================= BAU CUA =================

@bot.command(name="bc")
async def bc(ctx,ch:str=None,bet:int=None):
    a={"ca":"🐟","tom":"🦐","cua":"🦀","bau":"🥒","ga":"🐓","nai":"🦌"}
    ch=(ch or "").lower()
    if ch not in a or not bet or bet<=0:return await ctx.send("❌ `!bc cua 500`")
    u=user(ctx.author.id,ctx.author.name)
    if u["cash"]<bet:return await ctx.send("❌ Không đủ tiền!")
    u["cash"]-=bet
    m=await ctx.send(embed=emb("🎲 BẦU CUA",
        f"🎯 Cược **{a[ch]} {ch.upper()}** `{bet:,}$`\n\n"
        "🟠 **ĐANG LẮC HỘT...**\n\n`[ ❔ ] [ ❔ ] [ ❔ ]`",ORANGE))
    await asyncio.sleep(1.2)
    r=[random.choice(list(a)) for _ in range(3)];n=r.count(ch)
    if n:u["cash"]+=bet*(n+1)
    result=f"🎉 **TRÚNG {n} CON! +{bet*n:,}$**" if n else f"💸 **THUA -{bet:,}$**"
    await m.edit(embed=emb("🎲 BẦU CUA",
        f"🎯 Cược **{a[ch]} {ch.upper()}** `{bet:,}$`\n\n"
        f"`[ {a[r[0]]} ] [ {a[r[1]]} ] [ {a[r[2]]} ]`\n\n{result}",
        GREEN if n else RED))

# ================= RUN =================

token=os.getenv("TOKEN_BOT")
if not token:print("❌ Chưa có TOKEN_BOT!")
else:bot.run(token)
