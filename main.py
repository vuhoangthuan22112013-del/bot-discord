import os
import random
import asyncio
from datetime import datetime, timedelta

import discord
from discord.ext import commands

# ================= TOKEN =================

TOKEN = os.getenv("TOKEN_BOT")

if not TOKEN:
    raise RuntimeError(
        "❌ Chưa có TOKEN_BOT! "
        "Hãy tạo Environment Variable TOKEN_BOT trên Render."
    )

# ================= DISCORD =================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# ================= DATA =================

users = {}
loans = {}

tx = {
    "open": False,
    "bets": {}
}

BAD_DEBT_ROLE = "Nợ xấu"


# ================= HỖ TRỢ =================

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
    e = discord.Embed(
        title=title,
        description=text
    )
    e.set_footer(text="💎 BET88")
    return e


async def effect(ctx, title, text, seconds=1.5):
    msg = await ctx.send(
        embed=card(title, text)
    )
    await asyncio.sleep(seconds)
    return msg


# ================= READY =================

@bot.event
async def on_ready():
    print("=" * 40)
    print(f"✅ BOT ONLINE: {bot.user}")
    print(f"🆔 ID: {bot.user.id}")
    print("=" * 40)


# ================= TRỢ GIÚP =================

@bot.command()
async def trogiup(ctx):
    await ctx.send(embed=card(
        "💎 BET88 | MENU",
        """🎰 **TRÒ CHƠI**

🎲 `!tx` → Mở Tài Xỉu
🎯 `!tx tai 1000`
🦀 `!bc 1000`
🪙 `!xd chan 1000`
🎰 `!quay 1000`
✊ `!tuxi bao 1000`

💰 **TÀI KHOẢN**

💳 `!vi`
🎁 `!diemdanh`
🏦 `!gui 1000`
💸 `!rut 1000`
💱 `!chuyen @user 1000`

🏦 **VAY**

💰 `!vaybot 50000`
🤝 `!vay @user 50000`
💵 `!trano`

👑 **ADMIN**

💰 `!settien @user 100000`
🔄 `!resettien @user`
📊 `!tyle`

💎 Chúc anh em chơi vui!"""
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


# ================= ĐIỂM DANH =================

@bot.command()
async def diemdanh(ctx):
    x = user(ctx.author.id)

    reward = 2500
    x["money"] += reward

    await ctx.send(embed=card(
        "🎁 ĐIỂM DANH",
        f"""✨ **ĐIỂM DANH THÀNH CÔNG**

🎁 Nhận: `+{cash(reward)}`
💰 Ví: `{cash(x["money"])}`

🍀 Chúc may mắn!"""
    ))


# ================= NGÂN HÀNG =================

@bot.command()
async def gui(ctx, amount: int):
    x = user(ctx.author.id)

    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Số tiền không hợp lệ.")

    x["money"] -= amount
    x["bank"] += amount

    await ctx.send(embed=card(
        "🏦 GỬI TIỀN",
        f"""✅ Gửi thành công!

💰 Gửi: `{cash(amount)}`
👛 Ví: `{cash(x["money"])}`
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
        f"""✅ Rút thành công!

💰 Rút: `{cash(amount)}`
👛 Ví: `{cash(x["money"])}`
🏦 Ngân hàng: `{cash(x["bank"])}`"""
    ))


# ================= CHUYỂN TIỀN =================

@bot.command()
async def chuyen(ctx, member: discord.Member, amount: int):
    x = user(ctx.author.id)

    if member.bot:
        return await ctx.send("❌ Không thể chuyển cho bot.")

    if member.id == ctx.author.id:
        return await ctx.send("❌ Không thể chuyển cho chính mình.")

    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Không đủ tiền.")

    x["money"] -= amount
    user(member.id)["money"] += amount

    await ctx.send(embed=card(
        "💱 CHUYỂN TIỀN",
        f"""👤 Người nhận: {member.mention}
💰 Số tiền: `{cash(amount)}`

✅ Chuyển thành công!
👛 Ví còn: `{cash(x["money"])}`"""
    ))


# ================= TÀI XỈU =================

@bot.command()
async def tx(ctx, *args):

    # MỞ VÁN
    if not args:

        if tx["open"]:
            return await ctx.send("⚠️ Tài Xỉu đang mở.")

        tx["open"] = True
        tx["bets"] = {}

        await ctx.send(embed=card(
            "🎲 TÀI XỈU | 🔵 ĐANG MỞ",
            """🎯 Đặt cược:

`!tx tai 1000`
`!tx xiu 1000`

🔥 **TÀI**
❄️ **XỈU**

⏱️ Thời gian: **30 giây**
💰 Tối đa: **10,000,000$/ván**

🎮 Vào cược đi anh em!"""
        ))

        asyncio.create_task(finish_tx(ctx))
        return

    # ĐẶT CƯỢC
    if len(args) != 2:
        return await ctx.send(
            "❌ Dùng: `!tx tai 1000` hoặc `!tx xiu 1000`"
        )

    choice = args[0].lower()

    if choice not in ("tai", "xiu"):
        return await ctx.send(
            "❌ Chỉ chọn `tai` hoặc `xiu`."
        )

    try:
        amount = int(args[1])
    except ValueError:
        return await ctx.send("❌ Số tiền không hợp lệ.")

    x = user(ctx.author.id)

    if amount <= 0:
        return await ctx.send("❌ Số tiền phải lớn hơn 0.")

    if amount > 10_000_000:
        return await ctx.send("❌ Tối đa 10,000,000$/ván.")

    if amount > x["money"]:
        return await ctx.send("❌ Bạn không đủ tiền.")

    if not tx["open"]:
        return await ctx.send(
            "⚠️ Chưa có phiên Tài Xỉu."
        )

    if ctx.author.id in tx["bets"]:
        return await ctx.send(
            "⚠️ Bạn đã cược ván này."
        )

    x["money"] -= amount

    tx["bets"][ctx.author.id] = {
        "choice": choice,
        "amount": amount,
        "name": ctx.author.mention
    }

    await ctx.send(embed=card(
        "🎯 ĐẶT CƯỢC",
        f"""👤 {ctx.author.mention}

🎲 Cửa: **{choice.upper()}**
💰 Cược: `{cash(amount)}`

🔥 Chúc may mắn!"""
    ))


async def finish_tx(ctx):

    await asyncio.sleep(30)

    if not tx["open"]:
        return

    dice = [
        random.randint(1, 6),
        random.randint(1, 6),
        random.randint(1, 6)
    ]

    total = sum(dice)

    result = "tai" if total >= 11 else "xiu"

    winners = []

    for uid, bet in tx["bets"].items():

        if bet["choice"] == result:

            win = bet["amount"] * 2

            user(uid)["money"] += win

            winners.append(
                f"🏆 {bet['name']} `+{cash(win)}`"
            )

        else:

            winners.append(
                f"❌ {bet['name']} `-{cash(bet['amount'])}`"
            )

    text = (
        f"🎲 `[ {dice[0]} ] [ {dice[1]} ] [ {dice[2]} ]`\n\n"
        f"💥 **TỔNG: {total}**\n\n"
        f"{'🔥 TÀI' if result == 'tai' else '❄️ XỈU'}\n\n"
    )

    if winners:
        text += "\n".join(winners)
    else:
        text += "👥 Không có người chơi."

    await ctx.send(embed=card(
        "🎲 KẾT QUẢ | 🔴 ĐÃ ĐÓNG",
        text
    ))

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
        "🦀 BẦU CUA | 🟠 ĐANG LẮC",
        f"""🎯 Cược: `{cash(amount)}`

╔════════════╗
║ 🦀  LẮC... ║
║ 🐟  LẮC... ║
║ 🐓  LẮC... ║
╚════════════╝"""
    ))

    await asyncio.sleep(2)

    icons = ["🍐", "🦀", "🐟", "🦐", "🦌", "🐓"]

    result = random.choices(icons, k=3)

    await ctx.send(embed=card(
        "🦀 BẦU CUA | 🟢 KẾT QUẢ",
        f"""🎲 **KẾT QUẢ**

# {result[0]}   {result[1]}   {result[2]}

🎉 Ván đã kết thúc!"""
    ))


# ================= XÓC ĐĨA =================

@bot.command()
async def xd(ctx, choice: str, amount: int):

    choice = choice.lower()

    if choice not in ("chan", "le"):
        return await ctx.send(
            "❌ Chọn `chan` hoặc `le`."
        )

    x = user(ctx.author.id)

    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Không đủ tiền.")

    x["money"] -= amount

    await ctx.send(embed=card(
        "🪙 XÓC ĐĨA | 🟠 ĐANG XÓC",
        f"""🎯 Cửa: **{choice.upper()}**
💰 Cược: `{cash(amount)}`

🪙 Xóc...
🪙 Xóc...
🪙 Xóc..."""
    ))

    await asyncio.sleep(2)

    result = [
        random.choice(["🔴", "⚪"])
        for _ in range(4)
    ]

    is_chan = result.count("🔴") % 2 == 0

    result_text = "CHAN" if is_chan else "LE"

    await ctx.send(embed=card(
        "🪙 XÓC ĐĨA | 🟢 KẾT QUẢ",
        f"""# {result[0]}  {result[1]}  {result[2]}  {result[3]}

💥 Kết quả: **{result_text}**

🎉 Ván kết thúc!"""
    ))


# ================= QUAY =================

@bot.command()
async def quay(ctx, amount: int):

    x = user(ctx.author.id)

    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Không đủ tiền.")

    x["money"] -= amount

    await ctx.send(embed=card(
        "🎰 QUAY | 🟠 ĐANG QUAY",
        f"""🎯 Cược: `{cash(amount)}`

🎰 [ ❔ ] [ ❔ ] [ ❔ ]

⏳ Đang quay..."""
    ))

    await asyncio.sleep(1)

    icons = ["🍒", "7️⃣", "🍋", "💎"]

    result = random.choices(icons, k=3)

    await ctx.send(embed=card(
        "🎰 QUAY | 🟢 KẾT QUẢ",
        f"""# {result[0]}   {result[1]}   {result[2]}

🎉 Kết thúc!"""
    ))


# ================= TÙ XÌ =================

@bot.command()
async def tuxi(ctx, choice: str, amount: int):

    choice = choice.lower()

    if choice not in ("bao", "bua", "keo"):
        return await ctx.send(
            "❌ Chọn `bao`, `bua` hoặc `keo`."
        )

    x = user(ctx.author.id)

    if amount <= 0 or amount > x["money"]:
        return await ctx.send("❌ Không đủ tiền.")

    x["money"] -= amount

    bot_choice = random.choice(
        ["bao", "bua", "keo"]
    )

    await ctx.send(embed=card(
        "✊ TÙ XÌ",
        f"""👤 Bạn: **{choice.upper()}**
🤖 Bot: **{bot_choice.upper()}**

💰 Cược: `{cash(amount)}`"""
    ))


# ================= VAY BOT =================

@bot.command()
async def vaybot(ctx, amount: int):

    uid = ctx.author.id

    if amount < 1 or amount > 50_000:
        return await ctx.send(
            "❌ Bot cho vay từ 1$ đến 50,000$."
        )

    if uid in loans:
        return await ctx.send(
            "❌ Bạn đang có khoản vay."
        )

    user(uid)["money"] += amount

    loans[uid] = {
        "bot": True,
        "amount": amount,
        "due": datetime.utcnow() + timedelta(hours=1)
    }

    await ctx.send(embed=card(
        "🏦 VAY BOT",
        f"""👤 Người vay: {ctx.author.mention}

💰 Khoản vay: `{cash(amount)}`
⏱️ Hạn trả: **1 giờ**

🟢 **VAY THÀNH CÔNG**

💵 Trả bằng:
`!trano`"""
    ))


# ================= VAY NGƯỜI =================

@bot.command()
async def vay(ctx, member: discord.Member, amount: int):

    lender = user(ctx.author.id)

    if member.bot:
        return await ctx.send(
            "❌ Không thể vay bot."
        )

    if member.id == ctx.author.id:
        return await ctx.send(
            "❌ Không thể tự vay mình."
        )

    if amount <= 0 or amount > lender["money"]:
        return await ctx.send(
            "❌ Người cho vay không đủ tiền."
        )

    if member.id in loans:
        return await ctx.send(
            "❌ Người này đang có khoản vay."
        )

    lender["money"] -= amount
    user(member.id)["money"] += amount

    loans[member.id] = {
        "bot": False,
        "amount": amount,
        "lender": ctx.author.id,
        "due": datetime.utcnow() + timedelta(hours=1)
    }

    await ctx.send(embed=card(
        "🤝 VAY NGƯỜI CHƠI",
        f"""👤 Người vay: {member.mention}
🤝 Người cho vay: {ctx.author.mention}

💰 Khoản vay: `{cash(amount)}`
⏱️ Hạn trả: **1 giờ**

⚠️ Quá hạn sẽ nhận **Nợ xấu**."""
    ))


# ================= TRẢ NỢ =================

@bot.command()
async def trano(ctx):

    uid = ctx.author.id

    loan = loans.get(uid)

    if not loan:
        return await ctx.send(
            "❌ Bạn không có khoản nợ."
        )

    x = user(uid)
    amount = loan["amount"]

    if amount > x["money"]:
        return await ctx.send(
            f"❌ Bạn cần `{cash(amount)}`."
        )

    x["money"] -= amount

    if loan.get("bot"):

        del loans[uid]

        await ctx.send(embed=card(
            "💵 TRẢ NỢ BOT",
            f"""✅ Đã trả: `{cash(amount)}`

🏦 Khoản vay đã được xóa.
💰 Ví còn: `{cash(x["money"])}`"""
        ))

        return

    lender = loan["lender"]

    user(lender)["money"] += amount

    del loans[uid]

    await ctx.send(embed=card(
        "💵 TRẢ NỢ",
        f"""✅ Đã trả: `{cash(amount)}`

🤝 Tiền đã chuyển cho người cho vay.
💰 Ví còn: `{cash(x["money"])}`"""
    ))


# ================= ADMIN =================

def admin_only():
    async def predicate(ctx):
        return (
            ctx.guild is not None
            and ctx.author.guild_permissions.administrator
        )

    return commands.check(predicate)


@bot.command()
@admin_only()
async def settien(ctx, member: discord.Member, amount: int):

    if amount < 0:
        return await ctx.send(
            "❌ Số tiền không hợp lệ."
        )

    user(member.id)["money"] = amount

    await ctx.send(
        f"💰 {member.mention} → `{cash(amount)}`"
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
        f"🔄 Đã reset {member.mention}."
    )


@bot.command()
@admin_only()
async def tyle(ctx):

    await ctx.send(embed=card(
        "📊 TỶ LỆ BET88",
        """🎲 Tài Xỉu: **1:1**
🦀 Bầu Cua: **1:1**
🪙 Xóc Đĩa: **1:1**
🎰 Quay: **ngẫu nhiên**

💎 BET88"""
    ))


# ================= LỖI =================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(
        error,
        commands.CommandNotFound
    ):
        return

    if isinstance(
        error,
        commands.MissingRequiredArgument
    ):
        return await ctx.send(
            "❌ Thiếu thông tin.\n"
            "Dùng `!trogiup`."
        )

    if isinstance(
        error,
        commands.BadArgument
    ):
        return await ctx.send(
            "❌ Sai cú pháp hoặc số tiền.\n"
            "Dùng `!trogiup`."
        )

    if isinstance(
        error,
        commands.CheckFailure
    ):
        return await ctx.send(
            "❌ Bạn không có quyền."
        )

    print("ERROR:", repr(error))


# ================= START =================

bot.run(TOKEN)
