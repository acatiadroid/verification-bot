import discord
import asyncio
from discord.ext import commands
from discord.ui import view
from main import VERIFIED_ROLE, VERIFY_OUTPUT, DIDNT_RESPOND


class AgeRange(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.timeout = 60
        self.age = ""
        self.value = False

    @discord.ui.button(style=discord.ButtonStyle.green, label="13-15", row=1)
    async def btnFirst(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.age = "13-15"
        self.value = True
        self.stop()

    @discord.ui.button(style=discord.ButtonStyle.green, label="16-17", row=1)
    async def btnSecond(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.age = "16-17"
        self.value = True
        self.stop()

    @discord.ui.button(style=discord.ButtonStyle.green, label="18+", row=1)
    async def btnThird(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.age = "18+"
        self.value = True
        self.stop()

    @discord.ui.button(style=discord.ButtonStyle.red, label="Prefer not to say", row=1)
    async def btnFourth(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.age = "Didn't specify."
        self.value = True
        self.stop()


class Furry(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = False
        self.furry = False
        self.timeout = 60
        
    @discord.ui.button(style=discord.ButtonStyle.blurple, label="Yes", row=1)
    async def btnYes(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        self.furry = True
        self.stop()

    @discord.ui.button(style=discord.ButtonStyle.grey, label="No", row=1)
    async def btnNo(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        self.furry = False
        self.stop()


class Actions(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.timeout = 15
        self.value = False
        self.action = ""
        self.ctx = None
    
    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id == interaction.user.id:
            await interaction.response.send_message("This isn't yours to control.", ephemeral=True)
            return False
        else:
            return True
    
    @discord.ui.button(style=discord.ButtonStyle.red, label="Ban", row=1)
    async def btnBan(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.action = "ban"
        self.value = True
        self.stop()

    @discord.ui.button(style=discord.ButtonStyle.red, label="Kick", row=1)
    async def btnKick(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.action = "kick"
        self.value = True
        self.stop()
    
    @discord.ui.button(style=discord.ButtonStyle.grey, label="Don't punish", row=1)
    async def btnIgnore(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.action = "ignore"
        self.value = True
        self.stop()
    

class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global botobj
        botobj = self.bot

    @commands.command()
    async def msg(self, ctx):
        view = Interaction()
        view.ctx = ctx
        view.bot = self.bot

        await ctx.send("⬇️", view=view)
    
    @commands.command()
    async def approve(self, ctx, member: discord.Member):
        admin = ctx.guild.get_role(877960792782278676)
        vrole = ctx.guild.get_role(VERIFIED_ROLE)
        if admin not in ctx.author.roles:
            return await ctx.send("You need **admin** role.")
        
    @commands.command()
    async def deny(self, ctx, member: discord.Member, reason: str = None):
        admin = ctx.guild.get_role(877960792782278676)
        vrole = ctx.guild.get_role(VERIFIED_ROLE)
        if admin not in ctx.author.roles:
            return await ctx.send("You need **admin** role.")
        if vrole in member.roles:
            return await ctx.send("This member has already been approved. (they have Viber role)")
        
        actions = Actions()
        actions.ctx = ctx
        
        reason = f"Reason for denial: {reason}" if reason else "*no reason was provided*"

        try:
            await member.send(f"Sorry, a mod denied your verification to join Fluffy Vibe.\n\n{reason}")
        except:
            await ctx.send(f":warning: **Unable to DM that {member}.**")

        await ctx.send(f"Alright, they have been denied.\n\nWould you like to punish {member}?", view=actions)
        
        await actions.wait()
        if not actions.value:
            return
        
        if actions.action == "ban":
            await member.ban(reason="Failed verification")
        elif actions.action == "kick":
            await member.kick(reason="Failed verification")
        else:
            return

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.persistant_view:
            self.bot.add_view(Interaction(), message_id=925872114047778846)
            self.bot.persistant_view = True
            print("persistant view added")
    
def setup(bot):
    bot.add_cog(Main(bot))

class Interaction(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.timeout = None
        self.interaction = None
        self.bot = botobj

    async def interaction_check(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(VERIFIED_ROLE)
        if role in interaction.user.roles:
            await interaction.response.send_message("You're already verified. (you have verified role)", ephemeral=True)
            return False
        await interaction.response.send_message("You have mail! Check your DMs. Make sure your DMs are on.", ephemeral=True)
        return True

    @discord.ui.button(style=discord.ButtonStyle.green, label="Click me to begin verification", row=1, custom_id="btn")
    async def btnVerify(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.interaction = interaction
        await self.begin_verification()
    
    async def begin_verification(self):
        try:
            dm = await self.interaction.user.create_dm()
        except:
            return
        questions = [
            "What is your name? (nickname accepted)", # User input
            "Nice name! Please select your age range.",# Buttons
            "Okay. Why did you join this server?", # User input
            "Alright. What is your sexual orientation? (Example: straight, gay, asexual)", # User input
            "What are your pronouns? (Example: he/him, they/them, she/her)", # User input
            "Are you a furry?", # Yes/No
            "How did you find this server?" # User Input
        ]

        data = {}

        await dm.send(embed=discord.Embed(title="Hey there!", description="Let's begin the verification process. Please answer truthfully! If you are not comfortable with answering a specific question, you can put \"N/A\".\n\nThere are 7 questions in total.", color=0x266bd3))
        await asyncio.sleep(5)
        for i in range(7):
            if i == 1:
                age_btns = AgeRange()

                await dm.send(questions[i], view=age_btns)

                await age_btns.wait()
                if age_btns.value:
                    data["age"] = age_btns.age
                    continue
                else:
                    return await dm.send(DIDNT_RESPOND)
            
            elif i == 5:
                furry = Furry()
                
                await dm.send(questions[i], view=furry)
                await furry.wait()
                if furry.value:
                    if furry.furry:
                        data["furry"] = "✅"
                    else:
                        data["furry"] = "🚫"
                    continue
                else:
                    return await dm.send(DIDNT_RESPOND)
            else:
                await dm.send(questions[i])
            
            def dm_check(message):
                return message.author.id == self.interaction.user.id
            
            try:
                msg = await self.bot.wait_for("message", timeout=60, check=dm_check)
                if i == 0:
                    data["name"] = msg.content
                elif i == 2:
                    data["join_reason"] = msg.content
                elif i == 3:
                    data["orientation"] = msg.content
                elif i == 4:
                    data["gender"] = msg.content
                elif i == 6:
                    data["found_server"] = msg.content
                else:
                    continue

            except asyncio.TimeoutError:
                return await dm.send(DIDNT_RESPOND)
        
        channel = self.bot.get_channel(VERIFY_OUTPUT)
        e = discord.Embed(
            title=f"Verification for {self.interaction.user}",
            color=0x58d4ef
        )
        e.add_field(name="Name:", value=data["name"])
        e.add_field(name="Reason for joining:", value=data["join_reason"], inline=False)
        e.add_field(name="Sexual orientation:", value=data["orientation"], inline=False)
        e.add_field(name="Pronouns:", value=data["gender"], inline=False)
        e.add_field(name="Furry?:", value=data["furry"], inline=False)
        e.add_field(name="Found this server:", value=data["found_server"], inline=False)
        e.add_field(name="Verification options:", value=f"`?approve {self.interaction.user.id}` to approve\n`?deny {self.interaction.user.id} <reason>`")

        e.set_thumbnail(url=self.interaction.user.avatar.url)
        await channel.send(content=f"ID: {self.interaction.user.id}", embed=e)
        await dm.send("Thanks! You're all done. Your answers will be reviewed by moderators. Hang tight!\n\n(*if you don't get a response within 2 days, DM a moderator.*)")
