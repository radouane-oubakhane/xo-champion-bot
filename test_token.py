import os
import discord

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

class TestBot(discord.Client):
    async def on_ready(self):
        print(f'Successfully logged in as {self.user}')
        await self.close()

intents = discord.Intents.default()
client = TestBot(intents=intents)

client.run(TOKEN)