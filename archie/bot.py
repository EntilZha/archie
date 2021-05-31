import os

import discord

ENTILZHA_ID = 200801932728729600


class BD1(discord.Client):
    async def on_ready(self):
        print("Logged on as {0}!".format(self.user))

    async def on_message(self, message):
        print("Message from {0.author}: {0.content}".format(message))
        print(f"{message.author.id}")


def main():
    bot = BD1()
    token = os.environ.get("DISCORD_BD1_TOKEN")
    if token is None:
        raise ValueError("DISCORD_BD1_TOKEN not set")
    user = bot.get_user(ENTILZHA_ID)
    user.send("Hello there")
    bot.run(token)


if __name__ == "__main__":
    main()
