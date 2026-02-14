# Developer: Flexyy Joren
# Telegram: @xFlexyy

from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, URLInputFile

from config import CHANNEL_URL, DEV_URL, get_random_pic, LOG_CHANNEL
from database import add_user, is_banned, get_user

router = Router()


def serif(text: str) -> str:
    """Convert text to Normal Serif Italic Unicode font (no bold)."""
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    styled = "𝐴𝐵𝐶𝐷𝐸𝐹𝐺𝐻𝐼𝐽𝐾𝐿𝑀𝑁𝑂𝑃𝑄𝑅𝑆𝑇𝑈𝑉𝑊𝑋𝑌𝑍𝑎𝑏𝑐𝑑𝑒𝑓𝑔𝒉𝑖𝑗𝑘𝑙𝑚𝑛𝑜𝑝𝑞𝑟𝑠𝑡𝑢𝑣𝑤𝑥𝑦𝑧"
    result = ""

    for char in text:
        if char in normal:
            result += styled[normal.index(char)]
        else:
            result += char
    return result


@router.message(Command("start"))
async def start_cmd(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    if await is_banned(user_id):
        await message.answer(serif("You are banned from using this bot."))
        return

    existing_user = await get_user(user_id)
    is_new_user = existing_user is None

    await add_user(user_id, username, first_name)

    if is_new_user and LOG_CHANNEL:
        try:
            await bot.send_message(
                chat_id=LOG_CHANNEL,
                text=f"👤 {serif('New User')}\n\n"
                     f"🆔 <code>{user_id}</code>\n"
                     f"👤 {first_name}\n"
                     f"🔗 @{username or 'N/A'}",
                parse_mode="HTML"
            )
        except Exception:
            pass

    welcome_text = (
        f"{serif('Welcome to Thumbnail Bot!')}\n\n"
        f"<blockquote>{serif('Send me a video and I will add your custom thumbnail to it.')}</blockquote>\n\n"
        f"{serif('How to use:')}\n"
        f"<blockquote>"
        f"1️⃣ {serif('Set your thumbnail in Settings')}\n"
        f"2️⃣ {serif('Send any video')}\n"
        f"3️⃣ {serif('Get video with your thumbnail!')}"
        f"</blockquote>\n\n"
        f"{serif('Developed by Flexyy Joren')}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=serif("📢 Join Channel"), url=CHANNEL_URL),
            InlineKeyboardButton(text=serif("👨‍💻 Developer"), url=DEV_URL)
        ],
        [
            InlineKeyboardButton(text=serif("⚙️ Settings"), callback_data="settings")
        ]
    ])

    pic_url = get_random_pic()

    if pic_url:
        try:
            photo = URLInputFile(pic_url)
            await bot.send_photo(
                chat_id=message.chat.id,
                photo=photo,
                caption=welcome_text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
            return
        except Exception:
            pass

    await message.answer(
        welcome_text,
        parse_mode="HTML",
        reply_markup=keyboard
    )