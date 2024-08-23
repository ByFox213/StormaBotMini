import asyncio
from StormaLibs import start_bot

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

bot, tk = start_bot([435836413523787778])

if __name__ == '__main__':
    bot.run(tk)
