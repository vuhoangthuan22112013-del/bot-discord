import os,random,time,asyncio,discord
from discord.ext import commands

TOKEN=os.getenv("TOKEN_BOT")
START=2000
users={};codes={};spam={};loans={}
tx={"active":False,"bets":{}}

bot=commands.Bot(command_prefix="!",intents=discord.Intents.all(),help_command=None)

def U(m):
    if m.id not in users:
        users[m.id]={"cash":START,"bank":0,"daily":"","muted":False,"interest":time.time()}
    return users[m.id]

def fm(n): return f"{n:,}$"
def E(t,d,c=0x3498DB): return discord.Embed(title=t,description=d,color=c)
def adm(ctx): return ctx.author.guild_permissions.administrator

def bank_interest(u):
    now=time.time()
    days=int((now-u["interest"])/86400)
    if days>0 and u["bank"]>0:
        u["bank"]=int(u["bank"]*(1.02**days))
        u["interest"]+=days*86400

def block(ctx):
    u=U(ctx.author);bank_interest(u)
    if u["muted"]:
        asyncio.create_task(ctx.send("🔇 Bạn đang bị khóa mõm."))
        return True
    if ctx.author.id in loans and time.time()>loans[ctx.author.id]["due"]:
        asyncio.create_task(ctx.send("🔴 **CON NỢ!** Dùng `!trano số_tiền`."))
        return True
    return False

@bot.check
async def anti_spam(ctx):
    if ctx.author.bot:return False
    now=time.time();old=spam.get(ctx.author.id,0)
    if now-old<1.2:return False
    spam[ctx.author.id]=now
    return True

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online,activity=discord.Game("!trogiup | Casino"))
    print("BOT ONLINE:",bot.user)

@bot.command()
async def trogiup(ctx):
    text=("## 🎰 GAME\n`!quay 100` • `!bc cua 100`\n`!xd chan 100` • `!xd le 100`\n"
          "`!tx tai 100` • `!tx xiu 100`\n\n## 💰 TÀI KHOẢN\n"
          "`!vi` • `!chuyen @user 100`\n`!gui 100` • `!rut 100`\n"
          "`!vay 1000` • `!trano 1000`\n`!diemdanh` • `!bxh`\n\n## 🎟️ CODE\n`!nhapcode CODE`")
    if adm(ctx):
        text+="\n\n## 🛡️ ADMIN\n`!taocode tiền lượt`\n`!thuongcode tiền lượt`\n`!settien @user tiền`\n`!reset tien @user`\n`!kick @user` • `!ban @user`\n`!khoamom @user` • `!unkhoamom @user`"
    await ctx.send(embed=E("📖 HƯỚNG DẪN CASINO",text))

@bot.command()
async def vi(ctx,m:discord.Member=None):
    m=m or ctx.author;u=U(m);bank_interest(u)
    loan=loans.get(m.id,{}).get("amount",0)
    status="🔴 CON NỢ" if m.id in loans and time.time()>loans[m.id]["due"] else "🟢 Bình thường"
    await ctx.send(embed=E(f"💳 VÍ CỦA {m.display_name}",
        f"💵 Tiền: **{fm(u['cash'])}**\n🏦 Ngân hàng: **{fm(u['bank'])}**\n"
        f"💸 Khoản vay: **{fm(loan)}**\n📌 Trạng thái: **{status}**"))

@bot.command()
async def chuyen(ctx,m:discord.Member=None,amount:int=None):
    if not m or not amount or amount<=0:return await ctx.send("❌ `!chuyen @user số_tiền`")
    u=U(ctx.author)
    if amount>u["cash"]:return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=amount;U(m)["cash"]+=amount
    await ctx.send(f"💸 {ctx.author.mention} → {m.mention}: **{fm(amount)}**")

@bot.command()
async def gui(ctx,amount:int=None):
    if not amount or amount<=0:return await ctx.send("❌ `!gui số_tiền`")
    u=U(ctx.author)
    if amount>u["cash"]:return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=amount;u["bank"]+=amount
    await ctx.send(f"🏦 Đã gửi **{fm(amount)}**. Lãi ngân hàng **2%/ngày**.")

@bot.command()
async def rut(ctx,amount:int=None):
    if not amount or amount<=0:return await ctx.send("❌ `!rut số_tiền`")
    u=U(ctx.author);bank_interest(u)
    if amount>u["bank"]:return await ctx.send("❌ Ngân hàng không đủ tiền.")
    u["bank"]-=amount;u["cash"]+=amount
    await ctx.send(f"💵 Đã rút **{fm(amount)}**. Tiền mặt: **{fm(u['cash'])}**")

@bot.command()
async def diemdanh(ctx):
    u=U(ctx.author);today=time.strftime("%Y-%m-%d")
    if u["daily"]==today:return await ctx.send("⏰ Hôm nay đã điểm danh.")
    n=random.randint(1000,3000);u["cash"]+=n;u["daily"]=today
    await ctx.send(embed=E("🎁 ĐIỂM DANH",f"🎉 +**{fm(n)}**\n💰 **{fm(u['cash'])}**",0x2ECC71))

@bot.command()
async def bxh(ctx):
    arr=sorted(users.items(),key=lambda x:x[1]["cash"]+x[1]["bank"],reverse=True)[:5]
    s=""
    for i,(uid,u) in enumerate(arr,1):
        m=ctx.guild.get_member(uid);s+=f"**{i}.** {m.display_name if m else uid} — `{fm(u['cash']+u['bank'])}`\n"
    await ctx.send(embed=E("🏆 TOP 5",s,0xF1C40F))

@bot.command()
async def vay(ctx,amount:int=None):
    if not amount or not 1000<=amount<=50000:return await ctx.send("❌ Vay 1.000$ - 50.000$.")
    if ctx.author.id in loans:return await ctx.send("❌ Đang có khoản vay.")
    U(ctx.author)["cash"]+=amount;loans[ctx.author.id]={"amount":amount,"due":time.time()+3600}
    await ctx.send(f"💳 Vay thành công **{fm(amount)}**. Hạn 1 giờ.")

@bot.command()
async def trano(ctx,amount:int=None):
    if ctx.author.id not in loans:return await ctx.send("❌ Không có nợ.")
    d=loans[ctx.author.id]["amount"];u=U(ctx.author)
    if amount!=d:return await ctx.send(f"❌ Phải trả **{fm(d)}**.")
    if u["cash"]<d:return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=d;del loans[ctx.author.id]
    await ctx.send("✅ Đã trả nợ, được chơi lại.")

@bot.command()
async def quay(ctx,amount:int=None):
    if block(ctx):return
    if not amount or amount<1:return await ctx.send("❌ `!quay số_tiền`")
    u=U(ctx.author)
    if amount>u["cash"]:return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=amount;s=["🍒","🍋","⭐","🔔","💎"];a,b,c=[random.choice(s) for _ in range(3)]
    msg=await ctx.send(embed=E("🎰 7️⃣7️⃣7️⃣","【 ○ 】 【 ○ 】 【 ○ 】",0xF39C12))
    await asyncio.sleep(.7)
    win=amount*5 if a==b==c else amount*2 if len({a,b,c})<3 else 0
    if win:u["cash"]+=win
    text=f"【 {a} 】 【 {b} 】 【 {c} 】\n\n"+(f"🟢 THẮNG +{fm(win)}" if win else f"🔴 THUA -{fm(amount)}")
    await msg.edit(embed=E("🎰 7️⃣7️⃣7️⃣",text,0x2ECC71 if win else 0xE74C3C))

@bot.command()
async def bc(ctx,choice=None,amount:int=None):
    if block(ctx):return
    icons={"ca":"🐟","tom":"🦐","cua":"🦀","bau":"🥒","ga":"🐓","nai":"🦌"}
    if choice not in icons or not amount:return await ctx.send("❌ `!bc cua 100`")
    u=U(ctx.author)
    if amount>u["cash"]:return await ctx.send("❌ Không đủ tiền.")
    u["cash"]-=amount;r=[random.choice(list(icons)) for _ in range(3)];n=r.count(choice)
    win=amount*(n+1) if n else 0
    if win:u["cash"]+=win
    board=" ".join(f"【{icons[x]}】" for x in r)
    await ctx.send(embed=E("🎲 BẦU CUA",board+f"\n\n"+(f"🟢 TRÚNG x{n+1} +{fm(win)}" if win else f"🔴 THUA -{fm(amount)}"),0x2ECC71 if win else 0xE74C3C))

@bot.command()
async def xd(ctx,choice=None,amount:int=None):
    if block(ctx):return
    if choice not in ("chan","le") or not amount:return await ctx.send("❌ `!xd chan 100`")
    u=U(ctx.author)
    if amount<100 or amount>u["cash"]:return await ctx.send("❌ Cược không hợp lệ.")
    u["cash"]-=amount
    msg=await ctx.send(embed=E("🪙 XÓC ĐĨA","🔴 ⚪ 🔴 ⚪\n\n🥣 **Xóc... Xóc... Xóc...**",0xF39C12))
    await asyncio.sleep(1.5)
    balls=[random.randint(0,1) for _ in range(4)];n=sum(balls);r="chan" if n%2==0 else "le";win=amount*2 if choice==r else 0
    if win:u["cash"]+=win
    board=" ".join("🔴" if x else "⚪" for x in balls)
    await msg.edit(embed=E("🪙 XÓC ĐĨA",f"{board}\n\n🎯 **{r.upper()}**\n"+(f"🟢 THẮNG +{fm(win)}" if win else f"🔴 THUA -{fm(amount)}"),0x2ECC71 if win else 0xE74C3C))

@bot.command()
async def tx(ctx,choice=None,amount:int=None):
    if block(ctx):return
    if choice not in ("tai","xiu") or not amount:return await ctx.send("❌ `!tx tai 100`")
    u=U(ctx)
    if amount<100 or amount>u["cash"]:return await ctx.send("❌ Cược không hợp lệ.")
    if not tx["active"]:
        tx["active"]=True;tx["bets"]={}
        await ctx.send("🎲 **PHIÊN TÀI XỈU MỞ!** ⏰ 30 giây!")
        asyncio.create_task(tx_end())
    if ctx.author.id in tx["bets"]:return await ctx.send("❌ Bạn đã cược phiên này.")
    u["cash"]-=amount;tx["bets"][ctx.author.id]=(choice,amount)
    await ctx.send(f"✅ {ctx.author.mention} cược **{choice.upper()} {fm(amount)}**")

async def tx_end():
    await asyncio.sleep(30)
    if not tx["active"]:return
    d=[random.randint(1,6) for _ in range(3)];total=sum(d);r="tai" if total>=11 else "xiu"
    text=f"🎲 **KẾT QUẢ:** {d[0]} - {d[1]} - {d[2]} = **{total} → {r.upper()}**\n\n"
    for uid,(c,a) in tx["bets"].items():
        if c==r:
            w=a*2;users[uid]["cash"]+=w;text+=f"🟢 <@{uid}> +**{fm(w)}**\n"
        else:text+=f"🔴 <@{uid}> -**{fm(a)}**\n"
    ch=bot.get_channel(next(iter(tx["bets"]),0)) if False else None
    for g in bot.guilds:
        for channel in g.text_channels:
            if channel.permissions_for(g.me).send_messages:
                try: await channel.send(text);break
                except:pass
        break
    tx["active"]=False;tx["bets"]={}

@bot.command()
async def taocode(ctx,amount:int=None,uses:int=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    code="CASINO"+str(random.randint(100000,999999));codes[code]=[amount,uses]
    await ctx.author.send(f"🎟️ `{code}` — {fm(amount)} — {uses} lượt")
    await ctx.send("✅ Đã gửi code vào DM.")

@bot.command()
async def thuongcode(ctx,amount:int=None,uses:int=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    code="THUONG"+str(random.randint(100000,999999));codes[code]=[amount,uses]
    await ctx.send(f"🎁 CODE `{code}` — {fm(amount)} — {uses} lượt")

@bot.command()
async def nhapcode(ctx,code=None):
    if not code or code.upper() not in codes:return await ctx.send("❌ Code không tồn tại.")
    code=code.upper();a,n=codes[code]
    if n<=0:return await ctx.send("❌ Code hết lượt.")
    U(ctx.author)["cash"]+=a;codes[code][1]-=1
    await ctx.send(f"🎟️ Nhận **{fm(a)}**. Còn {n-1} lượt.")

@bot.command()
async def settien(ctx,m:discord.Member=None,amount:int=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if not m or amount is None:return await ctx.send("❌ `!settien @user tiền`")
    U(m)["cash"]=max(0,amount);await ctx.send(f"🛡️ Đã set {m.mention} → **{fm(amount)}**")

@bot.command()
async def reset(ctx,what=None,m:discord.Member=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if what!="tien" or not m:return await ctx.send("❌ `!reset tien @user`")
    U(m)["cash"]=START;U(m)["bank"]=0;await ctx.send(f"♻️ Reset {m.mention}.")

@bot.command()
async def kick(ctx,m:discord.Member=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if not m:return await ctx.send("❌ `!kick @user`")
    await m.kick();await ctx.send(f"👢 Đã kick {m.mention}")

@bot.command()
async def ban(ctx,m:discord.Member=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if not m:return await ctx.send("❌ `!ban @user`")
    await m.ban();await ctx.send(f"🔨 Đã ban {m.mention}")

@bot.command()
async def khoamom(ctx,m:discord.Member=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if not m:return await ctx.send("❌ `!khoamom @user`")
    U(m)["muted"]=True;await ctx.send(f"🔇 {m.mention} đã bị khóa.")

@bot.command()
async def unkhoamom(ctx,m:discord.Member=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin.")
    if not m:return await ctx.send("❌ `!unkhoamom @user`")
    U(m)["muted"]=False;await ctx.send(f"🔊 {m.mention} đã được mở khóa.")

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error,commands.CommandNotFound):return
    if isinstance(error,commands.CommandOnCooldown):return
    if isinstance(error,commands.MissingRequiredArgument):return await ctx.send("❌ Thiếu thông tin. `!trogiup`")
    if isinstance(error,commands.BadArgument):return await ctx.send("❌ Sai cú pháp.")
    print("ERROR:",error)

if not TOKEN:
    print("❌ Không tìm thấy TOKEN_BOT!")
else:
    bot.run(TOKEN)
