import os,asyncio,random,secrets,time,discord
from discord.ext import commands

I=discord.Intents.default();I.message_content=True
bot=commands.Bot(command_prefix="!",intents=I,help_command=None)

U={};C={}
BLUE,ORANGE,GREEN,RED,YELLOW=0x3498DB,0xF1C40F,0x2ECC71,0xE74C3C,0xF1C40F
TX={"on":0,"bets":{},"tai":0,"xiu":0,"msg":None}

def E(t,d,c=BLUE):
    return discord.Embed(title=t,description=d,color=c)

def user(i,n="Thành viên"):
    if i not in U:
        U[i]={"name":n,"cash":4899,"bank":0,"debt":0,"vip":0}
    return U[i]

def adm(c):
    return c.author.guild_permissions.administrator

async def blocked(c):
    if user(c.author.id,c.author.name)["debt"]>0:
        await c.send("🚫 Bạn đang có nợ, hãy trả hết nợ!")
        return 1
    return 0

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("!trogiup | Casino Bet88"))
    print("ONLINE:",bot.user)

# ================= HELP =================

@bot.command(name="trogiup",aliases=["help"])
async def help(c):
    await c.send(embed=E(
        "🎰 CASINO BET88",
        "**🎲 CASINO**\n"
        "`!tx tai 1000` `!tx xiu 1000`\n"
        "`!bc cua 1000` `!xd chan 1000` `!quay 1000`\n\n"
        "**💰 TIỀN**\n"
        "`!vi` `!gui` `!rut` `!chuyen @User 100`\n"
        "`!diemdanh` `!bxh`\n\n"
        "**💛 VIP**\n"
        "`!muarole Vip`\n\n"
        "**👑 ADMIN**\n"
        "`!taocode 10000 1`\n"
        "`!thuongcode 10000 10`\n"
        "`!settien @User 10000`\n"
        "`!resettien @User`"
    ))

# ================= VI =================

@bot.command()
async def vi(c,m:discord.Member=None):
    m=m or c.author
    u=user(m.id,m.name)

    if u["vip"]:
        hang="👑 **VIP**"
    else:
        hang="🐥 Người chơi Thường"

    await c.send(embed=E(
        "💳 TÀI KHOẢN",
        f"👤 **{m.name}**\n"
        f"🏷️ Hạng: {hang}\n\n"
        f"💵 Ví: `{u['cash']:,}$`\n"
        f"🏦 Bank: `{u['bank']:,}$`"
    ))

# ================= TIỀN =================

@bot.command()
async def gui(c,n:int=None):
    u=user(c.author.id,c.author.name)
    if not n or n<=0 or u["cash"]<n:
        return await c.send("❌ Không đủ tiền!")
    u["cash"]-=n
    u["bank"]+=n
    await c.send(f"🏦 Gửi `{n:,}$` thành công!")

@bot.command()
async def rut(c,n:int=None):
    u=user(c.author.id,c.author.name)
    if not n or n<=0 or u["bank"]<n:
        return await c.send("❌ Bank không đủ!")
    u["bank"]-=n
    u["cash"]+=n
    await c.send(f"🏦 Rút `{n:,}$` thành công!")

@bot.command()
async def chuyen(c,m:discord.Member=None,n:int=None):
    if not m or not n or n<=0:
        return await c.send("❌ `!chuyen @User 100`")

    a=user(c.author.id,c.author.name)
    b=user(m.id,m.name)

    if a["cash"]<n:
        return await c.send("❌ Không đủ tiền!")

    a["cash"]-=n
    b["cash"]+=n

    await c.send(
        f"💸 {c.author.mention} → {m.mention}: `{n:,}$`"
    )

# ================= ĐIỂM DANH =================

@bot.command()
async def diemdanh(c):
    u=user(c.author.id,c.author.name)

    now=time.time()
    last=u.get("dd",0)
    cooldown=43200

    if now-last<cooldown:
        remain=int(cooldown-(now-last))
        return await c.send(
            f"❌ **Mày đã điểm danh rồi!**\n"
            f"⏳ Đợi **{remain:,} giây** nữa."
        )

    u["dd"]=now
    u["cash"]+=2593

    await c.send(embed=E(
        "🎁 ĐIỂM DANH",
        "💰 **+2,593$ vào ví**\n\n"
        "⏰ Lần tiếp theo sau **43,200 giây**.",
        GREEN
    ))

# ================= BXH =================

@bot.command()
async def bxh(c):
    x=sorted(
        U.values(),
        key=lambda z:z["cash"]+z["bank"],
        reverse=True
    )[:5]

    await c.send(embed=E(
        "🏆 TOP 5",
        "".join(
            f"\n**{i}.** {u['name']} — "
            f"`{u['cash']+u['bank']:,}$`"
            for i,u in enumerate(x,1)
        )
    ))

# ================= TÀI XỈU =================

@bot.command()
async def tx(c,ch=None,bet:int=None):
    if await blocked(c):
        return

    if ch not in ("tai","xiu") or not bet or bet<=0:
        return await c.send(
            "❌ `!tx tai 1000` hoặc `!tx xiu 1000`"
        )

    if bet>10_000_000:
        return await c.send(
            "❌ Cược tối đa **10,000,000$/ván**!"
        )

    u=user(c.author.id,c.author.name)
    i=c.author.id

    if u["cash"]<bet:
        return await c.send("❌ Không đủ tiền!")

    if i in TX["bets"]:
        return await c.send("❌ Bạn đã cược ván này!")

    if not TX["on"]:
        TX.update(on=1,bets={},tai=0,xiu=0)

        TX["msg"]=await c.send(embed=E(
            "🎲 SÒNG TÀI XỈU 30S 🎲",
            "🎯 **ĐẶT CƯỢC TÀI XỈU**\n\n"
            "Gõ `!tx tai <tiền>` hoặc `!tx xiu <tiền>`\n\n"
            "⏱️ **Thời gian: 30 giây**\n"
            "💰 **Tối đa: 10,000,000$/ván**\n\n"
            "🔴 **Tài:** `0$`\n"
            "🔵 **Xỉu:** `0$`",
            ORANGE
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
        "🎯 **ĐANG NHẬN CƯỢC**\n\n"
        "`!tx tai <tiền>` hoặc `!tx xiu <tiền>`\n\n"
        "⏱️ **30 giây**\n"
        "💰 **Max 10,000,000$/ván**\n\n"
        f"🔴 **Tài:** `{TX['tai']:,}$`\n"
        f"🔵 **Xỉu:** `{TX['xiu']:,}$`",
        ORANGE
    ))

    try:
        await c.message.delete()
    except:
        pass

async def txround():
    await asyncio.sleep(30)

    d=[
        random.randint(1,6),
        random.randint(1,6),
        random.randint(1,6)
    ]

    total=sum(d)
    r="tai" if total>=11 else "xiu"

    w=[]
    l=[]

    for i,b in TX["bets"].items():

        if b["choice"]==r:

            p=b["amount"]*2

            if user(i).get("vip"):
                p=int(p*1.5)

            user(i)["cash"]+=p

            w.append(
                f"• {b['name']} `+{p:,}$`"
            )

        else:
            l.append(
                f"• {b['name']} `-{b['amount']:,}$`"
            )

    await TX["msg"].edit(embed=E(
        "🎲 KẾT QUẢ TÀI XỈU",
        f"`[ {d[0]} | {d[1]} | {d[2]} ]`\n\n"
        f"➡️ **{total} điểm — {r.upper()}**\n\n"
        f"🎉 **THẮNG**\n"
        f"{chr(10).join(w) or 'Không có'}\n\n"
        f"💸 **THUA**\n"
        f"{chr(10).join(l) or 'Không có'}",
        GREEN if w else RED
    ))

    TX.update(
        on=0,
        bets={},
        tai=0,
        xiu=0,
        msg=None
    )

# ================= BẦU CUA =================

@bot.command()
async def bc(c,ch=None,bet:int=None):
    if await blocked(c):
        return

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
        "🦀 BẦU CUA",
        "🎲 **LẮC... LẮC... LẮC...**\n\n"
        "`[ ❔ | ❔ | ❔ ]`",
        ORANGE
    ))

    await asyncio.sleep(1.5)

    r=[
        random.choice(list(a)),
        random.choice(list(a)),
        random.choice(list(a))
    ]

    n=r.count(ch)

    if n:
        p=int(bet*(n+1))
        if u["vip"]:
            p=int(p*1.5)

        u["cash"]+=p
        res=f"🎉 **THẮNG +{p:,}$ vào ví**"
        co=GREEN

    else:
        res=f"💸 **THUA -{bet:,}$**"
        co=RED

    await m.edit(embed=E(
        "🦀 BẦU CUA",
        f"`[ {' | '.join(a[x] for x in r)} ]`\n\n"
        f"{res}\n"
        f"💵 Ví: `{u['cash']:,}$`",
        co
    ))

# ================= XÓC ĐĨA =================

@bot.command()
async def xd(c,ch=None,bet:int=None):
    if await blocked(c):
        return

    if ch not in ("chan","le") or not bet or bet<=0:
        return await c.send(
            "❌ `!xd chan 1000` hoặc `!xd le 1000`"
        )

    if bet>10_000_000:
        return await c.send(
            "❌ Cược tối đa **10,000,000$**!"
        )

    u=user(c.author.id,c.author.name)

    if u["cash"]<bet:
        return await c.send("❌ Không đủ tiền!")

    u["cash"]-=bet

    # HIỆN XÓC TRƯỚC
    m=await c.send(embed=E(
        "🪙 XÓC ĐĨA",
        "🟠 **XÓC... XÓC... XÓC...**\n\n"
        "`[ ⚪ | ⚪ | ⚪ | ⚪ ]`",
        ORANGE
    ))

    await asyncio.sleep(2)

    # KẾT QUẢ
    n=random.randint(0,4)

    r="chan" if n%2==0 else "le"
    win=(r==ch)

    dia=" | ".join(
        "🔴" if i<n else "⚪"
        for i in range(4)
    )

    if win:
        p=bet*2

        if u["vip"]:
            p=int(p*1.5)

        u["cash"]+=p

        result=f"🎉 **THẮNG +{p:,}$ vào ví**"
        color=GREEN

    else:
        result=f"💸 **THUA -{bet:,}$**"
        color=RED

    await m.edit(embed=E(
        "🪙 XÓC ĐĨA",
        f"`[ {dia} ]`\n\n"
        f"🎯 **KẾT QUẢ: {r.upper()}**\n\n"
        f"{result}\n"
        f"💵 Ví: `{u['cash']:,}$`",
        color
    ))

# ================= QUAY =================

@bot.command()
async def quay(c,bet:int=None):
    if await blocked(c):
        return

    if not bet or bet<=0:
        return await c.send("❌ `!quay 1000`")

    if bet>10_000_000:
        return await c.send(
            "❌ Max **10,000,000$**!"
        )

    u=user(c.author.id,c.author.name)

    if u["cash"]<bet:
        return await c.send("❌ Không đủ tiền!")

    u["cash"]-=bet

    m=await c.send(embed=E(
        "🎰 MÁY SLOT",
        "🎰 **ĐANG QUAY...**\n\n"
        "`[ ❔ | ❔ | ❔ ]`",
        ORANGE
    ))

    await asyncio.sleep(1.2)

    s=[
        random.choice(
            ["🍒","🍋","🔔","⭐","💎","7️⃣"]
        )
        for _ in range(3)
    ]

    same=max(s.count(x) for x in set(s))

    if same==3:
        p=bet*5

        if u["vip"]:
            p=int(p*1.5)

        u["cash"]+=p
        res=f"🎉 **NỔ HŨ +{p:,}$ vào ví**"
        co=GREEN

    elif same==2:
        p=bet*2

        if u["vip"]:
            p=int(p*1.5)

        u["cash"]+=p
        res=f"🎉 **THẮNG +{p:,}$ vào ví**"
        co=GREEN

    else:
        res=f"💸 **THUA -{bet:,}$**"
        co=RED

    await m.edit(embed=E(
        "🎰 MÁY SLOT",
        f"`[ {' | '.join(s)} ]`\n\n"
        f"{res}\n"
        f"💵 Ví: `{u['cash']:,}$`",
        co
    ))

# ================= VIP =================

@bot.command()
async def muarole(c,r=None):
    if (r or "").lower()!="vip":
        return await c.send("❌ `!muarole Vip`")

    u=user(c.author.id,c.author.name)

    if u["vip"]:
        return await c.send("💛 Bạn đã là VIP!")

    if u["cash"]<30_000_000:
        return await c.send(
            "❌ VIP giá **30,000,000$**!"
        )

    role=discord.utils.find(
        lambda x:x.name.lower()=="vip",
        c.guild.roles
    )

    if not role:
        return await c.send(
            "❌ Server chưa có role `Vip`!"
        )

    if role>=c.guild.me.top_role:
        return await c.send(
            "❌ Kéo role Vip xuống dưới role Bot!"
        )

    try:
        await c.author.add_roles(role)
    except:
        return await c.send(
            "❌ Bot thiếu quyền quản lý role!"
        )

    u["cash"]-=30_000_000
    u["vip"]=1

    await c.send(embed=E(
        "👑 VIP",
        f"🎉 {c.author.mention} đã trở thành **VIP**!\n\n"
        "👑 Hạng: **VIP**\n"
        "💰 Giá: `30,000,000$`\n"
        "🎯 Thưởng game: **x1.5**",
        YELLOW
    ))

# ================= CODE =================

def newcode():
    return "BET-"+secrets.token_hex(3).upper()

@bot.command()
async def thuongcode(c,n:int=None,uses:int=None):
    if not adm(c):
        return await c.send("⛔ Chỉ Admin!")

    if not n or not uses:
        return await c.send(
            "❌ `!thuongcode 1000 5`"
        )

    x=newcode()

    C[x]={
        "money":n,
        "uses":uses,
        "used":set()
    }

    await c.send(embed=E(
        "🎁 PHẦN THƯỞNG CODE",
        f"🔐 Mã: `{x}`\n"
        f"💰 Tiền: `{n:,}$`\n"
        f"👥 Lượt: `{uses}`\n\n"
        f"`!nhapcode {x}`",
        GREEN
    ))

@bot.command()
async def nhapcode(c,x=None):
    x=(x or "").upper()

    if x not in C:
        return await c.send(
            "❌ Code không tồn tại!"
        )

    z=C[x]

    if (
        c.author.id in z["used"]
        or len(z["used"])>=z["uses"]
    ):
        return await c.send(
            "❌ Code hết lượt!"
        )

    z["used"].add(c.author.id)

    user(
        c.author.id,
        c.author.name
    )["cash"]+=z["money"]

    await c.send(
        f"🎁 **+{z['money']:,}$ vào ví!**"
    )

@bot.command()
async def taocode(c,n:int=None,uses:int=None):
    if not adm(c):
        return await c.send("⛔ Chỉ Admin!")

    if not n or not uses:
        return await c.send(
            "❌ `!taocode 1000 1`"
        )

    x=newcode()

    C[x]={
        "money":n,
        "uses":uses,
        "used":set()
    }

    try:
        await c.author.send(
            f"🎁 CODE: `{x}`\n"
            f"💰 `{n:,}$`\n"
            f"👥 `{uses}` lượt"
        )
    except:
        pass

    await c.send("✅ Code đã gửi DM!")

# ================= ADMIN =================

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
        f"👤 {m.mention}\n"
        f"💵 Ví mới: **`{n:,}$`**\n\n"
        "✅ **Đã cập nhật!**",
        GREEN
    ))

@bot.command()
async def resettien(c,m:discord.Member=None):
    if not adm(c):
        return await c.send("⛔ Chỉ Admin!")

    if not m:
        return await c.send(
            "❌ `!resettien @User`"
        )

    user(m.id,m.name)["cash"]=4899

    await c.send(embed=E(
        "🔄 RESET TIỀN",
        f"👤 {m.mention}\n"
        "💵 Ví: **`4,899$`**\n\n"
        "🧹 **Đã reset tiền!**",
        ORANGE
    ))

# ================= START =================

token=os.getenv("TOKEN_BOT")

if token:
    bot.run(token)
else:
    print("❌ Chưa có TOKEN_BOT!")
