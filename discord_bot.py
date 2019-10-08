import discord
import json
import sql_handler
import sheets_interface
import emoji
from datetime import datetime

version = "0.8.10.19 A"

config = json.load(open("config.json"))

# channel IDs
reg_channel = 406292711646167045
dev_channel = 385506783919079425
com_channel = 520680784949018639

# role constants
# TODO get actual message id
role_message = 0000000
# TODO replace keys with emojis
roles_dic =   { ':flag_jp:':                    487415117361971200, #need to ask Atom about each reaction
                ':pick:':                       570307869279518720,
                ':large_blue_diamond:':         554029029905137676,
                ':vs:':                         487415401085403157,
                ':feet:':                       488887610882916352,
                ':flower_playing_cards:':       448741569650714216,
                ':trophy:':                     619372177757831168,
                ':game_die:':                   626161640768798730,
                'MMO':                          619372523754094602,
                'table_top':                    619371680992591882,
                'video games':                  487415401131540490,
                'dnd':                          487415117420429312,

                # used by !... commands to get role id
                'guest':                        406508496314564608,
                'student':                      403701567305285633}

# Strings
not_reg_msg     = "You are not registered {}. Please finish the google form in the pinned message."
reg_msg         = "Welcome {}!"

# takes a text and logs into file with timestamp
def write_log(text: str):
    text = str(datetime.now()) + " - " + text + "\n"
    f = open("GEEK.log", "a+")
    f.write(text)
    f.close()
    pass

#bot client
client = discord.Client() # type: discord.Client()

# on ready function - logs ready time
@client.event
async def on_ready():
    print("TheGeek is ready.")
    write_log("Ready.")
    pass

@client.event
async def on_message(message: discord.Message):
    '''
    Called when a user sends a message in a chat the bot can access, server channels, DMs, etc.
    Used to react to messages asking for registration.
    '''
    if message.channel.id == dev_channel:
        pass
    # Used for registering users
    elif message.channel.id == reg_channel:
        '''
        handles commands on register channel
        '''
        # attempts to register user
        if "!register" in message.conents:
            register(message) 
        # gives them guest tag, maybe ask approval from mods using reactions
        elif "!guest" in message.contents:
            message.author.add_roles(message.guild.get_role(roles_dic['guest']))
    pass


# add role depending on reaction to message
@client.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    '''
    Only does something when users react to a specific message
    Removes user role depending on reaction only if they are registered/students
    '''
    if payload.message_id == role_message:
        # gets text form of emoji
        # if it a unicode emoji uses `emoji` library to get text form
        # else discord provides the name
        if(payload.emoji.is_unicode_emoji()):
            emoji_name = emoji.demojize(payload.emoji.name)
        else:
            emoji_name = payload.emoji.name
        guild = client.get_guild(payload.guild_id)  # type: discord.Guild
        member = guild.get_member(payload.user_id) # type: discord.Member
        channel = client.get_channel(payload.channel_id) # type: discord.TextChannel
        role = guild.get_role(roles_dic[emoji_name]) # type: discord.Role
        # remove member role
        member.remove_role(role)
        # print message and delete after 3 seconds
        await channel.send("Removed {} tag. {}.".format(role.name, member.mention))
        pass
    pass

@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    '''
    Only does something when users react to a specific message
    Gives user role depending on reaction only if they are registered/students
    '''
    if payload.message_id == role_message:
        # gets text form of emoji
        # if it a unicode emoji uses `emoji` library to get text form
        # else discord provides the name
        if(payload.emoji.is_unicode_emoji()):
            emoji_name = emoji.demojize(payload.emoji.name)
        else:
            emoji_name = payload.emoji.name
        guild = client.get_guild(payload.guild_id)  # type: discord.Guild
        member = guild.get_member(payload.user_id) # type: discord.Member
        channel = client.get_channel(payload.channel_id) # type: discord.TextChannel
        role = guild.get_role(roles_dic[emoji_name]) # type: discord.Role
        # add member role
        member.add_role(role)
        # print message and delete after 3 seconds
        await channel.send("Added {} tag. {}.".format(role.name, member.mention))
        pass
    pass


async def register(message: discord.Message):
    '''
    Gives user Student tag if they have registered on google form
    '''
    # log action start
    write_log(format("Registering {} ...", message.author.name))    
    # check if user registered
    if (is_registered(message.author.name, message.author.discriminator)):
        role = message.guild.get_role(roles_dic['student']) # type: discord.Role
        message.author.add_role(role) # add role
        write_log(format("Successfully registered {} !", message.author.name)) # log result
        message.channel.send(content=reg_msg.format(message.author.mention)).delete(delay=3) # notify user success and delete notify message after 3 seconds
        message.delete(delay=0.5) # delete user message
    else:
        write_log(format("Failed to register {}!", message.author.name)) # log result (failure)
        message.channel.send(content=not_reg_msg.format(message.author.mention)).delete(delay=3) # notify user of failure then delete notify message
        message.delete(delay=0.5) # delete user message
    pass

client.run(config['token'])
