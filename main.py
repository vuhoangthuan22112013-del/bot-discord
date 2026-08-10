import os, random, asyncio, time, discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), help_command=None)

U = {}
TX = {"on": False, "bets": {}}

def user(x):
    if x.id not in U:
        U[x.id] = {"cash": 4899, "bank": 0, "role": "Không có", "last": time.time()}
    return U[x.id]

def money(n):
    return f"{n:,}$"

async def game(ctx, title, result, win, lose):
    color = 0xF39C12
    e = discord.Embed(title=title, description=result, color=color)
    m = await ctx.send(embed=e)
    await asyncio.sleep(1)
    e.color = 0x2ECC71 if win else 0xE74C3C
    e.description = result + ("\n\n🟢 **THẮNG!**" if win else "\n\n🔴 **THUA!**")
    await m.edit(embed=e)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("!trogiup | Casino"))
    print("BOT ONLINE:", bot.user)

@bot.command()
async def trogiup(ctx):
    e = discord.Embed(
        title="🎰 CASINO BET88",
        description=(
            "⚔️ **PVP**\n"
            "`!danhbai` `!thachdau`\n\n"
            "🎲 **CASINO**\n"
            "`!tx tai 1000`\n"
            "`!bc cua 1000`\n"
            "`!quay 1000`\n"
            "`!xd chan 1000`\n\n"
            "🏦 **TÀI KHOẢN**\n"
            "`!vi` `!gui` `!rut` `!chuyen`\n\n"
            "🛒 **CỬA HÀNG**\n"
            "`!cuahang`\n"
            "`!muan vip`\n"
            "`!muan daigia`\n"
            "`!muan typhu`"
        ),
        color=0x3498DB
    )
    await ctx.send(embed=e)

@bot.command(aliases=["money","bal"])
async def vi(ctx):
    u = user(ctx)
    e = discord.Embed(title=f"💳 Ví của {ctx.author.display_name}", color=0x3498DB)
    e.add_field(name="💵 Tiền mặt", value=money(u["cash"]))
    e.add_field(name="🏦 Ngân hàng", value=money(u["bank"]))
    e.add_field(name="👑 Role", value=u["role"], inline=False)
    await ctx.send(embed=e)

@bot.command()
async def gui(ctx, n:int=None):
    u=user(ctx)
    if not n or n<=0 or n>u["cash"]:
        return await ctx.send("❌ Số tiền không hợp lệ.")
    u["cash"]-=n
    u["bank"]+=n
    await ctx.send(f"🏦 Đã gửi **{money(n)}** vào ngân hàng.")

@bot.command()
async def rut(ctx,n:int=None):
    u=user(ctx)
    if not n or n<=0 or n>u["bank"]:
        return await ctx.send("❌ Không đủ tiền trong ngân hàng.")
    u["bank"]-=n
    u["cash"]+=n
    await ctx.send(f"💵 Đã rút **{money(n)}**.")

@bot.command()
async def chuyen(ctx, member:discord.Member=None, n:int=None):
    u=user(ctx)
    if not member or not n or n<1 or n>10_000_000 or n>u["cash"]:
        return await ctx.send("❌ `!chuyen @người số_tiền` (tối đa 10.000.000$)")
    if member.id==ctx.author.id:
        return await ctx.send("❌ Không thể chuyển cho chính mình.")
    user(member)["cash"]+=n
    u["cash"]-=n
    await ctx.send(f"💸 Đã chuyển **{money(n)}** cho {member.mention}.")

@bot.command()
async def quay(ctx,n:int=None):
    u=user(ctx)
    if not n or n<=0 or n>u["cash"]:
        return await ctx.send("❌ Số tiền không hợp lệ.")
    u["cash"]-=n
    s=["🍒","🍋","🔔","⭐","💎"]
    a=[random.choice(s) for _ in range(3)]
    await game(ctx,"🎰 SLOT",f"`{a[0]}   ?   ?`",False,False)
    await asyncio.sleep(.5)
    msg=await ctx.channel.send(f"🎰 `{a[0]}   {a[1]}   ?`")
    await asyncio.sleep(.5)
    await msg.edit(content=f"🎰 `{a[0]}   {a[1]}   {a[2]}`")
    same=len(set(a))
    if same==1:
        u["cash"]+=n*5
        await ctx.send(f"🟢 **JACKPOT x5!** +{money(n*5)}")
    elif same==2:
        u["cash"]+=int(n*1.5)
        await ctx.send(f"🟢 **THẮNG x1.5!** +{money(int(n*1.5))}")
    else:
        await ctx.send(f"🔴 **THUA!** -{money(n)}")

@bot.command()
async def xd(ctx,choice:str=None,n:int=None):
    u=user(ctx)
    if choice not in ["chan","le"] or not n or n<=0 or n>u["cash"]:
        return await ctx.send("❌ `!xd chan/le số_tiền`")
    u["cash"]-=n
    m=await ctx.send("🟠 🪙 **Xóc... Xóc... Xóc...**")
    await asyncio.sleep(1)
    reds=random.randint(0,4)
    kq="chan" if reds%2==0 else "le"
    await m.edit(content=f"🪙 **XÓC ĐĨA**\n🔴⚪🔴⚪\nKết quả: **{kq.upper()}**")
    if choice==kq:
        u["cash"]+=n*2
        await ctx.send(f"🟢 **THẮNG!** +{money(n)}")
    else:
        await ctx.send(f"🔴 **THUA!** -{money(n)}")

@bot.command()
async def bc(ctx,choice:str=None,n:int=None):
    animals={"ca":"🐟","tom":"🦐","cua":"🦀","bau":"🥒","ga":"🐓","nai":"🦌"}
    u=user(ctx)
    if choice not in animals or not n or n<=0 or n>u["cash"]:
        return await ctx.send("❌ `!bc ca/tom/cua/bau/ga/nai số_tiền`")
    u["cash"]-=n
    r=[random.choice(list(animals)) for _ in range(3)]
    m=await ctx.send("🟠 🎲 **BẦU CUA đang quay...**")
    await asyncio.sleep(.6)
    await m.edit(content=f"🎲 `{animals[r[0]]}`")
    await asyncio.sleep(.6)
    await m.edit(content=f"🎲 `{animals[r[0]]} {animals[r[1]]}`")
    await asyncio.sleep(.6)
    await m.edit(content=f"🎲 `{animals[r[0]]} {animals[r[1]]} {animals[r[2]]}`")
    c=r.count(choice)
    if c:
        u["cash"]+=n*(1+c)
        await ctx.send(f"🟢 **TRÚNG {c} CON! x{1+c}** +{money(n*c)}")
    else:
        await ctx.send(f"🔴 **THUA!** -{money(n)}")

@bot.command(aliases=["taixiu"])
async def tx(ctx,choice:str=None,n:int=None):
    global TX
    if choice not in ["tai","xiu"] or not n or n<100 or n>10_000_000:
        return await ctx.send("❌ Dùng: `!tx tai/xiu 100-10000000`")
    u=user(ctx)
    if u["cash"]<n:
        return await ctx.send("❌ Không đủ tiền.")
    if not TX["on"]:
        TX={"on":True,"bets":{}}
        m=await ctx.send("🟠 🎲 **TÀI XỈU MỞ CỬA 30 GIÂY!**")
        await asyncio.sleep(30)
        if not TX["on"]: return
        bets=TX["bets"]
        TX={"on":False,"bets":{}}
        d=[random.randint(1,6) for _ in range(3)]
        kq="tai" if sum(d)>=11 else "xiu"
        for uid,b in bets.items():
            if b[0]==kq:
                user(type("X",(),{"id":uid})())["cash"]+=b[1]*2
        await m.edit(content=f"🎲 **TÀI XỈU** `{d[0]} {d[1]} {d[2]}` → **{kq.upper()}**")
        return
    if ctx.author.id in TX["bets"]:
        return await ctx.send("❌ Mỗi người chỉ được cược **1 lần/phiên**.")
    u["cash"]-=n
    TX["bets"][ctx.author.id]=(choice,n)
    await ctx.send(f"🟠 {ctx.author.mention} cược **{money(n)} {choice.upper()}**.")

@bot.command()
async def cuahang(ctx):
    await ctx.send(
        "🛒 **CỬA HÀNG ROLE**\n"
        "💛 `!muan vip` — 10.000.000$\n"
        "💙 `!muan daigia` — 5.000.000$\n"
        "💜 `!muan typhu` — 1.000.000.000$"
    )

@bot.command()
async def muan(ctx,role:str=None):
    prices={"vip":10_000_000,"daigia":5_000_000,"typhu":1_000_000_000}
    names={"vip":"VIP","daigia":"Đại Gia","typhu":"Tỷ Phú"}
    u=user(ctx)
    if role not in prices:
        return await ctx.send("❌ `!muan vip/daigia/typhu`")
    if u["cash"]<prices[role]:
        return await ctx.send("❌ Không đủ tiền.")
    discord_role=discord.utils.get(ctx.guild.roles,name=names[role])
    if not discord_role:
        return await ctx.send(f"❌ Server chưa tạo role **{names[role]}**.")
    u["cash"]-=prices[role]
    u["role"]=names[role]
    await ctx.author.add_roles(discord_role)
    await ctx.send(f"👑 {ctx.author.mention} đã mua **{names[role]}**!")

bot.run(os.getenv("TOKEN_BOT"))
