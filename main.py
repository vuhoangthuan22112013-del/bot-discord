import asyncio
import random
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
users = {}

def get_user(uid):
    if uid not in users:
        users[uid] = {"cash": 10000, "bank": 0}
    return users[uid]

@bot.event
async def on_ready():
    print(f"✅ BOT ONLINE: {bot.user}", flush=True)

@bot.command(name="vi", aliases=["money", "bal"])
async def check_vi(ctx):
    u = get_user(ctx.author.id)
    await ctx.send(f"💰 **Tài sản của {ctx.author.name}:**\n💵 Tiền mặt: **{u['cash']:,}** tiền\n🏦 Ngân hàng: **{u['bank']:,}** tiền")

@bot.command(name="diemdanh")
async def daily(ctx):
    u = get_user(ctx.author.id)
    thuong = random.randint(1000, 3000)
    u["cash"] += thuong
    await ctx.send(f"🎁 **{ctx.author.name}** đã nhận **+{thuong:,}** tiền điểm danh!\n💵 Tiền mặt hiện tại: **{u['cash']:,}** tiền.")

@bot.command(name="tx")
async def taixiu(ctx, lua_chon: str = None, tien: int = 0):
    u = get_user(ctx.author.id)
    if not lua_chon or lua_chon.lower() not in ["tai", "xiu"] or tien <= 0:
        await ctx.send("⚠️ Cú pháp đúng: `!tx tai 2000` hoặc `!tx xiu 2000`!")
        return
    if tien > u["cash"]:
        await ctx.send("❌ Bạn không đủ tiền mặt!")
        return
    d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
    tong = d1 + d2 + d3
    kq = "tai" if tong >= 11 else "xiu"
    msg = f"🎲 Kết quả: **{d1}-{d2}-{d3}** (Tổng **{tong}** -> **{kq.upper()}**)\n"
    if lua_chon.lower() == kq:
        u["cash"] += tien
        msg += f"🎉 Bạn đã thắng **+{tien:,}** tiền!"
    else:
        u["cash"] -= tien
        msg += f"💀 Bạn đã thua **-{tien:,}** tiền!"
    await ctx.send(msg)

@bot.command(name="coinflip")
async def coinflip(ctx, lua_chon: str = None, tien: int = 0):
    u = get_user(ctx.author.id)
    if not lua_chon or lua_chon.lower() not in ["ngua", "up"] or tien <= 0:
        await ctx.send("⚠️ Cú pháp đúng: `!coinflip ngua 2000`!")
        return
    if tien > u["cash"]:
        await ctx.send("❌ Bạn không đủ tiền mặt!")
        return
    kq = random.choice(["ngua", "up"])
    if lua_chon.lower() == kq:
        u["cash"] += tien
        await ctx.send(f"🪙 Ra mặt **{kq.upper()}**! 🎉 Bạn thắng **+{tien:,}** tiền!")
    else:
        u["cash"] -= tien
        await ctx.send(f"🪙 Ra mặt **{kq.upper()}**! 💀 Bạn thua **-{tien:,}** tiền!")

@bot.command(name="bxh")
async def leaderboard(ctx):
    if not users:
        await ctx.send("Chưa có dữ liệu người chơi!")
        return
    sorted_users = sorted(users.items(), key=lambda x: x[1]["cash"] + x[1]["bank"], reverse=True)
    embed = discord.Embed(title="🏆 BẢNG XẾP HẠNG ĐẠI PHÚ HÀO 🏆", color=discord.Color.gold())
    for idx, (uid, data) in enumerate(sorted_users[:5], 1):
        m = ctx.guild.get_member(uid)
        name = m.display_name if m else f"Người chơi ({uid})"
        embed.add_field(name=f"Top {idx}: {name}", value=f"💎 Tài sản: **{data['cash']+data['bank']:,}** tiền", inline=False)
    await ctx.send(embed=embed)

async def main():
    token = "MTUzNTg1NTE2NDcwMTgwNjY4Mw.GBIFu9.vk7u5qzcRAbTXP9NsbJfyNVvkdEEpagXDCmF90"
    while True:
        try:
            await bot.start(token)
        except Exception as e:
            print(f"🔄 Kết nối lại: {e}", flush=True)
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
