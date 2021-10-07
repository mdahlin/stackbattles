import discord

from secrets import API_KEY, TOKEN
from cards import CardManager

man = CardManager(player = 'Kabib Nurmagabob')
def getCardsString(man):

    ret = man.getCards(5)
    
    ret.sort(key=lambda x: x[0], reverse=True)
    string = ''

    for card in ret:
        string += '{0} - {4} | **{1}** - {2}'.format(*card[1])
        string += '\n'

    return string
#... discord.py not being maintained in the future
# any more and will likely break in the a future discord update
client = discord.Client()

@client.event
async def on_ready():
    print('Working')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$cards'):
        await message.channel.send(getCardsString(man))

client.run(TOKEN)
