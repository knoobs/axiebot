# -*- coding: utf-8 -*-
"""
Created on Fri Jan 21 12:08:49 2022

@author: kneub
"""

import requests
import json
from config import URL, USER_AGENTS, PAYLOADS
from scipy import stats
import xlwt
from datetime import datetime
import discord


def read_page(url):
    # Read api
    
    headers = {
        'Accept': '*/*',
        'User-Agent': USER_AGENTS.DEFAULT
        }
    payload = {}
    
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code != 200:
        raise Exception(response.status_code)
        
    return response.json()
        
def get_axie_stats(*argv):
    # Return axie stats for variable axie id arguments
    
    url_base = URL.AXIE_STATS
    url = url_base + ','.join(argv)
    
    data = read_page(url)
    return data

def get_leaderboard(start=1, end=10):
    # return leaderboard data for range or ranks
    
    offset = start-1
    limit = end-offset
    url_base = URL.LEADERBOARD
    url = url_base.replace('#',str(offset),1).replace('#',str(limit),1)
                           
    data = read_page(url)
    return data

def get_pvp_log(addr):
    # Return pvp log for a player based on address
    
    url_base = URL.PVP_LOG
    url = url_base + addr
    
    data = read_page(url)
    return data

def compile_data(start=1, end=10):
    # Get pertinment info for leaderboard axies
    
    data = {}
    leader_data = get_leaderboard(start, end)
    for val in leader_data['items']:
        print(f"Gathering data for rank {val['rank']}...")
        addr = val['client_id']
        data.update({ val['rank'] : { 'name' : val['name'], 'addr' : addr }})
        
        # Get pvp log
        pvp_data = get_pvp_log(addr)
        try:
            wins = [i for i in pvp_data['battles'] if i['winner'] == addr]
            if len(wins) < 1:
                continue
        except:
            continue
        teams = [i['first_team_fighters'] for i in wins]
        most_win_team = stats.mode(teams)[0][0]
        
        # Get axie data
        axie_data = get_axie_stats(str(most_win_team[0]),str(most_win_team[1]),str(most_win_team[2]))
        similar_sales = get_price_similar(str(most_win_team[0]),str(most_win_team[1]),str(most_win_team[2]))
        for i, axie in enumerate(axie_data):
            axie.update({ 'for_sale' : similar_sales[i] })  
        data[val['rank']].update({ 'team' : axie_data })
            
    return data

def get_sheet(data, filename):
    
    # Create sheet
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("Player Axies")
    row, col = 1, 0
    
    titles = ['Rank/Name/Address',
                  'Axie 1','Similar ID','Price',' ',
                  'Axie 2','Similar ID','Price',' ',
                  'Axie 3','Similar ID','Price',' ']
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    style.font = font
    
    # Place data
    for rank, p_data in data.items():
        try:
            rank = str(rank)
            name = p_data['name']
            addr = p_data['addr']
            axies = p_data['team']
        except:
            continue
        
        # Place titles
        for header in titles:
            sheet.write(row-1, col, header, style=style)
            col+=1
        col = 0
           
        # Place data
        sheet.write(row, col, rank)
        sheet.write(row+1, col, name)
        sheet.write(row+2, col, addr)
        for i, axie in enumerate(axies):
            shift = 4*int(i)+1
            sheet.write(row, col+shift, axie['class'])
            sheet.write(row+1, col+shift, axie['parts'][3]['name'])
            sheet.write(row+2, col+shift, axie['parts'][4]['name'])
            sheet.write(row+3, col+shift, axie['parts'][2]['name'])
            sheet.write(row+4, col+shift, axie['parts'][5]['name'])
            stats = f"{axie['stats']['hp']}/{axie['stats']['speed']}/{axie['stats']['skill']}/{axie['stats']['morale']}"
            sheet.write(row+5, col+shift, stats)
            sheet.write(row+6, col+shift, axie['figure']['image'])
            
            try:
                for j in range(7):
                    price_weth = int(axie['for_sale'][j]['auction']['currentPrice'])/(1E18)
                    price_usd  = float(axie['for_sale'][j]['auction']['currentPriceUSD'])
                    axie_id = axie['for_sale'][j]['id']
                    sheet.write(row+j, col+shift+2,
                                f"{str(round(price_weth,3))} | ${str(round(price_usd,2))}")
                    sheet.write(row+j, col+shift+1, axie_id)
            except:
                continue
            
        row+=9
        
    workbook.save(filename.split('.')[0]+'.xlsx')
        
    return

def get_axie_tx(addr, size=100):
    # Get axie transaction info
    
    url_base = URL.RONIN
    
    # Get purchased/sold axies
    url = url_base.replace('#',addr,1).replace('#','ERC721',1).replace('#',str(size),1)                  
    data = read_page(url)
    if data['total'] > size:
        print("WARNING: May be skipping some transactions")
    a_data = data['results']
    tx_data = {}
    for tx in a_data:
        if tx['token_symbol'] != 'AXIE':
            print("This tx is not an axie!")
            continue
        
        axie_id = tx['value']
        if axie_id not in tx_data:
            tx_data.update({ axie_id : [] })
        
        data = {}
        if tx['from'] == addr:
            data.update({ 'type' : 'Sold' })
        elif tx['to'] == addr:
            data.update({ 'type' : 'Bought' })
        else:
            print("This tx has no associated buyer/seller?")
            continue
        data.update({ 'tx_hash' : tx['tx_hash'] })
        data.update({ 'time' : datetime.utcfromtimestamp(tx['timestamp'])})
        
        tx_data[axie_id].append(data)
        
    # Get purchase cost
    url = url_base.replace('#',addr,1).replace('#','ERC20',1).replace('#',str(size),1)
    data = read_page(url)
    if data['total'] > size:
        print("WARNING: May be skipping some transactions")
    e_data = data['results']
    
    # for axie tx in data
    for axie_data in tx_data.values():
        for axie_tx in axie_data:
            tx_hash = axie_tx['tx_hash']
        
            # for each eth tx
            value = 0
            for e_tx in e_data:
                if e_tx['tx_hash'] == tx_hash:
                    value += int(e_tx['value'])/(1E18)
            axie_tx.update({ 'weth' : value })
                
    return tx_data

def embed_axie_tx(addr):
    # Create embed for axie transactions for discord bot
    
    # Get axie tx data
    data = get_axie_tx(addr)
    profit = axie_profit(addr)
    
    # Create embed
    embed = discord.Embed(title="Recent Transactions",
                          description=f"***Realized Gains: {profit} WETH***",
                          colour=0x87CEEB, timestamp=datetime.utcnow())
    
    for axie in data:
        axie_id = f"AxieID: {axie}"
        desc = ""
        for tx in data[axie]:
            desc+=f"**{tx['type']}:**\t{round(tx['weth'],3)} WETH\t-- *{str(tx['time'])}*\n"
                    
        embed.add_field(name=axie_id, value=desc, inline=False)
    
    return embed

def axie_profit(addr):
    # Create graph of profits
    
    # Get axie tx data
    data = get_axie_tx(addr)
    
    profit = 0
    for axie in data:
        for tx in data[axie]:
            if len(data[axie]) >= 2 and (len(data[axie])%2)==0:
                if tx['type'].lower() == 'bought':
                    profit -= tx['weth']
                if tx['type'].lower() == 'sold':
                    profit += tx['weth']
                    
    return round(profit,3)

def querify_payload(payload):
    
    with open('test.json','w') as f:
        json.dump(payload, f)
    
    with open('test.json','r') as f:
        payload = f.readlines()[0]
        
    return payload

def ping_graphql(payload):
    
    headers = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    }

    payload = querify_payload(payload)
    response = requests.request("POST", URL.GRAPHQL, data=payload, headers=headers)
    data = json.loads(response.text)
    
    return data
    
def get_price_similar(*argv):
    # Get price of axies with same parts/type as id
    
    data = get_axie_stats(*argv)
    if not isinstance(data, list):
        data = [data]
        
    # Get search criteria
    return_data = []
    for axie in data:
        parts = []
        for part in axie["parts"]:
            if part["type"].lower() in ['mouth','eyes','back','horn']:
                parts.append(part['id'])
        criteria = {
            "classes" : [axie["class"]],
            "parts" : parts
            }
        
        # Get payload
        payload = PAYLOADS.GET_AXIE_BRIEF_LIST
        payload["variables"]["criteria"] = criteria
        
        return_data.append(ping_graphql(payload)['data']['axies']['results'])
    
    return return_data    
    

if __name__ == '__main__':
    #data_axie = get_axie_stats("1234")
    #data_leader = get_leaderboard(1,5)
    #data_pvp = get_pvp_log('0x379f949790224820f969d92003e1f714ba02cee1')
    data = compile_data(1,5)
    print('goose snacks')
    get_sheet(data, 'axies')
    #data = get_axie_tx('0xb5bbaee57faee6b5fa32e23b42409f13ab06e96b')
    #embed_axie_tx('0xb5bbaee57faee6b5fa32e23b42409f13ab06e96b')
    #data = get_price_similar('123')
    