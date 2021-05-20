from bot import Bot

# initialize the bot
bot = Bot(command_prefix="!")

if __name__ == "__main__":
    # only run the bot if this file is being run directly
    bot.run(bot.config['core']['token'])
