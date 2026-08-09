import asyncio
import os
import random
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
  print(f"Bot đã đăng nhập thành công dưới tên: {bot.user}")


# Hàm phụ trợ để chọn màu thanh dọc bên trái của embed
def get_embed_color(status):
  # status: 'win', 'lose', 'draw' hoặc màu mặc định
  if status == "win":
    return discord.Color.green()  # Thắng -> Xanh lá
  elif status == "lose":
    return discord.Color.red()  # Thua -> Đỏ
  elif status == "draw":
    return discord.Color.gold()  # Hòa -> Vàng
  return discord.Color.blue()  # Mặc định / Đang chơi


# 1. Lệnh TÀI XỈU (!tx)
@bot.command(name="tx")
async def tai_xiu(ctx, choice: str = None, money: int = None):
  if not choice or not money:
    await ctx.send("⚠️ Cú pháp: `!tx <tai/xiu> <tien>` (Ví dụ: `!tx tai 100`)")
    return

  choice = choice.lower()
  if choice not in ["tai", "xiu"]:
    await ctx.send("⚠️ Bạn chỉ có thể chọn `tai` hoặc `xiu`!")
    return

  if money <= 0:
    await ctx.send("⚠️ Số tiền cược phải lớn hơn 0!")
    return

  embed = discord.Embed(
      title="🎲 SÒNG TÀI XỈU BET88 🎲",
      description=(
          f"**{ctx.author.name}** đã mở bát!\nGõ `!tx <tai/xiu> <tiền>` để"
          f" theo!\n*(Cước max: 10,000,000$/ván)*"
      ),
      color=get_embed_color("neutral"),
  )
  embed.add_field(name="⏱️ Thời gian:", value="10 giây", inline=False)
  embed.add_field(
      name="Tổng Tài:", value=f"{money}$" if choice == "tai" else "0$", inline=True
  )
  embed.add_field(
      name="Tổng Xỉu:", value=f"{money}$" if choice == "xiu" else "0$", inline=True
  )

  msg = await ctx.send(embed=embed)

  for i in range(10, 0, -3):
    await asyncio.sleep(3)
    embed.set_field_at(
        0, name="⏱️ Thời gian:", value=f"{max(0, i-3)} giây", inline=False
    )
    await msg.edit(embed=embed)

  await asyncio.sleep(1)
  await ctx.send(
      f"🏠 **NHÀ CÁI BET88 ĐANG XÓC BÁT...**\n🎲 [ ? ] [ ? ] [ ? ]"
  )
  await asyncio.sleep(2)

  dice1 = random.randint(1, 6)
  dice2 = random.randint(1, 6)
  dice3 = random.randint(1, 6)
  total_score = dice1 + dice2 + dice3

  result = "tai" if total_score >= 11 else "xiu"
  result_text = "TÀI" if result == "tai" else "XỈU"
  is_win = choice == result

  # Xác định màu cột dọc: Thắng = Xanh lá, Thua = Đỏ
  color_status = "win" if is_win else "lose"

  result_embed = discord.Embed(
      title="🔴 MỞ BÁT BET88",
      description=f"Kết Quả\n[ {dice1} ] - [ {dice2} ] - [ {dice3} ]",
      color=get_embed_color(color_status),
  )
  result_embed.add_field(
      name=f"➔ {total_score} ĐIỂM ({result_text})", value="", inline=False
  )

  if is_win:
    result_embed.add_field(
        name="🏆 THẮNG", value=f"Chúc mừng bạn nhận được +{money}$", inline=False
    )
  else:
    result_embed.add_field(
        name="💀 THUA", value=f"- {ctx.author.name} (-{money}$)", inline=False
    )

  await ctx.send(embed=result_embed)


# 2. Lệnh XÓC ĐĨA (!xd)
@bot.command(name="xd")
async def xoc_dia(ctx, choice: str = None, money: int = None):
  if not choice or not money:
    await ctx.send("⚠️ Cú pháp: `!xd <chan/le> <tien>` (Ví dụ: `!xd chan 100`)")
    return

  choice = choice.lower()
  if choice not in ["chan", "le"]:
    await ctx.send("⚠️ Bạn chỉ có thể chọn `chan` hoặc `le`!")
    return

  await ctx.send(
      f"🪙 **XÓC ĐĨA BET88**\nĐang xóc... Đặt bát xuống bàn..."
  )
  await asyncio.sleep(2)

  # 4 nút đồng xu ngẫu nhiên (màu đỏ / trắng)
  coins = [random.choice(["🔴", "⚪"]) for _ in range(4)]
  red_count = coins.count("🔴")

  # Quy ước chẵn/lẻ theo số lượng nút đỏ (4 đỏ, 2 đỏ, 0 đỏ là Chẵn; 3 đỏ, 1 đỏ là Lẻ)
  is_chan = red_count in [0, 2, 4]
  result_type = "chan" if is_chan else "le"
  result_name = "CHẴN" if is_chan else "LẺ"

  user_win = (choice == "chan" and is_chan) or (choice == "le" and not is_chan)
  color_status = "win" if user_win else "lose"

  embed = discord.Embed(
      title="🪙 XÓC ĐĨA BET88",
      description=(
          f"4 Đồng xu\n{' '.join(coins)}\n\nKết quả\n➔ {result_name} ({red_count}"
          " Đỏ)"
      ),
      color=get_embed_color(color_status),
  )

  if user_win:
    embed.add_field(
        name="🏆 THẮNG", value=f"Nhận được +{money}$", inline=False
    )
  else:
    embed.add_field(
        name="CÁI ĂN SẠCH!", value=f"-{money}$ (-{ctx.author.name})", inline=False
    )

  await ctx.send(embed=embed)


# 3. Lệnh QUAY (SLOT MACHINE - !quay)
@bot.command(name="quay")
async def quay_slot(ctx, money: int = 100):
  # Mô phỏng hiệu ứng máy đang quay
  msg = await ctx.send("🎰 **MÁY SLOT BET88**\nMáy đang quay...\n[ 🍋 ] [ 🔔 ] [ 🍒 ]")
  await asyncio.sleep(1.5)

  items = ["🍋", "🔔", "🍒", "💎", "⭐", "7️⃣"]
  r1, r2, r3 = random.choices(items, k=3)

  # Kiểm tra thắng: 3 biểu tượng giống nhau là trúng Jackpot (Thắng), ngược lại Thua
  is_win = r1 == r2 == r3
  color_status = "win" if is_win else "lose"

  embed = discord.Embed(
      title="🎰 MÁY SLOT BET88",
      description=f"KẾT QUẢ\n[ {r1} ] [ {r2} ] [ {r3} ]",
      color=get_embed_color(color_status),
  )

  if is_win:
    embed.add_field(
        name="🎉 TRẮNG HỦ (JACKPOT)!",
        value=f"Chúc mừng nhận +{money * 10}$",
        inline=False,
    )
  else:
    embed.add_field(
        name="Thông báo", value=f"TRẮT HỦ (MẤT TRẮNG)! -{money}$", inline=False
    )

  await ctx.send(embed=embed)


# 4. Lệnh BẦU CUA (!bc)
@bot.command(name="bc")
async def bau_cua(ctx, choice: str = None, money: int = None):
  if not choice or not money:
    await ctx.send(
        "⚠️ Cú pháp: `!bc <bau/cua/tom/ca/ga/nai> <tien>` (Ví dụ: `!bc bau"
        " 100`)"
    )
    return

  symbols = {
      "bau": " bầu 🟢",
      "cua": " cua 🔴",
      "tom": " tôm 🦞",
      "ca": " cá 🐟",
      "ga": " gà 🐓",
      "nai": " nai 🦌",
  }

  choice = choice.lower()
  if choice not in symbols:
    await ctx.send("⚠️ Lựa chọn không hợp lệ! Chọn: bau, cua, tom, ca, ga, nai.")
    return

  await ctx.send("🎲 **BẦU CUA BET88**\nTừ từ hé bát...")
  await asyncio.sleep(2)

  # Tung 3 con ngẫu nhiên
  dice_results = random.choices(list(symbols.keys()), k=3)
  displayed_dice = [symbols[d] for d in dice_results]

  # Đếm số lần xuất hiện của lựa chọn người chơi
  match_count = dice_results.count(choice)
  is_win = match_count > 0

  # Nếu trúng thì thắng, không trúng thì thua
  color_status = "win" if is_win else "lose"

  embed = discord.Embed(
      title="🦀 BẦU CUA BET88",
      description=(
          f"Trạng thái\n[ {displayed_dice[0]} ] [ {displayed_dice[1]} ] [ "
          f"{displayed_dice[2]} ]"
      ),
      color=get_embed_color(color_status),
  )

  if is_win:
    reward = money * match_count
    embed.add_field(
        name="🏆 THẮNG",
        value=f"Trúng {match_count} con! Nhận +{reward}$",
        inline=False,
    )
  else:
    embed.add_field(
        name="MẤT SẠCH!", value=f"Thua -{money}$", inline=False
    )

  await ctx.send(embed=embed)


# Chạy bot
token = os.getenv("BOT_TOKEN")
if token:
  bot.run(token)
else:
  print("Lỗi: Chưa thiết lập biến môi trường BOT_TOKEN!")
      
