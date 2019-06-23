from discord.ext import commands
import dnd5e_database
import dnd5e_discord_misc
import discord

debug = lambda *args, **kwargs: False  # dummy out the debug prints when disabled
if debug():
    from trace import print as debug
    debug = debug


class party_actions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def partycreate(self, ctx, leader, *args):
        """creates a party, with the named leader as both the only member, and its leader"""
        dnd5e_database.create_party(ctx.author.mention, leader)

    @commands.command(pass_context=True)
    async def partyleave(self, ctx, character):
        """leaves the party you are a member of\nsets a new leader if the leader leaves"""
        # todo: echo 'leaving %s's party', where %s is player_id: character_name
        party = dnd5e_database.get_party_member(ctx.author.mention, character)[0]
        dnd5e_database.leave_party(party, ctx.author.mention, character)

    @commands.command(pass_context=True)
    async def partyjoin(self, ctx, player: discord.Member = None, leader=None, character=None):
        """asks to join another player's character's party"""
        general = dnd5e_discord_misc.general
        if not player:
            await ctx.send('at minimum you must specify which player has the character you would like to invite')
            return
        # discord's handling of imported commands inside a class straight up breaks calling commands in the class if
        # those classes rely on having access to the instantiated class.  Good thing they can share bot references.
        player_id = player.mention if player else ctx.author.mention
        player_name = player.display_name.split('#')[0] if player else ctx.author.name
        if not leader:
            await general.print_characters_short_form(ctx, player_name, player_id,
                                                      chars=dnd5e_database.get_player_party_leaders(player_id),
                                                      desc='What character\'s party do you want to join?')
            return
        if not character:
            await ctx.send('its rather important to indicate which of your character\'s wants to join the party...')
            return

        # is character already in a party?
        party2 = dnd5e_database.get_party_member(ctx.author.mention, character)
        if party2:
            await ctx.send('%s is already in a party, leave that one before joining another.' % character)
            return
        # if not assign to party
        party = dnd5e_database.get_party_member(player_id, leader)
        if not party:
            await ctx.send('%s doesn\'t have a party for %s to join' % (leader, character))
            return
        party_id = party[0]
        dnd5e_database.set_party(party_id, player_id, character)
        await ctx.send(character + ' forcibly joining ' + leader + '\'s party, this will be contingent on their ' +
                       'acceptance eventually')

    @commands.command(pass_context=True)
    async def partyinvite(self, ctx, leader=None, player: discord.Member = None, character=None):
        """You must be the leader, invites another player's character to the party"""
        # todo: figure out how to type check the leader type is actually the character leader, and not member
        #       short of letting the event on_command_error consume ALL exceptions and fuck up tracing, not sure what
        #       I can do here except accept that it will suffer faults, or rail in the user by not letting them type
        #       parameters, or forcing them to label the parameters.
        if not leader:
            await ctx.send('specifying which character is party leader is required to indicate which party the ' +
                           'invite is for')
            return
        if isinstance(leader, discord.Member):
            await ctx.send('You must indicate the party leader character before the target player\'s handle')
            return
        if not player:
            await ctx.send('you must specify which player has the character you would like to invite')
            return
#        player_id = await dnd5e_discord_misc.general.get_player_id_by_name(self, ctx, player_name)
        player_id = player.mention if player else ctx.author.mention
        player_name = player.display_name.split('#')[0] if player else ctx.author.name
        if not character:
            s = 'You need a character name to invite it, printing %s\'s characters now. ' % player
            s += 'Note: this list does not exclude those already in parties yet'
            await ctx.send(s)
            await dnd5e_discord_misc.general.print_characters_short_form(ctx, player_name, player_id)
            return
        party, a, b, is_leader = dnd5e_database.get_party_member(player_id, leader)
        is_leader = bool(leader)
        if not is_leader:
            ctx.send('The character offering the invite must be the party leader')
            return
        party2 = dnd5e_database.get_party_member(player_id, character)
        if party2:
            ctx.send('Target character is already in a party.')
            return
        # todo: make the invites ask the target user if they want to join
        await ctx.send('forcibly inviting ' + character + ', this will be contingent on their acceptance eventually')
        dnd5e_database.set_party(party, player_id, character)

    @commands.command(pass_context=True)
    async def partykick(self, ctx, leader=None, member=None):
        """You must be the leader, kicks another player's character from the party"""
        if not leader:
            await ctx.send('You must state which character will be kicking members from his party')
            return

        party_id, _, _, is_leader = dnd5e_database.get_party_member(ctx.author.mention, leader)
        is_leader = bool(leader)
        if not is_leader:
            ctx.send('You must be the party leader')
            return
        if member is None:
            await ctx.send('You need to state who is going to get kicked from the party')
            return

        party_members = dnd5e_database.get_players_in_party(party_id)
        target = [(x[0], x[1]) for x in party_members if x[1] == member]
        if not target:
            await ctx.send(member + ' is not in ' + leader + '\'s party')
            return
        target_id, target_name = target[0]
        dnd5e_database.leave_party(party_id, target_id, target_name)

    @commands.command(pass_context=True)
    async def party(self, ctx, player: discord.Member = None, leader=None):
        player_id = player.mention if player else ctx.author.mention
        player = player.display_name.split('#')[0] if player else ctx.author.name
        if not player_id:
            return
        if player and leader:
            party_id = dnd5e_database.get_party_member(player_id, leader)[0]
            characters = dnd5e_database.get_players_in_party(party_id)
            await dnd5e_discord_misc.general.print_characters_short_form(ctx, player, player_id, characters,
                                                                         number=True,
                                                                         title='Members of %s\'s party' % leader)
            return
        leaders = dnd5e_database.get_player_party_leaders(player_id)
        if leaders:
            await dnd5e_discord_misc.general.print_characters_short_form(ctx, player, player_id, leaders,
                                                                         title='%s\'s Party Leaders' % player)
        else:
            await ctx.send(player + ' doesn\'t have any party leaders')


def setup(bot):
    bot.add_cog(party_actions(bot))
