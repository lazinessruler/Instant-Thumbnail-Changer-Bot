from aiogram import Router, types, F, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from config import CHANNEL_URL, DEV_URL
from database import get_thumbnail, set_thumbnail, remove_thumbnail, is_banned
import random

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

class ThumbnailState(StatesGroup):
    waiting_for_thumbnail = State()

# Start images list (from your start.py)
START_IMAGES = [
    "https://i.postimg.cc/JnY5fHyX/026736497b6d047c910a0da13bd23e7b.jpg",
    "https://i.postimg.cc/rmZNBRdt/23c874004ccca79fdd3fbcb260a80829.jpg",
    "https://i.postimg.cc/LXQ3cgqY/2412165f7ca24a6422b4bdb96d169e98.jpg",
    "https://i.postimg.cc/xCp3wNkx/3511407df15923bbc85720e712cec44e.jpg",
    "https://i.postimg.cc/DZpP94WP/45b4da77420ccfff9ab8196944c8cf26.jpg",
    "https://i.postimg.cc/gJtHCLwV/57e045c8b5bba2adfa522f15d6bd9094.jpg",
    "https://i.postimg.cc/hjt0Z1GV/72702cbdbf3bf0ceeac3ef6d7f0c118b.jpg",
    "https://i.postimg.cc/zB2FsHLk/7926a8d03b5c9094761a7ca17202e356.jpg",
    "https://i.postimg.cc/85Xm2fFY/82c3c50baee7980a9ae08c017bb669e6.jpg",
    "https://i.postimg.cc/85Xm2fFB/b16da8b99a83d33ad649c48210b4f42d.jpg",
    "https://i.postimg.cc/vB2tJx13/ba221a265c809c0ce3f3a83a2735d2bc.jpg",
    "https://i.postimg.cc/fLqfGS39/dbffd4c10a7db8b310f760bc4f5d5427.jpg",
    "https://i.postimg.cc/xCp3wNk6/e8b74238880bd9d67ec728cff79415e0.jpg"
]

def get_random_start_image() -> str:
    """Return a random image URL from the list."""
    return random.choice(START_IMAGES)

def get_settings_keyboard():
    """Return the settings inline keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🖼️ ᴜᴘᴅᴀᴛᴇ ᴛʜᴜᴍʙɴᴀɪʟ", callback_data="update_thumb")],
        [InlineKeyboardButton(text="👁️ ᴠɪᴇᴡ ᴛʜᴜᴍʙɴᴀɪʟ", callback_data="view_thumb")],
        [InlineKeyboardButton(text="🗑️ ʀᴇᴍᴏᴠᴇ ᴛʜᴜᴍʙɴᴀɪʟ", callback_data="remove_thumb")],
        [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data="back_to_start")],
        [InlineKeyboardButton(text="❌ ᴄʟᴏsᴇ", callback_data="close_settings")]
    ])

def get_start_keyboard():
    """Return the start menu keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="• sᴜᴘᴘᴏʀᴛ •", url=CHANNEL_URL),
            InlineKeyboardButton(text="• ᴅᴇᴠᴇʟᴏᴘᴇʀ •", url=DEV_URL)
        ],
        [InlineKeyboardButton(text="⚙️ sᴇᴛᴛɪɴɢs ", callback_data="settings")]
    ])

def get_welcome_text() -> str:
    """Return the welcome message text."""
    return (
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

@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery, bot: Bot):
    """Show settings menu - EDITS the current message instead of deleting."""
    user_id = callback.from_user.id
    
    if await is_banned(user_id):
        await callback.answer(small_caps("You are banned!"), show_alert=True)
        return
    
    thumb = await get_thumbnail(user_id)
    status = f"✅ {small_caps('Thumbnail is set')}" if thumb else f"❌ {small_caps('No thumbnail set')}"
    
    text = (
        f"<b>⚙️ {small_caps('Thumbnail Settings')}</b>\n\n"
        f"<blockquote>{status}</blockquote>\n\n"
        f"{small_caps('Choose an option below:')}"
    )
    
    # Check if current message has photo or not
    if callback.message.photo:
        # If it's a photo message, edit caption only
        try:
            await callback.message.edit_caption(
                caption=text,
                parse_mode="HTML",
                reply_markup=get_settings_keyboard()
            )
        except TelegramBadRequest:
            # If edit fails, try to edit as text
            try:
                await callback.message.edit_text(
                    text=text,
                    parse_mode="HTML",
                    reply_markup=get_settings_keyboard()
                )
            except:
                pass
    else:
        # If it's text message, edit text
        try:
            await callback.message.edit_text(
                text=text,
                parse_mode="HTML",
                reply_markup=get_settings_keyboard()
            )
        except TelegramBadRequest:
            pass
    
    await callback.answer()

@router.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery, bot: Bot):
    """Go back to start message - EDITS the current message with new random image."""
    
    welcome_text = get_welcome_text()
    random_image = get_random_start_image()
    
    try:
        # Check if current message has photo
        if callback.message.photo:
            # Edit photo and caption
            await callback.message.edit_media(
                media=types.InputMediaPhoto(
                    media=random_image,
                    caption=welcome_text,
                    parse_mode="HTML"
                ),
                reply_markup=get_start_keyboard()
            )
        else:
            # If no photo, send new photo (can't add photo to text message)
            await callback.message.delete()
            await bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=random_image,
                caption=welcome_text,
                parse_mode="HTML",
                reply_markup=get_start_keyboard()
            )
    except TelegramBadRequest:
        # Fallback to text only
        try:
            await callback.message.edit_text(
                text=welcome_text,
                parse_mode="HTML",
                reply_markup=get_start_keyboard()
            )
        except:
            pass
    
    await callback.answer()

@router.callback_query(F.data == "update_thumb")
async def update_thumbnail_prompt(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Prompt user to send a new thumbnail - EDITS current message."""
    user_id = callback.from_user.id
    
    if await is_banned(user_id):
        await callback.answer(small_caps("You are banned!"), show_alert=True)
        return
    
    await state.set_state(ThumbnailState.waiting_for_thumbnail)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_update")]
    ])
    
    text = (
        f"<b>📸 {small_caps('Send me a photo')}</b>\n\n"
        f"<blockquote>{small_caps('This image will be used as the cover for your videos.')}</blockquote>"
    )
    
    # Edit current message
    try:
        if callback.message.photo:
            await callback.message.edit_caption(
                caption=text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        else:
            await callback.message.edit_text(
                text=text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
    except TelegramBadRequest:
        pass
    
    await callback.answer()

@router.callback_query(F.data == "cancel_update")
async def cancel_update(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Cancel the thumbnail update and go back to settings."""
    await state.clear()
    await show_settings(callback, bot)

@router.message(ThumbnailState.waiting_for_thumbnail, F.photo)
async def receive_thumbnail(message: types.Message, state: FSMContext):
    """Save the received photo as thumbnail."""
    user_id = message.from_user.id
    file_id = message.photo[-1].file_id
    
    await set_thumbnail(user_id, file_id)
    await state.clear()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ ʙᴀᴄᴋ ᴛᴏ sᴇᴛᴛɪɴɢs", callback_data="settings")]
    ])
    
    await message.answer(
        f"<b>✅ {small_caps('Thumbnail saved!')}</b>\n\n"
        f"<blockquote>{small_caps('Your videos will now use this cover image.')}</blockquote>",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "view_thumb")
async def view_thumbnail(callback: CallbackQuery, bot: Bot):
    """Show the user's current thumbnail - EDITS current message if possible."""
    user_id = callback.from_user.id
    thumb = await get_thumbnail(user_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ ʙᴀᴄᴋ ᴛᴏ sᴇᴛᴛɪɴɢs", callback_data="settings")]
    ])
    
    if thumb:
        # Try to edit current message with photo
        try:
            await callback.message.delete()  # Need to delete because can't edit text to photo
            await bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=thumb,
                caption=f"<b>🖼️ {small_caps('Your Current Thumbnail')}</b>",
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except:
            # Fallback
            await bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=thumb,
                caption=f"<b>🖼️ {small_caps('Your Current Thumbnail')}</b>",
                parse_mode="HTML",
                reply_markup=keyboard
            )
    else:
        text = (
            f"<b>❌ {small_caps('No thumbnail set')}</b>\n\n"
            f"<blockquote>{small_caps('Use Update Thumbnail to set one.')}</blockquote>"
        )
        
        # Edit current message
        try:
            if callback.message.photo:
                await callback.message.edit_caption(
                    caption=text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            else:
                await callback.message.edit_text(
                    text=text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
        except TelegramBadRequest:
            pass
    
    await callback.answer()

@router.callback_query(F.data == "remove_thumb")
async def remove_thumbnail_handler(callback: CallbackQuery, bot: Bot):
    """Remove the user's thumbnail - EDITS current message."""
    user_id = callback.from_user.id
    removed = await remove_thumbnail(user_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ ʙᴀᴄᴋ ᴛᴏ sᴇᴛᴛɪɴɢs", callback_data="settings")]
    ])
    
    if removed:
        text = (
            f"<b>🗑️ {small_caps('Thumbnail Removed')}</b>\n\n"
            f"<blockquote>{small_caps('Your videos will now be sent without a custom cover.')}</blockquote>"
        )
    else:
        text = (
            f"<b>❌ {small_caps('No thumbnail to remove')}</b>\n\n"
            f"<blockquote>{small_caps('You have not set a thumbnail yet.')}</blockquote>"
        )
    
    # Edit current message
    try:
        if callback.message.photo:
            await callback.message.edit_caption(
                caption=text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        else:
            await callback.message.edit_text(
                text=text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
    except TelegramBadRequest:
        pass
    
    await callback.answer()

@router.callback_query(F.data == "close_settings")
async def close_settings(callback: CallbackQuery):
    """Close the settings menu - delete message."""
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    await callback.answer(small_caps("Settings closed"))
