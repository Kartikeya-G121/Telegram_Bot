import requests
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
from urllib.parse import quote
import re
import json

TOKEN: Final = "6837521529:AAFJqZl2TYgluimozBHu5XLWHoJlCD8lSo0"
BOT_USERNAME: Final = "@Desparado_Bot"
LYRICS_API_URL: Final = 'https://private-anon-43faa5c492-lyricsovh.apiary-proxy.com/v1/'


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "What I do? I ball like there's no tomorrow. Just Kidding, I fetch all the lyrics you need for your karaoke! Just use /lyrics (song_name)!")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "You need somethin'? Here's a list of all the commands you can use! \n/start - Starting the bot \n/help - lists out all the commands \n/lyrics - find the lyrics of all your favorite songs")


async def lyrics_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = ' '.join(context.args)  # Get the query from the command arguments
    if not query:
        await update.message.reply_text("Please provide the song title and artist.")
        return

    if ' - ' in query:
        song_title, artist_name = query.rsplit(' - ', 1)
    else:
        song_title, artist_name = query, 'Unknown'

    def clean_text(text):
        text = re.sub(r'\\n', '...', text)
        text = re.sub(r'\\', '', text)
        text = re.sub(r'{|}', '', text)
        text = re.sub(r'\\r', '...', text)
        return text.replace('"', '')

    song_title = quote(song_title)
    artist_name = quote(artist_name)

    # Construct the API request URL
    response = requests.get(f'{LYRICS_API_URL}/{artist_name}/{song_title}')
    response.raise_for_status()  # Check if the request was successful

    # Extract the text content
    text_content = response.text

    # Clean the text
    cleaned_text_content = clean_text(text_content)

    # Prepare the JSON format
    lyrics_data = {"lyrics": cleaned_text_content}

    lyrics_json = json.dumps(lyrics_data, indent=4)

    # Print or save the JSON
    lyrics = lyrics_json
    if lyrics:
        await update.message.reply_text(lyrics)
    else:
        await update.message.reply_text("Failed to retrieve lyrics. Please check the song title and artist.")


# Responses
def handle_responses(text: str) -> str:
    processed: str = text.lower()

    if "hello" in processed:
        return "Sup Dawg!"

    elif "how are you" in processed:
        return "I'm good, how's you my man?"

    elif "what's the weather like" in processed:
        return "A Sunny Side up, just how I like it."

    else:
        return "Come again?"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_type: str = update.message.chat.type  # Group Chat or Private Chat
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in ({message_type}): "{text}" ')

    if message_type == "group":  # Handles all the group chats
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME,
                                         "").strip()  # We don't want the bot username to be processed as part of the text
            response: str = handle_responses(new_text)
        else:
            return  # The bot shouldn't respond until it is called.
    else:
        response: str = handle_responses(text)  # Handles all the private chats

    print("Bot:", response)  # Prints the response
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f'Update {update} caused error {context.error}')


async def shutdown(application: Application) -> None:
    """Shut down the bot."""
    await application.bot.close()
    await application.shutdown()


if __name__ == '__main__':
    print("Starting Bot")
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('lyrics', lyrics_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Error Handling
    app.add_error_handler(error)

    # Start polling the bot's updates
    try:
        print("Polling...")
        asyncio.run(app.run_polling(poll_interval=3))
    except:  # Handle KeyboardInterrupt to gracefully stop the bot
        print("Shutting down the bot...")
        asyncio.run(shutdown(app))
