import requests

BASE_URL = 'https://api.twitch.tv/helix/'
authURL = 'https://id.twitch.tv/oauth2/token'

keys = open("newkeys2.txt", 'r')

CLIENT_ID = keys.readline().strip()
token = keys.readline().strip()
oauth = keys.readline().strip()
scope_token_lewusbot = keys.readline().strip()
scope_token_lewus = keys.readline().strip()
mongo_pw = keys.readline().strip()

INDENT = 2

AutParams = {'client_id': CLIENT_ID,
             'client_secret': token,
             'grant_type': 'client_credentials'
             }

AUTCALL = requests.post(url=authURL, params=AutParams)
ACCESS_TOKEN = AUTCALL.json()['access_token']
HEADERS = {'Client-ID': CLIENT_ID, 'Authorization': "Bearer " + ACCESS_TOKEN}


def get_user_id(user_login):
    url = f'{BASE_URL}users?login={user_login}'
    response_json = requests.get(url, headers=HEADERS).json()
    return response_json['data'][0]['id']


def _get_headers():
    headers = {
        "Content-Type": "application/json",
        "client-id": "q6batx0epp608isickayubi39itsckt",
        "Authorization": "Bearer " + "9cinol4datoyenmjk8b8vzjfwo5emy",
    }
    return headers


def ban_user(name, channel, reason, duration):
    name_id = get_user_id(name)
    channel_id = get_user_id(channel)
    ban = requests.post(
        url=f"https://api.twitch.tv/helix/moderation/bans?broadcaster_id={channel_id}&moderator_id=711014068",
        headers=_get_headers(),
        json={"data": {"user_id": name_id, "duration": duration, "reason": reason}})
    print(ban)


def check_if_x_follows_y(kto, kogo):
    kto_id = get_user_id(kto)
    kogo_id = get_user_id(kogo)
    url = f'{BASE_URL}users/follows?from_id={kto_id}&to_id={kogo_id}'
    response_json = requests.get(url, headers=HEADERS).json()
    if response_json['data']:
        return f"{kto} followuje {kogo} od {response_json['data'][0]['followed_at'][0:10]}"
    else:
        return f'{kto} nie followuje {kogo}'


def get_viewers(channel):
    url = f'{BASE_URL}streams?user_login={channel}'
    response = requests.get(url, headers=HEADERS)
    return response.json()['data'][0]['viewer_count']


def get_chatters_num(channel):
    channel_id = get_user_id(channel)
    url = f'{BASE_URL}chat/chatters?broadcaster_id={channel_id}&moderator_id=711014068'
    response = requests.get(url, headers={'Client-ID': CLIENT_ID, 'Authorization': "Bearer " + scope_token_lewusbot})
    return response.json()['total']


def get_all_chatters(channel):
    channel_id = get_user_id(channel)
    url = f'{BASE_URL}chat/chatters?broadcaster_id={channel_id}&moderator_id=711014068'
    response = requests.get(url, headers={'Client-ID': CLIENT_ID, 'Authorization': "Bearer " + scope_token_lewusbot})
    if response.status_code == 200:
        return go_through_all_users(url, response, scope_token_lewusbot)
    url = f'{BASE_URL}chat/chatters?broadcaster_id={channel_id}&moderator_id=27187817'
    response = requests.get(url,
                            headers={'Client-ID': CLIENT_ID, 'Authorization': "Bearer " + scope_token_lewus})
    if response.status_code == 200:
        return go_through_all_users(url, response, scope_token_lewus)

    return None


def go_through_all_users(url, response, token):
    response_json = response.json()
    users = response_json['data']
    while response_json['pagination']:
        print(response_json)
        users.extend(response_json['data'])
        cursor = response_json['pagination']['cursor']
        url = f'{url}&after={cursor}'
        response = requests.get(url,
                                headers={'Client-ID': CLIENT_ID, 'Authorization': "Bearer " + token})
        response_json = response.json()
    return sorted([entry['user_name'].lower() for entry in users])
