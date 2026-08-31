🤖 AI Intelligence Bot

An automated Python bot that collects the latest AI news, uses Gemini AI to generate concise summaries, discovers new AI tools, and delivers a daily intelligence update to Telegram.

✨ Features

- 📰 Collects the latest AI news from TechCrunch
- 🧠 Uses Gemini AI to summarize news
- 💡 Explains why each news story matters
- 🛠️ Finds newly released AI tools
- 📱 Sends updates directly to Telegram
- ⏰ Runs automatically every day at 8:00 AM IST
- ☁️ Runs using GitHub Actions, so no laptop is required
- 🔐 Protects API keys using environment variables and GitHub Secrets

🛠️ Technologies

- Python
- Gemini API
- Telegram Bot API
- RSS Feeds
- Product Hunt
- GitHub Actions

🔄 How It Works

AI News Sources
      ↓
Python Bot
      ↓
Gemini AI
      ↓
News Summary + AI Tools
      ↓
Telegram Bot
      ↓
📱 Daily Intelligence Update

⏰ Automation

The bot runs automatically every day at **8:00 AM IST** using GitHub Actions.

Your laptop does not need to be turned on.

📁 Project Structure

AI-Intelligence-Bot/
│
├── .github/
│   └── workflows/
│       └── ai-bot.yml
│
├── main.py
├── requirements.txt
├── .gitignore
└── README.md