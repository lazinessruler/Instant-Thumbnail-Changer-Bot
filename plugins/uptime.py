import aiohttp
import asyncio
import datetime
import random
from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from aiogram.exceptions import TelegramBadRequest
from config import OWNER_ID
from database import is_admin, add_url, remove_url, get_all_urls, update_url_status

router = Router()

START_TIME = datetime.datetime.now()
PING_TASK = None
BOT_NAME = "🖼️ Thumbnail Changer Bot"

# Premium Uptime Images
UPTIME_IMAGES = [
    "https://i.postimg.cc/Hx1qXv0f/0f22a4ab4d44a829a33797eb7d8fbdc6.jpg",
    "https://i.postimg.cc/j5YpP3Qb/22df44ff326cbce5d99344d904e993af.jpg",
    "https://i.postimg.cc/26Nsh9dg/2b8ed2a65ecec6caa3c442cd08cffd27.jpg",
    "https://i.postimg.cc/Kzh6Bprz/6274337955fefbe4c95d4712714597e4.jpg",
    "https://i.postimg.cc/SsLwrLDN/9a8fe855f0dc641cf81aae32d9f0e9bb.jpg",
    "https://i.postimg.cc/vB7pz73Z/a08029e31cd662dcb778a917b09deee4.jpg",
    "https://i.postimg.cc/ydhwPhvz/a85d30361837800fd31935ec137863bf.jpg",
    "https://i.postimg.cc/LsPdqFPW/b6e808ff4ded204ba2abadedaeeef2b2.jpg",
    "https://i.postimg.cc/vBwJf2Ly/bd7b083aebb810f4ffba2d60ee98053a.jpg",
    "https://i.postimg.cc/W3mQnmXc/cfbf4a2ce731632aa88dd87456844586.jpg",
    "https://i.postimg.cc/85dqHdtS/f4895703153ffd7f73fa8024eada8287.jpg"
]

def get_random_uptime_image() -> str:
    """Return a random premium image"""
    return random.choice(UPTIME_IMAGES)

class URLState(StatesGroup):
    waiting_for_url = State()
    waiting_for_name = State()

def small_caps(text: str) -> str:
    """Convert text to small caps unicode"""
    normal = "abcdefghijklmnopqrstuvwxyz"
    small = "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    result = ""
    for char in text:
        if char.lower() in normal:
            idx = normal.index(char.lower())
            result += small[idx]
        else:
            result += char
    return result

def get_uptime() -> str:
    """Bot ka uptime calculate karein"""
    now = datetime.datetime.now()
    diff = now - START_TIME
    
    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    seconds = diff.seconds % 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    
    return " ".join(parts)

async def ping_all_urls():
    """Sabhi URLs ko ping karein"""
    urls = await get_all_urls()
    
    async with aiohttp.ClientSession() as session:
        for url_data in urls:
            if not url_data.get("active", True):
                continue
                
            url = url_data["url"]
            name = url_data.get("name", url)
            
            try:
                async with session.get(url, timeout=10) as resp:
                    print(f"✅ [{name}] Ping successful - Status: {resp.status}")
                    await update_url_status(url, resp.status)
            except Exception as e:
                print(f"❌ [{name}] Ping failed: {e}")
                await update_url_status(url, error=str(e)[:100])

async def ping_loop():
    """Continuous ping loop"""
    while True:
        await ping_all_urls()
        await asyncio.sleep(300)  # 5 minutes

def get_status_emoji(status) -> str:
    """Status ke hisaab se emoji return karein"""
    if status == 200:
        return "✅"
    elif status == 404:
        return "🔍"
    elif status == 500:
        return "🔥"
    elif status == 403:
        return "🔒"
    elif status == 400:
        return "⚠️"
    elif status == "Failed":
        return "❌"
    else:
        return "🔄"

def format_url_list(urls) -> str:
    """URL list ko professionally format karein"""
    if not urls:
        return "   📭 No URLs configured yet."
    
    text = ""
    for i, url_data in enumerate(urls, 1):
        name = url_data.get("name", "Unnamed")
        url = url_data["url"]
        active = url_data.get("active", True)
        last_ping = url_data.get("last_ping")
        last_status = url_data.get("last_status", "Never")
        
        # Status emoji
        status_emoji = get_status_emoji(last_status)
        active_emoji = "🟢" if active else "🔴"
        
        # Last ping time
        if last_ping and isinstance(last_ping, datetime.datetime):
            time_diff = datetime.datetime.now() - last_ping
            mins_ago = int(time_diff.total_seconds() / 60)
            if mins_ago < 1:
                last_ping_str = "Just now"
            elif mins_ago < 60:
                last_ping_str = f"{mins_ago}m ago"
            else:
                hours_ago = mins_ago // 60
                last_ping_str = f"{hours_ago}h ago"
        else:
            last_ping_str = "Never"
        
        # Format URL for display
        display_url = url.replace("https://", "").replace("http://", "")
        if len(display_url) > 30:
            display_url = display_url[:27] + "..."
        
        # Add to text with proper formatting
        text += f"{active_emoji} <b>{i}. {name}</b>\n"
        text += f"   └ <code>{display_url}</code>\n"
        text += f"   └ {status_emoji} Status: <b>{last_status}</b> | ⏱️ {last_ping_str}\n\n"
    
    return text

def get_main_keyboard(is_admin: bool):
    """Main uptime keyboard with all options"""
    if not is_admin:
        return None
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ 𝗔𝗱𝗱 𝗨𝗥𝗟", callback_data="add_url"),
            InlineKeyboardButton(text="🗑️ 𝗥𝗲𝗺𝗼𝘃𝗲", callback_data="remove_url")
        ],
        [
            InlineKeyboardButton(text="🔄 𝗧𝗲𝘀𝘁 𝗔𝗹𝗹", callback_data="test_all"),
            InlineKeyboardButton(text="📊 𝗥𝗲𝗳𝗿𝗲𝘀𝗵", callback_data="refresh_uptime")
        ],
        [
            InlineKeyboardButton(text="❌ 𝗖𝗹𝗼𝘀𝗲", callback_data="close_uptime")
        ]
    ])

@router.message(Command("uptime"))
async def uptime_cmd(message: types.Message):
    """Main uptime command - ek hi page par sab kuch"""
    user_id = message.from_user.id
    is_admin_user = await is_admin(user_id)
    
    uptime_str = get_uptime()
    urls = await get_all_urls()
    
    # Format URLs
    url_list_text = format_url_list(urls)
    
    # Stats
    total_urls = len(urls)
    active_urls = sum(1 for u in urls if u.get("active", True))
    
    # Main text with professional formatting
    text = (
        f"<b>🤖 {BOT_NAME} - Uptime Monitor</b>\n\n"
        f"<b>📅 Started:</b> {START_TIME.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"<b>⏰ Uptime:</b> <code>{uptime_str}</code>\n"
        f"<b>📊 Stats:</b> {total_urls} Total | {active_urls} Active\n"
        f"<b>⏱️ Ping:</b> Every 5 minutes\n\n"
        f"<b>📋 Monitored URLs:</b>\n{url_list_text}"
    )
    
    # Get random image
    image_url = get_random_uptime_image()
    
    # Send with photo
    try:
        await message.answer_photo(
            photo=image_url,
            caption=text,
            parse_mode="HTML",
            reply_markup=get_main_keyboard(is_admin_user)
        )
    except Exception:
        # Fallback if image fails
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_main_keyboard(is_admin_user)
        )

@router.callback_query(F.data == "refresh_uptime")
async def refresh_uptime(callback: CallbackQuery):
    """Refresh uptime data - same page par rahe"""
    await callback.answer("🔄 Refreshing...")
    
    user_id = callback.from_user.id
    is_admin_user = await is_admin(user_id)
    
    uptime_str = get_uptime()
    urls = await get_all_urls()
    
    url_list_text = format_url_list(urls)
    
    total_urls = len(urls)
    active_urls = sum(1 for u in urls if u.get("active", True))
    
    text = (
        f"<b>🤖 {BOT_NAME} - Uptime Monitor</b>\n\n"
        f"<b>📅 Started:</b> {START_TIME.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"<b>⏰ Uptime:</b> <code>{uptime_str}</code>\n"
        f"<b>📊 Stats:</b> {total_urls} Total | {active_urls} Active\n"
        f"<b>⏱️ Ping:</b> Every 5 minutes\n\n"
        f"<b>📋 Monitored URLs:</b>\n{url_list_text}"
    )
    
    try:
        # Edit existing message
        await callback.message.edit_caption(
            caption=text,
            parse_mode="HTML",
            reply_markup=get_main_keyboard(is_admin_user)
        )
    except TelegramBadRequest:
        # If edit fails, send new
        image_url = get_random_uptime_image()
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=image_url,
            caption=text,
            parse_mode="HTML",
            reply_markup=get_main_keyboard(is_admin_user)
        )

@router.callback_query(F.data == "add_url")
async def add_url_prompt(callback: CallbackQuery, state: FSMContext):
    """Add URL - inline prompt without leaving page"""
    if callback.from_user.id != OWNER_ID:
        await callback.answer("❌ Only owner can add URLs!", show_alert=True)
        return
    
    await callback.answer()
    await state.set_state(URLState.waiting_for_url)
    
    # Store original message info
    await state.update_data(original_chat_id=callback.message.chat.id)
    await state.update_data(original_message_id=callback.message.message_id)
    
    # Prompt inline
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_add")]
    ])
    
    prompt_text = (
        f"<b>➕ Add New URL</b>\n\n"
        f"Please send the URL you want to monitor:\n"
        f"<code>https://your-app.onrender.com</code>\n\n"
        f"<i>or send /cancel to cancel</i>"
    )
    
    try:
        await callback.message.edit_caption(
            caption=prompt_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except:
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=get_random_uptime_image(),
            caption=prompt_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

@router.callback_query(F.data == "cancel_add")
async def cancel_add(callback: CallbackQuery, state: FSMContext):
    """Cancel add operation and return to main"""
    await state.clear()
    await callback.answer("❌ Cancelled")
    await refresh_uptime(callback)

@router.message(URLState.waiting_for_url)
async def receive_url(message: types.Message, state: FSMContext):
    """Receive URL and ask for name"""
    url = message.text.strip()
    
    if not (url.startswith("http://") or url.startswith("https://")):
        await message.answer("❌ Invalid URL! Must start with http:// or https://")
        return
    
    if url.endswith("/"):
        url = url[:-1]
    
    await state.update_data(url=url)
    await state.set_state(URLState.waiting_for_name)
    
    auto_name = url.replace("https://", "").replace("http://", "").split(".")[0]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭️ Use Auto Name", callback_data="use_auto_name")]
    ])
    
    text = (
        f"✅ URL: <code>{url}</code>\n\n"
        f"Now send a <b>name</b> for this URL:\n"
        f"Example: <code>Main Bot</code>\n"
        f"Auto name: <b>{auto_name}</b>"
    )
    
    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)

@router.callback_query(F.data == "use_auto_name")
async def use_auto_name(callback: CallbackQuery, state: FSMContext):
    """Use auto-generated name"""
    data = await state.get_data()
    url = data.get("url")
    auto_name = url.replace("https://", "").replace("http://", "").split(".")[0]
    
    success = await add_url(url, auto_name)
    await state.clear()
    
    if success:
        await callback.answer("✅ URL added!")
        await callback.message.edit_text(
            f"✅ <b>URL Added Successfully!</b>\n\n"
            f"<b>Name:</b> {auto_name}\n"
            f"<b>URL:</b> <code>{url}</code>"
        )
        await asyncio.sleep(2)
        # Return to uptime
        await refresh_uptime(callback)
    else:
        await callback.message.edit_text("❌ Failed to add URL. It might already exist.")

@router.message(URLState.waiting_for_name)
async def receive_name(message: types.Message, state: FSMContext):
    """Receive name and save URL"""
    data = await state.get_data()
    url = data.get("url")
    name = message.text.strip()
    
    success = await add_url(url, name)
    await state.clear()
    
    if success:
        await message.answer(f"✅ <b>URL Added Successfully!</b>\n\n<b>Name:</b> {name}\n<b>URL:</b> <code>{url}</code>")
        
        # Test ping
        await message.answer("🔄 Testing ping...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    await update_url_status(url, resp.status)
                    await message.answer(f"✅ Ping successful! Status: {resp.status}")
        except Exception as e:
            await update_url_status(url, error=str(e)[:100])
            await message.answer(f"⚠️ Initial ping failed: {str(e)[:100]}")
        
        # Return to uptime
        await asyncio.sleep(2)
        await uptime_cmd(message)
    else:
        await message.answer("❌ Failed to add URL. It might already exist.")

@router.callback_query(F.data == "remove_url")
async def remove_url_prompt(callback: CallbackQuery):
    """Remove URL - inline selection"""
    if callback.from_user.id != OWNER_ID:
        await callback.answer("❌ Only owner can remove URLs!", show_alert=True)
        return
    
    urls = await get_all_urls()
    
    if not urls:
        await callback.answer("📭 No URLs to remove!", show_alert=True)
        return
    
    # Create selection keyboard
    buttons = []
    for url_data in urls:
        name = url_data.get("name", "Unnamed")
        url = url_data["url"]
        short_url = url[:20] + "..." if len(url) > 20 else url
        buttons.append([InlineKeyboardButton(
            text=f"🗑️ {name} - {short_url}", 
            callback_data=f"remove_{url}"
        )])
    
    buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="refresh_uptime")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_caption(
        caption="🗑️ <b>Select URL to remove:</b>",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("remove_"))
async def confirm_remove(callback: CallbackQuery):
    """Confirm URL removal"""
    url = callback.data.replace("remove_", "")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes, Remove", callback_data=f"confirm_remove_{url}"),
            InlineKeyboardButton(text="❌ No", callback_data="refresh_uptime")
        ]
    ])
    
    await callback.message.edit_caption(
        caption=f"⚠️ <b>Are you sure?</b>\n\nRemove this URL?\n<code>{url}</code>",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("confirm_remove_"))
async def do_remove(callback: CallbackQuery):
    """Actually remove the URL"""
    url = callback.data.replace("confirm_remove_", "")
    
    success = await remove_url(url)
    
    await callback.answer("✅ Removed!" if success else "❌ Failed!")
    await refresh_uptime(callback)

@router.callback_query(F.data == "test_all")
async def test_all_urls(callback: CallbackQuery):
    """Test all URLs immediately"""
    await callback.answer("🔄 Testing all URLs...")
    
    await callback.message.edit_caption(
        caption="🔄 Testing all URLs... Please wait...",
        parse_mode="HTML"
    )
    
    await ping_all_urls()
    
    await callback.answer("✅ Test complete!")
    await refresh_uptime(callback)

@router.callback_query(F.data == "close_uptime")
async def close_uptime(callback: CallbackQuery):
    """Close uptime monitor"""
    await callback.answer("👋 Goodbye!")
    await callback.message.delete()

async def start_ping_task():
    global PING_TASK
    PING_TASK = asyncio.create_task(ping_loop())