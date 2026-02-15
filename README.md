# 🎬 Video Thumbnail Bot

<p align="center">
    <b>A powerful and advanced Telegram bot to add custom thumbnails to your videos instantly.</b>
    <br><br>
    <a href="https://t.me/DragonByte_Network">
        <img src="https://img.shields.io/badge/Community-DragonByte__Network-blue?style=flat-square&logo=telegram" alt="Community">
    </a>
    <a href="https://t.me/xFlexyy">
        <img src="https://img.shields.io/badge/Developer-xFlexyy-blue?style=flat-square&logo=telegram" alt="Developer">
    </a>
</p>

---

## 🚀 About This Bot

Video Thumbnail Bot is a fast and powerful Telegram bot that allows users to:

- 🖼️ Set custom thumbnails for videos  
- ⚡ Instantly process and forward videos  
- 🔄 Use rotating dynamic start images  
- 👥 Store users securely in MongoDB  
- 🏆 Track top users with leaderboard system  
- 🛡️ Use advanced admin controls  

Perfect for Telegram content creators and power users.

---

## ✨ Features

- 🎨 Custom Thumbnail Support  
- ⚡ High-Speed Processing  
- 🔄 Rotating Start Images  
- 📊 Leaderboard System  
- 👥 MongoDB User Database  
- 🔐 Admin Panel (Ban / Broadcast / Stats)  
- 🐳 Docker Supported  
- ☁️ Deployable on Render, Heroku & Koyeb  

---

## 📦 Deployment Guide

### ☁️ Render (Recommended Free Tier)
1. Fork this repository  
2. Create a new **Web Service**  
3. Connect your GitHub repo  
4. Add Environment Variables  
5. Deploy  

---

### 💜 Heroku
1. Fork repository  
2. Create new app  
3. Connect GitHub  
4. Add Config Vars  
5. Deploy `web` dyno  

---

### 🟢 Koyeb
1. Fork repository  
2. Create new App  
3. Choose Docker deployment  
4. Add Environment Variables  
5. Deploy  

---

### 🐳 Docker
```bash
docker build -t thumbnail-bot .
docker run --env-file .env thumbnail-bot
```

---

### 💻 Run Locally
```bash
pip install -r requirements.txt
python main.py
```

---

## ⚙️ Configuration Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `API_TOKEN` | Bot Token from @BotFather | ✅ |
| `MONGO_URL` | MongoDB Connection String | ✅ |
| `OWNER_ID` | Your Telegram User ID | ✅ |
| `LOG_CHANNEL` | Log Channel ID (Optional) | ❌ |
| `CHANNEL_URL` | Join Channel URL | ❌ |
| `DEV_URL` | Developer URL | ❌ |

---

## 🤖 Bot Commands

```
start - Start the bot
users - (Admin) View all users
topleaderboard - (Admin) View leaderboard
broadcast - (Admin) Broadcast message
ban - (Admin) Ban a user
unban - (Admin) Unban a user
add_admin - (Owner) Add admin
remove_admin - (Owner) Remove admin
```

---

## 📁 Project Structure

```
thumbnail-bot/
├── main.py
├── config.py
├── database.py
├── plugins/
│   ├── start.py
│   ├── settings.py
│   ├── video.py
│   └── admin.py
├── Dockerfile
├── Procfile
└── requirements.txt
```

---

## 👑 Credits

- 💻 Original Developer: [@cantarella_wuwa](https://t.me/cantarella_wuwa)  
- 🔥 Modified & Enhanced By: [@xFlexyy](https://t.me/xFlexyy)  
- 🌐 Community: [@DragonByte_Network](https://t.me/DragonByte_Network)  

---

## 📌 Important Notice

This repository was created by forking the original project:

👉 https://github.com/cantarella-wuwa/cantarellabots-thumbnail-bot  

All core credits belong to the original developer.  
Please give proper credit if you use or modify this project.

---

<p align="center">
⭐ Star this repo if you like it!
</p>