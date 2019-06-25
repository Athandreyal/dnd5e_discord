from discord.ext import commands
import dnd5e_database
import datetime
import discord
import dnd5e_encounter
from dnd5e_character_sheet import CharacterSheet
import json

# intended for discord actions relating to encounters

debug = lambda *args, **kwargs: False  # dummy out the debug prints when disabled
if debug():
    from trace import print as debug
    debug = debug

# will have to bring over a very highly customised version of encounter, or mod the current one to conditionally
# import discord - if it doesn't already - and conditionally throw await ctx or regular terminal io accordingly.

new_encounters = dict()


class encounter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # party leader needs to choose to pick a fight or adventure
    # periodically pit creatures against each other in public battles - GAMBLING!

    @commands.command(pass_context=True, hidden=True)
    async def edit_test(self, ctx):
        """a quick message editing test command"""
        now = datetime.datetime.now()
        end = now + datetime.timedelta(seconds=10)
        msg = await ctx.send(now)
        while now < end:
            now = datetime.datetime.now()
            await msg.edit(content=now)

    @commands.command(pass_context=True, hidden=True)
    async def endless(self, ctx):
        channel = ctx.channel
        author = ctx.author
        mention = ctx.author.mention
        pred = lambda m: m.author == author and m.channel == channel
        await ctx.send('this is an unending test loop which will hopefully echo whatever the caller\'s messages are')
        while True:
            msg = await self.bot.wait_for('message', check=pred)
            debug(msg)
            await ctx.send(mention + ' ' + msg.content)

    @commands.command(pass_context=True)
    async def encounter(self, ctx, player1_mention: discord.Member = None, leader1=None,
                               player2_mention: discord.Member = None, leader2=None):
        if ctx.author.id not in [350417514540302336]:
            await ctx.send("*I'm sorry Dave, I can't let you do that...*\nthis command will clutter chat pretty badly" +
                           "until it's actually ready with in place editing, reactions for controls, etc, it will be " +
                           "kept isolated - .....coming soon.....think valve-time.")
            return

        if None in (player1_mention, leader1):
            await ctx.send('a player and leader among that player\'s characters are required')
            return
        player1_id = player1_mention.mention if player1_mention else ctx.author.mention
        player1_name = player1_mention.display_name.split('#')[0] if player1_mention else ctx.author.name

        # =============================
        # get party 1, form it from leader if not in a party
        party1_member = dnd5e_database.get_party_member(player1_id, leader1)
        debug(party1_member)
        if not party1_member:
            await ctx.send(f'{leader1} is not in a party, forming a party of one')
            dnd5e_database.create_party(player1_id, leader1)
            party1_member = dnd5e_database.get_party_member(player1_id, leader1)
            party1_id = party1_member[0]
            party1_chars = dnd5e_database.get_players_in_party(party1_id)
        else:
            if party1_member[-1] == "False":
                await ctx.send(f'{leader1} is not the leader of this party, they cannot pick fights.')
                return
            party1_id = party1_member[0]
            party1_chars = dnd5e_database.get_players_in_party(party1_id)

        # =============================
        # get party 2, form it from leader if not in a party, form it form NPC if no leader given
        player2_id = player2_mention.mention if player2_mention else None
        player2_name = player2_mention.display_name.split('#')[0] if player2_mention else None
        if None in (player2_mention, leader2):
            await ctx.send('creating hostile party from NPCs to battle')
            party2_chars = None
        else:
            party2_member = dnd5e_database.get_party_member(player2_id, leader2)
            if not party2_member:
                await ctx.send(f'{leader2} is not in a party, forming a party of one')
                dnd5e_database.create_party(player2_id, leader2)
                party2_member = dnd5e_database.get_party_member(player2_id, leader2)
                party2_id = party2_member[0]
                party2_chars = dnd5e_database.get_players_in_party(party2_id)
            else:
                party2_id = party2_member[0]
                party2_chars = dnd5e_database.get_players_in_party(party2_id)

        # =============================
        # instantiate the entities in preparation for battle
        # todo: mark certain players as auto by testing their status?
        p1 = []
        debug(p1)
        for char in party1_chars:
            debug(char)
            char = dnd5e_database.database_char_tuple_to_dict(char)
            debug(char)
            p1.append(CharacterSheet.from_dict(char))
        p2 = []
        debug(p2)
        if party2_chars:
            for char in party2_chars:
                debug(char)
                p2.append(CharacterSheet.from_dict(char))

        # =============================
        # instantiate the party objects
        party1 = dnd5e_encounter.Party(*p1)
        party2 = dnd5e_encounter.Party(*p2) if p2 else dnd5e_encounter.Encounter.generate_party2(party1)

        difficulty = 'Normal'
        e = dnd5e_encounter.Encounter(party1=party1, difficulty=difficulty, verbose=True)
        await e.do_battle(ctx=ctx, bot=self.bot)
        for character in party1.members:
            dnd5e_database.set_player(character.to_dict())

    #    @commands.command(pass_context=True)
    async def combat_print(self, ctx, encounter, w1=None, w2=None, w3=None, w4=None):
        party1 = encounter.party1
        party2 = encounter.party2
        embed_party1 = discord.Embed(title='Party 1')
        embed_party2 = discord.Embed(title='Party 2')
        embed_action = discord.Embed(title='Action')
        embed_dialogue = discord.Embed(title='Dialogue')
        hostile_window = await ctx.send(embed=embed_party2)
        friendly_window = await ctx.send(embed=embed_party1)
        hostile_window = await ctx.send(embed=embed_action)
        hostile_window = await ctx.send(embed=embed_dialogue)


def setup(bot):
    bot.add_cog(encounter(bot))
