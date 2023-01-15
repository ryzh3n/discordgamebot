import discord
from discord.ext import commands
from discord import app_commands

TOKEN = "your_token_here"
bot = commands.Bot(command_prefix="-", intents=discord.Intents.all())
tick_emoji = u"\u2705"
cross_emoji = u"\u274c"


@bot.event
async def on_ready():
    print("Bot is Up and Ready!")
    await bot.change_presence(activity=discord.Game("NoxCraft by RyZh3n"))
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


@bot.tree.command(name="g", description="Calls a game with the given number of slots.")
@app_commands.describe(game="The game you want to call",
                       slot="The number of slots you want to call")
async def g(interaction: discord.Interaction, game: str, slot: int):
    if slot < 2:
        await interaction.response.send_message("Please call the game with at least 2 slots.")
        return
    description = f"{interaction.user.mention} is now calling for **{game}** with **{str(slot)}** slots left! \n\n" \
                  f"Click on the {tick_emoji} to join the game. \n\n" \
                  f"Players joined (**0**):"
    embed = discord.Embed(title="GGGGGGGG!",
                          description=description)
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    await msg.add_reaction(tick_emoji)


@bot.event
async def on_reaction_add(reaction, user):
    message: discord.Message = reaction.message
    if message.embeds[0].title == "GGGGGGGG!" and not user.bot and reaction.emoji == tick_emoji:
        embed = message.embeds[0]
        lines = embed.description.split('\n\n')

        slots_left = int(lines[0].split('with')[1].split('**')[1])
        if slots_left < 1:
            await message.remove_reaction(tick_emoji, user)
            lines[1] = f"The Game is now Full {cross_emoji}"
            embed.description = '\n\n'.join(lines)
            await message.edit(embed=embed)
            await message.channel.send(f"Sorry {user.mention}, the game is already full.")
            return
        caller = lines[0].split(' is')[0]
        if caller == user.mention:
            await message.remove_reaction(tick_emoji, user)
            await message.channel.send(f"Sorry {user.mention}, you can't join your own game!")
            return

        game = lines[0].split('**')[1]
        lines[0] = f'{caller} is now calling for **{game}** with **{slots_left - 1}** slots left!'

        line2 = lines[1].split('**')
        line2[1] = f'**{str(int(line2[1])+1)}**'
        line2.append(f' {user.mention}')
        line2 = ''.join(line2)
        lines[2] = line2

        embed.description = '\n\n'.join(lines)
        await message.edit(embed=embed)


@bot.event
async def on_reaction_remove(reaction, user):
    message = reaction.message
    if message.embeds[0].title == "GGGGGGGG!" and not user.bot and reaction.emoji == tick_emoji:
        embed = message.embeds[0]
        lines = embed.description.split('\n\n')

        slots_left = int(lines[0].split('with')[1].split('**')[1])
        if slots_left > 0:
            lines[1] = f'Click on the {tick_emoji} to join the game.'
        caller = lines[0].split(' is')[0]
        game = lines[0].split('**')[1]

        players = lines[1].split(': ')
        if len(players) > 1:
            players = players[1].split(' ')
            if user.mention in players:
                players.remove(user.mention)
                lines[0] = f'{caller} is now calling for **{game}** with **{slots_left + 1}** slots left!'
                lines[2] = f"Players joined (**{str(len(players))}**): {' '.join(players)}"
        else:
            lines[2] = f"Players joined (**0**): "

        embed.description = '\n\n'.join(lines)
        await message.edit(embed=embed)


bot.run(TOKEN)
