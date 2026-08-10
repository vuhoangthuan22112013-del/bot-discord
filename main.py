import os
import random
import asyncio
import discord
from discord.ext import commands

# ==========================================
# LẤY TOKEN TỪ SECRET / ENVIRONMENT
# Tên Secret: TOKEN_BOT
# ==========================================

TOKEN = os.getenv("TOKEN_BOT")

if not TOKEN:
    print("❌ Không tìm thấy TOKEN_BOT!")
    print("👉 Hãy kiểm tra Secret/Environment Variable.")
    raise SystemExit


# ==========================================
# CẤU HÌNH DISCORD
# ==========================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

users = {}


# ==========================================
# TIỀN ẢO
# ==========================================

def get_money(user_id):

    if user_id not in users:
        users[user_id] = 5000

    return users[user_id]


# ==========================================
# BOT ONLINE
# ==========================================

@bot.event
async def on_ready():

    print("======================================")
    print("          🎰 BOT ĐÃ ONLINE")
    print("======================================")
    print(f"🤖 Bot: {bot.user}")
    print(f"🆔 ID: {bot.user.id}")
    print("🎮 Prefix: !")
    print("======================================")

    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(
            name="🎰 !help | Tiền ảo"
        )
    )


# ==========================================
# MENU
# ==========================================

@bot.command(name="help")
async def help_cmd(ctx):

    embed = discord.Embed(
        title="🎰 CASINO GIẢI TRÍ",
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


# ==========================================
# VÍ
# ==========================================

@bot.command(name="vi")
async def vi(ctx):

    money = get_money(ctx.author.id)

    await ctx.send(
        f"💳 **VÍ CỦA {ctx.author.display_name}**\n\n"
        f"💰 Tiền ảo: `{money:,}`"
    )


# ==========================================
# DAILY
# ==========================================

@bot.command(name="daily")
async def daily(ctx):

    users[ctx.author.id] = get_money(ctx.author.id) + 1000

    await ctx.send(
        f"🎁 {ctx.author.mention}\n"
        f"Bạn nhận được **1,000 tiền ảo**!"
    )


# ==========================================
# TÀI XỈU
# ==========================================

@bot.command(name="tx")
async def tx(ctx, choice=None, bet=None):

    if choice not in ["tai", "xiu"]:
        await ctx.send(
            "❌ Cách dùng:\n"
            "`!tx tai 100`\n"
            "`!tx xiu 100`"
        )
        return

    try:
        bet = int(bet)
    except:
        await ctx.send("❌ Tiền cược phải là số!")
        return

    if bet <= 0:
        await ctx.send("❌ Tiền cược phải lớn hơn 0!")
        return

    money = get_money(ctx.author.id)

    if money < bet:
        await ctx.send(
            f"❌ Bạn chỉ có `{money:,}` tiền ảo!"
        )
        return

    msg = await ctx.send(
        "🎲 **TÀI XỈU**\n\n"
        "[ ❔ ] [ ❔ ] [ ❔ ]\n\n"
        "⏳ Đang lắc..."
    )

    await asyncio.sleep(1)

    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    d3 = random.randint(1, 6)

    total = d1 + d2 + d3

    result = "tai" if total >= 11 else "xiu"

    if choice == result:

        users[ctx.author.id] += bet

        status = (
            f"🎉 **THẮNG!**\n"
            f"💰 +`{bet:,}` tiền ảo"
        )

    else:

        users[ctx.author.id] -= bet

        status = (
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
            f"{status}"
        )
    )


# ==========================================
# SLOT
# ==========================================

@bot.command(name="quay")
async def quay(ctx, bet=None):

    try:
        bet = int(bet)
    except:
        await ctx.send("❌ Dùng: `!quay 100`")
        return

    if bet <= 0:
        await ctx.send("❌ Tiền cược không hợp lệ!")
        return

    money = get_money(ctx.author.id)

    if money < bet:
        await ctx.send("❌ Bạn không đủ tiền ảo!")
        return

    msg = await ctx.send(
        "🎰 **SLOT**\n"
        "[ ❔ ] [ ❔ ] [ ❔ ]"
    )

    await asyncio.sleep(1)

    symbols = ["🍒", "🍋", "🔔", "💎"]

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


# ==========================================
# BẢNG XẾP HẠNG
# ==========================================

@bot.command(name="bxh")
async def bxh(ctx):

    if not users:
        await ctx.send("🏆 Chưa có người chơi!")
        return

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

        if member:
            name = member.display_name
        else:
            name = "Người chơi"

        text += (
            f"**{i}.** {name} "
           
