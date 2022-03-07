<<<<<<< HEAD
<<<<<<< HEAD
=======
import discord
from discord.utils import get
from discord.ext import commands
import paper_scraper as ps
import multi_choice as mc
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
    embed.add_field(name="startmc", value="Begin setting up a multiple-choice question. Requires the subject code and year", inline=False)
    await ctx.channel.send(embed=embed)

@bot.command()
async def startmc(ctx, subject_code, year):
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
    newSesh = mc.MCSession(bot, ctx, subject_code, year, session_id, pp)
    await newSesh.get_choices()

@bot.event
async def on_ready():
    print("CIEQPS online")

bot.run("OTQzMzk1MjUwNDE4OTAxMDMz.YgybSw.5i34VYUnuGpgoziaEVFYcYx9Xls")
>>>>>>> parent of cd84af2... Changed bot name
=======
import discord
from discord.utils import get
from discord.ext import commands
import paper_scraper as ps
import multi_choice as mc
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
    embed.add_field(name="startmc", value="Begin setting up a multiple-choice question. Requires the subject code and year", inline=False)
    await ctx.channel.send(embed=embed)

@bot.command()
async def startmc(ctx, subject_code, year):
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
    newSesh = mc.MCSession(bot, ctx, subject_code, year, session_id, pp)
    await newSesh.get_choices()

@bot.event
async def on_ready():
    print("CIEQPS online")

bot.run("OTQzMzk1MjUwNDE4OTAxMDMz.YgybSw.5i34VYUnuGpgoziaEVFYcYx9Xls")
>>>>>>> parent of cd84af2... Changed bot name
