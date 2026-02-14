# Developer: Flexyy Joren
# Telegram: @xFlexyy

from aiogram import Router, types, F, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import CHANNEL_URL, DEV_URL
from database import get_thumbnail, set_thumbnail, remove_thumbnail, is_banned

router = Router()


# --------- Serif Font (No Bold) ----------
def serif(text: str) -> str:
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    styled = "𝐴𝐵𝐶𝐷𝐸𝐹𝐺𝐻𝐼𝐽𝐾𝐿𝑀𝑁𝑂𝑃𝑄𝑅𝑆𝑇𝑈𝑉𝑊𝑋𝑌𝑍𝑎𝑏𝑐𝑑𝑒𝑓𝑔𝒉𝑖𝑗𝑘𝑙𝑚𝑛𝑜𝑝𝑞𝑟𝑠𝑡𝑢𝑣𝑤𝑥𝑦𝑧"
    return "".join(styled[normal.index(c)] if c in normal else c for c in text)


# --------- State ----------
class ThumbnailState(StatesGroup):
    waiting_for_thumbnail = State()


# --------- Keyboards ----------
def start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=serif("📢 Join Channel"), url=CHANNEL_URL),
            InlineKeyboardButton(text=serif("👨‍💻 Developer"), url=DEV_URL)
        ],
        [InlineKeyboardButton(text=serif("⚙️ Settings"), callback_data="settings")]
    ])


def settings_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=serif("🖼️ Update Thumbnail"), callback_data="update_thumb")],
        [InlineKeyboardButton(text=serif("👁️ View Thumbnail"), callback_data="view_thumb")],
        [InlineKeyboardButton(text=serif("🗑️ Remove Thumbnail"), callback_data="remove_thumb")],
        [InlineKeyboardButton(text=serif("🔙 Back"), callback_data="back_to_start")],
        [InlineKeyboardButton(text=serif("❌ Close"), callback_data="close_settings")]
    ])


# --------- SETTINGS OPEN (EDIT MESSAGE) ----------
@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery):
    user_id = callback.from_user.id

    if await is_banned(user_id):
        await callback.answer(serif("You are banned!"), show_alert=True)
        return

    thumb = await get_thumbnail(user_id)
    status = f"✅ {serif('Thumbnail is set')}" if thumb else f"❌ {serif('No thumbnail set')}"

    text = (
        f"{serif('Thumbnail Settings')}\n\n"
        f"<blockquote>{status}</blockquote>\n\n"
        f"{serif('Choose an option below:')}"
    )

    await callback.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=settings_keyboard()
    )
    await callback.answer()


# --------- BACK TO START (EDIT SAME MESSAGE) ----------
@router.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery):

    text = (
        f"{serif('Welcome to Thumbnail Bot!')}\n\n"
        f"<blockquote>{serif('Send me a video and I will add your custom thumbnail to it.')}</blockquote>\n\n"
        f"{serif('How to use:')}\n"
        f"<blockquote>"
        f"1️⃣ {serif('Set your thumbnail in Settings')}\n"
        f"2️⃣ {serif('Send any video')}\n"
        f"3️⃣ {serif('Get video with your thumbnail!')}"
        f"</blockquote>"
    )

    await callback.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=start_keyboard()
    )
    await callback.answer()


# --------- UPDATE THUMB ----------
@router.callback_query(F.data == "update_thumb")
async def update_thumb(callback: CallbackQuery, state: FSMContext):

    await state.set_state(ThumbnailState.waiting_for_thumbnail)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=serif("❌ Cancel"), callback_data="settings")]
    ])

    text = (
        f"{serif('Send me a photo')}\n\n"
        f"<blockquote>{serif('This image will be used as your video cover.')}</blockquote>"
    )

    await callback.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()


# --------- RECEIVE THUMB ----------
@router.message(ThumbnailState.waiting_for_thumbnail, F.photo)
async def receive_thumb(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    file_id = message.photo[-1].file_id

    await set_thumbnail(user_id, file_id)
    await state.clear()

    await message.answer(
        f"✅ {serif('Thumbnail Saved Successfully!')}",
        reply_markup=settings_keyboard()
    )


# --------- VIEW THUMB ----------
@router.callback_query(F.data == "view_thumb")
async def view_thumb(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    thumb = await get_thumbnail(user_id)

    if thumb:
        await bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=thumb,
            caption=serif("Your Current Thumbnail"),
            reply_markup=settings_keyboard()
        )
    else:
        await callback.answer(serif("No Thumbnail Set"), show_alert=True)


# --------- REMOVE THUMB ----------
@router.callback_query(F.data == "remove_thumb")
async def remove_thumb(callback: CallbackQuery):
    user_id = callback.from_user.id
    await remove_thumbnail(user_id)

    await callback.message.edit_text(
        text=f"🗑️ {serif('Thumbnail Removed Successfully')}",
        reply_markup=settings_keyboard()
    )
    await callback.answer()


# --------- CLOSE ----------
@router.callback_query(F.data == "close_settings")
async def close_settings(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()