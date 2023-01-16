import discord
from discord.ext import commands
from discord import app_commands

TOKEN = "your_token"
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


@bot.tree.command(name="g", description="Calls a game with the given amount of slots.")
@app_commands.describe(game="The game you want to call",
                       slot="The number of slots you want to call")
async def g(interaction: discord.Interaction, game: str, slot: int):
    if slot < 1:
        await interaction.response.send_message(f"Hey {interaction.user.mention}, are you serious?")
        return
    elif slot > 20:
        await interaction.response.send_message(f"Sorry {interaction.user.mention}, the maximum value for ***slot*** is only 20.")
        return
    elif len(game) > 100:
        await interaction.response.send_message(f"Sorry {interaction.user.mention}, the maximum length for ***game*** is only 100.")
        return

    embed = discord.Embed(title=game,
                          description=f"{interaction.user.mention} is now calling for **{game}** with **{str(slot)}** slots!\n\n"
                                      f"Click on {tick_emoji} to join the game.")
    embed.add_field(name=f"Joined Players (0/{str(slot)}):", value="", inline=True)
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    await msg.add_reaction(tick_emoji)


@bot.event
async def on_reaction_add(reaction, user):
    message: discord.Message = reaction.message
    embed = message.embeds[0]
    if "Joined Players" in embed.fields[0].name and not user.bot and reaction.emoji == tick_emoji:
        caller = embed.description.split(' is')[0]
        if caller == user.mention:
            await message.channel.send(f"Sorry {user.mention}, you can't join your own game.")
            await message.remove_reaction(tick_emoji, user)
            return
        slots = int(embed.fields[0].name.split('/')[1][0])
        players = embed.fields[0].value
        if players == '':
            players = []
        else:
            players = embed.fields[0].value.split(' ')
        if len(players) != slots:
            embed.clear_fields()
            players.append(user.mention)
            name = f"Joined Players ({len(players)}/{str(slots)})"
            value = ' '.join(players)
            embed.add_field(name=name, value=value)

            if len(players) == slots:
                lines = embed.description.split('\n\n')
                lines[1] = f"The game is now full. {cross_emoji}"
                embed.description = '\n\n'.join(lines)
            await message.edit(embed=embed)
        else:
            await message.remove_reaction(tick_emoji, user)
            await message.channel.send(f"Sorry {user.mention}, the game is already full.")


@bot.event
async def on_reaction_remove(reaction, user):
    message = reaction.message
    embed = message.embeds[0]
    if "Joined Players" in embed.fields[0].name and not user.bot and reaction.emoji == tick_emoji:
        caller = embed.description.split(' is')[0]
        if caller == user.mention:
            return

        slots = int(embed.fields[0].name.split('/')[1][0])
        players = embed.fields[0].value.split(' ')

        embed.clear_fields()
        players.remove(user.mention)
        name = f"Joined Players ({len(players)}/{str(slots)})"
        value = ' '.join(players)
        embed.add_field(name=name, value=value)

        lines = embed.description.split('\n\n')
        lines[1] = f"Click on {tick_emoji} to join the game."
        embed.description = '\n\n'.join(lines)

        await message.edit(embed=embed)


bot.run(TOKEN)
