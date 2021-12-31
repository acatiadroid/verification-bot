import discord
from discord.ext import commands


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="?",
                         help_command=commands.MinimalHelpCommand(),
                         allowed_mentions=discord.AllowedMentions(users=True,
                                                                  everyone=False,
                                                                  roles=False,
                                                                  replied_user=False),
                         intents=discord.Intents.all(),
                         description='A verification bot for Furry Vibe server.',
                         owner_id=600056626749112322,
                         case_insensitive=True)
        self.persistant_view = False

    async def on_ready(self):
        print('sup dude')

bot = Bot()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

SERVER = 877960484823900190
VERIFY_OUTPUT = 925872478352470086
VERIFIED_ROLE = 877961404617994250
DIDNT_RESPOND = "You didn't respond! Cancelled verification process. Please click the button in <#877961552198774794> to try again. Remember, you have 60 seconds to answer each specific question."


@bot.event
async def on_ready():
    print("hey")

bot.load_extension("verification")
bot.run("")
