# Thumbnail Changer Bot !!
# Made By Flexyy Team dByte !!
# Telegram Username:- @xFlexyy
# Community:- @DragonByte_Network

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from flask import Flask
import threading
import os
from config import API_TOKEN
from database import init_db, close_db, set_bot_start_time
from plugins import start_router, settings_router, video_router, admin_router
from uptime import router as uptime_router, start_ping_task
import datetime

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Register routers
dp.include_router(start_router)
dp.include_router(settings_router)
dp.include_router(video_router)
dp.include_router(admin_router)
dp.include_router(uptime_router)

app = Flask(__name__)

@app.route("/")
def home():
    return "Thumbnail Changer Bot !! - Made By Flexyy Team dByte !! | Community @DragonByte_Network"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

async def main():
    await init_db()
    
    # Save bot start time
    await set_bot_start_time(datetime.datetime.now())
    
    # Start ping task
    await start_ping_task()
    
    print(" Bot is starting with Uptime Monitor...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await close_db()

if __name__ == "__main__":
    print("""
     
 
            
              
            
              
                                        
          THUMBNAIL CHANGER BOT WORKING PROPERLY....
          WITH UPTIME MONITOR & MULTIPLE URL SUPPORT
          Made By Flexyy Team dByte !! | @xFlexyy | Community @DragonByte_Network
    """)
    print("Starting Bot...")
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())