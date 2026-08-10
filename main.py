import os, asyncio, random, secrets, time, discord
from discord.ext import commands

I=discord.Intents.default()
I.message_content=True
bot=commands.Bot(command_prefix="!",intents=I,help_command=None)

U,C,D={}, {}, {}
DEFAULT=4899
BLUE,ORANGE,GREEN,RED=0x3498DB,0xF1C40F,0x2ECC71,0xE74C3C

TX={"on":False,"bets":{},"tai":0,"xiu":0,"msg":None}

def E(t,d,c=BLUE):
    return discord.Embed(title=t,description=d,color=c)

def user(i,n="Thành viên"):
    if i not in U:
        U[i]={"name":n,"cash":DEFAULT,"bank":0,
              "hang":"Người chơi Thường","ga":"Gà Công Nghiệp 🐥",
              "debt":0,"due":0}
    return U[i]

def admin(ctx):
    return ctx.author.guild_permissions.administrator

def no_check(ctx):
    u=user(ctx.author.id,ctx.author.name)
    if u["debt"]>0:
        return True
    return False

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("!trogiup | Casino Bet88"))
    print("BOT ONLINE:",bot.user)

# ===== HELP =====

@bot.command(name="trogiup",aliases=["help"])
async def help(ctx):
    await ctx.send(embed=E("🎰 CASINO BET88",
    "**🎲 CASINO**\n"
    "`!tx tai 1000` `!tx xiu 1000`\n"
    "`!bc cua 1000` `!xd chan 1000` `!quay 1000`\n\n"
    "**💰 TIỀN**\n"
    "`!vi` `!gui` `!rut` `!chuyen @User 100`\n"
    "`!diemdanh` `!bxh`\n\n"
    "**🏦 VAY TIỀN**\n"
    "`!vay 1000` — vay 1,000$ đến 100,000$\n"
    "`!trano 1000` — trả nợ\n"
    "`!no` — xem khoản nợ\n\n"
    "**👑 ADMIN**\n"
    "`!taocode 10000 1`\n"
    "`!thuongcode 10000 10`\n"
    "`!settien @User 10000`\n"
    "`!resettien @User`",BLUE))

# ===== MONEY =====

@bot.command(name="vi",aliases=["bal","money"])
async def vi(ctx,m:discord.Member=None):
    m=m or ctx.author
    u=user(m.id,m.name)
    debt=f"\n💳 Nợ: `{u['debt']:,}$`" if u["debt"] else ""
    await ctx.send(embed=E("💳 THÔNG TIN TÀI KHOẢN",
    f"👤 **{m.name.upper()}**\n"
    f"🏷️ {u['hang']}\n🐓 {u['ga']}\n\n"
    f"💵 Tiền mặt: `{u['cash']:,}$`\n"
    f"🏦 Ngân hàng: `{u['bank']:,}$`{debt}"))

@bot.command(name="diemdanh")
async def dd(ctx):
    u=user(ctx.author.id,ctx.author.name)
    now=time.time()
    if now-u.get("dd",0)<43200:
        left=int((43200-(now-u.get("dd",0)))/3600)
        return await ctx.send(f"⏳ Bạn đã điểm danh. Còn khoảng **{left} giờ**!")
    u["dd"]=now
    u["cash"]+=2593
    await ctx.send(embed=E("🎁 ĐIỂM DANH",
    f"💰 Nhận **+2,593$**\n💵 Ví: `{u['cash']:,}$`",GREEN))

@bot.command()
async def gui(ctx,n:int=None):
    u=user(ctx.author.id,ctx.author.name)
    if not n or n<=0 or u["cash"]<n:
        return await ctx.send("❌ Không đủ tiền!")
    u["cash"]-=n;u["bank"]+=n
    await ctx.send(embed=E("🏦 GỬI TIỀN",
    f"💰 `{n:,}$`\n🏦 Bank: `{u['bank']:,}$`"))

@bot.command()
async def rut(ctx,n:int=None):
    u=user(ctx.author.id,ctx.author.name)
    if not n or n<=0 or u["bank"]<n:
        return await ctx.send("❌ Bank không đủ!")
    u["bank"]-=n;u["cash"]+=n
    await ctx.send(embed=E("🏦 RÚT TIỀN",
    f"💰 `{n:,}$`\n💵 Ví: `{u['cash']:,}$`"))

@bot.command()
async def chuyen(ctx,m:discord.Member=None,n:int=None):
    if not m or not n or n<=0 or m.bot or m.id==ctx.author.id:
        return await ctx.send("❌ `!chuyen @User 100`")
    a,b=user(ctx.author.id,ctx.author.name),user(m.id,m.name)
    if a["cash"]<n:return await ctx.send("❌ Không đủ tiền!")
    a["cash"]-=n;b["cash"]+=n
    await ctx.send(embed=E("💸 CHUYỂN TIỀN",
    f"{ctx.author.mention} → {m.mention}\n💰 `{n:,}$`"))

@bot.command(name="bxh")
async def bxh(ctx):
    x=sorted(U.values(),key=lambda u:u["cash"]+u["bank"],reverse=True)[:5]
    s="\n".join(f"{i+1}. **{u['name']}** — `{u['cash']+u['bank']:,}$`"
                for i,u in enumerate(x))
    await ctx.send(embed=E("🏆 TOP 5 GIÀU NHẤT",s))

# ===== VAY TIỀN =====

@bot.command(name="vay")
async def vay(ctx,n:int=None):
    u=user(ctx.author.id,ctx.author.name)

    if u["debt"]>0:
        return await ctx.send("🚫 Bạn đang có khoản nợ! Hãy trả hết trước.")

    if not n or n<1000 or n>100000:
        return await ctx.send("❌ Số tiền vay từ **1,000$ - 100,000$**!")

    u["cash"]+=n
    u["debt"]=n
    u["due"]=time.time()+3600

    await ctx.send(embed=E("💰 VAY TIỀN", 
    f"🏦 Bạn đã vay thành công: **{n:,}$**\n"
    f"💵 Ví hiện tại: `{u['cash']:,}$`\n"
    f"⏰ Thời hạn trả: **1 giờ**\n\n"
    f"⚠️ Hết hạn không trả sẽ trở thành **Con nợ** và bị khóa chơi!",
    ORANGE))

@bot.command(name="no")
async def no(ctx):
    u=user(ctx.author.id,ctx.author.name)

    if not u["debt"]:
        return await ctx.send("✅ Bạn không có khoản nợ.")

    left=max(0,int(u["due"]-time.time()))
    h=left//3600
    m=(left%3600)//60

    await ctx.send(embed=E("💳 KHOẢN NỢ",
    f"💰 Nợ hiện tại: **{u['debt']:,}$**\n"
    f"⏰ Còn: **{h} giờ {m} phút**\n\n"
    f"💡 Dùng `!trano {u['debt']}` để trả hết.",
    RED if left==0 else ORANGE))

@bot.command(name="trano")
async def trano(ctx,n:int=None):
    u=user(ctx.author.id,ctx.author.name)

    if u["debt"]<=0:
        return await ctx.send("✅ Bạn không có khoản nợ.")

    if not n or n<=0:
        return await ctx.send(f"❌ Dùng `!trano {u['debt']}`")

    n=min(n,u["debt"])

    if u["cash"]<n:
        return await ctx.send("❌ Ví không đủ tiền trả nợ!")

    u["cash"]-=n
    u["debt"]-=n

    if u["debt"]==0:
        u["due"]=0
        await ctx.send(embed=E("✅ TRẢ NỢ THÀNH CÔNG",
        f"💰 Đã trả: **{n:,}$**\n"
        f"💳 Nợ còn: `0$`\n"
        f"💵 Ví: `{u['cash']:,}$`\n\n"
        f"🎉 Bạn có thể chơi lại bình thường!",GREEN))
    else:
        await ctx.send(embed=E("💳 TRẢ MỘT PHẦN",
        f"💰 Đã trả: **{n:,}$**\n"
        f"💳 Còn nợ: **{u['debt']:,}$**\n"
        f"💵 Ví: `{u['cash']:,}$`",ORANGE))

# ===== CHECK NỢ =====

async def blocked(ctx):
    u=user(ctx.author.id,ctx.author.name)
    if u["debt"]>0:
        if time.time()>u["due"]:
            return await ctx.send(embed=E("🚫 CON NỢ",
            f"Bạn đã quá hạn trả nợ!\n"
            f"💳 Nợ còn lại: **{u['debt']:,}$**\n\n"
            f"🚫 **Không thể chơi casino cho đến khi trả hết nợ.**\n"
            f"💡 Dùng `!trano {u['debt']}`",RED))
        return False
    return False

# ===== CODE =====

def newcode():
    return "BET-"+secrets.token_hex(3).upper()

@bot.command()
async def taocode(ctx,n:int=None,uses:int=None):
    if not admin(ctx):return await ctx.send("⛔ Chỉ Admin!")
    if not n or not uses:return await ctx.send("❌ `!taocode tiền lượt`")
    c=newcode()
    C[c]={"money":n,"uses":uses,"used":set()}
    try:
        await ctx.author.send(embed=E("🔐 CODE ADMIN",
        f"🎟️ `{c}`\n💰 `{n:,}$`\n🔢 `{uses}` lượt",BLUE))
        await ctx.send("✅ Code đã gửi riêng vào DM.")
    except:
        await ctx.send(f"🔐 Code: `{c}`")

@bot.command()
async def thuongcode(ctx,n:int=None,uses:int=None):
    if not admin(ctx):return await ctx.send("⛔ Chỉ Admin!")
    if not n or not uses:return await ctx.send("❌ `!thuongcode tiền lượt`")
    c=newcode()
    C[c]={"money":n,"uses":uses,"used":set()}
    await ctx.send(embed=E("🎁 CODE THƯỞNG",
    f"🎟️ **{c}**\n💰 **{n:,}$**\n👥 **{uses} lượt**\n\n"
    f"`!nhapcode {c}`",GREEN))

@bot.command()
async def nhapcode(ctx,c=None):
    if not c or c.upper() not in C:
        return await ctx.send("❌ Code không tồn tại!")
    c=C[c.upper()]
    i=ctx.author.id
    if i in c["used"]:return await ctx.send("❌ Bạn đã dùng code!")
    if len(c["used"])>=c["uses"]:
        return await ctx.send("❌ Code hết lượt!")
    c["used"].add(i)
    user(i,ctx.author.name)["cash"]+=c["money"]
    await ctx.send(embed=E("🎁 NHẬP CODE THÀNH CÔNG",
    f"💰 Nhận **+{c['money']:,}$**",GREEN))

@bot.command()
async def settien(ctx,m:discord.Member=None,n:int=None):
    if not admin(ctx):return await ctx.send("⛔ Chỉ Admin!")
    if not m or n is None:return await ctx.send("❌ `!settien @User tiền`")
    user(m.id,m.name)["cash"]=max(0,n)
    await ctx.send(f"✅ {m.mention}: `{n:,}$`")

@bot.command(name="resettien")
async def reset(ctx,m:discord.Member=None):
    if not admin(ctx):return await ctx.send("⛔ Chỉ Admin!")
    if not m:return await ctx.send("❌ `!resettien @User`")
    user(m.id,m.name)["cash"]=DEFAULT
    await ctx.send(f"🔄 {m.mention} → `{DEFAULT:,}$`")

# ===== TÀI XỈU =====

@bot.command()
async def tx(ctx,choice=None,bet:int=None):
    if await blocked(ctx): return

    if not choice or choice.lower() not in ("tai","xiu") or not bet or bet<=0:
        return await ctx.send("❌ `!tx tai 1000` hoặc `!tx xiu 1000`")

    choice=choice.lower()
    u=user(ctx.author.id,ctx.author.name)
    i=ctx.author.id

    if bet>10_000_000:
        return await ctx.send("❌ Cược max **10,000,000$**!")
    if i in TX["bets"]:
        return await ctx.send("❌ Mỗi người chỉ cược **1 lần/ván**!")
    if u["cash"]<bet:
        return await ctx.send("❌ Không đủ tiền!")

    if not TX["on"]:
        TX.update(on=True,bets={},tai=0,xiu=0)
        TX["msg"]=await ctx.send(embed=E("🎲 SÒNG TÀI XỈU 30S 🎲",
        "Gõ `!tx <tai/xiu> <tiền>`\n"
        "💰 **Tối đa 10,000,000$/ván**\n\n"
        "⏱️ **Thời gian: 30 giây**\n\n"
        "💰 Tổng Tài: `0$` | Tổng Xỉu: `0$`",ORANGE))
        asyncio.create_task(txround())

    u["cash"]-=bet
    TX["bets"][i]={"name":ctx.author.name,"choice":choice,"amount":bet}
    TX[choice]+=bet

    e=TX["msg"].embeds[0]
    e.description=(
        "Gõ `!tx <tai/xiu> <tiền>`\n"
        "💰 **Tối đa 10,000,000$/ván**\n\n"
        "⏱️ **Thời gian: 30 giây**\n\n"
        f"💰 Tổng Tài: `{TX['tai']:,}$` | "
        f"Tổng Xỉu: `{TX['xiu']:,}$`")
    await TX["msg"].edit(embed=e)

    try:await ctx.message.delete()
    except:pass

async def txround():
    await asyncio.sleep(30)
    if not TX["on"]:return

    TX["on"]=False
    m=TX["msg"]

    await m.edit(embed=E("🎲 KẾT QUẢ TÀI XỈU",
    "🥣 **XÓC... XÓC... XÓC...**\n\n"
    "`[ ❔ | ❔ | ❔ ]`",ORANGE))

    await asyncio.sleep(2)

    d=[random.randint(1,6) for _ in range(3)]
    total=sum(d)
    r="tai" if total>=11 else "xiu"

    win=[];lose=[]

    for i,b in TX["bets"].items():
        if b["choice"]==r:
            user(i)["cash"]+=b["amount"]*2
            win.append(f"• {b['name']} `+{b['amount']:,}$`")
        else:
            lose.append(f"• {b['name']} `-{b['amount']:,}$`")

    await m.edit(embed=E("🎲 KẾT QUẢ TÀI XỈU",
    f"Xúc xắc\n\n"
    f"`[ {d[0]} | {d[1]} | {d[2]} ]`\n\n"
    f"➡️ **{total} điểm ({'TÀI 🔴' if r=='tai' else 'XỈU 🔵'})**\n\n"
    "🎉 **THẮNG**\n"+("\n".join(win)or"Không có")+
    "\n\n💸 **THUA**\n"+("\n".join(lose)or"Không có"),
    GREEN if win else RED))

    TX.update(bets={},tai=0,xiu=0,msg=None)

# ===== BẦU CUA =====

@bot.command()
async def bc(ctx,choice=None,bet:int=None):
    if await blocked(ctx): return

    a={"ca":"🐟","tom":"🦐","cua":"🦀","bau":"🥒","ga":"🐓","nai":"🦌"}

    if not choice or choice.lower() not in a or not bet or bet<=0:
        return await ctx.send("❌ `!bc cua 1000`")

    u=user(ctx.author.id,ctx.author.name)

    if u["cash"]<bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"]-=bet
    choice=choice.lower()

    m=await ctx.send(embed=E("🦀 BẦU CUA CÁ TÔM",
    "🟠 **LẮC... LẮC... LẮC...**\n\n"
    "`[ ❔ | ❔ | ❔ ]`",ORANGE))

    await asyncio.sleep(1.5)

    r=[random.choice(list(a)) for _ in range(3)]
    n=r.count(choice)

    if n:
        u["cash"]+=bet*(n+1)

    icons=" | ".join(a[x] for x in r)

    if n:
        result=f"🎉 **THẮNG +{bet*n:,}$ VÀO TÚI**"
    else:
        result=f"💸 **TRẬT LẮT! -{bet:,}$**"

    await m.edit(embed=E("🦀 BẦU CUA CÁ TÔM",
    f"**KẾT QUẢ**\n\n"
    f"`[ {icons} ]`\n\n"
    f"**TỔNG KẾT**\n"
    f"{result}\n"
    f"💵 Ví: `{u['cash']:,}$`",
    GREEN if n else RED))

# ===== XÓC ĐĨA =====

@bot.command()
async def xd(ctx,choice=None,bet:int=None):
    if await blocked(ctx): return

    if not choice or choice.lower() not in ("chan","le") or not bet or bet<=0:
        return await ctx.send("❌ `!xd chan 1000` hoặc `!xd le 1000`")

    u=user(ctx.author.id,ctx.author.name)

    if u["cash"]<bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"]-=bet
    choice=choice.lower()

    m=await ctx.send(embed=E("🪙 XÓC ĐĨA",
    "🟠 **XÓC... XÓC... XÓC...**\n\n"
    "`[ ⚪ | ⚪ | ⚪ | ⚪ ]`",ORANGE))

    await asyncio.sleep(1.5)

    n=random.randint(0,4)
    r="chan" if n%2==0 else "le"
    win=r==choice

    if win:
        u["cash"]+=bet*2

    balls=" | ".join(["🔴" if i<n else "⚪" for i in range(4)])

    result=(
        f"🎉 **THẮNG +{bet:,}$ VÀO TÚI**"
        if win else f"💸 **THUA -{bet:,}$**")

    await m.edit(embed=E("🪙 XÓC ĐĨA",
    f"**KẾT QUẢ**\n\n"
    f"`[ {balls} ]`\n\n"
    f"🎯 **{r.upper()}**\n\n"
    f"{result}\n"
    f"💵 Ví: `{u['cash']:,}$`",
    GREEN if win else RED))

# ===== QUAY SLOT =====

@bot.command()
async def quay(ctx,bet:int=None):
    if await blocked(ctx): return

    if not bet or bet<=0:
        return await ctx.send("❌ `!quay 1000`")

    u=user(ctx.author.id,ctx.author.name)

    if u["cash"]<bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"]-=bet

    m=await ctx.send(embed=E("🎰 MÁY SLOT NỔ HŨ",
    "🎰 **QUAY... QUAY... QUAY...**\n\n"
    "`[ ❔ | ❔ | ❔ ]`",ORANGE))

    await asyncio.sleep(1)

    s=[random.choice(["🍒","🍋","🔔","⭐","💎","7️⃣"]) for _ in range(3)]
    win=s[0]==s[1]==s[2]

    if win:
        u["cash"]+=bet*5

    icons=" | ".join(s)

    result=(
        f"🎉 **NỔ HŨ! +{bet*5:,}$ VÀO TÚI**"
        if win else f"💸 **TRẬT HŨ! -{bet:,}$**")

    await m.edit(embed=E("🎰 MÁY SLOT NỔ HŨ",
    f"**KẾT QUẢ**\n\n"
    f"`[ {icons} ]`\n\n"
    f"**THÔNG BÁO**\n"
    f"{result}\n"
    f"💵 Ví: `{u['cash']:,}$`",
    GREEN if win else RED))

# ===== RUN =====

token=os.getenv("TOKEN_BOT")

if not token:
    print("❌ Chưa có TOKEN_BOT!")
else:
    bot.run(token)
