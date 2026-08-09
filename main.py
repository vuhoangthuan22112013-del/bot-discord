import asyncio
import os
import random
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
users = {}

# Quản lý phiên tài xỉu chung cho toàn server
tx_room = {
    "active": False,
    "bets": {},  # {user_id: {"name": str, "choice": str, "amount": int}}
    "msg": None,
}


def get_user(uid, name="Thành viên"):
  if uid not in users:
    users[uid] = {
        "name": name,
        "cash": 5000,  # Vốn khởi điểm
        "bank": 0,
    }
  return users[uid]


@bot.event
async def on_ready():
  print(f"🎲 Bot Game Discord Đã Sẵn Sàng: {bot.user}")


# --- 1. LỆNH XEM TÀI KHOẢN (!vi) ---
@bot.command(name="vi", aliases=["bal"])
async def vi_cmd(ctx):
  u = get_user(ctx.author.id, ctx.author.name)
  cash = u["cash"]

  if cash < 10000:
    rank = "👤 Người chơi Thường\n🐓 Gà Công Nghiệp 🐥"
  elif cash < 50000:
    rank = "🥈 Người chơi Bạc\n🐓 Gà Chiến 🔥"
  else:
    rank = "🥇 Đại Gia\n🦅 Phượng Hoàng Lửa 👑"

  embed = discord.Embed(
      title=f"💰 TÀI KHOẢN: {ctx.author.name.upper()}", color=0xF1C40F
  )
  embed.add_field(name="Hạng thẻ", value=rank, inline=False)
  embed.add_field(name="💵 Tiền mặt", value=f"`{u['cash']:,}$`", inline=False)
  embed.add_field(name="🏦 Két sắt", value=f"`{u['bank']:,}$`", inline=False)
  await ctx.send(embed=embed)


# --- 2. LỆNH ĐIỂM DANH (!diemdanh) ---
@bot.command(name="diemdanh", aliases=["diemdanhi", "nhantien"])
async def diemdanh_cmd(ctx):
  u = get_user(ctx.author.id, ctx.author.name)
  bonus = 2593
  u["cash"] += bonus
  await ctx.send(
      f"🎁 {ctx.author.mention} **Điểm danh thành công!** Nhận `+{bonus:,}$` vào ví"
      f" (Số dư: `{u['cash']:,}$`)"
  )


# --- 3. LỆNH QUAY SLOT (!quay) ---
@bot.command(name="quay")
async def quay_cmd(ctx, amount: int = 100):
  user_id = ctx.author.id
  u = get_user(user_id, ctx.author.name)

  if amount <= 0:
    return await ctx.send("❌ Số tiền cược phải lớn hơn 0!")
  if u["cash"] < amount:
    return await ctx.send("❌ Bạn không đủ tiền mặt để quay slot!")

  u["cash"] -= amount
  fruits = ["🍋", "🔔", "7️⃣", "🍒", "💎"]

  # Khung chờ: Màu vàng
  embed = discord.Embed(
      title="🎰 MÁY SLOT BET88",
      description=(
          "KẾT QUẢ\n[ `?` | `?` | `?` ]\n\nThông báo\n🔄 Máy đang quay..."
      ),
      color=0xF1C40F,
  )
  msg = await ctx.send(embed=embed)

  for _ in range(3):
    await asyncio.sleep(0.4)
    r1, r2, r3 = random.choice(fruits), random.choice(fruits), random.choice(fruits)
    embed.description = (
        f"KẾT QUẢ\n[ `{r1}` | `{r2}` | `{r3}` ]\n\nThông báo\n🔄 Đang quay..."
    )
    await msg.edit(embed=embed)

  res = [random.choice(fruits) for _ in range(3)]

  if res[0] == res[1] == res[2]:
    win_amount = amount * 10
    u["cash"] += win_amount
    result_text = f"🎉 **NỔ HŨ! TRÚNG TO!** `+{win_amount:,}$`"
    color = 0x2ECC71  # Xanh lá (Thắng)
  elif res[0] == res[1] or res[1] == res[2] or res[0] == res[2]:
    win_amount = amount * 2
    u["cash"] += win_amount
    result_text = f"✨ **TRÚNG CẶP!** `+{win_amount:,}$`"
    color = 0x2ECC71  # Xanh lá (Thắng)
  else:
    result_text = f"🌿 **TRẬT HŨ (MẤT TRẮNG)!** `-{amount:,}$`"
    color = 0xE74C3C  # Đỏ (Thua)

  embed = discord.Embed(
      title="🎰 MÁY SLOT BET88",
      description=(
          f"KẾT QUẢ\n[ `{res[0]}` | `{res[1]}` | `{res[2]}`"
          f"]\n\nThông báo\n{result_text}"
      ),
      color=color,
  )
  await msg.edit(embed=embed)


# --- 4. HỆ THỐNG TÀI XỈU PHÒNG CHUNG (!tx) ---
@bot.command(name="tx")
async def tx_cmd(ctx, choice: str = None, amount: str = None):
  global tx_room
  user_id = ctx.author.id
  u = get_user(user_id, ctx.author.name)

  if not choice:
    if tx_room["active"]:
      return await ctx.send(
          "⚠️ Đang có một phiên Tài Xỉu diễn ra rồi! Hãy nhanh tay đặt cược."
      )

    tx_room["active"] = True
    tx_room["bets"] = {}

    # Khi mở bàn: Màu vàng
    embed = discord.Embed(
        title="🎲 SÒNG TÀI XỈU BET88",
        description=(
            f"👤 **{ctx.author.name}** đã mở bát!\n👉 Gõ `!tx <tai/xiu>"
            " <tiền>` để theo cược!\n⏱️ Thời gian: **30 giây**\n\n💰 Tổng TÀI:"
            " `0$` | Tổng XỈU: `0$`"
        ),
        color=0xF1C40F,
    )
    msg = await ctx.send(embed=embed)
    tx_room["msg"] = msg

    for remaining in [20, 10, 0]:
      await asyncio.sleep(10)
      if not tx_room["active"]:
        return

      t_tai = sum(
          b["amount"]
          for b in tx_room["bets"].values()
          if b["choice"] == "tai"
      )
      t_xiu = sum(
          b["amount"]
          for b in tx_room["bets"].values()
          if b["choice"] == "xiu"
      )

      embed.description = (
          f"👤 **{ctx.author.name}** đã mở bát!\n👉 Gõ `!tx <tai/xiu>"
          f" <tiền>` để theo cược!\n⏱️ Thời gian còn lại: **{remaining}"
          f" giây**\n\n💰 Tổng TÀI: `{t_tai:,}$` | Tổng XỈU: `{t_xiu:,}$`"
      )
      try:
        await msg.edit(embed=embed)
      except:
        pass

    if not tx_room["active"]:
      return
    tx_room["active"] = False

    embed.description = "🎲 Đang lắc bát...\n[ ? ] - [ ? ] - [ ? ]"
    try:
      await msg.edit(embed=embed)
    except:
      pass

    await asyncio.sleep(2.0)

    d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
    total = d1 + d2 + d3
    ket_qua = "tai" if total >= 11 else "xiu"
    kq_text = "TÀI" if ket_qua == "tai" else "XỈU"

    thang_str = ""
    thua_str = ""
    has_win = False

    for uid, data in tx_room["bets"].items():
      player_u = get_user(uid)
      bet_amt = data["amount"]
      p_choice = data["choice"]
      p_name = data["name"]

      if p_choice == ket_qua:
        player_u["cash"] += bet_amt * 2
        thang_str += f"• {p_name}: +`{bet_amt * 2:,}$`\n"
        if uid == user_id:
          has_win = True
      else:
        thua_str += f"• {p_name}: -`{bet_amt:,}$`\n"

    if not thang_str:
      thang_str = "Không có\n"
    if not thua_str:
      thua_str = "Không có\n"

    # Nếu người dùng chạy lệnh mở bàn có thắng cược ko? (Tính theo tổng thể phiên hoặc mặc định màu xanh nếu có người thắng)
    color = 0x2ECC71 if thang_str != "Không có
    
