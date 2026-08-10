import os
import asyncio
import random
import discord
from discord.ext import commands

# ==============================
# TOKEN
# ==============================

TOKEN = os.getenv("BOT_TOKEN")

# ==============================
# DISCORD BOT
# ==============================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

users = {}


def get_money(user_id):
    if user_id not in users:
        users[user_id] = 5000
    return users[user_id]


# ==============================
# BOT TỰ ONLINE
# ==============================

@bot.event
async def on_ready():
    print("================================")
    print("🤖 BOT ĐÃ ONLINE")
    print(f"👤 {bot.user}")
    print(f"🆔 {bot.user.id}")
    print("🎮 Prefix: !")
    print("================================")

    # Đặt trạng thái Online/đang chơi
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(
            name="🎰 !help | Tiền ảo"
        )
    )


# ==============================
# MENU
# ==============================

@bot.command(name="help")
async def help_cmd(ctx):

    embed = discord.Embed(
        title="🎰 CASINO GIẢI TRÍ 🎰",
        description="💰 Hệ thống tiền ảo",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="🎲 TRÒ CHƠI",
        value=(
            "`!tx tai 100`\n"
            "`!tx xiu 100`\n"
            "`!quay 100`\n"
            "`!coinflip ngua 100`\n"
            "`!coinflip sap 100`"
        ),
        inline=False
    )

    embed.add_field(
        name="💰 HỆ THỐNG",
        value=(
            "`!vi` — Xem tiền\n"
            "`!daily` — Nhận tiền\n"
            "`!bxh` — Bảng xếp hạng"
        ),
        inline=False
    )

    await ctx.send(embed=embed)


# ==============================
# VÍ
# ==============================

@bot.command(name="vi")
async def vi(ctx):

    money = get_money(ctx.author.id)

    await ctx.send(
        f"💳 **VÍ CỦA {ctx.author.display_name}**\n\n"
        f"💰 Tiền ảo: `{money:,}`"
    )


# ==============================
# DAILY
# ==============================

@bot.command(name="daily")
async def daily(ctx):

    users[ctx.author.id] = get_money(ctx.author.id) + 1000

    await ctx.send(
        f"🎁 {ctx.author.mention}\n"
        f"Bạn nhận được **1,000 tiền ảo**!"
    )


# ==============================
# TÀI XỈU
# ==============================

@bot.command(name="tx")
async def tx(ctx, choice=None, bet=None):

    if choice not in ["tai", "xiu"]:
        return await ctx.send(
            "❌ Dùng: `!tx tai 100` hoặc `!tx xiu 100`"
        )

    try:
        bet = int(bet)
    except:
        return await ctx.send(
            "❌ Tiền cược phải là số!"
        )

    if bet <= 0:
        return await ctx.send(
            "❌ Tiền cược phải lớn hơn 0!"
        )

    money = get_money(ctx.author.id)

    if money < bet:
        return await ctx.send(
            "❌ Bạn không đủ tiền ảo!"
        )

    msg = await ctx.send(
        "🎲 **TÀI XỈU**\n\n"
        "[ ❔ ] [ ❔ ] [ ❔ ]\n"
        "⏳ Đang lắc..."
    )

    await asyncio.sleep(1)

    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    d3 = random.randint(1, 6)

    total = d1 + d2 + d3

    result = "tai" if total >= 11 else "xiu"

    if result == choice:

        users[ctx.author.id] += bet

        result_text = (
            f"🎉 **THẮNG!**\n"
            f"💰 +`{bet:,}` tiền ảo"
        )

    else:

        users[ctx.author.id] -= bet

        result_text = (
            f"💸 **THUA!**\n"
            f"💰 -`{bet:,}` tiền ảo"
        )

    await msg.edit(
        content=(
            "🎲 **TÀI XỈU**\n\n"
            f"[ **{d1}** ] "
            f"[ **{d2}** ] "
            f"[ **{d3}** ]\n\n"
            f"➕ Tổng: **{total}**\n"
            f"🎯 Kết quả: **{result.upper()}**\n\n"
            f"{result_text}"
        )
    )


# ==============================
# SLOT
# ==============================

@bot.command(name="quay")
async def quay(ctx, bet=None):

    try:
        bet = int(bet)
    except:
        return await ctx.send(
            "❌ Dùng: `!quay 100`"
        )

    if bet <= 0:
        return await ctx.send(
            "❌ Tiền cược không hợp lệ!"
        )

    money = get_money(ctx.author.id)

    if money < bet:
        return await ctx.send(
            "❌ Bạn không đủ tiền ảo!"
        )

    symbols = ["🍒", "🍋", "🔔", "💎"]

    msg = await ctx.send(
        "🎰 **SLOT**\n"
        "[ ❔ ] [ ❔ ] [ ❔ ]"
    )

    await asyncio.sleep(1)

    a = random.choice(symbols)
    b = random.choice(symbols)
    c = random.choice(symbols)

    await msg.edit(
        content=(
            "🎰 **SLOT**\n"
            f"[ {a} ] [ {b} ] [ {c} ]"
        )
    )

    if a == b == c:

        win = bet * 3
        users[ctx.author.id] += win

        await ctx.send(
            f"💎 **JACKPOT!** +`{win:,}` tiền ảo!"
        )

    elif a == b or b == c or a == c:

        users[ctx.author.id] += bet

        await ctx.send(
            f"✨ **THẮNG!** +`{bet:,}` tiền ảo!"
        )

    else:

        users[ctx.author.id] -= bet

        await ctx.send(
            f"💸 **THUA!** -`{bet:,}` tiền ảo!"
        )


# ==============================
# BẢNG XẾP HẠNG
# ==============================

@bot.command(name="bxh")
async def bxh(ctx):

    ranking = sorted(
        users.items(),
        key=lambda x: x[1],
        reverse=True
    )

    text = "🏆 **BẢNG XẾP HẠNG**\n\n"

    for i, (user_id, money) in enumerate(
        ranking[:10],
        1
    ):

        member = ctx.guild.get_member(user_id)

        name = (
            member.display_name
            if member
            else "Người chơi"
        )

        text += (
            f"**{i}.** {name} "
            f"— `{money:,}` 💰\n"
        )

    await ctx.send(text)


# ==============================
# KHỞI ĐỘNG
# ==============================

if not TOKEN:
    print("❌ CHƯA CÓ BOT_TOKEN!")
    print("👉 Hãy thêm BOT_TOKEN vào Environment Variables.")

else:
    print("🔄 Đang đăng nhập Discord...")
    bot.run(BOT_TOKEN)
