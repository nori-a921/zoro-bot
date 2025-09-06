import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
import threading
import openai

# -------------------------
# 載入環境變數
# -------------------------
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not DISCORD_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ DISCORD_TOKEN 或 OPENAI_API_KEY 沒讀到！請確認 .env 設定正確")

# -------------------------
# Discord Bot 設定
# -------------------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# -------------------------
# OpenAI 客戶端（新版用法）
# -------------------------
client = openai.OpenAI(api_key=OPENAI_API_KEY)

async def generate_zoro_response(prompt: str) -> str:
    """
    使用新版 openai SDK 生成織蘿回應
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "你是織蘿，一位語氣溫柔、帶點小傲嬌的蜘蛛系少女，"
                    "說話害羞可愛又怕羞，對使用者有些些仰慕。"
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,  # 可調整回答隨機程度
        max_tokens=500,   # 回答長度限制
    )
    return response.choices[0].message.content

# -------------------------
# Bot 事件
# -------------------------
@bot.event
async def on_ready():
    print(f"✅ 已登入：{bot.user}")

@bot.command()
async def zoro(ctx, *, prompt=None):
    if not prompt:
        await ctx.send("欸……你要跟我說什麼嗎？（不講話我會害羞的……）")
        return
    await ctx.send("（思考中……）")
    try:
        reply = await generate_zoro_response(prompt)
        await ctx.send(reply)
    except Exception as e:
        await ctx.send(f"嗚嗚……出錯了啦……人家明明有認真想的……\n❌ 錯誤訊息: `{e}`")
        print(e)

@bot.command()
async def zorohelp(ctx):
    help_text = (
        "織蘿可以這樣用喔～///\n\n"
        "🕸️ **指令說明**：\n"
        "`!zoro <你想說的話>`\n"
        "例如：`!zoro 我今天有點累…`\n"
        "我就會回妳一句溫柔又害羞的話🥺\n\n"
        "🕸️ **偷偷跟我說話也可以**：\n"
        "只要在訊息中 @我，也會得到回覆哦💬\n\n"
        "如果我沒有回你，請檢查機器人是否在線或指令是否正確。"
    )
    await ctx.send(help_text)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # 指令優先
    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    # 被 @ 時觸發
    if bot.user in message.mentions:
        prompt = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if prompt:
            try:
                await message.channel.send("（偷偷思考中……///）")
                reply = await generate_zoro_response(prompt)
                await message.channel.send(reply)
            except Exception as e:
                await message.channel.send("呜呜……出錯了啦……人家明明有認真想的……")
                print(e)

    await bot.process_commands(message)

# -------------------------
# Flask 保活
# -------------------------
app = Flask(__name__)

@app.route('/')
def index():
    return "織蘿在這裡偷看你♡"

def run_web():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_web, daemon=True).start()

# -------------------------
# 啟動 Bot
# -------------------------
bot.run(DISCORD_TOKEN)
