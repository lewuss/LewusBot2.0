import requests
import json

API_KEY = 'RGAPI-0f6e36e1-e8bc-4d41-9c5c-0f489059223a'
CHAMP_URL = 'http://ddragon.leagueoflegends.com/cdn/12.23.1/data/en_US/champion.json'
champs = requests.get(CHAMP_URL).json()
RUNES_URL = 'https://ddragon.leagueoflegends.com/cdn/12.23.1/data/en_US/runesReforged.json'
runes = requests.get(RUNES_URL).json()


def get_lp_for_chall(server):
    url = f'https://{server}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key={API_KEY}'
    chall_players = requests.get(url).json()['entries']
    chall_players = sorted(chall_players, key=lambda k: k['leaguePoints'], reverse=True)
    print(chall_players)
    return chall_players[299]['leaguePoints']


def get_lp_for_gm(server):
    url = f'https://{server}.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?api_key={API_KEY}'
    gm_players = requests.get(url).json()['entries']
    gm_players = sorted(gm_players, key=lambda k: k['leaguePoints'], reverse=True)
    return gm_players[699]['leaguePoints']


def check_if_in_game(summoner_id):
    url = f'https://euw1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{summoner_id}?api_key={API_KEY}'
    respone = requests.get(url)
    if respone.status_code == 200:
        return True
    else:
        return False


def get_players_from_live_game(channel):
    url = f"https://api.lolpros.gg/lol/game?query={channel}"
    response = requests.get(url)
    players_in_game = []
    if response.status_code == 200:
        response_json = response.json()
        for player in response_json['participants']:
            try:
                name = player['lolpros']['name']
            except:
                name = None
            champion_id = player['championId']
            champion_name = get_champ_name_from_id(champion_id)
            if name:
                players_in_game.append([name, champion_name])
    return response.status_code, players_in_game


def get_runes_ids(channel):
    url = f"https://api.lolpros.gg/lol/game?query={channel}"
    response = requests.get(url).json()
    if response.status_code == 200:
        for user in response['participants']:
            if user['lolpros'] is not None:
                if user['lolpros']['name'].lower() == channel:
                    return user['perks']
    else:
        return None


test_dict = {
    "perkIds": [
        8437,
        8446,
        8473,
        8453,
        8321,
        8304,
        5008,
        5008,
        5002
    ],
    "perkStyle": 8400,
    "perkSubStyle": 8300
}
third_tree = {
    5001: 'Health',
    5002: 'Armor',
    5003: 'MR',
    5005: 'AS',
    5007: 'CDR',
    5008: 'AD/AP'
}


def runes_ids_to_names(perks):
    rune_page = []
    for style in runes:
        if perks['perkStyle'] == style['id']:
            tree = style['slots']
        elif perks['perkSubStyle'] == style['id']:
            secondary_tree = style['slots']

    for x in range(4):
        for rune in tree[x]['runes']:
            if rune['id'] == perks['perkIds'][x]:
                rune_page.append(rune['key'])
    for x in range(4):
        for rune in secondary_tree[x]['runes']:
            if rune['id'] in perks['perkIds']:
                rune_page.append(rune['key'])
    for trd_runes in perks['perkIds'][-3:]:
        rune_page.append(third_tree[trd_runes])


def get_champ_name_from_id(champion_id):
    for champion, value in champs['data'].items():
        if int(value['key']) == champion_id:
            return value['id']


def get_accounts(player):
    url = f'https://api.lolpros.gg/es/profiles/{player.lower()}'
    response = requests.get(url)
    response_json = response.json()
    accounts = []
    for account in response_json['league_player']['accounts']:
        if account['rank']['tier'] != '90_unranked':
            accounts.append(account['summoner_name'])
    return accounts


def get_played(player):
    url = f'https://api.lolpros.gg/es/profiles/{player.lower()}'
    response = requests.get(url)
    response_json = response.json()
    wins = 0
    loses = 0
    for account in response_json['league_player']['accounts']:
        wins += account['seasons'][0]['end']['wins']
        loses += account['seasons'][0]['end']['losses']
    return wins, loses


def get_current_elo(player):
    url = f'https://api.lolpros.gg/es/profiles/{player.lower()}'
    response = requests.get(url)
    response_json = response.json()
    top_account = response_json['league_player']['accounts'][0]
    if int(top_account['rank']['tier'][0]) >= 3:
        rank = top_account['rank']['tier'][3:].capitalize() + str(top_account['rank']['rank'])
    else:
        rank = top_account['rank']['tier'][3:].capitalize()
    return f"{top_account['summoner_name']}: {rank} {top_account['rank']['league_points']}lp"


def get_czech_players(channel):
    url = f"https://api.lolpros.gg/lol/game?query={channel}"
    response = requests.get(url)
    czech = []
    if response.status_code == 200:
        response_json = response.json()
        for player in response_json['participants']:
            try:
                name = player['lolpros']['name']
                country = player['lolpros']['country']
            except:
                name = None
            champion_id = player['championId']
            champion_name = get_champ_name_from_id(champion_id)
            if name and country == 'CZ':
                czech.append([name, champion_name])
    return response.status_code, czech


def get_summoners_info(summoner_name):
    url = f'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={API_KEY}'
    response = requests.get(url)
    return response.json()


def make_info_json_file():
    players = []
    file = open('bootcampplayers.txt', 'r', encoding='utf-8')
    for line in file:
        summoner_name = line.strip()
        players.append(get_summoners_info(summoner_name))

    with open('bootcamp_info.json', 'w', encoding='utf-8') as f:
        json.dump(players, f, indent=4)


servers = {
    'EUW': "EUW1",
    "EUNE": "EUN1",
    "KR": "KR",
    "NA": "NA1",
    "TR": "TR1",
    "RU": "RU"
}


def get_summoner_id(summoner_name, server):
    url = f'https://{servers[server.upper()]}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={API_KEY}'
    return requests.get(url).json()['id']


def get_champion_id(champion):
    for name, champ in champs['data'].items():
        # print(champ['id'].lower(), name, champion)
        if champ['id'].lower() == champion:
            return champ['key']
    return champs['data'][champion.capitalize()]['key']


def get_mastery_points(id, champion, server):
    champion = champion.replace("'", "").replace(" ", "")
    try:
        champion_id = get_champion_id(champion)
    except:
        if champion.lower() == 'wukong':
            champion_id = 62
        elif champion.lower() == 'drmundo':
            champion_id = 36
    url = f'https://{servers[server.upper()]}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{id}/by-champion/{champion_id}?api_key={API_KEY}'
    return requests.get(url).json()['championPoints']


def get_all_mastery_points(summoner_name, server):
    id = get_summoner_id(summoner_name, server)
    url = f'https://{servers[server.upper()]}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{id}?api_key={API_KEY}'
    return requests.get(url).json()


def sum_mastery_from_all_account(accounts):
    champ_points = [0 for x in range(1000)]
    for acc in accounts:
        response = get_all_mastery_points(acc[0], acc[1])
        for champion in response:
            champ_points[champion['championId']] += champion['championPoints']
    return champ_points


def print_top_champs(champ_points):
    champs = {}
    for x, champ_points in enumerate(champ_points):
        name = get_champ_name_from_id(x)
        if name:
            champs[name] = champ_points
    champs = sorted(champs.items(), key=lambda x: x[1], reverse=True)
    for x in range(20):
        print(f'{x + 1}. {champs[x][0]} - {champs[x][1]}')


def rank_one(account_name):
    url = f'https://euw1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key={API_KEY}'
    response = requests.get(url).json()['entries']
    url = f'https://euw1.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?api_key={API_KEY}'
    response.extend(requests.get(url).json()['entries'])
    url = f'https://euw1.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?api_key={API_KEY}'
    response.extend(requests.get(url).json()['entries'])
    response = sorted(response, key=lambda k: k['leaguePoints'], reverse=True)
    print(response)
    rank = 0
    rank1_points = response[0]['leaguePoints']
    for player in response:
        rank += 1
        if player['summonerName'] == account_name:
            return rank, rank1_points - player['leaguePoints']
    return 999999, 0
