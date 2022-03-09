import discord
from discord.utils import get
from discord.ext import commands
import paper_scraper as ps
import time
from pdf2image import convert_from_path, convert_from_bytes
import os
import asyncio
TIMEOUT = 60
Q_TIMEOUT = 600

class MultiChoice():
    def __init__(self, session, ID):
        self.session = session
        self.user_answers = ""
        self.session
        self.bot = session.bot
        self.pp = session.pp
        self.channel = session.channel
        self.question_num = ""
        self.season = session.season
        self.time_zone = session.time_zone
        self.paper = session.paper
        self.ID = str(ID)
        self.cancel = False

    async def start_paper(self):
        await self.display_paper()
        if self.cancel:
            await self.cancel_paper()
            return   
        await self.compile_answers()
        
    async def cancel_paper(self):
        embed=discord.Embed(
                title="CIEQPS MC",
                description="Paper ended!",
                color=discord.Color.blue())
        await self.channel.send(embed=embed)
        for i in range(1, 100):
            if os.path.isfile(f"{self.ID}{i}.pdf"):
                os.remove(f"{self.ID}{i}.pdf")
            if os.path.isfile(f"{self.ID}{i}.png"):
                os.remove(f"{self.ID}{i}.png")

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
        self.question_num = ps.mc_questions(self.pp, self.ID)
        for i in range(1, 5):
        #for i in range(1, self.question_num+1):
            pages = convert_from_path(f'{self.ID}{i}.pdf', 500, poppler_path = r'poppler-0.68.0\bin')
            pages[0].save(f'{self.ID}{i}.png', 'PNG')
            msg = await self.channel.send(file=discord.File(f'{self.ID}{i}.png'))
            emojis = ["🇦", "🇧", "🇨", "🇩", "⏩", "❌"]
            answer = {"🇦":"A","🇧":"B","🇨":"C","🇩":"D"} 
            for x in emojis:
                await msg.add_reaction(x)
            def check(reaction, user):
                global option
                option = str(reaction.emoji)
                return msg.author != user and reaction.message == msg and reaction.emoji in emojis
            try:
                await self.bot.wait_for('reaction_add', timeout=Q_TIMEOUT, check=check)
            except asyncio.TimeoutError:
                self.cancel = True
                return
            if option == "❌":
                self.cancel = True
                return
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
                msg = await self.channel.send(file=discord.File(f'{self.ID}{i[0]}.png'))
                if self.user_answers[i[0]] == "A":
                    await msg.add_reaction("🇦")
                    await msg.add_reaction("❌")
                elif self.user_answers[i[0]] == "B":
                    await msg.add_reaction("🇧")
                    await msg.add_reaction("❌")
                elif self.user_answers[i[0]] == "C":
                    await msg.add_reaction("🇨")
                    await msg.add_reaction("❌")
                elif self.user_answers[i[0]] == "D":
                    await msg.add_reaction("🇩")
                    await msg.add_reaction("❌")               
                if i[1] == "A":
                    await msg.add_reaction("🇦")
                elif i[1] == "B":
                    await msg.add_reaction("🇧")
                elif i[1] == "C":
                    await msg.add_reaction("🇨")
                elif i[1] == "D":
                    await msg.add_reaction("🇩")
                await msg.add_reaction("✅")
        await self.cancel_paper()
