import os
import random
import asyncio
import discord
from discord.ext import commands

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("Chưa có BOT_TOKEN trong Secrets/Environment Variables!")

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


@bot.event
async def on_ready():
    print(f"✅ BOT ONLINE: {bot.user}")
    print("🎮 Gõ !help để xem menu")


@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(
        title="🎰 CASINO GIẢI TRÍ 🎰",
        description="💰 Sử dụng tiền ảo trong bot",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="🎲 CASINO",
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
        name="🏦 HỆ THỐNG",
        value=(
            "`!vi` — Xem tiền\n"
            "`!daily` — Nhận tiền\n"
            "`!bxh` — Bảng xếp hạng"
        ),
        inline=False
    )

    await ctx.send(embed=embed)


@bot.command(name="vi")
async def vi(ctx):
    money = get_money(ctx.author.id)

    await ctx.send(
        f"💳 **VÍ CỦA {ctx.author.display_name}**\n"
        f"💰 Tiền ảo: `{money:,}`"
    )


@bot.command(name="daily")
async def daily(ctx):
    users[ctx.author.id] = get_money(ctx.author.id) + 1000

    await ctx.send(
        f"🎁 {ctx.author.mention} nhận **1,000 tiền ảo**!"
    )


@bot.command(name="tx", aliases=["taixiu"])
async def tx(ctx, choice=None, bet=None):

    if choice not in ("tai", "xiu"):
        return await ctx.send(
            "❌ Dùng: `!tx tai 100` hoặc `!tx xiu 100`"
        )

    try:
        bet = int(bet)
    except (TypeError, ValueError):
        return await ctx.send("❌ Tiền cược phải là số!")

    if bet <= 0:
        return await ctx.send("❌ Tiền cược phải lớn hơn 0!")

    money = get_money(ctx.author.id)

    if money < bet:
        return await ctx.send("❌ Bạn không đủ tiền ảo!")

    msg = await ctx.send(
        "🎲 **TÀI XỈU**\n"
        "[ ❔ ] [ ❔ ] [ ❔ ]\n"
        "⏳ Đang lắc..."
    )

    await asyncio.sleep(1)

    dice = [
        random.randint(1, 6),
        random.randint(1, 6),
        random.randint(1, 6)
    ]

    total = sum(dice)
    result = "tai" if total >= 11 else "xiu"
    result_text = "TÀI 🔴" if result == "tai" else "XỈU 🔵"

    if choice == result:
        users[ctx.author.id] += bet
        status = f"🎉 **THẮNG!** +`{bet:,}` tiền ảo"
    else:
        users[ctx.author.id] -= bet
        status = f"💸 **THUA!** -`{bet:,}` tiền ảo"

    await msg.edit(
        content=(
            "🎲 **TÀI XỈU**\n\n"
            f"[ **{dice[0]}** ] [ **{dice[1]}** ] [ **{dice[2]}** ]\n\n"
            f"➕ Tổng: **{total}**\n"
            f"🎯 Kết quả: **{result_text}**\n\n"
            f"{status}"
        )
    )


@bot.command(name="quay")
async def quay(ctx, bet=None):

    try:
        bet = int(bet)
    except (TypeError, ValueError):
        return await ctx.send("❌ Dùng: `!quay 100`")

    if bet <= 0:
        return await ctx.send("❌ Tiền cược phải lớn hơn 0!")

    money = get_money(ctx.author.id)

    if money < bet:
        return await ctx.send("❌ Bạn không đủ tiền ảo!")

    msg = await ctx.send(
        "🎰 **SLOT**\n"
        "[ ❔ ] [ ❔ ] [ ❔ ]"
    )

    await asyncio.sleep(1)

    symbols = ["🍒", "🍋", "🔔", "💎"]

    result = [random.choice(symbols) for _ in range(3)]

    await msg.edit(
        content=(
            "🎰 **SLOT**\n"
            f"[ {result[0]} ] [ {result[1]} ] [ {result[2]} ]"
        )
    )

    if result[0] == result[1] == result[2]:
        prize = bet * 3
        users[ctx.author.id] += prize
        await ctx.send(f"💎 **JACKPOT!** +`{prize:,}` tiền ảo!")

    elif len(set(result)) < 3:
        users[ctx.author.id] += bet
        await ctx.send(f"✨ **THẮNG!** +`{bet:,}` tiền ảo!")

    else:
        users[ctx.author.id] -= bet
        await ctx.send(f"💸 **THUA!** -`{bet:,}` tiền ảo!")


@bot.command(name="coinflip")
async def coinflip(ctx, choice=None, bet=None):

    if choice not in ("ngua", "sap"):
        return await ctx.send(
            "❌ Dùng: `!coinflip ngua 100` hoặc `!coinflip sap 100`"
        )

    try:
        bet = int(bet)
    except (TypeError, ValueError):
        return await ctx.send("❌ Tiền cược phải là số!")

    if bet <= 0:
        return await ctx.send("❌ Tiền cược không hợp lệ!")

    money = get_money(ctx.author.id)

    if money < bet:
        return await ctx.send("❌ Bạn không đủ tiền ảo!")

    result = random.choice(["ngua", "sap"])

    if result == choice:
        users[ctx.author.id] += bet
        text = f"🪙 **{result.upper()}**\n🎉 Thắng `+{bet:,}` tiền ảo!"
    else:
        users[ctx.author.id] -= bet
        text = f"🪙 **{result.upper()}**\n💸 Thua `-{bet:,}` tiền ảo!"

    await ctx.send(text)


@bot.command(name="bxh")
async def bxh(ctx):

    if not users:
        return await ctx.send("🏆 Chưa có người chơi.")

    ranking = sorted(
        users.items(),
        key=lambda item: item[1],
        reverse=True
    )

    text = "🏆 **BẢNG XẾP HẠNG**\n\n"

    for i, (user_id, money) in enumerate(ranking[:10], 1):
        member = ctx.guild.get_member(user_id)
        name = member.display_name if member else "Người chơi"

        text += f"**{i}.** {name} — `{money:,}` 💰\n"

    await ctx.send(text)


@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CommandNotFound):
        await ctx.send(
            "❌ Không có lệnh này. Gõ `!help` để xem menu."
        )

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "❌ Thiếu thông tin. Gõ `!help` để xem cách dùng."
        )

    else:
        print(f"❌ Lỗi: {error}")


print("🔄 Đang khởi động bot...")

bot.run(BOT_TOKEN)
