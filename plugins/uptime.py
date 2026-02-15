import aiohttp
import asyncio
import datetime
from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import OWNER_ID
from database import is_admin, add_url, remove_url, get_all_urls, update_url_status, toggle_url, set_bot_start_time, get_bot_start_time

router = Router()

# Global variables
START_TIME = datetime.datetime.now()
PING_TASK = None
BOT_NAME = "Thumbnail Changer Bot"

class URLState(StatesGroup):
    waiting_for_url = State()
    waiting_for_name = State()
    waiting_for_remove = State()

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
    """Continuous ping loop - har 5 minute mein"""
    while True:
        await ping_all_urls()
        await asyncio.sleep(300)  # 5 minutes

@router.message(Command("uptime"))
async def uptime_cmd(message: types.Message):
    """Main uptime command - sab kuch yahin se manage karo"""
    global START_TIME
    
    uptime_str = get_uptime()
    is_admin_user = await is_admin(message.from_user.id)
    
    # Get all URLs from database
    urls = await get_all_urls()
    
    # Create URL list text
    url_list_text = ""
    if urls:
        for i, url_data in enumerate(urls, 1):
            name = url_data.get("name", "Unnamed")
            url = url_data["url"]
            active = "✅" if url_data.get("active", True) else "❌"
            last_ping = url_data.get("last_ping")
            last_status = url_data.get("last_status", "Never")
            
            if last_ping:
                time_diff = datetime.datetime.now() - last_ping
                mins_ago = int(time_diff.total_seconds() / 60)
                last_ping_str = f"{mins_ago}m ago"
            else:
                last_ping_str = "Never"
            
            url_list_text += f"{i}. {active} <b>{name}</b>\n"
            url_list_text += f"   <code>{url}</code>\n"
            url_list_text += f"   Last: {last_ping_str} | Status: {last_status}\n\n"
    else:
        url_list_text = "   No URLs configured yet.\n"
    
    text = (
        f"<b>🤖 {BOT_NAME} - Uptime Monitor</b>\n\n"
        f"<b>📅 Started:</b> {START_TIME.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"<b>⏰ Uptime:</b> <code>{uptime_str}</code>\n"
        f"<b>🔗 Total URLs:</b> {len(urls)}\n"
        f"<b>⏱️ Ping Interval:</b> Every 5 minutes\n\n"
        f"<b>📋 Monitored URLs:</b>\n{url_list_text}"
    )
    
    # Admin keyboard
    if is_admin_user:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Add New URL", callback_data="add_url")],
            [InlineKeyboardButton(text="🗑️ Remove URL", callback_data="remove_url")],
            [InlineKeyboardButton(text="🔄 Test All Now", callback_data="test_all")],
            [InlineKeyboardButton(text="❌ Close", callback_data="close_uptime")]
        ])
        await message.answer(text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await message.answer(text, parse_mode="HTML")

@router.callback_query(F.data == "add_url")
async def add_url_prompt(callback: CallbackQuery, state: FSMContext):
    """Naya URL add karne ka prompt"""
    if callback.from_user.id != OWNER_ID:
        await callback.answer("❌ Only owner can add URLs!", show_alert=True)
        return
    
    await callback.answer()
    await state.set_state(URLState.waiting_for_url)
    
    text = (
        f"<b>➕ Add New URL</b>\n\n"
        f"Send me the URL you want to monitor:\n"
        f"<code>https://your-app.onrender.com</code>\n"
        f"<code>https://another-bot.onrender.com</code>\n\n"
        f"<i>Send /cancel to cancel</i>"
    )
    
    await callback.message.edit_text(text, parse_mode="HTML")

@router.message(URLState.waiting_for_url)
async def receive_url(message: types.Message, state: FSMContext):
    """URL receive karein"""
    url = message.text.strip()
    
    if not (url.startswith("http://") or url.startswith("https://")):
        await message.answer("❌ Invalid URL! Must start with http:// or https://")
        return
    
    if url.endswith("/"):
        url = url[:-1]
    
    # Save to state and ask for name
    await state.update_data(url=url)
    await state.set_state(URLState.waiting_for_name)
    
    auto_name = url.replace("https://", "").replace("http://", "").split(".")[0]
    
    text = (
        f"✅ URL received: <code>{url}</code>\n\n"
        f"Send a name for this URL (or send 'skip' for auto-name):\n"
        f"Example: <code>Main Bot</code>\n"
        f"Auto name will be: <b>{auto_name}</b>"
    )
    
    await message.answer(text, parse_mode="HTML")

@router.message(URLState.waiting_for_name)
async def receive_name(message: types.Message, state: FSMContext):
    """Name receive karein aur URL save karein"""
    data = await state.get_data()
    url = data.get("url")
    
    name_input = message.text.strip()
    
    if name_input.lower() == "skip":
        name = url.replace("https://", "").replace("http://", "").split(".")[0]
    else:
        name = name_input
    
    # Save to database
    success = await add_url(url, name)
    
    if success:
        await state.clear()
        text = (
            f"✅ <b>URL Added Successfully!</b>\n\n"
            f"<b>Name:</b> {name}\n"
            f"<b>URL:</b> <code>{url}</code>\n\n"
            f"It will be pinged every 5 minutes."
        )
        await message.answer(text, parse_mode="HTML")
        
        # Test ping immediately
        await message.answer("🔄 Testing ping...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    await update_url_status(url, resp.status)
                    await message.answer(f"✅ Ping successful! Status: {resp.status}")
        except Exception as e:
            await update_url_status(url, error=str(e)[:100])
            await message.answer(f"⚠️ Initial ping failed: {str(e)[:100]}")
    else:
        await message.answer("❌ Failed to add URL. It might already exist.")

@router.callback_query(F.data == "remove_url")
async def remove_url_prompt(callback: CallbackQuery, state: FSMContext):
    """URL remove karne ka prompt"""
    if callback.from_user.id != OWNER_ID:
        await callback.answer("❌ Only owner can remove URLs!", show_alert=True)
        return
    
    urls = await get_all_urls()
    
    if not urls:
        await callback.answer("📭 No URLs to remove!", show_alert=True)
        return
    
    # Create keyboard with all URLs
    buttons = []
    for url_data in urls:
        name = url_data.get("name", "Unnamed")
        url = url_data["url"]
        short_url = url[:30] + "..." if len(url) > 30 else url
        buttons.append([InlineKeyboardButton(text=f"🗑️ {name}", callback_data=f"remove_{url}")])
    
    buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="back_to_uptime")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(
        "🗑️ <b>Select URL to remove:</b>",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("remove_"))
async def confirm_remove(callback: CallbackQuery):
    """URL remove confirmation"""
    url = callback.data.replace("remove_", "")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes, Remove", callback_data=f"confirm_remove_{url}"),
            InlineKeyboardButton(text="❌ No", callback_data="back_to_uptime")
        ]
    ])
    
    await callback.message.edit_text(
        f"⚠️ <b>Are you sure?</b>\n\nRemove this URL?\n<code>{url}</code>",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("confirm_remove_"))
async def do_remove(callback: CallbackQuery):
    """Actually remove the URL"""
    url = callback.data.replace("confirm_remove_", "")
    
    success = await remove_url(url)
    
    if success:
        await callback.answer("✅ URL removed!")
        text = "✅ URL removed successfully!"
    else:
        await callback.answer("❌ Failed to remove!")
        text = "❌ Failed to remove URL."
    
    # Go back to uptime menu
    await uptime_cmd(callback.message, callback.bot)

@router.callback_query(F.data == "test_all")
async def test_all_urls(callback: CallbackQuery):
    """Test all URLs immediately"""
    await callback.answer("🔄 Testing all URLs...", show_alert=False)
    
    await callback.message.edit_text("🔄 Testing all URLs... Please wait...")
    
    await ping_all_urls()
    
    await callback.message.edit_text("✅ Test complete! Check /uptime for results.")
    await uptime_cmd(callback.message, callback.bot)

@router.callback_query(F.data == "back_to_uptime")
async def back_to_uptime(callback: CallbackQuery):
    """Back to main uptime menu"""
    await uptime_cmd(callback.message, callback.bot)

@router.callback_query(F.data == "close_uptime")
async def close_uptime(callback: CallbackQuery):
    """Close the uptime menu"""
    await callback.answer()
    await callback.message.delete()

@router.message(Command("cancel"))
async def cancel_cmd(message: types.Message, state: FSMContext):
    """Cancel any ongoing operation"""
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        await message.answer("✅ Cancelled.")

# Start ping task
async def start_ping_task():
    global PING_TASK
    PING_TASK = asyncio.create_task(ping_loop())