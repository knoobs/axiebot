# -*- coding: utf-8 -*-
"""
Created on Fri Jan 21 13:51:39 2022

@author: kneub
"""

import nest_asyncio
nest_asyncio.apply()

import os
from axie_helper import compile_data, get_sheet, embed_axie_tx
from config import WALLETS

import discord
from dotenv import load_dotenv

from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN2')


intents = discord.Intents().all()
bot = commands.Bot(command_prefix='+', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingPermissions):
        await ctx.send("Hey there bucko... you don't have permission for that!")
    
@bot.command(name='excel',
             description='Generate excel sheet with data from specified ranks.',
             brief=' - `+excel 1-30` returns ranks 1-30')
async def get_excel(ctx, rank_bound):
    try:
        start = int(rank_bound.split('-')[0])
        end = int(rank_bound.split('-')[1])
        data = compile_data(start, end)
        get_sheet(data, 'axie')
        await ctx.send(file=discord.File('axie.xlsx'))
    except:
        await ctx.send("Improper command use. Use format: `+excel 1-30`")
        
@bot.command(name='axies',
             description='Return axie transactions',
             brief=' - `+axies <address>` returns axie transactions')
async def get_axie_tx(ctx, addr):
    try:
        if addr in WALLETS.SHORTCUT:
            addr = WALLETS.SHORTCUT[addr]
        if ':' in addr:
            addr = '0x'+addr.split(':')[1]
        embed = embed_axie_tx(addr)
        await ctx.send(embed=embed)
    except:
        await ctx.send("Improper command use. Use format: `+axies <address>`")      
        
bot.run(TOKEN)