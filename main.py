import discord
from discord.ext import commands
import requests

RIOT_API_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

DISCORD_TOKEN = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def pegar_info_jogador(nick_completo, servidor):
    if '#' in nick_completo:
        nome, tagline = nick_completo.split('#')
    else:
        return None
    
    servidor_api = {
        'br': 'br1',
        'euw': 'euw1',
        'na': 'na1',
        'lan': 'la1',
    }

    if servidor not in servidor_api:
        return None

    platform = servidor_api[servidor]
    headers = {"X-Riot-Token": RIOT_API_KEY}

    url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{nome}/{tagline}"
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print(f"Erro ao buscar Riot ID: {r.status_code} - {r.text}")
        return None

    account_data = r.json()
    print(f"Dados da conta (account_data): {account_data}")  # Diagnóstico

    if 'puuid' not in account_data:
        print(f"Erro: 'puuid' não encontrado na resposta. Resposta da API: {account_data}")
        return None

    puuid = account_data["puuid"]

    url_summoner = f"https://{platform}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    r2 = requests.get(url_summoner, headers=headers)

    if r2.status_code != 200:
        print(f"Erro ao buscar dados do invocador: {r2.status_code} - {r2.text}")
        return None

    summoner_data = r2.json()
    print(f"Dados do invocador (summoner_data): {summoner_data}")  # Diagnóstico

    summoner_name = summoner_data.get("name", "Nome não encontrado")
    summoner_id = summoner_data["id"]
    profile_icon_id = summoner_data.get("profileIconId", 0)

    icon_url = f"http://ddragon.leagueoflegends.com/cdn/latest/img/profileicon/{profile_icon_id}.png"

    url_rank = f"https://{platform}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
    r_rank = requests.get(url_rank, headers=headers)
    rank_data = r_rank.json()
    print(f"Dados do rank (rank_data): {rank_data}")  # Diagnóstico

    if rank_data:
        rank = rank_data[0].get("tier", "Unranked") + " " + rank_data[0].get("rank", "")
        wins = rank_data[0].get("wins", 0)
        losses = rank_data[0].get("losses", 0)
        total_games = wins + losses
        winrate = round((wins / total_games) * 100, 2) if total_games > 0 else 0
    else:
        rank = "Unranked"
        wins = 0
        losses = 0
        total_games = 0
        winrate = 0

    return {
        "nick": summoner_name,
        "icon_url": icon_url,
        "rank": rank,
        "total_games": total_games,
        "winrate": winrate
    }

@bot.command()
async def perfil(ctx, nick_completo: str, servidor: str):
    info = pegar_info_jogador(nick_completo, servidor)
    
    if info:
        embed = discord.Embed(title="Perfil do Jogador", color=discord.Color.blue())
        embed.set_thumbnail(url=info['icon_url'])
        embed.add_field(name="Nickname", value=info['nick'], inline=False)
        embed.add_field(name="Rank", value=info['rank'], inline=True)
        embed.add_field(name="Jogos", value=f"{info['total_games']} | Winrate: {info['winrate']}%", inline=True)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send("Não consegui encontrar o perfil. Verifique o nick ou a região.")

@bot.event
async def on_ready():
    print(f"Bot {bot.user} está online!")


bot.run(DISCORD_TOKEN)
