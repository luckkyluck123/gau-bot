import discord
from discord import app_commands
from aiohttp import web
import asyncio
import re
import time
import os
import sys
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding='utf-8')

# Lấy Token an toàn từ Environment Variable
TOKEN = os.environ.get('DISCORD_TOKEN')

if not TOKEN:
    # Nếu chạy local mà chưa set env thì đọc từ file bí mật local
    local_key_file = os.path.join(os.path.dirname(__file__), 'bot_token.secret')
    if os.path.exists(local_key_file):
        with open(local_key_file, 'r', encoding='utf-8') as f:
            TOKEN = f.read().strip()
    else:
        print("Lỗi: Chưa thiết lập DISCORD_TOKEN trong biến môi trường!")
        sys.exit(1)

PORT = int(os.environ.get('PORT', 8080))

GUILD_ID = 1564454825708490867
ROLE_MEMBER_ID = 1564467372700467330
ROLE_ADMIN_ID = 1564467364907720734
LOG_CH_ID = 1565547990146486362
GUIDE_CH_ID = 1566405530065305681
GAME_FORUM_CH_ID = 1565547970487783475

VN_TZ = timezone(timedelta(hours=7))

PHISHING_REGEX = re.compile(
    r'(discorcl|dlscord|disord|discord-app|discord-nitro|nitro-free|steam-community|steamcommuniity|airdrop|claim-nitro|t\.me/|gift-nitro)',
    re.IGNORECASE
)

FAQ_PATTERNS = [
    {
        "id": "pin",
        "regex": re.compile(r'(mã pin|ma pin|mật khẩu|mat khau|mã 5 số|ma 5 so|pass cài|pass game)', re.IGNORECASE),
        "reply": "🔑 **Chào bạn!** Mã PIN 5 số để kích hoạt game trên Launcher được ghim công khai ngay trong bài viết của tựa game đó tại kênh <#1565547970487783475> nha! Bạn chỉ cần vào đúng bài của game đó là thấy mã nhé."
    },
    {
        "id": "crack_license",
        "regex": re.compile(r'(crack|thuốc|thuoc|repack|bản quyền|ban quyen|steam|game pass)', re.IGNORECASE),
        "reply": "✨ **Bạn yên tâm nhé!** Toàn bộ các bản Việt hóa của Studio đều tương thích hoàn hảo 100% với **CẢ BẢN QUYỀN** (Steam, Epic, GOG...) **LẪN BẢN CRACK / THUỐC** (Repack, tải web...). Dù bạn chơi bản nào Launcher cũng tự nhận diện và nạp tiếng Việt chuẩn xác nha!"
    },
    {
        "id": "antivirus",
        "regex": re.compile(r'(virus|trojan|smartscreen|defender|bị chặn|bi chan|run anyway|báo độc)', re.IGNORECASE),
        "reply": "🛡️ **Đừng lo lắng bạn ơi!** Do Launcher tự động can thiệp nạp file Việt hóa vào game nên Windows Defender có thể hiện cảnh báo bảo vệ (*'Windows protected your PC'*). Mã nguồn của Studio đã được quét sạch 100% an toàn, bạn chỉ cần bấm **More info** ➔ chọn **Run anyway** (Chạy dù thế nào đi nữa) là cài ngon lành nhé!"
    },
    {
        "id": "font_bug",
        "regex": re.compile(r'(lỗi font|loi font|vỡ font|vo font|tràn chữ|tran chu|dịch sai|dich sai|lệch chữ)', re.IGNORECASE),
        "reply": "📸 **Cảm ơn bạn đã phản hồi!** Nếu gặp lỗi font, tràn khung hoặc câu từ chưa mượt, bạn hãy chụp ảnh màn hình in-game gửi vào kênh <#1565547972631207986> để Studio ghi nhận và ra bản vá sửa lỗi sớm cho anh em nhé!"
    },
    {
        "id": "launcher_link",
        "regex": re.compile(r'(tải launcher|tai launcher|link launcher|tải ở đâu|tai o dau|download launcher)', re.IGNORECASE),
        "reply": "🚀 **Chào bạn!** Bạn có thể tải trực tiếp file cài đặt **Gấu Cloud Launcher** mới nhất (kèm hướng dẫn 3 bước siêu nhanh) tại kênh <#1566405530065305681> nhé!"
    }
]

spam_tracker = {}
faq_cooldown = {}

class GauClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print("-> Đã đồng bộ toàn bộ Slash Commands vào Server!")

bot = GauClient()

@bot.event
async def on_ready():
    now_str = datetime.now(VN_TZ).strftime('%d/%m/%Y %H:%M:%S')
    print(f"==================================================")
    print(f"🐻 BOT GẤU CÔNG TÂM PRO ĐANG CHẠY TRÊN CLOUD 24/7!")
    print(f"⏰ Thời gian khởi động: {now_str}")
    print(f"👤 Bot: {bot.user} (ID: {bot.user.id})")
    print(f"🌐 Web Server Healthcheck: Port {PORT}")
    print(f"==================================================")
    
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Việt Hóa Gấu Công Tâm 🎮 | /trogiup"
        )
    )

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get('custom_id')
        
        if custom_id == 'verify_rules':
            guild = interaction.guild
            member = interaction.user
            role = guild.get_role(ROLE_MEMBER_ID)
            
            if not role:
                await interaction.response.send_message("❌ Lỗi: Chưa tìm thấy Role Thành Viên Gấu trên server!", ephemeral=True)
                return
                
            if role in member.roles:
                await interaction.response.send_message(
                    "🐻 Bạn đã là **Thành Viên Gấu** rồi nha! Kho Game và Hướng dẫn Launcher đã mở sẵn sàng cho bạn rồi đó!\n"
                    "💡 *Mẹo: Gõ lệnh `/trogiup` hoặc `/huongdan` trong khung chat bất cứ lúc nào để Bot hỗ trợ nhé!*",
                    ephemeral=True
                )
            else:
                await member.add_roles(role, reason="Đồng ý nội quy qua nút bấm xác thực")
                await interaction.response.send_message(
                    "🎉 **CHÚC MỪNG BẠN ĐÃ GIA NHẬP NHÀ GẤU THÀNH CÔNG!** ❤️\n\n"
                    "Cánh cổng máy chủ đã mở toang trước mắt bạn:\n"
                    "👉 Ghé kênh <#1566405530065305681> để tải **Gấu Cloud Launcher**.\n"
                    "👉 Ghé kênh <#1565547970487783475> để xem kho game và lấy **Mã PIN 5 Số**.\n"
                    "👉 Ghé kênh <#1565547978511613982> để cùng chém gió với anh em nhé!\n\n"
                    "💡 **HƯỚNG DẪN DÙNG LỆNH BOT:**\n"
                    "Trong bất kỳ kênh chat nào, bạn chỉ cần gõ **`/trogiup`** hoặc **`/huongdan`** là Bot sẽ hiện bảng chỉ dẫn ngay lập tức!",
                    ephemeral=True
                )

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
        
    guild = message.guild
    if not guild or guild.id != GUILD_ID:
        return

    member = message.author
    content = message.content
    now = time.time()
    now_str = datetime.now(VN_TZ).strftime('%H:%M:%S - %d/%m/%Y')

    # 1. Quét link độc hại
    if PHISHING_REGEX.search(content):
        try:
            await message.delete()
        except:
            pass
        await message.channel.send(
            f"⚠️ **CẢNH BÁO:** {member.mention}, tin nhắn của bạn chứa liên kết đáng ngờ/lừa đảo và đã bị xóa tự động để bảo vệ cộng đồng!"
        )
        return

    # 2. Chặn tag @everyone
    if ('@everyone' in content or '@here' in content) and not member.guild_permissions.administrator:
        try:
            await message.delete()
        except:
            pass
        await message.channel.send(
            f"🚫 {member.mention}, chỉ Ban Quản Trị mới được phép sử dụng thông báo `@everyone`!",
            delete_after=5
        )
        return

    # 3. Chống spam chat
    user_id = member.id
    if user_id not in spam_tracker:
        spam_tracker[user_id] = []
    
    spam_tracker[user_id] = [t for t in spam_tracker[user_id] if now - t < 3.0]
    spam_tracker[user_id].append(now)

    if len(spam_tracker[user_id]) >= 5:
        try:
            await message.delete()
        except:
            pass
        await message.channel.send(
            f"⏳ {member.mention}, bạn đang nhắn quá nhanh! Vui lòng chờ vài giây để tránh làm loãng kênh chat nhé.",
            delete_after=5
        )
        return

    # 4. Trả lời khi được tag (@Gấu Công Tâm)
    if bot.user in message.mentions:
        await message.reply(
            f"🐻 Chào {member.mention}! Mình là **Trợ Lý Bot Gấu Công Tâm** đang trực chiến 24/7. Bạn có thể gõ phím **`/trogiup`** hoặc **`/huongdan`** để mình hỗ trợ ngay nhé!",
            mention_author=True
        )
        return

    # 5. Tự động giải đáp thắc mắc tự nhiên (Auto-FAQ)
    for faq in FAQ_PATTERNS:
        if faq["regex"].search(content):
            last_answered = faq_cooldown.get(faq["id"], 0)
            if now - last_answered > 45:
                faq_cooldown[faq["id"]] = now
                await message.reply(faq["reply"], mention_author=True)
                break

# ==================== SLASH COMMANDS ====================
@bot.tree.command(name="trogiup", description="Xem toàn bộ danh sách lệnh và hướng dẫn sử dụng Bot Gấu")
async def cmd_trogiup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 BẢNG HƯỚNG DẪN LỆNH TRỢ LÝ BOT GẤU",
        description="Chào bạn! Chỉ cần gõ dấu **`/`** vào khung chat, bạn có thể gọi các lệnh tiện ích sau:",
        color=0xf1c40f
    )
    embed.add_field(name="📖 `/huongdan`", value="Xem cách tải Gấu Cloud Launcher, nhập Mã PIN 5 số và xử lý Antivirus.", inline=False)
    embed.add_field(name="🗂️ `/khogame`", value="Lấy đường dẫn trực tiếp đến Kho Game Diễn Đàn và cách nhận Mã PIN 5 số.", inline=False)
    embed.add_field(name="📶 `/ping`", value="Kiểm tra độ trễ mạng và tình trạng sức khỏe 24/7 của Bot.", inline=False)
    embed.set_footer(text="Studio Gấu Công Tâm • Phục vụ tự động 24/7")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="huongdan", description="Xem hướng dẫn tải Gấu Cloud Launcher và cài đặt game 1-Click")
async def cmd_huongdan(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🚀 HƯỚNG DẪN CÀI ĐẶT VIỆT HÓA - GẤU CLOUD LAUNCHER",
        description="Mọi bản Việt hóa của Studio đều tương thích **cả Game Bản Quyền lẫn Game Crack/Repack**!",
        color=0xe67e22
    )
    embed.add_field(name="1️⃣ Bước 1: Mở Launcher", value="Tải và mở **Gấu Cloud Launcher** tại kênh <#1566405530065305681>.", inline=False)
    embed.add_field(name="2️⃣ Bước 2: Nhập Mã PIN 5 Số", value="Bấm **[CÀI ĐẶT VIỆT HÓA]** ➔ Nhập **Mã PIN 5 Số** của game đó (lấy trong bài viết tại <#1565547970487783475>).", inline=False)
    embed.add_field(name="3️⃣ Bước 3: Vào Game", value="Bấm **[VÀO GAME]** để trải nghiệm tiếng Việt trọn vẹn!", inline=False)
    embed.set_footer(text="Việt Hóa Gấu Công Tâm • Miễn phí vì cộng đồng")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="khogame", description="Xem đường dẫn đến Kho Game và cách lấy Mã PIN 5 số")
async def cmd_khogame(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🗂️ KHO GAME VIỆT HÓA STUDIO GẤU CÔNG TÂM",
        description="Toàn bộ các dự án Việt hóa đã phát hành đều được lưu trữ dạng bài viết chi tiết tại kênh Diễn Đàn:\n👉 <#1565547970487783475>",
        color=0x3498db
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="ping", description="Kiểm tra trạng thái hoạt động và độ trễ của Bot Gấu")
async def cmd_ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🐻 TRẠNG THÁI HỆ THỐNG GẤU BOT",
        description=f"🟢 **Tình trạng:** Đang chạy Cloud 24/7\n📶 **Độ trễ:** `{latency}ms`\n🛡️ **Hệ thống bảo vệ:** Đang bật (Anti-Phishing, Anti-Spam, Auto-FAQ)",
        color=0x2ecc71
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Web Healthcheck
async def health_check(request):
    return web.json_response({
        "status": "online",
        "bot": "Gau Cong Tam Pro",
        "guild": "Viet Hoa Gau Cong Tam",
        "mode": "24/7 Cloud Service"
    })

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"-> Web server healthcheck đã chạy tại port {PORT}")

async def main():
    await start_web_server()
    while True:
        try:
            await bot.start(TOKEN)
        except Exception as e:
            print(f"⚠️ Mất kết nối: {e}. Kết nối lại sau 5s...")
            await asyncio.sleep(5)

if __name__ == '__main__':
    asyncio.run(main())
