import os,random,asyncio,time,discord
from discord.ext import commands

intents=discord.Intents.all()
bot=commands.Bot(command_prefix="!",intents=intents,help_command=None)

users={}
codes={}
TX={"on":False,"bets":{}}
START=2000

def U(m):
    if m.id not in users:
        users[m.id]={"cash":START,"bank":0,"role":"Không có",
        "loan":0,"due":0,"daily":0,"muted":False}
    return users[m.id]

def money(n): return f"{n:,}$"

def E(t,d="",c=0x3498DB):
    return discord.Embed(title=t,description=d,color=c)

def admin(ctx):
    return ctx.author.guild_permissions.administrator

def debt(u):
    return u["loan"]>0 and time.time()>u["due"]

def blocked(ctx):
    u=U(ctx.author)
    if u["muted"]:
        asyncio.create_task(ctx.send("🔇 Bạn đang bị khóa mõm."))
        return True
    if debt(u):
        asyncio.create_task(ctx.send(
            "🔴 **CON NỢ!**\n"
            "Bạn đã quá hạn vay và không được chơi.\n"
            "Dùng `!trano số_tiền` để trả nợ."
        ))
        return True
    return False

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino"))
    print("BOT ONLINE:",bot.user)

# ================= HELP =================

@bot.command(name="trogiup")
async def trogiup(ctx):
    t=(
    "## 🎰 CASINO\n"
    "`!tx tai 100` • `!tx xiu 100`\n"
    "`!bc cua 100` • `!bc tom 100`\n"
    "`!xd chan 100` • `!xd le 100`\n"
    "`!quay 100`\n\n"

    "## 💰 TÀI KHOẢN\n"
    "`!vi` • `!gui 100` • `!rut 100`\n"
    "`!chuyen @user 100`\n"
    "`!vay 1000` • `!trano 1000`\n"
    "`!diemdanh` • `!bxh`\n\n"

    "## 🛒 CỬA HÀNG\n"
    "`!cuahang` • `!muan vip`\n"
    "`!muan daigia` • `!muan typhu`\n\n"

    "## 🎟️ CODE\n"
    "`!nhapcode CODE`\n\n")

    if admin(ctx):
        t+=(
        "## 🛡️ ADMIN\n"
        "`!taocode tiền lượt` → gửi DM riêng\n"
        "`!thuongcode tiền lượt` → hiện trong nhóm\n"
        "`!settien @user tiền`\n"
        "`!kick @user` • `!ban @user`\n"
        "`!khoamom @user`\n"
        "`!reset tien @user`")

    await ctx.send(embed=E("🎰 CASINO BET88",t,0x3498DB))

# ================= VI =================

@bot.command()
async def vi(ctx,m:discord.Member=None):
    m=m or ctx.author
    u=U(m)
    st="CON NỢ" if debt(u) else "Bình thường"
    await ctx.send(embed=E(
        f"💳 VÍ CỦA {m.display_name}",
        f"💵 **Tiền mặt:** `{money(u['cash'])}`\n"
        f"🏦 **Ngân hàng:** `{money(u['bank'])}`\n"
        f"👑 **Role:** `{u['role']}`\n"
        f"💸 **Khoản vay:** `{money(u['loan'])}`\n"
        f"📌 **Trạng thái:** `{st}`",0x3498DB))

@bot.command()
async def gui(ctx,amount:int=None):
    if not amount or amount<=0:
        return await ctx.send("❌ `!gui số_tiền`")
    u=U(ctx.author)
    if amount>u["cash"]:
        return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=amount
    u["bank"]+=amount
    await ctx.send(embed=E(
        "🏦 NGÂN HÀNG",
        f"Đã gửi **{money(amount)}** vào ngân hàng.",0x2ECC71))

@bot.command()
async def rut(ctx,amount:int=None):
    if not amount or amount<=0:
        return await ctx.send("❌ `!rut số_tiền`")
    u=U(ctx.author)
    if amount>u["bank"]:
        return await ctx.send("❌ Ngân hàng không đủ tiền.")
    u["bank"]-=amount
    u["cash"]+=amount
    await ctx.send(embed=E(
        "💵 RÚT TIỀN",
        f"Đã rút **{money(amount)}**.",0x2ECC71))

@bot.command()
async def chuyen(ctx,m:discord.Member=None,amount:int=None):
    if not m or not amount:
        return await ctx.send("❌ `!chuyen @user số_tiền`")
    if amount<1 or amount>10_000_000:
        return await ctx.send("❌ Chỉ được 1$ - 10.000.000$.")
    if m.id==ctx.author.id:
        return await ctx.send("❌ Không thể chuyển cho chính mình.")
    a,b=U(ctx.author),U(m)
    if a["cash"]<amount:
        return await ctx.send("❌ Không đủ tiền.")
    a["cash"]-=amount
    b["cash"]+=amount
    await ctx.send(embed=E(
        "💸 CHUYỂN TIỀN",
        f"{ctx.author.mention} → {m.mention}\n"
        f"💵 **{money(amount)}**",0x2ECC71))

# ================= VAY =================

@bot.command()
async def vay(ctx,amount:int=None):
    if not amount or not 1000<=amount<=50000:
        return await ctx.send("❌ Vay từ **1.000$ đến 50.000$**.")
    u=U(ctx.author)
    if u["loan"]>0:
        return await ctx.send("❌ Bạn đang có khoản vay.")
    u["loan"]=amount
    u["cash"]+=amount
    u["due"]=time.time()+3600
    await ctx.send(embed=E(
        "💸 VAY TIỀN THÀNH CÔNG",
        f"💵 Đã vay: **{money(amount)}**\n"
        "⏰ Thời hạn: **1 giờ**\n"
        "⚠️ Quá hạn sẽ thành **CON NỢ**.\n"
        "🚫 Không được chơi cho đến khi trả nợ.\n\n"
        f"`!trano {amount}`",0xF39C12))

@bot.command()
async def trano(ctx,amount:int=None):
    u=U(ctx.author)
    if u["loan"]<=0:
        return await ctx.send("❌ Bạn không có khoản vay.")
    if not amount or amount!=u["loan"]:
        return await ctx.send(
            f"❌ Cần trả đúng **{money(u['loan'])}**.")
    if u["cash"]<amount:
        return await ctx.send("❌ Không đủ tiền trả nợ.")
    u["cash"]-=amount
    u["loan"]=0
    u["due"]=0
    await ctx.send(embed=E(
        "✅ ĐÃ TRẢ NỢ",
        f"{ctx.author.mention} đã trả **{money(amount)}**.\n"
        "🟢 Bạn đã được phép chơi lại!",0x2ECC71))

# ================= DAILY =================

@bot.command()
async def diemdanh(ctx):
    u=U(ctx.author)
    day=int(time.strftime("%Y%m%d"))
    if u["daily"]==day:
        return await ctx.send("❌ Hôm nay bạn đã điểm danh.")
    reward=random.randint(1000,3000)
    u["cash"]+=reward
    u["daily"]=day
    await ctx.send(embed=E(
        "🎁 ĐIỂM DANH",
        f"💰 Nhận **{money(reward)}**\n"
        f"💵 Số dư: **{money(u['cash'])}**",0x2ECC71))

# ================= BXH =================

@bot.command()
async def bxh(ctx):
    arr=sorted(
        users.items(),
        key=lambda x:x[1]["cash"]+x[1]["bank"],
        reverse=True)[:5]
    text=""
    for i,(uid,u) in enumerate(arr,1):
        m=ctx.guild.get_member(uid)
        n=m.display_name if m else f"User {uid}"
        text+=f"**{i}.** {n} — `{money(u['cash']+u['bank'])}`\n"
    await ctx.send(embed=E(
        "🏆 TOP 5 GIÀU NHẤT",
        text or "Chưa có dữ liệu.",0xF1C40F))

# ================= QUAY =================

@bot.command()
async def quay(ctx,amount:int=None):
    if blocked(ctx): return
    if not amount or amount<1:
        return await ctx.send("❌ `!quay số_tiền`")
    u=U(ctx.author)
    if amount>u["cash"]:
        return await ctx.send("❌ Không đủ tiền.")

    u["cash"]-=amount
    s=["🍒","🍋","⭐","🔔","💎"]
    a,b,c=[random.choice(s) for _ in range(3)]

    msg=await ctx.send(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        "🔵 **【 ❓ 】  【 ❓ 】  【 ❓ 】**",
        0xF39C12))

    await asyncio.sleep(.5)
    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        f"🔵 **【 {a} 】  【 ❓ 】  【 ❓ 】**",
        0xF39C12))

    await asyncio.sleep(.5)
    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        f"🔵 **【 {a} 】  【 {b} 】  【 ❓ 】**",
        0xF39C12))

    await asyncio.sleep(.5)
    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        f"🔵 **【 {a} 】  【 {b} 】  【 {c} 】**",
        0xF39C12))

    if a==b==c:
        win=amount*5
        u["cash"]+=win
        result=f"🟢 **JACKPOT x5!**\n💰 +{money(win)}"
        col=0x2ECC71
    elif a==b or a==c or b==c:
        win=int(amount*1.5)
        u["cash"]+=win
        result=f"🟢 **2 HÌNH GIỐNG x1.5!**\n💰 +{money(win)}"
        col=0x2ECC71
    else:
        result=f"🔴 **THUA!**\n💸 -{money(amount)}"
        col=0xE74C3C

    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        f"🔵 **【 {a} 】  【 {b} 】  【 {c} 】**\n\n{result}",
        col))

# ================= BC =================

@bot.command()
async def bc(ctx,choice:str=None,amount:int=None):
    if blocked(ctx): return

    icons={
        "ca":"🐟","tom":"🦐","cua":"🦀",
        "bau":"🥒","ga":"🐓","nai":"🦌"}

    if choice not in icons or not amount or amount<1:
        return await ctx.send(
            "❌ `!bc ca/tom/cua/bau/ga/nai số_tiền`")

    u=U(ctx.author)
    if amount>u["cash"]:
        return await ctx.send("❌ Không đủ tiền.")

    u["cash"]-=amount
    r=[random.choice(list(icons)) for _ in range(3)]

    msg=await ctx.send(embed=E(
        "🎲 BẦU CUA",
        "🟠 **ĐANG LẮC...**\n\n"
        "🔵 **【 ❓ 】  【 ❓ 】  【 ❓ 】**",
        0xF39C12))

    await asyncio.sleep(1)

    board="  ".join(f"【 {icons[x]} 】" for x in r)
    count=r.count(choice)

    if count:
        win=amount*(count+1)
        u["cash"]+=win
        text=(f"🔵 **{board}**\n\n"
              f"🟢 **TRÚNG {count} CON! x{count+1}**\n"
              f"💰 +{money(win)}")
        col=0x2ECC71
    else:
        text=(f"🔵 **{board}**\n\n"
              f"🔴 **THUA!**\n"
              f"💸 -{money(amount)}")
        col=0xE74C3C

    await msg.edit(embed=E("🎲 BẦU CUA",text,col))

# ================= XD =================

@bot.command()
async def xd(ctx,choice:str=None,amount:int=None):
    if blocked(ctx): return
    if choice not in ["chan","le"] or not amount or amount<1:
        return await ctx.send("❌ `!xd chan 100` hoặc `!xd le 100`")

    u=U(ctx.author)
    if amount>u["cash"]:
        return await ctx.send("❌ Không đủ tiền.")

    u["cash"]-=amount

    msg=await ctx.send(embed=E(
        "🪙 XÓC ĐĨA",
        "🥣 **Xóc... Xóc... Xóc...**",
        0xF39C12))

    await asyncio.sleep(1.5)

    balls=[random.randint(0,1) for _ in range(4)]
    n=sum(balls)
    result="chan" if n%2==0 else "le"
    board="  ".join("🔴" if x else "⚪" for x in balls)

    if choice==result:
        win=amount*2
        u["cash"]+=win
        text=(f"🔵 **{board}**\n\n"
              f"🎯 **{result.upper()}** • {n} đỏ\n\n"
              f"🟢 **THẮNG x2!** +{money(win)}")
        col=0x2ECC71
    else:
        text=(f"🔵 **{board}**\n\n"
              f"🎯 **{result.upper()}** • {n} đỏ\n\n"
              f"🔴 **THUA!** -{money(amount)}")
        col=0xE74C3C

    await msg.edit(embed=E("🪙 XÓC ĐĨA",text,col))

# ================= TX =================

@bot.command()
async def tx(ctx,choice:str=None,amount:int=None):
    if blocked(ctx): return
    if choice not in ["tai","xiu"]:
        return await ctx.send("❌ `!tx tai 100` hoặc `!tx xiu 100`")
    if not amount or not 100<=amount<=10_000_000:
        return await ctx.send("❌ Cược 100$ - 10.000.000$.")

    u=U(ctx.author)
    if u["cash"]<amount:
        return await ctx.send("❌ Không đủ tiền.")

    if not TX["on"]:
        TX["on"]=True
        TX["bets"]={}
        u["cash"]-=amount
        TX["bets"][ctx.author.id]=(choice,amount)

        msg=await ctx.send(embed=E(
            "🎲 TÀI XỈU",
            "🟠 **PHIÊN MỚI**\n\n"
            "⏱️ **30 giây**\n"
            "👥 Đã cược: **1**",0xF39C12))

        for left in [20,10]:
            await asyncio.sleep(10)
            if not TX["on"]: return
            await msg.edit(embed=E(
                "🎲 TÀI XỈU",
                f"🟠 **ĐANG NHẬN CƯỢC**\n\n"
                f"⏱️ Còn **{left} giây**\n"
                f"👥 Đã cược: **{len(TX['bets'])}**",
                0xF39C12))

        await asyncio.sleep(10)
        if not TX["on"]: return
        TX["on"]=False

        d=[random.randint(1,6) for _ in range(3)]
        total=sum(d)
        result="tai" if total>=11 else "xiu"

        text=f"🎲 **{d[0]} • {d[1]} • {d[2]}**\n\n"
        text+=f"🎯 **{total} điểm → {result.upper()}**\n\n"

        for uid,(ch,bet) in TX["bets"].items():
            mem=ctx.guild.get_member(uid)
            pl=U(mem) if mem else None
            if ch==result:
                win=bet*2
                if pl: pl["cash"]+=win
                text+=f"🟢 **{mem.display_name if mem else uid}** +{money(win)}\n"
            else:
                text+=f"🔴 **{mem.display_name if mem else uid}** -{money(bet)}\n"

        TX["bets"]={}
        await msg.edit(embed=E(
            "🎲 KẾT QUẢ TÀI XỈU",text,0x2ECC71))
        return

    if ctx.author.id in TX["bets"]:
        return await ctx.send("❌ Bạn đã cược rồi.")

    u["cash"]-=amount
    TX["bets"][ctx.author.id]=(choice,amount)

    await ctx.send(embed=E(
        "🎯 ĐẶT CƯỢC",
        f"{ctx.author.mention}\n"
        f"💰 **{money(amount)}** → **{choice.upper()}**",
        0xF39C12))

# ================= CODE =================

@bot.command()
async def taocode(ctx,amount:int=None,uses:int=None):
    if not admin(ctx):
        return await ctx.send("❌ Chỉ Admin.")

    if not amount or not uses or amount<=0 or uses<=0:
        return await ctx.send("❌ `!taocode số_tiền số_lượt`")

    code="CASINO"+str(random.randint(100000,999999))
    while code in codes:
        code="CASINO"+str(random.randint(100000,999999))

    codes[code]=[amount,uses]

    try:
        await ctx.author.send(embed=E(
            "🔐 CODE RIÊNG ADMIN",
            f"🎟️ **Code:** `{code}`\n"
            f"💰 **Tiền:** `{money(amount)}`\n"
            f"🔢 **Lượt:** `{uses}`",
            0x9B59B6))
        await ctx.send("✅ Code đã được gửi riêng vào DM.")
    except discord.Forbidden:
        await ctx.send("❌ Không gửi được DM.")

@bot.command()
async def thuongcode(ctx,amount:int=None,uses:int=None):
    if not admin(ctx):
        return await ctx.send("❌ Chỉ Admin.")

    if not amount or not uses or amount<=0 or uses<=0:
        return await ctx.send(
            "❌ `!thuongcode số_tiền số_lượt`")

    code="THUONG"+str(random.randint(100000,999999))
    while code in codes:
        code="THUONG"+str(random.randint(100000,999999))

    codes[code]=[amount,uses]

    await ctx.send(embed=E(
        "🎁 CODE THƯỞNG",
        "╭────────────────╮\n"
        f"│ 🎟️ **CODE:** `{code}`\n"
        f"│ 💰 **THƯỞNG:** `{money(amount)}`\n"
        f"│ 🔢 **LƯỢT:** `{uses}`\n"
        "╰────────────────╯\n\n"
        f"👉 Nhập: `!nhapcode {code}`",
        0xF1C40F))

@bot.command()
async def nhapcode(ctx,code:str=None):
    if not code:
        return await ctx.send("❌ `!nhapcode CODE`")

    code=code.upper()

    if code not in codes:
        return await ctx.send("❌ Code không tồn tại.")

    amount,uses=codes[code]

    if uses<=0:
        return await ctx.send("❌ Code đã hết lượt.")

    u=U(ctx.author)
    u["cash"]+=amount
    codes[code][1]-=1

    await ctx.send(embed=E(
        "🎉 NHẬP CODE THÀNH CÔNG",
        f"👤 {ctx.author.mention}\n"
        f"💰 Nhận: **{money(amount)}**\n"
        f"🎟️ Code: `{code}`\n"
        f"🔢 Còn: **{uses-1} lượt**",
        0x2ECC71))

# ================= ADMIN =================

@bot.command()
async def settien(ctx,m:discord.Member=None,amount:int=None):
    if not admin(ctx): return await ctx.send("❌ Chỉ Admin.")
    if not m or amount is None:
        return await ctx.send("❌ `!settien @user số_tiền`")
    if amount<0:
        return await ctx.send("❌ Số tiền không hợp lệ.")
    U(m)["cash"]=amount
    await ctx.send(embed=E(
        "🛡️ SET TIỀN",
        f"{m.mention} → **{money(amount)}**",0x3498DB))

@bot.command()
async def kick(ctx,m:discord.Member=None):
    if not admin(ctx): return await ctx.send("❌ Chỉ Admin.")
    if not m: return await ctx.send("❌ `!kick @user`")
    try:
        await m.kick()
        await ctx.send(f"👢 Đã kick {m.mention}.")
    except:
        await ctx.send("❌ Không thể kick.")

@bot.command()
async def ban(ctx,m:discord.Member=None):
    if not admin(ctx): return await ctx.send("❌ Chỉ Admin.")
    if not m: return await ctx.send("❌ `!ban @user`")
    try:
        await m.ban()
        await ctx.send(f"🔨 Đã ban {m.mention}.")
    except:
        await ctx.send("❌ Không thể ban.")

@bot.command()
async def khoamom(ctx,m:discord.Member=None):
    if not admin(ctx): return await ctx.send("❌ Chỉ Admin.")
    if not m: return await ctx.send("❌ `!khoamom @user`")
    u=U(m)
    u["muted"]=not u["muted"]
    await ctx.send(
        f"🔇 {m.mention} đã "
        f"{'bị khóa mõm.' if u['muted'] else 'được mở khóa.'}")

@bot.command()
async def reset(ctx,what:str=None,m:discord.Member=None):
    if not admin(ctx): return await ctx.send("❌ Chỉ Admin.")
    if what!="tien" or not m:
        return await ctx.send("❌ `!reset tien @user`")
    u=U(m)
    u["cash"]=START
    u["bank"]=0
    await ctx.send(
        f"♻️ {m.mention} → **{money(START)}**")

# ================= SHOP =================

@bot.command()
async def cuahang(ctx):
    await ctx.send(embed=E(
        "🛒 CỬA HÀNG ROLE",
        "💛 **VIP** — 10.000.000$\n`!muan vip`\n\n"
        "💙 **ĐẠI GIA** — 5.000.000$\n`!muan daigia`\n\n"
        "💜 **TỶ PHÚ** — 1.000.000.000$\n`!muan typhu`",
        0xF1C40F))

@bot.command()
async def muan(ctx,name:str=None):
    prices={
        "vip":10_000_000,
        "daigia":5_000_000,
        "typhu":1_000_000_000}
    names={
        "vip":"VIP",
        "daigia":"Đại Gia",
        "typhu":"Tỷ Phú"}

    if name not in prices:
        return await ctx.send("❌ `!muan vip/daigia/typhu`")

    u=U(ctx.author)
    p=prices[name]

    if u["cash"]<p:
        return await ctx.send("❌ Không đủ tiền.")

    role=discord.utils.get(
        ctx.guild.roles,name=names[name])

    if not role:
        return await ctx.send(
            f"❌ Chưa có role **{names[name]}**.")

    if role>=ctx.guild.me.top_role:
        return await ctx.send("❌ Role cao hơn bot.")

    u["cash"]-=p
    u["role"]=names[name]

    try:
        await ctx.author.add_roles(role)
    except discord.Forbidden:
        return await ctx.send("❌ Bot không có quyền gán role.")

    await ctx.send(embed=E(
        "👑 MUA ROLE THÀNH CÔNG",
        f"{ctx.author.mention}\n"
        f"Đã mua **{names[name]}**\n"
        f"💰 Giá: **{money(p)}**",0x2ECC71))

# ================= ERROR =================

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send("❌ Thiếu thông tin. Gõ `!trogiup`.")
    elif isinstance(error,commands.BadArgument):
        await ctx.send("❌ Sai cú pháp. Gõ `!trogiup`.")
    elif isinstance(error,commands.MissingPermissions):
        await ctx.send("⛔ Bạn không có quyền.")
    elif isinstance(error,commands.CommandNotFound):
        pass
    else:
        print("ERROR:",error)

# ================= START =================

TOKEN=os.getenv("TOKEN_BOT")

if not TOKEN:
    print("❌ Không tìm thấy TOKEN_BOT!")
else:
    bot.run(TOKEN)
