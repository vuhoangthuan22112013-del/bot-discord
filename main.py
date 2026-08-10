import os,random,asyncio,time,discord
from discord.ext import commands

TOKEN=os.getenv("TOKEN_BOT")
START=2000
intents=discord.Intents.all()
bot=commands.Bot(command_prefix="!",intents=intents,help_command=None)

users={}
codes={}
TX={"on":False,"bets":{}}
spam={}

def U(m):
    if m.id not in users:
        users[m.id]={"cash":START,"bank":0,"role":"Không có",
        "loan":0,"due":0,"daily":0,"muted":False}
    return users[m.id]

def M(n): return f"{n:,}$"

def E(t,d="",c=0x3498DB):
    return discord.Embed(title=t,description=d,color=c)

def ADM(ctx):
    return ctx.author.guild_permissions.administrator

def debt(u):
    return u["loan"]>0 and time.time()>u["due"]

async def play(ctx):
    u=U(ctx.author)
    if u["muted"]:
        await ctx.send("🔇 Bạn đang bị khóa.")
        return False
    if debt(u):
        await ctx.send(
            "🔴 **CON NỢ!** Bạn không được chơi.\n"
            "Dùng `!trano số_tiền` để trả nợ."
        )
        return False
    return True

async def spamcheck(ctx):
    uid=ctx.author.id
    now=time.time()
    old=spam.get(uid,0)
    if now-old<2:
        return False
    spam[uid]=now
    return True

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino")
    )
    print("BOT ONLINE:",bot.user)

@bot.check
async def anti_spam(ctx):
    if ctx.command and ctx.command.name in ["trogiup"]:
        return True
    return await spamcheck(ctx)

# ================= HELP =================

@bot.command()
async def trogiup(ctx):
    e=E("🎰 CASINO BET88","",0x3498DB)
    e.add_field(
        name="🎲 CASINO",
        value="`!tx tai 100` • `!tx xiu 100`\n"
              "`!bc cua 100` • `!bc tom 100`\n"
              "`!xd chan 100` • `!xd le 100`\n"
              "`!quay 100`",
        inline=False)
    e.add_field(
        name="💰 TÀI KHOẢN",
        value="`!vi` • `!gui 100` • `!rut 100`\n"
              "`!chuyen @user 100`\n"
              "`!vay 1000` • `!trano 1000`\n"
              "`!diemdanh` • `!bxh`",
        inline=False)
    e.add_field(
        name="🛒 CỬA HÀNG",
        value="`!cuahang`\n"
              "`!muan vip` • `!muan daigia` • `!muan typhu`",
        inline=False)
    e.add_field(
        name="🎟️ CODE",
        value="`!nhapcode CODE`",
        inline=False)
    if ADM(ctx):
        e.add_field(
            name="🛡️ ADMIN",
            value="`!taocode tiền lượt` — gửi riêng Admin\n"
                  "`!thuongcode tiền lượt` — hiện trong nhóm\n"
                  "`!settien @user tiền`\n"
                  "`!reset tien @user`\n"
                  "`!kick @user` • `!ban @user`\n"
                  "`!khoamom @user`",
            inline=False)
    await ctx.send(embed=e)

# ================= VI =================

@bot.command()
async def vi(ctx,m:discord.Member=None):
    m=m or ctx.author
    u=U(m)
    st="CON NỢ" if debt(u) else "Bình thường"
    await ctx.send(embed=E(
        f"💳 VÍ CỦA {m.display_name}",
        f"💵 Tiền mặt: **{M(u['cash'])}**\n"
        f"🏦 Ngân hàng: **{M(u['bank'])}**\n"
        f"👑 Role: **{u['role']}**\n"
        f"💸 Khoản vay: **{M(u['loan'])}**\n"
        f"📌 Trạng thái: **{st}**",
        0x3498DB))

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
        f"🟢 Đã gửi **{M(amount)}** vào ngân hàng.",
        0x2ECC71))

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
        f"🟢 Đã rút **{M(amount)}**.",
        0x2ECC71))

@bot.command()
async def chuyen(ctx,m:discord.Member=None,amount:int=None):
    if not m or not amount:
        return await ctx.send("❌ `!chuyen @user số_tiền`")
    if not 1<=amount<=10_000_000:
        return await ctx.send("❌ Tối đa 10.000.000$.")
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
        f"💰 **{M(amount)}**",
        0x2ECC71))

# ================= VAY =================

@bot.command()
async def vay(ctx,amount:int=None):
    if not amount or not 1000<=amount<=50000:
        return await ctx.send("❌ Vay từ 1.000$ đến 50.000$.")
    u=U(ctx.author)
    if u["loan"]:
        return await ctx.send("❌ Bạn đang có khoản vay.")
    u["loan"]=amount
    u["cash"]+=amount
    u["due"]=time.time()+3600
    await ctx.send(embed=E(
        "💳 VAY THÀNH CÔNG",
        f"🟢 Bạn đã vay **{M(amount)}**.\n"
        f"⏰ Thời hạn: **1 giờ**.\n"
        f"🔴 Quá hạn sẽ thành **CON NỢ**.\n\n"
        f"Trả bằng `!trano {amount}`",
        0xF39C12))

@bot.command()
async def trano(ctx,amount:int=None):
    u=U(ctx.author)
    if not u["loan"]:
        return await ctx.send("❌ Bạn không có khoản vay.")
    if amount!=u["loan"]:
        return await ctx.send(f"❌ Phải trả **{M(u['loan'])}**.")
    if u["cash"]<amount:
        return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=amount
    u["loan"]=0
    u["due"]=0
    await ctx.send(embed=E(
        "✅ ĐÃ TRẢ NỢ",
        f"💰 Bạn đã trả **{M(amount)}**.\n"
        "🟢 Bạn được phép chơi lại.",
        0x2ECC71))

# ================= DAILY =================

@bot.command()
async def diemdanh(ctx):
    u=U(ctx.author)
    day=time.strftime("%Y-%m-%d")
    if u["daily"]==day:
        return await ctx.send("⏰ Hôm nay bạn đã điểm danh.")
    n=random.randint(1000,3000)
    u["cash"]+=n
    u["daily"]=day
    await ctx.send(embed=E(
        "🎁 ĐIỂM DANH",
        f"🟢 Nhận **{M(n)}**!\n"
        f"💰 Số dư: **{M(u['cash'])}**",
        0x2ECC71))

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
        n=m.display_name if m else "Người chơi"
        total=u["cash"]+u["bank"]
        text+=f"**{i}.** {n} — 💰 `{M(total)}`\n"
    await ctx.send(embed=E(
        "🏆 TOP 5 GIÀU NHẤT",
        text or "Chưa có dữ liệu.",
        0xF1C40F))

# ================= QUAY =================

@bot.command()
async def quay(ctx,amount:int=None):
    if not await play(ctx): return
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
        "⚪   **[ ❓ ]   [ ❓ ]   [ ❓ ]**",
        0xF39C12))
    await asyncio.sleep(.5)
    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        f"⚪   **[ {a} ]   [ ❓ ]   [ ❓ ]**",
        0xF39C12))
    await asyncio.sleep(.5)
    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        f"⚪   **[ {a} ]   [ {b} ]   [ ❓ ]**",
        0xF39C12))
    await asyncio.sleep(.5)
    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        f"⚪   **[ {a} ]   [ {b} ]   [ {c} ]**",
        0xF39C12))
    if a==b==c:
        win=amount*5
        u["cash"]+=win
        text=f"🟢 **JACKPOT x5!**\n💰 +**{M(win)}**"
        col=0x2ECC71
    elif a==b or a==c or b==c:
        win=int(amount*1.5)
        u["cash"]+=win
        text=f"🟢 **2 HÌNH GIỐNG x1.5!**\n💰 +**{M(win)}**"
        col=0x2ECC71
    else:
        text=f"🔴 **THUA!**\n💸 -**{M(amount)}**"
        col=0xE74C3C
    await msg.edit(embed=E(
        "🎰 7️⃣7️⃣7️⃣",
        f"⚪ **[ {a} ]   [ {b} ]   [ {c} ]**\n\n{text}",
        col))

# ================= BẦU CUA =================

@bot.command()
async def bc(ctx,choice:str=None,amount:int=None):
    if not await play(ctx): return
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
        "⚪   **【 ? 】  【 ? 】  【 ? 】**",
        0xF39C12))
    await asyncio.sleep(.6)
    await msg.edit(embed=E(
        "🎲 BẦU CUA",
        "⚪   **【 🔄 】  【 🔄 】  【 🔄 】**",
        0xF39C12))
    await asyncio.sleep(.7)
    board="   ".join(f"【 {icons[x]} 】" for x in r)
    count=r.count(choice)
    if count:
        win=amount*(count+1)
        u["cash"]+=win
        text=f"{board}\n\n🟢 **TRÚNG {count} CON x{count+1}!**\n💰 +**{M(win)}**"
        col=0x2ECC71
    else:
        text=f"{board}\n\n🔴 **THUA!**\n💸 -**{M(amount)}**"
        col=0xE74C3C
    await msg.edit(embed=E("🎲 BẦU CUA",text,col))

# ================= XÓC ĐĨA =================

@bot.command()
async def xd(ctx,choice:str=None,amount:int=None):
    if not await play(ctx): return
    if choice not in ["chan","le"] or not amount:
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
    board="   ".join("🔴" if x else "⚪" for x in balls)
    if choice==result:
        win=amount*2
        u["cash"]+=win
        text=f"{board}\n\n🟢 **{result.upper()} — THẮNG x2!**\n💰 +**{M(win)}**"
        col=0x2ECC71
    else:
        text=f"{board}\n\n🔴 **{result.upper()} — THUA!**\n💸 -**{M(amount)}**"
        col=0xE74C3C
    await msg.edit(embed=E("🪙 XÓC ĐĨA",text,col))

# ================= TÀI XỈU =================

@bot.command()
async def tx(ctx,choice:str=None,amount:int=None):
    if not await play(ctx): return
    if choice not in ["tai","xiu"]:
        return await ctx.send("❌ `!tx tai 100` hoặc `!tx xiu 100`")
    if not amount or not 100<=amount<=10_000_000:
        return await ctx.send("❌ 100$ - 10.000.000$.")
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
            "⏱️ **30 giây** nhận cược\n"
            "🎯 Mỗi người 1 cược",
            0xF39C12))
        for left in [20,10]:
            await asyncio.sleep(10)
            if not TX["on"]: return
            await msg.edit(embed=E(
                "🎲 TÀI XỈU",
                f"🟠 **ĐANG NHẬN CƯỢC**\n\n"
                f"⏱️ Còn **{left} giây**\n"
                f"👥 **{len(TX['bets'])}** người",
                0xF39C12))
        await asyncio.sleep(10)
        TX["on"]=False
        d=[random.randint(1,6) for _ in range(3)]
        total=sum(d)
        result="tai" if total>=11 else "xiu"
        text=f"🎲 **{d[0]} • {d[1]} • {d[2]}**\n\n"
        text+=f"🎯 **{total} → {result.upper()}**\n\n"
        for uid,(ch,bet) in TX["bets"].items():
            mem=ctx.guild.get_member(uid)
            if not mem: continue
            p=U(mem)
            if ch==result:
                win=bet*2
                p["cash"]+=win
                text+=f"🟢 {mem.display_name} +**{M(win)}**\n"
            else:
                text+=f"🔴 {mem.display_name} -**{M(bet)}**\n"
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
        f"💰 **{M(amount)}** → **{choice.upper()}**",
        0xF39C12))

# ================= CODE =================

@bot.command()
async def taocode(ctx,amount:int=None,uses:int=None):
    if not ADM(ctx):
        return await ctx.send("❌ Chỉ Admin.")
    if not amount or not uses or amount<1 or uses<1:
        return await ctx.send("❌ `!taocode tiền lượt`")
    code="CASINO"+str(random.randint(100000,999999))
    while code in codes:
        code="CASINO"+str(random.randint(100000,999999))
    codes[code]=[amount,uses,set()]
    try:
        await ctx.author.send(embed=E(
            "🔐 CODE ADMIN",
            f"🎟️ **CODE:** `{code}`\n"
            f"💰 Tiền: **{M(amount)}**\n"
            f"🎫 Lượt: **{uses}**",
            0x9B59B6))
        await ctx.send("✅ Code đã được gửi riêng qua DM.")
    except discord.Forbidden:
        await ctx.send("❌ Không thể gửi DM cho bạn.")

@bot.command()
async def thuongcode(ctx,amount:int=None,uses:int=None):
    if not ADM(ctx):
        return await ctx.send("❌ Chỉ Admin.")
    if not amount or not uses or amount<1 or uses<1:
        return await ctx.send("❌ `!thuongcode tiền lượt`")
    code="THUONG"+str(random.randint(100000,999999))
    while code in codes:
        code="THUONG"+str(random.randint(100000,999999))
    codes[code]=[amount,uses,set()]
    await ctx.send(embed=E(
        "🎁 CODE THƯỞNG",
        f"╭──────────────╮\n"
        f"🎟️ **CODE:** `{code}`\n"
        f"💰 **Tiền:** `{M(amount)}`\n"
        f"🎫 **Lượt nhập:** `{uses}`\n"
        f"╰──────────────╯\n\n"
        f"📌 Nhập bằng `!nhapcode {code}`",
        0xF1C40F))

@bot.command()
async def nhapcode(ctx,code:str=None):
    if not code:
        return await ctx.send("❌ `!nhapcode CODE`")
    code=code.upper()
    if code not in codes:
        return await ctx.send("❌ Code không tồn tại.")
    amount,uses,used=codes[code]
    if uses<=0:
        return await ctx.send("❌ Code hết lượt.")
    if ctx.author.id in used:
        return await ctx.send("❌ Bạn đã nhập code này.")
    used.add(ctx.author.id)
    codes[code][1]-=1
    U(ctx.author)["cash"]+=amount
    await ctx.send(embed=E(
        "🎟️ NHẬP CODE",
        f"🟢 Nhận **{M(amount)}**!\n"
        f"🎫 Còn **{uses-1} lượt**.",
        0x2ECC71))

# ================= ADMIN =================

@bot.command()
async def settien(ctx,m:discord.Member=None,amount:int=None):
    if not ADM(ctx): return await ctx.send("❌ Chỉ Admin.")
    if not m or amount is None:
        return await ctx.send("❌ `!settien @user tiền`")
    if amount<0:
        return await ctx.send("❌ Tiền không hợp lệ.")
    U(m)["cash"]=amount
    await ctx.send(embed=E(
        "🛡️ SET TIỀN",
        f"{m.mention} → **{M(amount)}**",
        0x3498DB))

@bot.command()
async def reset(ctx,what:str=None,m:discord.Member=None):
    if not ADM(ctx): return await ctx.send("❌ Chỉ Admin.")
    if what!="tien" or not m:
        return await ctx.send("❌ `!reset tien @user`")
    u=U(m)
    u["cash"]=START
    u["bank"]=0
    await ctx.send(
        f"♻️ {m.mention} đã được reset về **{M(START)}**.")

@bot.command()
async def kick(ctx,m:discord.Member=None):
    if not ADM(ctx): return await ctx.send("❌ Chỉ Admin.")
    if not m: return await ctx.send("❌ `!kick @user`")
    try:
        await m.kick()
        await ctx.send(f"👢 Đã kick {m.mention}.")
    except:
        await ctx.send("❌ Không thể kick.")

@bot.command()
async def ban(ctx,m:discord.Member=None):
    if not ADM(ctx): return await ctx.send("❌ Chỉ Admin.")
    if not m: return await ctx.send("❌ `!ban @user`")
    try:
        await m.ban()
        await ctx.send(f"🔨 Đã ban {m.mention}.")
    except:
        await ctx.send("❌ Không thể ban.")

@bot.command()
async def khoamom(ctx,m:discord.Member=None):
    if not ADM(ctx): return await ctx.send("❌ Chỉ Admin.")
    if not m: return await ctx.send("❌ `!khoamom @user`")
    u=U(m)
    u["muted"]=not u["muted"]
    st="khóa" if u["muted"] else "mở khóa"
    await ctx.send(f"🔇 Đã **{st}** {m.mention}.")

# ================= SHOP =================

@bot.command()
async def cuahang(ctx):
    await ctx.send(embed=E(
        "🛒 CỬA HÀNG ROLE",
        "💛 **VIP** — `10.000.000$`\n"
        "`!muan vip`\n\n"
        "💙 **ĐẠI GIA** — `5.000.000$`\n"
        "`!muan daigia`\n\n"
        "💜 **TỶ PHÚ** — `1.000.000.000$`\n"
        "`!muan typhu`",
        0xF1C40F))

@bot.command()
async def muan(ctx,name:str=None):
    price={
        "vip":10_000_000,
        "daigia":5_000_000,
        "typhu":1_000_000_000}
    rn={"vip":"VIP","daigia":"Đại Gia","typhu":"Tỷ Phú"}
    if name not in price:
        return await ctx.send("❌ `!muan vip/daigia/typhu`")
    u=U(ctx.author)
    if u["cash"]<price[name]:
        return await ctx.send("❌ Không đủ tiền.")
    role=discord.utils.get(ctx.guild.roles,name=rn[name])
    if not role:
        return await ctx.send(f"❌ Chưa có role **{rn[name]}**.")
    if role>=ctx.guild.me.top_role:
        return await ctx.send("❌ Role cao hơn bot.")
    u["cash"]-=price[name]
    u["role"]=rn[name]
    try:
        await ctx.author.add_roles(role)
    except discord.Forbidden:
        return await ctx.send("❌ Bot không có quyền.")
    await ctx.send(embed=E(
        "👑 MUA ROLE THÀNH CÔNG",
        f"{ctx.author.mention}\n"
        f"👑 **{rn[name]}**\n"
        f"💰 Giá: **{M(price[name])}**",
        0x2ECC71))

# ================= ERROR =================

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error,commands.CommandNotFound):
        return
    if isinstance(error,commands.MissingRequiredArgument):
        return await ctx.send("❌ Thiếu thông tin. Gõ `!trogiup`.")
    if isinstance(error,commands.BadArgument):
        return await ctx.send("❌ Sai cú pháp. Gõ `!trogiup`.")
    if isinstance(error,commands.CheckFailure):
        return
    print("ERROR:",error)

if not TOKEN:
    print("❌ Không tìm thấy TOKEN_BOT!")
else:
    bot.run(TOKEN)
