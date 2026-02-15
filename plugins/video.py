from aiogram import Router, types, F, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
from config import LOG_CHANNEL
from database import get_thumbnail, increment_usage, is_banned, add_user
import asyncio

router = Router()

def small_caps(text: str) -> str:
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

@router.message(F.video)
async def handle_video(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    video = message.video
    
    if await is_banned(user_id):
        await message.react(emoji="⛔")
        return
    
    await add_user(user_id, username, first_name)
    
    caption = message.caption or None
    
    thumb_file_id = await get_thumbnail(user_id)
    
    if thumb_file_id:
        processing_msg = await message.answer("🎬")
        await asyncio.sleep(1)
        await processing_msg.delete()
        
        try:
            await message.react(emoji="🎬")
            
            await increment_usage(user_id)
            
            await bot.send_video(
                chat_id=message.chat.id,
                video=video.file_id,
                caption=caption,
                cover=thumb_file_id,
                parse_mode="HTML" if caption else None
            )
            
            if LOG_CHANNEL:
                try:
                    await bot.send_message(
                        chat_id=LOG_CHANNEL,
                        text=f"<b>🎥 ᴠɪᴅᴇᴏ ᴘʀᴏᴄᴇssᴇᴅ</b>\n\n"
                             f"<b>👤 ᴜsᴇʀ:</b> {first_name}\n"
                             f"<b>🔗 ᴜsᴇʀɴᴀᴍᴇ:</b> @{username or 'N/A'}\n"
                             f"<b>🆔 ɪᴅ:</b> <code>{user_id}</code>",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
                    
        except Exception as e:
            await message.answer("❌")
            print(f"Video processing error: {e}")
    
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🖼️ sᴇᴛ ᴛʜᴜᴍʙɴᴀɪʟ", callback_data="update_thumb")]
        ])
        
        await message.answer(
            f"<b>⚠️ {small_caps('No thumbnail set!')}</b>\n\n"
            f"{small_caps('Click below to set one.')}",
            parse_mode="HTML",
            reply_markup=keyboard
        )

@router.message(F.video_note)
async def handle_video_note(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    
    if await is_banned(user_id):
        return
    
    await message.answer(
        f"<b>🎯 {small_caps('Video notes not supported')}</b>\n\n"
        f"{small_caps('Send regular video.')}"
    )

@router.message(F.animation)
async def handle_gif(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    
    if await is_banned(user_id):
        return
    
    await message.answer(
        f"<b>🎪 {small_caps('GIFs not supported')}</b>\n\n"
        f"{small_caps('Send MP4 video.')}"
    )