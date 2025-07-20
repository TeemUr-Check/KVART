import os
import logging
from typing import Optional
import json
import httpx

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()

# LangFlow API configuration
LANGFLOW_API_KEY = os.getenv("sk-HD60fbsNWCkNivtgCP1LPH9FIIP0K0XOPKCBbz1YcsA")
LANGFLOW_API_URL = "http://localhost:7860/api/v1/run/adecbbe7-7ffd-4638-9d39-59849f5975da"

async def call_langflow_api(message_text: str):
    payload = {
        "output_type": "chat",
        "input_type": "chat",
        "input_value": message_text
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": LANGFLOW_API_KEY
    }

    try:
        response = requests.request("POST", LANGFLOW_API_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception for bad status codes
        return json.loads(response.text)['outputs'][0]['outputs'][0]['results']['message']['data']['text']
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling LangFlow API: {e}")
        return None

@dp.message(Command("start"))
async def start_handler(message: Message):
    """
    Handle /start command
    """
    welcome_text = (
        "👋 Hello! I'm a chatbot powered by LangFlow.\n\n"
        "Just send me a message and I'll respond using the LangFlow AI integration."
    )
    await message.answer(welcome_text)

@dp.message(Command("help"))
async def help_handler(message: Message):
    """
    Handle /help command
    """
    help_text = (
        "ℹ️ This bot uses LangFlow AI to respond to your messages.\n\n"
        "Available commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help message\n\n"
        "Just type anything else to chat with the AI!"
    )
    await message.answer(help_text)

@dp.message()
async def message_handler(message: types.Message):
    """
    Handle all text messages
    """
    # Show typing action to let user know we're working on the response
    print(message.document)
    await message.answer("Дайте-ка подумать...")
    await bot.send_chat_action(message.chat.id, "typing")

    # Call LangFlow API with the user's message
    api_response = await call_langflow_api(str(message.text))

    if api_response is None:
        await message.answer("Уупс... Кажется у меня проблемки с подключением...")
    else:
        await message.answer(api_response)

async def main():
    """
    Main function to start the bot
    """
    logger.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
