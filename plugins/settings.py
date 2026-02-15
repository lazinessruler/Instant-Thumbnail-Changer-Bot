from aiogram import Router, types, F, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from config import CHANNEL_URL, DEV_URL
from database import get_thumbnail, set_thumbnail, remove_thumbnail, is_banned
import random
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

class ThumbnailState(StatesGroup):
    waiting_for_thumbnail = State()

START_IMAGES = [
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

def get_random_start_image() -> str:
    return random.choice(START_IMAGES)

def get_settings_keyboard(thumb_status: bool = False):
    status_emoji = "✅" if thumb_status else "❌"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🖼️ ᴜᴘᴅᴀᴛᴇ ᴛʜᴜᴍʙɴᴀɪʟ", callback_data="update_thumb")],
        [InlineKeyboardButton(text=f"👁️ ᴠɪᴇᴡ ᴛʜᴜᴍʙɴᴀɪʟ {status_emoji}", callback_data="view_thumb")],
        [InlineKeyboardButton(text=f"🗑️ ʀᴇᴍᴏᴠᴇ ᴛʜᴜᴍʙɴᴀɪʟ", callback_data="remove_thumb")],
        [
            InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data="back_to_start"),
            InlineKeyboardButton(text="❌ ᴄʟᴏsᴇ", callback_data="close_settings")
        ]
    ])

def get_start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
       [
            InlineKeyboardButton(text="ᴡ", callback_data="none1"),
            InlineKeyboardButton(text="ᴇ", callback_data="none2"),
            InlineKeyboardButton(text="ʟ", callback_data="none3"),
            InlineKeyboardButton(text="ᴄ", callback_data="none4"),
            InlineKeyboardButton(text="ᴏ", callback_data="none5"),
            InlineKeyboardButton(text="ᴍ", callback_data="none6"),
            InlineKeyboardButton(text="ᴇ", callback_data="none7"),
        ],
 [
            InlineKeyboardButton(text="• sᴜᴘᴘᴏʀᴛ •", url=CHANNEL_URL),
            InlineKeyboardButton(text="• ᴅᴇᴠᴇʟᴏᴘᴇʀ •", url=DEV_URL)
        ],
        [InlineKeyboardButton(text="⚙️ sᴇᴛᴛɪɴɢs ", callback_data="settings")]
    ])

def get_welcome_text() -> str:
    return (
        f"<b>{small_caps('✨ Welcome to Thumbnail Bot! ✨')}</b>\n\n"
        f"<blockquote>{small_caps('Transform your videos with custom thumbnails effortlessly!')}</blockquote>\n\n"
        f"<b>{small_caps('📌 Quick Guide:')}</b>\n"
        f"1️⃣ {small_caps('Set your thumbnail in Settings')}\n"
        f"2️⃣ {small_caps('Send any video file')}\n"
        f"3️⃣ {small_caps('Get your video with the custom thumbnail!')}\n\n"
        f"<b>{small_caps('💡 Powered by dByte Network')}</b>"
    )

@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    
    if await is_banned(user_id):
        await callback.answer(small_caps("You are banned!"), show_alert=True)
        return
    
    await callback.answer("⚙️ Opening settings...", show_alert=False)
    
    thumb = await get_thumbnail(user_id)
    status = f"✅ {small_caps('Thumbnail is set')}" if thumb else f"❌ {small_caps('No thumbnail set')}"
    
    text = (
        f"<b>⚙️ {small_caps('Thumbnail Settings')}</b>\n\n"
        f"{status}\n\n"
        f"{small_caps('Choose an option below:')}"
    )
    
    try:
        if callback.message.photo:
            await callback.message.edit_caption(
                caption=text,
                parse_mode="HTML",
                reply_markup=get_settings_keyboard(bool(thumb))
            )
        else:
            await callback.message.edit_text(
                text=text,
                parse_mode="HTML",
                reply_markup=get_settings_keyboard(bool(thumb))
            )
    except TelegramBadRequest:
        await callback.message.delete()
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text=text,
            parse_mode="HTML",
            reply_markup=get_settings_keyboard(bool(thumb))
        )
    
    await callback.answer()

@router.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery, bot: Bot):
    await callback.answer("🏠 Going home...", show_alert=False)
    
    welcome_text = get_welcome_text()
    random_image = get_random_start_image()
    
    try:
        if callback.message.photo:
            await callback.message.edit_media(
                media=types.InputMediaPhoto(
                    media=random_image,
                    caption=welcome_text,
                    parse_mode="HTML"
                ),
                reply_markup=get_start_keyboard()
            )
        else:
            await callback.message.delete()
            await bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=random_image,
                caption=welcome_text,
                parse_mode="HTML",
                reply_markup=get_start_keyboard()
            )
    except TelegramBadRequest:
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
    user_id = callback.from_user.id
    
    if await is_banned(user_id):
        await callback.answer(small_caps("You are banned!"), show_alert=True)
        return
    
    await callback.answer("📸 Prepare your photo...", show_alert=False)
    await state.set_state(ThumbnailState.waiting_for_thumbnail)
    
    await state.update_data(original_chat_id=callback.message.chat.id)
    await state.update_data(original_message_id=callback.message.message_id)
    await state.update_data(original_has_photo=bool(callback.message.photo))
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_update")]
    ])
    
    text = (
        f"<b>📸 {small_caps('Send Thumbnail')}</b>\n\n"
        f"{small_caps('Please send a high-quality photo.')}\n"
        f"{small_caps('This will be your video cover.')}"
    )
    
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
    await state.clear()
    await callback.answer("↩️ Cancelled", show_alert=False)
    await show_settings(callback, bot)

@router.message(ThumbnailState.waiting_for_thumbnail, F.photo)
async def receive_thumbnail(message: types.Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    file_id = message.photo[-1].file_id
    
    data = await state.get_data()
    original_chat_id = data.get('original_chat_id')
    original_message_id = data.get('original_message_id')
    original_has_photo = data.get('original_has_photo', False)
    
    await set_thumbnail(user_id, file_id)
    await state.clear()
    
    try:
        await message.delete()
    except:
        pass
    
    try:
        original_message = await bot.edit_message_reply_markup(
            chat_id=original_chat_id,
            message_id=original_message_id,
            reply_markup=None
        )
        
        success_text = (
            f"<b>✅ {small_caps('Thumbnail Updated!')}</b>\n\n"
            f"{small_caps('Your new cover is ready.')}\n"
            f"{small_caps('All videos will now use this thumbnail.')}"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⚙️ ʙᴀᴄᴋ ᴛᴏ sᴇᴛᴛɪɴɢs", callback_data="settings"),
                InlineKeyboardButton(text="👁️ ᴠɪᴇᴡ ᴛʜᴜᴍʙɴᴀɪʟ", callback_data="view_thumb")
            ]
        ])
        
        await bot.edit_message_media(
            chat_id=original_chat_id,
            message_id=original_message_id,
            media=types.InputMediaPhoto(
                media=file_id,
                caption=success_text,
                parse_mode="HTML"
            ),
            reply_markup=keyboard
        )
        
    except Exception as e:
        print(f"Error transforming message: {e}")
        success_text = (
            f"<b>✅ {small_caps('Thumbnail Updated!')}</b>\n\n"
            f"{small_caps('Your new cover is ready.')}"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ ʙᴀᴄᴋ ᴛᴏ sᴇᴛᴛɪɴɢs", callback_data="settings")]
        ])
        
        await message.answer_photo(
            photo=file_id,
            caption=success_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

@router.callback_query(F.data == "view_thumb")
async def view_thumbnail(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    thumb = await get_thumbnail(user_id)
    
    if thumb:
        await callback.answer("🖼️ Loading thumbnail...", show_alert=False)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🖼️ ᴜᴘᴅᴀᴛᴇ", callback_data="update_thumb"),
                InlineKeyboardButton(text="🗑️ ʀᴇᴍᴏᴠᴇ", callback_data="remove_thumb")
            ],
            [InlineKeyboardButton(text="⚙️ ʙᴀᴄᴋ ᴛᴏ sᴇᴛᴛɪɴɢs", callback_data="settings")]
        ])
        
        try:
            if callback.message.photo:
                await callback.message.edit_media(
                    media=types.InputMediaPhoto(
                        media=thumb,
                        caption=f"<b>🖼️ {small_caps('Your Current Thumbnail')}</b>\n\n{small_caps('This cover will appear on all your videos.')}",
                        parse_mode="HTML"
                    ),
                    reply_markup=keyboard
                )
            else:
                await callback.message.delete()
                await bot.send_photo(
                    chat_id=callback.message.chat.id,
                    photo=thumb,
                    caption=f"<b>🖼️ {small_caps('Your Current Thumbnail')}</b>\n\n{small_caps('This cover will appear on all your videos.')}",
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
        except:
            pass
    else:
        await callback.answer("❌ No thumbnail set", show_alert=True)
        await show_settings(callback, bot)
    
    await callback.answer()

@router.callback_query(F.data == "remove_thumb")
async def remove_thumbnail_handler(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    thumb = await get_thumbnail(user_id)
    
    if not thumb:
        await callback.answer("❌ No thumbnail to remove", show_alert=True)
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ ʏᴇs, ʀᴇᴍᴏᴠᴇ", callback_data="confirm_remove"),
            InlineKeyboardButton(text="❌ ɴᴏ", callback_data="settings")
        ]
    ])
    
    text = (
        f"<b>⚠️ {small_caps('Confirm Removal')}</b>\n\n"
        f"{small_caps('Are you sure you want to remove your thumbnail?')}\n"
        f"{small_caps('Videos will be sent without custom cover.')}"
    )
    
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
    except:
        pass
    
    await callback.answer()

@router.callback_query(F.data == "confirm_remove")
async def confirm_remove(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    removed = await remove_thumbnail(user_id)
    
    if removed:
        await callback.answer("🗑️ Thumbnail removed", show_alert=False)
        
        text = (
            f"<b>✅ {small_caps('Thumbnail Removed')}</b>\n\n"
            f"{small_caps('Your thumbnail has been deleted.')}"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ ʙᴀᴄᴋ ᴛᴏ sᴇᴛᴛɪɴɢs", callback_data="settings")]
        ])
        
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
        except:
            pass
    else:
        await callback.answer("❌ Error removing thumbnail", show_alert=True)
        await show_settings(callback, bot)
    
    await callback.answer()

@router.callback_query(F.data == "close_settings")
async def close_settings(callback: CallbackQuery):
    await callback.answer("👋 Goodbye!", show_alert=False)
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass