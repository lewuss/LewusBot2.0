from twitchio.ext import commands
from TwitchStuff import *
import random
import pymongo
import lolapi
import spotifyapi as spotify
import spotifykeys

znani_users = []

with open('znaniusers.txt', 'r') as file:
    for line in file:
        znani_users.append(line.strip().lower())

lol_accounts = {}

with open('lolaccounts.txt', "r") as file:
    for line in file:
        key, value = line.strip().split(";")
        lol_accounts[key] = value

client = pymongo.MongoClient(
    f"mongodb+srv://twitchdata:{mongo_pw}@cluster0.qtyar.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.twitch.chatters
db_vips = client.twitch.vips


class Bot(commands.Bot):
    bannable = []
    sr = {}
    file = open("banned_words.txt", "r", encoding='UTF-8')
    for data in file:
        bannable.append(data.strip())

    def __init__(self):
        super().__init__(token=oauth, prefix='$', initial_channels=['lewus', 'waxjan', 'sinmivak', 'vvarion', 'kasix'])

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')

    async def event_message(self, message):
        if message.echo:
            return
        print(message.content)
        await self.handle_commands(message)

    async def send_msg(self, msg, ctx):
        if any(ban_words in msg.lower().replace(" ", "") for ban_words in self.bannable):
            print('trigerred')
            await ctx.send(f"{ctx.message.author.name} - Bardzo nieładne słowo w wiadomości Sadeg")
        else:
            await ctx.send(msg)

    @commands.command()
    async def vanish(self, ctx: commands.Context):
        ban_user(ctx.author.name, ctx.channel.name, 'vanish', 1)

    @commands.command()
    @commands.cooldown(5, 60, commands.Bucket.channel)
    async def ruletka(self, ctx: commands.Context):
        if ctx.author.is_mod:
            await ctx.send("Masz moda nie da się w ciebie strzelic :tf:")
        else:
            chance = random.randint(1, 2)
            if chance == 1:
                duration = random.randint(60, 10800)
                ban_user(ctx.author.name, ctx.channel.name, 'ruletka', duration)
                await ctx.send(f'{ctx.author.name} umarł na {duration / 60} minut Sadeg')
            else:
                await ctx.send(f'{ctx.author.name} żyjesz')

    @commands.command()
    @commands.cooldown(5, 60, commands.Bucket.channel)
    async def follow(self, ctx: commands.Context):
        kto = ctx.message.content.split()[1]
        kogo = ctx.message.content.split()[2]
        await ctx.send(check_if_x_follows_y(kto, kogo))

    @commands.command(name='help', aliases=['commands', 'komendy', 'pomoc', 'info'])
    @commands.cooldown(5, 60, commands.Bucket.channel)
    async def help(self, ctx: commands.Context):
        await ctx.send("Wszystkie komendy dostępne tutaj https://lewus.netlify.app/ lewusHey ")

    @commands.command(name='chatters', aliases=['viewers'])
    @commands.cooldown(1, 60, commands.Bucket.channel)
    async def chatters(self, ctx: commands.Context):
        viewers_num = get_viewers(ctx.channel.name)
        chatters_num = get_chatters_num(ctx.channel.name)
        await ctx.send(f'{ctx.channel.name.capitalize()}: {viewers_num} widzów, {chatters_num} chattersów')

    @commands.command()
    @commands.cooldown(1, 15, commands.Bucket.channel)
    async def kto(self, ctx: commands.Context):
        try:
            channel = ctx.message.content.split()[1]
        except:
            channel = ctx.channel.name
        chatters = get_all_chatters(channel)
        print(chatters)
        if chatters:
            in_chat = list(set(chatters) & set(znani_users))
            print(in_chat)
            await ctx.send(f"lewusClap {', '.join(in_chat)} oglada stream {channel}")
        else:
            await ctx.send(
                f'Niestety Twitch ograniczył sprawdzanie wszystkich chattersow, a na tym streamie ani lewusbot ani lewus nie ma moda.')

    @commands.command(name="vips", aliases=['vip'])
    @commands.cooldown(1, 60, commands.Bucket.user)
    async def vip(self, ctx: commands.Context):
        try:
            user = ctx.message.content.split()[1].lower()
        except:
            user = ctx.author.name
        result = db_vips.find({'vips': user})
        message = ''
        num_of_channels = 0
        for res in result:
            if res['login'].capitalize() not in message:
                message += f'{res["login"].capitalize()}, '
                num_of_channels += 1
        if message == '':
            await ctx.send(f'Sadeg {user} nie ma nigdzie vipa Sadge (stara baza)')
        elif len(message) < 400:
            await ctx.send(f'PogU {user} ma vipa na tych kanałach: {message[:-2]}.')
        else:
            await ctx.send(f'PogO {user} ma tyle vipów {num_of_channels}. '
                           f'Jest ich tyle, że na da się ich wypisać GG Sadge')

    @commands.command(name="livegame", aliases=['gra', 'game'])
    @commands.cooldown(1, 10, commands.Bucket.channel)
    async def livegame(self, ctx: commands.Context):
        try:
            user_name = ctx.message.content.split()[1]
        except:
            user_name = lol_accounts[ctx.channel.name]
        code, players = lolapi.get_players_from_live_game(user_name)
        if code == 200:
            message = ''
            for player in players:
                message += f'{player[0]}({player[1]}), '
            await self.send_msg(f'W grze {message[:-2]}.', ctx)
        elif code == 204:
            await self.send_msg(f'Sadge {user_name} nie jest aktualnie w grze.', ctx)
        elif code == 406:
            await self.send_msg(f'Taki gracz nie istnieje.', ctx)
        elif code == 402:
            await self.send_msg(f'Lewus nie zapłacił Porvalo', ctx)

    @commands.command(name="elo", aliases=['rank', 'lp'])
    @commands.cooldown(1, 10, commands.Bucket.channel)
    async def elo(self, ctx: commands.Context):
        try:
            user_name = ctx.message.content.split()[1]
        except:
            user_name = lol_accounts[ctx.channel.name]
        message = lolapi.get_current_elo(user_name)
        await self.send_msg(f'Elo użytkownika {user_name} - konto {message}', ctx)

    @commands.command(name="opgg")
    @commands.cooldown(1, 10, commands.Bucket.channel)
    async def opgg(self, ctx: commands.Context):
        try:
            user_name = ctx.message.content.split()[1]
        except:
            user_name = lol_accounts[ctx.channel.name]
        accounts = lolapi.get_accounts(user_name)
        if len(accounts) == 1:
            link = f'https://euw.op.gg/summoner/userName={accounts[0]}'
        else:
            link = "https://euw.op.gg/multi/query="
            for account in accounts:
                link += account.replace(" ", "") + '%2C%20'
        await self.send_msg(f"OPGG gracza {user_name} {link}", ctx)

    @commands.command(name="pkt", aliases=['mastery', 'maestria', 'punkty'])
    @commands.cooldown(1, 3, commands.Bucket.channel)
    async def pkt(self, ctx: commands.Context):
        args = ctx.message.content.split()
        accounts = []
        pkt_maestry = 0
        champion = args[1].lower()
        if len(args) == 2:
            user = lol_accounts[ctx.channel.name]
            accounts = lolapi.get_accounts(user)
            print(accounts)
            server = 'euw'
        else:
            user = ''.join(args[2:])
            print(user)
            accounts = lolapi.get_accounts(user)
            server = 'euw'

        for account in accounts:
            id = lolapi.get_summoner_id(account, server)
            pkt_maestry += lolapi.get_mastery_points(id, champion, server)
        if user == 'lewus':
            id = lolapi.get_summoner_id('medusakongo2008', 'eune')
            pkt_maestry += lolapi.get_mastery_points(id, champion, 'eune')
        pkt_maestry = "{:,}".format(pkt_maestry)
        return await self.send_msg(f'Gracz {user} ma {pkt_maestry} punktów mastery na {champion.capitalize()}.', ctx)

    @commands.command()
    @commands.cooldown(1, 5, commands.Bucket.channel)
    async def play(self, ctx: commands.Context):
        if ctx.author.is_mod:
            spotify.play(ctx.channel.name)

    @commands.command()
    @commands.cooldown(1, 5, commands.Bucket.channel)
    async def pause(self, ctx: commands.Context):
        if ctx.author.is_mod:
            spotify.pause(ctx.channel.name)

    @commands.command()
    @commands.cooldown(1, 5, commands.Bucket.channel)
    async def skip(self, ctx: commands.Context):
        if ctx.author.is_mod:
            spotify.skip(ctx.channel.name)

    @commands.command()
    @commands.cooldown(1, 5, commands.Bucket.channel)
    async def volume(self, ctx: commands.Context):
        if ctx.author.is_mod:
            words = ctx.message.content.split()
            try:
                level = words[1]
                if level[0] == '+':
                    level = int(level[1:]) + int(spotify.get_current_volume(ctx.channel.name))
                elif level[0] == '-':
                    level = int(spotify.get_current_volume(ctx.channel.name)) - int(level[1:])
                level = int(level)
                if level < 1:
                    level = 1
                elif level > 100:
                    level = 100
                spotify.change_volume(level, ctx.channel.name)
                await ctx.send(f'Spotify Volume changed to {level}')
            except Exception as e:
                print(e)
                await ctx.send(f'Current Volume - {spotify.get_current_volume()}.')

    @commands.command(name='song', aliases=['piosenka'])
    @commands.cooldown(1, 5, commands.Bucket.channel)
    async def song(self, ctx: commands.Context):
        if spotify.get_current_playback_state(ctx.channel.name):
            track = spotify.get_current_track_name(ctx.channel.name)
            await self.send_msg(f'Aktualnie leci {track}', ctx)
        else:
            await ctx.send('Aktualnie nic nie leci.')

    @commands.command(name="sr", aliases=["songrequest"])
    @commands.cooldown(1, 2, commands.Bucket.user)
    async def song_request(self, ctx: commands.Context):
        if ctx.author.name == ctx.channel.name or ctx.author.name == "lewus":
            words = ctx.message.content.split()
            if words[1] == 'on':
                self.sr[ctx.channel.name] = True
                await ctx.send('Song Request spotifyowy włączony')
            elif words[1] == 'off':
                self.sr[ctx.channel.name] = False
                await ctx.send('Song Request spotifyowy wyłączony')

    @commands.command(name="add_to_que", aliases=['add'])
    @commands.cooldown(1, 5, commands.Bucket.user)
    async def add_to_que(self, ctx: commands.Context):
        if self.sr[ctx.channel.name]:
            artist, title, track_id = spotify.find_song(ctx.message.content[4:], ctx.channel.name)
            if any(x in f'{title} {artist}'.lower().split() for x in self.bannable):
                await ctx.send("lewusMrozon NIE WYSYŁAJ TAKICH PIOSENEK RASISTO lewusMrozon")
            else:
                spotify.add_to_que(artist, title, track_id, ctx.channel.name)
                await self.send_msg(f"@{ctx.author.name} {artist} - {title} zostało dodane do kolejki", ctx)


bot = Bot()
bot.run()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.
