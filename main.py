import discord
from discord.utils import get
from discord.ext import commands
import paper_scraper as ps
import multi_choice as mc
import start_paper as sp
import time
from pdf2image import convert_from_path, convert_from_bytes
import os
import asyncio
bot = commands.Bot(command_prefix='$')
bot.remove_command("help")

@bot.command()
async def help(ctx):
    embed=discord.Embed(
        title="CIEQPS Help",
        description="Made by Gamenado#8487 and NathanHueg#8084",
        color=discord.Color.blue())
    embed.add_field(name="start", value="Begin setting up a paper. Requires the subject code and year", inline=False)
    await ctx.channel.send(embed=embed)

@bot.command()
async def start(ctx, subject_code, year):
    avaliable_years = [str(i) for i in range(2010, 2022)]
    pp = ps.PDFPaper(category = "A%20Levels", subject_code = subject_code, year = year)
    pp.subject = ps.subject_finder(pp)
    if year not in avaliable_years and pp.subject == "":
        embed=discord.Embed(
        title="CIEQPS",
        description="Invalid subject code and year!",
        color=discord.Color.blue())
        await ctx.channel.send(embed=embed)
        return
    if pp.subject == "":
        embed=discord.Embed(
        title="CIEQPS",
        description="Invalid subject code!",
        color=discord.Color.blue())
        await ctx.channel.send(embed=embed)
        return
    if year not in avaliable_years:
        embed=discord.Embed(
        title="CIEQPS",
        description="Invalid year!",
        color=discord.Color.blue())
        await ctx.channel.send(embed=embed)
        return
    embed=discord.Embed(
        title="CIEQPS",
        description="Starting paper...",
        color=discord.Color.blue())
    await ctx.channel.send(embed=embed)                          
    session_id = hash(str(ctx.author)+subject_code+year)
    newSesh = sp.Session(bot, ctx, subject_code, year, pp)
    await newSesh.get_choices()
    if newSesh.cancel == True:
        return
    if newSesh.paper == "1":
        MCSesh = mc.MultiChoice(newSesh, session_id)
        await MCSesh.start_paper()
    

@bot.event
async def on_ready():
    print("CIEQPS online")

bot.run("")
