import discord
from discord.utils import get
from discord.ext import commands
import paper_scraper as ps
import time
from pdf2image import convert_from_path
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

    async def get_choices(self):
        await self.get_seasons()
        await self.get_papers()
        await self.get_time_zone()
        option = await self.display_options()
        if option == False:
            embed=discord.Embed(
                title="CIEQPS MC",
                description="Cancelled!",
                color=discord.Color.blue())
            await self.channel.send(embed=embed)
            return
        else:
            await self.display_paper()
        
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
        pp = ps.PDFPaper(category = "A%20Levels", subject_code = self.subject_code, year = self.year)
        pp.subject = ps.subject_finder(pp)
        paper_count = ps.scan_papers(pp)
        papers = set()
        for version in paper_count:
            pp.season = version[0]
            pp.paper = version[1]
            pp.time_zone = version[2]
            if pp.season == self.season:
                papers.add(pp.paper)
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
        pp = ps.PDFPaper(category = "A%20Levels", subject_code = self.subject_code, year = self.year)
        pp.subject = ps.subject_finder(pp)
        paper_count = ps.scan_papers(pp)
        papers = set()
        for version in paper_count:
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
        if option == emojis[0]:
            return True
        else:
            return False

    async def display_paper(self):
        embed=discord.Embed(
            title="CIEQPS",
            description="Creating paper...",
            color=discord.Color.blue())
        msg = await self.channel.send(embed=embed)
        pp = ps.PDFPaper(category = "A%20Levels", subject_code = self.subject_code, year = self.year)
        pp.subject = ps.subject_finder(pp)
        pp.season = self.season
        pp.time_zone = self.time_zone
        pp.paper = self.paper
        name = ps.mc_questions(pp)
        time.sleep(10)
        pages = convert_from_path(name, 50, poppler_path = r'poppler-22.01.0\Library\bin')
        q = 1
        for i in range(len(pages)):
            pages[i].save(f'{q}.png', 'PNG')
            q += 1
        #os.remove(name)
        for x in range(1,3):
            await self.channel.send(file=discord.File(f'{x}.png'))
            os.remove(f"{x}.png")
        
@bot.command()
async def help(ctx):
    embed=discord.Embed(
        title="CIEQPS Help",
        description="CIEQPS is a bot... yea that's it",
        color=discord.Color.blue())
    embed.add_field(name = chr(173), value = chr(173))
    embed.add_field(name="startmc", value="Begin setting up a multiple-choice question", inline=False)
    embed.add_field(name="Option2", value="Description", inline=False)
    embed.add_field(name="Option3", value="Description", inline=False)
    embed.add_field(name="Option4", value="Description", inline=False)
    embed.add_field(name="Option5", value="Description", inline=False)
    await ctx.channel.send(embed=embed)

@bot.command()
async def startmc(ctx, subject_code, year):
    newSesh = Session(ctx, subject_code, year)
    await newSesh.get_choices()
    
    
@bot.event
async def on_ready():
    print("wa hoo")

bot.run("OTQzMzk1MjUwNDE4OTAxMDMz.YgybSw.bKA8VXl2UVOYAYBtv73cB9jVZyQ")
