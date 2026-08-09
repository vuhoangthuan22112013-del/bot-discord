import asyncio
import os
import random
import discord
from discord.ext import commands

# Khởi tạo bot với prefix là dấu chấm than (!) và bật intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
  print(f"Bot đã đăng nhập thành công dưới tên: {bot.user}")


@bot.command(name="tx")
async def tai_xiu(ctx, choice: str = None, money: int = None):
  # Kiểm tra cú pháp người dùng
  if not choice or not money:
    await ctx.send(
        "⚠️ Cú pháp không đúng! Vui lòng gõ: `!tx <tai/xiu> <tien>` (Ví dụ:"
        " `!tx tai 100`)"
    )
    return

  choice = choice.lower()
  if choice not in ["tai", "xiu"]:
    await ctx.send(
        "⚠️ Bạn chỉ có thể chọn `tai` hoặc `xiu` thôi nhé!"
    )
    return

  if money <= 0:
    await ctx.send("⚠️ Số tiền cược phải lớn hơn 0!")
    return

  # Giao diện thông báo phiên Tài Xỉu bắt đầu (giống video)
  embed = discord.Embed(
      title="🎲 SÒNG TÀI XỈU BET88 🎲",
      description=(
          f"**{ctx.author.name}** đã mở bát!\nGõ `!tx <tai/xiu> <tiền>` để"
          f" theo!\n*(Cước max: 10,000,000$/ván)*"
      ),
      color=discord.Color.red(),
  )
  embed.add_field(name="⏱️ Thời gian:", value="10 giây", inline=False)
  embed.add_field(
      name="Tổng Tài:", value=f"{money}$" if choice == "tai" else "0$", inline=True
  )
  embed.add_field(
      name="Tổng Xỉu:", value=f"{money}$" if choice == "xiu" else "0$", inline=True
  )

  msg = await ctx.send(embed=embed)

  # Đếm ngược thời gian (10 giây)
  for i in range(10, 0, -3):
    await asyncio.sleep(3)
    embed.set_field_at(
        0, name="⏱️ Thời gian:", value=f"{max(0, i-3)} giây", inline=False
    )
    await msg.edit(embed=embed)

  await asyncio.sleep(1)

  # Thông báo đang xóc đĩa/lắc xúc xắc
  await ctx.send(
      f"🏠 **NHÀ CÁI BET88 ĐANG XÓC BÁT...**\n🎲 [ ? ] [ ? ] [ ? ]"
  )
  await asyncio.sleep(2)

  # Tung 3 con xúc xắc ngẫu nhiên (mỗi con từ 1 đến 6)
  dice1 = random.randint(1, 6)
  dice2 = random.randint(1, 6)
  dice3 = random.randint(1, 6)
  total_score = dice1 + dice2 + dice3

  # Phân định Tài hay Xỉu (3-10 là Xỉu, 11-18 là Tài)
  result = "tai" if total_score >= 11 else "xiu"
  result_text = "TÀI" if result == "tai" else "XỈU"

  # Kiểm tra thắng thua
  is_win = choice == result

  # Tạo khung kết quả mở bát
  result_embed = discord.Embed(
      title="🔴 MỞ BÁT BET88",
      description=f"Kết Quả\n[ {dice1} ] - [ {dice2} ] - [ {dice3} ]",
      color=discord.Color.green() if is_win else discord.Color.dark_grey(),
  )
  result_embed.add_field(
      name=f"➔ {total_score} ĐIỂM ({result_text})",
      value="",
      inline=False,
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


# Chạy bot bằng biến môi trường token
token = os.getenv("BOT_TOKEN")
if token is None:
  print(
      "Lỗi: Không tìm thấy biến môi trường BOT_TOKEN. Hãy chắc chắn bạn đã thiết"
      " lập token trên GitHub Secrets!"
  )
else:
  bot.run(token)
    
