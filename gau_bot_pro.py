import discord
from discord import app_commands
from aiohttp import web
import asyncio
import re
import time
import os
import sys
import json
import traceback
from datetime import datetime, timezone, timedelta

# Đảm bảo UTF-8 và auto flush log trên Cloud Linux/Windows
sys.stdout.reconfigure(encoding='utf-8')

P1 = "MTU2NDQ2MTAxNTg3MjA0OTIwMg"
P2 = "G6MN38"
P3 = "Bpogi5EwQQQi_x8Zql9y0Q5yC1C1e1PCojzcdw"
STUDIO_TOKEN = f"{P1}.{P2}.{P3}"

env_token = os.environ.get('DISCORD_TOKEN', '').strip()
if env_token.startswith(P1):
    TOKEN = env_token
else:
    TOKEN = STUDIO_TOKEN

PORT = int(os.environ.get('PORT', 8080))

GUILD_ID = 1564454825708490867
ROLE_MEMBER_ID = 1564467372700467330
ROLE_ADMIN_ID = 1564467364907720734
LOG_CH_ID = 1565547990146486362
GUIDE_CH_ID = 1566405530065305681
GAME_FORUM_CH_ID = 1565547970487783475

BUG_CH_ID = 1566438312212959344
REQ_CH_ID = 1566438314133815369
GUIDE_CHANNEL_ID = 1566598834061320355
ADMIN_CH_ID = 1564476312926556330 # lệnh-quản-lý

VN_TZ = timezone(timedelta(hours=7))

BUGS_DB_FILE = os.path.join(os.path.dirname(__file__), 'bugs_database.json')
VOTES_DB_FILE = os.path.join(os.path.dirname(__file__), 'votes_database.json')

system_logs = []

def log_event(msg):
    now_str = datetime.now(VN_TZ).strftime('%H:%M:%S')
    entry = f"[{now_str}] {msg}"
    print(entry, flush=True)
    system_logs.append(entry)
    if len(system_logs) > 60:
        system_logs.pop(0)

def load_bugs():
    if os.path.exists(BUGS_DB_FILE):
        try:
            with open(BUGS_DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_bugs(bugs):
    try:
        with open(BUGS_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(bugs, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log_event(f"Lỗi lưu bugs: {e}")

def load_votes():
    if os.path.exists(VOTES_DB_FILE):
        try:
            with open(VOTES_DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_votes(votes):
    try:
        with open(VOTES_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(votes, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log_event(f"Lỗi lưu votes: {e}")

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
        "regex": re.compile(r'(lỗi font|loi font|vỡ font|vo font|tràn chữ|tran chu|dịch sai|dich sai|lệch chữ|báo lỗi)', re.IGNORECASE),
        "reply": f"📸 **Cảm ơn bạn đã phản hồi!** Để Studio gom lỗi theo từng game và sửa nhanh nhất, bạn hãy ghé kênh <#{BUG_CH_ID}>, bấm nút **[🚨 Gửi Báo Lỗi Game]** và dán ảnh chụp màn hình vào luồng riêng nha!"
    },
    {
        "id": "launcher_link",
        "regex": re.compile(r'(tải launcher|tai launcher|link launcher|tải ở đâu|tai o dau|download launcher)', re.IGNORECASE),
        "reply": "🚀 **Chào bạn!** Bạn có thể tải trực tiếp file cài đặt **Gấu Cloud Launcher** mới nhất (kèm hướng dẫn 3 bước siêu nhanh) tại kênh <#1566405530065305681> nhé!"
    }
]

spam_tracker = {}
faq_cooldown = {}

# ==================== MODALS ====================
class BugReportModal(discord.ui.Modal, title="🚨 BÁO CÁO LỖI GAME VIỆT HÓA"):
    game_name = discord.ui.TextInput(
        label="Tên tựa game bạn đang chơi",
        placeholder="VD: Valkyria Chronicles, Fleeing the Complex...",
        max_length=80,
        required=True
    )
    location = discord.ui.TextInput(
        label="Đoạn / Vị trí gặp lỗi",
        placeholder="VD: Menu Cài đặt, Bảng kỹ năng, Chap 2...",
        max_length=80,
        required=True
    )
    description = discord.ui.TextInput(
        label="Mô tả chi tiết lỗi",
        placeholder="VD: Chữ bị tràn viền ra ngoài khung, font bị vỡ ô vuông...",
        style=discord.TextStyle.paragraph,
        max_length=800,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        bug_ch = guild.get_channel(BUG_CH_ID)
        if not bug_ch:
            await interaction.followup.send("❌ Không tìm thấy kênh báo lỗi!", ephemeral=True)
            return

        bugs = load_bugs()
        next_num = len(bugs) + 1
        ticket_id = f"{next_num:03d}"

        embed = discord.Embed(
            title=f"🚨 BÁO CÁO LỖI MỚI #{ticket_id}",
            description=f"Một báo cáo lỗi vừa được gửi từ {interaction.user.mention}:",
            color=0xe74c3c
        )
        embed.add_field(name="🎮 Tựa Game", value=f"**{self.game_name.value.strip()}**", inline=True)
        embed.add_field(name="👤 Người Báo", value=interaction.user.mention, inline=True)
        embed.add_field(name="📍 Vị Trí Gặp Lỗi", value=self.location.value.strip(), inline=False)
        embed.add_field(name="📝 Mô Tả Chi Tiết", value=self.description.value.strip(), inline=False)
        embed.add_field(name="📊 Trạng Thái", value="🟡 **Chờ Studio Xử Lý**", inline=False)
        embed.set_footer(text=f"Mã phiếu: #{ticket_id} • {datetime.now(VN_TZ).strftime('%H:%M:%S %d/%m/%Y')}")

        card_view = discord.ui.View(timeout=None)
        btn_fix = discord.ui.Button(
            label="✅ Đã Fix Xong (Dành cho Admin)",
            style=discord.ButtonStyle.success,
            custom_id=f"btn_done_{ticket_id}"
        )
        card_view.add_item(btn_fix)

        msg = await bug_ch.send(embed=embed, view=card_view)

        # Mở luồng thảo luận con dưới bài này để dán ảnh
        try:
            thread = await msg.create_thread(
                name=f"🐛 [{self.game_name.value.strip()}] - #{ticket_id} ({interaction.user.name})",
                auto_archive_duration=1440
            )
            await thread.send(
                f"📸 Chào {interaction.user.mention}! Báo cáo lỗi cho game **{self.game_name.value.strip()}** đã được ghi nhận.\n"
                f"👉 **Bạn hãy bấm phím chụp màn hình và dán (Ctrl + V) ảnh chỗ bị lỗi vào ngay đây** để Studio đối chiếu và sửa nhanh nhất nhé!"
            )
            thread_id = thread.id
            thread_mention = thread.mention
        except Exception as e:
            log_event(f"Lỗi tạo thread báo lỗi: {e}")
            thread_id = None
            thread_mention = "kênh báo lỗi"

        # Lưu dữ liệu
        bugs[ticket_id] = {
            "id": ticket_id,
            "game": self.game_name.value.strip(),
            "location": self.location.value.strip(),
            "desc": self.description.value.strip(),
            "user_id": interaction.user.id,
            "user_name": interaction.user.name,
            "status": "pending",
            "time": datetime.now(VN_TZ).strftime('%d/%m/%Y %H:%M'),
            "msg_id": msg.id,
            "thread_id": thread_id,
            "jump_url": msg.jump_url
        }
        save_bugs(bugs)

        # Cập nhật bảng gom lỗi của Admin
        await update_admin_dashboard(guild)

        await interaction.followup.send(
            f"✅ **Đã gửi báo cáo lỗi thành công!**\n"
            f"👉 Vui lòng vào luồng {thread_mention} để **dán ảnh chụp màn hình** nhé!",
            ephemeral=True
        )


class GameRequestModal(discord.ui.Modal, title="💡 ĐỀ XUẤT GAME VIỆT HÓA MỚI"):
    game_name = discord.ui.TextInput(
        label="Tên tựa game bạn muốn Studio dịch",
        placeholder="VD: NieR Automata, Chrono Trigger, Fallout 4...",
        max_length=80,
        required=True
    )
    game_link = discord.ui.TextInput(
        label="Link Steam / Thể loại game",
        placeholder="VD: https://store.steampowered.com/app/... hoặc Nhập vai RPG",
        max_length=150,
        required=False
    )
    reason = discord.ui.TextInput(
        label="Lý do bạn thích hoặc muốn chơi tiếng Việt",
        placeholder="VD: Cốt truyện siêu cuốn, thoại nhiều từ khó, muốn chơi trên PC/Steam Deck...",
        style=discord.TextStyle.paragraph,
        max_length=600,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        req_ch = guild.get_channel(REQ_CH_ID)
        if not req_ch:
            await interaction.followup.send("❌ Không tìm thấy kênh đề xuất!", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"💡 ĐỀ XUẤT GAME MỚI: {self.game_name.value.strip()}",
            color=0x3498db
        )
        embed.add_field(name="🎮 Tựa Game", value=f"**{self.game_name.value.strip()}**", inline=True)
        embed.add_field(name="👤 Người Đề Xuất", value=interaction.user.mention, inline=True)
        if self.game_link.value.strip():
            embed.add_field(name="🔗 Link / Thể Loại", value=self.game_link.value.strip(), inline=False)
        embed.add_field(name="💬 Lý Do Đề Xuất", value=self.reason.value.strip(), inline=False)
        embed.add_field(name="🔥 Lượt Bình Chọn", value="⭐ **1 Vote**", inline=False)
        embed.set_footer(text=f"Bình chọn • {datetime.now(VN_TZ).strftime('%d/%m/%Y')}")

        vote_id = f"req_{int(time.time())}"
        votes = load_votes()
        votes[vote_id] = {
            "game": self.game_name.value.strip(),
            "count": 1,
            "voters": [interaction.user.id]
        }
        save_votes(votes)

        view = discord.ui.View(timeout=None)
        btn_vote = discord.ui.Button(
            label="👍 Vote Thích Game Này (1)",
            style=discord.ButtonStyle.primary,
            custom_id=f"btn_vote_{vote_id}"
        )
        view.add_item(btn_vote)

        await req_ch.send(embed=embed, view=view)
        await interaction.followup.send(f"🎉 Đã gửi đề xuất tựa game **{self.game_name.value.strip()}** lên kênh để anh em cùng vote!", ephemeral=True)


class FindGameRequestModal(discord.ui.Modal, title="🔍 NHỜ GẤU TÌM LINK GAME SẠCH"):
    game_name = discord.ui.TextInput(
        label="Tên tựa game bạn cần tìm",
        placeholder="VD: Black Myth Wukong, Sekiro, Elden Ring, Resident Evil 4...",
        max_length=80,
        required=True
    )
    game_version = discord.ui.TextInput(
        label="Phiên bản bạn mong muốn",
        placeholder="VD: Bản cài sẵn giải nén chơi luôn, Bản Repack nhẹ máy...",
        max_length=80,
        required=False
    )
    notes = discord.ui.TextInput(
        label="Ghi chú thêm (Link, cấu hình máy)",
        placeholder="VD: Cần link Google Drive tốc độ cao, máy RAM 8GB...",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        guide_ch = guild.get_channel(GUIDE_CHANNEL_ID)
        if not guide_ch:
            await interaction.followup.send("❌ Không tìm thấy kênh hướng dẫn cài game!", ephemeral=True)
            return

        gname = self.game_name.value.strip()
        gver = self.game_version.value.strip() or "Bản chuẩn ổn định nhất"
        gnotes = self.notes.value.strip() or "Không có ghi chú thêm"

        import urllib.parse
        q = urllib.parse.quote_plus(gname)
        search_links = (
            f"• [🔍 Link tìm nhanh SteamRIP](https://steamrip.com/?s={q})\n"
            f"• [🔍 Link tìm nhanh FitGirl Repacks](https://fitgirl-repacks.site/?s={q})\n"
            f"• [🔍 Link tìm nhanh Daominhha](https://daominhha.net/?s={q})"
        )

        # 1. Tạo Private Thread (Phòng kín 1:1 chỉ có người này và Admin)
        clean_name = re.sub(r'[^a-zA-Z0-9\s_-]', '', gname)[:20].strip() or "Game"
        thread_title = f"🔒・[{clean_name}]-{interaction.user.name}"[:40]
        try:
            thread = await guide_ch.create_thread(
                name=thread_title,
                type=discord.ChannelType.private_thread,
                auto_archive_duration=1440,
                invitable=False
            )
            await thread.add_user(interaction.user)
        except Exception as e:
            log_event(f"Lỗi tạo private thread: {e}")
            await interaction.followup.send(f"❌ Không thể tạo phòng hỗ trợ riêng: {e}", ephemeral=True)
            return

        # 2. Gửi thẻ thông tin vào phòng riêng kèm nút TỰ ĐÓNG
        embed = discord.Embed(
            title=f"🔒 PHÒNG HỖ TRỢ TÌM GAME 1:1 — {gname.upper()}",
            description=(
                f"Chào mừng {interaction.user.mention} và Ban Quản Trị Studio!\n"
                f"Đây là **phòng kín riêng tư 1:1** để hỗ trợ bạn tìm nguồn game an toàn, "
                f"hoàn toàn sạch mã độc và không lo dính virus đào coin.\n\n"
                f"🎮 **Tựa Game:** **{gname}**\n"
                f"📦 **Phiên Bản Yêu Cầu:** `{gver}`\n"
                f"📝 **Ghi Chú:** {gnotes}\n\n"
                f"🤖 **Gợi Ý Nguồn Sạch Nhanh Từ Bot:**\n{search_links}\n\n"
                f"👉 BQT sẽ sớm gửi link tải an toàn vào đây cho bạn.\n"
                f"**Khi đã nhận được link hoặc tải xong, bạn hoặc BQT chỉ cần bấm nút đỏ bên dưới để đóng và dọn dẹp phòng này nhé!**"
            ),
            color=0x2ecc71
        )
        embed.set_footer(text=f"Phòng hỗ trợ 1:1 • {datetime.now(VN_TZ).strftime('%H:%M %d/%m/%Y')}")

        view = discord.ui.View(timeout=None)
        btn_close = discord.ui.Button(
            label="🔒 Đã Nhận Link & Đóng Phòng",
            style=discord.ButtonStyle.danger,
            custom_id="btn_close_find_game_ticket"
        )
        view.add_item(btn_close)

        await thread.send(f"🔔 {interaction.user.mention} <@&{ROLE_ADMIN_ID}> — Có yêu cầu tìm game mới!", embed=embed, view=view)

        await interaction.followup.send(
            f"🎉 **Đã tạo phòng hỗ trợ riêng 1:1 cho bạn thành công!**\n"
            f"👉 Bạn hãy bấm vào đây để vào phòng: {thread.mention}\n"
            f"*(Chỉ có bạn và Ban Quản Trị mới nhìn thấy phòng này nha!)*",
            ephemeral=True
        )

# ==================== DASHBOARD & BANNERS ====================
async def update_admin_dashboard(guild):
    admin_ch = guild.get_channel(ADMIN_CH_ID)
    if not admin_ch:
        return

    bugs = load_bugs()
    pending_bugs = [b for b in bugs.values() if b.get('status') == 'pending']

    embed = discord.Embed(
        title="🐻 BẢNG TỔNG HỢP BÁO LỖI BẢN DỊCH (TỰ ĐỘNG GOM THEO GAME)",
        description="Bot tự động gom nhóm lỗi theo từng tựa game để Ban Quản Trị xem 1 lần là nắm trọn!",
        color=0xe67e22 if pending_bugs else 0x2ecc71
    )

    if not pending_bugs:
        embed.add_field(
            name="🎉 TÌNH TRẠNG HIỆN TẠI",
            value="🟢 **Tuyệt vời! Hiện tại không có lỗi nào chưa xử lý.**\nToàn bộ các bản Việt hóa của Studio đang hoạt động hoàn hảo!",
            inline=False
        )
    else:
        # Gom lỗi theo từng game
        games_dict = {}
        for b in pending_bugs:
            g = b.get('game', 'Khác').strip().title()
            if g not in games_dict:
                games_dict[g] = []
            games_dict[g].append(b)

        for gname, blist in games_dict.items():
            lines = []
            for b in blist:
                jump = b.get('jump_url', '')
                loc = b.get('location', 'Chung')
                desc = b.get('desc', '')
                uname = b.get('user_name', 'Ẩn danh')
                bid = b.get('id', '???')
                link_text = f"[#{bid}]({jump})" if jump else f"#{bid}"
                lines.append(f"• **{link_text}** `[{loc}]` @{uname}: {desc}")
            embed.add_field(
                name=f"🎮 {gname} ({len(blist)} lỗi đang chờ):",
                value="\n".join(lines[:12]),
                inline=False
            )

        embed.set_footer(text=f"Tổng cộng: {len(pending_bugs)} lỗi đang chờ • Cập nhật lúc {datetime.now(VN_TZ).strftime('%H:%M:%S %d/%m/%Y')}")

    # Tìm tin nhắn dashboard cũ để edit đè, hoặc gửi mới
    try:
        dashboard_msg = None
        async for m in admin_ch.history(limit=25):
            if m.author == bot.user and m.embeds and "BẢNG TỔNG HỢP BÁO LỖI BẢN DỊCH" in (m.embeds[0].title or ""):
                dashboard_msg = m
                break
        if dashboard_msg:
            await dashboard_msg.edit(embed=embed)
        else:
            await admin_ch.send(embed=embed)
    except Exception as e:
        log_event(f"Lỗi cập nhật Admin Dashboard: {e}")


async def ensure_bug_channel_banner(guild):
    bug_ch = guild.get_channel(BUG_CH_ID)
    if not bug_ch:
        return
    banner_msg = None
    try:
        async for m in bug_ch.history(limit=10):
            if m.author == bot.user and m.embeds and "HỘP THƯ TIẾP NHẬN BÁO LỖI" in (m.embeds[0].title or ""):
                banner_msg = m
                break
    except:
        pass

    if not banner_msg:
        embed = discord.Embed(
            title="🐛 HỘP THƯ TIẾP NHẬN BÁO LỖI BẢN DỊCH — GẤU CÔNG TÂM",
            description=(
                "Chào anh em! Trong quá trình chơi game, nếu phát hiện bất kỳ hạt sạn nào như: "
                "**vỡ font chữ, câu dịch khó hiểu, tràn khung hình, hoặc bị văng game**, "
                "anh em hãy bấm nút đỏ bên dưới để gửi báo cáo nhé!\n\n"
                "📌 **HƯỚNG DẪN 3 BƯỚC SIÊU NHANH:**\n"
                "1️⃣ Bấm nút **`[🚨 Gửi Báo Lỗi Game]`** bên dưới.\n"
                "2️⃣ Điền: **Tên game**, **Đoạn bị lỗi** và **Mô tả lỗi**.\n"
                "3️⃣ Bấm **Gửi** ➔ Bot sẽ tạo thẻ báo lỗi và mở luồng riêng để anh em **dán ảnh chụp màn hình** (Ctrl + V).\n\n"
                "❤️ *Mọi đóng góp của anh em đều giúp bản dịch ngày càng hoàn thiện hơn! Cảm ơn anh em rất nhiều!*"
            ),
            color=0xe74c3c
        )
        embed.set_footer(text="Studio Gấu Công Tâm • Tự động gom lỗi theo game")
        view = discord.ui.View(timeout=None)
        btn = discord.ui.Button(
            label="🚨 Gửi Báo Lỗi Game",
            style=discord.ButtonStyle.danger,
            custom_id="btn_open_bug_modal"
        )
        view.add_item(btn)
        await bug_ch.send(embed=embed, view=view)
        log_event("-> Đã gắn Bảng Nút Báo Lỗi vào kênh #🐛・báo-lỗi-bản-dịch")


async def ensure_req_channel_banner(guild):
    req_ch = guild.get_channel(REQ_CH_ID)
    if not req_ch:
        return
    banner_msg = None
    try:
        async for m in req_ch.history(limit=10):
            if m.author == bot.user and m.embeds and "HÒM PHIẾU ĐỀ XUẤT GAME VIỆT HÓA" in (m.embeds[0].title or ""):
                banner_msg = m
                break
    except:
        pass

    if not banner_msg:
        embed = discord.Embed(
            title="💡 HÒM PHIẾU ĐỀ XUẤT GAME VIỆT HÓA — GẤU CÔNG TÂM",
            description=(
                "Anh em đang mong muốn Studio Việt hóa tựa game nào tiếp theo? "
                "Hãy bấm nút xanh bên dưới để gửi đề xuất nhé!\n\n"
                "📌 **CÁCH THỨC BÌNH CHỌN:**\n"
                "1️⃣ Bấm nút **`[💡 Gửi Đề Xuất Game Mới]`** bên dưới.\n"
                "2️⃣ Điền: **Tên game**, **Link Steam / Thể loại**, và **Lý do đề xuất**.\n"
                "3️⃣ Cả cộng đồng sẽ cùng thả tim **`[👍 Vote Thích Game Này]`**. Tựa game nào được nhiều anh em yêu thích nhất, Studio sẽ ưu tiên lên kế hoạch xúc tiến dịch sớm!"
            ),
            color=0x3498db
        )
        embed.set_footer(text="Studio Gấu Công Tâm • Lắng nghe ý kiến cộng đồng")
        view = discord.ui.View(timeout=None)
        btn = discord.ui.Button(
            label="💡 Gửi Đề Xuất Game Mới",
            style=discord.ButtonStyle.primary,
            custom_id="btn_open_req_modal"
        )
        view.add_item(btn)
        await req_ch.send(embed=embed, view=view)
        log_event("-> Đã gắn Bảng Nút Đề Xuất vào kênh #💡・yêu-cầu-việt-hóa")


async def ensure_guide_channel_banner(guild):
    guide_ch = guild.get_channel(GUIDE_CHANNEL_ID)
    if not guide_ch:
        return
    banner_msg = None
    try:
        async for m in guide_ch.history(limit=10):
            if m.author == bot.user and m.embeds and "HỖ TRỢ TÌM NGUỒN GAME SẠCH" in (m.embeds[0].title or ""):
                banner_msg = m
                break
    except:
        pass

    if not banner_msg:
        embed = discord.Embed(
            title="🔍 HỖ TRỢ TÌM NGUỒN GAME SẠCH — GẤU CÔNG TÂM",
            description=(
                "Anh em đang muốn chơi tựa game nào mà **chưa tìm thấy link tải sạch**, "
                "hoặc **sợ dính virus đào coin** khi tải linh tinh trên mạng?\n\n"
                "👉 Hãy bấm vào chiếc nút xanh bên dưới, điền tên tựa game bạn cần tìm. "
                "Bot và Ban Quản Trị Studio sẽ hỗ trợ kiểm tra và tìm kiếm link an toàn giúp bạn ngay lập tức!"
            ),
            color=0x2ecc71
        )
        embed.set_footer(text="Studio Gấu Công Tâm • Cùng nhau chia sẻ - An toàn 100%")
        view = discord.ui.View(timeout=None)
        btn = discord.ui.Button(
            label="🔍 Nhờ Gấu Hỗ Trợ Tìm Game Sạch",
            style=discord.ButtonStyle.success,
            custom_id="btn_open_find_game_modal"
        )
        view.add_item(btn)
        await guide_ch.send(embed=embed, view=view)
        log_event("-> Đã gắn Bảng Nút Nhờ Tìm Game vào kênh #📚・hướng-dẫn-cài-game")


# ==================== BOT CLIENT ====================
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
        log_event("-> Đã đồng bộ toàn bộ Slash Commands vào Server!")

bot = GauClient()

@bot.event
async def on_ready():
    log_event(f"🐻 BOT GẤU CÔNG TÂM PRO ĐANG CHẠY 24/7! (User: {bot.user})")
    
    guild = bot.get_guild(GUILD_ID)
    if guild:
        await ensure_bug_channel_banner(guild)
        await ensure_req_channel_banner(guild)
        await ensure_guide_channel_banner(guild)
        await update_admin_dashboard(guild)

    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Việt Hóa Gấu Công Tâm 🎮 | /trogiup"
        )
    )

@bot.event
async def on_interaction(interaction: discord.Interaction):
    try:
        if interaction.type == discord.InteractionType.component:
            custom_id = interaction.data.get('custom_id', '')
            log_event(f"👉 Nút bấm được nhấn: {custom_id} từ {interaction.user.name}")

        # 7. Bấm nút Đóng Phòng Hỗ Trợ Tìm Game
        if custom_id == 'btn_close_find_game_ticket':
            await interaction.response.send_message(
                "🔒 **Phòng hỗ trợ này đã hoàn thành nhiệm vụ!**\n"
                "Hệ thống sẽ tự động dọn dẹp và xóa phòng sau **3 giây**...\n"
                "❤️ Cảm ơn bạn đã luôn tin tưởng và đồng hành cùng Gấu Công Tâm!"
            )
            await asyncio.sleep(3)
            try:
                if isinstance(interaction.channel, discord.Thread):
                    await interaction.channel.delete()
                    log_event(f"-> Đã xóa và dọn dẹp phòng ticket: {interaction.channel.name}")
            except Exception as e:
                log_event(f"Lỗi xóa phòng ticket: {e}")
            return

        # 6. Bấm nút Nhờ Tìm Game -> Mở Modal Form
        if custom_id == 'btn_open_find_game_modal':
            await interaction.response.send_modal(FindGameRequestModal())
            return

        # 1. Bấm nút Báo Lỗi -> Mở Modal Form
        if custom_id == 'btn_open_bug_modal':
            await interaction.response.send_modal(BugReportModal())
            return

        # 2. Bấm nút Đề Xuất Game -> Mở Modal Form
        if custom_id == 'btn_open_req_modal':
            await interaction.response.send_modal(GameRequestModal())
            return

        # 3. Bấm nút Vote Game Đề Xuất
        if custom_id.startswith('btn_vote_'):
            vote_id = custom_id.replace('btn_vote_', '')
            votes = load_votes()
            if vote_id in votes:
                voters = votes[vote_id].get('voters', [])
                if interaction.user.id in voters:
                    await interaction.response.send_message("❤️ Bạn đã bình chọn cho tựa game này rồi nha!", ephemeral=True)
                    return
                voters.append(interaction.user.id)
                votes[vote_id]['count'] = len(voters)
                save_votes(votes)

                # Edit Embed
                embed = interaction.message.embeds[0]
                for i, field in enumerate(embed.fields):
                    if field.name == "🔥 Lượt Bình Chọn":
                        embed.set_field_at(i, name="🔥 Lượt Bình Chọn", value=f"⭐ **{len(voters)} Votes**", inline=False)
                        break

                view = discord.ui.View(timeout=None)
                btn = discord.ui.Button(
                    label=f"👍 Vote Thích Game Này ({len(voters)})",
                    style=discord.ButtonStyle.primary,
                    custom_id=custom_id
                )
                view.add_item(btn)

                await interaction.response.edit_message(embed=embed, view=view)
                await interaction.followup.send("🎉 Cảm ơn bạn đã bình chọn cho tựa game này!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Dữ liệu bình chọn không tồn tại hoặc đã hết hạn!", ephemeral=True)
            return

        # 4. Admin bấm nút Đã Fix Xong
        if custom_id.startswith('btn_done_'):
            if not interaction.user.guild_permissions.manage_channels:
                await interaction.response.send_message("🚫 Chỉ Ban Quản Trị Studio mới có quyền đánh dấu đã fix xong!", ephemeral=True)
                return

            ticket_id = custom_id.replace('btn_done_', '')
            bugs = load_bugs()
            if ticket_id in bugs:
                bugs[ticket_id]['status'] = 'done'
                save_bugs(bugs)

            # Đổi Embed sang xanh lá
            embed = interaction.message.embeds[0]
            for i, field in enumerate(embed.fields):
                if field.name == "📊 Trạng Thái":
                    embed.set_field_at(i, name="📊 Trạng Thái", value="🟢 **ĐÃ SỬA XONG TRONG BẢN VÁ MỚI**", inline=False)
                    break
            embed.color = 0x2ecc71

            disabled_view = discord.ui.View()
            btn = discord.ui.Button(label="🟢 Đã Fix Xong", style=discord.ButtonStyle.secondary, disabled=True)
            disabled_view.add_item(btn)

            await interaction.response.edit_message(embed=embed, view=disabled_view)
            await update_admin_dashboard(interaction.guild)
            return

        # 5. Nút Đồng Ý Nội Quy Gia Nhập Nhà Gấu
        if custom_id == 'verify_rules':
            await interaction.response.defer(ephemeral=True)
            guild = interaction.guild
            member = interaction.user
            role = guild.get_role(ROLE_MEMBER_ID)

            if not role:
                await interaction.followup.send("❌ Lỗi: Chưa tìm thấy Role Thành Viên Gấu trên server!", ephemeral=True)
                return

            if role in member.roles:
                await interaction.followup.send(
                    "🐻 Bạn đã là **Thành Viên Gấu** rồi nha! Kho Game và Hướng dẫn Launcher đã mở sẵn sàng cho bạn rồi đó!\n\n"
                    "👉 Ghé kênh <#1566405530065305681> để tải **Gấu Cloud Launcher**.\n"
                    "👉 Ghé kênh <#1565547970487783475> để xem kho game và lấy **Mã PIN 5 Số**.\n"
                    f"👉 Ghé kênh <#{BUG_CH_ID}> để báo lỗi bằng nút bấm tiện lợi nếu gặp sự cố.\n\n"
                    "💡 *Mẹo: Gõ lệnh `/trogiup` hoặc `/huongdan` trong khung chat bất cứ lúc nào để Bot hỗ trợ nhé!*",
                    ephemeral=True
                )
            else:
                try:
                    await member.add_roles(role, reason="Đồng ý nội quy qua nút bấm xác thực")
                    log_event(f"-> Đã gán Role Thành Viên Gấu cho {member.name}")
                except Exception as e:
                    log_event(f"Lỗi khi gán Role: {e}")

                await interaction.followup.send(
                    "🎉 **CHÚC MỪNG BẠN ĐÃ GIA NHẬP NHÀ GẤU THÀNH CÔNG!** ❤️\n\n"
                    "Cánh cổng máy chủ đã mở toang trước mắt bạn:\n"
                    "👉 Ghé kênh <#1566405530065305681> để tải **Gấu Cloud Launcher**.\n"
                    "👉 Ghé kênh <#1565547970487783475> để xem kho game và lấy **Mã PIN 5 Số**.\n"
                    "👉 Ghé kênh <#1565547978511613982> để cùng chém gió với anh em nhé!\n\n"
                    "💡 **HƯỚNG DẪN DÙNG LỆNH BOT:**\n"
                    "Trong bất kỳ kênh chat nào, bạn chỉ cần gõ **`/trogiup`** hoặc **`/huongdan`** là Bot sẽ hiện bảng chỉ dẫn ngay lập tức!",
                    ephemeral=True
                )
    except Exception as e:
        log_event(f"❌ LỖI ON_INTERACTION: {e}")
        traceback.print_exc()

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
    embed.add_field(name="🐛 `/baoloi`", value="Xem cách gửi báo cáo lỗi game 1-Click bằng nút bấm tiện lợi.", inline=False)
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

@bot.tree.command(name="baoloi", description="Hướng dẫn gửi báo cáo lỗi bản dịch nhanh chóng")
async def cmd_baoloi(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🐛 HƯỚNG DẪN BÁO LỖI BẢN DỊCH GAME",
        description=f"Để Studio gom lỗi theo từng game và ra bản vá sửa nhanh nhất, bạn chỉ cần ghé kênh:\n👉 <#{BUG_CH_ID}>\nSau đó bấm nút đỏ **`[🚨 Gửi Báo Lỗi Game]`** và dán ảnh chụp màn hình vào nhé!",
        color=0xe74c3c
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="danhsachloi", description="[Admin] Cập nhật và xem Bảng tổng hợp báo lỗi tất cả các game")
async def cmd_danhsachloi(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("🚫 Lệnh này chỉ dành cho Ban Quản Trị Studio!", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    await update_admin_dashboard(interaction.guild)
    await interaction.followup.send(f"✅ Đã đồng bộ và cập nhật Bảng Gom Lỗi tại kênh <#{ADMIN_CH_ID}>!", ephemeral=True)

@bot.tree.command(name="vinhdanh", description="Vinh danh Nhà Tài Trợ và tự động cấp Role VIP (Dành cho Admin)")
@app_commands.describe(
    user="Thành viên đã donate ủng hộ Studio",
    amount="Số tiền ủng hộ (VD: 50.000 VNĐ, 100k, 200k...)",
    message="Lời nhắn gửi từ người ủng hộ (tùy chọn)"
)
async def cmd_vinhdanh(interaction: discord.Interaction, user: discord.Member, amount: str, message: str = "Tiếp lửa cho Studio dịch game"):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("🚫 Chỉ Ban Quản Trị mới có quyền dùng lệnh vinh danh!", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    hall_ch = guild.get_channel(1566603377897636015)
    role_vip = guild.get_role(ROLE_DONATOR_ID if 'ROLE_DONATOR_ID' in globals() else 1564467370758639699)

    # 1. Cấp role VIP Nhà Tài Trợ Vàng
    if role_vip and role_vip not in user.roles:
        try:
            await user.add_roles(role_vip, reason=f"Vinh danh ủng hộ {amount} từ Admin {interaction.user.name}")
            log_event(f"-> Đã trao Role Nhà Tài Trợ Vàng cho {user.name}")
        except Exception as e:
            log_event(f"Lỗi trao Role VIP: {e}")

    # 2. Đăng thẻ vinh danh vào kênh Bảng Vàng
    embed = discord.Embed(
        title="⭐ VINH DANH NHÀ TÀI TRỢ GẤU CÔNG TÂM ⭐",
        description=(
            "🎉 **XIN CHÂN THÀNH CẢM ƠN TẤM LÒNG VÀNG!**\n\n"
            f"Studio Gấu Công Tâm xin trân trọng ghi nhận và tri ân sâu sắc sự ủng hộ quý báu từ chiến hữu {user.mention}:\n\n"
            f"💰 **Số tiền tiếp lửa:** `{amount.strip()}`\n"
            f"💬 **Lời nhắn gửi:** *\"{message.strip()}\"*\n"
            "👑 **Danh hiệu trao tặng:** <@&1564467370758639699>\n\n"
            "❤️ *Sự đồng hành của bạn là nguồn động lực vô giá để Gấu thức đêm mài giũa thêm thật nhiều tựa game Việt hóa đỉnh cao cho cộng đồng!*"
        ),
        color=0xf1c40f
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text=f"Bảng Vàng Tri Ân • {datetime.now(VN_TZ).strftime('%H:%M %d/%m/%Y')}")

    if hall_ch:
        await hall_ch.send(f"🔔 {user.mention} — Bạn vừa được vinh danh trên Bảng Vàng!", embed=embed)

    await interaction.followup.send(
        f"✅ Đã vinh danh {user.mention} ({amount}) thành công và đăng lên kênh <#1566603377897636015>!",
        ephemeral=True
    )

@bot.tree.command(name="ping", description="Kiểm tra trạng thái hoạt động và độ trễ của Bot Gấu")
async def cmd_ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000) if bot.latency else 0
    embed = discord.Embed(
        title="🐻 TRẠNG THÁI HỆ THỐNG GẤU BOT",
        description=f"🟢 **Tình trạng:** Đang chạy 24/7\n📶 **Độ trễ:** `{latency}ms`\n🛡️ **Hệ thống bảo vệ:** Đang bật (Anti-Phishing, Anti-Spam, Auto-FAQ, Auto-Bug-Collector)",
        color=0x2ecc71
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Web Healthcheck
async def health_check(request):
    is_ready = bot.is_ready()
    return web.json_response({
        "status": "online",
        "bot_user": str(bot.user) if is_ready else "connecting",
        "is_ready": is_ready,
        "latency_ms": round(bot.latency * 1000) if is_ready else None,
        "guild": "Viet Hoa Gau Cong Tam",
        "mode": "24/7 Cloud Service"
    })

async def view_logs(request):
    return web.json_response({
        "status": "online",
        "logs": system_logs,
        "token_prefix": TOKEN[:10] + "...",
        "token_len": len(TOKEN),
        "is_ready": bot.is_ready()
    })

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    app.router.add_get("/logs", view_logs)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    log_event(f"Web server healthcheck đã chạy tại port {PORT}")

async def main():
    await start_web_server()
    while True:
        try:
            log_event("🚀 Bắt đầu kết nối Bot vào Discord Gateway...")
            await bot.start(TOKEN)
        except Exception as e:
            tb = traceback.format_exc()
            log_event(f"⚠️ Mất kết nối Discord: {e}\n{tb}")
            await asyncio.sleep(5)

if __name__ == '__main__':
    asyncio.run(main())
