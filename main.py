import os,asyncio,random,secrets,time,discord
from discord.ext import commands

I=discord.Intents.default();I.message_content=True
bot=commands.Bot(command_prefix="!",intents=I,help_command=None)

U={};C={}
BLUE,ORANGE,GREEN,RED=0x3498DB,0xF1C40F,0x2ECC71,0xE74C3C
TX={"on":False,"bets":{},"tai":0,"xiu":0,"msg":None}

def E(t,d,c=BLUE):return discord.Embed(title=t,description=d,color=c)

def user(i,n="Thành viên"):
    if i not in U:U[i]={"name":n,"cash":4899,"bank":0,"debt":0}
    return U[i]

def adm(c):return c.author.guild_permissions.administrator

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("!trogiup | Casino Bet88"))
    print("BOT ONLINE:",bot.user)

@bot.command(name="trogiup",aliases=["help"])
async def help(ctx):
    await ctx.send(embed=E("🎰 CASINO BET88",
    "`!tx tai 1000` `!tx xiu 1000`\n"
    "`!bc cua 1000` `!xd chan 1000` `!quay 1000`\n\n"
    "`!vi` `!gui` `!rut` `!chuyen @User 100`\n"
    "`!diemdanh` `!bxh`\n\n"
    "👑 Admin: `!taocode` `!thuongcode` `!settien` `!resettien`"))

@bot.command()
async def vi(ctx,m:discord.Member=None):
    m=m or ctx.author;u=user(m.id,m.name)
    await ctx.send(embed=E(f"💳 TÀI KHOẢN: {m.name.upper()}",
    f"🏷️ Hạng: Người chơi Thường\n🐥 Gà Công Nghiệp\n\n"
    f"💵 **Tiền mặt**\n`{u['cash']:,}$`\n\n"
    f"🏦 **Két sắt**\n`{u['bank']:,}$`"))

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
    if not m or not n or n<=0:return await ctx.send("❌ `!chuyen @User 100`")
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
        await ctx.send("🚫 Bạn đang có nợ, hãy trả nợ trước!")
        return True
    return False


# ================= TÀI XỈU =================

@bot.command()
async def tx(ctx,ch=None,bet:int=None):
    if await blocked(ctx):return

    if ch not in ("tai","xiu") or not bet or bet<=0:
        return await ctx.send("❌ `!tx tai 1000` hoặc `!tx xiu 1000`")

    if bet>10_000_000:
        return await ctx.send("❌ Tối đa `10,000,000$`/ván!")

    u=user(ctx.author.id,ctx.author.name)
    i=ctx.author.id

    if u["cash"]<bet:
        return await ctx.send("❌ Không đủ tiền!")

    if i in TX["bets"]:
        return await ctx.send("❌ Bạn đã cược ván này!")

    # MỞ PHIÊN
    if not TX["on"]:
        TX.update(on=True,bets={},tai=0,xiu=0)

        TX["msg"]=await ctx.send(embed=E(
            "🎲 SÒNG TÀI XỈU 30S 🎲",
            "Gõ `!tx <tai/xiu> <tiền>`\n"
            "💰 **Tối đa 10,000,000$/ván**\n\n"
            "⏱️ **Thời gian: 30 giây**\n\n"
            "💰 Tổng TÀI: `0$` | Tổng XỈU: `0$`",
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
        "🎲 SÒNG TÀI XỈU 30S 🎲",
        "Gõ `!tx <tai/xiu> <tiền>`\n"
        "💰 **Tối đa 10,000,000$/ván**\n\n"
        "⏱️ **Đang nhận cược...**\n\n"
        f"💰 Tổng TÀI: `{TX['tai']:,}$` | "
        f"Tổng XỈU: `{TX['xiu']:,}$`",
        ORANGE))

    try:await ctx.message.delete()
    except:pass


async def txround():
    await asyncio.sleep(30)

    if not TX["on"]:return

    d=[random.randint(1,6) for _ in range(3)]
    total=sum(d)

    # 11-18 TÀI, 4-10 XỈU
    result="tai" if total>=11 else "xiu"

    win=[]
    lose=[]

    for i,b in list(TX["bets"].items()):
        u=user(i)

        if b["choice"]==result:
            prize=b["amount"]*2
            u["cash"]+=prize
            win.append(
                f"• **{b['name']}** `+{prize:,}$ vào ví`"
            )
        else:
            lose.append(
                f"• **{b['name']}** `-{b['amount']:,}$`"
            )

    await TX["msg"].edit(embed=E(
        "🎲 KẾT QUẢ TÀI XỈU",
        f"**Xúc xắc**\n"
        f"`[ {d[0]} | {d[1]} | {d[2]} ]`\n\n"
        f"💥 **{total} điểm — "
        f"{'TÀI 🔴' if result=='tai' else 'XỈU 🔵'}**\n\n"
        f"🎉 **THẮNG**\n"
        f"{chr(10).join(win) or 'Không có'}\n\n"
        f"💸 **THUA**\n"
        f"{chr(10).join(lose) or 'Không có'}",
        GREEN if win else RED))

    TX.update(
        on=False,
        bets={},
        tai=0,
        xiu=0,
        msg=None
    )


# ================= BẦU CUA =================

@bot.command()
async def bc(ctx,ch=None,bet:int=None):
    if await blocked(ctx):return

    icons={
        "ca":"🐟",
        "tom":"🦐",
        "cua":"🦀",
        "bau":"🍐",
        "ga":"🐓",
        "nai":"🦌"
    }

    if ch not in icons or not bet or bet<=0:
        return await ctx.send(
            "❌ `!bc ca 1000` `!bc tom 1000` `!bc cua 1000`\n"
            "`!bc bau 1000` `!bc ga 1000` `!bc nai 1000`"
        )

    u=user(ctx.author.id,ctx.author.name)

    if u["cash"]<bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"]-=bet

    m=await ctx.send(embed=E(
        "🦀 BẦU CUA TÔM CÁ",
        "🎲 **LẮC... LẮC... LẮC...**\n\n"
        "`[  ·  |  ·  |  ·  ]`",
        ORANGE))

    await asyncio.sleep(1.5)

    r=[random.choice(list(icons)) for _ in range(3)]
    n=r.count(ch)

    # 1 mặt = hoàn vốn + lời 1 lần
    # 2 mặt = x3
    # 3 mặt = x4
    if n:
        prize=bet*(n+1)
        u["cash"]+=prize
        result=f"🎉 **THẮNG**\n💰 **+{prize:,}$ VÀO VÍ**"
    else:
        result=f"💸 **THUA**\n🔻 **-{bet:,}$**"

    faces=" | ".join(icons[x] for x in r)

    await m.edit(embed=E(
        "🦀 BẦU CUA TÔM CÁ",
        f"**KẾT QUẢ**\n\n"
        f"`[ {faces} ]`\n\n"
        f"{result}\n"
        f"💵 Ví: `{u['cash']:,}$`",
        GREEN if n else RED))


# ================= XÓC ĐĨA =================

@bot.command()
async def xd(ctx,ch=None,bet:int=None):
    if await blocked(ctx):return

    if ch not in ("chan","le") or not bet or bet<=0:
        return await ctx.send(
            "❌ `!xd chan 1000` hoặc `!xd le 1000`"
        )

    u=user(ctx.author.id,ctx.author.name)

    if u["cash"]<bet:
        return await ctx.send("❌ Không đủ tiền!")

    u["cash"]-=bet

    m=await ctx.send(embed=E(
        "🪙 XÓC ĐĨA",
        "🟠 **XÓC... XÓC... XÓC...**\n\n"
        "`[  ·  |  ·  |  ·  |  ·  ]`",
        ORANGE))

    await asyncio.sleep(1.5)

    # 4 cục, mỗi cục đỏ/trắng
    balls=[random.choice([0,1]) for _ in range(4)]
    red=sum(balls)

    result="chan" if red%2==0 else "le"
    win=result==ch

    if win:
        prize=bet*2
        u["cash"]+=prize
        res=f"🎉 **THẮNG**\n💰 **+{prize:,}$ VÀO VÍ**"
    else:
        res=f"💸 **THUA**\n🔻 **-{bet:,}$**"

    faces=" | ".join("🔴" if x else "⚪" for x in balls)

    await m.edit(embed=E(
        "🪙 XÓC ĐĨA",
        f"**KẾT QUẢ**\n\n"
        f"`[ {faces} ]`\n\n"
        f"🎯 **{result.upper()}**\n\n"
        f"{res}\n"
        f"💵 Ví: `{u['cash']:,}$`",
        GREEN if win else RED))


# ================= SLOT =================

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
        "🎰 MÁY SLOT NỔ HŨ",
        "🎰 **QUAY... QUAY... QUAY...**\n\n"
        "`[  ·  |  ·  |  ·  ]`",
        ORANGE))

    await asyncio.sleep(1.2)

    s=[
        random.choice(["🍒","🍋","🔔","⭐","💎","7️⃣"])
        for _ in range(3)
    ]

    # 3 giống = x5
    # 2 giống = x2
    if s[0]==s[1]==s[2]:
        prize=bet*5
        u["cash"]+=prize
        result=f"🎉 **NỔ HŨ!**\n💰 **+{prize:,}$ VÀO VÍ**"

    elif s[0]==s[1] or s[0]==s[2] or s[1]==s[2]:
        prize=bet*2
        u["cash"]+=prize
        result=f"🎉 **THẮNG!**\n💰 **+{prize:,}$ VÀO VÍ**"

    else:
        result=f"💸 **THUA**\n🔻 **-{bet:,}$**"

    await m.edit(embed=E(
        "🎰 MÁY SLOT NỔ HŨ",
        f"**KẾT QUẢ**\n\n"
        f"`[ {' | '.join(s)} ]`\n\n"
        f"{result}\n"
        f"💵 Ví: `{u['cash']:,}$`",
        GREEN if "THẮNG" in result or "NỔ HŨ" in result else RED))


# ================= ADMIN =================

def code():
    return "BET-"+secrets.token_hex(3).upper()

@bot.command()
async def taocode(ctx,n:int=None,uses:int=None):
    if not adm(ctx):
        return await ctx.send("⛔ Chỉ Admin!")

    if not n or not uses:
        return await ctx.send("❌ `!taocode 10000 5`")

    c=code()
    C[c]={"money":n,"uses":uses,"used":set()}

    await ctx.author.send(
        f"🔐 Code: `{c}` — 💰 `{n:,}$` — {uses} lượt"
    )
    await ctx.send("✅ Đã gửi code vào DM.")

@bot.command()
async def thuongcode(ctx,n:int=None,uses:int=None):
    if not adm(ctx):
        return await ctx.send("⛔ Chỉ Admin!")

    if not n or not uses:
        return await ctx.send("❌ `!thuongcode 10000 5`")

    c=code()
    C[c]={"money":n,"uses":uses,"used":set()}

    await ctx.send(
        f"🎁 **CODE:** `{c}` — 💰 `{n:,}$` — `{uses}` lượt"
    )

@bot.command()
async def nhapcode(ctx,c=None):
    c=(c or "").upper()

    if c not in C:
        return await ctx.send("❌ Code không tồn tại!")

    x=C[c]
    i=ctx.author.id

    if i in x["used"] or len(x["used"])>=x["uses"]:
        return await ctx.send("❌ Code hết lượt!")

    x["used"].add(i)
    user(i,ctx.author.name)["cash"]+=x["money"]

    await ctx.send(
        f"🎁 Nhận **+{x['money']:,}$ vào ví**!"
    )

@bot.command()
async def settien(ctx,m:discord.Member=None,n:int=None):
    if not adm(ctx):
        return await ctx.send("⛔ Chỉ Admin!")

    if not m or n is None:
        return await ctx.send("❌ `!settien @User 10000`")

    user(m.id,m.name)["cash"]=max(0,n)

    await ctx.send(
        f"✅ {m.mention}: `{n:,}$`"
    )

@bot.command()
async def resettien(ctx,m:discord.Member=None):
    if not adm(ctx):
        return await ctx.send("⛔ Chỉ Admin!")

    if not m:return

    user(m.id,m.name)["cash"]=4899

    await ctx.send(
        f"🔄 {m.mention} → `4,899$`"
    )


token=os.getenv("TOKEN_BOT")

if token:
    bot.run(token)
else:
    print("❌ Chưa có TOKEN_BOT!")
