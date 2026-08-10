import os,asyncio,random,secrets,time,discord
from discord.ext import commands

I=discord.Intents.default();I.message_content=True
bot=commands.Bot(command_prefix="!",intents=I,help_command=None)

U={};C={}
BLUE,ORANGE,GREEN,RED=0x3498DB,0xF1C40F,0x2ECC71,0xE74C3C
TX={"on":False,"bets":{},"tai":0,"xiu":0,"msg":None}

def E(t,d,c=BLUE):return discord.Embed(title=t,description=d,color=c)

def user(i,n="Thành viên"):
    if i not in U:
        U[i]={"name":n,"cash":4899,"bank":0,"debt":0,"vip":False}
    return U[i]

def adm(c):return c.author.guild_permissions.administrator

def vip(u):
    return u.get("vip",False)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("!trogiup | Casino"))
    print("BOT ONLINE:",bot.user)

@bot.command(name="trogiup",aliases=["help"])
async def help(ctx):
    await ctx.send(embed=E("🎰 CASINO",
    "`!tx tai 1000` `!tx xiu 1000`\n"
    "`!bc cua 1000` `!xd chan 1000` `!quay 1000`\n"
    "`!vi` `!gui 1000` `!rut 1000`\n"
    "`!chuyen @User 100`\n"
    "`!diemdanh` `!bxh`\n"
    "`!muarole Vip`\n\n"
    "👑 Admin: `!taocode` `!thuongcode` `!settien` `!resettien`"))

@bot.command()
async def vi(ctx,m:discord.Member=None):
    m=m or ctx.author;u=user(m.id,m.name)
    rank="💛 **VIP**" if vip(u) else "🐥 Người chơi Thường"
    await ctx.send(embed=E(f"💳 TÀI KHOẢN: {m.name.upper()}",
    f"🏷️ Hạng: {rank}\n\n"
    f"💵 **Tiền mặt:** `{u['cash']:,}$`\n"
    f"🏦 **Két sắt:** `{u['bank']:,}$`"))

@bot.command()
async def gui(ctx,n:int=None):
    u=user(ctx.author.id,ctx.author.name)
    if not n or n<=0 or u["cash"]<n:return await ctx.send("❌ Không đủ tiền!")
    u["cash"]-=n;u["bank"]+=n
    await ctx.send(f"🏦 Gửi `{n:,}$` thành công!")

@bot.command()
async def rut(ctx,n:int=None):
    u=user(ctx.author.id,ctx.author.name)
    if not n or n<=0 or u["bank"]<n:return await ctx.send("❌ Két không đủ!")
    u["bank"]-=n;u["cash"]+=n
    await ctx.send(f"🏦 Rút `{n:,}$` thành công!")

@bot.command()
async def chuyen(ctx,m:discord.Member=None,n:int=None):
    if not m or not n or n<=0:
        return await ctx.send("❌ `!chuyen @User 100`")
    a,b=user(ctx.author.id,ctx.author.name),user(m.id,m.name)
    if a["cash"]<n:return await ctx.send("❌ Không đủ tiền!")
    a["cash"]-=n;b["cash"]+=n
    await ctx.send(f"💸 {ctx.author.mention} → {m.mention}: `{n:,}$`")

@bot.command()
async def diemdanh(ctx):
    u=user(ctx.author.id,ctx.author.name);now=time.time()
    if now-u.get("dd",0)<43200:return await ctx.send("⏳ Hãy quay lại sau!")
    u["dd"]=now;u["cash"]+=2593
    await ctx.send(embed=E("🎁 ĐIỂM DANH","💰 **+2,593$ vào ví**",GREEN))

@bot.command()
async def bxh(ctx):
    x=sorted(U.values(),key=lambda z:z["cash"]+z["bank"],reverse=True)[:5]
    await ctx.send(embed=E("🏆 TOP 5","".join(
        f"\n**{i}.** {u['name']} — `{u['cash']+u['bank']:,}$`"
        for i,u in enumerate(x,1))))

async def blocked(ctx):
    if user(ctx.author.id,ctx.author.name)["debt"]>0:
        await ctx.send("🚫 Bạn đang có nợ!")
        return True
    return False

# ===== TÀI XỈU =====

@bot.command()
async def tx(ctx,ch=None,bet:int=None):
    if await blocked(ctx):return
    if ch not in ("tai","xiu") or not bet or bet<=0:
        return await ctx.send("❌ `!tx tai 1000` hoặc `!tx xiu 1000`")

    u=user(ctx.author.id,ctx.author.name);i=ctx.author.id

    if u["cash"]<bet:
        return await ctx.send("❌ Không đủ tiền!")

    if i in TX["bets"]:
        return await ctx.send("❌ Bạn đã cược ván này!")

    if not TX["on"]:
        TX.update(on=True,bets={},tai=0,xiu=0)

        TX["msg"]=await ctx.send(embed=E(
            "🎲 SÒNG TÀI XỈU 30S 🎲",
            "Gõ `!tx <tai/xiu> <tiền>`\n\n"
            "⏱️ **Thời gian: 30 giây**\n"
            "💰 **Tối đa: 10,000,000$/ván**\n\n"
            "💵 Tổng Tài: `0$` | Tổng Xỉu: `0$`",
            ORANGE))

        asyncio.create_task(txround())

    u["cash"]-=bet
    TX["bets"][i]={"name":ctx.author.name,"choice":ch,"amount":bet}
    TX[ch]+=bet

    await TX["msg"].edit(embed=E(
        "🎲 SÒNG TÀI XỈU 30S 🎲",
        "Gõ `!tx <tai/xiu> <tiền>`\n\n"
        "⏱️ **Đang nhận cược...**\n\n"
        f"💵 Tổng Tài: `{TX['tai']:,}$`\n"
        f"💵 Tổng Xỉu: `{TX['xiu']:,}$`",
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
        u=user(i)

        if b["choice"]==r:
            reward=b["amount"]*2
            if vip(u):reward=int(reward*1.5)

            u["cash"]+=reward
            win.append(f"• {b['name']} `+{reward:,}$`")
        else:
            lose.append(f"• {b['name']} `-{b['amount']:,}$`")

    await TX["msg"].edit(embed=E(
        "🎲 KẾT QUẢ TÀI XỈU",
        f"🎲 Xúc xắc\n`[ {d[0]} | {d[1]} | {d[2]} ]`\n\n"
        f"➡️ **{total} điểm — {r.upper()}**\n\n"
        f"🎉 **THẮNG**\n{chr(10).join(win) or 'Không có'}\n\n"
        f"💸 **THUA**\n{chr(10).join(lose) or 'Không có'}",
        GREEN if win else RED))

    TX.update(on=False,bets={},tai=0,xiu=0,msg=None)

# ===== BẦU CUA =====

@bot.command()
async def bc(ctx,ch=None,bet:int=None):
    if await blocked(ctx):return

    a={"ca":"🐟","tom":"🦐","cua":"🦀","bau":"🍐","ga":"🐓","nai":"🦌"}

    if ch not in a or not bet or bet<=0:
        return await ctx.send("❌ `!bc cua 1000`")

    u=user(ctx.author.id,ctx.author.name)

    if u["cash"]<bet:return await ctx.send("❌ Không đủ tiền!")

    u["cash"]-=bet

    m=await ctx.send(embed=E(
        "🦀 BẦU CUA CÁ TÔM",
        "🎲 **LẮC... LẮC... LẮC...**\n\n`[ ❔ | ❔ | ❔ ]`",
        ORANGE))

    await asyncio.sleep(1.5)

    r=[random.choice(list(a)) for _ in range(3)]
    n=r.count(ch)

    if n:
        reward=bet*(n+1)
        if vip(u):reward=int(reward*1.5)
        u["cash"]+=reward
        res=f"🎉 **THẮNG**\n💰 **+{reward:,}$ vào ví**"
    else:
        res=f"💸 **THUA**\n🔻 **-{bet:,}$**"

    icons=" | ".join(a[x] for x in r)

    await m.edit(embed=E(
        "🦀 BẦU CUA CÁ TÔM",
        f"**KẾT QUẢ**\n\n`[ {icons} ]`\n\n"
        f"{res}\n💵 Ví: `{u['cash']:,}$`",
        GREEN if n else RED))

# ===== XÓC ĐĨA =====

@bot.command()
async def xd(ctx,ch=None,bet:int=None):
    if await blocked(ctx):return

    if ch not in ("chan","le") or not bet or bet<=0:
        return await ctx.send("❌ `!xd chan 1000`")

    u=user(ctx.author.id,ctx.author.name)

    if u["cash"]<bet:return await ctx.send("❌ Không đủ tiền!")

    u["cash"]-=bet

    m=await ctx.send(embed=E(
        "🪙 XÓC ĐĨA",
        "🟠 **XÓC... XÓC... XÓC...**\n\n`[ ⚪ | ⚪ | ⚪ | ⚪ ]`",
        ORANGE))

    await asyncio.sleep(1.5)

    n=random.randint(0,4)
    r="chan" if n%2==0 else "le"
    win=r==ch

    if win:
        reward=bet*2
        if vip(u):reward=int(reward*1.5)
        u["cash"]+=reward

    balls=" | ".join("🔴" if i<n else "⚪" for i in range(4))

    res=(f"🎉 **THẮNG**\n💰 **+{reward:,}$ vào ví**"
         if win else f"💸 **THUA**\n🔻 **-{bet:,}$**")

    await m.edit(embed=E(
        "🪙 XÓC ĐĨA",
        f"**KẾT QUẢ**\n\n`[ {balls} ]`\n\n"
        f"🎯 **{r.upper()}**\n\n{res}\n"
        f"💵 Ví: `{u['cash']:,}$`",
        GREEN if win else RED))

# ===== SLOT =====

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

    # Có tỉ lệ jackpot, nhưng nếu 3 hình giống nhau thì LUÔN thắng
    if random.random()<0.08:
        x=random.choice(["🍒","🍋","🔔","⭐","💎","7️⃣"])
        s=[x,x,x]
    else:
        s=[random.choice(["🍒","🍋","🔔","⭐","💎","7️⃣"]) for _ in range(3)]

    win=s[0]==s[1]==s[2]

    if win:
        reward=bet*5
        if vip(u):reward=int(reward*1.5)
        u["cash"]+=reward

    if win:
        res=f"🎉 **NỔ HŨ!**\n💰 **+{reward:,}$ vào ví**"
    else:
        res=f"💸 **THUA**\n🔻 **-{bet:,}$**"

    await m.edit(embed=E(
        "🎰 MÁY SLOT",
        f"**KẾT QUẢ**\n\n`[ {' | '.join(s)} ]`\n\n"
        f"{res}\n💵 Ví: `{u['cash']:,}$`",
        GREEN if win else RED))

# ===== VIP =====

@bot.command()
async def muarole(ctx,r=None):
    if r and r.lower()!="vip":
        return await ctx.send("❌ Chỉ có `Vip`!")

    u=user(ctx.author.id,ctx.author.name)

    if u.get("vip"):
        return await ctx.send("💛 Bạn đã là VIP!")

    price=30_000_000

    if u["cash"]<price:
        return await ctx.send(
            f"❌ Không đủ tiền!\n💰 Giá VIP: `{price:,}$`")

    role=discord.utils.find(
        lambda x:x.name.lower()=="vip",ctx.guild.roles)

    if not role:
        return await ctx.send(
            "❌ Chưa có role `Vip` trong server!")

    if role >= ctx.guild.me.top_role:
        return await ctx.send(
            "❌ Hãy kéo role **Vip** xuống dưới role của Bot!")

    u["cash"]-=price
    u["vip"]=True

    try:
        await ctx.author.add_roles(role)
    except:
        return await ctx.send(
            "❌ Bot chưa có quyền **Quản lý vai trò**!")

    await ctx.send(embed=E(
        "💛 NÂNG CẤP VIP THÀNH CÔNG",
        f"👤 {ctx.author.mention}\n\n"
        f"💰 Đã trả: `{price:,}$`\n"
        "👑 Hạng: **VIP**\n"
        "💵 Tiền thắng: **x1.5**\n"
        "🍀 May mắn: **+1%**\n\n"
        "🎉 Chúc mừng bạn đã trở thành VIP!",
        0xF1C40F))

# ===== ADMIN =====

def code():
    return "BET-"+secrets.token_hex(3).upper()

@bot.command()
async def taocode(ctx,n:int=None,uses:int=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin!")

    if not n or not uses:
        return await ctx.send("❌ `!taocode 1000 1`")

    c=code()
    C[c]={"money":n,"uses":uses,"used":set()}

    await ctx.author.send(
        f"🔐 Code: `{c}` — 💰 `{n:,}$` — `{uses}` lượt")
    await ctx.send("✅ Đã gửi code vào DM.")

@bot.command()
async def thuongcode(ctx,n:int=None,uses:int=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin!")

    if not n or not uses or n<=0 or uses<=0:
        return await ctx.send("❌ `!thuongcode 1000 1`")

    c=code()
    C[c]={"money":n,"uses":uses,"used":set()}

    await ctx.send(embed=E(
        "🎁 PHẦN THƯỞNG CODE",
        f"🔐 **Mã code**\n`{c}`\n\n"
        f"💰 **Phần thưởng:** `{n:,}$`\n"
        f"👥 **Số lượt:** `{uses}`\n\n"
        "🎟️ Nhập: `!nhapcode <mã>`",
        GREEN))

@bot.command()
async def nhapcode(ctx,c=None):
    c=(c or "").upper()

    if c not in C:
        return await ctx.send("❌ Code không tồn tại!")

    x=C[c];i=ctx.author.id

    if i in x["used"] or len(x["used"])>=x["uses"]:
        return await ctx.send("❌ Code hết lượt!")

    x["used"].add(i)
    user(i,ctx.author.name)["cash"]+=x["money"]

    await ctx.send(
        f"🎁 Nhận **+{x['money']:,}$ vào ví**!")

@bot.command()
async def settien(ctx,m:discord.Member=None,n:int=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin!")

    if not m or n is None:
        return await ctx.send("❌ `!settien @User 10000`")

    user(m.id,m.name)["cash"]=max(0,n)

    await ctx.send(embed=E(
        "💰 SET TIỀN",
        f"👤 {m.mention}\n"
        f"💵 Số dư mới: **`{n:,}$`**\n\n"
        "✅ Đã cập nhật tài khoản!",
        GREEN))

@bot.command()
async def resettien(ctx,m:discord.Member=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin!")

    if not m:return

    user(m.id,m.name)["cash"]=4899

    await ctx.send(embed=E(
        "🔄 RESET TIỀN",
        f"🧹 Đã reset tài khoản!\n\n"
        f"👤 {m.mention}\n"
        "💵 Ví: **`4,899$`**",
        ORANGE))

token=os.getenv("TOKEN_BOT")

if token:
    bot.run(token)
else:
    print("❌ Chưa có TOKEN_BOT!")
