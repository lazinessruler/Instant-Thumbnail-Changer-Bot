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