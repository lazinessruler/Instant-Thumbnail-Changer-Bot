from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from config import CHANNEL_URL, DEV_URL, LOG_CHANNEL
from database import add_user, is_banned, get_user
import aiohttp
import os

router = Router()

def small_caps(text: str) -> str:
    """Convert text to small caps unicode."""
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

@router.message(Command("start"))
async def start_cmd(message: types.Message, bot: Bot):
    """Handle /start command with video and buttons."""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Check if banned
    if await is_banned(user_id):
        await message.answer(small_caps("You are banned from using this bot."))
        return
    
    # Check if new user
    existing_user = await get_user(user_id)
    is_new_user = existing_user is None
    
    # Add/update user in database
    await add_user(user_id, username, first_name)
    
    # Log new user to log channel
    if is_new_user and LOG_CHANNEL:
        try:
            await bot.send_message(
                chat_id=LOG_CHANNEL,
                text=f"👤 <b>ɴᴇᴡ ᴜsᴇʀ</b>\n\n"
                     f"🆔 <code>{user_id}</code>\n"
                     f"👤 {first_name}\n"
                     f"🔗 @{username or 'N/A'}",
                parse_mode="HTML"
            )
        except Exception:
            pass
    
    # Enhanced Welcome text in small caps with blockquote and emojis
    welcome_text = (
        f"<b>{small_caps('✨ Welcome to Thumbnail Bot! ✨')}</b>\n\n"
        f"<blockquote>{small_caps('Transform your videos with custom thumbnails effortlessly!')}</blockquote>\n\n"
        f"<b>{small_caps('📌 Quick Guide:')}</b>\n"
        f"<blockquote>"
        f"1️⃣ {small_caps('Set your thumbnail in Settings')}\n"
        f"2️⃣ {small_caps('Send any video file')}\n"
        f"3️⃣ {small_caps('Get your video with the custom thumbnail!')}\n"
        f"</blockquote>\n"
        f"<b>{small_caps('💡 Powered by @xFlexyy')}</b>"
    )
    
    # Buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="• sᴜᴘᴘᴏʀᴛ •", url=CHANNEL_URL),
            InlineKeyboardButton(text="• ᴅᴇᴠᴇʟᴏᴘᴇʀ •", url=DEV_URL)
        ],
        [InlineKeyboardButton(text="⚙️ sᴇᴛᴛɪɴɢs ", callback_data="settings")]
    ])
    
    # Video link
    video_url = "https://files.catbox.moe/yiyzkx.mp4"
    video_path = "start_video.mp4"
    
    # Download video if not exists
    if not os.path.exists(video_path):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url) as resp:
                    if resp.status == 200:
                        with open(video_path, 'wb') as f:
                            f.write(await resp.read())
        except Exception as e:
            print(f"Failed to download video: {e}")
    
    # Send video with caption
    try:
        if os.path.exists(video_path):
            video = FSInputFile(video_path)
            await bot.send_video(
                chat_id=message.chat.id,
                video=video,
                caption=welcome_text,
                parse_mode="HTML",
                reply_markup=keyboard,
                supports_streaming=True
            )
        else:
            # Fallback if video file is missing
            await message.answer(
                welcome_text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
    except Exception as e:
        print(f"Error sending video: {e}")
        # Final fallback
        await message.answer(
            welcome_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
