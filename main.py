import os, asyncio, random, time, secrets, discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

users, codes, cooldowns, last_dd = {}, {}, {}, {}
DEFAULT = 4899
BLUE, ORANGE, GREEN, RED = 0x3498DB, 0xF1C40F, 0x2ECC71, 0xE74C3C

tx = {"active":False,"bets":{},"tai":0,"xiu":0,"msg":None}

def emb(t,d,c):
    return discord.Embed(title=t,description=d,color=c)

def user(uid,name="Thành viên"):
    if uid not in users:
        users[uid]={"name":name,"cash":DEFAULT,"bank":0,
                    "hang":"Người chơi Thường","ga":"Gà Công Nghiệp 🐥"}
    return users[uid]

def cd(uid,cmd,sec=1.5):
    k=f"{uid}_{cmd}"; now=time.time()
    if k in cooldowns and now-cooldowns[k]<sec:
        return round(sec-(now-cooldowns[k]),1)
    cooldowns[k]=now

def admin(ctx):
    return ctx.author.guild_permissions.administrator

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino Bet88")
    )
    print(f"✅ BOT ONLINE: {bot.user}")

# ================= TRỢ GIÚP =================

@bot.command(name="trogiup",aliases=["help"])
async def trogiup(ctx):
    if cd(ctx.author.id,"help"): return
    await ctx.send(embed=emb(
        "🎰 CASINO BET88",
        "**⚔️ PVP**\n"
        "`!danhbai` `!thachdau` `!dagapvp` `!tuxipvp @User`\n\n"
        "**🎲 CASINO**\n"
        "`!tx tai 100` `!bc ca 100` `!xd chan 100` `!quay 100`\n\n"
        "**🏛️ HỆ THỐNG**\n"
        "`!vi` `!gui` `!rut` `!chuyen @User 100`\n"
        "`!diemdanh` `!bxh` `!nhapcode CODE`\n\n"
        "**👑 ADMIN**\n"
        "`!taocode 10000 1`\n"
        "`!thuongcode 10000 10`\n"
        "`!settien @User 10000`\n"
        "`!resettien @User`",
        BLUE))

# ================= VÍ =================

@bot.command(name="vi",aliases=["money","bal"])
async def vi(ctx,member:discord.Member=None):
    t=member or ctx.author
    u=user(t.id,t.name)
    await ctx.send(embed=emb(
        "💳 THÔNG TIN TÀI KHOẢN",
        f"👤 **{t.name.upper()}**\n"
        f"🏷️ Hạng: {u['hang']}\n🐓 Gà: {u['ga']}\n\n"
        f"💵 Tiền mặt: `{u['cash']:,}$`\n"
        f"🏦 Ngân hàng: `{u['bank']:,}$`",
        BLUE))

# ================= ĐIỂM DANH =================

@bot.command(name="diemdanh")
async def diemdanh(ctx):
    uid=ctx.author.id; now=time.time()
    if uid in last_dd and now-last_dd[uid]<43200:
        return await ctx.send("⚠️ Bạn đã điểm danh rồi!")
    last_dd[uid]=now
    u=user(uid,ctx.author.name)
    u["cash"]+=2593
    await ctx.send(embed=emb(
        "🎁 ĐIỂM DANH",
        f"💰 Nhận **+2,593$**\n💵 Ví: `{u['cash']:,}$`",
        GREEN))

# ================= BANK =================

@bot.command(name="gui")
async def gui(ctx,amount:int=None):
    if not amount or amount<=0:return await ctx.send("❌ `!gui số_tiền`")
    u=user(ctx.author.id,ctx.author.name)
    if u["cash"]<amount:return await ctx.send("❌ Không đủ tiền!")
    u["cash"]-=amount;u["bank"]+=amount
    await ctx.send(embed=emb(
        "🏦 GỬI TIỀN",
        f"💰 Gửi: `{amount:,}$`\n🏦 Bank: `{u['bank']:,}$`\n📈 Lãi: **2%/ngày**",
        BLUE))

@bot.command(name="rut")
async def rut(ctx,amount:int=None):
    if not amount or amount<=0:return await ctx.send("❌ `!rut số_tiền`")
    u=user(ctx.author.id,ctx.author.name)
    if u["bank"]<amount:return await ctx.send("❌ Bank không đủ!")
    u["bank"]-=amount;u["cash"]+=amount
    await ctx.send(embed=emb(
        "🏦 RÚT TIỀN",
        f"💰 Rút: `{amount:,}$`\n💵 Ví: `{u['cash']:,}$`",
        BLUE))

@bot.command(name="chuyen")
async def chuyen(ctx,member:discord.Member=None,amount:int=None):
    if not member or not amount or amount<=0:
        return await ctx.send("❌ `!chuyen @User số_tiền`")
    if member.id==ctx.author.id or member.bot:
        return await ctx.send("❌ Không thể chuyển!")
    a=user(ctx.author.id,ctx.author.name)
    b=user(member.id,member.name)
    if a["cash"]<amount:return await ctx.send("❌ Không đủ tiền!")
    a["cash"]-=amount;b["cash"]+=amount
    await ctx.send(embed=emb(
        "💸 CHUYỂN TIỀN",
        f"👤 {ctx.author.mention} → {member.mention}\n💰 `{amount:,}$`",
        BLUE))

# ================= BXH =================

@bot.command(name="bxh")
async def bxh(ctx):
    top=sorted(users.values(),
               key=lambda x:x["cash"]+x["bank"],reverse=True)[:5]
    medals=["🥇","🥈","🥉","4️⃣","5️⃣"]
    text="\n".join(
        f"{medals[i]} **{u['name']}** — `{u['cash']+u['bank']:,}$`"
        for i,u in enumerate(top))
    await ctx.send(embed=emb("🏆 TOP 5 GIÀU NHẤT",
                              text or "Chưa có người chơi.",BLUE))

# ================= CODE =================

def newcode():
    return "BET-"+secrets.token_hex(3).upper()

def makecode(ctx,amount,uses):
    if not admin(ctx):return None
    if amount<=0 or uses<=0:return None
    code=newcode()
    codes[code]={"money":amount,"uses":uses,"used":set()}
    return code

@bot.command(name="taocode")
async def taocode(ctx,amount:int=None,uses:int=None):
    if amount is None or uses is None:
        return await ctx.send("❌ `!taocode số_tiền số_lượt`")
    code=makecode(ctx,amount,uses)
    if not code:return await ctx.send("⛔ Không có quyền hoặc số liệu sai!")
    try:
        await ctx.author.send(embed=emb(
            "🔐 CODE RIÊNG CỦA ADMIN",
            f"🎟️ Code: `{code}`\n💰 Tiền: `{amount:,}$`\n🔢 Lượt: `{uses}`",
            BLUE))
        await ctx.send("✅ Đã gửi code riêng vào DM của bạn.")
    except:
        await ctx.send("❌ Không thể gửi DM cho bạn.")

@bot.command(name="thuongcode")
async def thuongcode(ctx,amount:int=None,uses:int=None):
    if amount is None or uses is None:
        return await ctx.send("❌ `!thuongcode số_tiền số_lượt`")
    code=makecode(ctx,amount,uses)
    if not code:return await ctx.send("⛔ Không có quyền hoặc số liệu sai!")
    await ctx.send(embed=emb(
        "🎁 CODE THƯỞNG",
        f"🎟️ **CODE:** `{code}`\n"
        f"💰 **Thưởng:** `{amount:,}$`\n"
        f"👥 **Lượt:** `{uses}`\n\n"
        f"Nhập: `!nhapcode {code}`",
        GREEN))

@bot.command(name="nhapcode")
async def nhapcode(ctx,code:str=None):
    if not code:return await ctx.send("❌ `!nhapcode CODE`")
    code=code.upper()
    if code not in codes:return await ctx.send("❌ Code không tồn tại!")
    c=codes[code];uid=ctx.author.id
    if uid in c["used"]:return await ctx.send("❌ Bạn đã dùng code này!")
    if len(c["used"])>=c["uses"]:return await ctx.send("❌ Code hết lượt!")
    c["used"].add(uid)
    user(uid,ctx.author.name)["cash"]+=c["money"]
    await ctx.send(embed=emb(
        "🎁 NHẬP CODE THÀNH CÔNG",
        f"🎟️ `{code}`\n💰 Nhận **+{c['money']:,}$**",
        GREEN))

# ================= ADMIN =================

@bot.command(name="settien")
async def settien(ctx,member:discord.Member=None,amount:int=None):
    if not admin(ctx):return await ctx.send("⛔ Chỉ Admin!")
    if not member or amount is None or amount<0:
        return await ctx.send("❌ `!settien @User số_tiền`")
    user(member.id,member.name)["cash"]=amount
    await ctx.send(f"✅ {member.mention} → `{amount:,}$`")

@bot.command(name="resettien",aliases=["reset"])
async def resettien(ctx,member:discord.Member=None):
    if not admin(ctx):return await ctx.send("⛔ Chỉ Admin!")
    if not member:return await ctx.send("❌ `!resettien @User`")
    user(member.id,member.name)["cash"]=DEFAULT
    await ctx.send(f"🔄 {member.mention} → `{DEFAULT:,}$`")

# ================= SLOT =================

@bot.command(name="quay")
async def quay(ctx,bet:int=None):
    if cd(ctx.author.id,"quay"):return
    if not bet or bet<=0:return await ctx.send("❌ `!quay 100`")
    u=user(ctx.author.id,ctx.author.name)
    if u["cash"]<bet:return await ctx.send("❌ Không đủ tiền!")
    u["cash"]-=bet
    s=[random.choice(["🍋","🔔","🍒","⭐","💎"]) for _ in range(3)]
    msg=await ctx.send(embed=emb(
        "🎰 MÁY SLOT",
        "🟠 **ĐANG QUAY...**\n\n`[ ❔ ] [ ❔ ] [ ❔ ]`",
        ORANGE))
    await asyncio.sleep(1)
    win=s[0]==s[1]==s[2]
    if win:
        gain=bet*5
        u["cash"]+=gain
        text=f"`[ {s[0]} ] [ {s[1]} ] [ {s[2]} ]`\n\n🎉 **THẮNG +{gain:,}$**"
    else:
        text=f"`[ {s[0]} ] [ {s[1]} ] [ {s[2]} ]`\n\n💸 **THUA -{bet:,}$**"
    await msg.edit(embed=emb("🎰 MÁY SLOT",text,GREEN if win else RED))

# ================= TÀI XỈU =================

def tx_board():
    return (
        "🟠 **ĐANG NHẬN CƯỢC**\n\n"
        f"🔴 **TÀI:** `{tx['tai']:,}$`\n"
        f"🔵 **XỈU:** `{tx['xiu']:,}$`\n"
        f"👥 Người chơi: **{len(tx['bets'])}**\n\n"
        "🎯 `!tx tai số_tiền`\n"
        "🎯 `!tx xiu số_tiền`\n\n"
        "⚠️ Mỗi người chỉ được cược **1 lần/ván**."
    )

@bot.command(name="tx")
async def taixiu(ctx,choice:str=None,bet:int=None):

    # !tx = xem bảng
    if not choice:
        if not tx["active"]:
            return await ctx.send(
                "❌ Chưa có phiên!\nDùng `!tx tai 100` để mở."
            )
        return await ctx.send(
            embed=emb("🎲 SÒNG TÀI XỈU 30S",
                      tx_board(),ORANGE))

    choice=choice.lower()

    if choice not in ("tai","xiu") or not bet or bet<=0:
        return await ctx.send(
            "❌ Dùng `!tx tai 100` hoặc `!tx xiu 100`"
        )

    uid=ctx.author.id
    u=user(uid,ctx.author.name)

    # Tự mở phiên
    if not tx["active"]:
        tx.update(active=True,bets={},tai=0,xiu=0)

        tx["msg"]=await ctx.send(
            embed=emb(
                "🎲 SÒNG TÀI XỈU 30S",
                tx_board(),
                ORANGE
            )
        )

        asyncio.create_task(tx_round())

    # Chỉ 1 cược
    if uid in tx["bets"]:
        try: await ctx.message.delete()
        except: pass
        return await ctx.send(
            f"❌ {ctx.author.mention} bạn đã cược rồi!",
            delete_after=3
        )

    if u["cash"]<bet:
        try: await ctx.message.delete()
        except: pass
        return await ctx.send(
            f"❌ {ctx.author.mention} Không đủ tiền!",
            delete_after=3
        )

    # Trừ tiền
    u["cash"]-=bet

    tx["bets"][uid]={
        "name":ctx.author.name,
        "choice":choice,
        "amount":bet
    }

    tx[choice]+=bet

    # Xóa tin nhắn lệnh
    try:
        await ctx.message.delete()
    except:
        pass

    # Cập nhật bảng
    if tx["msg"]:
        try:
            await tx["msg"].edit(
                embed=emb(
                    "🎲 SÒNG TÀI XỈU 30S",
                    tx_board(),
                    ORANGE
                )
            )
        except:
            pass

async def tx_round():

    await asyncio.sleep(30)

    if not tx["active"]:
        return

    tx["active"]=False
    msg=tx["msg"]

    if msg:
        await msg.edit(
            embed=emb(
                "🎲 NHÀ CÁI ĐANG XÓC BÁT...",
                "🟠 **Đang xóc...**\n\n"
                "`[ ❔ ] [ ❔ ] [ ❔ ]`",
                ORANGE
            )
        )

    await asyncio.sleep(2)

    d=[random.randint(1,6) for _ in range(3)]
    total=sum(d)
    result="tai" if total>=11 else "xiu"

    win=[]
    lose=[]

    for uid,b in tx["bets"].items():

        if b["choice"]==result:

            user(uid)["cash"]+=b["amount"]*2

            win.append(
                f"• **{b['name']}** `+{b['amount']:,}$`"
            )

        else:

            lose.append(
                f"• **{b['name']}** `-{b['amount']:,}$`"
            )

    text=(
        f"`[ {d[0]} ] [ {d[1]} ] [ {d[2]} ]`\n"
        f"→ **{total} điểm — "
        f"{'TÀI 🔴' if result=='tai' else 'XỈU 🔵'}**\n\n"

        "🟢 **THẮNG**\n"
        f"{chr(10).join(win) if win else 'Không có'}\n\n"

        "🔴 **THUA**\n"
        f"{chr(10).join(lose) if lose else 'Không có'}"
    )

    if msg:
        await msg.edit(
            embed=emb(
                "🎲 KẾT QUẢ TÀI XỈU",
                text,
                GREEN if win else RED
            )
        )

    tx.update(
        active=False,
        bets={},
        tai=0,
        xiu=0,
        msg=None
    )

# ================= XÓC ĐĨA =================

@bot.command(name="xd")
async def xd(ctx,choice:str=None,bet:int=None):

    if not choice or choice.lower() not in ("chan","le") or not bet or bet<=0:
        return await ctx.send("❌ `!xd chan 100` hoặc `!xd le 100`")

    u=user(ctx.author.id,ctx.author.name)

    if u["cash"]<bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"]-=bet

    msg=await ctx.send(
        embed=emb(
            "🪙 XÓC ĐĨA",
            "🟠 **ĐANG XÓC ĐĨA...**",
            ORANGE
        )
    )

    await asyncio.sleep(1.5)

    n=random.randint(0,4)
    even=n%2==0
    win=(choice.lower()=="chan")==even

    if win:
        u["cash"]+=bet*2

    await msg.edit(
        embed=emb(
            "🪙 XÓC ĐĨA",
            f"`{'🔴'*n+'⚪'*(4-n)}` → "
            f"**{'CHẴN' if even else 'LẺ'}**\n\n"
            + (
                f"🎉 **THẮNG +{bet:,}$**"
                if win else
                f"💸 **THUA -{bet:,}$**"
            ),
            GREEN if win else RED
        )
    )

# ================= BẦU CUA =================

@bot.command(name="bc")
async def bc(ctx,choice:str=None,bet:int=None):

    a={
        "ca":"🐟",
        "tom":"🦐",
        "cua":"🦀",
        "bau":"🥒",
        "ga":"🐓",
        "nai":"🦌"
    }

    if choice not in a or not bet or bet<=0:
        return await ctx.send("❌ `!bc ca 100`")

    u=user(ctx.author.id,ctx.author.name)

    if u["cash"]<bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"]-=bet

    msg=await ctx.send(
        embed=emb(
            "🎲 BẦU CUA",
            "🟠 **ĐANG LẮC HỘT...**",
            ORANGE
        )
    )

    await asyncio.sleep(1.5)

    r=[random.choice(list(a)) for _ in range(3)]
    n=r.count(choice)

    if n:
        u["cash"]+=bet*(n+1)

    text=(
        f"`[ {a[r[0]]} ] [ {a[r[1]]} ] [ {a[r[2]]} ]`\n\n"
        + (
            f"🎉 **TRÚNG {n} CON! +{bet*n:,}$**"
            if n else
            f"💸 **THUA -{bet:,}$**"
        )
    )

    await msg.edit(
        embed=emb(
            "🎲 BẦU CUA",
            text,
            GREEN if n else RED
        )
    )

# ================= RUN =================

token=os.getenv("TOKEN_BOT")

if not token:
    print("❌ Chưa có TOKEN_BOT!")
else:
    bot.run(token)
