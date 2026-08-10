import os, asyncio, random, time
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

users = {}
tx_rooms = {}

ORANGE = 0xF39C12
GREEN = 0x2ECC71
RED = 0xE74C3C

def user(uid, name="Thành viên"):
    if uid not in users:
        users[uid] = {"name": name, "cash": 4899, "bank": 0}
    return users[uid]

def embed(title, text, color=ORANGE):
    return discord.Embed(title=title, description=text, color=color)

def money(n):
    return f"{n:,}$"

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("!trogiup | Casino Bet88")
    )
    print("BOT ONLINE:", bot.user)

@bot.command(name="trogiup", aliases=["help"])
async def trogiup(ctx):
    e = embed("🎰 CASINO BET88 UY TÍN", 
        "⚔️ **ĐỐI KHÁNG (PVP)**\n"
        "`!danhbai`, `!thachdau`, `!dagapvp`, `!tuxipvp @User`\n\n"
        "🎲 **CASINO (SOLO)**\n"
        "`!tx`, `!daga`, `!tuxi`, `!bc`, `!xd`, `!bai`, `!rl`, `!quay`, `!duangua`, `!coinflip`\n\n"
        "🏛️ **HỆ THỐNG**\n"
        "`!vi`, `!gui`, `!rut`, `!chuyen`, `!diemdanh`, `!bxh`, `!nhapcode`")
    await ctx.send(embed=e)

@bot.command(name="vi", aliases=["money", "bal"])
async def vi(ctx, member: discord.Member = None):
    m = member or ctx.author
    u = user(m.id, m.name)
    e = embed(f"💳 TÀI KHOẢN: {m.name}", 
              f"💵 **Tiền mặt:** `{money(u['cash'])}`\n"
              f"🏦 **Két sắt:** `{money(u['bank'])}`")
    await ctx.send(embed=e)

# ================= TX =================

async def run_tx(guild_id, channel, opener):
    room = tx_rooms[guild_id]
    msg = await channel.send(embed=embed(
        "🟠 🎲 SÒNG TÀI XỈU BET88",
        f"**{opener}** đã mở phiên!\n\n"
        "🎯 Đặt cược bằng:\n`!tx tai <tiền>` hoặc `!tx xiu <tiền>`\n\n"
        "🟠 **THỜI GIAN: 30 GIÂY**\n"
        "Mỗi người chỉ được cược **1 lần**.",
        ORANGE
    ))
    room["msg"] = msg

    for left in [20, 10]:
        await asyncio.sleep(10)
        if guild_id not in tx_rooms or not tx_rooms[guild_id]["active"]:
            return
        room = tx_rooms[guild_id]
        await msg.edit(embed=embed(
            "🟠 🎲 SÒNG TÀI XỈU BET88",
            f"🎯 `!tx tai <tiền>` / `!tx xiu <tiền>`\n\n"
            f"⏳ **CÒN {left} GIÂY**\n"
            f"🔴 Tài: `{money(room['tai'])}`\n"
            f"🔵 Xỉu: `{money(room['xiu'])}`",
            ORANGE
        ))

    await asyncio.sleep(10)
    if guild_id not in tx_rooms or not tx_rooms[guild_id]["active"]:
        return

    room = tx_rooms[guild_id]
    await msg.edit(embed=embed(
        "🟠 🎲 NHÀ CÁI ĐANG XÓC BÁT...",
        "🎲 **[ ⚪ ]  [ ⚪ ]  [ ⚪ ]**\n\n"
        "⏳ Đang mở bát...",
        ORANGE
    ))
    await asyncio.sleep(.7)
    await msg.edit(embed=embed(
        "🟠 🎲 NHÀ CÁI ĐANG XÓC BÁT...",
        "🎲 **[ 🔴 ]  [ ⚪ ]  [ ⚪ ]**",
        ORANGE
    ))
    await asyncio.sleep(.7)

    d = [random.randint(1, 6) for _ in range(3)]
    total = sum(d)
    result = "tai" if total >= 11 else "xiu"
    text_result = "TÀI" if result == "tai" else "XỈU"

    wins, loses = [], []
    for uid, bet in room["bets"].items():
        u = user(uid)
        if bet["choice"] == result:
            payout = bet["amount"] * 2
            u["cash"] += payout
            wins.append(f"🏆 {bet['name']} +`{money(payout)}`")
        else:
            loses.append(f"💸 {bet['name']} -`{money(bet['amount'])}`")

    desc = (
        f"🎲 **KẾT QUẢ:**\n\n"
        f"## 🎲  {d[0]}  •  {d[1]}  •  {d[2]}\n"
        f"### ➜ {total} ĐIỂM — **{text_result}**\n\n"
        f"🏆 **THẮNG**\n" + ("\n".join(wins) if wins else "Không có") +
        f"\n\n💸 **THUA**\n" + ("\n".join(loses) if loses else "Không có")
    )
    await msg.edit(embed=embed(
        "🟢 🎲 MỞ BÁT BET88" if wins else "🔴 🎲 MỞ BÁT BET88",
        desc,
        GREEN if wins else RED
    ))
    del tx_rooms[guild_id]

@bot.command(name="tx", aliases=["taixiu"])
async def tx(ctx, choice: str = None, amount: int = None):
    gid = ctx.guild.id
    if choice is None:
        if gid in tx_rooms and tx_rooms[gid]["active"]:
            return await ctx.send(embed=embed(
                "🟠 SÒNG ĐANG MỞ",
                "Phiên hiện tại đã mở. Hãy dùng `!tx tai <tiền>` hoặc `!tx xiu <tiền>`.",
                ORANGE))
        tx_rooms[gid] = {"active": True, "bets": {}, "tai": 0, "xiu": 0}
        asyncio.create_task(run_tx(gid, ctx.channel, ctx.author.name))
        return

    choice = choice.lower()
    if choice not in ("tai", "xiu") or not amount or amount <= 0:
        return await ctx.send("❌ Dùng: `!tx tai 1000` hoặc `!tx xiu 1000`")

    room = tx_rooms.get(gid)
    if not room or not room["active"]:
        return await ctx.send("❌ Chưa có phiên. Gõ `!tx` để mở.")
    uid = ctx.author.id
    if uid in room["bets"]:
        return await ctx.send("⚠️ Bạn đã cược rồi, mỗi ván chỉ được **1 lần**.")
    u = user(uid, ctx.author.name)
    if u["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền.")

    u["cash"] -= amount
    room["bets"][uid] = {"name": ctx.author.name, "choice": choice, "amount": amount}
    room[choice] += amount
    await ctx.send(embed=embed(
        "🟠 ĐẶT CƯỢC THÀNH CÔNG",
        f"👤 {ctx.author.mention}\n"
        f"🎯 Cửa: **{choice.upper()}**\n"
        f"💰 Cược: **{money(amount)}**",
        ORANGE))

# ================= SLOT =================

@bot.command(name="quay")
async def quay(ctx, amount: int = None):
    if not amount or amount <= 0:
        return await ctx.send("❌ Dùng: `!quay 1000`")
    u = user(ctx.author.id, ctx.author.name)
    if u["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền.")
    u["cash"] -= amount

    icons = ["🍒", "🍋", "🔔", "⭐", "💎"]
    result = [random.choice(icons) for _ in range(3)]

    msg = await ctx.send(embed=embed(
        "🟠 🎰 MÁY SLOT BET88",
        "## 🎰  [ ❔ ]   [ ❔ ]   [ ❔ ]\n\n🟠 **ĐANG QUAY...**",
        ORANGE
    ))

    shown = []
    for icon in result:
        await asyncio.sleep(.8)
        shown.append(icon)
        boxes = "   ".join(f"[ {x} ]" for x in shown)
        boxes += "   " + "   ".join("[ ❔ ]" for _ in range(3-len(shown)))
        await msg.edit(embed=embed(
            "🟠 🎰 MÁY SLOT BET88",
            f"## 🎰  {boxes}\n\n🟠 **ĐANG QUAY...**",
            ORANGE
        ))

    same = result.count(result[0]) if result[0] == result[1] or result[0] == result[2] else 0
    # Xác định số biểu tượng giống nhau cao nhất
    same = max(result.count(x) for x in set(result))
    mult = {1: 0, 2: 2, 3: 5}[same] if same >= 2 else 0

    if same == 1:
        # Không trúng
        win = False
    else:
        win = True
        u["cash"] += amount * mult

    if same == 3:
        line = f"🎉 **JACKPOT x5!** Nhận `{money(amount*5)}`"
    elif same == 2:
        line = f"🎉 **2 BIỂU TƯỢNG x2!** Nhận `{money(amount*2)}`"
    else:
        line = f"💸 **TRƯỢT!** Mất `{money(amount)}`"

    await msg.edit(embed=embed(
        "🟢 🎰 MÁY SLOT BET88" if win else "🔴 🎰 MÁY SLOT BET88",
        f"## 🎰  [ {result[0]} ]   [ {result[1]} ]   [ {result[2]} ]\n\n{line}",
        GREEN if win else RED
    ))

# ================= XOCDIA =================

@bot.command(name="xd", aliases=["xocdia"])
async def xd(ctx, choice: str = None, amount: int = None):
    if not choice or choice.lower() not in ("chan", "le") or not amount or amount <= 0:
        return await ctx.send("❌ Dùng: `!xd chan 1000` hoặc `!xd le 1000`")
    u = user(ctx.author.id, ctx.author.name)
    if u["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền.")
    u["cash"] -= amount

    coins = ["🔴" if random.choice([0,1]) else "⚪" for _ in range(4)]
    msg = await ctx.send(embed=embed(
        "🟠 🪙 XÓC ĐĨA BET88",
        "## 🪙  [ ❔ ]  [ ❔ ]  [ ❔ ]  [ ❔ ]\n\n🟠 **ĐANG XÓC...**",
        ORANGE
    ))

    shown = []
    for i in range(4):
        await asyncio.sleep(.45)
        shown.append(coins[i])
        boxes = "  ".join(f"[ {x} ]" for x in shown)
        boxes += "  " + "  ".join("[ ❔ ]" for _ in range(4-len(shown)))
        await msg.edit(embed=embed(
            "🟠 🪙 XÓC ĐĨA BET88",
            f"## 🪙  {boxes}\n\n🟠 **ĐANG MỞ...**",
            ORANGE
        ))

    reds = coins.count("🔴")
    # Theo yêu cầu: chẵn = 2,4 ; lẻ = 1,3
    result = "chan" if reds in (2,4) else "le"
    win = choice.lower() == result
    if win:
        u["cash"] += amount * 2

    await msg.edit(embed=embed(
        "🟢 🪙 XÓC ĐĨA BET88" if win else "🔴 🪙 XÓC ĐĨA BET88",
        f"## 🪙  [ {coins[0]} ]  [ {coins[1]} ]  [ {coins[2]} ]  [ {coins[3]} ]\n\n"
        f"🎯 Kết quả: **{result.upper()}** ({reds} đỏ)\n"
        f"{'🏆 THẮNG — Nhận `'+money(amount*2)+'`' if win else '💸 THUA — Mất `'+money(amount)+'`'}",
        GREEN if win else RED
    ))

# ================= BAU CUA =================

@bot.command(name="bc", aliases=["baucua", "bx"])
async def bc(ctx, choice: str = None, amount: int = None):
    animals = {
        "ca":"🐟","tom":"🦐","cua":"🦀",
        "bau":"🥒","ga":"🐓","nai":"🦌"
    }
    if not choice or choice.lower() not in animals or not amount or amount <= 0:
        return await ctx.send("❌ Dùng: `!bc ca 1000` / `!bc cua 1000` ...")
    u = user(ctx.author.id, ctx.author.name)
    if u["cash"] < amount:
        return await ctx.send("❌ Không đủ tiền.")
    u["cash"] -= amount

    result = [random.choice(list(animals)) for _ in range(3)]
    msg = await ctx.send(embed=embed(
        "🟠 🎲 BẦU CUA BET88",
        "## 🎲  [ ❔ ]  [ ❔ ]  [ ❔ ]\n\n🟠 **ĐANG QUAY...**",
        ORANGE
    ))

    shown = []
    for x in result:
        await asyncio.sleep(.7)
        shown.append(x)
        boxes = "  ".join(f"[ {animals[a]} ]" for a in shown)
        boxes += "  " + "  ".join("[ ❔ ]" for _ in range(3-len(shown)))
        await msg.edit(embed=embed(
            "🟠 🎲 BẦU CUA BET88",
            f"## 🎲  {boxes}\n\n🟠 **ĐANG MỞ...**",
            ORANGE
        ))

    matches = result.count(choice.lower())
    if matches:
        mult = {1:1.5, 2:2, 3:3}[matches]
        payout = int(amount * mult)
        u["cash"] += payout
        text = f"🏆 **TRÚNG {matches} CON — x{mult}**\n💰 Nhận `{money(payout)}`"
        color = GREEN
    else:
        text = f"💸 **KHÔNG TRÚNG — Mất `{money(amount)}`**"
        color = RED

    await msg.edit(embed=embed(
        "🟢 🎲 BẦU CUA BET88" if matches else "🔴 🎲 BẦU CUA BET88",
        f"## 🎲  [ {animals[result[0]]} ]  [ {animals[result[1]]} ]  [ {animals[result[2]]} ]\n\n{text}",
        color
    ))

# ================= ĐIỂM DANH =================

last_checkin = {}
@bot.command(name="diemdanh")
async def diemdanh(ctx):
    now = time.time()
    if now - last_checkin.get(ctx.author.id, 0) < 43200:
        return await ctx.send("⚠️ Bạn đã điểm danh rồi. Thử lại sau 12 giờ.")
    last_checkin[ctx.author.id] = now
    reward = 2593
    user(ctx.author.id, ctx.author.name)["cash"] += reward
    await ctx.send(embed=embed(
        "🟢 🎁 ĐIỂM DANH",
        f"🎉 {ctx.author.mention}\n💰 **+{money(reward)}**",
        GREEN))

token = os.getenv("TOKEN_BOT")
if not token:
    raise RuntimeError("Chưa đặt biến môi trường TOKEN_BOT!")
bot.run(token)
    
