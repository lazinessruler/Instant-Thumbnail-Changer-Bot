from aiogram import Router, types, F, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
from config import LOG_CHANNEL
from database import get_thumbnail, increment_usage, is_banned, add_user
import time
import asyncio

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

def get_processing_animation() -> list:
    """Cool processing animations."""
    return ["🎬", "⚙️", "🔄", "✨", "🎯", "💫", "⭐", "🌟"]

@router.message(F.video)
async def handle_video(message: types.Message, bot: Bot):
    """COOL: Handle video with style and swagger!"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    video = message.video
    
    # Check if banned
    if await is_banned(user_id):
        await message.react(emoji="⛔")
        await message.answer(
            f"<b>🚫 {small_caps('Access Denied')}</b>\n\n"
            f"<blockquote>{small_caps('You have been banned from using this bot.')}</blockquote>"
        )
        return
    
    # Add/update user
    await add_user(user_id, username, first_name)
    
    # Keep ORIGINAL caption
    caption = message.caption or ""
    
    # Get user's thumbnail
    thumb_file_id = await get_thumbnail(user_id)
    
    # Send processing message with animation
    processing_msg = await message.answer(
        f"<b>{small_caps('🎬 Processing Your Video')}</b>\n\n"
        f"<blockquote>{small_caps('Please wait...')}</blockquote>\n"
        f"<code>⚡ Applying your custom thumbnail ⚡</code>"
    )
    
    # Small delay for dramatic effect
    await asyncio.sleep(1)
    
    if thumb_file_id:
        try:
            # Add reaction to user's message
            await message.react(emoji="🎬")
            
            # Increment usage count
            await increment_usage(user_id)
            
            # Prepare cool caption with emojis
            final_caption = f"{caption}\n\n━━━━━━━━━━━━━━\n✨ <b>{small_caps('Powered by @xFlexyy')}</b> ✨" if caption else f"✨ <b>{small_caps('Powered by @xFlexyy')}</b> ✨"
            
            # Send video with custom cover
            await bot.send_video(
                chat_id=message.chat.id,
                video=video.file_id,
                caption=final_caption,
                cover=thumb_file_id,
                parse_mode="HTML"
            )
            
            # Delete processing message
            await processing_msg.delete()
            
            # Send success reaction
            await message.answer(
                f"<b>✅ {small_caps('Video Processed!')}</b>\n\n"
                f"<blockquote>{small_caps('Your custom thumbnail has been applied.')}</blockquote>"
            )
            
            # Log to channel
            if LOG_CHANNEL:
                try:
                    await bot.send_message(
                        chat_id=LOG_CHANNEL,
                        text=f"<b>🎥 ᴠɪᴅᴇᴏ ᴘʀᴏᴄᴇssᴇᴅ</b>\n\n"
                             f"<b>👤 ᴜsᴇʀ:</b> {first_name}\n"
                             f"<b>🔗 ᴜsᴇʀɴᴀᴍᴇ:</b> @{username or 'N/A'}\n"
                             f"<b>🆔 ɪᴅ:</b> <code>{user_id}</code>\n"
                             f"<b>📊 sɪᴢᴇ:</b> {video.file_size / (1024*1024):.2f} MB\n"
                             f"<b>⏱️ ᴅᴜʀᴀᴛɪᴏɴ:</b> {video.duration}s\n"
                             f"<b>📝 ᴄᴀᴘᴛɪᴏɴ:</b> {caption[:100] + '...' if len(caption) > 100 else caption or 'No caption'}",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
                    
        except Exception as e:
            await processing_msg.delete()
            await message.answer(
                f"<b>❌ {small_caps('Error Processing')}</b>\n\n"
                f"<blockquote>{small_caps('Something went wrong. Please try again.')}</blockquote>"
            )
            print(f"Video processing error: {e}")
    
    else:
        # No thumbnail set - cool warning with instructions
        await processing_msg.delete()
        
        # Create cool no-thumbnail keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🖼️ sᴇᴛ ᴛʜᴜᴍʙɴᴀɪʟ ɴᴏᴡ", callback_data="update_thumb")],
            [InlineKeyboardButton(text="📖 ʜᴏᴡ ᴛᴏ ᴜsᴇ", url="https://t.me/xFlexyy")]
        ])
        
        await message.answer(
            f"<b>⚠️ {small_caps('Thumbnail Missing!')}</b>\n\n"
            f"<blockquote>{small_caps('To add custom covers to your videos:')}</blockquote>\n\n"
            f"1️⃣ {small_caps('Click the button below')}\n"
            f"2️⃣ {small_caps('Send any photo')}\n"
            f"3️⃣ {small_caps('Send video & get thumbnail!')}\n\n"
            f"<b>{small_caps('✨ It\'s that simple!')}</b>",
            parse_mode="HTML",
            reply_markup=keyboard
        )

@router.message(F.video_note)
async def handle_video_note(message: types.Message, bot: Bot):
    """COOL: Handle video notes (round videos)."""
    user_id = message.from_user.id
    
    if await is_banned(user_id):
        await message.react(emoji="⛔")
        return
    
    await message.answer(
        f"<b>🎯 {small_caps('Video Notes Detected')}</b>\n\n"
        f"<blockquote>{small_caps('Video notes are not supported yet.')}</blockquote>\n"
        f"{small_caps('Send a regular video file instead!')}"
    )

@router.message(F.animation)
async def handle_gif(message: types.Message, bot: Bot):
    """COOL: Handle GIFs with style."""
    user_id = message.from_user.id
    
    if await is_banned(user_id):
        return
    
    await message.react(emoji="🎪")
    await message.answer(
        f"<b>🎪 {small_caps('Nice GIF!')}</b>\n\n"
        f"<blockquote>{small_caps('But I work with videos only.')}</blockquote>\n"
        f"{small_caps('Send me an MP4 file!')}"
    )
