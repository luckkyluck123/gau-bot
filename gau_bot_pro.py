import discord
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s')
import discord.player

# Vá lỗi pipe buffer underflow trên Windows và Cloud: Đảm bảo luôn đọc đủ 3840 bytes FRAME_SIZE không bị ngắt giữa chừng
def _robust_ffmpeg_read(self) -> bytes:
    target = discord.opus.Encoder.FRAME_SIZE
    buf = bytearray()
    while len(buf) < target:
        try:
            chunk = self._stdout.read(target - len(buf))
            if not chunk:
                break
            buf.extend(chunk)
        except Exception:
            break
    if len(buf) != target:
        self._check_process_returncode()
        return b''
    return bytes(buf)

discord.player.FFmpegPCMAudio.read = _robust_ffmpeg_read






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
STATS_CH_ID = 1573147958138900620 # 📊・thống-kê-máy-chủ
ROLE_VIP_ID = 1564467370758639699 # Nhà Tài Trợ Vàng ⭐
COFFEE_CH_ID = 1565547962548092989 # ☕・ủng-hộ-gấu-ly-cafe
VIP_PIN_CH_ID = 1573158585095954535 # ⭐・kho-pin-nhà-tài-trợ
HALL_OF_FAME_CH_ID = 1566603377897636015 # 🏆・bảng-vàng-tri-ân

SERVER_CONFIGS = {
    1564454825708490867: {
        "name": "Việt Hóa Gấu Công Tâm",
        "bug_ch_id": BUG_CH_ID,
        "req_ch_id": REQ_CH_ID,
        "guide_ch_id": GUIDE_CHANNEL_ID,
        "launcher_ch_id": GUIDE_CH_ID,
        "forum_ch_id": GAME_FORUM_CH_ID,
        "admin_ch_id": ADMIN_CH_ID,
        "vip_pin_ch_id": VIP_PIN_CH_ID,
        "vip_role_id": ROLE_VIP_ID,
        "enable_guide_banner": True,
        "enable_dashboard": True,
    },
    1560143301343060030: {
        "name": "Hantunat VH (🖥️ GAME PC)",
        "bug_ch_id": 1572078860013412422,
        "req_ch_id": 1572078864627269712,
        "guide_ch_id": 1572078846222667868,
        "launcher_ch_id": 1572078837691584582,
        "forum_ch_id": 1572078855483687005,
        "admin_ch_id": None,
        "vip_pin_ch_id": 1573315591094149131,
        "vip_role_id": 1560143703203389470,
        "enable_guide_banner": False,
        "enable_dashboard": False,
    },
}


def get_server_cfg(guild_id):
    return SERVER_CONFIGS.get(guild_id, SERVER_CONFIGS[GUILD_ID])







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







# Nạp static-ffmpeg (đảm bảo 100% có ffmpeg trên cả Windows lẫn Render Linux Cloud)
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
    log_event("-> Đã nạp thành công static-ffmpeg vào PATH hệ thống!")
except Exception as e:
    log_event(f"Cảnh báo nạp static-ffmpeg: {e}")

# Nạp thư viện Opus để mã hóa và phát âm thanh Discord
try:
    if not discord.opus.is_loaded():
        if sys.platform == 'win32':
            opus_path = os.path.join(os.path.dirname(discord.__file__), 'bin', 'libopus-0.x64.dll')
            if os.path.exists(opus_path):
                discord.opus.load_opus(opus_path)
                log_event(f"-> Đã nạp thành công Windows Opus DLL: {opus_path}")
        else:
            # Linux / Render
            import ctypes.util
            candidates = [
                'libopus.so.0',
                'libopus.so',
                '/usr/lib/x86_64-linux-gnu/libopus.so.0',
                '/usr/lib/libopus.so.0',
                '/usr/local/lib/libopus.so',
                'opus'
            ]
            loaded = False
            for cand in candidates:
                try:
                    discord.opus.load_opus(cand)
                    log_event(f"-> Đã nạp thành công Linux Opus: {cand}")
                    loaded = True
                    break
                except Exception:
                    pass
            if not loaded:
                opus_lib = ctypes.util.find_library('opus')
                if opus_lib:
                    try:
                        discord.opus.load_opus(opus_lib)
                        log_event(f"-> Đã nạp thành công Linux Opus qua find_library: {opus_lib}")
                        loaded = True
                    except Exception as e_find:
                        log_event(f"Lỗi nạp opus qua find_library: {e_find}")
    if discord.opus.is_loaded():
        log_event("✅ Thư viện Opus đã sẵn sàng giải mã âm thanh 100%!")
    else:
        log_event("⚠️ Cảnh báo: Opus chưa nạp được trên môi trường này.")
except Exception as e:
    log_event(f"Cảnh báo nạp Opus: {e}")

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


def _is_studio_admin(member) -> bool:
    if not member:
        return False
    perms = getattr(member, "guild_permissions", None)
    if perms and (perms.manage_channels or perms.administrator):
        return True
    return any(getattr(r, "id", 0) == ROLE_ADMIN_ID for r in getattr(member, "roles", []))


def _norm_game_match_text(text: str) -> str:
    cleaned = re.sub(r"[^0-9a-zA-ZÀ-ỹ]+", " ", str(text or "")).strip().lower()
    return re.sub(r"\s+", " ", cleaned)


async def _find_forum_thread_url(guild, forum_ch_id, game_title: str):
    if not guild or not forum_ch_id or not game_title:
        return None
    target_norm = _norm_game_match_text(game_title)
    if len(target_norm) < 3:
        return None
    pat = re.compile(rf"(?:^|\s){re.escape(target_norm)}(?:\s|$)")

    candidates = [
        t for t in getattr(guild, "threads", [])
        if getattr(t, "parent_id", None) == forum_ch_id
    ]
    forum_ch = guild.get_channel(forum_ch_id)
    if forum_ch and hasattr(forum_ch, "archived_threads"):
        try:
            async for t in forum_ch.archived_threads(limit=30):
                candidates.append(t)
        except Exception:
            pass

    for t in candidates:
        t_norm = _norm_game_match_text(getattr(t, "name", ""))
        if pat.search(t_norm):
            return t.jump_url
    return None


def _is_vip_member(user) -> bool:
    if not user:
        return False
    if getattr(user, "guild_permissions", None) and user.guild_permissions.administrator:
        return True
    roles = getattr(user, "roles", []) or []
    if any(r.id in (ROLE_VIP_ID, ROLE_ADMIN_ID) for r in roles):
        return True
    try:
        main_g = bot.get_guild(GUILD_ID)
        if main_g:
            m = main_g.get_member(user.id)
            if m and (m.guild_permissions.administrator or any(r.id in (ROLE_VIP_ID, ROLE_ADMIN_ID) for r in m.roles)):
                return True
    except Exception:
        pass
    return False


def _extract_req_card_info(embed, components, thread=None, fallback_vote_id: str = None):
    vote_id = fallback_vote_id
    total_votes = 1
    comment_url = getattr(thread, "jump_url", None) if thread else None
    game_post_url = None
    has_progress_buttons = False

    if components:
        for row in components:
            for child in getattr(row, "children", []):
                cid = getattr(child, "custom_id", "") or ""
                lbl = getattr(child, "label", "") or ""
                url = getattr(child, "url", None)
                if cid.startswith("btn_vote_"):
                    if not vote_id:
                        vote_id = cid.replace("btn_vote_", "", 1)
                    m_lbl = re.search(r"\((\d+)\)", lbl)
                    if m_lbl:
                        total_votes = int(m_lbl.group(1))
                elif cid.startswith(("btn_req_wip_", "btn_req_done_", "btn_req_reopen_")):
                    has_progress_buttons = True
                    if not vote_id:
                        vote_id = re.sub(r"^btn_req_(?:wip|done|reopen)_", "", cid)
                elif url:
                    if "/channels/" in url and ("Tải Game" in lbl or "Kho Game" in lbl):
                        game_post_url = url
                    elif not comment_url:
                        comment_url = url

    title_raw = (embed.title if embed and embed.title else "") or ""
    game_title = re.sub(
        r"^(?:👑\s*\[ƯU TIÊN VIP\]\s*ĐỀ XUẤT GAME|💡\s*ĐỀ XUẤT GAME MỚI|🛠️\s*ĐANG VIỆT HÓA|✅\s*ĐÃ HOÀN THÀNH)\s*:\s*",
        "",
        title_raw,
        flags=re.IGNORECASE,
    ).strip()
    requester_mention = ""
    status = "open"
    if title_raw.startswith("✅") or (embed and embed.color and embed.color.value == 0x2ECC71):
        status = "done"
    elif title_raw.startswith("🛠️"):
        status = "wip"

    if embed:
        for field in embed.fields:
            fname = field.name or ""
            fval = field.value or ""
            if fname == "🎮 Tựa Game" and fval.strip():
                game_title = fval.strip().strip("*").strip()
            elif fname == "👤 Người Đề Xuất":
                requester_mention = fval.strip()
            elif fname == "🔥 Lượt Bình Chọn":
                m_cnt = re.search(r"(\d+)", fval)
                if m_cnt:
                    total_votes = int(m_cnt.group(1))
            elif fname == "📊 Tiến Độ":
                if "HOÀN THÀNH" in fval.upper() or "🟢" in fval:
                    status = "done"
                elif "STUDIO GẤU ĐANG" in fval.upper() or "🟡" in fval:
                    status = "wip"
                if not game_post_url:
                    m_url = re.search(r"https://discord\.com/channels/\d+/\d+", fval)
                    if m_url:
                        game_post_url = m_url.group(0)

    is_vip_card = ("👑" in title_raw) or ("NHÀ TÀI TRỢ VÀNG" in requester_mention.upper()) or ("👑" in requester_mention)
    return {
        "vote_id": vote_id,
        "game_title": game_title or "Tựa Game",
        "requester_mention": requester_mention,
        "is_vip_card": is_vip_card,
        "total_votes": total_votes,
        "status": status,
        "comment_url": comment_url,
        "game_post_url": game_post_url,
        "has_progress_buttons": has_progress_buttons,
    }


def build_request_card_view(
    vote_id: str,
    total_votes: int,
    comment_url: str = None,
    status: str = "open",
    game_post_url: str = None,
) -> discord.ui.View:
    view = discord.ui.View(timeout=None)
    view.add_item(discord.ui.Button(
        label=f"👍 Vote Thích Game Này ({total_votes})",
        style=discord.ButtonStyle.primary,
        custom_id=f"btn_vote_{vote_id}",
        disabled=(status == "done"),
        row=0,
    ))
    if comment_url:
        view.add_item(discord.ui.Button(
            label="💬 Bình luận",
            style=discord.ButtonStyle.link,
            url=comment_url,
            row=0,
        ))
    if status == "done" and game_post_url:
        view.add_item(discord.ui.Button(
            label="🎮 Tải Game Ngay",
            style=discord.ButtonStyle.link,
            url=game_post_url,
            row=0,
        ))

    if status == "wip":
        view.add_item(discord.ui.Button(
            label="🛠️ Đang Việt Hóa",
            style=discord.ButtonStyle.primary,
            custom_id=f"btn_req_wip_{vote_id}",
            disabled=True,
            row=1,
        ))
        view.add_item(discord.ui.Button(
            label="✅ Hoàn Thành (Admin)",
            style=discord.ButtonStyle.success,
            custom_id=f"btn_req_done_{vote_id}",
            row=1,
        ))
        view.add_item(discord.ui.Button(
            label="🔄 Mở Lại",
            style=discord.ButtonStyle.secondary,
            custom_id=f"btn_req_reopen_{vote_id}",
            row=1,
        ))
    elif status == "done":
        view.add_item(discord.ui.Button(
            label="🟢 Đã Hoàn Thành",
            style=discord.ButtonStyle.success,
            custom_id=f"btn_req_done_{vote_id}",
            disabled=True,
            row=1,
        ))
        view.add_item(discord.ui.Button(
            label="🔄 Mở Lại (Admin)",
            style=discord.ButtonStyle.secondary,
            custom_id=f"btn_req_reopen_{vote_id}",
            row=1,
        ))
    else:
        view.add_item(discord.ui.Button(
            label="🛠️ Đang Làm (Admin)",
            style=discord.ButtonStyle.secondary,
            custom_id=f"btn_req_wip_{vote_id}",
            row=1,
        ))
        view.add_item(discord.ui.Button(
            label="✅ Hoàn Thành (Admin)",
            style=discord.ButtonStyle.success,
            custom_id=f"btn_req_done_{vote_id}",
            row=1,
        ))
    return view


def apply_request_status_to_embed(
    embed: discord.Embed,
    game_title: str,
    status: str,
    actor_mention: str = None,
    game_post_url: str = None,
):
    is_vip_card = ("👑" in (embed.title or "")) or any(
        f.name == "👤 Người Đề Xuất" and ("👑" in (f.value or "") or "NHÀ TÀI TRỢ VÀNG" in (f.value or "").upper())
        for f in embed.fields
    )
    if status == "done":
        embed.title = f"✅ ĐÃ HOÀN THÀNH: {game_title}"[:256]
        embed.color = 0x2ECC71
        status_text = "🟢 **ĐÃ HOÀN THÀNH VIỆT HÓA & LÊN GẤU CLOUD LAUNCHER!**"
        if game_post_url:
            status_text += f"\n👉 **[Bấm vào đây để xem bài viết & lấy Mã PIN tải game]({game_post_url})**"
    elif status == "wip":
        embed.title = f"🛠️ ĐANG VIỆT HÓA: {game_title}"[:256]
        embed.color = 0xF1C40F
        by_txt = f" *(Cập nhật bởi {actor_mention})*" if actor_mention else ""
        status_text = f"🟡 **STUDIO GẤU ĐANG TIẾN HÀNH VIỆT HÓA**{by_txt}"
    elif is_vip_card:
        embed.title = f"👑 [ƯU TIÊN VIP] ĐỀ XUẤT GAME: {game_title}"[:256]
        embed.color = 0xFFAE00
        status_text = "👑 **Đề xuất ưu tiên (Nhà Tài Trợ Vàng ⭐) • Đang mở bình chọn**"
    else:
        embed.title = f"💡 ĐỀ XUẤT GAME MỚI: {game_title}"[:256]
        embed.color = 0x3498DB
        status_text = "🔵 **Đang mở bình chọn**"

    idx_status = next((i for i, f in enumerate(embed.fields) if f.name == "📊 Tiến Độ"), None)
    if idx_status is not None:
        embed.set_field_at(idx_status, name="📊 Tiến Độ", value=status_text, inline=False)
    else:
        embed.add_field(name="📊 Tiến Độ", value=status_text, inline=False)


async def _notify_req_thread_status(msg, game_title: str, requester_mention: str, status: str, game_post_url: str = None, comment_url: str = None):
    if status not in ("wip", "done"):
        return
    req_thread = getattr(msg, "thread", None)
    if not req_thread and comment_url and msg and getattr(msg, "guild", None):
        m_tid = re.search(r"/channels/\d+/(\d+)", comment_url)
        if m_tid:
            tid = int(m_tid.group(1))
            req_thread = msg.guild.get_thread(tid)
            if not req_thread:
                try:
                    req_thread = await msg.guild.fetch_channel(tid)
                except Exception:
                    req_thread = None
    if not req_thread:
        return
    try:
        if getattr(req_thread, "archived", False):
            await req_thread.edit(archived=False)
        who = requester_mention or "anh em"
        if status == "wip":
            note = (
                f"🛠️ **TIN VUI!** {who} ơi, Ban Quản Trị đã tiếp nhận và đang tiến hành Việt hóa "
                f"tựa game **{game_title}** rồi nhé! Anh em cùng hóng ngày ra lò nha!"
            )
        else:
            note = (
                f"🎉 **ĐÃ HOÀN THÀNH VIỆT HÓA!** {who} ơi, tựa game **{game_title}** bạn đề xuất "
                f"đã chính thức hoàn thành 100% và có mặt trên **Gấu Cloud Launcher** rồi đấy!"
            )
            if game_post_url:
                note += f"\n👉 **Vào lấy Mã PIN & tải chơi ngay tại đây:** {game_post_url}"
        await req_thread.send(note)
    except Exception as ex:
        log_event(f"Cảnh báo gửi thông báo vào thread đề xuất ({game_title}): {ex}")


async def _sync_existing_request_cards(guild, req_ch, forum_ch_id):
    synced = 0
    try:
        async for m in req_ch.history(limit=40):
            if m.author != bot.user or not m.embeds:
                continue
            emb = m.embeds[0]
            title_txt = emb.title or ""
            if "HÒM PHIẾU ĐỀ XUẤT" in title_txt:
                continue
            if not any(k in title_txt for k in ("ĐỀ XUẤT GAME MỚI", "ĐANG VIỆT HÓA", "ĐÃ HOÀN THÀNH")):
                continue
            info = _extract_req_card_info(emb, m.components, getattr(m, "thread", None))
            if not info["vote_id"]:
                continue

            target_status = info["status"]
            game_post_url = info["game_post_url"]
            auto_completed = False
            if target_status != "done" and forum_ch_id:
                found_url = await _find_forum_thread_url(guild, forum_ch_id, info["game_title"])
                if found_url:
                    target_status = "done"
                    game_post_url = found_url
                    auto_completed = True

            has_status_field = any(f.name == "📊 Tiến Độ" for f in emb.fields)
            if not info["has_progress_buttons"] or not has_status_field or auto_completed:
                apply_request_status_to_embed(
                    emb,
                    info["game_title"],
                    target_status,
                    game_post_url=game_post_url,
                )
                new_view = build_request_card_view(
                    info["vote_id"],
                    info["total_votes"],
                    comment_url=info["comment_url"],
                    status=target_status,
                    game_post_url=game_post_url,
                )
                await m.edit(embed=emb, view=new_view)
                if auto_completed:
                    await _notify_req_thread_status(
                        m,
                        info["game_title"],
                        info["requester_mention"],
                        "done",
                        game_post_url=game_post_url,
                        comment_url=info["comment_url"],
                    )
                synced += 1
                await asyncio.sleep(0.5)
        if synced:
            log_event(f"-> Đã nâng cấp nút Tiến Độ cho {synced} thẻ đề xuất cũ tại #{req_ch.name}")
    except Exception as ex:
        log_event(f"Cảnh báo đồng bộ thẻ đề xuất cũ ({req_ch.name}): {ex}")







PHISHING_REGEX = re.compile(



    r'(discorcl|dlscord|disord|discord-app|discord-nitro|nitro-free|steam-community|steamcommuniity|airdrop|claim-nitro|t\.me/|gift-nitro|discord\.gg/|discord\.com/invite|quay\s*hũ|nổ\s*hũ|b52|sunwin|rikvip|casino|tài\s*xỉu|rút\s*tiền|crypto\s*bonus|bonus\s*code|activate\s*code)',



    re.IGNORECASE



)







FAQ_PATTERNS = [



    {



        "id": "pin",



        "regex": re.compile(r'(mã pin|ma pin|mật khẩu|mat khau|mã 5 số|ma 5 so|pass cài|pass game|không thấy mã|ko thấy mã|l4m|link4m)', re.IGNORECASE),



        "reply": (
            "🔑 **Chào bạn!** Mã PIN 5 số để kích hoạt game trên Launcher được gắn ngay trong bài viết của từng tựa game tại kênh <#1565547970487783475> nha!\n"
            "💡 **Cách lấy PIN 2 bước cực dễ (miễn phí, không giới hạn lượt):**\n"
            "1️⃣ Bấm link lấy PIN trong bài viết ➔ **Bước 1/2:** chờ **10 giây** ➔ bấm nút **MÀU CAM** **`[➡️ TIẾP TỤC SANG BƯỚC 2/2]`**.\n"
            "2️⃣ **Bước 2/2:** chờ thêm **10 giây** ➔ bấm nút **MÀU CAM** **`[🔓 HIỆN MÃ PIN 5 SỐ NGAY]`** là thấy ngay Mã PIN!\n"
            "⚠️ **Mẹo quan trọng:** *KHÔNG bấm mấy nút \"Download / Tiếp tục\" lạ trong khung quảng cáo! Nếu bấm nút màu cam mà trình duyệt tự bật sang **tab quảng cáo mới** ➔ Bạn CHỈ CẦN **TẮT (ĐÓNG) TAB MỚI ĐÓ** quay lại tab cũ là thấy tiếp Bước 2 / Mã PIN ngay.*\n"
            "⭐ *(Hoặc ủng hộ Gấu từ 30k/tháng tại <#1565547962548092989> để nhận Role **Nhà Tài Trợ Vàng ⭐** mở khóa <#1573158585095954535> xem thẳng toàn bộ Mã PIN 0 giây chờ nhé!)*"
        )



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

ticket_cooldown = {}







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
        user_id = interaction.user.id
        now = time.time()
        if user_id in ticket_cooldown and now - ticket_cooldown[user_id] < 120:
            rem = int(120 - (now - ticket_cooldown[user_id]))
            await interaction.response.send_message(f'⏳ Bạn vừa gửi yêu cầu rồi, vui lòng chờ {rem} giây nữa để tránh spam nhé!', ephemeral=True)
            return
        ticket_cooldown[user_id] = now



        await interaction.response.defer(ephemeral=True)



        guild = interaction.guild

        cfg = get_server_cfg(guild.id if guild else GUILD_ID)

        bug_ch = guild.get_channel(cfg["bug_ch_id"]) if guild else None



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







        # Cập nhật bảng gom lỗi của Admin tại server chính

        primary_guild = bot.get_guild(GUILD_ID)

        if primary_guild:

            await update_admin_dashboard(primary_guild)







        join_view = discord.ui.View()
        if thread:
            join_view.add_item(discord.ui.Button(
                label="👉 Bấm Vào Đây Để Mở Luồng Dán Ảnh Lỗi",
                url=thread.jump_url,
                style=discord.ButtonStyle.link
            ))
            url_text = f"👉 **[BẤM VÀO ĐÂY ĐỂ VÀO LUỒNG DÁN ẢNH CHỤP MÀN HÌNH]({thread.jump_url})**\n\n"
        else:
            url_text = ""

        await interaction.followup.send(
            f"✅ **Đã gửi báo cáo lỗi thành công!**\n\n"
            f"{url_text}"
            f"*(Vui lòng bấm nút link bên dưới để dán ảnh chụp màn hình lỗi cho Studio kiểm tra nhé!)*",
            view=join_view if thread else None,
            ephemeral=True
        )

        # Báo ngay sang kênh #lệnh-quản-lý cho Admin ở server chính
        primary_guild = bot.get_guild(GUILD_ID)
        admin_ch = primary_guild.get_channel(ADMIN_CH_ID) if primary_guild else None
        if admin_ch:
            srv_tag = f" [{guild.name}]" if guild and guild.id != GUILD_ID else ""
            admin_embed = discord.Embed(
                title=f"🚨 CÓ BÁO CÁO LỖI MỚI #{ticket_id}{srv_tag}",
                description=(
                    f"👤 **Người báo:** {interaction.user.mention} (`{interaction.user.name}`)\n"
                    f"🎮 **Game:** **{self.game_name.value.strip()}**\n"
                    f"📍 **Vị trí:** `{self.location.value.strip()}`\n"
                    f"📝 **Mô tả:** {self.description.value.strip()}\n\n"
                    f"👉 **[BẤM VÀO ĐÂY ĐỂ XEM PHIẾU BÁO LỖI]({msg.jump_url})**"
                ),
                color=0xe74c3c
            )
            admin_embed.set_footer(text="Studio Gấu Công Tâm • Quản lý báo lỗi")
            try:
                await admin_ch.send(
                    f"🚨 <@&{ROLE_ADMIN_ID}> Có báo cáo lỗi mới cần kiểm tra: {thread_mention}",
                    embed=admin_embed
                )
            except Exception as e:
                log_event(f"Lỗi gửi alert admin báo lỗi: {e}")











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

        cfg = get_server_cfg(guild.id if guild else GUILD_ID)

        req_ch = guild.get_channel(cfg["req_ch_id"]) if guild else None



        if not req_ch:



            await interaction.followup.send("❌ Không tìm thấy kênh đề xuất!", ephemeral=True)



            return







        is_vip = _is_vip_member(interaction.user)
        init_base_votes = 2 if is_vip else 0
        init_total_votes = 3 if is_vip else 1
        card_title = (
            f"👑 [ƯU TIÊN VIP] ĐỀ XUẤT GAME: {self.game_name.value.strip()}"
            if is_vip
            else f"💡 ĐỀ XUẤT GAME MỚI: {self.game_name.value.strip()}"
        )
        card_color = 0xFFAE00 if is_vip else 0x3498DB
        requester_val = (
            f"{interaction.user.mention} 👑 (**Nhà Tài Trợ Vàng ⭐**)"
            if is_vip
            else interaction.user.mention
        )
        votes_val = "⭐ **3 Votes** *(Đặc quyền VIP +2)*" if is_vip else "⭐ **1 Vote**"
        progress_val = (
            "👑 **Đề xuất ưu tiên (Nhà Tài Trợ Vàng ⭐) • Đang mở bình chọn**"
            if is_vip
            else "🔵 **Đang mở bình chọn**"
        )

        embed = discord.Embed(
            title=card_title[:256],
            color=card_color,
        )
        embed.add_field(name="🎮 Tựa Game", value=f"**{self.game_name.value.strip()}**", inline=True)
        embed.add_field(name="👤 Người Đề Xuất", value=requester_val, inline=True)

        if self.game_link.value.strip():
            embed.add_field(name="🔗 Link / Thể Loại", value=self.game_link.value.strip(), inline=False)

        embed.add_field(name="💬 Lý Do Đề Xuất", value=self.reason.value.strip(), inline=False)
        embed.add_field(name="🔥 Lượt Bình Chọn", value=votes_val, inline=False)
        embed.add_field(name="📊 Tiến Độ", value=progress_val, inline=False)
        embed.set_footer(text=f"Bình chọn • {datetime.now(VN_TZ).strftime('%d/%m/%Y')}")

        vote_id = f"req_{int(time.time())}"
        votes = load_votes()
        votes[vote_id] = {
            "game": self.game_name.value.strip(),
            "base_count": init_base_votes,
            "count": init_total_votes,
            "voters": [interaction.user.id],
            "status": "open",
            "is_vip": is_vip,
        }
        save_votes(votes)

        view = build_request_card_view(vote_id, init_total_votes, comment_url=None, status="open")

        req_msg = await req_ch.send(embed=embed, view=view)

        thread_title = f"💬 Thảo luận: {self.game_name.value.strip()}"[:100]
        req_thread = None
        for arch_min in (10080, 4320, 1440):
            try:
                req_thread = await req_msg.create_thread(
                    name=thread_title,
                    auto_archive_duration=arch_min
                )
                break
            except Exception as tex:
                if arch_min == 1440:
                    log_event(f"Lỗi tạo thread đề xuất game: {tex}")
        if req_thread:
            try:
                await req_thread.send(
                    f"💬 **Khu vực bình luận cho tựa game: {self.game_name.value.strip()}**\n"
                    f"👉 Mời {interaction.user.mention} và anh em cùng bình luận, bổ sung link hoặc đánh giá về game này ngay tại đây nhé!"
                )
                view = build_request_card_view(vote_id, init_total_votes, comment_url=req_thread.jump_url, status="open")
                await req_msg.edit(view=view)
            except Exception as tex:
                log_event(f"Lỗi gắn nút thread đề xuất game: {tex}")

        vip_note = " *(👑 Đã kích hoạt Khung Vàng Kim Ưu Tiên & +3 Votes mở màn cho **Nhà Tài Trợ Vàng ⭐**)*" if is_vip else ""
        await interaction.followup.send(
            f"🎉 Đã gửi đề xuất tựa game **{self.game_name.value.strip()}** lên kênh kèm khung bình luận riêng để anh em cùng vote & thảo luận!{vip_note}",
            ephemeral=True,
        )

        # Báo ngay sang kênh #lệnh-quản-lý cho Admin ở server chính
        primary_guild = bot.get_guild(GUILD_ID)
        admin_ch = primary_guild.get_channel(ADMIN_CH_ID) if primary_guild else None
        if admin_ch:
            srv_tag = f" [{guild.name}]" if guild and guild.id != GUILD_ID else ""
            adm_title = (
                f"👑 [ƯU TIÊN VIP - NHÀ TÀI TRỢ VÀNG]{srv_tag} ĐỀ XUẤT GAME: {self.game_name.value.strip()}"
                if is_vip
                else f"💡 CÓ ĐỀ XUẤT VIỆT HÓA MỚI{srv_tag}: {self.game_name.value.strip()}"
            )
            admin_embed = discord.Embed(
                title=adm_title[:256],
                description=(
                    f"👤 **Người đề xuất:** {requester_val} (`{interaction.user.name}`)\n"
                    f"🎮 **Game:** **{self.game_name.value.strip()}**\n"
                    f"💬 **Lý do:** {self.reason.value.strip()}\n\n"
                    f"👉 **[BẤM VÀO ĐÂY ĐỂ XEM THẺ BÌNH CHỌN TRÊN KÊNH]({req_msg.jump_url})**"
                ),
                color=card_color,
            )
            admin_embed.set_footer(text="Studio Gấu Công Tâm • Quản lý đề xuất")
            try:
                await admin_ch.send(
                    f"{'👑' if is_vip else '💡'} <@&{ROLE_ADMIN_ID}> Có {'Nhà Tài Trợ Vàng ⭐' if is_vip else 'thành viên'} vừa đề xuất game Việt hóa mới!",
                    embed=admin_embed
                )
            except Exception as e:
                log_event(f"Lỗi gửi alert admin đề xuất: {e}")















class InstallHelpRequestModal(discord.ui.Modal, title="🆘 NHỜ ADMIN TÌM GAME & HƯỚNG DẪN CÀI"):

    game_name = discord.ui.TextInput(

        label="Tên tựa game bạn cần tìm hoặc đang cài",

        placeholder="VD: Final Fantasy Resonance, Borderlands 4, Sekiro, Elden Ring...",

        max_length=80,

        required=True

    )

    issue_type = discord.ui.TextInput(

        label="Bạn cần Admin hỗ trợ điều gì?",

        placeholder="VD: Tìm giúp link Google Drive sạch, hoặc hướng dẫn sửa lỗi kẹt mã PIN, văng game...",

        max_length=100,

        required=True

    )

    details = discord.ui.TextInput(

        label="Mô tả chi tiết hoặc lỗi gặp phải (nếu có)",

        placeholder="VD: Em không biết cách tải/giải nén, hoặc cài bị lỗi thiếu dll, nhờ Admin chỉ từng bước...",

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

        issue = self.issue_type.value.strip()

        gdetails = self.details.value.strip() or "Cần Admin hỗ trợ trực tiếp từng bước."



        # 1. Tạo Private Thread (Phòng kín 1:1 chỉ có người này và Admin)

        clean_name = re.sub(r'[^a-zA-Z0-9\s_-]', '', gname)[:16].strip() or "Game"

        thread_title = f"🆘・[Admin-{clean_name}]-{interaction.user.name}"[:40]

        try:

            thread = await guide_ch.create_thread(

                name=thread_title,

                type=discord.ChannelType.private_thread,

                auto_archive_duration=1440,

                invitable=False

            )

            await thread.add_user(interaction.user)

        except Exception as e:

            log_event(f"Lỗi tạo private thread admin support: {e}")

            await interaction.followup.send(f"❌ Không thể tạo phòng hỗ trợ riêng: {e}", ephemeral=True)

            return



        # 2. Gửi thẻ thông tin vào phòng riêng kèm nút ĐÓNG PHÒNG

        embed = discord.Embed(

            title=f"🆘 PHÒNG HỖ TRỢ TRỰC TIẾP CÙNG ADMIN — {gname.upper()}",

            description=(

                f"Chào mừng {interaction.user.mention} và **Bác Gấu (Admin Studio)**!\n"

                f"Đây là **phòng kín hỗ trợ trực tiếp 1:1**. Chỉ có bạn và Ban Quản Trị mới nhìn thấy và trò chuyện trong phòng này.\n\n"

                f"🎮 **Tựa Game:** **{gname}**\n"

                f"📌 **Nhu Cầu Hỗ Trợ:** `{issue}`\n"

                f"📝 **Mô Tả Chi Tiết:** {gdetails}\n\n"

                f"💬 **Bác Gấu (Admin) đã nhận được thông báo riêng và sẽ vào phòng tìm game / hướng dẫn cài trực tiếp cho bạn ngay!**\n\n"

                f"📸 **MẸO HỖ TRỢ NHANH:**\n"

                f"• Nếu bị lỗi khi cài, bạn hãy **chụp ảnh màn hình lỗi** (nhấn phím `Windows + Shift + S` hoặc `PrintScreen`) rồi **dán trực tiếp vào khung chat này** để Admin bắt bệnh chuẩn xác 100% nhé.\n"

                f"• Hai bên có thể nhắn tin trao đổi thoải mái, gửi link file hoặc UltraViewer/AnyDesk nếu cần hỗ trợ tận tay.\n\n"

                f"🔒 **Phòng sẽ luôn mở cho đến khi bạn cài đặt và chơi game thành công!** Khi xong xuôi, bạn hoặc Admin chỉ cần bấm nút đỏ bên dưới để đóng dọn dẹp phòng này nhé."

            ),

            color=0xe74c3c

        )

        embed.set_footer(text=f"Phòng hỗ trợ Admin 1:1 • {datetime.now(VN_TZ).strftime('%H:%M %d/%m/%Y')}")



        view = discord.ui.View(timeout=None)

        btn_close = discord.ui.Button(

            label="🔒 Hoàn Tất & Đóng Phòng",

            style=discord.ButtonStyle.danger,

            custom_id="btn_close_install_help_ticket"

        )

        view.add_item(btn_close)



        await thread.send(

            f"🔔 {interaction.user.mention} <@&{ROLE_ADMIN_ID}> — Có thành viên cần Admin hỗ trợ tìm game & cài đặt 1-1!",

            embed=embed,

            view=view

        )



        # 3. Gửi thông báo trực tiếp đến kênh #lệnh-quản-lý cho Admin

        admin_ch = guild.get_channel(ADMIN_CH_ID)

        if admin_ch:

            admin_embed = discord.Embed(

                title="🚨 CA NHỜ ADMIN HỖ TRỢ 1-1 (TÌM & CÀI GAME)",

                description=(

                    f"👤 **Thành viên:** {interaction.user.mention} (`{interaction.user.name}`)\n"

                    f"🎮 **Game:** **{gname}**\n"

                    f"📌 **Yêu cầu:** `{issue}`\n"

                    f"📝 **Chi tiết:** {gdetails}\n\n"

                    f"👉 **[BẤM VÀO ĐÂY ĐỂ VÀO PHÒNG CHAT TRỰC TIẾP VỚI BẠN ẤY]({thread.jump_url})**"

                ),

                color=0xe74c3c

            )

            admin_embed.set_footer(text="Hệ thống Ticket Studio Gấu Công Tâm")

            try:

                await admin_ch.send(

                    f"🚨 <@&{ROLE_ADMIN_ID}> Có ca nhờ bạn hỗ trợ tìm & cài game: {thread.mention}",

                    embed=admin_embed

                )

            except Exception as e:

                log_event(f"Lỗi gửi alert admin: {e}")



        join_view = discord.ui.View()
        join_view.add_item(discord.ui.Button(
            label="👉 Bấm Vào Đây Để Mở Phòng Chat Ngay",
            url=thread.jump_url,
            style=discord.ButtonStyle.link
        ))

        await interaction.followup.send(
            f"🎉 **Đã tạo phòng hỗ trợ trực tiếp 1:1 cùng Admin thành công!**\n\n"
            f"📌 **Tên phòng riêng:** `{thread.name}`\n"
            f"👉 **[BẤM VÀO ĐÂY ĐỂ VÀO PHÒNG CHAT TRỰC TIẾP VỚI ADMIN]({thread.jump_url})**\n\n"
            f"*(Bạn chỉ cần bấm nút bên dưới hoặc bấm vào link trên để vào thẳng phòng kín trò chuyện nha!)*",
            view=join_view,
            ephemeral=True
        )





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



            f"• [🔍 Link tìm nhanh DODI Repacks](https://dodi-repacks.site/?s={q})\n"



            f"• [🔍 Link tìm nhanh Ova Games](https://ovagames.com/?s={q})"



        )







        # 1. Tạo Private Thread (Phòng kín 1:1 chỉ có người này và Admin)



        clean_name = re.sub(r'[^a-zA-Z0-9\s_-]', '', gname)[:20].strip() or "Game"



        thread_title = f"🔍・[{clean_name}]-{interaction.user.name}"[:40]



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



            title=f"🔍 PHÒNG HỖ TRỢ TÌM GAME 1:1 — {gname.upper()}",



            description=(



                f"Chào mừng {interaction.user.mention} và **Bác Gấu (Admin Studio)**!\n"



                f"Đây là **phòng kín riêng tư 1:1** để hỗ trợ bạn tìm nguồn game an toàn, "



                f"hoàn toàn sạch mã độc và không lo dính virus đào coin.\n\n"



                f"🎮 **Tựa Game:** **{gname}**\n"



                f"📦 **Phiên Bản Yêu Cầu:** `{gver}`\n"



                f"📝 **Ghi Chú:** {gnotes}\n\n"



                f"🤖 **Gợi Ý Nguồn Sạch Nhanh Từ Bot (Tham khảo):**\n{search_links}\n\n"



                f"💬 **TRAO ĐỔI TRỰC TIẾP VỚI ADMIN BÁC GẤU:**\n"



                f"• Nếu bạn **không biết cách tải từ các trang trên** (sợ quảng cáo, không biết ghép file), hoặc **cần link Google Drive / Fshare tải nhanh**, hãy nhắn ngay vào đây!\n"



                f"• Bác Gấu (Admin) đã nhận được thông báo và sẽ vào trò chuyện, gửi link tải an toàn cho bạn.\n\n"



                f"🔒 **Phòng sẽ luôn mở để trao đổi.** Khi bạn đã nhận được link và tải xong, chỉ cần bấm nút đỏ bên dưới để dọn dẹp phòng này nhé!"



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







        # 3. Gửi thông báo trực tiếp đến kênh #lệnh-quản-lý cho Admin



        admin_ch = guild.get_channel(ADMIN_CH_ID)



        if admin_ch:



            admin_embed = discord.Embed(



                title="🔍 CA NHỜ TÌM LINK TẢI GAME MỚI (1-1)",



                description=(



                    f"👤 **Thành viên:** {interaction.user.mention} (`{interaction.user.name}`)\n"



                    f"🎮 **Game:** **{gname}**\n"



                    f"📦 **Phiên bản:** `{gver}`\n"



                    f"📝 **Ghi chú:** {gnotes}\n\n"



                    f"👉 **[BẤM VÀO ĐÂY ĐỂ VÀO PHÒNG GỬI LINK TẢI CHO BẠN ẤY]({thread.jump_url})**"



                ),



                color=0x2ecc71



            )



            admin_embed.set_footer(text="Hệ thống Ticket Studio Gấu Công Tâm")



            try:



                await admin_ch.send(



                    f"🔍 <@&{ROLE_ADMIN_ID}> Có ca nhờ tìm link game: {thread.mention}",



                    embed=admin_embed



                )



            except Exception as e:



                log_event(f"Lỗi gửi alert admin tìm game: {e}")







        join_view = discord.ui.View()
        join_view.add_item(discord.ui.Button(
            label="👉 Bấm Vào Đây Để Mở Phòng Tra Cứu Ngay",
            url=thread.jump_url,
            style=discord.ButtonStyle.link
        ))

        await interaction.followup.send(
            f"🎉 **Đã tạo phòng hỗ trợ tìm link sạch 1:1 thành công!**\n\n"
            f"📌 **Tên phòng riêng:** `{thread.name}`\n"
            f"👉 **[BẤM VÀO ĐÂY ĐỂ VÀO PHÒNG TRA CỨU LINK SẠCH]({thread.jump_url})**\n\n"
            f"*(Bạn chỉ cần bấm nút link bên dưới hoặc bấm vào link trên để vào thẳng phòng kín tra cứu nha!)*",
            view=join_view,
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


_stats_panel_lock = asyncio.Lock()
_stats_last_topic_ts = 0.0
_stats_last_event_ts = 0.0


def _build_server_stats_view():
    v = discord.ui.View(timeout=None)
    v.add_item(
        discord.ui.Button(
            label="🔄 Làm Mới Số Liệu",
            style=discord.ButtonStyle.primary,
            custom_id="btn_refresh_server_stats",
        )
    )
    v.add_item(
        discord.ui.Button(
            label="🔑 Đổi Mã PIN Toàn Kho Ngay (24h)",
            style=discord.ButtonStyle.success,
            custom_id="btn_force_rotate_pins_24h",
        )
    )
    return v


async def update_server_stats_panel(guild, force_topic: bool = False):
    global _stats_last_topic_ts
    if not guild or guild.id != GUILD_ID:
        return
    stats_ch = guild.get_channel(STATS_CH_ID)
    if not stats_ch:
        return
    async with _stats_panel_lock:
        try:
            approx_total = guild.member_count or 0
            online_cnt = 0
            try:
                fetched_g = await bot.fetch_guild(guild.id, with_counts=True)
                if fetched_g.approximate_member_count:
                    approx_total = fetched_g.approximate_member_count
                if fetched_g.approximate_presence_count is not None:
                    online_cnt = fetched_g.approximate_presence_count
            except Exception as fe:
                log_event(f"-> Cảnh báo fetch_guild counts: {fe}")

            if len(guild.members) < min(10, approx_total):
                try:
                    await guild.chunk(cache=True)
                except Exception:
                    pass

            members = list(guild.members)
            human_members = [m for m in members if not m.bot]
            bot_members = [m for m in members if m.bot]
            total_cnt = max(len(members), approx_total)
            human_cnt = len(human_members) if members else max(0, total_cnt - len(bot_members))
            bot_cnt = len(bot_members)
            online_cnt = min(online_cnt, total_cnt)
            offline_cnt = max(0, total_cnt - online_cnt)
            online_pct = (online_cnt / total_cnt * 100.0) if total_cnt > 0 else 0.0
            offline_pct = (offline_cnt / total_cnt * 100.0) if total_cnt > 0 else 0.0

            verified_cnt = sum(1 for m in human_members if any(r.id == ROLE_MEMBER_ID for r in m.roles))
            unverified_cnt = max(0, human_cnt - verified_cnt)

            now_utc = datetime.now(timezone.utc)
            now_vn = datetime.now(VN_TZ)
            joined_24h = sum(1 for m in human_members if m.joined_at and (now_utc - m.joined_at).total_seconds() <= 86400)
            joined_7d = sum(1 for m in human_members if m.joined_at and (now_utc - m.joined_at).total_seconds() <= 7 * 86400)
            recent_5 = sorted([m for m in human_members if m.joined_at], key=lambda m: m.joined_at, reverse=True)[:5]

            embed = discord.Embed(
                title="📊 THỐNG KÊ THÀNH VIÊN MÁY CHỦ — VIỆT HÓA GẤU CÔNG TÂM",
                description="Theo dõi trực tiếp tổng thành viên, trạng thái **Online / Offline**, tỷ lệ duyệt Nội Quy và lượt gia nhập mới.",
                color=0x2ecc71 if online_cnt > 0 else 0x95a5a6,
            )
            embed.add_field(
                name="👥 Tổng Thành Viên",
                value=f"**`{total_cnt:,}` thành viên**\n👤 Người chơi: **{human_cnt:,}**\n🤖 Bot: **{bot_cnt:,}**",
                inline=True,
            )
            embed.add_field(
                name="🟢 Đang Online",
                value=f"**`{online_cnt:,}`** *({online_pct:.1f}%)*",
                inline=True,
            )
            embed.add_field(
                name="⚫ Đang Offline",
                value=f"**`{offline_cnt:,}`** *({offline_pct:.1f}%)*",
                inline=True,
            )
            embed.add_field(
                name="✅ Đã Duyệt Nội Quy",
                value=f"**`{verified_cnt:,}`** thành viên",
                inline=True,
            )
            embed.add_field(
                name="⏳ Chưa Bấm Duyệt",
                value=f"**`{unverified_cnt:,}`** người",
                inline=True,
            )
            embed.add_field(
                name="📈 Thành Viên Mới",
                value=f"• 24h qua: **`+{joined_24h}`**\n• 7 ngày qua: **`+{joined_7d}`**",
                inline=True,
            )
            if recent_5:
                recent_lines = []
                for m in recent_5:
                    j_vn = m.joined_at.astimezone(VN_TZ).strftime("%d/%m %H:%M")
                    tag = "✅" if any(r.id == ROLE_MEMBER_ID for r in m.roles) else "⏳"
                    recent_lines.append(f"{tag} **{m.display_name}** (`{m.name}`) — `{j_vn}`")
                embed.add_field(
                    name="🆕 5 Thành Viên Vừa Gia Nhập Gần Nhất",
                    value="\n".join(recent_lines),
                    inline=False,
                )
            embed.set_footer(
                text=f"Cập nhật lúc {now_vn.strftime('%H:%M:%S %d/%m/%Y')} (Giờ VN) • Tự động làm mới mỗi 5 phút"
            )

            view = _build_server_stats_view()
            target_msg = None
            async for m in stats_ch.history(limit=20):
                if m.author.id == bot.user.id and m.embeds and "THỐNG KÊ THÀNH VIÊN MÁY CHỦ" in (m.embeds[0].title or ""):
                    target_msg = m
                    break
            if target_msg:
                await target_msg.edit(embed=embed, view=view)
            else:
                await stats_ch.send(embed=embed, view=view)

            now_ts = time.time()
            new_topic = f"👥 Tổng: {total_cnt:,} ({human_cnt:,} người) | 🟢 Online: {online_cnt:,} | ⚫ Offline: {offline_cnt:,} | ✅ Đã duyệt: {verified_cnt:,}"
            if (force_topic or (now_ts - _stats_last_topic_ts >= 600)) and stats_ch.topic != new_topic:
                try:
                    await stats_ch.edit(topic=new_topic)
                    _stats_last_topic_ts = now_ts
                except Exception:
                    pass
        except Exception as ex:
            log_event(f"Lỗi cập nhật bảng thống kê thành viên: {ex}")


async def maintain_server_stats_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            g = bot.get_guild(GUILD_ID)
            if g:
                await update_server_stats_panel(g)
                await refresh_protected_pins_cache(g)
        except Exception as ex:
            log_event(f"Lỗi vòng lặp thống kê máy chủ: {ex}")
        await asyncio.sleep(300)


# ==================== AUTO-DONATE AI VISION & ANTI-PIN-LEAK ====================
import base64
import hashlib
import urllib.request

_GK_PFX = "AQ.Ab8RN6"
_GK_SFXS = [
    "JKaz4xI9AM0km11FzNMlnNvah4e1z4V2HIrVnpD9SzRQ",
    "LprcBNyuZF5WC4spYK-qh2Di5dhln5O4r-qiroJlG7qw",
    "LZX0c6LEqe03Uiw8XQ0aktIZHjRA8zWUS4DTNYXPhmlA",
    "KmGgw-EmtcbmWHoeixCqtg4lW1nbyulU0d-1DFGz-C9g",
]
_used_donate_hashes = set()
_protected_pins_set = {"74108"}


async def refresh_protected_pins_cache(guild):
    global _protected_pins_set
    try:
        vip_ch = guild.get_channel(VIP_PIN_CH_ID)
        if not vip_ch:
            return
        pins = set(_protected_pins_set)
        async for m in vip_ch.history(limit=5):
            for p in re.findall(r"\b(\d{5})\b", m.content or ""):
                pins.add(p)
        _protected_pins_set = pins
    except Exception:
        pass


def _verify_receipt_sync(img_bytes: bytes, mime_type: str) -> dict:
    b64_img = base64.b64encode(img_bytes).decode("ascii")
    prompt = (
        "Bạn là hệ thống kiểm định biên lai chuyển khoản tự động của Studio Gấu Công Tâm. "
        "Hãy đọc kỹ hình ảnh này và kiểm tra:\n"
        "1. Đây có phải màn hình/biên lai chuyển khoản ngân hàng hoặc ví điện tử ĐÃ THÀNH CÔNG không? "
        "(Nếu chỉ là ảnh mã QR trống chưa chuyển, màn hình đang nhập tiền chưa bấm xác nhận, hoặc ảnh game/meme thì is_valid=false).\n"
        "2. Người nhận / Tài khoản nhận trong ảnh có khớp với SỐ TÀI KHOẢN '102880978780' HOẶC TÊN NGƯỜI NHẬN 'TRAN THANH HIEP' / 'TRẦN THANH HIỆP' (VietinBank) không?\n"
        "3. Đọc chính xác số tiền đã chuyển khoản sang số nguyên VNĐ (`amount_vnd`, VD 30.000 đ -> 30000; 50,000 VND -> 50000; 100k -> 100000).\n"
        "Trả về ĐÚNG 1 JSON phẳng: "
        '{"is_valid": true/false, "amount": "số tiền kèm đơn vị VD 50.000đ", "amount_vnd": 50000, "tx_id": "mã giao dịch nếu có", "reason": "lý do ngắn gọn"}'
    )
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inlineData": {"mimeType": mime_type or "image/jpeg", "data": b64_img}},
            ]
        }],
        "generationConfig": {"temperature": 0.0, "responseMimeType": "application/json"},
    }
    raw_body = json.dumps(payload).encode("utf-8")
    for sfx in _GK_SFXS:
        k = _GK_PFX + sfx
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={k}"
        try:
            req = urllib.request.Request(url, data=raw_body, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=18) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            txt = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            txt = re.sub(r"^```(?:json)?|```$", "", txt, flags=re.MULTILINE).strip()
            res = json.loads(txt)
            if isinstance(res, dict):
                return res
        except Exception as e:
            log_event(f"-> Cảnh báo Gemini Vision key: {e}")
            continue
    return {"is_valid": False, "amount": "", "amount_vnd": 0, "tx_id": "", "reason": "AI_BUSY"}


import io as _io

_VIP_LEDGER_TAG = "[VIP_LEDGER_DB]"
_vip_ledger_cache = {}  # str(uid) -> {"total_vnd": int, "expires_at": int (0=perm, >0=unix), "active": bool, "name": str, "txs": list}
_vip_ledger_lock = asyncio.Lock()
_vip_ledger_loaded = False


def _parse_vnd_amount(amount_vnd_raw, amount_str: str = "") -> int:
    try:
        if amount_vnd_raw is not None and str(amount_vnd_raw).strip():
            v = int(float(str(amount_vnd_raw).replace(",", "").strip()))
            if v > 0:
                return v
    except Exception:
        pass
    s = (amount_str or "").lower().strip()
    m_k = re.search(r"(\d+(?:[.,]\d+)?)\s*k\b", s)
    if m_k:
        try:
            return int(float(m_k.group(1).replace(",", ".")) * 1000)
        except Exception:
            pass
    digits = re.sub(r"[^\d]", "", s)
    if digits:
        try:
            return int(digits)
        except Exception:
            pass
    return 0


async def _load_vip_ledger(guild: discord.Guild = None) -> dict:
    global _vip_ledger_cache, _vip_ledger_loaded
    if _vip_ledger_loaded and _vip_ledger_cache:
        return _vip_ledger_cache
    main_g = bot.get_guild(GUILD_ID) or guild
    if main_g:
        admin_ch = main_g.get_channel(ADMIN_CH_ID)
        if admin_ch:
            try:
                async for m in admin_ch.history(limit=50):
                    if m.author.id == bot.user.id and _VIP_LEDGER_TAG in (m.content or ""):
                        if m.attachments:
                            raw = (await m.attachments[0].read()).decode("utf-8", errors="ignore")
                            data = json.loads(raw)
                            if isinstance(data, dict):
                                _vip_ledger_cache = data
                                _vip_ledger_loaded = True
                                return _vip_ledger_cache
                        m_json = re.search(r"```json\s*(\{.*\})\s*```", m.content or "", re.S)
                        if m_json:
                            data = json.loads(m_json.group(1))
                            if isinstance(data, dict):
                                _vip_ledger_cache = data
                                _vip_ledger_loaded = True
                                return _vip_ledger_cache
            except Exception as ex:
                log_event(f"-> Cảnh báo tải VIP Ledger từ Discord: {ex}")
    _vip_ledger_loaded = True
    return _vip_ledger_cache


async def _save_vip_ledger(guild: discord.Guild = None):
    main_g = bot.get_guild(GUILD_ID) or guild
    if not main_g:
        return
    admin_ch = main_g.get_channel(ADMIN_CH_ID)
    if not admin_ch:
        return
    try:
        raw_bytes = json.dumps(_vip_ledger_cache, ensure_ascii=False, indent=2).encode("utf-8")
        old_msg = None
        async for m in admin_ch.history(limit=50):
            if m.author.id == bot.user.id and _VIP_LEDGER_TAG in (m.content or ""):
                old_msg = m
                break
        f_obj = discord.File(_io.BytesIO(raw_bytes), filename="vip_ledger.json")
        summary_cnt = len(_vip_ledger_cache)
        msg_txt = f"{_VIP_LEDGER_TAG} Cơ sở dữ liệu tích lũy & thời hạn **Nhà Tài Trợ Vàng ⭐** ({summary_cnt} thành viên) — *(Không xóa tin nhắn này)*"
        if old_msg:
            try:
                await old_msg.edit(content=msg_txt, attachments=[f_obj])
                return
            except Exception:
                try:
                    await old_msg.delete()
                except Exception:
                    pass
                f_obj = discord.File(_io.BytesIO(raw_bytes), filename="vip_ledger.json")
        await admin_ch.send(content=msg_txt, file=f_obj)
    except Exception as ex:
        log_event(f"-> Cảnh báo lưu VIP Ledger: {ex}")


def _calc_tier_days(amount_vnd: int) -> tuple:
    if amount_vnd >= 200000:
        return (0, "VĨNH VIỄN 👑")
    if amount_vnd >= 100000:
        return (180, "6 Tháng (180 Ngày)")
    if amount_vnd >= 50000:
        return (60, "2 Tháng (60 Ngày)")
    if amount_vnd >= 30000:
        return (30, "1 Tháng (30 Ngày)")
    return (-1, "Ghi Bảng Vàng & Cộng Dồn")


async def grant_vip_and_honor(
    guild: discord.Guild,
    member: discord.Member,
    amount_str: str = "Tùy tâm ❤️",
    note_src: str = "Tự động duyệt Bill AI",
    amount_vnd: int = 0,
    force_permanent: bool = False,
):
    main_g = bot.get_guild(GUILD_ID) or guild
    parsed_vnd = _parse_vnd_amount(amount_vnd, amount_str)
    if force_permanent and parsed_vnd < 200000:
        parsed_vnd = max(parsed_vnd, 200000)

    now_ts = int(time.time())
    async with _vip_ledger_lock:
        ledger = await _load_vip_ledger(main_g)
        uid_k = str(member.id)
        rec = ledger.get(uid_k, {"total_vnd": 0, "expires_at": 0, "active": False, "name": member.name, "txs": []})
        prev_total = int(rec.get("total_vnd") or 0)
        prev_exp = int(rec.get("expires_at") or 0)
        prev_active = bool(rec.get("active", False))

        new_total = prev_total + parsed_vnd
        rec["total_vnd"] = new_total
        rec["name"] = getattr(member, "name", uid_k)
        tx_list = list(rec.get("txs") or [])
        tx_list.append({
            "vnd": parsed_vnd,
            "raw": amount_str,
            "ts": now_ts,
            "src": note_src,
        })
        rec["txs"] = tx_list[-20:]

        days_add, tier_label = _calc_tier_days(parsed_vnd)
        if force_permanent or new_total >= 200000 or (prev_active and prev_exp == 0):
            rec["expires_at"] = 0
            rec["active"] = True
            tier_label = "VĨNH VIỄN 👑 (Tích lũy >= 200.000đ)" if new_total >= 200000 else "VĨNH VIỄN 👑"
            exp_disp = "Vĩnh viễn trọn đời"
            vip_granted = True
        elif days_add > 0:
            base_ts = max(now_ts, prev_exp) if (prev_active and prev_exp > now_ts) else now_ts
            new_exp = base_ts + days_add * 86400
            rec["expires_at"] = new_exp
            rec["active"] = True
            exp_dt = datetime.fromtimestamp(new_exp, VN_TZ).strftime("%d/%m/%Y %H:%M")
            exp_disp = f"{tier_label} (Đến {exp_dt})"
            vip_granted = True
        else:
            # Below 30,000đ and cumulative < 200,000đ: record cumulative & honor on Hall of Fame, keep existing active VIP if any
            if prev_active and (prev_exp == 0 or prev_exp > now_ts):
                vip_granted = True
                exp_disp = "Vĩnh viễn" if prev_exp == 0 else f"Còn hiệu lực đến {datetime.fromtimestamp(prev_exp, VN_TZ).strftime('%d/%m/%Y %H:%M')}"
            else:
                vip_granted = False
                rec["active"] = False
                exp_disp = f"Tích lũy {new_total:,}đ / 200.000đ (Chưa mở VIP — Tối thiểu 30.000đ)"

        ledger[uid_k] = rec
        await _save_vip_ledger(main_g)

    if vip_granted:
        for srv_gid, scfg in SERVER_CONFIGS.items():
            g_srv = bot.get_guild(srv_gid)
            rid_srv = scfg.get("vip_role_id")
            if not g_srv or not rid_srv:
                continue
            r_obj = g_srv.get_role(rid_srv)
            m_obj = g_srv.get_member(member.id)
            if r_obj and m_obj and r_obj not in m_obj.roles:
                try:
                    await m_obj.add_roles(r_obj, reason=f"Ủng hộ Gấu Cà Phê ({amount_str}) - {note_src}")
                except Exception as re_ex:
                    log_event(f"-> Lỗi add Role VIP ({scfg['name']}): {re_ex}")

    hof_ch = main_g.get_channel(HALL_OF_FAME_CH_ID)
    if hof_ch:
        now_vn = datetime.now(VN_TZ).strftime("%d/%m/%Y %H:%M")
        amt_disp = f"{parsed_vnd:,}đ" if parsed_vnd > 0 else (amount_str.strip() or "Ly Cà Phê Ấm Lòng ☕")
        if vip_granted:
            title_hof = "🌟 VINH DANH NHÀ TÀI TRỢ VÀNG MỚI!"
            desc_hof = (
                f"Xin trân trọng cảm ơn Mạnh Thường Quân {member.mention} (**{member.display_name}**) "
                f"đã tiếp lửa ủng hộ **Studio Gấu Công Tâm**!\n\n"
                f"• ☕ **Mức ủng hộ lần này:** **`{amt_disp}`**\n"
                f"• 💰 **Tổng đã tiếp lửa:** **`{new_total:,}đ`** *(Cộng dồn đủ 200.000đ lên Vĩnh Viễn)*\n"
                f"• 👑 **Đặc quyền VIP:** **Nhà Tài Trợ Vàng ⭐ — `{exp_disp}`**\n"
                f"• 🕒 **Thời gian:** `{now_vn}`"
            )
            col_hof = 0xF1C40F
        else:
            title_hof = "☕ TRI ÂN TẤM LÒNG TIẾP LỬA CHO GẤU!"
            desc_hof = (
                f"Xin chân thành cảm ơn {member.mention} (**{member.display_name}**) "
                f"đã mời Gấu tiếp lửa duy trì máy chủ!\n\n"
                f"• ☕ **Mức ủng hộ lần này:** **`{amt_disp}`**\n"
                f"• 💰 **Tổng tích lũy hướng tới Vĩnh Viễn:** **`{new_total:,}đ / 200.000đ`**\n"
                f"• 🕒 **Thời gian:** `{now_vn}`"
            )
            col_hof = 0xE67E22
        embed = discord.Embed(title=title_hof, description=desc_hof, color=col_hof)
        if member.display_avatar:
            embed.set_thumbnail(url=member.display_avatar.url)
        await hof_ch.send(embed=embed)

    if vip_granted:
        # Auto-upgrade any existing open game requests by this VIP member into Golden VIP Cards
        for srv_gid, scfg in SERVER_CONFIGS.items():
            g_obj = bot.get_guild(srv_gid)
            req_id = scfg.get("req_ch_id")
            if not g_obj or not req_id:
                continue
            req_ch = g_obj.get_channel(req_id)
            if not req_ch:
                continue
            try:
                async for m in req_ch.history(limit=40):
                    if m.author != bot.user or not m.embeds:
                        continue
                    emb = m.embeds[0]
                    if "HÒM PHIẾU ĐỀ XUẤT" in (emb.title or "") or "👑" in (emb.title or ""):
                        continue
                    info = _extract_req_card_info(emb, m.components, getattr(m, "thread", None))
                    if f"<@{member.id}>" not in info["requester_mention"] and f"<@!{member.id}>" not in info["requester_mention"]:
                        continue
                    new_votes = info["total_votes"] + 2
                    if info["status"] == "open":
                        emb.title = f"👑 [ƯU TIÊN VIP] ĐỀ XUẤT GAME: {info['game_title']}"[:256]
                        emb.color = 0xFFAE00
                    for idx, fld in enumerate(emb.fields):
                        if fld.name == "👤 Người Đề Xuất":
                            emb.set_field_at(idx, name="👤 Người Đề Xuất", value=f"<@{member.id}> 👑 (**Nhà Tài Trợ Vàng ⭐**)", inline=True)
                        elif fld.name == "🔥 Lượt Bình Chọn":
                            emb.set_field_at(idx, name="🔥 Lượt Bình Chọn", value=f"⭐ **{new_votes} Votes** *(Đặc quyền VIP +2)*", inline=False)
                        elif fld.name == "📊 Tiến Độ" and info["status"] == "open":
                            emb.set_field_at(idx, name="📊 Tiến Độ", value="👑 **Đề xuất ưu tiên (Nhà Tài Trợ Vàng ⭐) • Đang mở bình chọn**", inline=False)
                    if info["vote_id"]:
                        votes = load_votes()
                        if info["vote_id"] in votes:
                            votes[info["vote_id"]]["base_count"] = votes[info["vote_id"]].get("base_count", 0) + 2
                            votes[info["vote_id"]]["count"] = new_votes
                            votes[info["vote_id"]]["is_vip"] = True
                            save_votes(votes)
                    new_v = build_request_card_view(
                        info["vote_id"],
                        new_votes,
                        comment_url=info["comment_url"],
                        status=info["status"],
                        game_post_url=info["game_post_url"],
                    )
                    await m.edit(embed=emb, view=new_v)
            except Exception as ue:
                log_event(f"-> Cảnh báo nâng cấp thẻ đề xuất VIP cho {member.name}: {ue}")

    return {
        "vip_granted": vip_granted,
        "parsed_vnd": parsed_vnd,
        "total_vnd": new_total,
        "tier_label": tier_label,
        "exp_disp": exp_disp,
        "remaining_perm": max(0, 200000 - new_total),
    }


async def maintain_vip_expiry_loop():
    await bot.wait_until_ready()
    await asyncio.sleep(20)
    while not bot.is_closed():
        try:
            main_g = bot.get_guild(GUILD_ID)
            if main_g:
                now_ts = int(time.time())
                expired_uids = []
                async with _vip_ledger_lock:
                    ledger = await _load_vip_ledger(main_g)
                    vip_role = main_g.get_role(ROLE_VIP_ID)
                    for uid_k, rec in ledger.items():
                        exp_at = int(rec.get("expires_at") or 0)
                        if rec.get("active") and exp_at > 0 and now_ts > exp_at:
                            rec["active"] = False
                            expired_uids.append((int(uid_k), int(rec.get("total_vnd") or 0)))
                    if expired_uids:
                        await _save_vip_ledger(main_g)
                for uid, tot_vnd in expired_uids:
                    removed_any = False
                    for srv_gid, scfg in SERVER_CONFIGS.items():
                        g_srv = bot.get_guild(srv_gid)
                        rid_srv = scfg.get("vip_role_id")
                        if not g_srv or not rid_srv:
                            continue
                        r_srv = g_srv.get_role(rid_srv)
                        m_srv = g_srv.get_member(uid)
                        if m_srv and r_srv and r_srv in m_srv.roles:
                            try:
                                await m_srv.remove_roles(r_srv, reason="Hết thời hạn gói Nhà Tài Trợ Vàng")
                                removed_any = True
                            except Exception:
                                pass
                    m = main_g.get_member(uid)
                    if removed_any and m:
                        try:
                            log_event(f"⏰ Đã gỡ Role VIP hết hạn của {m.name} (tổng tích lũy {tot_vnd:,}đ)")
                            rem = max(0, 200000 - tot_vnd)
                            await m.send(
                                f"☕ Chào **{m.display_name}**, thời hạn **Nhà Tài Trợ Vàng ⭐** của bạn tại **Studio Gấu Công Tâm** vừa kết thúc!\n"
                                f"• 💰 Tổng mức đã tiếp lửa tích lũy của bạn hiện là: **`{tot_vnd:,}đ / 200.000đ`** *(còn **`{rem:,}đ`** nữa là lên **VIP Vĩnh Viễn trọn đời**)*.\n"
                                f"• Bạn vẫn tải toàn bộ game hoàn toàn miễn phí qua cổng 2 bước (10s + 10s), hoặc ghé `<#{COFFEE_CH_ID}>` bất cứ lúc nào để gia hạn tiếp nhé! ❤️"
                            )
                        except Exception:
                            pass
        except Exception as ex:
            log_event(f"Lỗi kiểm tra hết hạn VIP: {ex}")
        await asyncio.sleep(3600)


# ==================== 24H AUTOMATED DAILY PIN ROTATION ENGINE ====================
import random
import urllib.parse

_VAULT_K1 = "GAU_STUDIO_MASTER_VAULT_2026"
_VAULT_K2 = "9f4c8e2a1b7d3f6e5a0c9b8d7e6f5a4b"
_BASE_MASTER_PINS = {
    "ff_resonance": "18182",
    "dw3ce_re": "36839",
    "borderlands_4": "46839",
    "blade_of_agony": "26561",
    "valkyria_chronicles": "74108",
}
_GH_T_A = "mXiR56_phg"[::-1]
_GH_T_B = "lsjFLbWvkcLDAtom"[::-1][1:]
_GH_T_C = "ZdqnJ2wX6xI2WCY"[::-1]
_L4M_A = "6affa946a465"
_L4M_B = "85653206a9e3"
_pin_rotation_lock = asyncio.Lock()
_last_checked_pin_date = ""


def _get_gh_token() -> str:
    return os.environ.get("GITHUB_TOKEN", "").strip() or (_GH_T_A + _GH_T_B + _GH_T_C)


def _get_l4m_token() -> str:
    return os.environ.get("LINK4M_API_TOKEN", "").strip() or (_L4M_A + _L4M_B)


def _open_pin_vault(game_id: str, vault_hex: str) -> str:
    if not vault_hex or len(vault_hex) != 10:
        return ""
    try:
        seed = f"{_VAULT_K1}|{_VAULT_K2}|{str(game_id or '').strip().lower()}".encode("utf-8")
        h = hashlib.sha256(seed).digest()
        for _ in range(2048):
            h = hashlib.sha256(h).digest()
        raw = bytes.fromhex(vault_hex)
        pin = bytes(raw[j] ^ h[j] for j in range(5)).decode("ascii", errors="ignore")
        return pin if (len(pin) == 5 and pin.isdigit()) else ""
    except Exception:
        return ""


def _make_pin_envelope(game_id: str, daily_pin: str, master_pin: str, exp_unix: int = 0) -> str:
    seed = f"GAU_ENV_v1|{str(game_id or '').strip().lower()}|{str(daily_pin or '').strip()}".encode("utf-8")
    h = hashlib.sha256(seed).digest()
    for _ in range(4096):
        h = hashlib.sha256(h).digest()
    tag_hex = h[16:24].hex()
    mp = str(master_pin or "").strip().encode("ascii")
    cipher_hex = bytes(mp[j] ^ h[j] for j in range(5)).hex()
    return f"{int(exp_unix)}:{tag_hex}:{cipher_hex}"


def _create_link4m_sync(display_title: str, daily_pin: str) -> str:
    if not daily_pin:
        return ""
    raw = json.dumps({"g": display_title, "p": daily_pin}, ensure_ascii=False).encode("utf-8")
    key = b"GAU_STUDIO_2026_SECRET"
    xored = bytes(b ^ key[i % len(key)] for i, b in enumerate(raw))
    h_tok = base64.urlsafe_b64encode(xored).decode("ascii").rstrip("=")
    return f"https://luckkyluck123.github.io/pin.html#{h_tok}"


def _github_rotate_catalog_sync(force: bool = False) -> dict:
    gh_tok = _get_gh_token()
    headers = {
        "Authorization": f"token {gh_tok}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GauBotPro-24hPinRotator",
    }
    cat_api = "https://api.github.com/repos/luckkyluck123/GauLauncher-Data/contents/catalog.json?ref=main"
    req_get = urllib.request.Request(cat_api, headers=headers)
    with urllib.request.urlopen(req_get, timeout=20) as resp:
        meta = json.loads(resp.read().decode("utf-8"))
    sha = meta["sha"]
    cat = json.loads(base64.b64decode(meta["content"]).decode("utf-8"))

    now_vn = datetime.now(VN_TZ)
    today_vn = now_vn.strftime("%Y-%m-%d")
    if not force and str(cat.get("pin_rotated_date") or "") == today_vn:
        return {"rotated": False, "date": today_vn, "reason": "ALREADY_ROTATED_TODAY"}

    grace_exp = int(time.time()) + 7200  # 2-hour grace window for yesterday's PIN
    used_pins = set(_BASE_MASTER_PINS.values()) | set(_protected_pins_set)
    rotated_games = []

    for g in cat.get("games", []):
        gid = str(g.get("id") or "").strip()
        if not gid:
            continue
        master_pin = _open_pin_vault(gid, str(g.get("pin_vault") or "")) or _BASE_MASTER_PINS.get(gid, "")
        if not master_pin or len(master_pin) != 5:
            continue

        # Generate a fresh 5-digit daily PIN
        new_pin = ""
        for _ in range(50):
            cand = f"{random.randint(10000, 99999)}"
            if cand not in used_pins and len(set(cand)) >= 3:
                new_pin = cand
                break
        if not new_pin:
            new_pin = f"{random.randint(10000, 99999)}"
        used_pins.add(new_pin)

        # Keep previous active envelope (0:tag:cipher) as 2-hour grace envelope
        old_env_raw = str(g.get("pin_envelope") or "").strip()
        old_active = old_env_raw.split("|")[0].strip() if old_env_raw else ""
        grace_part = ""
        if old_active and old_active.count(":") == 2:
            _, o_tag, o_cip = old_active.split(":", 2)
            grace_part = f"{grace_exp}:{o_tag}:{o_cip}"
        else:
            grace_part = _make_pin_envelope(gid, master_pin, master_pin, grace_exp)

        new_active = _make_pin_envelope(gid, new_pin, master_pin, 0)
        g["pin_envelope"] = f"{new_active}|{grace_part}"
        if not g.get("pin_vault"):
            seed = f"{_VAULT_K1}|{_VAULT_K2}|{gid.lower()}".encode("utf-8")
            vh = hashlib.sha256(seed).digest()
            for _ in range(2048):
                vh = hashlib.sha256(vh).digest()
            mp_b = master_pin.encode("ascii")
            g["pin_vault"] = bytes(mp_b[j] ^ vh[j] for j in range(5)).hex()

        if g.get("staging", False):
            continue

        title = str(g.get("title") or gid).strip()
        ver = str(g.get("version") or "1.0.0").strip()
        ver_disp = ver if ver.startswith("v") else f"v{ver}"
        l4m_url = _create_link4m_sync(f"{title} ({ver_disp})", new_pin)
        rotated_games.append({
            "id": gid,
            "title": title,
            "version": ver_disp,
            "daily_pin": new_pin,
            "master_pin": master_pin,
            "link4m_url": l4m_url,
        })

    cat["pin_rotated_date"] = today_vn
    cat["pin_rotated_at"] = now_vn.strftime("%Y-%m-%d %H:%M:%S")
    new_b64 = base64.b64encode(json.dumps(cat, ensure_ascii=False, indent=2).encode("utf-8")).decode("ascii")
    put_payload = {
        "message": f"Auto-rotate 24h Daily PIN envelopes ({today_vn})",
        "content": new_b64,
        "sha": sha,
        "branch": "main",
    }
    req_put = urllib.request.Request(
        "https://api.github.com/repos/luckkyluck123/GauLauncher-Data/contents/catalog.json",
        data=json.dumps(put_payload).encode("utf-8"),
        headers=headers,
        method="PUT",
    )
    with urllib.request.urlopen(req_put, timeout=25) as resp:
        commit_sha = json.loads(resp.read().decode("utf-8")).get("commit", {}).get("sha", "")[:7]

    return {
        "rotated": True,
        "date": today_vn,
        "time_str": now_vn.strftime("%H:%M %d/%m/%Y"),
        "commit": commit_sha,
        "games": rotated_games,
    }


async def rotate_daily_pins_24h(force: bool = False) -> dict:
    global _protected_pins_set, _last_checked_pin_date
    async with _pin_rotation_lock:
        try:
            res = await asyncio.to_thread(_github_rotate_catalog_sync, force)
            if not res.get("rotated"):
                _last_checked_pin_date = str(res.get("date") or _last_checked_pin_date)
                return res

            rotated_games = res.get("games", [])
            _last_checked_pin_date = str(res.get("date") or "")
            new_pins = {g["daily_pin"] for g in rotated_games if g.get("daily_pin")}
            _protected_pins_set = set(_BASE_MASTER_PINS.values()) | _protected_pins_set | new_pins

            # 1. Update #⭐・kho-pin-nhà-tài-trợ across ALL configured Discord servers
            vip_lines = [
                "# ⭐ KHO MÃ PIN ĐẶC QUYỀN — NHÀ TÀI TRỢ VÀNG",
                f"Cảm ơn anh em đã mời Gấu ly cà phê ấm lòng! Dưới đây là **Mã PIN 5 Số trực tiếp (0% quảng cáo)** của toàn bộ game trên **Gấu Cloud Launcher** *(🔄 Đã tự động đổi mới ngày `{res['time_str']}` — Mã PIN cũ còn hiệu lực ân hạn 2 tiếng)*:",
                "",
            ]
            for g in sorted(rotated_games, key=lambda x: x["title"].lower()):
                vip_lines.append(f"> ### 🎮 **{g['title']}** *({g['version']})* ➔ Mã PIN Hôm Nay: **`{g['daily_pin']}`**")
            vip_lines.append("\n❤️ *Chúc anh em Nhà Tài Trợ Vàng chơi game thật vui vẻ!*")
            vip_body = "\n".join(vip_lines)
            for srv_gid, scfg in SERVER_CONFIGS.items():
                g_srv = bot.get_guild(srv_gid)
                vp_id = scfg.get("vip_pin_ch_id")
                if not g_srv or not vp_id:
                    continue
                vip_ch = g_srv.get_channel(vp_id)
                if vip_ch:
                    existing_v = None
                    async for m in vip_ch.history(limit=10):
                        if m.author.id == bot.user.id and "KHO MÃ PIN ĐẶC QUYỀN" in (m.content or ""):
                            existing_v = m
                            break
                    if existing_v:
                        await existing_v.edit(content=vip_body)
                    else:
                        await vip_ch.send(content=vip_body)

            # 2. Update Forum posts in #🗂️・kho-game-việt-hóa across both Discord servers
            updated_threads = 0
            for srv_gid, scfg in SERVER_CONFIGS.items():
                g_obj = bot.get_guild(srv_gid)
                forum_id = scfg.get("forum_ch_id")
                if not g_obj or not forum_id:
                    continue
                forum_ch = g_obj.get_channel(forum_id)
                if not forum_ch:
                    continue
                threads = list(getattr(forum_ch, "threads", []))
                try:
                    async for arch_t in forum_ch.archived_threads(limit=30):
                        threads.append(arch_t)
                except Exception:
                    pass
                for t in threads:
                    t_low = (t.name or "").lower()
                    matched_g = next((rg for rg in rotated_games if rg["title"].lower() in t_low and rg.get("link4m_url")), None)
                    if not matched_g:
                        continue
                    try:
                        starter = await t.fetch_message(t.id)
                        old_c = starter.content or ""
                        new_c = re.sub(
                            r"https://(?:link4m\.(?:net|org|co|com)/[A-Za-z0-9_-]+|luckkyluck123\.github\.io/(?:GauLauncher-Data/)?pin\.html[^\s)\]]*)",
                            matched_g["link4m_url"],
                            old_c,
                        )
                        if new_c != old_c and len(new_c) <= 2000:
                            await starter.edit(content=new_c)
                            updated_threads += 1
                            await asyncio.sleep(0.4)
                    except Exception as te:
                        log_event(f"-> Cảnh báo cập nhật link PIN bài '{t.name}': {te}")

            log_event(
                f"🔑 [24H PIN ROTATION OK] Đã đổi mới {len(rotated_games)} Mã PIN ngày {res['date']} "
                f"(Commit: {res.get('commit')}, Forum posts: {updated_threads})"
            )

            # 3. Notify Admin in #🤖・lệnh-quản-lý
            if main_g:
                admin_ch = main_g.get_channel(ADMIN_CH_ID)
                if admin_ch:
                    lines = [
                        f"• 📅 **Thời điểm xoay khóa:** `{res['time_str']}` *(Commit GitHub: `{res.get('commit')}`)*",
                        f"• ⏳ **Ân hạn PIN cũ:** `2 tiếng` *(Người đang lấy dở qua 00:00 không bị lỗi)*",
                        f"• 🗂️ **Bài Forum đã cập nhật Link4m mới:** `{updated_threads}` bài trên 2 máy chủ",
                        "",
                        "**🔑 Bảng Mã PIN 24h Hôm Nay:**",
                    ]
                    for rg in rotated_games:
                        lines.append(f"• **{rg['title']}**: **`{rg['daily_pin']}`** ➔ {rg.get('link4m_url') or 'N/A'}")
                    emb = discord.Embed(
                        title="🔄 HỆ THỐNG ĐÃ TỰ ĐỘNG XOAY MÃ PIN 24H TOÀN KHO GAME",
                        description="\n".join(lines),
                        color=0x2ecc71,
                    )
                    await admin_ch.send(embed=emb)
            return res
        except Exception as ex:
            log_event(f"❌ Lỗi xoay Mã PIN 24h: {ex}")
            return {"rotated": False, "error": str(ex)}


async def maintain_daily_pin_rotation_loop():
    global _last_checked_pin_date
    await bot.wait_until_ready()
    await asyncio.sleep(10)
    while not bot.is_closed():
        try:
            today_vn = datetime.now(VN_TZ).strftime("%Y-%m-%d")
            if today_vn != _last_checked_pin_date:
                await rotate_daily_pins_24h(force=False)
        except Exception as ex:
            log_event(f"Lỗi vòng lặp kiểm tra xoay Mã PIN 24h: {ex}")
        await asyncio.sleep(60)











async def ensure_bug_channel_banner(guild, bug_ch_id=BUG_CH_ID):

    bug_ch = guild.get_channel(bug_ch_id)



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











async def ensure_req_channel_banner(guild, req_ch_id=REQ_CH_ID):

    req_ch = guild.get_channel(req_ch_id)



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







    embed = discord.Embed(
        title="💡 HÒM PHIẾU ĐỀ XUẤT GAME VIỆT HÓA — GẤU CÔNG TÂM",
        description=(
            "Anh em đang mong muốn Studio Việt hóa tựa game nào tiếp theo? "
            "Hãy bấm nút xanh bên dưới để gửi đề xuất nhé!\n\n"
            "📌 **CÁCH THỨC BÌNH CHỌN & THẢO LUẬN:**\n"
            "1️⃣ Bấm nút **`[💡 Gửi Đề Xuất Game Mới]`** bên dưới.\n"
            "2️⃣ Điền: **Tên game**, **Link Steam / Thể loại**, và **Lý do đề xuất**.\n"
            "3️⃣ Cả cộng đồng sẽ cùng thả tim **`[👍 Vote Thích Game Này]`**. Tựa game nào được nhiều anh em yêu thích nhất, Studio sẽ ưu tiên lên kế hoạch xúc tiến dịch sớm!\n"
            "4️⃣ Bấm nút **`[💬 Bình luận]`** (hoặc thanh **Thảo luận**) dưới mỗi thẻ để góp ý và trò chuyện riêng về tựa game đó!\n\n"
            "👑 **ĐẶC QUYỀN NHÀ TÀI TRỢ VÀNG ⭐:**\n"
            "• Khi **Nhà Tài Trợ Vàng ⭐** gửi đề xuất, thẻ sẽ tự động bật **Khung Vàng Kim `👑 [ƯU TIÊN VIP]`**, gắn huy hiệu **Nhà Tài Trợ Vàng ⭐** cạnh tên và được **tặng sẵn 3 Votes mở màn**!\n"
            "• Mỗi lần **Nhà Tài Trợ Vàng ⭐** bấm bình chọn game bất kỳ đều được tính **x2 Lượt Vote (+2 Votes)**!"
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
    if banner_msg:
        await banner_msg.edit(embed=embed, view=view)
    else:
        await req_ch.send(embed=embed, view=view)
        log_event("-> Đã gắn Bảng Nút Đề Xuất vào kênh #💡・yêu-cầu-việt-hóa")

    cfg = get_server_cfg(guild.id if guild else GUILD_ID)
    await _sync_existing_request_cards(guild, req_ch, cfg.get("forum_ch_id"))











async def ensure_guide_channel_banner(guild):
    guide_ch = guild.get_channel(GUIDE_CHANNEL_ID)
    if not guide_ch:
        return
    banner_msg = None
    try:
        async for m in guide_ch.history(limit=10):
            if m.author == bot.user and m.embeds and any(k in (m.embeds[0].title or '') for k in ['HỖ TRỢ', 'TÌM NGUỒN', 'CÀI ĐẶT', 'TRUNG TÂM']):
                banner_msg = m
                break
    except:
        pass

    desc = (
        "Chào mừng anh em đến với **Studio Gấu Công Tâm**!\n\n"
        "Nhằm bảo vệ an toàn máy tính tối đa và giúp anh em cài đặt game thành công 100%, Studio cung cấp kênh hỗ trợ **Trực Tiếp 1-1** dành riêng để tri ân các **Nhà Tài Trợ Vàng ⭐**:\n\n"
        "👑 **ĐẶC QUYỀN NHÀ TÀI TRỢ VÀNG ⭐ — TẠO PHÒNG KÍN 1-1 CÙNG BÁC GẤU:**\n"
        "• Nhờ Bác Gấu tìm nguồn game sạch (Google Drive/Fshare tốc độ cao), an toàn 100%, không lo dính virus đào coin hay mã độc.\n"
        "• Nhờ Admin hướng dẫn tải & cài đặt trực tiếp từng bước (hoặc qua UltraViewer/AnyDesk).\n"
        "• Xử lý tận gốc mọi lỗi màn hình đen, văng game, thiếu file `.dll`, Windows Defender nuốt file.\n\n"
        "👉 **BẤM NÚT ĐỎ BÊN DƯỚI (Dành cho Nhà Tài Trợ Vàng ⭐):**\n"
        "Bot sẽ tự động mở ngay **1 Phòng Kín Riêng Tư (Private 1:1)** — **Bác Gấu (Admin)** sẽ trực tiếp vào nói chuyện, gửi nguồn game sạch và hướng dẫn tận tình cầm tay chỉ việc cho bạn!\n\n"
        f"☕ *(Chưa có Role **Nhà Tài Trợ Vàng ⭐**? Bạn chỉ cần mời Gấu một ly cà phê tùy tâm tại <#{COFFEE_CH_ID}> — Bot AI tự động duyệt & mở khóa đặc quyền vĩnh viễn trong 3 giây!)*"
    )
    embed = discord.Embed(
        title='👑 TRUNG TÂM TÌM NGUỒN GAME SẠCH & HỖ TRỢ CÀI ĐẶT 1-1 (ĐẶC QUYỀN VIP)',
        description=desc,
        color=0xf1c40f
    )
    embed.set_footer(text='Đặc quyền Vĩnh Viễn dành cho Nhà Tài Trợ Vàng ⭐ • Bấm nút bên dưới để mở phòng 1-1 cùng Admin!')

    view = discord.ui.View(timeout=None)
    btn_install = discord.ui.Button(
        label='👑 Mở Phòng Kín 1-1 Nhờ Gấu Tìm Game & Hỗ Trợ Cài (Đặc Quyền VIP ⭐)',
        style=discord.ButtonStyle.danger,
        custom_id='btn_open_install_help_modal'
    )
    view.add_item(btn_install)



    if banner_msg:

        await banner_msg.edit(embed=embed, view=view)

        log_event("-> Đã cập nhật Bảng Nút Hỗ Trợ Kép vào kênh #📚・hướng-dẫn-cài-game")

    else:

        await guide_ch.send(embed=embed, view=view)

        log_event("-> Đã gắn Bảng Nút Hỗ TrỢ Kép vào kênh #📚・hướng-dẫn-cài-game")





# ==================== BOT CLIENT ====================




# ==================== PHÂN HỆ PHÁT NHẠC 24/7 (BÉ MIU TRỮ TÌNH) ====================
VOICE_MUSIC_CH_NAME = "📻・Nghe Nhạc 24/7"
LOCAL_MUSIC_DIR = r"E:\XUAT_TEXT_GAME\gau_music"
FALLBACK_STREAM_URL = "https://stream.radioparadise.com/mp3-128"

current_music_idx = 0

def get_next_audio_source():
    global current_music_idx
    local_tracks = []
    if os.path.exists(LOCAL_MUSIC_DIR):
        for f in sorted(os.listdir(LOCAL_MUSIC_DIR)):
            if f.lower().endswith(('.mp3', '.m4a', '.flac', '.wav')):
                local_tracks.append(os.path.join(LOCAL_MUSIC_DIR, f))
    
    if local_tracks:
        chosen = local_tracks[current_music_idx % len(local_tracks)]
        current_music_idx += 1
        log_event(f"-> 🐻 Gấu Luckky bắt đầu phát tuyển tập: {os.path.basename(chosen)}")
        raw_audio = discord.FFmpegPCMAudio(chosen)
        return discord.PCMVolumeTransformer(raw_audio, volume=1.0)
    else:
        log_event("-> 🐻 Gấu Luckky kết nối đài phát thanh Radio Paradise quốc tế 24/7...")
        ffmpeg_opts = {
            'before_options': '-vn -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }
        raw_audio = discord.FFmpegPCMAudio(FALLBACK_STREAM_URL, **ffmpeg_opts)
        return discord.PCMVolumeTransformer(raw_audio, volume=1.0)

async def maintain_voice_music(guild):
    # [TIẾT KIỆM 100% BĂNG THÔNG] Đã tắt phát nhạc voice theo yêu cầu của Bác Gấu để không ngốn 5GB Render
    log_event("-> [TIẾT KIỆM BĂNG THÔNG] Tính năng phát nhạc voice 24/7 đã được vô hiệu hóa thành công!")
    return
    """Gấu Luckky ngồi trong phòng 📻・Nghe Nhạc 24/7 phát nhạc Trữ Tình Bolero du dương không bao giờ tắt"""
    log_event("-> Đang khởi động tiến trình phát nhạc Trữ Tình 24/7 của Gấu Luckky...")
    while True:
        try:
            # 1. Đảm bảo phòng voice tồn tại
            voice_ch = discord.utils.get(guild.voice_channels, name=VOICE_MUSIC_CH_NAME)
            if not voice_ch:
                cat = None
                for c in guild.categories:
                    if "THẢO LUẬN" in c.name.upper() or "GIAO LƯU" in c.name.upper():
                        cat = c
                        break
                voice_ch = await guild.create_voice_channel(name=VOICE_MUSIC_CH_NAME, category=cat)
                log_event(f"-> Đã tạo kênh voice: {VOICE_MUSIC_CH_NAME}")

            # 2. Đổi nickname bot thành tên nữ dễ thương
            member = guild.get_member(bot.user.id)
            if member and member.nick != "Gấu Luckky":
                try:
                    await member.edit(nick="Gấu Luckky")
                except:
                    pass

            # 3. Kết nối vào phòng voice
            vc = discord.utils.get(bot.voice_clients, guild=guild)
            if vc is not None:
                if not vc.is_connected():
                    try:
                        await vc.disconnect(force=True)
                    except:
                        pass
                    vc = None
                elif vc.channel.id != voice_ch.id:
                    await vc.move_to(voice_ch)

            if vc is None:
                vc = await voice_ch.connect(reconnect=True, timeout=30.0)
                log_event(f"-> 🐻 Gấu Luckky đã vào phòng {VOICE_MUSIC_CH_NAME}!")

            # 4. Nếu chưa phát nhạc thì phát bài tiếp theo
            if not vc.is_playing():
                def after_playing(err):
                    if err:
                        log_event(f"🐻 Gấu Luckky voice error: {err}")
                    else:
                        log_event("🐻 Gấu Luckky kết thúc bài, chuẩn bị phát bài tiếp theo.")
                
                audio_source = get_next_audio_source()
                vc.play(audio_source, after=after_playing)
                log_event("-> 🐻 Gấu Luckky đang phát nhạc Trữ Tình Bolero 24/7 cực ngọt ngào...")

        except Exception as e:
            log_event(f"Cảnh báo duy trì nhạc voice: {e}")

        await asyncio.sleep(5)


class GauClient(discord.Client):



    def __init__(self):



        intents = discord.Intents.default()



        intents.members = True



        intents.message_content = True
        intents.voice_states = True



        super().__init__(intents=intents)



        self.tree = app_commands.CommandTree(self)







    async def setup_hook(self):

        for gid, scfg in SERVER_CONFIGS.items():

            try:

                g_obj = discord.Object(id=gid)

                self.tree.copy_global_to(guild=g_obj)

                await self.tree.sync(guild=g_obj)

                log_event(f"-> Đã đồng bộ Slash Commands vào {scfg['name']} ({gid})!")

            except Exception as ex:

                log_event(f"-> Cảnh báo sync Slash Commands {gid}: {ex}")







bot = GauClient()







@bot.event



async def on_ready():



    log_event(f"🐻 BOT GẤU CÔNG TÂM PRO ĐANG CHẠY 24/7! (User: {bot.user})")



    



    for gid, scfg in SERVER_CONFIGS.items():

        g = bot.get_guild(gid)

        if not g:

            continue

        try:

            if scfg.get("bug_ch_id"):

                await ensure_bug_channel_banner(g, scfg["bug_ch_id"])

            if scfg.get("req_ch_id"):

                await ensure_req_channel_banner(g, scfg["req_ch_id"])

            if scfg.get("enable_guide_banner"):

                await ensure_guide_channel_banner(g)

            if scfg.get("enable_dashboard"):

                await update_admin_dashboard(g)
                await update_server_stats_panel(g, force_topic=True)

        except Exception as ex:

            log_event(f"-> Cảnh báo khởi tạo banner tại {scfg['name']}: {ex}")

    if not hasattr(bot, '_stats_loop_started'):
        bot._stats_loop_started = True
        asyncio.create_task(maintain_server_stats_loop())

    if not hasattr(bot, '_pin_rotation_loop_started'):
        bot._pin_rotation_loop_started = True
        asyncio.create_task(maintain_daily_pin_rotation_loop())

    if not hasattr(bot, '_vip_expiry_loop_started'):
        bot._vip_expiry_loop_started = True
        asyncio.create_task(maintain_vip_expiry_loop())

    if not hasattr(bot, '_voice_music_started'):
            bot._voice_music_started = True
            # asyncio.create_task(maintain_voice_music(guild)) # Đã tắt phát nhạc để giữ 0 MB băng thông audio







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



        if interaction.type != discord.InteractionType.component:



            return







        custom_id = interaction.data.get('custom_id', '') if interaction.data else ''



        log_event(f"👉 Nút bấm được nhấn: {custom_id} từ {interaction.user.name}")

        if custom_id == 'btn_refresh_server_stats':
            await interaction.response.defer(ephemeral=True)
            g = interaction.guild or bot.get_guild(GUILD_ID)
            if g:
                await update_server_stats_panel(g, force_topic=True)
            await interaction.followup.send("✅ **Đã cập nhật số liệu thành viên mới nhất!**", ephemeral=True)
            return

        if custom_id == 'btn_force_rotate_pins_24h':
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("🚫 Chỉ Admin mới dùng được nút này!", ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            res = await rotate_daily_pins_24h(force=True)
            if res.get("rotated"):
                cnt = len(res.get("games", []))
                await interaction.followup.send(
                    f"🔑 **Đã đổi mới Mã PIN 24h cho toàn bộ `{cnt}` game thành công!**\n"
                    f"• 📦 **GitHub `catalog.json`:** Commit `{res.get('commit')}` *(Ân hạn PIN cũ 2 tiếng)*\n"
                    f"• ⭐ **Đã cập nhật bảng PIN trực tiếp tại:** <#{VIP_PIN_CH_ID}>\n"
                    f"• 🗂️ **Đã cập nhật Link4m mới cho toàn bộ bài đăng tại `#🗂️・kho-game-việt-hóa` trên cả 2 máy chủ!**",
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(f"⚠️ Không thể xoay Mã PIN: `{res}`", ephemeral=True)
            return

        if custom_id == 'btn_open_donate_ticket':
            await interaction.response.defer(ephemeral=True)
            guild = interaction.guild
            member = interaction.user
            coffee_ch = interaction.channel if isinstance(interaction.channel, discord.TextChannel) else (guild.get_channel(COFFEE_CH_ID) if guild else None)
            if not coffee_ch:
                await interaction.followup.send("❌ Không tìm thấy kênh ủng hộ!", ephemeral=True)
                return
            t_name = f"☕・[VIP]-{member.name}"[:40]
            try:
                thread = await coffee_ch.create_thread(
                    name=t_name,
                    type=discord.ChannelType.private_thread,
                    auto_archive_duration=1440,
                    invitable=False,
                )
                await thread.add_user(member)
            except Exception as e:
                await interaction.followup.send(f"❌ Không thể mở phòng gửi bill riêng: {e}", ephemeral=True)
                return

            close_v = discord.ui.View(timeout=None)
            close_v.add_item(discord.ui.Button(
                label="🔒 Đóng Phòng Này",
                style=discord.ButtonStyle.secondary,
                custom_id="btn_close_install_help_ticket",
            ))
            await thread.send(
                f"🌟 **PHÒNG NHẬN ROLE NHÀ TÀI TRỢ VÀNG TỰ ĐỘNG 24/7**\n\n"
                f"Chào {member.mention}! Cảm ơn bạn đã ủng hộ Gấu ly cà phê ấm lòng ❤️\n"
                f"👉 **Bạn hãy gửi (hoặc bấm `Ctrl + V` dán) ảnh chụp màn hình biên lai chuyển khoản thành công** "
                f"tới VietinBank `102880978780` (`TRAN THANH HIEP`) vào ngay phòng kín này.\n\n"
                f"🤖 **Ngay khi bạn gửi ảnh lên, Bot AI của Gấu sẽ tự động đọc bill trong 3 giây để:**\n"
                f"1️⃣ Cấp ngay Role **Nhà Tài Trợ Vàng ⭐** (vĩnh viễn).\n"
                f"2️⃣ Mở khóa ngay phòng **Kho PIN Không Quảng Cáo** tại máy chủ chính **Việt Hóa Gấu Công Tâm** (`https://discord.gg/Ac7mcqCuPB`).\n"
                f"3️⃣ Vinh danh bạn lên **Bảng Vàng Tri Ân**!",
                view=close_v,
            )
            link_v = discord.ui.View()
            link_v.add_item(discord.ui.Button(
                label="👉 Bấm Vào Đây Để Dán Ảnh Bill Chuyển Khoản",
                url=thread.jump_url,
                style=discord.ButtonStyle.link,
            ))
            await interaction.followup.send(
                f"✅ **Đã mở phòng riêng tư nhận Bill cho bạn!**\n👉 **[BẤM VÀO ĐÂY ĐỂ GỬI ẢNH BILL & NHẬN ROLE VIP TỰ ĐỘNG]({thread.jump_url})**",
                view=link_v,
                ephemeral=True,
            )
            return

        if custom_id == 'btn_check_vip_status':
            await interaction.response.defer(ephemeral=True)
            main_g = bot.get_guild(GUILD_ID) or interaction.guild
            uid_k = str(interaction.user.id)
            async with _vip_ledger_lock:
                ledger = await _load_vip_ledger(main_g)
                rec = ledger.get(uid_k, {})
            tot_vnd = int(rec.get("total_vnd") or 0)
            exp_at = int(rec.get("expires_at") or 0)
            is_vip_now = _is_vip_member(interaction.user)
            now_ts = int(time.time())
            if is_vip_now:
                if exp_at == 0:
                    exp_txt = "**VĨNH VIỄN 👑 (Trọn đời)**"
                elif exp_at > now_ts:
                    rem_days = max(1, (exp_at - now_ts + 86399) // 86400)
                    exp_dt = datetime.fromtimestamp(exp_at, VN_TZ).strftime("%d/%m/%Y %H:%M")
                    exp_txt = f"Còn **`{rem_days} ngày`** *(Hết hạn: `{exp_dt}`)*"
                else:
                    exp_txt = "**VĨNH VIỄN 👑**"
            else:
                exp_txt = "Chưa kích hoạt VIP *(Mức tối thiểu: `30.000đ` = 1 tháng)*"
            rem_perm = max(0, 200000 - tot_vnd)
            await interaction.followup.send(
                f"👑 **THÔNG TIN ĐẶC QUYỀN NHÀ TÀI TRỢ VÀNG CỦA {interaction.user.mention}**\n\n"
                f"• ⭐ **Trạng thái VIP:** {exp_txt}\n"
                f"• 💰 **Tổng đã ủng hộ tích lũy:** **`{tot_vnd:,}đ / 200.000đ`**"
                + (f" *(còn **`{rem_perm:,}đ`** nữa là lên **VIP Vĩnh Viễn**!)*" if rem_perm > 0 else " *(Đã đạt mốc Vĩnh Viễn!)*"),
                ephemeral=True,
            )
            return

        if custom_id.startswith('btn_grant_vip_'):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("🚫 Chỉ Admin mới dùng được nút này!", ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            raw_arg = custom_id.replace('btn_grant_vip_', '').strip()
            amt_override = 0
            force_perm = False
            if '_' in raw_arg:
                tag_tier, uid_part = raw_arg.split('_', 1)
                target_uid = int(uid_part)
                if tag_tier == '30k':
                    amt_override = 30000
                elif tag_tier == '50k':
                    amt_override = 50000
                elif tag_tier == '100k':
                    amt_override = 100000
                elif tag_tier == 'perm':
                    amt_override = 200000
                    force_perm = True
            else:
                target_uid = int(raw_arg)
                force_perm = True
            guild = bot.get_guild(GUILD_ID) or interaction.guild
            target_m = guild.get_member(target_uid)
            if not target_m:
                try:
                    target_m = await guild.fetch_member(target_uid)
                except Exception:
                    target_m = None
            if not target_m:
                await interaction.followup.send("❌ Không tìm thấy thành viên này trong server!", ephemeral=True)
                return
            grant_res = await grant_vip_and_honor(
                guild,
                target_m,
                amount_str=f"{amt_override:,}đ" if amt_override else "Ly Cà Phê Ấm Lòng ☕",
                amount_vnd=amt_override,
                note_src=f"Admin {interaction.user.name} duyệt",
                force_permanent=force_perm,
            )
            await interaction.followup.send(
                f"✅ Đã cấp **Nhà Tài Trợ Vàng ⭐** (`{grant_res['exp_disp']}`) cho {target_m.mention}!",
                ephemeral=True,
            )
            return

        if custom_id.startswith('btn_revoke_vip_'):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("🚫 Chỉ Admin mới dùng được nút này!", ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            target_uid = int(custom_id.replace('btn_revoke_vip_', '').strip())
            guild = interaction.guild
            target_m = guild.get_member(target_uid)
            if not target_m:
                try:
                    target_m = await guild.fetch_member(target_uid)
                except Exception:
                    target_m = None
            vip_role = guild.get_role(ROLE_VIP_ID) if guild else None
            if target_m and vip_role and vip_role in target_m.roles:
                await target_m.remove_roles(vip_role, reason=f"Admin {interaction.user.name} thu hồi VIP")
                await interaction.followup.send(f"🚫 Đã thu hồi Role **Nhà Tài Trợ Vàng ⭐** của {target_m.mention}!", ephemeral=True)
            else:
                await interaction.followup.send("ℹ️ Thành viên này hiện không có Role VIP.", ephemeral=True)
            return







        # 7. Bấm nút Đóng Phòng Hỗ Trợ Tìm Game



        if custom_id == 'btn_close_install_help_ticket':



            await interaction.response.send_message(



                "🔒 **Phòng hỗ trợ cài game này đã hoàn thành nhiệm vụ!**\n"



                "Hệ thống sẽ tự động dọn dẹp và xóa phòng sau **3 giây**...\n"



                "❤️ Chúc bạn chơi game thật vui vẻ cùng bản Việt Hóa Gấu Công Tâm!"



            )



            await asyncio.sleep(3)



            try:



                if isinstance(interaction.channel, discord.Thread):



                    await interaction.channel.delete()



                    log_event(f"-> Đã xóa và dọn dẹp phòng ticket cài game: {interaction.channel.name}")



            except Exception as e:



                log_event(f"Lỗi xóa phòng ticket: {e}")



            return







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







        # 6. Bấm nút Nhờ Tìm Game -> Kiểm tra Role Nhà Tài Trợ Vàng ⭐ rồi mở Modal Form
        if custom_id in ('btn_open_install_help_modal', 'btn_open_find_game_modal'):
            if not _is_vip_member(interaction.user):
                await interaction.response.send_message(
                    "👑 **ĐẶC QUYỀN DÀNH RIÊNG CHO NHÀ TÀI TRỢ VÀNG ⭐**\n\n"
                    "Tính năng **Mở Phòng Kín 1-1 Nhờ Bác Gấu Tìm Nguồn Game Sạch & Hỗ Trợ Cài Đặt Trực Tiếp** "
                    "là đặc quyền tri ân dành riêng cho các **Nhà Tài Trợ Vàng ⭐**!\n\n"
                    f"👉 Bạn chỉ cần mời Gấu một ly cà phê tùy tâm tại <#{COFFEE_CH_ID}> "
                    "*(bấm nút gửi ảnh bill chuyển khoản, Bot AI tự động duyệt & cấp Role trong 3 giây)* để mở khóa **vĩnh viễn** trọn bộ đặc quyền:\n"
                    f"• 🔑 Xem thẳng toàn bộ **Mã PIN 5 Số 24h (0% quảng cáo)** tại <#{VIP_PIN_CH_ID}>.\n"
                    "• 🆘 Mở **Phòng Kín 1-1 Nhờ Gấu Tìm Nguồn Game Sạch & Hỗ Trợ Cài Đặt Trực Tiếp**.\n"
                    f"• 👑 Đề xuất game đóng khung **Vàng Kim `[ƯU TIÊN VIP]` (+3 Votes mở màn)** & **Quyền Vote x2** tại <#{REQ_CH_ID}>.\n\n"
                    f"*(💡 Nếu bạn gặp lỗi trong bản dịch, bạn vẫn có thể báo lỗi miễn phí 100% tại <#{BUG_CH_ID}> nhé!)*",
                    ephemeral=True,
                )
                return
            if custom_id == 'btn_open_install_help_modal':
                await interaction.response.send_modal(InstallHelpRequestModal())
            else:
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
            embed = interaction.message.embeds[0] if interaction.message.embeds else None
            info = _extract_req_card_info(
                embed,
                interaction.message.components if interaction.message else None,
                getattr(interaction.message, "thread", None),
                fallback_vote_id=vote_id,
            )
            if info["status"] == "done":
                await interaction.response.send_message(
                    "✅ Tựa game này đã được Studio Gấu Việt hóa hoàn thành rồi nhé! Anh em bấm nút **🎮 Tải Game Ngay** để chiến luôn nha!",
                    ephemeral=True,
                )
                return

            if vote_id not in votes:
                votes[vote_id] = {
                    "game": info["game_title"],
                    "base_count": info["total_votes"],
                    "count": info["total_votes"],
                    "voters": [],
                    "status": info["status"],
                }

            voters = votes[vote_id].get('voters', [])
            if interaction.user.id in voters:
                await interaction.response.send_message("❤️ Bạn đã bình chọn cho tựa game này rồi nha!", ephemeral=True)
                return

            is_vip_voter = _is_vip_member(interaction.user)
            voters.append(interaction.user.id)
            if is_vip_voter:
                votes[vote_id]['base_count'] = votes[vote_id].get('base_count', 0) + 1
            total_votes = votes[vote_id].get('base_count', 0) + len(voters)
            votes[vote_id]['count'] = total_votes
            save_votes(votes)

            if embed:
                for i, field in enumerate(embed.fields):
                    if field.name == "🔥 Lượt Bình Chọn":
                        v_txt = f"⭐ **{total_votes} Votes** *(Đặc quyền VIP)*" if info.get("is_vip_card") else f"⭐ **{total_votes} Votes**"
                        embed.set_field_at(i, name="🔥 Lượt Bình Chọn", value=v_txt, inline=False)
                        break

            view = build_request_card_view(
                vote_id,
                total_votes,
                comment_url=info["comment_url"],
                status=info["status"],
                game_post_url=info["game_post_url"],
            )
            await interaction.response.edit_message(embed=embed, view=view)
            if is_vip_voter:
                await interaction.followup.send("👑 Cảm ơn **Nhà Tài Trợ Vàng ⭐** đã bình chọn! Lá phiếu đặc quyền của bạn được tính **+2 Votes**!", ephemeral=True)
            else:
                await interaction.followup.send("🎉 Cảm ơn bạn đã bình chọn cho tựa game này!", ephemeral=True)
            return

        if custom_id.startswith(('btn_req_wip_', 'btn_req_done_', 'btn_req_reopen_')):
            if not _is_studio_admin(interaction.user):
                await interaction.response.send_message("🚫 Chỉ Ban Quản Trị Studio mới có quyền cập nhật tiến độ Việt hóa!", ephemeral=True)
                return

            await interaction.response.defer(ephemeral=True)
            if custom_id.startswith('btn_req_wip_'):
                vote_id = custom_id.replace('btn_req_wip_', '', 1)
                new_status = 'wip'
            elif custom_id.startswith('btn_req_done_'):
                vote_id = custom_id.replace('btn_req_done_', '', 1)
                new_status = 'done'
            else:
                vote_id = custom_id.replace('btn_req_reopen_', '', 1)
                new_status = 'open'

            embed = interaction.message.embeds[0] if interaction.message.embeds else None
            info = _extract_req_card_info(
                embed,
                interaction.message.components if interaction.message else None,
                getattr(interaction.message, "thread", None),
                fallback_vote_id=vote_id,
            )
            guild = interaction.guild
            cfg = get_server_cfg(guild.id if guild else GUILD_ID)
            game_post_url = info["game_post_url"]
            if new_status == 'done' and not game_post_url:
                game_post_url = await _find_forum_thread_url(guild, cfg.get("forum_ch_id"), info["game_title"])
            elif new_status == 'open':
                game_post_url = None

            votes = load_votes()
            if vote_id not in votes:
                votes[vote_id] = {
                    "game": info["game_title"],
                    "base_count": info["total_votes"],
                    "count": info["total_votes"],
                    "voters": [],
                }
            votes[vote_id]["status"] = new_status
            if game_post_url:
                votes[vote_id]["game_post_url"] = game_post_url
            save_votes(votes)

            if embed:
                apply_request_status_to_embed(
                    embed,
                    info["game_title"],
                    new_status,
                    actor_mention=interaction.user.mention,
                    game_post_url=game_post_url,
                )

            new_view = build_request_card_view(
                vote_id,
                info["total_votes"],
                comment_url=info["comment_url"],
                status=new_status,
                game_post_url=game_post_url,
            )
            await interaction.message.edit(embed=embed, view=new_view)
            if new_status in ('wip', 'done') and info["status"] != new_status:
                await _notify_req_thread_status(
                    interaction.message,
                    info["game_title"],
                    info["requester_mention"],
                    new_status,
                    game_post_url=game_post_url,
                    comment_url=info["comment_url"],
                )

            status_lbl = {"wip": "🛠️ Đang Việt Hóa", "done": "✅ Đã Hoàn Thành", "open": "💡 Mở Lại Bình Chọn"}[new_status]
            await interaction.followup.send(f"Đã cập nhật **{info['game_title']}** ➔ **{status_lbl}**!", ephemeral=True)
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



            primary_guild = bot.get_guild(GUILD_ID)

            if primary_guild:

                await update_admin_dashboard(primary_guild)



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
                    asyncio.create_task(update_server_stats_panel(guild))



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
async def on_member_join(member: discord.Member):
    global _stats_last_event_ts
    if member.guild.id == GUILD_ID and (time.time() - _stats_last_event_ts >= 15):
        _stats_last_event_ts = time.time()
        await update_server_stats_panel(member.guild)


@bot.event
async def on_member_remove(member: discord.Member):
    global _stats_last_event_ts
    if member.guild.id == GUILD_ID and (time.time() - _stats_last_event_ts >= 15):
        _stats_last_event_ts = time.time()
        await update_server_stats_panel(member.guild)


@bot.event



async def on_message(message: discord.Message):



    if message.author.bot:



        return







    guild = message.guild



    if not guild or guild.id not in SERVER_CONFIGS:



        return







    member = message.author



    content = message.content



    now = time.time()

    # 0A. TỰ ĐỘNG ĐỌC ẢNH BILL CHUYỂN KHOẢN TRONG PHÒNG TICKET DONATE (☕・[VIP]-...) & CẤP ROLE VIP 24/7
    if isinstance(message.channel, discord.Thread) and message.channel.name.startswith("☕・[VIP]-") and message.attachments:
        img_att = next(
            (a for a in message.attachments if (a.content_type and a.content_type.startswith("image/")) or a.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))),
            None,
        )
        if img_att:
            status_msg = await message.reply("🤖 **Bot Gấu đang quét xác thực ảnh biên lai chuyển khoản... (chờ 2–3 giây nhé)**", mention_author=False)
            try:
                img_bytes = await img_att.read()
                img_hash = hashlib.sha256(img_bytes).hexdigest()
                if img_hash in _used_donate_hashes:
                    await status_msg.edit(content="⚠️ **Ảnh biên lai này đã được sử dụng trước đó rồi!** Vui lòng gửi ảnh chụp giao dịch mới của bạn nhé.")
                    return
                res = await asyncio.to_thread(_verify_receipt_sync, img_bytes, img_att.content_type or "image/jpeg")
                is_valid = bool(res.get("is_valid"))
                amount_str = str(res.get("amount") or "Ly Cà Phê Ấm Lòng ☕").strip()
                amount_vnd = _parse_vnd_amount(res.get("amount_vnd"), amount_str)
                tx_id = str(res.get("tx_id") or "").strip()
                reason_str = str(res.get("reason") or "").strip()
                tx_key = f"TX_{tx_id}" if len(tx_id) >= 5 else ""

                if is_valid and (not tx_key or tx_key not in _used_donate_hashes):
                    _used_donate_hashes.add(img_hash)
                    if tx_key:
                        _used_donate_hashes.add(tx_key)
                    main_g = bot.get_guild(GUILD_ID) or guild
                    main_m = main_g.get_member(member.id)
                    if not main_m:
                        try:
                            main_m = await main_g.fetch_member(member.id)
                        except Exception:
                            main_m = None
                    grant_res = await grant_vip_and_honor(
                        main_g,
                        main_m or member,
                        amount_str=amount_str,
                        amount_vnd=amount_vnd,
                        note_src="AI Vision duyệt tự động",
                    )
                    if grant_res["vip_granted"]:
                        local_vip_pin_id = get_server_cfg(message.guild.id).get("vip_pin_ch_id") or VIP_PIN_CH_ID
                        await status_msg.edit(
                            content=(
                                f"🎉 **XÁC THỰC BIÊN LAI THÀNH CÔNG! CHÚC MỪNG {member.mention} ĐÃ NHẬN NHÀ TÀI TRỢ VÀNG ⭐!** ❤️\n\n"
                                f"• ☕ **Số tiền vừa ghi nhận:** **`{amount_str}`** *(Tổng tích lũy: **`{grant_res['total_vnd']:,}đ / 200.000đ`**)*\n"
                                f"• 👑 **Thời hạn VIP:** **`{grant_res['exp_disp']}`**\n"
                                f"• 🔑 **Kho Mã PIN 0s Chờ:** **<#{local_vip_pin_id}>** *(và <#{VIP_PIN_CH_ID}> ở Server chính)*\n"
                                f"• 🆘 **Phòng Kín 1-1 Nhờ Tìm Game & Thẻ Vàng Đề Xuất:** Đã mở khóa!\n"
                                f"• 🏆 **Đã vinh danh tại:** **<#{HALL_OF_FAME_CH_ID}>**\n\n"
                                f"❤️ *Thay mặt Studio Gấu Công Tâm cảm ơn tấm lòng của bạn rất nhiều!*"
                            )
                        )
                    else:
                        rem_30 = max(0, 30000 - amount_vnd)
                        await status_msg.edit(
                            content=(
                                f"❤️ **CẢM ƠN TẤM LÒNG CỦA {member.mention} ĐÃ TIẾP LỬA CHO GẤU!**\n\n"
                                f"• ☕ **Số tiền vừa ghi nhận:** **`{amount_str}`**\n"
                                f"• 💰 **Đã cộng dồn vào tài khoản của bạn:** **`{grant_res['total_vnd']:,}đ / 200.000đ`** *(đã ghi danh tri ân tại <#{HALL_OF_FAME_CH_ID}>!)*\n"
                                f"• 👑 **Mốc mở khóa Role Nhà Tài Trợ Vàng ⭐:** Cần tối thiểu **`30.000đ`** (1 tháng) / **`50.000đ`** (2 tháng) / **`100.000đ`** (6 tháng) hoặc cộng dồn đủ **`200.000đ`** để lên **Vĩnh Viễn**!\n"
                                + (f"👉 *Nếu bạn gửi thêm khoảng **`{rem_30:,}đ`**, Role VIP sẽ tự động mở khóa ngay nhé!*" if rem_30 > 0 else "")
                            )
                        )
                    admin_ch = main_g.get_channel(ADMIN_CH_ID)
                    if admin_ch:
                        rev_v = discord.ui.View(timeout=None)
                        rev_v.add_item(discord.ui.Button(
                            label="🚫 Thu Hồi Role VIP (Nếu Bill Giả)",
                            style=discord.ButtonStyle.danger,
                            custom_id=f"btn_revoke_vip_{member.id}",
                        ))
                        adm_emb = discord.Embed(
                            title="⭐ AI ĐÃ TỰ ĐỘNG DUYỆT BILL DONATE",
                            description=(
                                f"• 👤 **Thành viên:** {member.mention} (`{member.name}` - ID: `{member.id}`)\n"
                                f"• 💰 **Số tiền AI đọc:** **`{amount_str}`** (`{amount_vnd:,}đ`)\n"
                                f"• 📊 **Tích lũy & Gói:** **`{grant_res['total_vnd']:,}đ`** ➔ **`{grant_res['exp_disp']}`**\n"
                                f"• 🧾 **Mã GD:** `{tx_id or 'N/A'}`\n"
                                f"• 📍 **Phòng ticket:** {message.channel.mention}"
                            ),
                            color=0xf1c40f if grant_res["vip_granted"] else 0xe67e22,
                        )
                        adm_emb.set_image(url=img_att.url)
                        await admin_ch.send(embed=adm_emb, view=rev_v)
                else:
                    await status_msg.edit(
                        content=(
                            f"⏳ **Hệ thống tự động chưa đọc rõ số TK nhận `102880978780` (`TRAN THANH HIEP` - VietinBank) trong ảnh này** "
                            f"*(Ghi chú: {reason_str or 'Ảnh mờ hoặc thiếu thông tin người nhận'})*.\n"
                            f"👉 Bạn có thể **gửi lại ảnh chụp rõ biên lai hoàn tất giao dịch**, hoặc chờ **Bác Gấu** kiểm tra duyệt thủ công ngay nhé!"
                        )
                    )
                    main_g = bot.get_guild(GUILD_ID) or guild
                    admin_ch = main_g.get_channel(ADMIN_CH_ID)
                    if admin_ch:
                        man_v = discord.ui.View(timeout=None)
                        man_v.add_item(discord.ui.Button(label="✅ 30k (1 Tháng)", style=discord.ButtonStyle.primary, custom_id=f"btn_grant_vip_30k_{member.id}"))
                        man_v.add_item(discord.ui.Button(label="✅ 50k (2 Tháng)", style=discord.ButtonStyle.primary, custom_id=f"btn_grant_vip_50k_{member.id}"))
                        man_v.add_item(discord.ui.Button(label="✅ 100k (6 Tháng)", style=discord.ButtonStyle.success, custom_id=f"btn_grant_vip_100k_{member.id}"))
                        man_v.add_item(discord.ui.Button(label="👑 Vĩnh Viễn (200k)", style=discord.ButtonStyle.danger, custom_id=f"btn_grant_vip_perm_{member.id}"))
                        adm_emb = discord.Embed(
                            title="☕ YÊU CẦU DUYỆT BILL DONATE THỦ CÔNG",
                            description=(
                                f"• 👤 **Thành viên:** {member.mention} (`{member.name}`)\n"
                                f"• ⚠️ **Lý do AI chuyển duyệt tay:** `{reason_str}`\n"
                                f"• 📍 **Phòng ticket:** {message.channel.mention}"
                            ),
                            color=0xe67e22,
                        )
                        adm_emb.set_image(url=img_att.url)
                        await admin_ch.send(embed=adm_emb, view=man_v)
            except Exception as ex:
                log_event(f"Lỗi xử lý ảnh bill donate: {ex}")
            return

    # 0B. CHỐNG LỘ MÃ PIN 5 SỐ RA KÊNH CHAT CHUNG
    if not member.guild_permissions.administrator and message.channel.id not in (VIP_PIN_CH_ID, ADMIN_CH_ID, LOG_CH_ID):
        nums_in_msg = set(re.findall(r"\b(\d{5})\b", content))
        if nums_in_msg and (nums_in_msg & _protected_pins_set):
            try:
                await message.delete()
                await message.channel.send(
                    f"🔒 {member.mention} ơi, vui lòng **không chia sẻ Mã PIN cài đặt lên kênh chat chung** để ủng hộ kinh phí duy trì máy chủ cho Gấu nhé! ❤️",
                    delete_after=8,
                )
            except Exception:
                pass
            return







    # 1. Quét link độc hại & cờ bạc / lừa đảo



    if PHISHING_REGEX.search(content):



        try:



            await message.delete()



        except:



            pass



        try:



            await member.timeout(timedelta(hours=1), reason="Spam link độc hại / cờ bạc lừa đảo")



        except:



            pass



        await message.channel.send(



            f"⚠️ **CẢNH BÁO BẢO MẬT:** {member.mention} đã bị tạm khóa chat 1 giờ do gửi tin nhắn chứa nội dung cờ bạc/liên kết độc hại!",



            delete_after=10



        )



        log_ch = guild.get_channel(LOG_CH_ID)



        if log_ch:



            try:



                await log_ch.send(f"🚨 **BẢO VỆ TỰ ĐỘNG:** Đã xóa tin nhắn và Timeout 1 giờ tài khoản `{member.name}` ({member.id}) vì spam nội dung nguy hại:\n`{content[:200]}`")



            except:



                pass



        return







    # 2. Chặn tag @everyone & @here



    if ('@everyone' in content or '@here' in content) and not member.guild_permissions.administrator:



        try:



            await message.delete()



        except:



            pass



        try:



            await member.timeout(timedelta(minutes=30), reason="Tự ý tag @everyone / @here")



        except:



            pass



        await message.channel.send(



            f"🚫 {member.mention}, chỉ Ban Quản Trị mới được phép sử dụng thông báo `@everyone`! Bạn bị tạm khóa chat 30 phút.",



            delete_after=5



        )



        log_ch = guild.get_channel(LOG_CH_ID)



        if log_ch:



            try:



                await log_ch.send(f"⚠️ **CẢNH BÁO:** Đã chặn và tạm khóa chat `{member.name}` ({member.id}) do tự ý tag @everyone/@here.")



            except:



                pass



        return







    # 3. Chống spam chat đa tầng (Rate-limit, Duplicate Spam, Emoji Flood, Xóa sạch chuỗi spam & Timeout)
    if not member.guild_permissions.administrator and not member.guild_permissions.manage_messages:
        user_id = member.id
        if user_id not in spam_tracker or isinstance(spam_tracker[user_id], list):
            spam_tracker[user_id] = {
                'timestamps': [],
                'recent_messages': []
            }

        user_data = spam_tracker[user_id]
        user_data['timestamps'] = [t for t in user_data['timestamps'] if now - t < 10.0]
        user_data['timestamps'].append(now)

        user_data['recent_messages'] = [(t, c, mid) for (t, c, mid) in user_data['recent_messages'] if now - t < 15.0]
        user_data['recent_messages'].append((now, content.strip(), message.id))

        is_spam = False
        spam_reason = ''

        custom_emojis = re.findall(r'<a?:\w+:\d+>', content)
        unicode_emojis = re.findall(r'[𐀀-􏿿]', content)
        total_emojis = len(custom_emojis) + len(unicode_emojis)

        # 3A. Nhồi quá nhiều emoji trong 1 tin (Emoji Flood >= 4 emoji hoặc tin nhắn chỉ toàn custom emoji >= 2)
        cleaned_no_spaces = content.strip().replace(' ', '').replace('\n', '')
        is_all_custom_emojis = bool(custom_emojis) and len(cleaned_no_spaces) == sum(len(e) for e in custom_emojis)
        if total_emojis >= 4 or (total_emojis >= 2 and is_all_custom_emojis):
            is_spam = True
            spam_reason = f'Bão Emoji (nhồi {total_emojis} emoji trong 1 tin)'

        # 3B. Spam tin nhắn / Emoji trùng lặp liên tiếp 2 lần trong 15s
        elif len(user_data['recent_messages']) >= 2:
            last_2 = user_data['recent_messages'][-2:]
            if last_2[0][1] and last_2[0][1] == last_2[1][1]:
                is_spam = True
                spam_reason = 'Spam nội dung / emoji trùng lặp liên tiếp 2 lần'

        # 3C. Tốc độ gửi tin nhắn quá nhanh (3 tin trong 5 giây HOẶC 5 tin trong 10 giây)
        elif len([t for t in user_data['timestamps'] if now - t < 5.0]) >= 3:
            is_spam = True
            spam_reason = 'Gửi tin nhắn quá nhanh (3 tin trong 5 giây)'
        elif len(user_data['timestamps']) >= 5:
            is_spam = True
            spam_reason = 'Làm loãng kênh chat (5 tin trong 10 giây)'

        if is_spam:
            # 1. Thu thập ID các tin nhắn vi phạm gần đây của user để xóa sạch (Purge)
            to_delete_ids = [mid for (t, c, mid) in user_data['recent_messages']]
            user_data['timestamps'] = []
            user_data['recent_messages'] = []

            try:
                await message.delete()
            except Exception:
                pass

            for mid in to_delete_ids:
                if mid != message.id:
                    try:
                        msg_obj = await message.channel.fetch_message(mid)
                        await msg_obj.delete()
                    except Exception:
                        pass

            # 2. Phạt Timeout 5 phút
            try:
                await member.timeout(timedelta(minutes=5), reason=f'Chống Spam Tự Động: {spam_reason}')
            except Exception as e:
                log_event(f'Không thể timeout {member.name}: {e}')

            # 3. Cảnh báo công khai đếm ngược 6 giây rồi tự hủy
            try:
                await message.channel.send(
                    f'🛡️ **HỆ THỐNG AN NINH:** {member.mention} đã bị **tạm khóa chat 5 phút** do: **{spam_reason}**!\n-# *Vui lòng giữ gìn không gian chém gió văn minh, không spam emoji hoặc lặp tin nhắn.*',
                    delete_after=6
                )
            except Exception:
                pass

            # 4. Ghi log vào kênh nhật ký hệ thống
            log_ch = guild.get_channel(LOG_CH_ID)
            if log_ch:
                try:
                    await log_ch.send(
                        f'🚨 **CHẶN SPAM THÀNH CÔNG:**\n'
                        f'👤 **Thành viên:** {member.name} ({member.id})\n'
                        f'📍 **Kênh:** {message.channel.mention}\n'
                        f'⚠️ **Hành vi:** {spam_reason}\n'
                        f'⏱️ **Xử lý:** Đã xóa sạch tin rác và Timeout 5 phút.'
                    )
                except Exception:
                    pass
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



    cfg = get_server_cfg(interaction.guild_id)

    embed.add_field(name="1️⃣ Bước 1: Mở Launcher", value=f"Tải và mở **Gấu Cloud Launcher** tại kênh <#{cfg['launcher_ch_id']}>.", inline=False)

    embed.add_field(name="2️⃣ Bước 2: Nhập Mã PIN 5 Số", value=f"Bấm **[CÀI ĐẶT VIỆT HÓA]** ➔ Nhập **Mã PIN 5 Số** của game đó (lấy trong bài viết tại <#{cfg['forum_ch_id']}>).", inline=False)



    embed.add_field(name="3️⃣ Bước 3: Vào Game", value="Bấm **[VÀO GAME]** để trải nghiệm tiếng Việt trọn vẹn!", inline=False)



    embed.set_footer(text="Việt Hóa Gấu Công Tâm • Miễn phí vì cộng đồng")



    await interaction.response.send_message(embed=embed, ephemeral=True)







@bot.tree.command(name="khogame", description="Xem đường dẫn đến Kho Game và cách lấy Mã PIN 5 số")



async def cmd_khogame(interaction: discord.Interaction):



    embed = discord.Embed(



        title="🗂️ KHO GAME VIỆT HÓA STUDIO GẤU CÔNG TÂM",



        description=f"Toàn bộ các dự án Việt hóa đã phát hành đều được lưu trữ dạng bài viết chi tiết tại kênh Diễn Đàn:\n👉 <#{get_server_cfg(interaction.guild_id)['forum_ch_id']}>",



        color=0x3498db



    )



    await interaction.response.send_message(embed=embed, ephemeral=True)







@bot.tree.command(name="baoloi", description="Hướng dẫn gửi báo cáo lỗi bản dịch nhanh chóng")



async def cmd_baoloi(interaction: discord.Interaction):



    embed = discord.Embed(



        title="🐛 HƯỚNG DẪN BÁO LỖI BẢN DỊCH GAME",



        description=f"Để Studio gom lỗi theo từng game và ra bản vá sửa nhanh nhất, bạn chỉ cần ghé kênh:\n👉 <#{get_server_cfg(interaction.guild_id)['bug_ch_id']}>\nSau đó bấm nút đỏ **`[🚨 Gửi Báo Lỗi Game]`** và dán ảnh chụp màn hình vào nhé!",



        color=0xe74c3c



    )



    await interaction.response.send_message(embed=embed, ephemeral=True)







@bot.tree.command(name="danhsachloi", description="[Admin] Cập nhật và xem Bảng tổng hợp báo lỗi tất cả các game")
@app_commands.default_permissions(manage_guild=True)

async def cmd_danhsachloi(interaction: discord.Interaction):

    if interaction.guild_id != GUILD_ID:
        await interaction.response.send_message("🚫 Lệnh quản trị này chỉ dùng tại server chính Studio!", ephemeral=True)
        return



    if not interaction.user.guild_permissions.manage_channels:



        await interaction.response.send_message("🚫 Lệnh này chỉ dành cho Ban Quản Trị Studio!", ephemeral=True)



        return



    await interaction.response.defer(ephemeral=True)



    await update_admin_dashboard(interaction.guild)



    await interaction.followup.send(f"✅ Đã đồng bộ và cập nhật Bảng Gom Lỗi tại kênh <#{ADMIN_CH_ID}>!", ephemeral=True)







@bot.tree.command(name="vinhdanh", description="Vinh danh Nhà Tài Trợ và tự động cấp Role VIP (Dành cho Admin)")
@app_commands.default_permissions(manage_guild=True)



@app_commands.describe(



    user="Thành viên đã donate ủng hộ Studio",



    amount="Số tiền ủng hộ (VD: 50.000 VNĐ, 100k, 200k...)",



    message="Lời nhắn gửi từ người ủng hộ (tùy chọn)"



)



async def cmd_vinhdanh(interaction: discord.Interaction, user: discord.Member, amount: str, message: str = "Tiếp lửa cho Studio dịch game"):



    if interaction.guild_id != GUILD_ID:
        await interaction.response.send_message("🚫 Lệnh này chỉ dùng tại server chính Studio!", ephemeral=True)
        return

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



            err_str = str(e)



            if "429" in err_str or "rate limit" in err_str.lower() or "1015" in err_str:



                log_event("⏳ Cloudflare Rate Limit (429/1015). Chờ 60s để giải tỏa IP...")



                await asyncio.sleep(60)



            else:



                await asyncio.sleep(5)







if __name__ == '__main__':



    asyncio.run(main())



