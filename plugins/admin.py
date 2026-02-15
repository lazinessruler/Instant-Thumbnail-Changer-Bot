from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import OWNER_ID
from database import (
    is_admin, add_admin, remove_admin, get_all_admins,
    ban_user, unban_user, get_all_users, get_user_count,
    get_leaderboard, get_user
)

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

class BroadcastState(StatesGroup):
    waiting_for_message = State()

async def check_admin(message: types.Message) -> bool:
    if not await is_admin(message.from_user.id):
        await message.answer(f"⛔ {small_caps('Admin only command.')}")
        return False
    return True

@router.message(Command("users"))
async def users_cmd(message: types.Message):
    if not await check_admin(message):
        return
    
    total = await get_user_count()
    
    await message.answer(
        f"<b>👥 {small_caps('Total Users:')}</b> <code>{total}</code>",
        parse_mode="HTML"
    )

@router.message(Command("add_admin"))
async def add_admin_cmd(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer(f"⛔ {small_caps('Owner only command.')}")
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer(f"❌ {small_caps('Usage: /add_admin <user_id>')}")
        return
    
    try:
        user_id = int(args[1])
    except ValueError:
        await message.answer(f"❌ {small_caps('Invalid user ID.')}")
        return
    
    await add_admin(user_id)
    await message.answer(f"✅ {small_caps('Admin added:')} <code>{user_id}</code>", parse_mode="HTML")

@router.message(Command("remove_admin"))
async def remove_admin_cmd(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer(f"⛔ {small_caps('Owner only command.')}")
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer(f"❌ {small_caps('Usage: /remove_admin <user_id>')}")
        return
    
    try:
        user_id = int(args[1])
    except ValueError:
        await message.answer(f"❌ {small_caps('Invalid user ID.')}")
        return
    
    if user_id == OWNER_ID:
        await message.answer(f"❌ {small_caps('Cannot remove owner.')}")
        return
    
    removed = await remove_admin(user_id)
    if removed:
        await message.answer(f"✅ {small_caps('Admin removed:')} <code>{user_id}</code>", parse_mode="HTML")
    else:
        await message.answer(f"❌ {small_caps('User was not an admin.')}")

@router.message(Command("ban"))
async def ban_cmd(message: types.Message):
    if not await check_admin(message):
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer(f"❌ {small_caps('Usage: /ban <user_id>')}")
        return
    
    try:
        user_id = int(args[1])
    except ValueError:
        await message.answer(f"❌ {small_caps('Invalid user ID.')}")
        return
    
    if user_id == OWNER_ID:
        await message.answer(f"❌ {small_caps('Cannot ban owner.')}")
        return
    
    if await is_admin(user_id):
        await message.answer(f"❌ {small_caps('Cannot ban an admin.')}")
        return
    
    banned = await ban_user(user_id)
    if banned:
        await message.answer(f"🚫 {small_caps('User banned:')} <code>{user_id}</code>", parse_mode="HTML")
    else:
        await message.answer(f"❌ {small_caps('User not found.')}")

@router.message(Command("unban"))
async def unban_cmd(message: types.Message):
    if not await check_admin(message):
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer(f"❌ {small_caps('Usage: /unban <user_id>')}")
        return
    
    try:
        user_id = int(args[1])
    except ValueError:
        await message.answer(f"❌ {small_caps('Invalid user ID.')}")
        return
    
    unbanned = await unban_user(user_id)
    if unbanned:
        await message.answer(f"✅ {small_caps('User unbanned:')} <code>{user_id}</code>", parse_mode="HTML")
    else:
        await message.answer(f"❌ {small_caps('User not found or not banned.')}")

@router.message(Command("topleaderboard"))
async def leaderboard_cmd(message: types.Message):
    if not await check_admin(message):
        return
    
    leaders = await get_leaderboard(10)
    
    if not leaders:
        await message.answer(f"📊 {small_caps('No usage data yet.')}")
        return
    
    text = f"<b>🏆 {small_caps('Top Leaderboard')}</b>\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    for i, user in enumerate(leaders):
        medal = medals[i] if i < 3 else f"{i+1}."
        user_id = user.get("user_id")
        username = user.get("username", "N/A")
        usage = user.get("usage_count", 0)
        text += f"{medal} @{username} (<code>{user_id}</code>) — <b>{usage}</b> {small_caps('videos')}\n"
    
    await message.answer(text, parse_mode="HTML")

@router.message(Command("broadcast"))
async def broadcast_cmd(message: types.Message, state: FSMContext):
    if not await check_admin(message):
        return
    
    await state.set_state(BroadcastState.waiting_for_message)
    await message.answer(
        f"📢 {small_caps('Send the message you want to broadcast.')}\n\n"
        f"<i>{small_caps('Send /cancel to cancel.')}</i>",
        parse_mode="HTML"
    )

@router.message(Command("cancel"))
async def cancel_broadcast(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        await message.answer(f"❌ {small_caps('Cancelled.')}")

@router.message(BroadcastState.waiting_for_message)
async def do_broadcast(message: types.Message, state: FSMContext, bot: Bot):
    await state.clear()
    
    users = await get_all_users()
    success = 0
    failed = 0
    
    status_msg = await message.answer(f"📢 {small_caps('Broadcasting...')} 0/{len(users)}")
    
    for i, user in enumerate(users):
        user_id = user.get("user_id")
        try:
            await bot.copy_message(
                chat_id=user_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
            success += 1
        except Exception:
            failed += 1
        
        if (i + 1) % 10 == 0:
            try:
                await status_msg.edit_text(
                    f"📢 {small_caps('Broadcasting...')} {i+1}/{len(users)}"
                )
            except Exception:
                pass
    
    await status_msg.edit_text(
        f"✅ {small_caps('Broadcast complete!')}\n\n"
        f"📨 {small_caps('Sent:')} {success}\n"
        f"❌ {small_caps('Failed:')} {failed}"
    )