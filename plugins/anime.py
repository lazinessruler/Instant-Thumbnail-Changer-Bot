import aiohttp
import asyncio
import datetime
import html
import textwrap
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.markdown import hbold, hcode, hlink
from bs4 import BeautifulSoup
import jikanpy
from config import OWNER_ID

# Create router for this module
router = Router()

# Module constants
MODULE_NAME = "Anime"
MODULE_DESCRIPTION = "Get information about anime, manga and characters"

# AniList API URL
ANILIST_API_URL = "https://graphql.anilist.co"

# Button texts
INFO_BTN = "More Information"
KAIZOKU_BTN = "Kaizoku ☠️"
KAYO_BTN = "Kayo 🏴‍☠️"
PREQUEL_BTN = "⬅️ Prequel"
SEQUEL_BTN = "Sequel ➡️"
CLOSE_BTN = "Close ❌"

# GraphQL Queries
AIRING_QUERY = """
query ($id: Int,$search: String) {
    Media (id: $id, type: ANIME,search: $search) {
        id
        episodes
        title {
            romaji
            english
            native
        }
        nextAiringEpisode {
            airingAt
            timeUntilAiring
            episode
        }
    }
}
"""

ANIME_QUERY = """
query ($id: Int,$search: String) {
    Media (id: $id, type: ANIME,search: $search) {
        id
        title {
            romaji
            english
            native
        }
        description (asHtml: false)
        startDate{
            year
        }
        episodes
        season
        type
        format
        status
        duration
        siteUrl
        studios{
            nodes{
                name
            }
        }
        trailer{
            id
            site
            thumbnail
        }
        averageScore
        genres
        bannerImage
    }
}
"""

CHARACTER_QUERY = """
query ($query: String) {
    Character (search: $query) {
        id
        name {
            first
            last
            full
        }
        siteUrl
        image {
            large
        }
        description
    }
}
"""

MANGA_QUERY = """
query ($id: Int,$search: String) {
    Media (id: $id, type: MANGA,search: $search) {
        id
        title {
            romaji
            english
            native
        }
        description (asHtml: false)
        startDate{
            year
        }
        type
        format
        status
        siteUrl
        averageScore
        genres
        bannerImage
    }
}
"""

FAV_QUERY = """
query ($id: Int) {
    Media (id: $id, type: ANIME) {
        id
        title {
            romaji
            english
            native
        }
    }
}
"""

def shorten(description: str, info: str = "anilist.co") -> str:
    """Shorten long descriptions"""
    if len(description) > 700:
        description = description[0:500] + "..."
        return f"\n*Description*: _{description}_ [Read More]({info})"
    else:
        return f"\n*Description*: _{description}_"

def format_time(milliseconds: int) -> str:
    """Format time from milliseconds"""
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    
    parts = []
    if days:
        parts.append(f"{days} Days")
    if hours:
        parts.append(f"{hours} Hours")
    if minutes:
        parts.append(f"{minutes} Minutes")
    if seconds:
        parts.append(f"{seconds} Seconds")
    if milliseconds:
        parts.append(f"{milliseconds} ms")
    
    return ", ".join(parts) if parts else "0 Seconds"

async def fetch_anilist(query: str, variables: dict):
    """Fetch data from AniList API"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                ANILIST_API_URL,
                json={"query": query, "variables": variables},
                timeout=10
            ) as resp:
                data = await resp.json()
                return data
        except Exception as e:
            print(f"AniList API error: {e}")
            return None

def extract_arg(message: types.Message) -> str:
    """Extract argument from message"""
    if not message.text:
        return None
        
    split = message.text.split(" ", 1)
    if len(split) > 1:
        return split[1]
    
    if message.reply_to_message and message.reply_to_message.text:
        return message.reply_to_message.text
    
    return None

@router.message(Command("airing"))
async def airing_command(message: types.Message):
    """Get anime airing information"""
    search_str = extract_arg(message)
    
    if not search_str:
        await message.reply(
            "❌ Please provide an anime name!\n"
            "Usage: /airing <anime name>"
        )
        return
    
    status_msg = await message.reply("🔍 Searching for anime...")
    
    variables = {"search": search_str}
    data = await fetch_anilist(AIRING_QUERY, variables)
    
    if not data or "errors" in data:
        await status_msg.edit_text("❌ Anime not found!")
        return
    
    media = data["data"]["Media"]
    
    # Format message
    title = media['title']['romaji']
    native = media['title']['native']
    
    text = (
        f"🎬 {hbold(title)} ({hcode(native)})\n"
        f"📋 ID: {hcode(str(media['id']))}\n"
    )
    
    if media.get("nextAiringEpisode"):
        next_ep = media["nextAiringEpisode"]
        time_str = format_time(next_ep["timeUntilAiring"] * 1000)
        text += (
            f"📺 Next Episode: {hbold(str(next_ep['episode']))}\n"
            f"⏰ Airing in: {hcode(time_str)}"
        )
    else:
        text += f"📺 Episodes: {media.get('episodes', 'N/A')}\n"
        text += f"⏰ Status: {hcode('Completed/Airing unknown')}"
    
    await status_msg.edit_text(text, parse_mode="HTML")

@router.message(Command("anime"))
async def anime_command(message: types.Message):
    """Get anime information"""
    search_str = extract_arg(message)
    
    if not search_str:
        await message.reply(
            "❌ Please provide an anime name!\n"
            "Usage: /anime <anime name>"
        )
        return
    
    status_msg = await message.reply("🔍 Searching for anime...")
    
    variables = {"search": search_str}
    data = await fetch_anilist(ANIME_QUERY, variables)
    
    if not data or "errors" in data:
        await status_msg.edit_text("❌ Anime not found!")
        return
    
    media = data["data"]["Media"]
    
    # Build message
    title_romaji = media['title']['romaji']
    title_native = media['title']['native']
    
    msg = (
        f"🎬 {hbold(title_romaji)} ({hcode(title_native)})\n"
        f"📺 Type: {media.get('format', 'N/A')}\n"
        f"📊 Status: {media.get('status', 'N/A')}\n"
        f"📋 Episodes: {media.get('episodes', 'N/A')}\n"
        f"⏱️ Duration: {media.get('duration', 'N/A')} min/ep\n"
        f"⭐ Score: {media.get('averageScore', 'N/A')}\n"
    )
    
    # Genres
    genres = media.get('genres', [])
    if genres:
        msg += f"🎭 Genres: {hcode(', '.join(genres[:5]))}\n"
    
    # Studios
    studios = media.get('studios', {}).get('nodes', [])
    if studios:
        studio_names = [s['name'] for s in studios[:3]]
        msg += f"🏢 Studios: {hcode(', '.join(studio_names))}\n"
    
    # Description
    description = media.get('description', 'No description available.')
    description = description.replace('<i>', '').replace('</i>', '').replace('<br>', '')
    if len(description) > 500:
        description = description[:500] + "..."
    msg += f"\n📝 {description}"
    
    # Buttons
    buttons = []
    info_url = media.get('siteUrl')
    if info_url:
        buttons.append([InlineKeyboardButton(text="📖 More Info", url=info_url)])
    
    # Trailer
    trailer = media.get('trailer')
    if trailer and trailer.get('site') == 'youtube':
        trailer_url = f"https://youtu.be/{trailer['id']}"
        buttons.append([InlineKeyboardButton(text="🎬 Trailer", url=trailer_url)])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None
    
    # Send with image if available
    image = media.get('bannerImage')
    if image:
        try:
            await status_msg.delete()
            await message.reply_photo(
                photo=image,
                caption=msg,
                parse_mode="HTML",
                reply_markup=keyboard
            )
            return
        except:
            pass
    
    await status_msg.edit_text(msg, parse_mode="HTML", reply_markup=keyboard)

@router.message(Command("character"))
async def character_command(message: types.Message):
    """Get character information"""
    search_str = extract_arg(message)
    
    if not search_str:
        await message.reply(
            "❌ Please provide a character name!\n"
            "Usage: /character <character name>"
        )
        return
    
    status_msg = await message.reply("🔍 Searching for character...")
    
    variables = {"query": search_str}
    data = await fetch_anilist(CHARACTER_QUERY, variables)
    
    if not data or "errors" in data:
        await status_msg.edit_text("❌ Character not found!")
        return
    
    character = data["data"]["Character"]
    
    # Build message
    name = character['name']['full']
    native = character['name'].get('native', '')
    
    msg = f"👤 {hbold(name)}"
    if native:
        msg += f" ({hcode(native)})"
    msg += "\n\n"
    
    # Description
    description = character.get('description', 'No description available.')
    description = description.replace('<b>', '').replace('</b>', '')
    if len(description) > 1000:
        description = description[:1000] + "..."
    msg += description
    
    # Image
    image = character.get('image', {}).get('large')
    if image:
        try:
            await status_msg.delete()
            await message.reply_photo(
                photo=image,
                caption=msg,
                parse_mode="HTML"
            )
            return
        except:
            pass
    
    await status_msg.edit_text(msg, parse_mode="HTML")

@router.message(Command("manga"))
async def manga_command(message: types.Message):
    """Get manga information"""
    search_str = extract_arg(message)
    
    if not search_str:
        await message.reply(
            "❌ Please provide a manga name!\n"
            "Usage: /manga <manga name>"
        )
        return
    
    status_msg = await message.reply("🔍 Searching for manga...")
    
    variables = {"search": search_str}
    data = await fetch_anilist(MANGA_QUERY, variables)
    
    if not data or "errors" in data:
        await status_msg.edit_text("❌ Manga not found!")
        return
    
    media = data["data"]["Media"]
    
    # Build message
    title_romaji = media['title']['romaji']
    title_native = media['title']['native']
    
    msg = (
        f"📚 {hbold(title_romaji)} ({hcode(title_native)})\n"
        f"📋 Type: {media.get('format', 'N/A')}\n"
        f"📊 Status: {media.get('status', 'N/A')}\n"
        f"📅 Start Year: {media.get('startDate', {}).get('year', 'N/A')}\n"
        f"⭐ Score: {media.get('averageScore', 'N/A')}\n"
    )
    
    # Genres
    genres = media.get('genres', [])
    if genres:
        msg += f"🎭 Genres: {hcode(', '.join(genres[:5]))}\n"
    
    # Description
    description = media.get('description', 'No description available.')
    description = description.replace('<i>', '').replace('</i>', '').replace('<br>', '')
    if len(description) > 500:
        description = description[:500] + "..."
    msg += f"\n📝 {description}"
    
    # Button
    info_url = media.get('siteUrl')
    keyboard = None
    if info_url:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📖 More Info", url=info_url)]
        ])
    
    # Send with image if available
    image = media.get('bannerImage')
    if image:
        try:
            await status_msg.delete()
            await message.reply_photo(
                photo=image,
                caption=msg,
                parse_mode="HTML",
                reply_markup=keyboard
            )
            return
        except:
            pass
    
    await status_msg.edit_text(msg, parse_mode="HTML", reply_markup=keyboard)

@router.message(Command("user"))
async def user_command(message: types.Message):
    """Get MyAnimeList user information"""
    search_str = extract_arg(message)
    
    if not search_str:
        await message.reply(
            "❌ Please provide a username!\n"
            "Usage: /user <username>"
        )
        return
    
    status_msg = await message.reply("🔍 Searching for user...")
    
    try:
        # Using jikanpy with asyncio
        loop = asyncio.get_event_loop()
        jikan = jikanpy.jikan.Jikan()
        user_data = await loop.run_in_executor(None, lambda: jikan.user(search_str))
    except Exception:
        await status_msg.edit_text("❌ User not found!")
        return
    
    # Format dates
    date_format = "%Y-%m-%d"
    
    try:
        if user_data.get('birthday'):
            birthday = datetime.datetime.fromisoformat(user_data['birthday'].replace('Z', '+00:00'))
            birthday_str = birthday.strftime(date_format)
        else:
            birthday_str = "Unknown"
    except:
        birthday_str = "Unknown"
    
    try:
        joined = datetime.datetime.fromisoformat(user_data['joined'].replace('Z', '+00:00'))
        joined_str = joined.strftime(date_format)
    except:
        joined_str = "Unknown"
    
    # Clean about section
    about = user_data.get('about', 'No bio available.')
    about = about.replace('<br>', '').strip()
    if len(about) > 200:
        about = about[:200] + "..."
    
    # Build message
    msg = (
        f"👤 {hbold(user_data['username'])}\n"
        f"🔗 {hlink('MAL Profile', user_data['url'])}\n\n"
        f"⚥ Gender: {user_data.get('gender', 'Unknown')}\n"
        f"🎂 Birthday: {birthday_str}\n"
        f"📅 Joined: {joined_str}\n"
        f"📺 Anime Days: {user_data.get('anime_stats', {}).get('days_watched', 0)}\n"
        f"📚 Manga Days: {user_data.get('manga_stats', {}).get('days_read', 0)}\n\n"
        f"📝 {about}"
    )
    
    # Image
    image = user_data.get('image_url')
    if image and image != "https://cdn.myanimelist.net/img/sp/icon_user.jpg":
        try:
            await status_msg.delete()
            await message.reply_photo(
                photo=image,
                caption=msg,
                parse_mode="HTML"
            )
            return
        except:
            pass
    
    await status_msg.edit_text(msg, parse_mode="HTML", disable_web_page_preview=True)

@router.message(Command("upcoming"))
async def upcoming_command(message: types.Message):
    """Get upcoming anime"""
    status_msg = await message.reply("🔍 Fetching upcoming anime...")
    
    try:
        loop = asyncio.get_event_loop()
        jikan = jikanpy.jikan.Jikan()
        upcoming = await loop.run_in_executor(
            None, 
            lambda: jikan.top("anime", page=1, subtype="upcoming")
        )
        
        upcoming_list = [entry["title"] for entry in upcoming["top"][:10]]
        
        msg = "📅 **Upcoming Anime:**\n\n"
        for i, title in enumerate(upcoming_list, 1):
            msg += f"{i}. {title}\n"
        
        await status_msg.edit_text(msg, parse_mode="MARKDOWN")
    except Exception as e:
        await status_msg.edit_text(f"❌ Error fetching upcoming anime: {str(e)}")

async def site_search(message: types.Message, site: str):
    """Search anime on specific sites"""
    search_str = extract_arg(message)
    
    if not search_str:
        await message.reply(f"❌ Please provide an anime name!\nUsage: /{site} <anime name>")
        return
    
    status_msg = await message.reply(f"🔍 Searching on {site}...")
    
    if site == "kaizoku":
        search_url = f"https://animekaizoku.com/?s={search_str.replace(' ', '+')}"
    elif site == "kayo":
        search_url = f"https://animekayo.com/?s={search_str.replace(' ', '+')}"
    else:
        return
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, timeout=10) as resp:
                html_text = await resp.text()
        
        soup = BeautifulSoup(html_text, "html.parser")
        
        if site == "kaizoku":
            results = soup.find_all("h2", {"class": "post-title"})
        else:  # kayo
            results = soup.find_all("h2", {"class": "title"})
        
        if not results or (len(results) == 1 and "Nothing Found" in results[0].text):
            await status_msg.edit_text(
                f"❌ No results found for '{search_str}' on {site}"
            )
            return
        
        msg = f"📦 **Results on {site}:**\n\n"
        count = 0
        for result in results:
            if count >= 10:
                break
            
            if site == "kaizoku":
                link = "https://animekaizoku.com/" + result.a["href"]
                title = result.text.strip()
            else:  # kayo
                if result.text.strip() == "Nothing Found":
                    continue
                link = result.a["href"]
                title = result.text.strip()
            
            msg += f"• [{title}]({link})\n"
            count += 1
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔍 View All Results", url=search_url)]
        ])
        
        await status_msg.edit_text(
            msg,
            parse_mode="MARKDOWN",
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Error searching: {str(e)}")

@router.message(Command("kaizoku"))
async def kaizoku_command(message: types.Message):
    """Search on Kaizoku"""
    await site_search(message, "kaizoku")

@router.message(Command("kayo"))
async def kayo_command(message: types.Message):
    """Search on Kayo"""
    await site_search(message, "kayo")

# Help text
HELP_TEXT = """
🎬 <b>Anime Module Commands:</b>

• /anime &lt;name&gt; - Get anime information
• /manga &lt;name&gt; - Get manga information
• /character &lt;name&gt; - Get character information
• /user &lt;username&gt; - Get MyAnimeList user info
• /upcoming - List upcoming anime
• /airing &lt;anime&gt; - Get airing information
• /kaizoku &lt;anime&gt; - Search on Kaizoku
• /kayo &lt;anime&gt; - Search on Kayo

<i>Powered by AniList and MyAnimeList</i>
"""

@router.message(Command("anime_help"))
async def anime_help_command(message: types.Message):
    """Show anime module help"""
    await message.reply(HELP_TEXT, parse_mode="HTML")

# Module metadata (similar to uptime.py)
__module_name__ = "Anime"
__module_description__ = "Get information about anime, manga and characters from AniList"
__commands__ = [
    "/anime - Get anime information",
    "/manga - Get manga information", 
    "/character - Get character information",
    "/user - Get MyAnimeList user information",
    "/upcoming - List upcoming anime",
    "/airing - Get anime airing info",
    "/kaizoku - Search on Kaizoku",
    "/kayo - Search on Kayo",
    "/anime_help - Show this help message"
]
__handlers__ = [
    "airing_command",
    "anime_command", 
    "character_command",
    "manga_command",
    "user_command",
    "upcoming_command",
    "kaizoku_command",
    "kayo_command",
    "anime_help_command"
]
