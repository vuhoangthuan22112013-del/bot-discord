import os
import asyncio
import random
import time
import discord
from discord.ext import commands

# =========================================================
# CẤU HÌNH BOT
# =========================================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# =========================================================
# DỮ LIỆU
# =========================================================

users = {}
cooldowns = {}
diemdanh_cooldowns = {}

tx_session = {
    "active": False,
    "msg": None,
    "bets": {},
    "total_tai": 0,
    "total_xiu": 0
}

# =========================================================
# TIỆN ÍCH
# =========================================================

def check_spam(user_id, cmd_name, limit_seconds=1.5):
    now = time.time()
    key = f"{user_id}_{cmd_name}"

    if key in cooldowns:
        diff = now - cooldowns[key]

        if diff < limit_seconds:
            return round(limit_seconds - diff, 1)

    cooldowns[key] = now
    return 0.0


def get_user(uid, name="Thành viên"):
    if uid not in users:
        users[uid] = {
            "name": name,
            "cash": 4899,
            "bank": 0,
            "hang": "Người chơi Thường",
            "ga": "Gà Công Nghiệp 🐥"
        }

    else:
        users[uid]["name"] = name

    return users[uid]


def fmt_money(number):
    return f"{number:,}$"


# =========================================================
# BOT ONLINE
# =========================================================

@bot.event
async def on_ready():
    print("====================================")
    print(f"BOT ONLINE: {bot.user}")
    print(f"SERVER: {len(bot.guilds)}")
    print("====================================")


# =========================================================
# MENU
# =========================================================

@bot.command(name="menu")
async def menu_cmd(ctx):

    embed = discord.Embed(
        title="🎰 CASINO BET88 🎰",
        description="**HỆ THỐNG TRÒ CHƠI & TIỆN ÍCH**",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="⚔️ ĐỐI KHÁNG",
        value=(
            "`!danhbai @user`\n"
            "`!thachdau @user`\n"
            "`!dagapvp @user`\n"
            "`!tuxipvp @user`"
        ),
        inline=False
    )

    embed.add_field(
        name="🎲 CASINO",
        value=(
            "`!tx` — Tài Xỉu\n"
            "`!xd chan 100` — Xóc Đĩa\n"
            "`!bc ca 100` — Bầu Cua\n"
            "`!quay 100` — Slot\n"
            "`!coinflip 100` — Tung Xu\n"
            "`!rl 100` — Roulette\n"
            "`!bai 100` — Bài\n"
            "`!daga 100` — Đá Gà\n"
            "`!tuxi 100` — Tú Xì\n"
            "`!duangua 100` — Đua Ngựa"
        ),
        inline=False
    )

    embed.add_field(
        name="💰 TÀI KHOẢN",
        value=(
            "`!vi` — Xem ví\n"
            "`!diemdanh` — Điểm danh\n"
            "`!gui 100` — Gửi ngân hàng\n"
            "`!rut 100` — Rút tiền\n"
            "`!chuyen @user 100` — Chuyển tiền\n"
            "`!bxh` — Bảng xếp hạng\n"
            "`!nhapcode CODE` — Nhập code"
        ),
        inline=False
    )

    embed.set_footer(
        text="🎰 Chúc bạn may mắn • Tiền trong bot là tiền ảo"
    )

    await ctx.send(embed=embed)


# =========================================================
# VÍ
# =========================================================

@bot.command(name="vi", aliases=["money", "bal"])
async def vi_cmd(ctx, member: discord.Member = None):

    target = member if member else ctx.author

    u = get_user(
        target.id,
        target.name
    )

    embed = discord.Embed(
        title="💳 THÔNG TIN TÀI KHOẢN",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="👤 Người chơi",
        value=target.mention,
        inline=False
    )

    embed.add_field(
        name="🏆 Hạng",
        value=u["hang"],
        inline=True
    )

    embed.add_field(
        name="🐥 Gà chiến",
        value=u["ga"],
        inline=True
    )

    embed.add_field(
        name="💵 Tiền mặt",
        value=f"`{fmt_money(u['cash'])}`",
        inline=False
    )

    embed.add_field(
        name="🏦 Ngân hàng",
        value=f"`{fmt_money(u['bank'])}`",
        inline=False
    )

    await ctx.send(embed=embed)


# =========================================================
# ĐIỂM DANH
# =========================================================

@bot.command(name="diemdanh")
async def diemdanh_cmd(ctx):

    cd = check_spam(
        ctx.author.id,
        "diemdanh",
        2
    )

    if cd > 0:
        return await ctx.send(
            f"⚠️ {ctx.author.mention} Đợi **{cd} giây**!"
        )

    user_id = ctx.author.id
    now = time.time()

    if (
        user_id in diemdanh_cooldowns
        and now - diemdanh_cooldowns[user_id] < 12 * 3600
    ):
        return await ctx.send(
            f"⚠️ {ctx.author.mention} "
            "Bạn đã điểm danh trong 12 giờ qua!"
        )

    diemdanh_cooldowns[user_id] = now

    reward = 2593

    u = get_user(
        user_id,
        ctx.author.name
    )

    u["cash"] += reward

    await ctx.send(
        f"🎁 {ctx.author.mention} Điểm danh thành công!\n"
        f"💵 Nhận được **+{fmt_money(reward)}**"
    )


# =========================================================
# SLOT
# =========================================================

@bot.command(name="quay")
async def quay_cmd(ctx, bet: int =
