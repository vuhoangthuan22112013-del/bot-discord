import discord, os, random, time, asyncio, json
from discord.ext import commands

TOKEN=os.getenv("BOT_TOKEN")
START=2000
FILE="data.json"

intents=discord.Intents.default()
intents.message_content=True
intents.members=True
bot=commands.Bot(command_prefix="!",intents=intents,help_command=None)

users={}; codes={}; daily={}; debts={}; banned=set(); muted=set()

def load():
    global users,codes,daily,debts,banned,muted
    try:
        with open(FILE,"r",encoding="utf8") as f:
            d=json.load(f)
        users={int(k):v for k,v in d.get("users",{}).items()}
        codes=d.get("codes",{})
        daily={int(k):v for k,v in d.get("daily",{}).items()}
        debts={int(k):v for k,v in d.get("debts",{}).items()}
        banned=set(map(int,d.get("banned",[])))
        muted=set(map(int,d.get("muted",[])))
    except:
        pass

def save():
    d={"users":users,"codes":codes,"daily":daily,"debts":debts,
       "banned":list(banned),"muted":list(muted)}
    try:
        with open(FILE,"w",encoding="utf8") as f:
            json.dump(d,f,ensure_ascii=False,indent=2)
    except Exception as e:
        print("SAVE:",e)

load()

def uid(m): return m.id
def money(m):
    if uid(m) not in users: users[uid(m)]=START
    return int(users[uid(m)])
def fmt(n): return f"{int(n):,}$"
def em(t,d="",c=0x5865F2): return discord.Embed(title=t,description=d,color=c)

def overdue(m):
    d=debts.get(uid(m))
    if not d:return False
    if time.time()>=d["due"]:
        d["overdue"]=True; save(); return True
    return d.get("overdue",False)

async def playok(ctx):
    m=ctx.author
    if uid(m) in banned:
        await ctx.send("⛔ Bạn đã bị cấm sử dụng bot."); return False
    if uid(m) in muted:
        await ctx.send("🔇 Bạn đang bị khóa chat."); return False
    if overdue(m):
        await ctx.send("💳 Bạn đang là **CON NỢ**!\n❌ Dùng `!trano số_tiền` để trả nợ."); return False
    return True

@bot.event
async def on_ready():
    print("BOT ONLINE:",bot.user)
    await bot.change_presence(activity=discord.Game("!trogiup"))

@bot.command(name="vi")
async def vi(ctx):
    d=debts.get(uid(ctx.author))
    debt=f"\n💳 **Nợ:** `{fmt(d['amount'])}`" if d else ""
    st="🔴 CON NỢ" if overdue(ctx.author) else "🟢 Bình thường"
    await ctx.send(embed=em(
        f"💳 VÍ CỦA {ctx.author.display_name}",
        f"💵 **Tiền:** `{fmt(money(ctx.author))}`\n"
        f"👤 **Trạng thái:** `{st}`{debt}",0x3498DB))

@bot.command(name="diemdanh")
async def diemdanh(ctx):
    u=uid(ctx.author); day=time.strftime("%Y-%m-%d")
    if daily.get(u)==day:
        await ctx.send("⏰ Hôm nay bạn đã điểm danh rồi!"); return
    n=random.randint(1000,3000); users[u]=money(ctx.author)+n; daily[u]=day; save()
    await ctx.send(embed=em("📅 ĐIỂM DANH THÀNH CÔNG",
        f"🎁 Nhận **{fmt(n)}**!\n💰 Số dư: **{fmt(money(ctx.author))}**",0x2ECC71))

@bot.command(name="bxh")
async def bxh(ctx):
    top=sorted(users.items(),key=lambda x:x[1],reverse=True)[:5]
    medals=["🥇","🥈","🥉","4️⃣","5️⃣"]
    text="\n".join(f"{medals[i]} **{bot.get_user(u).display_name if bot.get_user(u) else u}** — `{fmt(v)}`"
                   for i,(u,v) in enumerate(top))
    await ctx.send(embed=em("🏆 TOP 5 GIÀU NHẤT",text or "Chưa có dữ liệu.",0xF1C40F))

@bot.command(name="quay")
async def quay(ctx,amount:int=0):
    if not await playok(ctx): return
    if amount<=0 or money(ctx.author)<amount:
        await ctx.send("❌ Số tiền không hợp lệ hoặc bạn không đủ tiền."); return
    u=uid(ctx.author); users[u]-=amount
    icons=["🍒","🍋","⭐","🔔","🍉","💎"]
    a,b,c=random.choices(icons,k=3)
    msg=await ctx.send(embed=em("777", "⏳ **Đang quay...**",0xF1C40F))
    await asyncio.sleep(.4)
    await msg.edit(embed=em("777",f"**[ {a} ]   [ ❔ ]   [ ❔ ]**",0xF1C40F))
    await asyncio.sleep(.4)
    await msg.edit(embed=em("777",f"**[ {a} ]   [ {b} ]   [ ❔ ]**",0xF1C40F))
    await asyncio.sleep(.4)
    await msg.edit(embed=em("777",f"**[ {a} ]   [ {b} ]   [ {c} ]**",0xF1C40F))
    if a==b==c:
        win=amount*5; users[u]+=win
        r=f"🟢 **JACKPOT x5!**\n💰 Nhận `{fmt(win)}`"; col=0x2ECC71
    elif a==b or a==c or b==c:
        win=amount*3//2; users[u]+=win
        r=f"🟢 **2 HÌNH GIỐNG NHAU x1.5!**\n💰 Nhận `{fmt(win)}`"; col=0x2ECC71
    else:
        r=f"🔴 **THUA!**\n💸 Mất `{fmt(amount)}`"; col=0xE74C3C
    save()
    await asyncio.sleep(.3)
    await msg.edit(embed=em("777",f"**[ {a} ]   [ {b} ]   [ {c} ]**\n\n{r}",col))

@bot.command(name="bc")
async def bc(ctx,amount:int=0):
    if not await playok(ctx): return
    if amount<=0 or money(ctx.author)<amount:
        await ctx.send("❌ Số tiền không hợp lệ hoặc bạn không đủ tiền."); return
    u=uid(ctx.author); users[u]-=amount
    icons=["🦀","🦌","🐟","🐓","🍐","🦐"]
    roll=random.choices(icons,k=3)
    msg=await ctx.send(embed=em("🎲 BẦU CUA","⏳ **Đang lắc...**",0xF1C40F))
    await asyncio.sleep(.5)
    await msg.edit(embed=em("🎲 BẦU CUA","**[ 🎲 ]   [ 🎲 ]   [ 🎲 ]**",0xF1C40F))
    await asyncio.sleep(.6)
    pick=random.choice(icons); count=roll.count(pick)
    if count:
        win=amount*count; users[u]+=win
        r=f"🟢 **TRÚNG {count} CON! x{count}**\n💰 Nhận `{fmt(win)}`"; col=0x2ECC71
    else:
        r=f"🔴 **THUA!**\n💸 Mất `{fmt(amount)}`"; col=0xE74C3C
    save()
    await msg.edit(embed=em("🎲 BẦU CUA",
        f"**[ {roll[0]} ]   [ {roll[1]} ]   [ {roll[2]} ]**\n\n🎯 Kết quả: **{pick}**\n{r}",col))

@bot.command(name="vay")
async def vay(ctx,amount:int=0):
    u=uid(ctx.author)
    if amount<1000 or amount>50000:
        await ctx.send("❌ Chỉ được vay từ **1.000$ đến 50.000$**."); return
    if u in debts:
        await ctx.send("❌ Bạn đang có khoản vay. Hãy trả bằng `!trano`."); return
    users[u]=money(ctx.author)+amount
    debts[u]={"amount":amount,"due":time.time()+3600,"overdue":False}; save()
    await ctx.send(embed=em("💳 VAY TIỀN THÀNH CÔNG",
        f"✅ Đã vay **{fmt(amount)}**.\n⏰ Hạn: **1 giờ**.\n"
        "⚠️ Quá hạn sẽ thành **CON NỢ** và không được chơi.\n"
        f"💡 Trả bằng `!trano {amount}`",0xE67E22))

@bot.command(name="trano")
async def trano(ctx,amount:int=0):
    u=uid(ctx.author)
    if u not in debts:
        await ctx.send("❌ Bạn không có khoản nợ."); return
    debt=debts[u]["amount"]
    if amount!=debt:
        await ctx.send(f"❌ Bạn phải trả đúng **{fmt(debt)}**."); return
    if money(ctx.author)<amount:
        await ctx.send("❌ Bạn không đủ tiền trả nợ."); return
    users[u]-=amount; del debts[u]; save()
    await ctx.send(embed=em("✅ ĐÃ TRẢ NỢ",
        f"💳 Đã trả **{fmt(amount)}**.\n🟢 Bạn đã hết nợ và được chơi lại.\n"
        f"💰 Còn **{fmt(money(ctx.author))}**",0x2ECC71))

@bot.command(name="nhapcode")
async def nhapcode(ctx,code:str=""):
    code=code.upper()
    if code not in codes:
        await ctx.send("❌ Code không tồn tại hoặc đã hết lượt."); return
    c=codes[code]; u=uid(ctx.author); used=c.setdefault("used",[])
    if u in used:
        await ctx.send("❌ Bạn đã nhập code này rồi."); return
    if c["left"]<=0:
        await ctx.send("❌ Code đã hết lượt."); return
    used.append(u); c["left"]-=1; users[u]=money(ctx.author)+c["money"]; save()
    await ctx.send(embed=em("🎟️ NHẬP CODE THÀNH CÔNG",
        f"🔑 Code: `{code}`\n💰 Nhận: **{fmt(c['money'])}**\n"
        f"🎫 Lượt còn: **{c['left']}**\n💵 Số dư: **{fmt(money(ctx.author))}**",0x2ECC71))

@bot.command(name="thuongcode")
@commands.has_permissions(administrator=True)
async def thuongcode(ctx,amount:int=0,luot:int=0):
    if amount<=0 or luot<=0:
        await ctx.send("❌ Dùng: `!thuongcode số_tiền số_lượt`"); return
    code="CODE"+str(random.randint(100000,999999))
    while code in codes: code="CODE"+str(random.randint(100000,999999))
    codes[code]={"money":amount,"left":luot,"used":[]}; save()
    await ctx.send(embed=em("🎁 CODE THƯỞNG ĐÃ TẠO",
        f"🔑 **CODE:** `{code}`\n💰 **Tiền:** `{fmt(amount)}`\n"
        f"🎫 **Lượt nhập:** `{luot}`\n\n📌 Nhập: `!nhapcode {code}`",0xF1C40F))

@bot.command(name="settien")
@commands.has_permissions(administrator=True)
async def settien(ctx,member:discord.Member=None,amount:int=-1):
    if not member or amount<0:
        await ctx.send("❌ Dùng: `!settien @user số_tiền`"); return
    users[member.id]=amount; save()
    await ctx.send(f"✅ Đã set **{member.display_name}** thành **{fmt(amount)}**.")

@bot.command(name="resettien")
@commands.has_permissions(administrator=True)
async def resettien(ctx,member:discord.Member=None):
    if not member:
        await ctx.send("❌ Dùng: `!resettien @user`"); return
    users[member.id]=START; save()
    await ctx.send(f"♻️ Đã reset **{member.display_name}** về **{fmt(START)}**.")

@bot.command(name="kick")
@commands.has_permissions(administrator=True)
async def kick(ctx,member:discord.Member=None):
    if not member: await ctx.send("❌ Dùng: `!kick @user`"); return
    try:
        await member.kick(reason=f"Admin: {ctx.author}")
        await ctx.send(f"👢 Đã kick **{member.display_name}**.")
    except: await ctx.send("❌ Bot không có quyền kick người này.")

@bot.command(name="ban")
@commands.has_permissions(administrator=True)
async def ban(ctx,member:discord.Member=None):
    if not member: await ctx.send("❌ Dùng: `!ban @user`"); return
    try:
        await member.ban(reason=f"Admin: {ctx.author}")
        banned.add(member.id); save()
        await ctx.send(f"🔨 Đã ban **{member.display_name}**.")
    except: await ctx.send("❌ Bot không có quyền ban người này.")

@bot.command(name="khoamom")
@commands.has_permissions(administrator=True)
async def khoamom(ctx,member:discord.Member=None):
    if not member: await ctx.send("❌ Dùng: `!khoamom @user`"); return
    if member.id in muted:
        muted.remove(member.id); text=f"🔊 Đã mở khóa **{member.display_name}**."
    else:
        muted.add(member.id); text=f"🔇 Đã khóa **{member.display_name}**."
    save(); await ctx.send(text)

@bot.command(name="trogiup")
async def trogiup(ctx):
    e=em("📖 HƯỚNG DẪN BOT CỜ BẠC",color=0x5865F2)
    e.add_field(name="🎰 GAME",value="`!quay 1000` • `!bc 1000`",inline=False)
    e.add_field(name="💰 TÀI KHOẢN",value="`!vi` • `!diemdanh` • `!bxh`\n`!vay 1000` • `!trano 1000`",inline=False)
    e.add_field(name="🎟️ CODE",value="`!nhapcode CODE`",inline=False)
    e.add_field(name="🛒 SHOP",value="`!cuahang` • `!mua vip`",inline=False)
    if ctx.author.guild_permissions.administrator:
        e.add_field(name="🛡️ ADMIN",
                    value="`!thuongcode tiền lượt`\n`!settien @user tiền`\n"
                          "`!resettien @user`\n`!kick @user` • `!ban @user`\n"
                          "`!khoamom @user`",inline=False)
    await ctx.send(embed=e)

@bot.command(name="cuahang")
async def cuahang(ctx):
    await ctx.send(embed=em("🛒 CỬA HÀNG",
        "👑 `!mua vip` — **5.000$**\n"
        "💎 `!mua daigia` — **20.000$**\n"
        "🔥 `!mua typhu` — **50.000$**",0x9B59B6))

@bot.command(name="mua")
async def mua(ctx,item:str=""):
    prices={"vip":5000,"daigia":20000,"typhu":50000}; item=item.lower()
    if item not in prices:
        await ctx.send("❌ Sản phẩm không tồn tại."); return
    p=prices[item]
    if money(ctx.author)<p:
        await ctx.send("❌ Bạn không đủ tiền."); return
    users[uid(ctx.author)]-=p; save()
    await ctx.send(embed=em("🛒 MUA THÀNH CÔNG",
        f"✅ Đã mua **{item.upper()}**.\n💸 Giá: **{fmt(p)}**",0x2ECC71))

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error,commands.CommandNotFound): return
    if isinstance(error,commands.MissingPermissions):
        await ctx.send("⛔ Bạn không có quyền Admin."); return
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send("❌ Thiếu thông tin. Gõ `!trogiup`."); return
    if isinstance(error,commands.BadArgument):
        await ctx.send("❌ Sai cú pháp. Gõ `!trogiup`."); return
    print("ERROR:",repr(error))

async def debt_check():
    await bot.wait_until_ready()
    while not bot.is_closed():
        changed=False
        for u,d in debts.items():
            if not d.get("overdue") and time.time()>=d["due"]:
                d["overdue"]=True; changed=True
        if changed: save()
        await asyncio.sleep(10)

@bot.event
async def setup_hook():
    bot.loop.create_task(debt_check())

if not TOKEN:
    print("❌ Không tìm thấy BOT_TOKEN trong Environment Variables.")
else:
    bot.run(TOKEN)
