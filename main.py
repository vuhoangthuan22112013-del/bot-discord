import asyncio
import random
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
users = {}

def get_user(uid):
    if uid not in users:
        users[uid] = {"cash": 10000, "bank": 0}
    return users[uid]

@bot.event
async def on_ready():
    print(f"✅ BOT ONLINE: {bot.user}")

@bot.command(name="vi", aliases=["money", "bal"])
async def check_vi(ctx):
    u = get_user(ctx.author.id)
    await ctx.send(f"💰 **Tài sản của {ctx.author.name}:**\n- Tiền mặt: `{u['cash']:,}` $\n- Ngân hàng: `{u['bank']:,}` $")

@bot.command(name="diemdanh", aliases=["daily"])
async def diem_danh(ctx):
    u = get_user(ctx.author.id)
    reward = random.randint(5000, 20000)
    u["cash"] += reward
    await ctx.send(f"🎉 **{ctx.author.name}** đã điểm danh và nhận được `{reward:,}` $!")

# Token của bạn đã được cập nhật ở đây
token = "MTUzNTg1NTE2NDcwMTgwNjY4Mw.GDdGF4.uG_TSc9AVfx-Q9dki52eQRUjN8wn3dnjMmoXK4"
bot.run(token)
