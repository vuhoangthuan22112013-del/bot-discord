import os
import json
import random
import asyncio
from datetime import date

import discord
from discord.ext import commands

# =========================
# CONFIG
# =========================

TOKEN = os.getenv("BOT_TOKEN")

START_MONEY = 10000
MIN_BET = 100
MAX_BET = 1_000_000
BET_TIME = 30
DATA_FILE = "data.json"

# =========================
# DISCORD
# =========================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# =========================
# DATABASE
# =========================

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


users = load_data()


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def get_user(user_id):
    uid = str(user_id)

    if uid not in users:
        users[uid] = {
            "money": START_MONEY,
            "wins": 0,
            "losses": 0,
            "daily": None
        }
        save_data()

    return users[uid]


def fmt(number):
    return f"{number:,}".replace(",", ".")


# =========================
# GAME
# =========================

game = {
    "active": False,
    "channel": None,
    "bets": {}
}


# =========================
# READY
# =========================

@bot.event
async def on_ready():
    print(f"ONLINE: {bot.user}")


# =========================
# BALANCE
# =========================

@bot.command(name="balance")
async def balance(ctx):

    user = get_user(ctx.author.id)

    embed = discord.Embed(
        title="💰 SỐ DƯ",
        description=(
            f"👤 {ctx.author.mention}\n\n"
            f"💵 **{fmt(user['money'])} xu**"
        ),
        color=discord.Color.gold()
    )

    await ctx.send(embed=embed)


# =========================
# DAILY
# =========================

@bot.command(name="daily")
async def daily(ctx):

    user = get_user(ctx.author.id)
    today = str(date.today())

    if user["daily"] == today:
        await ctx.send(
            f"⏳ {ctx.author.mention}, hôm nay bạn đã nhận Daily rồi!"
        )
        return

    reward = random.randint(1000, 5000)

    user["money"] += reward
    user["daily"] = today

    save_data()

    embed = discord.Embed(
        title="🎁 DAILY",
        description=(
            f"🎉 {ctx.author.mention}\n\n"
            f"💰 Nhận được: **+{fmt(reward)} xu**\n"
            f"💵 Số dư: **{fmt(user['money'])} xu**"
        ),
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)


# =========================
# TOP
# =========================

@bot.command(name="top")
async def top(ctx):

    ranking = sorted(
        users.items(),
        key=lambda x: x[1].get("money", 0),
        reverse=True
    )

    embed = discord.Embed(
        title="🏆 BẢNG XẾP HẠNG",
        color=discord.Color.blurple()
    )

    if not ranking:
        embed.description = "Chưa có người chơi."
        await ctx.send(embed=embed)
        return

    lines = []

    for i, (uid, data) in enumerate(ranking[:10], 1):

        member = ctx.guild.get_member(int(uid))

        if member:
            name = member.display_name
        else:
            name = f"User {uid}"

        lines.append(
            f"**#{i}** {name}\n"
            f"💰 {fmt(data.get('money', 0))} xu"
        )

    embed.description = "\n\n".join(lines)

    await ctx.send(embed=embed)


# =========================
# TAIXIU
# =========================

@bot.command(name="taixiu", aliases=["tx"])
async def taixiu(ctx):

    if game["active"]:
        await ctx.send("⚠️ Đang có một phiên Tài Xỉu!")
        return

    game["active"] = True
    game["channel"] = ctx.channel.id
    game["bets"] = {}

    embed = discord.Embed(
        title="🎲 TÀI XỈU",
        description=(
            "╔════════════════════╗\n"
            "      🎰 **PHIÊN MỚI**\n"
            "╚════════════════════╝\n\n"
            "🟢 **TÀI** — Tổng 11 → 17\n"
            "🔴 **XỈU** — Tổng 4 → 10\n\n"
            f"⏳ Thời gian cược: **{BET_TIME} giây**\n\n"
            "💰 Đặt cược:\n"
            "`!cuoc tai 1000`\n"
            "`!cuoc xiu 1000`"
        ),
        color=discord.Color.blurple()
    )

    message = await ctx.send(embed=embed)

    for remaining in range(BET_TIME, 0, -1):

        embed.description = (
            "╔════════════════════╗\n"
            "      🎰 **TÀI XỈU**\n"
            "╚════════════════════╝\n\n"
            "🟢 **TÀI**\n"
            "🔴 **XỈU**\n\n"
            f"⏳ Còn **{remaining} giây**!\n\n"
            "💰 Đặt cược:\n"
            "`!cuoc tai 1000`\n"
            "`!cuoc xiu 1000`"
        )

        if remaining <= 10:
            embed.color = discord.Color.red()

        try:
            await message.edit(embed=embed)
        except:
            pass

        await asyncio.sleep(1)

    await finish_game(ctx.channel)


# =========================
# BET
# =========================

@bot.command(name="cuoc", aliases=["bet"])
async def bet(ctx, choice=None, amount=None):

    if not game["active"]:
        await ctx.send("❌ Chưa có phiên Tài Xỉu.")
        return

    if choice is None or amount is None:
        await ctx.send(
            "❌ Dùng:\n"
            "`!cuoc tai 1000`\n"
            "`!cuoc xiu 1000`"
        )
        return

    choice = choice.lower()

    if choice not in ("tai", "xiu"):
        await ctx.send("❌ Chỉ được chọn `tai` hoặc `xiu`.")
        return

    try:
        amount = int(amount)
    except:
        await ctx.send("❌ Số tiền không hợp lệ.")
        return

    if amount < MIN_BET:
        await ctx.send(
            f"❌ Cược tối thiểu **{fmt(MIN_BET)} xu**."
        )
        return

    if amount > MAX_BET:
        await ctx.send(
            f"❌ Cược tối đa **{fmt(MAX_BET)} xu**."
        )
        return

    user = get_user(ctx.author.id)
    uid = str(ctx.author.id)

    # Nếu người chơi đã cược,
    # hoàn lại cược cũ trước khi thay cược mới.
    if uid in game["bets"]:
        old = game["bets"][uid]
        user["money"] += old["amount"]

    if user["money"] < amount:
        await ctx.send(
            f"❌ Không đủ xu.\n"
            f"💰 Bạn có **{fmt(user['money'])} xu**."
        )
        return

    user["money"] -= amount

    game["bets"][uid] = {
        "name": ctx.author.display_name,
        "choice": choice,
        "amount": amount
    }

    save_data()

    emoji = "🟢" if choice == "tai" else "🔴"

    embed = discord.Embed(
        title="✅ ĐẶT CƯỢC",
        description=(
            f"👤 {ctx.author.mention}\n\n"
            f"{emoji} Cửa: **{choice.upper()}**\n"
            f"💰 Cược: **{fmt(amount)} xu**\n"
            f"💵 Còn lại: **{fmt(user['money'])} xu**"
        ),
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)


# =========================
# RESULT
# =========================

async def finish_game(channel):

    dice = [
        random.randint(1, 6),
        random.randint(1, 6),
        random.randint(1, 6)
    ]

    total = sum(dice)

    if total >= 11:
        result = "tai"
        result_name = "TÀI"
        result_emoji = "🟢"
        color = discord.Color.green()
    else:
        result = "xiu"
        result_name = "XỈU"
        result_emoji = "🔴"
        color = discord.Color.red()

    dice_box = (
        f"╔══ 🎲 ══╗   ╔══ 🎲 ══╗   ╔══ 🎲 ══╗\n"
        f"║   **{dice[0]}**   ║   ║   **{dice[1]}**   ║   ║   **{dice[2]}**   ║\n"
        f"╚════════╝   ╚════════╝   ╚════════╝"
    )

    winners = []
    losers = []

    for uid, bet_data in game["bets"].items():

        user = get_user(uid)
        amount = bet_data["amount"]

        if bet_data["choice"] == result:

            reward = amount * 2
            user["money"] += reward
            user["wins"] += 1

            winners.append(
                f"🟢 {bet_data['name']}  +{fmt(amount)} xu"
            )

        else:

            user["losses"] += 1

            losers.append(
                f"🔴 {bet_data['name']}  -{fmt(amount)} xu"
            )

    save_data()

    embed = discord.Embed(
        title="🎰 KẾT QUẢ TÀI XỈU",
        description=(
            "╔══════════════════════════╗\n"
            "          🎲 **KẾT QUẢ**\n"
            "╚══════════════════════════╝\n\n"
            f"{dice_box}\n\n"
            f"➕ Tổng: **{total}**\n\n"
            f"{result_emoji} KẾT QUẢ: **{result_name}**\n"
        ),
        color=color
    )

    if winners:
        embed.add_field(
            name="🏆 THẮNG",
            value="\n".join(winners[:10]),
            inline=False
        )

    if losers:
        embed.add_field(
            name="💀 THUA",
            value="\n".join(losers[:10]),
            inline=False
        )

    embed.set_footer(
        text="🎲 Tài Xỉu • Phiên mới: !taixiu"
    )

    await channel.send(embed=embed)

    game["active"] = False
    game["channel"] = None
    game["bets"] = {}


# =========================
# ADMIN
# =========================

@bot.command(name="addmoney")
@commands.has_permissions(administrator=True)
async def addmoney(ctx, member: discord.Member = None, amount: int = None):

    if member is None or amount is None:
        await ctx.send("❌ Dùng: `!addmoney @user 10000`")
        return

    if amount <= 0:
        await ctx.send("❌ Số tiền phải lớn hơn 0.")
        return

    user = get_user(member.id)
    user["money"] += amount

    save_data()

    await ctx.send(
        f"✅ Đã cộng **{fmt(amount)} xu** cho {member.mention}."
    )


@bot.command(name="removemoney")
@commands.has_permissions(administrator=True)
async def removemoney(ctx, member: discord.Member = None, amount: int = None):

    if member is None or amount is None:
        await ctx.send("❌ Dùng: `!removemoney @user 10000`")
        return

    if amount <= 0:
        await ctx.send("❌ Số tiền phải lớn hơn 0.")
        return

    user = get_user(member.id)
    user["money"] = max(0, user["money"] - amount)

    save_data()

    await ctx.send(
        f"✅ Đã trừ **{fmt(amount)} xu** của {member.mention}."
    )


# =========================
# HELP
# =========================

@bot.command(name="helpme")
async def helpme(ctx):

    embed = discord.Embed(
        title="🎲 BOT TÀI XỈU",
        description=(
            "**🎰 TRÒ CHƠI**\n"
            "`!taixiu` — Mở phiên\n"
            "`!cuoc tai 1000` — Cược Tài\n"
            "`!cuoc xiu 1000` — Cược Xỉu\n\n"
            "**💰 TIỀN**\n"
            "`!balance` — Xem xu\n"
            "`!daily` — Nhận xu mỗi ngày\n"
            "`!top` — Bảng xếp hạng\n\n"
            "**👑 ADMIN**\n"
            "`!addmoney @user 10000`\n"
            "`!removemoney @user 10000`"
        ),
        color=discord.Color.blurple()
    )

    await ctx.send(embed=embed)


# =========================
# ERROR
# =========================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bạn không có quyền dùng lệnh này.")

    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Không tìm thấy người chơi.")

    elif isinstance(error, commands.CommandNotFound):
        pass

    else:
        print("ERROR:", error)


# =========================
# START
# =========================

if not TOKEN:
    raise RuntimeError(
        "Chưa đặt biến môi trường BOT_TOKEN!"
    )

bot.run(TOKEN)
