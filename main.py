import os,random,asyncio,time,secrets,discord
from discord.ext import commands

I=discord.Intents.default();I.message_content=True
bot=commands.Bot(command_prefix="!",intents=I,help_command=None)

U={}; CODES={}; TX={"on":0,"bets":{},"msg":None}
START=4899

def u(i,n="Player"):
    if i not in U: U[i]={"name":n,"cash":START,"bank":0,"debt":0,"dd":0}
    return U[i]

def money(n): return f"{int(n):,}$"
def E(t,s,c=0x3498DB):
    return discord.Embed(title=t,description=s,color=c)

def F(s): return s+"\n\n💎 BET88"
def adm(ctx): return ctx.author.guild_permissions.administrator

B={"ca":"🐟","tom":"🦐","cua":"🦀","bau":"🍐","ga":"🐓","nai":"🦌"}
R={"bao":"🖐️","bua":"✊","keo":"✌️"}

@bot.event
async def on_ready():
    print("BET88 ONLINE:",bot.user)
    await bot.change_presence(activity=discord.Game("!trogiup | BET88"))

@bot.command()
async def trogiup(ctx):
    await ctx.send(embed=E("🎰 BET88 • TRỢ GIÚP",F(
        "🎲 `!tx tai 1000`\n"
        "🎲 `!tx xiu 1000`\n"
        "🦀 `!bc cua 1000`\n"
        "🪙 `!xd chan 1000`\n"
        "🎰 `!quay 1000`\n"
        "✊ `!tuxi bao 1000`\n\n"
        "💳 `!vi`\n🎁 `!diemdanh`\n"
        "🎫 `!thuongcode CODE`\n"
        "🏦 `!vaybot 50000`\n"
        "💵 `!trano bot 50000`\n\n"
        "👑 ADMIN\n"
        "`!taocode 50000 100`\n"
        "`!settien @user 10000`\n"
        "`!resettien @user`"
    )))

@bot.command()
async def vi(ctx):
    x=u(ctx.author.id,ctx.author.name)
    await ctx.send(embed=E("💳 TÀI KHOẢN",F(
        f"👤 Người chơi: `{ctx.author.name}`\n"
        f"💵 Tiền mặt: `{money(x['cash'])}`\n"
        f"🏦 Két sắt: `{money(x['bank'])}`\n"
        f"💸 Nợ: `{money(x['debt'])}`\n"
        "🟢 SẴN SÀNG CHƠI"
    ),0xFFD700))

@bot.command()
async def diemdanh(ctx):
    x=u(ctx.author.id,ctx.author.name);now=time.time()
    if now-x["dd"]<43200:
        return await ctx.send(embed=E("⏳ ĐIỂM DANH",F("❌ Bạn đã điểm danh!\n⏰ Hãy quay lại sau."),0xE74C3C))
    x["dd"]=now;b=2593;x["cash"]+=b
    await ctx.send(embed=E("🎁 ĐIỂM DANH",F(
        "🎉 ĐIỂM DANH THÀNH CÔNG!\n\n"
        f"💰 Tiền thưởng: `+{money(b)}`\n"
        f"💵 Đã vào ví: `{money(b)}`\n"
        f"👛 Ví hiện tại: `{money(x['cash'])}`\n\n"
        "⏰ Lần tiếp theo: `12 giờ`"
    ),0x2ECC71))

# ===== TÀI XỈU =====

@bot.command()
async def tx(ctx,ch=None,n:int=None):
    if ch not in ("tai","xiu") or not n or n<=0:
        return await ctx.send("❌ `!tx tai 1000` hoặc `!tx xiu 1000`")
    if n>10000000:return await ctx.send("❌ Tối đa `10,000,000$`!")
    x=u(ctx.author.id,ctx.author.name)

    if x["cash"]<n:return await ctx.send("❌ Không đủ tiền!")
    if ctx.author.id in TX["bets"]:return await ctx.send("❌ Bạn đã cược!")

    if not TX["on"]:
        TX.update(on=1,bets={})
        TX["msg"]=await ctx.send(embed=E("🎲 TÀI XỈU",
            "🎯 Anh em gõ `!tx <tai/xiu> <tiền>`\n"
            "💰 Cược tối đa: `10,000,000$/ván`\n"
            "⏱️ Thời gian: `30 giây`\n\n"
            "🔥 Tài  |  ❄️ Xỉu"))
        asyncio.create_task(txrun())

    x["cash"]-=n
    TX["bets"][ctx.author.id]=(ch,n,ctx.author.name)

async def txrun():
    await asyncio.sleep(30)
    d=[random.randint(1,6) for _ in range(3)]
    total=sum(d);res="tai" if total>=11 else "xiu"
    wins=[];lose=[]

    for i,(ch,n,name) in TX["bets"].items():
        x=u(i)
        if ch==res:
            p=n*2;x["cash"]+=p
            wins.append(f"🏆 {name}: `+{money(p)}`")
        else:lose.append(f"💸 {name}: `-{money(n)}`")

    icon="🔥" if res=="tai" else "❄️"
    text=F(
        "🎲 KẾT QUẢ\n\n"
        f"[ {d[0]} | {d[1]} | {d[2]} ]\n\n"
        f"💥 Tổng: `{total} điểm`\n"
        f"{icon} Kết quả: **{res.upper()}**\n\n"
        "🏆 THẮNG\n"+("\n".join(wins) if wins else "Không có")+
        "\n\n💸 THUA\n"+("\n".join(lose) if lose else "Không có")
    )
    await TX["msg"].edit(embed=E("🎲 TÀI XỈU",text,0x2ECC71 if wins else 0xE74C3C))
    TX.update(on=0,bets={},msg=None)

# ===== BẦU CUA =====

@bot.command()
async def bc(ctx,ch=None,n:int=None):
    if ch not in B or not n or n<=0:return await ctx.send("❌ `!bc cua 1000`")
    x=u(ctx.author.id,ctx.author.name)
    if x["cash"]<n:return await ctx.send("❌ Không đủ tiền!")
    x["cash"]-=n
    m=await ctx.send(embed=E("🦀 BẦU CUA",F(
        f"🎯 Bạn chọn: {B[ch]} {ch.upper()}\n"
        f"💰 Cược: `{money(n)}`\n\n"
        "🥁 ĐANG LẮC...\n🪘 Lắc... Lắc... Lắc..."
    ),0xF1C40F))
    await asyncio.sleep(1.5)
    r=[random.choice(list(B)) for _ in range(3)];k=r.count(ch)
    if k:
        p=n*(k+1);x["cash"]+=p
        s=F(
            f"[ {B[r[0]]} | {B[r[1]]} | {B[r[2]]} ]\n\n"
            f"🎯 Bạn chọn: {B[ch]} {ch.upper()}\n"
            f"💥 Kết quả: {B[ch]} {ch.upper()}\n\n"
            "🏆 THẮNG\n"
            f"🎉 Tiền thắng: `+{money(p)}`\n"
            f"💵 Đã vào ví: `{money(p)}`\n"
            f"👛 Ví hiện tại: `{money(x['cash'])}`"
        )
        c=0x2ECC71
    else:
        s=F(
            f"[ {B[r[0]]} | {B[r[1]]} | {B[r[2]]} ]\n\n"
            "💸 THUA\n"
            f"📉 Tiền mất: `-{money(n)}`\n"
            f"👛 Ví hiện tại: `{money(x['cash'])}`"
        );c=0xE74C3C
    await m.edit(embed=E("🦀 BẦU CUA",s,c))

# ===== XÓC ĐĨA =====

@bot.command()
async def xd(ctx,ch=None,n:int=None):
    if ch not in ("chan","le") or not n or n<=0:
        return await ctx.send("❌ `!xd chan 1000` hoặc `!xd le 1000`")
    x=u(ctx.author.id,ctx.author.name)
    if x["cash"]<n:return await ctx.send("❌ Không đủ tiền!")
    x["cash"]-=n
    m=await ctx.send(embed=E("🪙 XÓC ĐĨA",F(
        f"🎯 Bạn chọn: `{ch.upper()}`\n"
        f"💰 Cược: `{money(n)}`\n\n"
        "🟡 ĐANG XÓC...\n🪙 Xóc... Xóc... Xóc..."
    ),0xF1C40F))
    await asyncio.sleep(1.5)
    q=random.randint(0,4);res="chan" if q%2==0 else "le"
    balls=["⚪"]*4
    for i in random.sample(range(4),q):balls[i]="🔴"
    a=" | ".join(balls)
    if res==ch:
        p=n*2;x["cash"]+=p
        s=F(f"[ {a} ]\n\n💥 Kết quả: **{res.upper()}**\n\n"
            "🏆 THẮNG\n"
            f"🎉 Tiền thắng: `+{money(p)}`\n"
            f"💵 Đã vào ví: `{money(p)}`\n"
            f"👛 Ví hiện tại: `{money(x['cash'])}`");c=0x2ECC71
    else:
        s=F(f"[ {a} ]\n\n💥 Kết quả: **{res.upper()}**\n\n"
            "💸 THUA\n"
            f"📉 Tiền mất: `-{money(n)}`\n"
            f"👛 Ví hiện tại: `{money(x['cash'])}`");c=0xE74C3C
    await m.edit(embed=E("🪙 XÓC ĐĨA",s,c))

# ===== SLOT =====

@bot.command()
async def quay(ctx,n:int=None):
    if not n or n<=0:return await ctx.send("❌ `!quay 1000`")
    x=u(ctx.author.id,ctx.author.name)
    if x["cash"]<n:return await ctx.send("❌ Không đủ tiền!")
    x["cash"]-=n
    m=await ctx.send(embed=E("🎰 MÁY SLOT",F(
        f"💰 Cược: `{money(n)}`\n\n"
        "🟡 ĐANG QUAY...\n🎰 Quay... Quay... Quay..."
    ),0xF1C40F))
    await asyncio.sleep(1.5)
    z=["🍒","🍋","🔔","⭐","💎","7️⃣"]
    s=[random.choice(z) for _ in range(3)]
    same=max(s.count(a) for a in set(s))
    if same>=2:
        p=n*(5 if same==3 else 2);x["cash"]+=p
        t=F(f"[ {' | '.join(s)} ]\n\n✨ {same} BIỂU TƯỢNG\n\n"
            "🏆 THẮNG\n"
            f"🎉 Tiền thắng: `+{money(p)}`\n"
            f"💵 Đã vào ví: `{money(p)}`\n"
            f"👛 Ví hiện tại: `{money(x['cash'])}`");c=0x2ECC71
    else:
        t=F(f"[ {' | '.join(s)} ]\n\n💸 THUA\n"
            f"📉 Tiền mất: `-{money(n)}`\n"
            f"👛 Ví hiện tại: `{money(x['cash'])}`");c=0xE74C3C
    await m.edit(embed=E("🎰 MÁY SLOT",t,c))

# ===== TÙ XÌ =====

@bot.command()
async def tuxi(ctx,ch=None,n:int=None):
    if ch not in R or not n or n<=0:return await ctx.send("❌ `!tuxi bao 1000`")
    x=u(ctx.author.id,ctx.author.name)
    if x["cash"]<n:return await ctx.send("❌ Không đủ tiền!")
    x["cash"]-=n;b=random.choice(list(R))
    win={"bao":"bua","bua":"keo","keo":"bao"}
    s=f"💰 Cược: `{money(n)}`\n\n👤 Bạn: {R[ch]} {ch.upper()}  VS  🤖 Bot: {R[b]} {b.upper()}\n\n"
    if ch==b:
        x["cash"]+=n;s+="🤝 HÒA\n💵 Hoàn lại cược."
    elif win[ch]==b:
        p=n*2;x["cash"]+=p;s+=f"🏆 THẮNG\n🎉 Tiền thắng: `+{money(p)}`\n💵 Đã vào ví: `{money(p)}`"
    else:s+=f"💸 THUA\n📉 Tiền mất: `-{money(n)}`"
    await ctx.send(embed=E("✊ TÙ XÌ",F(s+f"\n👛 Ví hiện tại: `{money(x['cash'])}`"),0x2ECC71 if "THẮNG" in s else 0xE74C3C))

# ===== CODE =====

@bot.command()
async def taocode(ctx,amount:int=None,uses:int=100):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin!")
    if not amount:return await ctx.send("❌ `!taocode 50000 100`")
    code="BET88-"+secrets.token_hex(3).upper()
    CODES[code]=[amount,uses,set()]
    await ctx.send(embed=E("🔐 TẠO CODE",F(
        "👑 QUẢN TRỊ VIÊN\n\n"
        f"🎟️ Mã: `{code}`\n"
        f"💰 Giá trị: `{money(amount)}`\n"
        f"👥 Lượt dùng: `{uses}`\n"
        "🟢 Đang hoạt động"
    ),0x9B59B6))

@bot.command()
async def thuongcode(ctx,code=None):
    if not code:return await ctx.send("❌ `!thuongcode CODE`")
    code=code.upper()
    if code not in CODES:return await ctx.send("❌ Code không tồn tại!")
    a,lim,used=CODES[code]
    if ctx.author.id in used:return await ctx.send("❌ Bạn đã dùng code!")
    if len(used)>=lim:return await ctx.send("❌ Code hết lượt!")
    used.add(ctx.author.id);x=u(ctx.author.id,ctx.author.name);x["cash"]+=a
    await ctx.send(embed=E("🎫 CODE THƯỞNG",F(
        f"🎟️ Mã: `{code}`\n💰 Phần thưởng: `{money(a)}`\n"
        f"💵 Đã vào ví: `{money(a)}`\n👛 Ví hiện tại: `{money(x['cash'])}`"
    ),0x2ECC71))

# ===== VAY BOT =====

@bot.command()
async def vaybot(ctx,n:int=None):
    if not n or not 1<=n<=50000:return await ctx.send("❌ Vay: `1$ - 50,000$`")
    x=u(ctx.author.id,ctx.author.name)
    if x["debt"]:return await ctx.send("❌ Bạn đang có nợ!")
    x["cash"]+=n;x["debt"]=n
    await ctx.send(embed=E("🏦 VAY BOT",F(
        f"💰 Khoản vay: `{money(n)}`\n"
        f"💵 Đã nhận: `{money(n)}`\n"
        f"💸 Nợ hiện tại: `{money(n)}`\n\n"
        f"📌 Trả nợ: `!trano bot {n}`"
    ),0xF1C40F))

@bot.command()
async def trano(ctx,target=None,n:int=None):
    x=u(ctx.author.id,ctx.author.name)
    if not target or not n or n<=0:return await ctx.send("❌ `!trano bot 50000`")
    if x["debt"]<=0:return await ctx.send("❌ Bạn không có nợ!")
    if n>x["debt"] or n>x["cash"]:return await ctx.send("❌ Không đủ tiền!")
    x["cash"]-=n;x["debt"]-=n
    await ctx.send(embed=E("💵 TRẢ NỢ",F(
        f"💰 Đã trả: `{money(n)}`\n"
        f"💸 Nợ còn: `{money(x['debt'])}`\n"
        +("🟢 ĐÃ TRẢ HẾT" if not x["debt"] else "🟡 CÒN NỢ")
    ),0x2ECC71))

# ===== ADMIN =====

@bot.command()
async def settien(ctx,m:discord.Member=None,n:int=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin!")
    if not m or n is None:return await ctx.send("❌ `!settien @user 10000`")
    u(m.id,m.name)["cash"]=max(0,n)
    await ctx.send(embed=E("👑 ADMIN • SET TIỀN",F(
        f"👤 Người chơi: {m.mention}\n💰 Tiền mới: `{money(n)}`"
    ),0x9B59B6))

@bot.command()
async def resettien(ctx,m:discord.Member=None):
    if not adm(ctx):return await ctx.send("⛔ Chỉ Admin!")
    if not m:return await ctx.send("❌ `!resettien @user`")
    x=u(m.id,m.name);x["cash"]=START;x["bank"]=0
    await ctx.send(embed=E("👑 ADMIN • RESET",F(
        f"👤 Người chơi: {m.mention}\n🔄 Ví: `{money(START)}`"
    ),0x9B59B6))

TOKEN=os.getenv("TOKEN_BOT")
if not TOKEN: print("❌ Thiếu TOKEN_BOT!")
else: bot.run(TOKEN)
