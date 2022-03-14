import discord
from discord.utils import get
from discord.ext import commands
import paper_scraper as ps
import time
from pdf2image import convert_from_path, convert_from_bytes
import os
import asyncio
TIMEOUT = 60

class Session():
    def __init__(self, bot, ctx, subject_code, year, pp):
        self.bot = bot
        self.ctx = ctx
        self.channel = ctx.channel
        self.subject_code = subject_code
        self.year = year
        self.season = ""  # "summer", "winter"
        self.paper = ""
        self.time_zone = ""
        self.pp = pp
        self.paper_count = ps.scan_papers(pp)
        self.seasons = set([i[0] for i in self.paper_count])
        self.cancel = False

    async def cancel_paper(self):
        embed=discord.Embed(
                title="CIEQPS MC",
                description="Paper ended!",
                color=discord.Color.blue())
        await self.channel.send(embed=embed)
    
    async def get_choices(self):
        await self.get_seasons()
        if self.cancel:
            await self.cancel_paper()
            return
        await self.get_papers()
        if self.cancel:
            await self.cancel_paper()
            return    
        await self.get_time_zone()
        if self.cancel:
            await self.cancel_paper()
            return
        await self.display_options()
        if self.cancel:
            await self.cancel_paper()
            return               
        
    async def get_seasons(self):
        embed=discord.Embed(
            title="CIEQPS",
            description="Select a season!",
            color=discord.Color.blue())
        msg = await self.channel.send(embed=embed)
        emojis = ["🇲", "🇸", "🇼"]
        if "m" in self.seasons:
            await msg.add_reaction("🇲")
        if "s" in self.seasons:
            await msg.add_reaction("🇸")
        if "w" in self.seasons:
            await msg.add_reaction("🇼")
        def check(reaction, user):
            self.season = reaction.emoji
            return msg.author != user and reaction.message == msg and reaction.emoji in emojis
        try:
            await self.bot.wait_for('reaction_add', timeout=TIMEOUT, check=check)
        except asyncio.TimeoutError:
            self.cancel = True
            return
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
        try:
            await self.bot.wait_for('reaction_add', timeout=TIMEOUT, check=check)
        except asyncio.TimeoutError:
            self.cancel = True
            return
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
        try:
            await self.bot.wait_for('reaction_add', timeout=TIMEOUT, check=check)
        except asyncio.TimeoutError:
            self.cancel = True
            return
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
        try:
            await self.bot.wait_for('reaction_add', timeout=TIMEOUT, check=check)
        except asyncio.TimeoutError:
            self.cancel = True
            return
        if option == emojis[1]:
            self.cancel = True
