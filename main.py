import os,random,asyncio,time,discord
from discord.ext import commands

TOKEN=os.getenv("BOT_TOKEN")
bot=commands.Bot(command_prefix="!",intents=discord.Intents.all(),help_command=None)
U={}
TX={"on":False,"bets":{}}

def u(i):
    if i not in U: U[i]={"money":7500,"bank":0,"luck":100}
    return U[i]

def money(n): return f"{n:,}$"

def emb(title,text):
    e=discord.Embed(title=title,description=text)
    e.set_footer(text="💎 BET88")
    return e

@bot.event
async def on_ready():
    print("BET88 ONLINE:",bot.user)

@bot.command()
async def trogiup(ctx):
    await ctx.send(embed=emb("💎 BET88",
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
💵 `!trano @user 50000`

👑 **ADMIN**
🔐 `!taocode`
🎫 `!thuongcode`
📊 `!tyle`
💰 `!settien`
🔄 `!resettien`"""))

@bot.command()
async def vi(ctx):
    x=u(ctx.author.id)
    await ctx.send(embed=emb("💳 TÀI KHOẢN",
    f"👤 {ctx.author.mention}\n\n💰 Ví: `{money(x['money'])}`\n🏦 Ngân hàng: `{money(x['bank'])}`\n🍀 May mắn: `{x['luck']}%`"))

@bot.command()
async def diemdanh(ctx):
    x=u(ctx.author.id); r=2500
    x["money"]+=r
    await ctx.send(embed=emb("🎁 ĐIỂM DANH",
    f"✅ ĐIỂM DANH THÀNH CÔNG!\n\n🎉 Thưởng: `+{money(r)}`\n👛 Ví: `{money(x['money'])}`\n\n🍀 Chúc anh em may mắn!"))

@bot.command()
async def gui(ctx,n:int):
    x=u(ctx.author.id)
    if n<=0 or n>x["money"]: return await ctx.send("❌ Không đủ tiền.")
    x["money"]-=n;x["bank"]+=n
    await ctx.send(embed=emb("🏦 GỬI TIỀN",f"💰 Số tiền: `{money(n)}`\n\n✅ Thành công!\n🏦 Ngân hàng: `{money(x['bank'])}`\n👛 Ví: `{money(x['money'])}`"))

@bot.command()
async def rut(ctx,n:int):
    x=u(ctx.author.id)
    if n<=0 or n>x["bank"]: return await ctx.send("❌ Ngân hàng không đủ tiền.")
    x["bank"]-=n;x["money"]+=n
    await ctx.send(embed=emb("💸 RÚT TIỀN",f"💰 Số tiền: `{money(n)}`\n\n✅ Thành công!\n🏦 Ngân hàng: `{money(x['bank'])}`\n👛 Ví: `{money(x['money'])}`"))

@bot.command()
async def chuyen(ctx,m:discord.Member,n:int):
    x=u(ctx.author.id)
    if n<=0 or n>x["money"]: return await ctx.send("❌ Không đủ tiền.")
    x["money"]-=n;u(m.id)["money"]+=n
    await ctx.send(embed=emb("💱 CHUYỂN TIỀN",
    f"👤 Người nhận: {m.mention}\n💰 Số tiền: `{money(n)}`\n\n✅ Chuyển thành công!\n👛 Ví còn lại: `{money(x['money'])}`"))

@bot.command()
async def tx(ctx,*a):
    if not TX["on"]:
        TX["on"]=True;TX["bets"]={}
        await ctx.send(embed=emb("🎲 TÀI XỈU",
        "🎯 Anh em gõ `!tx <tai/xiu> <tiền>`\n\n💰 Cược tối đa: `10,000,000$/ván`\n⏱️ Thời gian: `30 giây`\n\n🔥 TÀI: `0$`\n❄️ XỈU: `0$`\n\n👥 Người chơi: `0`"))
        asyncio.create_task(endtx(ctx))
        return
    if len(a)==2 and a[0].lower() in ("tai","xiu"):
        n=int(a[1]);x=u(ctx.author.id)
        if n<=0 or n>10000000 or n>x["money"]: return
        x["money"]-=n;TX["bets"][ctx.author.id]=(a[0].lower(),n,ctx.author)
        await ctx.send(f"✅ {ctx.author.mention} cược **{a[0].upper()}** `{money(n)}`")

async def endtx(ctx):
    await asyncio.sleep(30)
    d=[random.randint(1,6) for _ in range(3)];s=sum(d)
    win="tai" if s>=11 else "xiu"
    lines=[]
    for uid,(c,n,m) in TX["bets"].items():
        if c==win:
            p=n*2;u(uid)["money"]+=p
            lines.append(f"🏆 {m.mention} `+{money(p)}`")
        else: lines.append(f"❌ {m.mention} `-{money(n)}`")
    await ctx.send(embed=emb("🎲 KẾT QUẢ TÀI XỈU",
    f"🎯 **Kết quả**\n\n`[ {d[0]} ] [ {d[1]} ] [ {d[2]} ]`\n\n💥 **TỔNG: {s}**\n{'🔥 TÀI' if win=='tai' else '❄️ XỈU'}\n\n"+("\n".join(lines) or "Không có người chơi.")+"\n\n🍀 Chúc anh em may mắn!"))
    TX["on"]=False;TX["bets"]={}

@bot.command()
async def bc(ctx,n:int):
    x=u(ctx.author.id)
    if n<=0 or n>x["money"]: return
    x["money"]-=n
    await ctx.send(embed=emb("🦀 BẦU CUA",f"🎯 Cược: `{money(n)}`\n\n🦀 Lắc... Lắc... Lắc..."))
    await asyncio.sleep(2)
    r=random.choices(["🍐","🦀","🐟","🦐","🦌","🐓"],k=3)
    await ctx.send(embed=emb("🦀 BẦU CUA",f"📢 **Thông báo**\n\n`[ {r[0]} ] [ {r[1]} ] [ {r[2]} ]`\n\n🍀 Chúc anh em may mắn!"))

@bot.command()
async def xd(ctx,c:str,n:int):
    if c.lower() not in ("chan","le"): return
    x=u(ctx.author.id)
    if n<=0 or n>x["money"]: return
    x["money"]-=n
    await ctx.send(embed=emb("🪙 XÓC ĐĨA",f"🎯 Cược: **{c.upper()}** — `{money(n)}`\n\n🪙 Xóc... Xóc... Xóc..."))
    await asyncio.sleep(2)
    r=[random.choice(["🔴","⚪"]) for _ in range(4)]
    k="chan" if r.count("🔴")%2==0 else "le"
    await ctx.send(embed=emb("🪙 XÓC ĐĨA",f"📢 **Thông báo**\n\n`[ {' ] [ '.join(r)} ]`\n\n💥 Kết quả: **{k.upper()}**\n\n🍀 Chúc anh em may mắn!"))

@bot.command()
async def quay(ctx,n:int):
    x=u(ctx.author.id)
    if n<=0 or n>x["money"]: return
    x["money"]-=n
    await ctx.send(embed=emb("🎰 QUAY",f"🎯 Cược: `{money(n)}`\n\n🎰 Đang quay..."))
    await asyncio.sleep(2)
    r=random.choices(["🍒","7️⃣","🍋","💎"],k=3)
    await ctx.send(embed=emb("🎰 QUAY",f"📢 **Thông báo**\n\n`[ {' ] [ '.join(r)} ]`\n\n🍀 Chúc anh em may mắn!"))

@bot.command()
async def tuxi(ctx,c:str,n:int):
    x=u(ctx.author.id)
    if n<=0 or n>x["money"]: return
    x["money"]-=n
    b=random.choice(["bao","bua","keo"])
    await asyncio.sleep(1)
    await ctx.send(embed=emb("✊ TÙ XÌ",
    f"🎯 Cược: `{money(n)}`\n\n👤 Bạn: **{c.upper()}**\n🤖 Bot: **{b.upper()}**\n\n🍀 Chúc anh em may mắn!"))

@bot.command()
async def vaybot(ctx,n:int):
    if n<1 or n>50000: return await ctx.send("❌ Vay từ `1$` đến `50,000$`.")
    u(ctx.author.id)["money"]+=n
    await ctx.send(embed=emb("🏦 VAY BOT",
    f"👤 Người vay: {ctx.author.mention}\n\n💰 Khoản vay: `{money(n)}`\n📈 Lãi: `2% / ngày`\n⏱️ Hạn trả: `1 giờ`\n\n🟢 VAY THÀNH CÔNG\n\n💵 `!trano {n}`"))

@bot.command()
async def vay(ctx,m:discord.Member,n:int):
    if n<=0: return
    x=u(ctx.author.id)
    if n>x["money"]: return await ctx.send("❌ Bạn không đủ tiền.")
    x["money"]-=n;u(m.id)["money"]+=n
    await ctx.send(embed=emb("🤝 VAY NGƯỜI CHƠI",
    f"👤 Người vay: {m.mention}\n🤝 Người cho vay: {ctx.author.mention}\n\n💰 Khoản vay: `{money(n)}`\n📈 Lãi: `2% / ngày`\n⏱️ Hạn trả: `1 giờ`"))

@bot.command()
async def trano(ctx,*a):
    await ctx.send(embed=emb("💵 TRẢ NỢ","✅ Giao dịch trả nợ đã được ghi nhận."))

bot.run(TOKEN)
