import os
import asyncio
import random
import time
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
users = {}
cooldowns = {}

# Quản lý phiên tài xỉu chung cho toàn server
tx_room = {
    "active": False,
    "bets": {},      # Lưu tiền cược: {user_id: {"name": str, "choice": "tai"/"xiu", "amount": int}}
    "msg": None
}

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
            "cash": 5000, # Vốn khởi điểm cho người chơi mới
            "bank": 0
        }
    return users[uid]

@bot.event
async def on_ready():
    print(f"🎲 Bot Tài Xỉu Phiên Bản Mới Đã Sẵn Sàng: {bot.user}")

@bot.command(name="vi", aliases=["bal"])
async def vi_cmd(ctx):
    u = get_user(ctx.author.id, ctx.author.name)
    embed = discord.Embed(title=f"💰 TÀI KHOẢN: {ctx.author.name}", color=0x00FF00)
    embed.add_field(name="Tiền mặt", value=f"`{u['cash']:,}$`", inline=True)
    embed.add_field(name="Két sắt", value=f"`{u['bank']:,}$`", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="nhantien")
async def nhantien_cmd(ctx):
    u = get_user(ctx.author.id, ctx.author.name)
    u["cash"] += 2000
    await ctx.send(f"🎁 {ctx.author.mention} Đã nhận cứu trợ `+2,000$` vào ví!")

# --- HỆ THỐNG TÀI XỈU PHÒNG CHUNG ---
@bot.command(name="tx")
async def tx_cmd(ctx, choice: str = None, amount: str = None):
    global tx_room
    user_id = ctx.author.id
    u = get_user(user_id, ctx.author.name)

    # Trường hợp 1: Gõ lệnh !tx để mở phiên mới
    if not choice:
        if tx_room["active"]:
            return await ctx.send("⚠️ Đang có một phiên Tài Xỉu diễn ra rồi! Hãy nhanh tay đặt cược.")

        tx_room["active"] = True
        tx_room["bets"] = {}
        
        msg = await ctx.send(
            f"🎲 **PHIÊN TÀI XỈU MỚI ĐÃ MỞ!** 🎲\n"
            f"👤 Người mở: **{ctx.author.name}**\n"
            f"-------------------------------------\n"
            f"👉 Cú pháp đặt cược: `!tx tai [số_tiền]` hoặc `!tx xiu [số_tiền]`\n"
            f"⏱️ Thời gian đặt cược: **25 giây**\n"
            f"💰 Tổng cược Tài: `0$` | Tổng cược Xỉu: `0$`"
        )
        tx_room["msg"] = msg

        # Đếm ngược 25 giây cho phép người chơi vào tiền
        for remaining in [20, 15, 10, 5]:
            await asyncio.sleep(5.0)
            if not tx_room["active"]: return
            
            # Tính tổng tiền các cửa
            t_tai = sum(b["amount"] for b in tx_room["bets"].values() if b["choice"] == "tai")
            t_xiu = sum(b["amount"] for b in tx_room["bets"].values() if b["choice"] == "xiu")
            
            try:
                await msg.edit(content=
                    f"🎲 **PHIÊN TÀI XỈU ĐANG DIỄN RA...** 🎲\n"
                    f"⏱️ Thời gian còn lại: **{remaining} giây**\n"
                    f"-------------------------------------\n"
                    f"💰 Tổng cược Tài: `{t_tai:,}$` | Tổng cược Xỉu: `{t_xiu:,}$`\n"
                    f"👉 Gõ `!tx tai [tiền]` hoặc `!tx xiu [tiền]` để tham gia!"
                )
            except: pass

        await asyncio.sleep(5.0)
        if not tx_room["active"]: return

        # Đóng phiên và quay thưởng
        tx_room["active"] = False
        
        try:
            await msg.edit(content="🎰 **HỆ THỐNG ĐANG LẮC XÚC XẮC...** 🎲🎲🎲")
        except: pass
        
        await asyncio.sleep(2.0)

        d1, d2, d3 = random.randint(1,6), random.randint(1,6), random.randint(1,6)
        total = d1 + d2 + d3
        ket_qua = "tai" if total >= 11 else "xiu"
        kq_text = "TÀI" if ket_qua == "tai" else "XỈU"

        # Tổng kết thắng thua cho từng người
        thang_str = ""
        thua_str = ""

        for uid, data in tx_room["bets"].items():
            player_u = get_user(uid)
            bet_amt = data["amount"]
            p_choice = data["choice"]
            p_name = data["name"]

            if p_choice == ket_qua:
                player_u["cash"] += bet_amt * 2  # Hoàn vốn + lãi 1-1
                thang_str += f"• {p_name}: +`{bet_amt * 2:,}$` (Cửa {p_choice.upper()})\n"
            else:
                thua_str += f"• {p_name}: -`{bet_amt:,}$` (Cửa {p_choice.upper()})\n"

        if not thang_str: thang_str = "Không có\n"
        if not thua_str: thua_str = "Không có\n"

        result_message = (
            f"👑 **KẾT QUẢ PHIÊN TÀI XỈU** 👑\n"
            f"🎲 Xúc xắc: `[ {d1} ] - [ {d2} ] - [ {d3} ]`\n"
            f"🎯 Tổng điểm: **{total} ({kq_text})**\n\n"
            f"✨ **DANH SÁCH THẮNG:**\n{thang_str}\n"
            f"💸 **DANH SÁCH THUA:**\n{thua_str}"
        )

        try:
            await msg.edit(content=result_message)
        except:
            await ctx.send(result_message)
        return

    # Trường hợp 2: Người chơi đặt cược !tx [tai/xiu] [tiền]
    choice = choice.lower()
    if choice not in ["tai", "xiu"]:
        return await ctx.send("❌ Cú pháp sai! Vui lòng dùng: `!tx tai [tiền]` hoặc `!tx xiu [tiền]`")

    if not tx_room["active"]:
        return await ctx.send("❌ Hiện tại chưa có phiên Tài Xỉu nào mở! Hãy gõ lệnh `!tx` đơn độc lập để mở phiên mới.")

    if not amount:
        return await ctx.send("❌ Vui lòng nhập số tiền cược! Ví dụ: `!tx tai 500`")

    # Xử lý số tiền (hỗ trợ chữ 'all')
    if amount.lower() == "all":
        bet_val = u["cash"]
    else:
        try:
            bet_val = int(amount)
        except ValueError:
            return await ctx.send("❌ Số tiền cược không hợp lệ!")

    if bet_val <= 0:
        return await ctx.send("❌ Số tiền cược phải lớn hơn 0!")

    if u["cash"] < bet_val:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt! Ví bạn chỉ còn `{u['cash']:,}$`.")

    # Trừ tiền ngay khi đặt cược
    u["cash"] -= bet_val

    # Lưu hoặc cộng dồn cược của người chơi trong phiên này
    if user_id in tx_room["bets"]:
        tx_room["bets"][user_id]["amount"] += bet_val
        tx_room["bets"][user_id]["choice"] = choice  # Cập nhật cửa mới nhất nếu đổi
    else:
        tx_room["bets"][user_id] = {
            "name": ctx.author.name,
            "choice": choice,
            "amount": bet_val
        }

    await ctx.send(f"✅ `{ctx.author.name}` đã đặt thành công `{bet_val:,}$` vào cửa **{choice.upper()}**!")

token = os.getenv("BOT_TOKEN")
bot.run(token)
            
