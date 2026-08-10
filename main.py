import os,asyncio,random,secrets,time,discord
from discord.ext import commands

I=discord.Intents.default();I.message_content=True
bot=commands.Bot(command_prefix="!",intents=I,help_command=None)

U={};C={}
BLUE,ORANGE,GREEN,RED=0x3498DB,0xF1C40F,0x2ECC71,0xE74C3C
VIP_ROLE="Vip";VIP_PRICE=30_000_000
TX={"on":False,"bets":{},"tai":0,"xiu":0,"msg":None}

def E(t,d,c=BLUE):return discord.Embed(title=t,description=d,color=c)

def user(i,n="Thành viên"):
    if i not in U:
        U[i]={"name":n,"cash":4899,"bank":0,"debt":0}
    return U[i]

def adm(c):return c.author.guild_permissions.administrator

def vip(ctx):
    r=discord.utils.get(ctx.guild.roles,name=VIP_ROLE)
    return bool(r and r in ctx.author.roles)

def winmoney(ctx,bet,mul=2):
    return int(bet*mul*(1.5 if vip(ctx) else 1))

async def blocked(ctx):
    u=user(ctx.author.id,ctx.author.name)
    if u["debt"]>0:
        await ctx.send(
            f"🚫 **CON NỢ**\n"
            f"💳 Nợ: `{u['debt']:,}$`\n"
            f"💡 Dùng `!trano {u['debt']}` để trả."
        )
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
    "`!tx tai 1000` `!tx xiu 1000`\n"
    "`!bc cua 1000` `!xd chan 1000` `!quay 1000`\n\n"
    "`!vi` `!gui` `!rut` `!chuyen @User 100`\n"
    "`!diemdanh` `!bxh`\n\n"
    "💰 `!vay 1000` `!no` `!trano 1000`\n"
    "👑 `!muarole vip`\n\n"
    "👑 Admin: `!taocode` `!thuongcode` `!settien` `!resettien`"))

# ===== VI =====

@bot.command()
async def vi(ctx,m:discord.Member=None):
    m=m or ctx.author
    u=user(m.id,m.name)
    r=discord.utils.get(ctx.guild.roles,name=VIP_ROLE)
    isvip=bool(r and r in m.roles)

    await ctx.send(embed=E(
        f"💳 TÀI KHOẢN: {m.name.upper()}",
        f"🏷️ Hạng: **{'👑 VIP' if isvip else 'Người chơi Thường'}**\n"
        f"🐥 Gà Công Nghiệp\n\n"
        f"💵 **Tiền mặt**\n`{u['cash']:,}$`\n\n"
        f"🏦 **Két sắt**\n`{u['bank']:,}$`\n\n"
        f"💳 **Nợ**\n`{u['debt']:,}$`",
        0xF1C40F if isvip else BLUE
    ))

# ===== MONEY =====

@bot.command()
async def gui(ctx,n:int=None):
    u=user(ctx.author.id,ctx.author.name)
    if not n or n<=0 or u["cash"]<n:
        return await ctx.send("❌ Không đủ tiền!")
    u["cash"]-=n;u["bank"]+=n
    await ctx.send(f"🏦 Gửi `{n:,}$` thành công!")

@bot.command()
async def rut(ctx,n:int=None):
    u=user(ctx.author.id,ctx.author.name)
    if not n or n<=0 or u["bank"]<n:
        return await ctx.send("❌ Két không đủ tiền!")
    u["bank"]-=n;u["cash"]+=n
    await ctx.send(f"🏦 Rút `{n:,}$` thành công!")

@bot.command()
async def chuyen(ctx,m:discord.Member=None,n:int=None):
    if not m or not n or n<=0 or m.bot or m.id==ctx.author.id:
        return await ctx.send("❌ `!chuyen @User 100`")
    a,b=user(ctx.author.id,ctx.author.name),user(m.id,m.name)
    if a["cash"]<n:
        return await ctx.send("❌ Không đủ tiền!")
    a["cash"]-=n;b["cash"]+=n
    await ctx.send(f"💸 {ctx.author.mention} → {m.mention}: `{n:,}$`")

@bot.command()
async def diemdanh(ctx):
    u=user(ctx.author.id,ctx.author.name)
    now=time.time()
    if now-u.get("dd",0)<43200:
        return await ctx.send("⏳ Hãy quay lại sau!")
    u["dd"]=now;u["cash"]+=2593
    await ctx.send(embed=E(
        "🎁 ĐIỂM DANH",
        f"💰 **+2,593$ vào ví**\n💵 Ví: `{u['cash']:,}$`",
        GREEN))

@bot.command()
async def bxh(ctx):
    x=sorted(U.values(),
             key=lambda z:z["cash"]+z["bank"],
             reverse=True)[:5]
    s="\n".join(
        f"**{i}.** {u['name']} — `{u['cash']+u['bank']:,}$`"
        for i,u in enumerate(x,1))
    await ctx.send(embed=E("🏆 TOP 5",s))

# ===== VAY =====

@bot.command()
async def vay(ctx,n:int=None):
    u=user(ctx.author.id,ctx.author.name)

    if u["debt"]>0:
        return await ctx.send("🚫 Bạn đang có khoản nợ!")

    if not n or n<1000 or n>100000:
        return await ctx.send(
            "❌ Chỉ được vay từ **1,000$ - 100,000$**!")

    u["cash"]+=n
    u["debt"]=n
    u["due"]=time.time()+3600

    await ctx.send(embed=E(
        "💰 VAY TIỀN",
        f"🏦 Vay thành công: **{n:,}$**\n"
        f"💵 Ví: `{u['cash']:,}$`\n"
        f"⏰ Thời hạn: **1 giờ**\n\n"
        f"⚠️ Quá hạn sẽ bị khóa chơi!",
        ORANGE))

@bot.command()
async def no(ctx):
    u=user(ctx.author.id,ctx.author.name)

    if u["debt"]<=0:
        return await ctx.send("✅ Bạn không có khoản nợ.")

    left=max(0,int(u.get("due",0)-time.time()))
    h=left//3600
    m=(left%3600)//60

    await ctx.send(embed=E(
        "💳 KHOẢN NỢ",
        f"💰 Nợ: **{u['debt']:,}$**\n"
        f"⏰ Còn: **{h} giờ {m} phút**\n\n"
        f"💡 `!trano {u['debt']}`",
        RED if left==0 else ORANGE))

@bot.command()
async def trano(ctx,n:int=None):
    u=user(ctx.author.id,ctx.author.name)

    if u["debt"]<=0:
        return await ctx.send("✅ Bạn không có khoản nợ.")

    if not n or n<=0:
        return await ctx.send(f"❌ `!trano {u['debt']}`")

    n=min(n,u["debt"])

    if u["cash"]<n:
        return await ctx.send("❌ Ví không đủ tiền!")

    u["cash"]-=n
    u["debt"]-=n

    if u["debt"]==0:
        u["due"]=0
        await ctx.send(embed=E(
            "✅ TRẢ NỢ THÀNH CÔNG",
            f"💰 Đã trả: `{n:,}$`\n"
            f"💳 Nợ còn: `0$`\n"
            f"💵 Ví: `{u['cash']:,}$`\n\n"
            f"🎉 Bạn được chơi lại!",
            GREEN))
    else:
        await ctx.send(embed=E(
            "💳 TRẢ MỘT PHẦN",
            f"💰 Đã trả: `{n:,}$`\n"
            f"💳 Còn nợ: `{u['debt']:,}$`\n"
            f"💵 Ví: `{u['cash']:,}$`",
            ORANGE))

# ===== VIP =====

@bot.command()
async def muarole(ctx,role=None):
    if (role or "").lower()!="vip":
        return await ctx.send("❌ Dùng: `!muarole vip`")

    u=user(ctx.author.id,ctx.author.name)
    r=discord.utils.get(ctx.guild.roles,name=VIP_ROLE)

    if not r:
        return await ctx.send("❌ Không tìm thấy role **Vip**!")

    if r in ctx.author.roles:
        return await ctx.send("👑 Bạn đã là **VIP**!")

    if u["cash"]<VIP_PRICE:
        return await ctx.send(
            f"❌ Không đủ tiền!\n"
            f"💰 Cần: `{VIP_PRICE:,}$`\n"
            f"💵 Ví: `{u['cash']:,}$`")

    if r>=ctx.guild.me.top_role:
        return await ctx.send(
            "❌ Role **Vip** phải nằm dưới role của bot!")

    try:
        u["cash"]-=VIP_PRICE
        await ctx.author.add_roles(r)
    except discord.Forbidden:
        u["cash"]+=VIP_PRICE
        return await ctx.send(
            "❌ Bot không có quyền cấp role Vip!")

    await ctx.send(embed=E(
        "👑 NÂNG CẤP VIP",
        f"🎉 {ctx.author.mention}\n\n"
        f"⭐ **Hạng: VIP**\n"
        f"💰 Giá: `{VIP_PRICE:,}$`\n"
        f"💵 Ví còn: `{u['cash']:,}$`\n\n"
        f"✨ Tiền thắng × **1.5**\n"
        f"🍀 May mắn **+1%**",
        0xF1C40F))

# ===== TX =====

@bot.command()
async def tx(ctx,ch=None,bet:int=None):
    if await blocked(ctx):return

    if ch not in ("tai","xiu") or not bet or bet<=0:
        return await ctx.send(
            "❌ `!tx tai 1000` hoặc `!tx xiu 1000`")

    u=user(ctx.author.id,ctx.author.name)
    i=ctx.author.id

    if bet>10_000_000:
        return await ctx.send("❌ Cược tối đa `10,000,000$`!")

    if u["cash"]<bet:
        return await ctx.send("❌ Không đủ tiền!")

    if i in TX["bets"]:
        return await ctx.send("❌ Bạn đã cược ván này!")

    if not TX["on"]:
        TX.update(on=True,bets={},tai=0,xiu=0)

        TX["msg"]=await ctx.send(embed=E(
            "🎲 SÒNG TÀI XỈU 30S",
            "🔴 **TÀI** — `!tx tai số_tiền`\n"
            "🔵 **XỈU** — `!tx xiu số_tiền`\n\n"
            "⏱️ **MỞ PHIÊN — 30 GIÂY**\n"
            "💰 Tối đa: `10,000,000$`\n\n"
            "💰 Tài: `0$` | Xỉu: `0$`",
            ORANGE))

        asyncio.create_task(txround())

    u["cash"]-=bet
    TX["bets"][i]={
        "name":ctx.author.name,
        "choice":ch,
        "amount":bet
    }
    TX[ch]+=bet

    await TX["msg"].edit(embed=E(
        "🎲 SÒNG TÀI XỈU 30S",
        "🔴 **TÀI** — `!tx tai số_tiền`\n"
        "🔵 **XỈU** — `!tx xiu số_tiền`\n\n"
        "⏱️ **ĐANG NHẬN CƯỢC...**\n"
        f"💰 Tài: `{TX['tai']:,}$` | "
        f"Xỉu: `{TX['xiu']:,}$`",
        ORANGE))

    try:await ctx.message.delete()
    except:pass

async def txround():
    await asyncio.sleep(30)

    if not TX["on"]:return

    d=[random.randint(1,6) for _ in range(3)]
    total=sum(d)
    r="tai" if total>=11 else "xiu"

    win=[];lose=[]

    for i,b in TX["bets"].items():
        if b["choice"]==r:
            p=winmoney(
                type("X",(),{"guild":None,"author":None})(),
                b["amount"]
            )
            # kiểm tra VIP bằng role không thể dùng ctx ở đây,
            # nên lấy tiền thưởng theo dữ liệu VIP
            role_vip=False

            # Discord role kiểm tra ở các server bên dưới
            for g in bot.guilds:
                member=g.get_member(i)
                if member:
                    vr=discord.utils.get(
                        g.roles,name=VIP_ROLE)
                    if vr and vr in member.roles:
                        role_vip=True
                    break

            p=int(b["amount"]*2*(1.5 if role_vip else 1))
            user(i)["cash"]+=p

            win.append(
                f"• **{b['name']}** `+{p:,}$ vào ví`")
        else:
            lose.append(
                f"• **{b['name']}** `-{b['amount']:,}$`")

    await TX["msg"].edit(embed=E(
        "🎲 KẾT QUẢ TÀI XỈU",
        f"`[ {d[0]} | {d[1]} | {d[2]} ]`\n\n"
        f"💥 **{total} điểm — "
        f"{'TÀI 🔴' if r=='tai' else 'XỈU 🔵'}**\n\n"
        f"🎉 **THẮNG**\n"
        f"{chr(10).join(win) or 'Không có'}\n\n"
        f"💸 **THUA**\n"
        f"{chr(10).join(lose) or 'Không có'}",
        GREEN if win else RED))

    TX.update(
        on=False,bets={},tai=0,xiu=0,msg=None)

# ===== BC =====

@bot.command()
async def bc(ctx,ch=None,bet:int=None):
    if await blocked(ctx):return

    a={
        "ca":"🐟",
        "tom":"🦐",
        "cua":"🦀",
        "bau":"🍐",
        "ga":"🐓",
        "nai":"🦌"
    }

    if ch not in a or not bet or bet<=0:
        return await ctx.send("❌ `!bc cua 1000`")

    u=user(ctx.author.id,ctx.author.name)

    if u["cash"]<bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"]-=bet

    m=await ctx.send(embed=E(
        "🦀 BẦU CUA",
        "🟠 **LẮC... LẮC... LẮC...**\n\n"
        "`[ ❔ | ❔ | ❔ ]`",
        ORANGE))

    await asyncio.sleep(1.5)

    r=[random.choice(list(a)) for _ in range(3)]
    n=r.count(ch)

    if n:
        p=int(
            bet*(n+1)*
            (1.5 if vip(ctx) else 1)
        )
        u["cash"]+=p
        res=f"🎉 **THẮNG**\n💰 **+{p:,}$ vào ví**"
    else:
        res=f"💸 **THUA**\n🔻 **-{bet:,}$**"

    icons=" | ".join(a[x] for x in r)

    await m.edit(embed=E(
        "🦀 BẦU CUA",
        f"**KẾT QUẢ**\n\n"
        f"`[ {icons} ]`\n\n"
        f"{res}\n"
        f"💵 Ví: `{u['cash']:,}$`",
        GREEN if n else RED))

# ===== XD =====

@bot.command()
async def xd(ctx,ch=None,bet:int=None):
    if await blocked(ctx):return

    if ch not in ("chan","le") or not bet or bet<=0:
        return await ctx.send(
            "❌ `!xd chan 1000` hoặc `!xd le 1000`")

    u=user(ctx.author.id,ctx.author.name)

    if u["cash"]<bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"]-=bet

    m=await ctx.send(embed=E(
        "🪙 XÓC ĐĨA",
        "🟠 **XÓC... XÓC... XÓC...**",
        ORANGE))

    await asyncio.sleep(1.5)

    n=random.randint(0,4)
    r="chan" if n%2==0 else "le"
    win=r==ch

    if win:
        p=winmoney(ctx,bet)
        u["cash"]+=p
        res=f"🎉 **THẮNG**\n💰 **+{p:,}$ vào ví**"
    else:
        res=f"💸 **THUA**\n🔻 **-{bet:,}$**"

    balls=" | ".join(
        "🔴" if i<n else "⚪"
        for i in range(4)
    )

    await m.edit(embed=E(
        "🪙 XÓC ĐĨA",
        f"**KẾT QUẢ**\n\n"
        f"`[ {balls} ]`\n\n"
        f"🎯 **{r.upper()}**\n\n"
        f"{res}\n"
        f"💵 Ví: `{u['cash']:,}$`",
        GREEN if win else RED))

# ===== QUAY =====

@bot.command()
async def quay(ctx,bet:int=None):
    if await blocked(ctx):return

    if not bet or bet<=0:
        return await ctx.send("❌ `!quay 1000`")

    u=user(ctx.author.id,ctx.author.name)

    if u["cash"]<bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"]-=bet

    m=await ctx.send(embed=E(
        "🎰 MÁY SLOT",
        "🎰 **QUAY... QUAY... QUAY...**\n\n"
        "`[ ❔ | ❔ | ❔ ]`",
        ORANGE))

    await asyncio.sleep(1.2)

    s=[
        random.choice(
            ["🍒","🍋","🔔","⭐","💎","7️⃣"]
        )
        for _ in range(3)
    ]

    # VIP có thêm 1% cơ hội nổ hũ
    win=s[0]==s[1]==s[2]

    if not win and vip(ctx) and random.random()<0.01:
        s[1]=s[0]
        s[2]=s[0]
        win=True

    if win:
        p=winmoney(ctx,bet,5)
        u["cash"]+=p
        res=f"🎉 **NỔ HŨ!**\n💰 **+{p:,}$ vào ví**"
    else:
        res=f"💸 **THUA**\n🔻 **-{bet:,}$**"

    await m.edit(embed=E(
        "🎰 MÁY SLOT",
        f"**KẾT QUẢ**\n\n"
        f"`[ {' | '.join(s)} ]`\n\n"
        f"{res}\n"
        f"💵 Ví: `{u['cash']:,}$`",
        GREEN if win else RED))

# ===== ADMIN =====

def code():
    return "BET-"+secrets.token_hex(3).upper()

@bot.command()
async def taocode(ctx,n:int=None,uses:int=None):
    if not adm(ctx):
        return await ctx.send("⛔ Chỉ Admin!")
    if not n or not uses:
        return await ctx.send("❌ `!taocode 10000 1`")

    c=code()
    C[c]={"money":n,"uses":uses,"used":set()}

    try:
        await ctx.author.send(
            f"🔐 **CODE:** `{c}`\n"
            f"💰 `{n:,}$` | `{uses}` lượt")
        await ctx.send("✅ Code đã gửi vào DM!")
    except:
        await ctx.send(f"🔐 Code: `{c}`")

@bot.command()
async def thuongcode(ctx,n:int=None,uses:int=None):
    if not adm(ctx):
        return await ctx.send("⛔ Chỉ Admin!")
    if not n or not uses:
        return await ctx.send("❌ `!thuongcode 10000 10`")

    c=code()
    C[c]={"money":n,"uses":uses,"used":set()}

    await ctx.send(
        f"🎁 **CODE:** `{c}`\n"
        f"💰 `{n:,}$` | `{uses}` lượt")

@bot.command()
async def nhapcode(ctx,c=None):
    c=(c or "").upper()

    if c not in C:
        return await ctx.send("❌ Code không tồn tại!")

    x=C[c]
    i=ctx.author.id

    if i in x["used"]:
        return await ctx.send("❌ Bạn đã dùng code!")

    if len(x["used"])>=x["uses"]:
        return await ctx.send("❌ Code hết lượt!")

    x["used"].add(i)
    user(i,ctx.author.name)["cash"]+=x["money"]

    await ctx.send(
        f"🎁 Nhận **+{x['money']:,}$ vào ví**!")

@bot.command()
async def settien(ctx,m:discord.Member=None,n:int=None):
    if not adm(ctx):
        return await ctx.send("⛔ Chỉ Admin!")

    if not m or n is None:
        return await ctx.send(
            "❌ `!settien @User 10000`")

    user(m.id,m.name)["cash"]=max(0,n)

    await ctx.send(embed=E(
        "💰 SET TIỀN",
        f"👤 {m.mention}\n"
        f"💵 Ví mới: **{n:,}$**\n\n"
        f"✅ **Đã cập nhật số dư!**",
        GREEN))

@bot.command()
async def resettien(ctx,m:discord.Member=None):
    if not adm(ctx):
        return await ctx.send("⛔ Chỉ Admin!")

    if not m:
        return await ctx.send(
            "❌ `!resettien @User`")

    user(m.id,m.name)["cash"]=4899

    await ctx.send(embed=E(
        "🔄 RESET TÀI KHOẢN",
        f"👤 {m.mention}\n"
        f"💵 Ví → **4,899$**\n\n"
        f"✅ **Tài khoản đã được reset!**",
        ORANGE))

# ===== RUN =====

token=os.getenv("TOKEN_BOT")

if token:
    bot.run(token)
else:
    print("❌ Chưa có TOKEN_BOT!")
