import discord
from discord.utils import get
from discord.ext import commands
import paper_scraper as ps
import time
from pdf2image import convert_from_path, convert_from_bytes
import os

bot = commands.Bot(command_prefix='$')
bot.remove_command("help")

class Session():
    def __init__(self, ctx, subject_code, year):
        self.ctx = ctx
        self.channel = ctx.channel
        self.subject_code = subject_code
        self.year = year
        self.season = ""  # "summer", "winter"
        self.paper = ""
        self.time_zone = ""
        self.pp = ps.PDFPaper(category = "A%20Levels", subject_code = self.subject_code, year = self.year)
        self.pp.subject = ps.subject_finder(self.pp)
        self.paper_count = ps.scan_papers(self.pp)
        self.user_answers = ""
        self.question_num = 1
        self.cancel = False
        
    async def get_choices(self):
        await self.get_seasons()
        await self.get_papers()
        await self.get_time_zone()
        await self.display_options()
        if self.cancel:
            await self.cancel_paper()
            return
        else:
            await self.display_paper()
            if self.cancel == False:
                await self.compile_answers()

    async def cancel_paper(self):
        embed=discord.Embed(
                title="CIEQPS MC",
                description="Paper ended!",
                color=discord.Color.blue())
        await self.channel.send(embed=embed)
        for i in range(1, 100):
            if os.path.isfile(f"{i}.pdf"):
                os.remove(f"{i}.pdf")
            if os.path.isfile(f"{i}.png"):
                os.remove(f"{i}.png")
        
    async def get_seasons(self):
        embed=discord.Embed(
            title="CIEQPS",
            description="Select a season!",
            color=discord.Color.blue())
        msg = await self.channel.send(embed=embed)
        emojis = ["🇲", "🇸", "🇼"]
        for x in emojis:
            await msg.add_reaction(x)
        def check(reaction, user):
            self.season = reaction.emoji
            return msg.author != user and reaction.message == msg and reaction.emoji in emojis
        await bot.wait_for('reaction_add', check=check)
        if self.season == emojis[0]:
            self.season = "m"
        elif self.season == emojis[1]:
            self.season = "s"
        elif self.season == emojis[2]:
            self.season = "w"
        
    async def get_papers(self):
        papers = set()
        for version in self.paper_count:
            if version[0] == self.season:
                papers.add(version[1])
        papers = list(papers)
        papers.sort()
        emojis = {"1":"1️⃣", "2":"2️⃣", "3":"3️⃣", "4":"4️⃣", "5":"5️⃣", "6":"6️⃣"}
        embed=discord.Embed(
            title="CIEQPS",
            description="Select a paper!",
            color=discord.Color.blue())
        msg = await self.channel.send(embed=embed)
        for x in range(len(papers)):
            papers[x] = emojis[str(x+1)]
        for x in papers:
            await msg.add_reaction(x)
        def check(reaction, user):
            self.paper = reaction.emoji
            return msg.author != user and reaction.message == msg and reaction.emoji in papers
        await bot.wait_for('reaction_add', check=check)
        self.paper = str(papers.index(self.paper)+1)
        
    async def get_time_zone(self):
        papers = set()
        for version in self.paper_count:
            if version[:2] == self.season+self.paper:
                papers.add(version[2])
        papers = list(papers)
        papers.sort()
        emojis = {"1":"1️⃣", "2":"2️⃣", "3":"3️⃣"}
        reverse = {"1️⃣":"1", "2️⃣":"2", "3️⃣":"3"}
        embed=discord.Embed(
            title="CIEQPS",
            description="Select a time zone!",
            color=discord.Color.blue())
        msg = await self.channel.send(embed=embed)
        for x in range(len(papers)):
            papers[x] = emojis[papers[x]]
        for x in papers:
            await msg.add_reaction(x)
        def check(reaction, user):
            self.time_zone = reaction.emoji
            return msg.author != user and reaction.message == msg and reaction.emoji in papers
        await bot.wait_for('reaction_add', check=check)
        self.time_zone = str(reverse[self.time_zone])

    async def display_options(self):
        embed=discord.Embed(
            title="CIEQPS",
            description=f"You have chosen: {self.subject_code} {self.year} {self.season}{self.paper}{self.time_zone}",
            color=discord.Color.blue())
        msg = await self.channel.send(embed=embed)
        emojis = ["✅", "❌"]
        for x in emojis:
            await msg.add_reaction(x)
        def check(reaction, user):
            global option
            option = str(reaction.emoji)
            return msg.author != user and reaction.message == msg and reaction.emoji in emojis
        await bot.wait_for('reaction_add', check=check)
        if option == emojis[1]:
            self.cancel = True

    async def display_paper(self):
        answers = {}
        embed=discord.Embed(
            title="CIEQPS",
            description="Creating paper...",
            color=discord.Color.blue())
        msg = await self.channel.send(embed=embed)
        self.pp.season = self.season
        self.pp.time_zone = self.time_zone
        self.pp.paper = self.paper
        self.question_num = ps.mc_questions(self.pp)
        for i in range(1, 5):
        #for i in range(1, self.question_num+1):
            pages = convert_from_path(f'{i}.pdf', 500, poppler_path = r'poppler-0.68.0\bin')
            pages[0].save(f'{i}.png', 'PNG')
            msg = await self.channel.send(file=discord.File(f'{i}.png'))
            emojis = ["🇦", "🇧", "🇨", "🇩", "⏩", "❌"]
            answer = {"🇦":"A","🇧":"B","🇨":"C","🇩":"D"} 
            for x in emojis:
                await msg.add_reaction(x)
            def check(reaction, user):
                global option
                option = str(reaction.emoji)
                return msg.author != user and reaction.message == msg and reaction.emoji in emojis
            await bot.wait_for('reaction_add', check=check)
            if option == "❌":
                self.cancel = True
                await self.cancel_paper()
                break
            elif option == "⏩":
                answers[i] = ""
            else:
                answers[i] = answer[option]
        if self.cancel != True:            
            self.user_answers = answers
        
    async def compile_answers(self):
        embed=discord.Embed(
            title="CIEQPS",
            description="Marking paper...",
            color=discord.Color.blue())
        msg = await self.channel.send(embed=embed)
        answers = ps.mc_ans_finder(self.pp)
        correct = 0
        wrong = []
        for qn in range(1, len(self.user_answers)+1):
            if answers[qn] == self.user_answers[qn]:
                correct += 1
            else:
                wrong.append([qn, answers[qn]])
        embed=discord.Embed(
            title="CIEQPS",
            description=f"You got {correct} right!",
            color=discord.Color.blue())
        await self.channel.send(embed=embed)
        if len(wrong) > 0:
            embed=discord.Embed(
                title="CIEQPS",
                description=f"Questions you got wrong:",
                color=discord.Color.blue())
            await self.channel.send(embed=embed)
            for i in wrong:
                msg = await self.channel.send(file=discord.File(f'{i[0]}.png'))
                if i[1] == "A":
                    await msg.add_reaction("🇦")
                elif i[1] == "B":
                    await msg.add_reaction("🇧")
                elif i[1] == "C":
                    await msg.add_reaction("🇨")
                elif i[1] == "D":
                    await msg.add_reaction("🇩")
        await self.cancel_paper()
        
@bot.command()
async def help(ctx):
    embed=discord.Embed(
        title="CIEQPS Help",
        description="CIEQPS is a bot... yea that's it",
        color=discord.Color.blue())
    embed.add_field(name="startmc", value="Begin setting up a multiple-choice question. Requires the subject code and year", inline=False)
    await ctx.channel.send(embed=embed)

@bot.command()
async def startmc(ctx, subject_code, year):
    embed=discord.Embed(
        title="CIEQPS",
        description="Starting paper...",
        color=discord.Color.blue())
    await ctx.channel.send(embed=embed)
    newSesh = Session(ctx, subject_code, year)
    await newSesh.get_choices()

@bot.event
async def on_ready():
    print("wa hoo")

bot.run("")
