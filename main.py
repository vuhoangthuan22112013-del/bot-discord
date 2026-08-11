import os,random,asyncio,time,discord
from discord.ext import commands

TOKEN_BOT=os.getenv("TOKEN_BOT")
if not TOKEN_BOT: raise RuntimeError("❌ Chưa có TOKEN_BOT!")

intents=discord.Intents.default()
intents.message_content=True
intents.members=True
bot=commands.Bot(command_prefix="!",intents=intents,help_command=None)

users={}
tx={"open":False,"bets":{}}
loans={}

def user(i):
    if i not in users:
        users[i]={"money":7500,"bank":0,"luck":100,"locked":False}
    return users[i]

def cash(n): return f"{n:,}$"

def card(t,s):
    e=discord.Embed(title=t,description=s)
    e.set_footer(text="💎 BET88")
    return e

def locked(i):
    return user(i)["locked"]

@bot.event
async def on_ready():
    print(f"✅ BET88 ONLINE: {bot.user}")

# ================= TRỢ GIÚP =================

@bot.command()
async def trogiup(ctx):
    await ctx.send(embed=card("💎 BET88",
"""🎰 **CASINO**

🎲 `!tx tai/xiu 1000`
🦀 `!bc 1000`
🪙 `!xd chan/le 1000`
🎰 `!quay 1000`
✊ `!tuxi bao/bua/keo 1000`

💰 **TÀI KHOẢN**

💳 `!vi`
🎁 `!diemdanh`
🏦 `!gui 50000`
💸 `!rut 50000`
💱 `!chuyen @user 50000`

🏦 **VAY BOT**

💰 `!vaybot 50000`
💵 `!trano 50000`

🤝 **VAY NGƯỜI CHƠI**

💰 `!vay @user 50000`
💵 `!trano 50000`

👑 **ADMIN**

🔐 `!taocode`
🎫 `!thuongcode`
📊 `!tyle`
💰 `!settien`
🔄 `!resettien`"""))

# ================= VÍ =================

@bot.command()
async def vi(ctx):
    x=user(ctx.author.id)
    await ctx.send(embed=card("💳 TÀI KHOẢN",
f"""👤 {ctx.author.mention}

💰 Ví: `{cash(x["money"])}`
🏦 Ngân hàng: `{cash(x["bank"])}`
🍀 May mắn: `{x["luck"]}%`"""))

@bot.command()
async def diemdanh(ctx):
    x=user(ctx.author.id)
    x["money"]+=2500
    await ctx.send(embed=card("🎁 ĐIỂM DANH",
f"""✅ Điểm danh thành công!

🎁 Thưởng: `+2,500$`
💰 Ví: `{cash(x["money"])}`

🍀 Chúc anh em may mắn!"""))

@bot.command()
async def gui(ctx,n:int):
    x=user(ctx.author.id)
    if n<=0 or n>x["money"]: return await ctx.send("❌ Không đủ tiền.")
    x["money"]-=n;x["bank"]+=n
    await ctx.send(embed=card("🏦 GỬI TIỀN",
f"""💰 Số tiền: `{cash(n)}`

✅ Gửi thành công!
💰 Ví: `{cash(x["money"])}`
🏦 Ngân hàng: `{cash(x["bank"])}`"""))

@bot.command()
async def rut(ctx,n:int):
    x=user(ctx.author.id)
    if n<=0 or n>x["bank"]: return await ctx.send("❌ Ngân hàng không đủ tiền.")
    x["bank"]-=n;x["money"]+=n
    await ctx.send(embed=card("💸 RÚT TIỀN",
f"""💰 Số tiền: `{cash(n)}`

✅ Rút thành công!
💰 Ví: `{cash(x["money"])}`
🏦 Ngân hàng: `{cash(x["bank"])}`"""))

@bot.command()
async def chuyen(ctx,m:discord.Member,n:int):
    x=user(ctx.author.id)
    if n<=0 or n>x["money"]: return await ctx.send("❌ Không đủ tiền.")
    x["money"]-=n;user(m.id)["money"]+=n
    await ctx.send(embed=card("💱 CHUYỂN TIỀN",
f"""👤 Người nhận: {m.mention}
💰 Số tiền: `{cash(n)}`

✅ Chuyển thành công!
💰 Ví còn lại: `{cash(x["money"])}`"""))

# ================= TÀI XỈU =================

@bot.command()
async def tx(ctx,*a):
    if locked(ctx.author.id):
        return await ctx.send("🔒 Bạn đang bị khóa Casino vì chưa trả nợ Bot.")

    if not a:
        if tx["open"]: return await ctx.send("⚠️ Phiên Tài Xỉu đang mở.")
        tx["open"]=True;tx["bets"]={}
        await ctx.send(embed=card("🎲 TÀI XỈU",
"""🎯 Anh em gõ `!tx <tai/xiu> <tiền>`

💰 Cược tối đa: `10,000,000$/ván`
⏱️ Thời gian: `30 giây`

🔥 TÀI: `0$`
❄️ XỈU: `0$`

👥 Người chơi: `0`"""))
        asyncio.create_task(endtx(ctx))
        return

    if len(a)!=2 or a[0].lower() not in ("tai","xiu"):
        return await ctx.send("❌ Dùng: `!tx tai 1000`")

    try:n=int(a[1])
    except:return await ctx.send("❌ Số tiền không hợp lệ.")

    x=user(ctx.author.id)
    if not tx["open"]: return await ctx.send("⚠️ Chưa có phiên Tài Xỉu.")
    if n<=0 or n>10000000 or n>x["money"]:
        return await ctx.send("❌ Số tiền cược không hợp lệ.")

    x["money"]-=n
    tx["bets"][ctx.author.id]=(a[0].lower(),n,ctx.author.mention)
    await ctx.send(f"✅ {ctx.author.mention} cược **{a[0].upper()}** `{cash(n)}`")

async def endtx(ctx):
    await asyncio.sleep(30)
    if not tx["open"]: return

    d=[random.randint(1,6) for _ in range(3)]
    total=sum(d)
    result="tai" if total>=11 else "xiu"
    out=[]

    for uid,(c,n,name) in tx["bets"].items():
        if c==result:
            win=n*2
            user(uid)["money"]+=win
            out.append(f"🏆 {name} `+{cash(win)}`")
        else:
            out.append(f"❌ {name} `-{cash(n)}`")

    await ctx.send(embed=card("🎲 TÀI XỈU",
f"""🎯 **Kết quả**

`[ {d[0]} ] [ {d[1]} ] [ {d[2]} ]`

💥 **TỔNG: {total}**

{"🔥 TÀI" if result=="tai" else "❄️ XỈU"}

{chr(10).join(out) if out else "👥 Không có người chơi."}

🍀 Chúc anh em may mắn!"""))

    tx["open"]=False
    tx["bets"]={}

# ================= BẦU CUA =================

@bot.command()
async def bc(ctx,n:int):
    if locked(ctx.author.id): return await ctx.send("🔒 Bạn đang bị khóa Casino.")
    x=user(ctx.author.id)
    if n<=0 or n>x["money"]: return await ctx.send("❌ Không đủ tiền.")

    x["money"]-=n

    await ctx.send(embed=card("🦀 BẦU CUA",
f"""🎯 Cược: `{cash(n)}`

🦀 Lắc... Lắc... Lắc..."""))

    await asyncio.sleep(2)

    r=random.choices(["🍐","🦀","🐟","🦐","🦌","🐓"],k=3)

    await ctx.send(embed=card("🦀 BẦU CUA",
f"""📢 **Thông báo**

`[ {r[0]} ] [ {r[1]} ] [ {r[2]} ]`

🍀 Chúc anh em may mắn!"""))

# ================= XÓC ĐĨA =================

@bot.command()
async def xd(ctx,c:str,n:int):
    if locked(ctx.author.id): return await ctx.send("🔒 Bạn đang bị khóa Casino.")
    if c.lower() not in ("chan","le"):
        return await ctx.send("❌ Chọn `chan` hoặc `le`.")

    x=user(ctx.author.id)
    if n<=0 or n>x["money"]: return await ctx.send("❌ Không đủ tiền.")

    x["money"]-=n

    await ctx.send(embed=card("🪙 XÓC ĐĨA",
f"""🎯 Cược: **{c.upper()}** — `{cash(n)}`

🪙 Xóc... Xóc... Xóc..."""))

    await asyncio.sleep(2)

    r=[random.choice(["🔴","⚪"]) for _ in range(4)]
    res="CHAN" if r.count("🔴")%2==0 else "LE"

    await ctx.send(embed=card("🪙 XÓC ĐĨA",
f"""📢 **Thông báo**

`[ {r[0]} ] [ {r[1]} ] [ {r[2]} ] [ {r[3]} ]`

💥 Kết quả: **{res}**

🍀 Chúc anh em may mắn!"""))

# ================= QUAY =================

@bot.command()
async def quay(ctx,n:int):
    if locked(ctx.author.id): return await ctx.send("🔒 Bạn đang bị khóa Casino.")
    x=user(ctx.author.id)
    if n<=0 or n>x["money"]: return await ctx.send("❌ Không đủ tiền.")

    x["money"]-=n

    await ctx.send(embed=card("🎰 QUAY",
f"""🎯 Cược: `{cash(n)}`

🎰 Đang quay..."""))

    await asyncio.sleep(2)

    r=random.choices(["🍒","7️⃣","🍋","💎"],k=3)

    await ctx.send(embed=card("🎰 QUAY",
f"""📢 **Thông báo**

`[ {r[0]} ] [ {r[1]} ] [ {r[2]} ]`

🍀 Chúc anh em may mắn!"""))

# ================= TÙ XÌ =================

@bot.command()
async def tuxi(ctx,c:str,n:int):
    if locked(ctx.author.id): return await ctx.send("🔒 Bạn đang bị khóa Casino.")
    if c.lower() not in ("bao","bua","keo"):
        return await ctx.send("❌ Chọn `bao`, `bua` hoặc `keo`.")

    x=user(ctx.author.id)
    if n<=0 or n>x["money"]: return await ctx.send("❌ Không đủ tiền.")

    x["money"]-=n
    b=random.choice(["bao","bua","keo"])

    await ctx.send(embed=card("✊ TÙ XÌ",
f"""🎯 Cược: `{cash(n)}`

👤 Bạn: **{c.upper()}**
🤖 Bot: **{b.upper()}**

🍀 Chúc anh em may mắn!"""))

# ================= VAY BOT =================

@bot.command()
async def vaybot(ctx,n:int):
    uid=ctx.author.id

    if uid in loans:
        return await ctx.send("❌ Bạn đang có khoản vay.")

    if n<1 or n>50000:
        return await ctx.send("❌ Bot cho vay từ `1$` đến `50,000$`.")

    user(uid)["money"]+=n

    loans[uid]={
        "type":"bot",
        "amount":n,
        "start":time.time()
    }

    await ctx.send(embed=card("🏦 VAY BOT",
f"""👤 Người vay: {ctx.author.mention}

💰 Khoản vay: `{cash(n)}`
📈 Lãi: `2% / ngày`
⏱️ Hạn trả: `1 giờ`

🟢 **VAY THÀNH CÔNG**

💵 Trả: `!trano {n}`"""))

# ================= VAY NGƯỜI =================

@bot.command()
async def vay(ctx,m:discord.Member,n:int):
    if m.id==ctx.author.id:
        return await ctx.send("❌ Không thể vay chính mình.")

    lender=user(ctx.author.id)

    if n<=0 or n>lender["money"]:
        return await ctx.send("❌ Bạn không đủ tiền.")

    if m.id in loans:
        return await ctx.send("❌ Người này đang có khoản nợ.")

    lender["money"]-=n
    user(m.id)["money"]+=n

    loans[m.id]={
        "type":"player",
        "amount":n,
        "lender":ctx.author.id,
        "start":time.time(),
        "bad":False
    }

    await ctx.send(embed=card("🤝 VAY NGƯỜI CHƠI",
f"""👤 Người vay: {m.mention}
🤝 Người cho vay: {ctx.author.mention}

💰 Khoản vay: `{cash(n)}`
📈 Lãi: `2% / ngày`
⏱️ Hạn trả: `1 giờ`"""))

# ================= TRẢ NỢ =================

@bot.command()
async def trano(ctx,n:int):
    uid=ctx.author.id

    if uid not in loans:
        return await ctx.send("❌ Bạn không có khoản nợ.")

    loan=loans[uid]
    debt=loan["amount"]
    x=user(uid)

    if n<debt:
        return await ctx.send(f"❌ Cần trả đủ `{cash(debt)}`.")

    if x["money"]<debt:
        return await ctx.send("❌ Bạn không đủ tiền.")

    x["money"]-=debt

    if loan["type"]=="bot":
        x["locked"]=False
        role=discord.utils.get(ctx.guild.roles,name="Con Nợ")
        if role and role in ctx.author.roles:
            await ctx.author.remove_roles(role)
    else:
        role=discord.utils.get(ctx.guild.roles,name="Nợ xấu")
        if role and role in ctx.author.roles:
            await ctx.author.remove_roles(role)

    del loans[uid]

    await ctx.send(embed=card("💵 TRẢ NỢ",
f"""✅ Đã trả: `{cash(debt)}`

💰 Ví còn: `{cash(x["money"])}`

🍀 Chúc anh em may mắn!"""))

# ================= KIỂM TRA NỢ =================

async def loan_checker():
    await bot.wait_until_ready()

    while not bot.is_closed():
        now=time.time()

        for uid,loan in list(loans.items()):

            if now-loan["start"]<3600:
                continue

            member=None
            guild=None

            for g in bot.guilds:
                m=g.get_member(uid)
                if m:
                    member=m
                    guild=g
                    break

            x=user(uid)

            if loan["type"]=="bot":

                x["locked"]=True

                if member and guild:
                    role=discord.utils.get(guild.roles,name="Con Nợ")

                    if not role:
                        try:
                            role=await guild.create_role(name="Con Nợ")
                        except:
                            role=None

                    if role and role not in member.roles:
                        try:
                            await member.add_roles(role)
                        except:
                            pass

            elif not loan["bad"]:

                loan["bad"]=True

                x["luck"]=max(0,x["luck"]-1)

                loss=int(x["money"]*0.005)
                x["money"]=max(0,x["money"]-loss)

                if member and guild:
                    role=discord.utils.get(guild.roles,name="Nợ xấu")

                    if not role:
                        try:
                            role=await guild.create_role(name="Nợ xấu")
                        except:
                            role=None

                    if role and role not in member.roles:
                        try:
                            await member.add_roles(role)
                        except:
                            pass

        await asyncio.sleep(60)

@bot.event
async def setup_hook():
    asyncio.create_task(loan_checker())

# ================= ADMIN =================

def admin(ctx):
    return ctx.author.guild_permissions.administrator

@bot.command()
async def settien(ctx,m:discord.Member,n:int):
    if not admin(ctx): return await ctx.send("❌ Không có quyền Admin.")
    user(m.id)["money"]=n
    await ctx.send(f"💰 Đã đặt tiền {m.mention}: `{cash(n)}`")

@bot.command()
async def resettien(ctx,m:discord.Member):
    if not admin(ctx): return await ctx.send("❌ Không có quyền Admin.")
    users[m.id]={"money":7500,"bank":0,"luck":100,"locked":False}
    await ctx.send(f"🔄 Đã reset {m.mention}.")

@bot.command()
async def tyle(ctx):
    if not admin(ctx): return await ctx.send("❌ Không có quyền Admin.")
    await ctx.send(embed=card("📊 TỶ LỆ",
"""🎲 Tài Xỉu: `1 : 1`
🦀 Bầu Cua: `1 : 1`
🪙 Xóc Đĩa: `1 : 1`
🎰 Quay: `1 : 1`"""))

@bot.command()
async def taocode(ctx):
    if not admin(ctx): return await ctx.send("❌ Không có quyền Admin.")
    await ctx.send("🔐 **TẠO CODE**\nChức năng Admin đang sẵn sàng.")

@bot.command()
async def thuongcode(ctx):
    if not admin(ctx): return await ctx.send("❌ Không có quyền Admin.")
    await ctx.send("🎫 **THƯỞNG CODE**\nChức năng Admin đang sẵn sàng.")

# ================= LỖI =================

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error,commands.CommandNotFound):
        return
    if isinstance(error,commands.MissingRequiredArgument):
        return await ctx.send("❌ Thiếu thông tin.\nDùng `!trogiup`.")
    if isinstance(error,commands.BadArgument):
        return await ctx.send("❌ Sai cú pháp hoặc số tiền.\nDùng `!trogiup`.")
    print("ERROR:",error)

# ================= START =================

bot.run(TOKEN_BOT)
