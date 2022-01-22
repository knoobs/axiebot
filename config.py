# -*- coding: utf-8 -*-
"""
Created on Fri Jan 21 12:19:24 2022

@author: kneub
"""

class URL:
    AXIE_STATS = "https://api.axie.technology/getaxies/"
    PVP_LOG = "https://game-api.axie.technology/logs/pvp/"
    LEADERBOARD = "https://game-api.axie.technology/toprank?offset=#&limit=#"
    RONIN = "https://explorer.roninchain.com/api/tokentxs?addr=#&token=#&size=#"
    GRAPHQL = "https://graphql-gateway.axieinfinity.com/graphql"
    
class USER_AGENTS:
    DEFAULT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    
class WALLETS:
    SHORTCUT = {
            'bruh' : 'ronin:b5bbaee57faee6b5fa32e23b42409f13ab06e96b',
            'saw'  : 'ronin:511f4a85fc82ad411b574d978ad29c25efb3fdcf',
            'even' : 'ronin:dfeb5fd5c103856803616373cc3399da474b3b68'
            }
    
class PAYLOADS:
    GET_AXIE_BRIEF_LIST = {
      "operationName": "GetAxieBriefList",
      "variables": {
        "from": 0,
        "size": 24,
        "sort": "PriceAsc",
        "auctionType": "Sale",
        "criteria": {}
      },
      "query": "query GetAxieBriefList($auctionType: AuctionType, $criteria: AxieSearchCriteria, $from: Int, $sort: SortBy, $size: Int, $owner: String) {\n  axies(auctionType: $auctionType, criteria: $criteria, from: $from, sort: $sort, size: $size, owner: $owner) {\n    total\n    results {\n      ...AxieBrief\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment AxieBrief on Axie {\n  id\n  name\n  stage\n  class\n  breedCount\n  image\n  title\n  battleInfo {\n    banned\n    __typename\n  }\n  auction {\n    currentPrice\n    currentPriceUSD\n    __typename\n  }\n  parts {\n    id\n    name\n    class\n    type\n    specialGenes\n    __typename\n  }\n  __typename\n}\n"
    }