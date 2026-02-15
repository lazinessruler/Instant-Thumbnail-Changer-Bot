from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, URLInputFile
from config import CHANNEL_URL, DEV_URL, LOG_CHANNEL
from database import add_user, is_banned, get_user
import random

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

@router.message(Command("start"))
async def start_cmd(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    if await is_banned(user_id):
        await message.answer(small_caps("You are banned from using this bot."))
        return
    
    existing_user = await get_user(user_id)
    is_new_user = existing_user is None
    
    await add_user(user_id, username, first_name)
    
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
    
    welcome_text = (
        f"<b>{small_caps('✨ Welcome to Thumbnail Bot! ✨')}</b>\n\n"
        f"<blockquote>{small_caps('Transform your videos with custom thumbnails effortlessly!')}</blockquote>\n\n"
        f"<b>{small_caps('📌 Quick Guide:')}</b>\n"
        f"1️⃣ {small_caps('Set your thumbnail in Settings')}\n"
        f"2️⃣ {small_caps('Send any video file')}\n"
        f"3️⃣ {small_caps('Get your video with the custom thumbnail!')}\n\n"
        f"<b>{small_caps('💡 Powered by dByte Network')}</b>"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
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
        [
            InlineKeyboardButton(text="⚙️ sᴇᴛᴛɪɴɢs", callback_data="settings")
        ]
])
    
    image_url = get_random_start_image()
    
    try:
        photo = URLInputFile(image_url)
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=photo,
            caption=welcome_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Error sending image: {e}")
        await message.answer(
            welcome_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )