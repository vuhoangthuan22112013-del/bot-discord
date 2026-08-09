import discord
import random

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Lưu trữ số dư tiền ảo của người chơi (Mặc định mỗi người có 1000$)
nguoi_dung_tien = {}

@client.event
async def on_ready():
    print(f'Bot Tài Xỉu đã hoạt động: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user_id = message.author.id
    # Nếu người chơi chưa có tiền, cấp mặc định 1000$
    if user_id not in nguoi_dung_tien:
        nguoi_dung_tien[user_id] = 1000

    noi_dung = message.content.strip().lower()

    # Lệnh xem số dư: !vi
    if noi_dung == '!vi':
        tien = nguoi_dung_tien[user_id]
        await message.channel.send(
            f"💰 **TÀI KHOẢN: {message.author.name.upper()}**\n"
            f"💵 Tiền mặt: **{tien:,}$**"
        )

    # Lệnh chơi tài xỉu: !tx [tai/xiu] [so_tien]
    # Ví dụ: !tx tai 100 hoặc !tx xiu 50
    elif noi_dung.startswith('!tx '):
        phan_chia = noi_dung.split()
        if len(phan_chia) < 3:
            await message.channel.send("⚠️ Cú pháp sai! Hãy dùng: `!tx <tai/xiu> <số tiền>` (Ví dụ: `!tx tai 100`)")
            return

        lua_chon = phan_chia[1]
        if lua_chon not in ['tai', 'xiu']:
            await message.channel.send("⚠️ Bạn chỉ được chọn `tai` hoặc `xiu` thôi nhé!")
            return

        try:
            so_tien_cuoc = int(phan_chia[2])
        except ValueError:
            await message.channel.send("⚠️ Số tiền cược phải là một con số hợp lệ!")
            return

        if so_tien_cuoc <= 0:
            await message.channel.send("⚠️ Số tiền cược phải lớn hơn 0!")
            return

        if nguoi_dung_tien[user_id] < so_tien_cuoc:
            await message.channel.send(f"❌ Bạn không đủ tiền! Số dư hiện tại của bạn là: **{nguoi_dung_tien[user_id]:,}$**")
            return

        # Trừ tiền cược trước
        nguoi_dung_tien[user_id] -= so_tien_cuoc

        # Gửi thông báo bắt đầu lắc xúc xắc giống trong video
        await message.channel.send("🎲 **SÒNG TÀI XỈU**\n*Đang lắc xúc xắc...*")

        # Sinh ngẫu nhiên 3 viên xúc xắc từ 1 đến 6
        x1 = random.randint(1, 6)
        x2 = random.randint(1, 6)
        x3 = random.randint(1, 6)
        tong_diem = x1 + x2 + x3

        # Xác định Tài hay Xỉu (Từ 3-10 là Xỉu, từ 11-18 là Tài)
        ket_qua_ban = "xiu" if 3 <= tong_diem <= 10 else "tai"
        ten_ket_qua = "XỈU" if ket_qua_ban == "xiu" else "TÀI"

        # Kiểm tra thắng thua
        thong_bao_ket_qua = ""
        if lua_chon == ket_qua_ban:
            # Thắng thì nhận lại tiền cược + số tiền thắng (nhân đôi tiền cược)
            tien_thuong = so_tien_cuoc * 2
            nguoi_dung_tien[user_id] += tien_thuong
            thong_bao_ket_qua = f"🎉 **THẮNG!** Nhận được `+{tien_thuong:,}$`"
        else:
            thong_bao_ket_qua = f"💸 **THUA!** Mất `-{so_tien_cuoc:,}$`"

        # Gửi kết quả chi tiết giống video
        await message.channel.send(
            f"🎲 **MỞ BÁT**\n"
            f"Kết Quả: `[ {x1} ] - [ {x2} ] - [ {x3} ]`\n"
            f"📊 Tổng Điểm: **{tong_diem} ({ten_ket_qua})**\n"
            f"{thong_bao_ket_qua}\n"
            f"💵 Số dư ví hiện tại: **{nguoi_dung_tien[user_id]:,}$**"
        )

# Dán Token của bạn vào đây:
client.run('MTUzNTg1NTE2NDcwMTgwNjY4Mw.Gk2jJM.GWEYHx3BsB4j86h9qgyNQakjAbJ4h4t5TU-Pq0')
