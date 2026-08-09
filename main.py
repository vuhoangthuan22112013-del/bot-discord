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


# --- 3. LỆNH QUAY SLOT (!quay) - HIỆU ỨNG TỪ TỪ GIỐNG VIDEO ---
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

  # Gửi tin nhắn khung ban đầu
  msg = await ctx.send(
      "🎰 **MÁY SLOT BET88**\nKẾT QUẢ\n[ `?` | `?` | `?` ]\nThông"
      " báo\n🔄 Đang quay..."
  )

  # Hiệu ứng đổi khung liên tục tạo cảm giác quay thật
  for _ in range(3):
    await asyncio.sleep(0.4)
    r1, r2, r3 = random.choice(fruits), random.choice(fruits), random.choice(fruits)
    await msg.edit(
        content=f"🎰 **MÁY SLOT BET88**\nKẾT QUẢ\n[ `{r1}` | `{r2}` | `{r3}` ]\nThông"
        " báo\n🔄 Đang quay..."
    )

  # Kết quả cuối cùng
  res = [random.choice(fruits) for _ in range(3)]

  if res[0] == res[1] == res[2]:
    win_amount = amount * 10
    u["cash"] += win_amount
    result_text = f"🎉 **NỔ HŨ! TRÚNG TO!** `+{win_amount:,}$`"
  elif res[0] == res[1] or res[1] == res[2] or res[0] == res[2]:
    win_amount = amount * 2
    u["cash"] += win_amount
    result_text = f"✨ **TRÚNG CẶP!** `+{win_amount:,}$`"
  else:
    result_text = f"🌿 **TRẬT HŨ (MẤT TRẮNG)!** `-{amount:,}$`"

  await msg.edit(
      content=f"🎰 **MÁY SLOT BET88**\n"
      f"KẾT QUẢ\n"
      f"[ `{res[0]}` | `{res[1]}` | `{res[2]}` ]\n"
      f"Thông báo\n"
      f"{result_text}"
  )


# --- 4. HỆ THỐNG TÀI XỈU PHÒNG CHUNG (!tx) ---
@bot.command(name="tx")
async def tx_cmd(ctx, choice: str = None, amount: str = None):
  global tx_room
  user_id = ctx.author.id
  u = get_user(user_id, ctx.author.name)

  # Nếu chỉ gõ !tx -> Mở phiên mới
  if not choice:
    if tx_room["active"]:
      return await ctx.send(
          "⚠️ Đang có một phiên Tài Xỉu diễn ra! Hãy nhanh tay đặt cược."
      )

    tx_room["active"] = True
    tx_room["bets"] = {}

    msg = await ctx.send(
        f"🎲 **SÒNG TÀI XỈU BET88** 🎲\n"
        f"👤 {ctx.author.name} đã mở bát!\n"
        f"👉 Gõ `!tx <tai/xiu> <tiền>` để theo cược!\n"
        f"⏱️ Thời gian: **30 giây**\n\n"
        f"💰 Tổng TÀI: `0$` | Tổng XỈU: `0$`"
    )
    tx_room["msg"] = msg

    # Đếm ngược 30 giây (mỗi 10 giây cập nhật 1 lần)
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

      try:
        await msg.edit(
            content=f"🎲 **SÒNG TÀI XỈU BET88** 🎲\n"
            f"👤 {ctx.author.name} đã mở bát!\n"
            f"👉 Gõ `!tx <tai/xiu> <tiền>` để theo cược!\n"
            f"⏱️ Thời gian còn lại: **{remaining} giây**\n\n"
            f"💰 Tổng TÀI: `{t_tai:,}$` | Tổng XỈU: `{t_xiu:,}$`"
        )
      except:
        pass

    if not tx_room["active"]:
      return
    tx_room["active"] = False

    try:
      await msg.edit(
          content="🎲 **SÒNG TÀI XỈU BET88** 🎲\nĐang lắc bát...\n[ ? ] - [ ? ]"
          " - [ ? ]"
      )
    except:
      pass

    await asyncio.sleep(2.0)

    d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
    total = d1 + d2 + d3
    ket_qua = "tai" if total >= 11 else "xiu"
    kq_text = "TÀI" if ket_qua == "tai" else "XỈU"

    thang_str = ""
    thua_str = ""

    for uid, data in tx_room["bets"].items():
      player_u = get_user(uid)
      bet_amt = data["amount"]
      p_choice = data["choice"]
      p_name = data["name"]

      if p_choice == ket_qua:
        player_u["cash"] += bet_amt * 2
        thang_str += f"• {p_name}: +`{bet_amt * 2:,}$`\n"
      else:
        thua_str += f"• {p_name}: -`{bet_amt:,}$`\n"

    if not thang_str:
      thang_str = "Không có\n"
    if not thua_str:
      thua_str = "Không có\n"

    result_message = (
        f"🎲 **MỞ BẮT BET88**\n"
        f"Kết quả: `[ {d1} ] - [ {d2} ] - [ {d3} ]`\n"
        f"🎯 **{total} ĐIỂM ({kq_text})**\n\n"
        f"✨ **THẮNG:**\n{thang_str}\n"
        f"💀 **THUA:**\n{thua_str}"
    )

    try:
      await msg.edit(content=result_message)
    except:
      await ctx.send(result_message)
    return

  # Nếu người chơi gõ !tx tai/xiu [tiền]
  choice = choice.lower()
  if choice not in ["tai", "xiu"]:
    return await ctx.send(
        "❌ Cú pháp sai! Dùng: `!tx tai <tiền>` hoặc `!tx xiu <tiền>`"
    )

  if not tx_room["active"]:
    return await ctx.send(
        "❌ Chưa có bàn Tài Xỉu nào mở! Hãy gõ `!tx` để mở bàn mới."
    )

  if not amount:
    return await ctx.send("❌ Vui lòng nhập số tiền cược!")

  if amount.lower() == "all":
    bet_val = u["cash"]
  else:
    try:
      bet_val = int(amount)
    except ValueError:
      return await ctx.send("❌ Số tiền cược không hợp lệ!")

  if bet_val <= 0 or u["cash"] < bet_val:
    return await ctx.send(f"❌ Số dư không đủ! Ví bạn có `{u['cash']:,}$`.")

  u["cash"] -= bet_val

  # Mỗi người chỉ được đặt 1 lần hoặc dồn tiền vào cửa đã chọn trong phiên
  if user_id in tx_room["bets"]:
    tx_room["bets"][user_id]["amount"] += bet_val
    tx_room["bets"][user_id]["choice"] = choice
  else:
    tx_room["bets"][user_id] = {
        "name": ctx.author.name,
        "choice": choice,
        "amount": bet_val,
    }

  await ctx.send(
      f"✅ `{ctx.author.name}` đã đặt `{bet_val:,}$` vào cửa **{choice.upper()}**!"
  )


# --- 5. LỆNH XÓC ĐĨA (!xd) ---
@bot.command(name="xd")
async def xoc_dia(ctx, choice: str, amount: int = 100):
  user_id = ctx.author.id
  u = get_user(user_id, ctx.author.name)
  choice = choice.lower()

  if choice not in ["chan", "le", "do", "trang"]:
    return await ctx.send("⚠️ Cú pháp: `!xd chan 100` hoặc `le`, `do`, `trang`")

  if u["cash"] < amount:
    return await ctx.send("❌ Bạn không đủ tiền mặt!")

  u["cash"] -= amount
  msg = await ctx.send(
      f"🥣 **XÓC ĐĨA BET88**\n4 Đồng xu\n⚪ ⚪ ⚪ ⚪\n*Xóc... xóc... xóc...*"
  )
  await asyncio.sleep(2.0)

  coins = [random.choice(["🔴", "⚪"]) for _ in range(4)]
  red_count = coins.count("🔴")
  ket_qua_chan_le = "chan" if red_count % 2 == 0 else "le"

  win = False
  if choice in ["chan", "le"] and choice == ket_qua_chan_le:
    win = True
  elif choice == "do" and red_count == 4:
    win = True
  elif choice == "trang" and red_count == 0:
    win = True

  if win:
    win_amt = amount * 2
    u["cash"] += win_amt
    status = f"🏆 **THẮNG LỚN!** `+{win_amt:,}$`"
  else:
    status = f"💀 **CÁI ĂN SẠCH!** `-{amount:,}$`"

  await msg.edit(
      content=f"🥣 **XÓC ĐĨA BET88**\n"
      f"4 Đồng xu\n"
      f"{coins[0]} {coins[1]} {coins[2]} {coins[3]}\n"
      f"Kết quả\n"
      f"➔ {ket_qua_chan_le.upper()} ({red_count} Đỏ)\n"
      f"{status}"
  )


# --- 6. LỆNH BẦU CUA (!bc) ---
@bot.command(name="bc")
async def bau_cua(ctx, choice: str, amount: int = 100):
  user_id = ctx.author.id
  u = get_user(user_id, ctx.author.name)

  symbols = {"bau": "🍐", "cua": "🦀", "tom": "🦐", "ca": "🐟", "ga": "🐓", "nai": "🦌"}
  choice = choice.lower()

  if choice not in symbols:
    return await ctx.send(
        "⚠️ Chọn linh vật: `bau`, `cua`, `tom`, `ca`, `ga`, `nai`\nVí dụ: `!bc"
        " cua 100`"
    )

  if u["cash"] < amount:
    return await ctx.send("❌ Bạn không đủ tiền mặt!")

  u["cash"] -= amount
  msg = await ctx.send(
      f"🏮 **BẦU CUA BET88**\nTrạng thái\nĐang ủ bát...\n[ ? ] [ ? ] [ ? ]"
  )
  await asyncio.sleep(2.0)

  res_keys = [random.choice(list(symbols.keys())) for _ in range(3)]
  res_icons = [symbols[k] for k in res_keys]

  matches = res_keys.count(choice)
  if matches > 0:
    win_amt = amount * matches
    u["cash"] += amount + win_amt  # Hoàn vốn + tiền thưởng theo số con
    status = f"✨ **TRÚNG {matches} CON!** `+{win_amt:,}$`"
  else:
    status = f"💀 **MẤT SẠCH!** `-{amount:,}$`"

  await msg.edit(
      content=f"🏮 **BẦU CUA BET88**\nMỞ BẮT\nTổng kết\n"
      f"[ {res_icons[0]} ] [ {res_icons[1]} ] [ {res_icons[2]} ]\n"
      f"{status}"
  )


token = os.getenv("BOT_TOKEN")
bot.run(token)
    
