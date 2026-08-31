import feedparser
import urllib.request
import urllib.parse
import json
import time
import re
import os

from dotenv import load_dotenv

from google import genai
from google.genai import types

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)

MODEL_NAME = "gemini-3.5-flash"


# ============================================================
# AI NEWS SOURCES
# ============================================================

RSS_FEEDS = {
    "TechCrunch AI":
        "https://techcrunch.com/category/artificial-intelligence/feed/"
}


# ============================================================
# PRODUCT HUNT SOURCE
# ============================================================

PRODUCT_HUNT_RSS = "https://www.producthunt.com/feed"


# ============================================================
# GET AI NEWS
# ============================================================

def get_ai_news():

    news = []

    for source, url in RSS_FEEDS.items():

        try:

            print(f"📰 Reading {source}...")

            feed = feedparser.parse(url)

            for article in feed.entries[:5]:

                title = article.get(
                    "title",
                    "No title"
                )

                link = article.get(
                    "link",
                    "No link"
                )

                news.append({
                    "source": source,
                    "title": title,
                    "link": link
                })

        except Exception as error:

            print(
                f"❌ Error collecting news: {error}"
            )

    return news


# ============================================================
# PREPARE NEWS FOR GEMINI
# ============================================================

def prepare_news_for_gemini(news):

    news_text = ""

    for number, article in enumerate(
        news,
        start=1
    ):

        news_text += (
            f"\nNews {number}\n"
            f"Title: {article['title']}\n"
            f"Source: {article['source']}\n"
        )

    return news_text


# ============================================================
# GEMINI AI SUMMARY
# ============================================================

def generate_gemini_summary(news):

    news_text = prepare_news_for_gemini(news)

    prompt = f"""
You are an AI news editor.

Analyze exactly 5 AI news articles.

Create a short and professional Telegram news update.

STRICT RULES:

- Do not write an introduction.
- Do not use Markdown.
- Do not use bullet points.
- Do not include links.
- Keep every section short.
- Summary must be exactly one sentence.
- Why it matters must be exactly one sentence.
- Finish with one overall trend sentence.

Use exactly this format:

1️⃣ NEWS TITLE

📝 Summary:
One short sentence.

💡 Why it matters:
One short sentence.

2️⃣ NEWS TITLE

📝 Summary:
One short sentence.

💡 Why it matters:
One short sentence.

3️⃣ NEWS TITLE

📝 Summary:
One short sentence.

💡 Why it matters:
One short sentence.

4️⃣ NEWS TITLE

📝 Summary:
One short sentence.

💡 Why it matters:
One short sentence.

5️⃣ NEWS TITLE

📝 Summary:
One short sentence.

💡 Why it matters:
One short sentence.

🔥 OVERALL AI TREND

One short sentence only.

NEWS ARTICLES:

{news_text}
"""

    for attempt in range(1, 4):

        try:

            print(
                f"⏳ Asking Gemini... "
                f"Attempt {attempt}/3"
            )

            response = client.models.generate_content(

                model=MODEL_NAME,

                contents=prompt,

                config=types.GenerateContentConfig(

                    temperature=0.2,

                    max_output_tokens=2000,

                    thinking_config=types.ThinkingConfig(
                        thinking_level="low"
                    )
                )
            )

            if response and response.text:

                print(
                    "✅ Gemini summary generated!"
                )

                return response.text.strip()

            print(
                "❌ Gemini returned empty response."
            )

        except Exception as error:

            print(
                f"❌ Gemini error: {error}"
            )

            if attempt < 3:

                print(
                    "⏰ Waiting 20 seconds "
                    "before retry..."
                )

                time.sleep(20)

    print(
        "❌ Gemini failed after 3 attempts."
    )

    return None


# ============================================================
# FIND NEW AI TOOLS FROM PRODUCT HUNT
# ============================================================

def get_new_ai_tools():

    print(
        "\n🛠️ Searching Product Hunt "
        "for new AI tools..."
    )

    try:

        feed = feedparser.parse(
            PRODUCT_HUNT_RSS
        )

        if not feed.entries:

            print(
                "❌ No Product Hunt products found."
            )

            return []

        print(
            "✅ Product Hunt page loaded."
        )

        # ----------------------------------------------------
        # AI KEYWORDS
        # ----------------------------------------------------

        ai_keywords = [

            "ai",

            "artificial intelligence",

            "machine learning",

            "llm",

            "gpt",

            "chatbot",

            "copilot",

            "ai agent",

            "ai agents",

            "agentic",

            "automation",

            "generative ai",

            "voice ai",

            "image ai",

            "video ai",

            "coding ai",

            "developer ai",

            "ai assistant",

            "ai-powered",

            "ai powered"

        ]

        tools = []

        # ----------------------------------------------------
        # CHECK UP TO 50 RECENT PRODUCTS
        # ----------------------------------------------------

        for article in feed.entries[:50]:

            title = article.get(
                "title",
                ""
            ).strip()

            description = article.get(
                "summary",
                article.get(
                    "description",
                    ""
                )
            )

            link = article.get(
                "link",
                ""
            ).strip()

            # ------------------------------------------------
            # Skip incomplete products
            # ------------------------------------------------

            if not title or not link:

                continue

            # ------------------------------------------------
            # Remove HTML
            # ------------------------------------------------

            clean_description = re.sub(
                r"<[^>]+>",
                "",
                description
            )

            clean_description = re.sub(
                r"\s+",
                " ",
                clean_description
            ).strip()

            # ------------------------------------------------
            # Ignore Product Hunt itself
            # ------------------------------------------------

            if "product hunt" in title.lower():

                continue

            # ------------------------------------------------
            # Check whether product is AI related
            # ------------------------------------------------

            combined_text = (
                title
                + " "
                + clean_description
            ).lower()

            is_ai = False

            for keyword in ai_keywords:

                if keyword in combined_text:

                    is_ai = True

                    break

            if not is_ai:

                continue

            # ------------------------------------------------
            # Remove duplicate products
            # ------------------------------------------------

            duplicate = False

            for existing in tools:

                if existing["link"] == link:

                    duplicate = True

                    break

            if duplicate:

                continue

            # ------------------------------------------------
            # Save product
            # ------------------------------------------------

            tools.append({

                "title": title,

                "description":
                    clean_description,

                "link": link

            })

            # ------------------------------------------------
            # Stop after 5 AI products
            # ------------------------------------------------

            if len(tools) >= 5:

                break

        print(
            f"✅ Found {len(tools)} recent "
            f"AI products."
        )

        return tools

    except Exception as error:

        print(
            f"❌ Product Hunt error: {error}"
        )

        return []


# ============================================================
# FORMAT AI TOOLS
# ============================================================

def format_ai_tools(tools):

    if not tools:

        return None

    message = ""

    for number, tool in enumerate(
        tools,
        start=1
    ):

        title = tool["title"]

        description = tool["description"]

        link = tool["link"]

        # ----------------------------------------------------
        # Keep description short
        # ----------------------------------------------------

        if len(description) > 250:

            description = (
                description[:247]
                + "..."
            )

        # ----------------------------------------------------
        # Create Telegram tool section
        # ----------------------------------------------------

        message += (

            f"{number}️⃣ {title}\n\n"

            f"📝 What it does:\n"

            f"{description}\n\n"

            f"🔗 Product Hunt:\n"

            f"{link}\n\n"

        )

        if number < len(tools):

            message += (
                "━━━━━━━━━━━━━━━━━━\n\n"
            )

    return message.strip()


# ============================================================
# CREATE TELEGRAM MESSAGE
# ============================================================

def create_telegram_message(
    summary,
    ai_tools
):

    message = (

        "🤖 AI DAILY INTELLIGENCE\n\n"

        "🧠 TODAY'S AI NEWS\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

    )

    message += summary.strip()

    # --------------------------------------------------------
    # AI TOOLS
    # --------------------------------------------------------

    if ai_tools:

        message += (

            "\n\n"

            "━━━━━━━━━━━━━━━━━━\n"

            "🛠️ NEW AI TOOLS\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

        )

        message += ai_tools.strip()

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    message += (

        "\n\n"

        "━━━━━━━━━━━━━━━━━━\n"

        "🚀 Generated by My AI Intelligence Bot"

    )

    return message


# ============================================================
# SEND MESSAGE TO TELEGRAM
# ============================================================

def send_to_telegram(message):

    url = (

        f"https://api.telegram.org/"

        f"bot{BOT_TOKEN}/sendMessage"

    )

    data = urllib.parse.urlencode({

        "chat_id": CHAT_ID,

        "text": message,

        # Prevent Telegram from creating
        # website preview cards

        "disable_web_page_preview": "true"

    }).encode()

    try:

        print(
            "📡 Connecting to Telegram..."
        )

        request = urllib.request.Request(

            url,

            data=data,

            method="POST"

        )

        with urllib.request.urlopen(

            request,

            timeout=30

        ) as response:

            result = response.read().decode()

            result_data = json.loads(
                result
            )

            if result_data.get("ok"):

                print(
                    "✅ AI summary sent to Telegram!"
                )

            else:

                print(
                    "❌ Telegram rejected "
                    "the message."
                )

                print(result)

    except Exception as error:

        print(
            f"❌ Telegram error: {error}"
        )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("=" * 60)

    print(
        "🤖 AI DAILY INTELLIGENCE BOT"
    )

    print("=" * 60)


    # ========================================================
    # STEP 1 — COLLECT NEWS
    # ========================================================

    print(
        "\n🔍 Collecting latest AI news..."
    )

    news = get_ai_news()

    print(
        f"✅ Collected {len(news)} articles."
    )

    if not news:

        print(
            "❌ No news found."
        )

        return


    # ========================================================
    # STEP 2 — GEMINI NEWS SUMMARY
    # ========================================================

    print(
        "\n🧠 Sending news to Gemini AI..."
    )

    summary = generate_gemini_summary(
        news
    )

    if not summary:

        print(
            "❌ Could not generate "
            "Gemini summary."
        )

        return


    # ========================================================
    # STEP 3 — FIND REAL AI TOOLS
    # ========================================================

    tools = get_new_ai_tools()


    # ========================================================
    # STEP 4 — FORMAT AI TOOLS
    # ========================================================

    ai_tools = None

    if tools:

        ai_tools = format_ai_tools(
            tools
        )


    # ========================================================
    # STEP 5 — CREATE TELEGRAM MESSAGE
    # ========================================================

    print(
        "\n📝 Preparing Telegram message..."
    )

    telegram_message = (
        create_telegram_message(
            summary,
            ai_tools
        )
    )


    # ========================================================
    # STEP 6 — SEND TO TELEGRAM
    # ========================================================

    print(
        "\n📱 Sending summary to Telegram..."
    )

    send_to_telegram(
        telegram_message
    )


    # ========================================================
    # FINISHED
    # ========================================================

    print(
        "\n" + "=" * 60
    )

    print(
        "✅ DAILY AI INTELLIGENCE COMPLETED!"
    )

    print(
        "=" * 60
    )


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":

    main()