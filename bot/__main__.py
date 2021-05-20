from bot import Bot
import argparse

parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument("-p", "--prefix", default="!")

args = parser.parse_args()

# initialize the bot
bot = Bot(command_prefix=args.prefix)

if __name__ == "__main__":
    # only run the bot if this file is being run directly
    bot.run(bot.config['core']['token'])
