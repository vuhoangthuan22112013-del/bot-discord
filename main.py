import os
import random
import asyncio
from datetime import datetime, timedelta

import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN_BOT")
if not TOKEN:
    raise RuntimeError("❌ Chưa có biến TOKEN_BOT trên GitHub/Render!")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

users = {}
tx = {"open": False, "bets": {}}
loans = {}
bad_debt_role = "Nợ xấu"


def user(uid):
    if uid not in users:
        users[uid] = {
            "money": 7500,
            "bank": 0,
            "luck": 100
        }
    return users[uid]


def cash(n):
    return f"{n:,}$"


def card(title, text):
    e = discord.Embed(title=title, description=text)
    e.set_footer(text="💎 BET88")
    return e


@bot.event
async def on_ready():
    print(f"✅ BOT ONLINE: {bot.user}")
    print(f"🆔 ID: {bot.user.id}")


# ================= TRỢ GIÚP =================

@bot.command()
async def trogiup(ctx):
    await ctx.send(embed=card(
        "💎 BET88",
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
💵 `!trano`

🤝 **VAY NGƯỜI CHƠI**

💰 `!vay @user 50000`
💵 `!trano @user`

👑 **ADMIN**

🔐 `!taocode`
🎫 `!thuongcode`
📊 `!tyle`
💰 `!settien`
🔄 `!resettien`"""
    ))


# ================= VÍ =================

@bot.command()
async def vi(ctx):
    x = user(ctx.author.id)

    await ctx.send(embed=card(
        "💳 TÀI KHOẢN",
        f"""👤 {ctx.author.mention}

💰 Ví: `{cash(x["money"])}`
🏦 Ngân hàng: `{cash(x["bank"])}`
🍀 May mắn: `{x["luck"]}%`"""
    ))


@bot.command()
async def diemdanh(ctx):
    x = user(ctx.author.id)
    reward = 2500
    x["money"] += reward

    await ctx.send(embed=card(
        "🎁 ĐIỂM DANH",
        f"""✅ Điểm danh thành công!

🎁 Thưởng: `+{cash(reward)}`
💰 Ví hiện tại: `{cash(x["money"])}`

🍀 Chúc anh em may mắn!"""
    ))


@bot.command()
async def gui(ctx, amount: int):
    x = user(ctx.author.id)

    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Số tiền không hợp lệ.")

    x["money"] -= amount
    x["bank"] += amount

    await ctx.send(embed=card(
        "🏦 GỬI TIỀN",
        f"""💰 Số tiền: `{cash(amount)}`

✅ Gửi thành công!
💰 Ví: `{cash(x["money"])}`
🏦 Ngân hàng: `{cash(x["bank"])}`"""
    ))


@bot.command()
async def rut(ctx, amount: int):
    x = user(ctx.author.id)

    if amount <= 0 or amount > x["bank"]:
        return await ctx.send("❌ Ngân hàng không đủ tiền.")

    x["bank"] -= amount
    x["money"] += amount

    await ctx.send(embed=card(
        "💸 RÚT TIỀN",
        f"""💰 Số tiền: `{cash(amount)}`

✅ Rút thành công!
💰 Ví: `{cash(x["money"])}`
🏦 Ngân hàng: `{cash(x["bank"])}`"""
    ))


@bot.command()
async def chuyen(ctx, member: discord.Member, amount: int):
    x = user(ctx.author.id)

    if member.bot:
        return await ctx.send("❌ Không thể chuyển cho bot.")

    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Không đủ tiền.")

    x["money"] -= amount
    user(member.id)["money"] += amount

    await ctx.send(embed=card(
        "💱 CHUYỂN TIỀN",
        f"""👤 Người nhận: {member.mention}
💰 Số tiền: `{cash(amount)}`

✅ Chuyển thành công!
💰 Ví còn lại: `{cash(x["money"])}`"""
    ))


# ================= TÀI XỈU =================

@bot.command()
async def tx(ctx, *args):

    if not args:
        if tx["open"]:
            return await ctx.send("⚠️ Phiên Tài Xỉu đang mở.")

        tx["open"] = True
        tx["bets"] = {}

        await ctx.send(embed=card(
            "🎲 TÀI XỈU",
            """🎯 **Anh em gõ `!tx <tai/xiu> <tiền>`**

💰 Cược tối đa: `10,000,000$/ván`
⏱️ Thời gian: `30 giây`

🔥 TÀI: `0$`
❄️ XỈU: `0$`

👥 Người chơi: `0`

💎 BET88"""
        ))

        asyncio.create_task(finish_tx(ctx))
        return

    if len(args) != 2:
        return await ctx.send("❌ Dùng: `!tx tai/xiu số_tiền`")

    choice = args[0].lower()

    if choice not in ("tai", "xiu"):
        return await ctx.send("❌ Chỉ chọn `tai` hoặc `xiu`.")

    try:
        amount = int(args[1])
    except ValueError:
        return await ctx.send("❌ Số tiền không hợp lệ.")

    x = user(ctx.author.id)

    if amount <= 0 or amount > 10_000_000:
        return await ctx.send("❌ Số tiền cược không hợp lệ.")

    if amount > x["money"]:
        return await ctx.send("❌ Bạn không đủ tiền.")

    if not tx["open"]:
        return await ctx.send("⚠️ Chưa có phiên Tài Xỉu.")

    if ctx.author.id in tx["bets"]:
        return await ctx.send("⚠️ Bạn đã cược ván này.")

    x["money"] -= amount

    tx["bets"][ctx.author.id] = {
        "choice": choice,
        "amount": amount,
        "name": ctx.author.mention
    }

    await ctx.send(
        f"🎯 {ctx.author.mention} cược **{choice.upper()}** `{cash(amount)}`"
    )


async def finish_tx(ctx):
    await asyncio.sleep(30)

    if not tx["open"]:
        return

    dice = [random.randint(1, 6) for _ in range(3)]
    total = sum(dice)
    result = "tai" if total >= 11 else "xiu"

    winners = []

    for uid, bet in tx["bets"].items():
        if bet["choice"] == result:
            win = bet["amount"] * 2
            user(uid)["money"] += win
            winners.append(
                f"🏆 {bet['name']} `+{cash(win)}`
"
            )
        else:
            winners.append(
                f"❌ {bet['name']} `-{cash(bet['amount'])}`"
            )

    text = (
        f"🎯 **Kết quả**\n\n"
        f"`[ {dice[0]} ] [ {dice[1]} ] [ {dice[2]} ]`\n\n"
        f"💥 **TỔNG: {total}**\n"
        f"{'🔥 TÀI' if result == 'tai' else '❄️ XỈU'}\n\n"
    )

    text += "\n".join(winners) if winners else "👥 Không có người chơi."
    text += "\n\n🍀 Chúc anh em may mắn!"

    await ctx.send(embed=card("🎲 KẾT QUẢ TÀI XỈU", text))

    tx["open"] = False
    tx["bets"] = {}


# ================= BẦU CUA =================

@bot.command()
async def bc(ctx, amount: int):
    x = user(ctx.author.id)

    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Không đủ tiền.")

    x["money"] -= amount

    await ctx.send(embed=card(
        "🦀 BẦU CUA",
        f"""🎯 Cược: `{cash(amount)}`

🎲 Lắc... Lắc... Lắc..."""
    ))

    await asyncio.sleep(2)

    icons = ["🍐", "🦀", "🐟", "🦐", "🦌", "🐓"]
    result = random.choices(icons, k=3)

    await ctx.send(embed=card(
        "🦀 BẦU CUA",
        f"""📢 **Thông báo**

# {result[0]}   {result[1]}   {result[2]}

🍀 Chúc anh em may mắn!"""
    ))


# ================= XÓC ĐĨA =================

@bot.command()
async def xd(ctx, choice: str, amount: int):
    choice = choice.lower()

    if choice not in ("chan", "le"):
        return await ctx.send("❌ Chọn `chan` hoặc `le`.")

    x = user(ctx.author.id)

    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Không đủ tiền.")

    x["money"] -= amount

    await ctx.send(embed=card(
        "🪙 XÓC ĐĨA",
        f"""🎯 Cược: `{choice.upper()}` — `{cash(amount)}`

🪙 Xóc... Xóc... Xóc..."""
    ))

    await asyncio.sleep(2)

    result = [random.choice(["🔴", "⚪"]) for _ in range(4)]
    is_chan = result.count("🔴") % 2 == 0
    result_text = "CHAN" if is_chan else "LE"

    await ctx.send(embed=card(
        "🪙 XÓC ĐĨA",
        f"""📢 **Thông báo**

# {result[0]}   {result[1]}   {result[2]}   {result[3]}

💥 Kết quả: **{result_text}**

🍀 Chúc anh em may mắn!"""
    ))


# ================= QUAY =================

@bot.command()
async def quay(ctx, amount: int):
    x = user(ctx.author.id)

    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Không đủ tiền.")

    x["money"] -= amount

    await ctx.send(embed=card(
        "🎰 QUAY",
        f"""🎯 Cược: `{cash(amount)}`

🎰 Đang quay..."""
    ))

    await asyncio.sleep(2)

    icons = ["🍒", "7️⃣", "🍋", "💎"]
    result = random.choices(icons, k=3)

    await ctx.send(embed=card(
        "🎰 QUAY",
        f"""📢 **Thông báo**

# {result[0]}   {result[1]}   {result[2]}

🍀 Chúc anh em may mắn!"""
    ))


# ================= TÙ XÌ =================

@bot.command()
async def tuxi(ctx, choice: str, amount: int):
    choice = choice.lower()

    if choice not in ("bao", "bua", "keo"):
        return await ctx.send("❌ Chọn `bao`, `bua` hoặc `keo`.")

    x = user(ctx.author.id)

    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Không đủ tiền.")

    x["money"] -= amount

    bot_choice = random.choice(["bao", "bua", "keo"])

    await ctx.send(embed=card(
        "✊ TÙ XÌ",
        f"""🎯 Cược: `{cash(amount)}`

👤 Bạn: **{choice.upper()}**
🤖 Bot: **{bot_choice.upper()}**

🍀 Chúc anh em may mắn!"""
    ))


# ================= VAY BOT =================

@bot.command()
async def vaybot(ctx, amount: int):
    if amount < 1 or amount > 50_000:
        return await ctx.send("❌ Bot cho vay từ `1$` đến `50,000$`.")

    uid = ctx.author.id

    if uid in loans and loans[uid].get("bot"):
        return await ctx.send("❌ Bạn đang có khoản vay Bot chưa trả.")

    user(uid)["money"] += amount

    loans[uid] = {
        "bot": True,
        "amount": amount,
        "borrower": uid,
        "due": datetime.utcnow() + timedelta(hours=1)
    }

    await ctx.send(embed=card(
        "🏦 VAY BOT",
        f"""👤 Người vay: {ctx.author.mention}

💰 Khoản vay: `{cash(amount)}`
⏱️ Hạn trả: `1 giờ`

🟢 **VAY THÀNH CÔNG**

💵 Trả bằng:
`!trano`"""
    ))

    asyncio.create_task(check_bot_debt(ctx.guild, uid))


async def check_bot_debt(guild, uid):
    await asyncio.sleep(3600)

    loan = loans.get(uid)

    if not loan or not loan.get("bot"):
        return

    member = guild.get_member(uid)

    if member:
        try:
            await member.edit(nick=f"Con Nợ | {member.display_name}")
        except discord.Forbidden:
            pass

    loans[uid]["overdue"] = True


# ================= VAY NGƯỜI CHƠI =================

@bot.command()
async def vay(ctx, member: discord.Member, amount: int):
    x = user(ctx.author.id)

    if member.bot:
        return await ctx.send("❌ Không thể vay bot/người máy.")

    if member.id == ctx.author.id:
        return await ctx.send("❌ Không thể tự vay chính mình.")

    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Người cho vay không đủ tiền.")

    x["money"] -= amount
    user(member.id)["money"] += amount

    loans[member.id] = {
        "bot": False,
        "amount": amount,
        "lender": ctx.author.id,
        "borrower": member.id,
        "due": datetime.utcnow() + timedelta(hours=1)
    }

    await ctx.send(embed=card(
        "🤝 VAY NGƯỜI CHƠI",
        f"""👤 Người vay: {member.mention}
🤝 Người cho vay: {ctx.author.mention}

💰 Khoản vay: `{cash(amount)}`
⏱️ Hạn trả: `1 giờ`

⚠️ Quá hạn sẽ nhận **Nợ xấu**."""
    ))

    asyncio.create_task(check_player_debt(ctx.guild, member.id))


async def check_player_debt(guild, uid):
    await asyncio.sleep(3600)

    loan = loans.get(uid)

    if not loan or loan.get("bot"):
        return

    member = guild.get_member(uid)

    if member:
        role = discord.utils.get(guild.roles, name=bad_debt_role)

        if role is None:
            try:
                role = await guild.create_role(
                    name=bad_debt_role,
                    reason="BET88 - người chơi quá hạn khoản vay"
                )
            except discord.Forbidden:
                return

        try:
            await member.add_roles(role)
        except discord.Forbidden:
            pass

        x = user(uid)
        x["luck"] = max(0, x["luck"] - 1)


# ================= TRẢ NỢ =================

@bot.command()
async def trano(ctx):
    uid = ctx.author.id
    loan = loans.get(uid)

    if not loan:
        return await ctx.send("❌ Bạn không có khoản nợ.")

    x = user(uid)
    amount = loan["amount"]

    if amount > x["money"]:
        return await ctx.send(
            f"❌ Bạn cần `{cash(amount)}` để trả nợ."
        )

    x["money"] -= amount

    if loan.get("bot"):
        del loans[uid]

        try:
            if ctx.guild:
                member = ctx.guild.get_member(uid)
                if member:
                    name = member.display_name.replace("Con Nợ | ", "")
                    await member.edit(nick=name)
        except discord.Forbidden:
            pass

        await ctx.send(embed=card(
            "💵 TRẢ NỢ BOT",
            f"""✅ Đã trả: `{cash(amount)}`

🏦 Đã xóa khoản vay Bot.
💰 Ví còn: `{cash(x["money"])}`

🍀 Chúc anh em may mắn!"""
        ))
        return

    lender = loan["lender"]
    user(lender)["money"] += amount
    del loans[uid]

    role = discord.utils.get(ctx.guild.roles, name=bad_debt_role)

    if role and role in ctx.author.roles:
        try:
            await ctx.author.remove_roles(role)
        except discord.Forbidden:
            pass

    await ctx.send(embed=card(
        "💵 TRẢ NỢ",
        f"""✅ Đã trả: `{cash(amount)}`

🤝 Tiền đã chuyển cho người cho vay.
💰 Ví còn: `{cash(x["money"])}`

🍀 Chúc anh em may mắn!"""
    ))


# ================= ADMIN =================

def admin_only():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator

    return commands.check(predicate)


@bot.command()
@admin_only()
async def settien(ctx, member: discord.Member, amount: int):
    user(member.id)["money"] = max(0, amount)

    await ctx.send(
        f"💰 Đã đặt ví của {member.mention} thành `{cash(amount)}`."
    )


@bot.command()
@admin_only()
async def resettien(ctx, member: discord.Member):
    users[member.id] = {
        "money": 7500,
        "bank": 0,
        "luck": 100
    }

    await ctx.send(
        f"🔄 Đã reset tài khoản {member.mention}."
    )


@bot.command()
@admin_only()
async def tyle(ctx):
    await ctx.send(embed=card(
        "📊 TỶ LỆ",
        """🎲 Tài Xỉu: 1:1
🦀 Bầu Cua: 1:1
🪙 Xóc Đĩa: 1:1
🎰 Quay: tùy biểu tượng

🍀 May mắn ảnh hưởng các trò chơi."""
    ))


# ================= LỖI =================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "❌ Thiếu thông tin.\n"
            "Dùng `!trogiup` để xem lệnh."
        )

    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            "❌ Sai cú pháp hoặc số tiền.\n"
            "Dùng `!trogiup` để xem lệnh."
        )

    elif isinstance(error, commands.CheckFailure):
        await ctx.send("❌ Bạn không có quyền dùng lệnh này.")

    else:
        print("ERROR:", repr(error))


# ================= START =================

bot.run(TOKEN)
