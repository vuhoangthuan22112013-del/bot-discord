import os, asyncio, random, time, secrets, discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

users, codes, cooldowns, last_dd = {}, {}, {}, {}
DEFAULT, MAXBET = 4899, 10_000_000
BLUE, ORANGE, GREEN, RED = 0x3498DB, 0xF1C40F, 0x2ECC71, 0xE74C3C

tx = {"on":False,"bets":{},"tai":0,"xiu":0,"msg":None}

def E(title, text, color):
    return discord.Embed(title=title, description=text, color=color)

def U(uid, name="Thành viên"):
    if uid not in users:
        users[uid]={"name":name,"cash":DEFAULT,"bank":0}
    return users[uid]

def cd(uid, name, sec=1):
    k=f"{uid}{name}"; now=time.time()
    if now-cooldowns.get(k,0)<sec:return True
    cooldowns[k]=now
    return False

def adm(ctx):
    return ctx.author.guild_permissions.administrator

def checkbet(bet):
    return bet and 0 < bet <= MAXBET

# ================= ONLINE =================

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | CASINO BET88")
    )
    print(f"✅ ONLINE: {bot.user}")

# ================= HELP =================

@bot.command(name="trogiup", aliases=["help"])
async def help(ctx):
    await ctx.send(embed=E(
        "🎰 CASINO BET88",
        "**🎲 CASINO**\n"
        "`!tx tai 1000` `!tx xiu 1000`\n"
        "`!bc cua 500` `!quay 1000` `!xd chan 1000`\n\n"
        "**💰 HỆ THỐNG**\n"
        "`!vi` `!gui 1000` `!rut 1000`\n"
        "`!chuyen @User 1000` `!diemdanh` `!bxh`\n"
        "`!nhapcode CODE`\n\n"
        "**👑 ADMIN**\n"
        "`!taocode 10000 1`\n"
        "`!thuongcode 10000 10`\n"
        "`!settien @User 10000`\n"
        "`!resettien @User`",
        BLUE
    ))

# ================= VÍ =================

@bot.command(name="vi", aliases=["bal","money"])
async def vi(ctx, member:discord.Member=None):
    m=member or ctx.author
    u=U(m.id,m.name)
    await ctx.send(embed=E(
        "💳 THÔNG TIN TÀI KHOẢN",
        f"👤 **{m.name}**\n\n"
        f"💵 Tiền mặt: `{u['cash']:,}$`\n"
        f"🏦 Ngân hàng: `{u['bank']:,}$`\n"
        f"💰 Tổng: `{u['cash']+u['bank']:,}$`",
        BLUE))

# ================= ĐIỂM DANH =================

@bot.command()
async def diemdanh(ctx):
    uid=ctx.author.id
    if time.time()-last_dd.get(uid,0)<43200:
        return await ctx.send("⚠️ Bạn đã điểm danh rồi!")
    last_dd[uid]=time.time()
    u=U(uid,ctx.author.name)
    u["cash"]+=2593
    await ctx.send(embed=E(
        "🎁 ĐIỂM DANH",
        f"💰 Nhận **+2,593$**\n💵 Ví: `{u['cash']:,}$`",
        GREEN))

# ================= BANK =================

@bot.command()
async def gui(ctx, amount:int=None):
    if not amount or amount<=0:
        return await ctx.send("❌ `!gui số_tiền`")
    u=U(ctx.author.id,ctx.author.name)
    if u["cash"]<amount:return await ctx.send("❌ Không đủ tiền!")
    u["cash"]-=amount;u["bank"]+=amount
    await ctx.send(embed=E("🏦 GỬI TIỀN",
        f"💰 Gửi: `{amount:,}$`\n🏦 Bank: `{u['bank']:,}$`",BLUE))

@bot.command()
async def rut(ctx, amount:int=None):
    if not amount or amount<=0:
        return await ctx.send("❌ `!rut số_tiền`")
    u=U(ctx.author.id,ctx.author.name)
    if u["bank"]<amount:return await ctx.send("❌ Bank không đủ!")
    u["bank"]-=amount;u["cash"]+=amount
    await ctx.send(embed=E("🏦 RÚT TIỀN",
        f"💰 Rút: `{amount:,}$`\n💵 Ví: `{u['cash']:,}$`",BLUE))

@bot.command()
async def chuyen(ctx, member:discord.Member=None, amount:int=None):
    if not member or not amount or amount<=0:
        return await ctx.send("❌ `!chuyen @User số_tiền`")
    if member.id==ctx.author.id or member.bot:
        return await ctx.send("❌ Không thể chuyển!")
    a,b=U(ctx.author.id,ctx.author.name),U(member.id,member.name)
    if a["cash"]<amount:return await ctx.send("❌ Không đủ tiền!")
    a["cash"]-=amount;b["cash"]+=amount
    await ctx.send(embed=E("💸 CHUYỂN TIỀN",
        f"{ctx.author.mention} ➜ {member.mention}\n💰 `{amount:,}$`",BLUE))

# ================= BXH =================

@bot.command()
async def bxh(ctx):
    top=sorted(users.values(),key=lambda x:x["cash"]+x["bank"],reverse=True)[:5]
    medals=["🥇","🥈","🥉","4️⃣","5️⃣"]
    text="\n".join(
        f"{medals[i]} **{u['name']}** — `{u['cash']+u['bank']:,}$`"
        for i,u in enumerate(top))
    await ctx.send(embed=E("🏆 TOP 5 GIÀU NHẤT",text or "Chưa có người chơi.",BLUE))

# ================= SLOT =================

@bot.command()
async def quay(ctx, bet:int=None):
    if cd(ctx.author.id,"quay",1.5):return
    if not checkbet(bet):
        return await ctx.send("❌ `!quay 1000` | Max `10,000,000$`")
    u=U(ctx.author.id,ctx.author.name)
    if u["cash"]<bet:return await ctx.send("❌ Không đủ tiền!")

    u["cash"]-=bet
    icons=["💎","🍒","🍋","🔔","⭐","7️⃣"]
    r=[random.choice(icons) for _ in range(3)]

    msg=await ctx.send(embed=E(
        "🎰 MÁY SLOT BET88",
        "🎰\n\n"
        "`[ ❔ ]   [ ❔ ]   [ ❔ ]`\n\n"
        "⏳ **Đang quay...**",
        ORANGE))

    await asyncio.sleep(.7)
    await msg.edit(embed=E(
        "🎰 MÁY SLOT BET88",
        "🎰\n\n"
        f"`[ {random.choice(icons)} ]   [ ❔ ]   [ ❔ ]`\n\n"
        "⏳ **Đang quay...**",
        ORANGE))

    await asyncio.sleep(.7)
    await msg.edit(embed=E(
        "🎰 MÁY SLOT BET88",
        "🎰\n\n"
        f"`[ {r[0]} ]   [ {r[1]} ]   [ ❔ ]`\n\n"
        "⏳ **Đang quay...**",
        ORANGE))

    await asyncio.sleep(.8)

    win=r[0]==r[1]==r[2]
    if win:
        gain=bet*5
        u["cash"]+=gain
        notice=f"🎉 **NỔ HŨ! +{gain:,}$**"
        color=GREEN
    else:
        notice=f"💸 **TRẬT HŨ! -{bet:,}$**"
        color=RED

    await msg.edit(embed=E(
        "🎰 MÁY SLOT BET88",
        "🎰\n\n"
        "**KẾT QUẢ**\n"
        f"`[ {r[0]} ]   [ {r[1]} ]   [ {r[2]} ]`\n\n"
        "**Thông báo**\n"
        f"💰 {notice}",
        color))

# ================= BẦU CUA =================

@bot.command()
async def bc(ctx, choice:str=None, bet:int=None):
    faces={
        "ca":"🐟","tom":"🦐","cua":"🦀",
        "bau":"🥒","ga":"🐓","nai":"🦌"
    }

    if choice not in faces or not checkbet(bet):
        return await ctx.send(
            "❌ `!bc ca 100` / `!bc tom 100` / `!bc cua 100`\n"
            "Max `10,000,000$`")

    u=U(ctx.author.id,ctx.author.name)
    if u["cash"]<bet:return await ctx.send("❌ Không đủ tiền!")
    u["cash"]-=bet

    msg=await ctx.send(embed=E(
        "🦀 BẦU CUA CÁ TÔM",
        "🦀\n\n"
        "**KẾT QUẢ**\n"
        "`[ ❔ ]   [ ❔ ]   [ ❔ ]`\n\n"
        "🎲 **Lắc... Lắc... Lắc...**",
        ORANGE))

    await asyncio.sleep(.7)
    await msg.edit(embed=E(
        "🦀 BẦU CUA CÁ TÔM",
        "🦀\n\n"
        "**KẾT QUẢ**\n"
        f"`[ {random.choice(list(faces.values()))} ]   [ ❔ ]   [ ❔ ]`\n\n"
        "🎲 **Lắc... Lắc... Lắc...**",
        ORANGE))

    await asyncio.sleep(.7)
    await msg.edit(embed=E(
        "🦀 BẦU CUA CÁ TÔM",
        "🦀\n\n"
        "**KẾT QUẢ**\n"
        f"`[ {random.choice(list(faces.values()))} ]   [ {random.choice(list(faces.values()))} ]   [ ❔ ]`\n\n"
        "🎲 **Lắc... Lắc... Lắc...**",
        ORANGE))

    await asyncio.sleep(.8)

    r=[random.choice(list(faces)) for _ in range(3)]
    n=r.count(choice)

    if n:
        gain=bet*(n+1)
        u["cash"]+=gain
        notice=f"🎉 **TRÚNG {n} CON! +{bet*n:,}$**"
        color=GREEN
    else:
        notice=f"💸 **TRẬT LẤT! -{bet:,}$**"
        color=RED

    await msg.edit(embed=E(
        "🦀 BẦU CUA CÁ TÔM",
        "🦀\n\n"
        "**KẾT QUẢ**\n"
        f"`[ {faces[r[0]]} ]   [ {faces[r[1]]} ]   [ {faces[r[2]]} ]`\n\n"
        "**Tổng kết**\n"
        f"💰 {notice}",
        color))

# ================= XÓC ĐĨA =================

@bot.command()
async def xd(ctx, choice:str=None, bet:int=None):
    choice=(choice or "").lower()

    if choice not in ("chan","le") or not checkbet(bet):
        return await ctx.send(
            "❌ `!xd chan 1000` hoặc `!xd le 1000`\n"
            "Max `10,000,000$`")

    u=U(ctx.author.id,ctx.author.name)
    if u["cash"]<bet:return await ctx.send("❌ Không đủ tiền!")
    u["cash"]-=bet

    msg=await ctx.send(embed=E(
        "🪙 XÓC ĐĨA BET88",
        "🪙\n\n"
        "**KẾT QUẢ**\n"
        "`[ ⚪ ] [ ⚪ ] [ ⚪ ] [ ⚪ ]`\n\n"
        "🥣 **Xóc... Xóc... Xóc...**",
        ORANGE))

    await asyncio.sleep(1)
    n=random.randint(0,4)
    balls="🔴"*n+"⚪"*(4-n)
    result="CHẴN" if n%2==0 else "LẺ"
    win=(result.lower()==("chẵn" if choice=="chan" else "lẻ"))

    if win:
        u["cash"]+=bet*2
        notice=f"🎉 **THẮNG +{bet:,}$**"
        color=GREEN
    else:
        notice=f"💸 **THUA -{bet:,}$**"
        color=RED

    await msg.edit(embed=E(
        "🪙 XÓC ĐĨA BET88",
        "🪙\n\n"
        "**KẾT QUẢ**\n"
        f"`[ {balls} ]`\n\n"
        f"💥 **{result}**\n\n"
        "**Thông báo**\n"
        f"💰 {notice}",
        color))

# ================= TÀI XỈU =================

@bot.command()
async def tx(ctx, choice:str=None, bet:int=None):

    if not choice:
        if not tx["on"]:
            return await ctx.send(
                "❌ Dùng: `!tx tai 1000` hoặc `!tx xiu 1000`")
        return await ctx.send(embed=E(
            "🎲 SÒNG TÀI XỈU 10S 🎲",
            "Gõ `!tx <tai/xiu> <tiền>`\n"
            "**💰 Cược tối đa: 10,000,000$/ván**\n\n"
            f"⏱️ **Thời gian: 10 giây**\n\n"
            f"🔴 Tổng Tài: `{tx['tai']:,}$`\n"
            f"🔵 Tổng Xỉu: `{tx['xiu']:,}$`",
            ORANGE))

    choice=choice.lower()

    if choice not in ("tai","xiu") or not checkbet(bet):
        return await ctx.send(
            "❌ `!tx tai 1000` hoặc `!tx xiu 1000`\n"
            "💰 Cược tối đa: `10,000,000$/ván`")

    uid=ctx.author.id
    u=U(uid,ctx.author.name)

    if uid in tx["bets"]:
        return await ctx.send("❌ Bạn đã cược ván này rồi!")

    if u["cash"]<bet:
        return await ctx.send("❌ Không đủ tiền!")

    if not tx["on"]:
        tx.update(on=True,bets={},tai=0,xiu=0)

        tx["msg"]=await ctx.send(embed=E(
            "🎲 SÒNG TÀI XỈU 10S 🎲",
            "Gõ `!tx <tai/xiu> <tiền>`\n"
            "**💰 Cược tối đa: 10,000,000$/ván**\n\n"
            "⏱️ **Thời gian: 10 giây**\n\n"
            "🔴 Tổng Tài: `0$`\n"
            "🔵 Tổng Xỉu: `0$`",
            ORANGE))

        asyncio.create_task(tx_round())

    u["cash"]-=bet
    tx["bets"][uid]={
        "name":ctx.author.name,
        "choice":choice,
        "amount":bet
    }
    tx[choice]+=bet

    await tx["msg"].edit(embed=E(
        "🎲 SÒNG TÀI XỈU 10S 🎲",
        "Gõ `!tx <tai/xiu> <tiền>`\n"
        "**💰 Cược tối đa: 10,000,000$/ván**\n\n"
        "⏱️ **Thời gian: 10 giây**\n\n"
        f"🔴 Tổng Tài: `{tx['tai']:,}$`\n"
        f"🔵 Tổng Xỉu: `{tx['xiu']:,}$`",
        ORANGE))

    try: await ctx.message.delete()
    except: pass

async def tx_round():
    await asyncio.sleep(10)

    if not tx["on"]:return

    msg=tx["msg"]
    tx["on"]=False

    await msg.edit(embed=E(
        "🎲 KẾT QUẢ TÀI XỈU",
        "🎲\n\n"
        "⏳ **Đang xóc bát...**\n\n"
        "`[ ❔ ] [ ❔ ] [ ❔ ]`",
        ORANGE))

    await asyncio.sleep(2)

    d=[random.randint(1,6) for _ in range(3)]
    total=sum(d)
    result="tai" if total>=11 else "xiu"

    win=[];lose=[]

    for uid,b in tx["bets"].items():
        if b["choice"]==result:
            U(uid)["cash"]+=b["amount"]*2
            win.append(f"• {b['name']} `+{b['amount']:,}$`")
        else:
            lose.append(f"• {b['name']} `-{b['amount']:,}$`")

    label="TÀI 🔴" if result=="tai" else "XỈU 🔵"

    await msg.edit(embed=E(
        "🎲 KẾT QUẢ TÀI XỈU",
        "🎲\n\n"
        "**Xúc xắc**\n"
        f"`[ {d[0]} ] [ {d[1]} ] [ {d[2]} ]`\n"
        f"→ **{total} điểm — {label}**\n\n"
        "🎉 **THẮNG**\n"
        + ("\n".join(win) if win else "Không có")+
        "\n\n💸 **THUA**\n"+
        ("\n".join(lose) if lose else "Không có"),
        GREEN if win else RED))

    tx.update(on=False,bets={},tai=0,xiu=0,msg=None)

# ================= CODE =================

def newcode():
    return "BET-"+secrets.token_hex(3).upper()

@bot.command()
async def taocode(ctx,amount:int=None,uses:int=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin!")
    if not amount or not uses or amount<=0 or uses<=0:
        return await ctx.send("❌ `!taocode 10000 1`")
    code=newcode()
    codes[code]={"money":amount,"uses":uses,"used":set()}
    try:
        await ctx.author.send(f"🔐 CODE: `{code}` | 💰 `{amount:,}$` | 👥 `{uses}` lượt")
        await ctx.send("✅ Đã gửi code vào DM Admin.")
    except:
        await ctx.send(f"🔐 Code: `{code}`")

@bot.command()
async def thuongcode(ctx,amount:int=None,uses:int=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin!")
    if not amount or not uses:return await ctx.send("❌ `!thuongcode 10000 10`")
    code=newcode()
    codes[code]={"money":amount,"uses":uses,"used":set()}
    await ctx.send(embed=E(
        "🎁 CODE THƯỞNG",
        f"🎟️ `{code}`\n💰 `{amount:,}$`\n👥 `{uses}` lượt\n\n"
        f"`!nhapcode {code}`",GREEN))

@bot.command()
async def nhapcode(ctx,code:str=None):
    if not code:return await ctx.send("❌ `!nhapcode CODE`")
    code=code.upper()
    if code not in codes:return await ctx.send("❌ Code không tồn tại!")
    c=codes[code];uid=ctx.author.id
    if uid in c["used"]:return await ctx.send("❌ Bạn đã dùng code!")
    if len(c["used"])>=c["uses"]:return await ctx.send("❌ Code hết lượt!")
    c["used"].add(uid)
    U(uid,ctx.author.name)["cash"]+=c["money"]
    await ctx.send(embed=E(
        "🎁 NHẬP CODE THÀNH CÔNG",
        f"🎟️ `{code}`\n💰 **+{c['money']:,}$**",GREEN))

# ================= ADMIN =================

@bot.command()
async def settien(ctx,member:discord.Member=None,amount:int=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin!")
    if not member or amount is None or amount<0:
        return await ctx.send("❌ `!settien @User 10000`")
    U(member.id,member.name)["cash"]=amount
    await ctx.send(f"✅ {member.mention} → `{amount:,}$`")

@bot.command()
async def resettien(ctx,member:discord.Member=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin!")
    if not member:return await ctx.send("❌ `!resettien @User`")
    U(member.id,member.name)["cash"]=DEFAULT
    await ctx.send(f"🔄 {member.mention} → `{DEFAULT:,}$`")

# ================= RUN =================

TOKEN=os.getenv("TOKEN_BOT")

if not TOKEN:
    print("❌ Chưa có TOKEN_BOT!")
else:
    bot.run(TOKEN)
