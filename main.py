import os
import asyncio
import random
import time
import discord
from discord.ext import commands
from collections import Counter

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
users = {}
codes_db = {"BET88": 50000, "VIP2026": 100000}

cooldowns = {}

def check_spam(user_id, cmd_name, limit_seconds=1.5):
    now = time.time()
    key = f"{user_id}_{cmd_name}"
    if key in cooldowns:
        diff = now - cooldowns[key]
        if diff < limit_seconds:
            return round(limit_seconds - diff, 1)
    cooldowns[key] = now
    return 0.0

def get_user(uid):
    if uid not in users:
        users[uid] = {
            "cash": 5003,
            "bank": 0,
            "used_codes": []
        }
    return users[uid]

@bot.event
async def on_ready():
    print(f"✅ BOT FULL CHỨC NĂNG & ĐỦ HIỆU ỨNG ĐÃ SẴN SÀNG: {bot.user}")

# --- MENU TRỢ GIÚP ---
@bot.command(name="menu", aliases=["trogiup"])
async def menu_cmd(ctx):
    cd = check_spam(ctx.author.id, "menu", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    msg = (
        "🎰 **CASINO BET88 UY TÍN** 🎰\n\n"
        "⚔️ **ĐỐI KHÁNG (PVP)**\n"
        "`!danhbai @User [tiền]` | `!thachdau @User [tiền]`\n"
        "`!dagapvp @User [tiền]` | `!tuxipvjp @User [tiền]`\n\n"
        "🎲 **CASINO (SOLO)**\n"
        "`!tx [tai/xiu] [tiền]` | `!rl [xanh/do/den] [tiền]`\n"
        "`!quay [tiền]` | `!bc [ca/tom/cua/bau/ga/nai] [tiền]`\n"
        "`!xd [chan/le] [tiền]` | `!daga [tiền]`\n"
        "`!tuxi [bua/bao/keo] [tiền]` | `!bai [tiền]`\n"
        "`!duangua [1/2/3/4] [tiền]` | `!coinflip [ngua/saph] [tiền]`\n\n"
        "🏛️ **HỆ THỐNG**\n"
        "`!vi` | `!gui [tiền/all]` | `!rut [tiền/all]` | `!chuyen @User [tiền]`\n"
        "`!diemdanh` | `!bxh` | `!nhapcode [code]`"
    )
    await ctx.send(msg)

# --- NHÓM LỆNH HỆ THỐNG & TÀI CHÍNH ---
@bot.command(name="vi", aliases=["money", "bal"])
async def vi_cmd(ctx, member: discord.Member = None):
    cd = check_spam(ctx.author.id, "vi", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    target = member if member else ctx.author
    u = get_user(target.id)
    
    msg = (
        f"💳 Tài sản của {target.name}_{target.id[:4]}4617:\n"
        f"• Tiền mặt: `{u['cash']:,} $`\n"
        f"• Ngân hàng: `{u['bank']:,} $ (Lãi 2%/ngày)`"
    )
    await ctx.send(msg)

@bot.command(name="gui")
async def gui_cmd(ctx, amount: str = None):
    cd = check_spam(ctx.author.id, "gui", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    u = get_user(ctx.author.id)
    if not amount:
        return await ctx.send("❌ Cú pháp: `!gui [số_tiền hoặc all]`")
    
    if amount.lower() == "all":
        val = u["cash"]
    else:
        try:
            val = int(amount)
        except ValueError:
            return await ctx.send("❌ Số tiền không hợp lệ!")
            
    if val <= 0 or u["cash"] < val:
        return await ctx.send("❌ Bạn không đủ tiền mặt để gửi!")
        
    u["cash"] -= val
    u["bank"] += val
    await ctx.send(f"🏦 Đã gửi thành công `{val:,} $` vào két sắt!")

@bot.command(name="rut")
async def rut_cmd(ctx, amount: str = None):
    cd = check_spam(ctx.author.id, "rut", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    u = get_user(ctx.author.id)
    if not amount:
        return await ctx.send("❌ Cú pháp: `!rut [số_tiền hoặc all]`")
    
    if amount.lower() == "all":
        val = u["bank"]
    else:
        try:
            val = int(amount)
        except ValueError:
            return await ctx.send("❌ Số tiền không hợp lệ!")
            
    if val <= 0 or u["bank"] < val:
        return await ctx.send("❌ Số dư két sắt không đủ!")
        
    u["bank"] -= val
    u["cash"] += val
    await ctx.send(f"💸 Đã rút thành công `{val:,} $` từ két sắt về ví!")

@bot.command(name="chuyen")
async def chuyen_cmd(ctx, member: discord.Member = None, amount: int = None):
    cd = check_spam(ctx.author.id, "chuyen", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    if not member or not amount or amount <= 0:
        return await ctx.send("❌ Cú pháp: `!chuyen @User [tiền]`")
    if member.id == ctx.author.id:
        return await ctx.send("❌ Không thể tự chuyển tiền cho chính mình!")
        
    u_sender = get_user(ctx.author.id)
    if u_sender["cash"] < amount:
        return await ctx.send("❌ Tiền mặt của bạn không đủ để chuyển!")
        
    u_receiver = get_user(member.id)
    u_sender["cash"] -= amount
    u_receiver["cash"] += amount
    await ctx.send(f"🤝 **{ctx.author.name}** đã chuyển thành công `{amount:,} $` cho **{member.name}**!")

@bot.command(name="bxh")
async def bxh_cmd(ctx):
    cd = check_spam(ctx.author.id, "bxh", 2.0)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    if not users:
        return await ctx.send("🏆 Bảng xếp hạng đang trống!")
        
    sorted_users = sorted(users.items(), key=lambda x: x[1]["cash"] + x[1]["bank"], reverse=True)[:5]
    desc = "🏆 **TOP TÀI PHÚ HỘ HÀNG ĐẦU** 🏆\n"
    for idx, (uid, data) in enumerate(sorted_users, 1):
        try:
            member = await ctx.guild.fetch_member(uid)
            name = member.name
        except:
            name = f"User_{uid}"
        total = data["cash"] + data["bank"]
        desc += f"{idx}. **{name}** - Tổng tài sản: `{total:,} $`\n"
    await ctx.send(desc)

@bot.command(name="nhapcode")
async def nhapcode_cmd(ctx, code: str = None):
    cd = check_spam(ctx.author.id, "nhapcode", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    if not code:
        return await ctx.send("❌ Cú pháp: `!nhapcode [mã_code]`")
        
    code_upper = code.upper()
    if code_upper not in codes_db:
        return await ctx.send("❌ Mã quà tặng không tồn tại hoặc đã hết hạn!")
        
    u = get_user(ctx.author.id)
    if code_upper in u["used_codes"]:
        return await ctx.send("❌ Bạn đã nhập mã quà tặng này rồi!")
        
    reward = codes_db[code_upper]
    u["cash"] += reward
    u["used_codes"].append(code_upper)
    await ctx.send(f"🎁 Nhập code thành công! Nhận ngay `+{reward:,} $` vào ví.")

@bot.command(name="diemdanh", aliases=["daily"])
async def diemdanh_cmd(ctx):
    cd = check_spam(ctx.author.id, "diemdanh", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    u = get_user(ctx.author.id)
    rw = random.randint(1000, 3000)
    u["cash"] += rw
    await ctx.send(f"🎁 **{ctx.author.name}** Điểm danh thành công! Nhận `+{rw:,} $`")

# --- CÁC TRÒ CHƠI CASINO CÓ ĐẦY ĐỦ HIỆU ỨNG GỐC ---

@bot.command(name="tx", aliases=["taixiu"])
async def taixiu_cmd(ctx, choice: str = None, bet: int = None):
    cd = check_spam(ctx.author.id, "tx", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    if not choice or choice.lower() not in ["tai", "xiu"] or not bet or bet <= 0:
        return await ctx.send(f"❌ Cú pháp: `!tx [tai/xiu] [tiền]`")
        
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt!")

    # HIỆU ỨNG GỐC: Lắc xúc xắc
    msg = await ctx.send(f"🎲 **TÀI XỈU BET88**\n📳 *Đang lắc xúc xắc...*")
    await asyncio.sleep(0.6)
    
    d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
    tong = d1 + d2 + d3
    ket_qua = "tai" if tong >= 11 else "xiu"
    
    res_text = f"🎲 **TÀI XỈU BET88 - KẾT QUẢ**\n`[ {d1} ] - [ {d2} ] - [ {d3} ]`\n➔ **{tong} Điểm ({ket_qua.upper()})**"
    
    if choice.lower() == ket_qua:
        u["cash"] += bet
        res_text += f"\n🎉 **Thắng!** Nhận `+{bet:,} $`"
    else:
        u["cash"] -= bet
        res_text += f"\n💸 **Thua!** Mất `-{bet:,} $`"
        
    await msg.edit(content=res_text)

@bot.command(name="rl", aliases=["roulette"])
async def rl_cmd(ctx, color_choice: str = None, bet: int = None):
    cd = check_spam(ctx.author.id, "rl", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    valid_colors = {"do": ("🔴", 1.5, 50), "den": ("⚫", 2.0, 25), "xanh": ("🟢", 3.0, 10)}
    if not color_choice or color_choice.lower() not in valid_colors or not bet or bet <= 0:
        return await ctx.send(f"❌ Cú pháp: `!rl [xanh/do/den] [tiền]`")
        
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt!")

    choice = color_choice.lower()
    
    # HIỆU ỨNG GỐC: Xoay roulette trực quan
    msg = await ctx.send(f"🎡 **ROULETTE BET88**\n🔄 *Bánh xe đang quay: `[ 🔴 | 🟢 | ⚫ ]`*")
    await asyncio.sleep(0.5)
    await msg.edit(content=f"🎡 **ROULETTE BET88**\n🔄 *Đang dừng lại: `[ ⚫ | 🔴 | 🟢 ]`*")
    await asyncio.sleep(0.5)

    rand_val = random.randint(1, 100)
    if rand_val <= 10:
        result_color = "xanh"
    elif rand_val <= 35:
        result_color = "den"
    else:
        result_color = "do"

    emoji, multiplier, _ = valid_colors[result_color]
    res_text = f"🎡 **ROULETTE BET88 - KẾT QUẢ**\n🎯 Ô trúng: **{emoji} {result_color.upper()}**"
    
    if choice == result_color:
        win = int(bet * multiplier)
        u["cash"] += (win - bet)
        res_text += f"\n🎉 **TRÚNG ROULETTE!** Nhận `+{win:,} $` (x{multiplier})"
    else:
        u["cash"] -= bet
        res_text += f"\n💸 **TRẬT LẤT!** Mất `-{bet:,} $`"
        
    await msg.edit(content=res_text)

@bot.command(name="quay")
async def quay_cmd(ctx, bet: int = None):
    cd = check_spam(ctx.author.id, "quay", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    if not bet or bet <= 0:
        return await ctx.send(f"❌ Cú pháp: `!quay [tiền]`")
    
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt!")

    symbols = ["💎", "🔔", "🍋", "🍒"]
    
    # HIỆU ỨNG GỐC: Máy slot chạy ô
    msg = await ctx.send(f"🎰 Vòng quay: `[ ? ] [ ? ] [ ? ]`")
    await asyncio.sleep(0.5)
    await msg.edit(content=f"🎰 Vòng quay: `[ 💎 ] [ ? ] [ ? ]`")
    await asyncio.sleep(0.5)
    
    is_win = random.random() < 0.4
    if is_win:
        s = random.choice(symbols)
        r1, r2, r3 = s, s, random.choice(symbols)
    else:
        r1, r2, r3 = random.sample(symbols, 3)
        
    cnt = Counter([r1, r2, r3])
    max_f = max(cnt.values())
    
    if max_f >= 2:
        win = bet * max_f
        u["cash"] += (win - bet)
        await msg.edit(content=f"🎰 Vòng quay: `[ {r1} ] [ {r2} ] [ {r3} ]`\n✨ **Trúng {max_f} con (x{max_f})!** Nhận `+{win:,} $`")
    else:
        u["cash"] -= bet
        await msg.edit(content=f"🎰 Vòng quay: `[ {r1} ] [ {r2} ] [ {r3} ]`\n😢 **Chúc bạn may mắn lần sau!** Mất `-{bet:,} $`")

@bot.command(name="xd")
async def xocdia_cmd(ctx, choice: str = None, bet: int = None):
    cd = check_spam(ctx.author.id, "xd", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    if not choice or choice.lower() not in ["chan", "le"] or not bet or bet <= 0:
        return await ctx.send(f"❌ Cú pháp: `!xd [chan/le] [tiền]`")
        
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt!")

    # HIỆU ỨNG GỐC: Xóc đĩa
    msg = await ctx.send(f"🪙 **XÓC ĐĨA BET88**\n📳 *Xóc... xóc... xóc...*")
    await asyncio.sleep(0.8)
    
    red_count = random.randint(0, 4)
    ket_qua = "chan" if red_count % 2 == 0 else "le"
    board = "🔴" * red_count + "⚪" * (4 - red_count)
    
    res_text = f"🪙 **XÓC ĐĨA BET88 - KẾT QUẢ**\n📊 Bát mở: `{board}` (Đỏ: {red_count} ➔ **{ket_qua.upper()}**)"
    
    if choice.lower() == ket_qua:
        u["cash"] += bet
        res_text += f"\n🎉 **Thắng!** Ăn được `+{bet:,} $`"
    else:
        u["cash"] -= bet
        res_text += f"\n💸 **Thua!** Bạn mất `-{bet:,} $`"
        
    await msg.edit(content=res_text)

@bot.command(name="bc")
async def baucua_cmd(ctx, choice: str = None, bet: int = None):
    cd = check_spam(ctx.author.id, "bc", 1.5)
    if cd > 0:
        return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")

    animals = {"ca": "🐟", "tom": "🦐", "cua": "🦀", "bau": "🥒", "ga": "🐓", "nai": "🦌"}
    if not choice or choice.lower() not in animals or not bet or bet <= 0:
        return await ctx.send(f"❌ Cú pháp: `!bc [ca/tom/cua/bau/ga/nai] [tiền]`")
        
    u = get_user(ctx.author.id)
    if u["cash"] < bet:
        return await ctx.send(f"❌ Bạn không đủ tiền mặt!")

    # HIỆU ỨNG GỐC: Bầu cua
    msg = await ctx.send(f"🎲 **BẦU CUA BET88**\n📳 *Đang úp bát...*")
    await asyncio.sleep(0.8)
    
    keys = list(animals.keys())
    d1, d2, d3 = random.choice(keys), random.choice(keys), random.choice(keys)
    matches = [d1, d2, d3].count(choice.lower())
    
    res_text = f"🎲 **BẦU CUA BET88 - KẾT QUẢ**\n🎯 Kết quả: `{animals[d1]} {d1.capitalize()} | {animals[d2]} {d2.capitalize()} | {animals[d3]} {d3.capitalize()}`"
    
    if matches > 0:
        win = int(bet * matches * 1.5)
        u["cash"] += win
        res_text += f"\n✨ **Trúng {matches} con (x1.5)!** Nhận `+{win:,} $`"
    else:
        u["cash"] -= bet
        res_text += f"\n😢 **Tróc vẩy!** Mất `-{bet:,} $`"
        
    await msg.edit(content=res_text)

@bot.command(name="daga")
async def daga_solo_cmd(ctx, bet: int = None):
    cd = check_spam(ctx.author.id, "daga", 1.5)
    if cd > 0: return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")
    if not bet or bet <= 0: return await ctx.send("❌ Cú pháp: `!daga [tiền]`")
    u = get_user(ctx.author.id)
    if u["cash"] < bet: return await ctx.send("❌ Không đủ tiền mặt!")
    
    msg = await ctx.send("🐓 **ĐÁ GÀ TRỰC TUYẾN**\n⚔️ *Hai chiến kê đang lao vào huyết chiến...*")
    await asyncio.sleep(0.8)
    win = random.choice([True, False])
    if win:
        u["cash"] += bet
        await msg.edit(content=f"🐓 **ĐÁ GÀ KẾT QUẢ**\n🏆 Gà của bạn đã hạ gục đối thủ! Nhận `+{bet:,} $`")
    else:
        u["cash"] -= bet
        await msg.edit(content=f"🐓 **ĐÁ GÀ KẾT QUẢ**\n💀 Gà của bạn đã bỏ mạng! Mất `-{bet:,} $`")

@bot.command(name="tuxi")
async def tuxi_solo_cmd(ctx, choice: str = None, bet: int = None):
    cd = check_spam(ctx.author.id, "tuxi", 1.5)
    if cd > 0: return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")
    valid = ["bua", "bao", "keo"]
    if not choice or choice.lower() not in valid or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!tuxi [bua/bao/keo] [tiền]`")
    u = get_user(ctx.author.id)
    if u["cash"] < bet: return await ctx.send("❌ Không đủ tiền mặt!")
    
    bot_choice = random.choice(valid)
    emojis = {"bua": "🪨", "bao": "📄", "keo": "✂️"}
    c = choice.lower()
    if c == bot_choice:
        res = "🤝 **Hòa tiền!**"
    elif (c=="bua" and bot_choice=="keo") or (c=="bao" and bot_choice=="bua") or (c=="keo" and bot_choice=="bao"):
        u["cash"] += bet
        res = f"🎉 **Thắng!** Nhận `+{bet:,} $`"
    else:
        u["cash"] -= bet
        res = f"💸 **Thua!** Mất `-{bet:,} $`"
    await ctx.send(f"✊ Oẳn tù tì: Bạn ra **{emojis[c]}** | Bot ra **{emojis[bot_choice]}**\n{res}")

@bot.command(name="bai")
async def bai_cmd(ctx, bet: int = None):
    cd = check_spam(ctx.author.id, "bai", 1.5)
    if cd > 0: return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")
    if not bet or bet <= 0: return await ctx.send("❌ Cú pháp: `!bai [tiền]`")
    u = get_user(ctx.author.id)
    if u["cash"] < bet: return await ctx.send("❌ Không đủ tiền!")
    
    p_score = random.randint(1, 10)
    b_score = random.randint(1, 10)
    if p_score > b_score:
        u["cash"] += bet
        await ctx.send(f"🃏 Đánh Bài: Bạn ({p_score} điểm) vs Bot ({b_score} điểm) ➔ **Thắng `+{bet:,} $`**")
    elif p_score < b_score:
        u["cash"] -= bet
        await ctx.send(f"🃏 Đánh Bài: Bạn ({p_score} điểm) vs Bot ({b_score} điểm) ➔ **Thua `-{bet:,} $`**")
    else:
        await ctx.send(f"🃏 Đánh Bài: Bạn ({p_score} điểm) vs Bot ({b_score} điểm) ➔ **Hòa!**")

@bot.command(name="duangua")
async def duangua_cmd(ctx, horse: int = None, bet: int = None):
    cd = check_spam(ctx.author.id, "duangua", 1.5)
    if cd > 0: return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")
    if not horse or horse not in [1, 2, 3, 4] or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!duangua [1-4] [tiền]`")
    u = get_user(ctx.author.id)
    if u["cash"] < bet: return await ctx.send("❌ Không đủ tiền!")
    
    winner = random.randint(1, 4)
    msg = await ctx.send("🐎 **ĐUA NGỰA VƯỜN HỒNG**\n🏇 *Các chiến mã đang phi nước đại...*")
    await asyncio.sleep(1.0)
    
    if horse == winner:
        win = bet * 3
        u["cash"] += (win - bet)
        await msg.edit(content=f"🐎 Ngựa số **{winner}** về nhất!\n🎉 **Thắng lớn!** Nhận `+{win:,} $`")
    else:
        u["cash"] -= bet
        await msg.edit(content=f"🐎 Ngựa về nhất là số **{winner}** (Bạn chọn số {horse}).\n💸 **Thua cược!** Mất `-{bet:,} $`")

@bot.command(name="coinflip")
async def coinflip_cmd(ctx, choice: str = None, bet: int = None):
    cd = check_spam(ctx.author.id, "coinflip", 1.5)
    if cd > 0: return await ctx.send(f"⚠️ {ctx.author.mention} Gõ từ từ thôi con vợ! Đợi **{cd}**s nữa!")
    if not choice or choice.lower() not in ["ngua", "saph"] or not bet or bet <= 0:
        return await ctx.send("❌ Cú pháp: `!coinflip [ngua/saph] [tiền]`")
    u = get_user(ctx.author.id)
    if u["cash"] < bet: return await ctx.send("❌ Không đủ tiền!")
    
    res = random.choice(["ngua", "saph"])
    if choice.lower() == res:
        u["cash"] += bet
        await ctx.send(f"🪙 Tung đồng xu ra mặt: **{res.upper()}**\n🎉 **Trúng!** Nhận `+{bet:,} $`")
    else:
        u["cash"] -= bet
        await ctx.send(f"🪙 Tung đồng xu ra mặt: **{res.upper()}**\n💸 **Trật!** Mất `-{bet:,} $`")

# --- NHÓM LỆNH ĐỐI KHÁNG (PVP) ---
@bot.command(name="danhbai")
async def danhbai_pvp(ctx, member: discord.Member = None, bet: int = None):
    if not member or not bet or bet <= 0: return await ctx.send("❌ Cú pháp: `!danhbai @User [tiền]`")
    await ctx.send(f"⚔️ **{ctx.author.name}** đã thách đấu đánh bài với **{member.name}** mức cược `{bet:,} $`!")

@bot.command(name="thachdau")
async def thachdau_pvp(ctx, member: discord.Member = None, bet: int = None):
    if not member or not bet or bet <= 0: return await ctx.send("❌ Cú pháp: `!thachdau @User [tiền]`")
    await ctx.send(f"⚔️ **{ctx.author.name}** phát lệnh thách đấu tay đôi với **{member.name}** cược `{bet:,} $`!")

@bot.command(name="dagapvp")
async def dagapvp_cmd(ctx, member: discord.Member = None, bet: int = None):
    if not member or not bet or bet <= 0: return await ctx.send("❌ Cú pháp: `!dagapvp @User [tiền]`")
    await ctx.send(f"🐓 Trận đá gà đỉnh cao giữa **{ctx.author.name}** và **{member.name}** với mức cược `{bet:,} $` đang được thiết lập!")

@bot.command(name="tuxipvjp")
async def tuxipvjp_cmd(ctx, member: discord.Member = None, bet: int = None):
    if not member or not bet or bet <= 0: return await ctx.send("❌ Cú pháp: `!tuxipvjp @User [tiền]`")
    await ctx.send(f"✊ Sới bạc Oẳn Tù Tì PvP giữa **{ctx.author.name}** và **{member.name}** (`{bet:,} $`) đã sẵn sàng!")

token = os.getenv("BOT_TOKEN")
bot.run(token)
                 
