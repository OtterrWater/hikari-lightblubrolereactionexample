
from operator import xor
import attr
import hikari as h
from hikari.traits import RESTAware
from hikari.events.base_events import Event
from hikari.users import User
import lightbulb as lb

bot = lb.BotApp(token =
    'tokenhere',
    intents=h.Intents.ALL)

@bot.listen(h.StartedEvent)
async def on_started(event):
    print('Bot has started!')

@attr.define()
class SuccessfulAddRoleEvent(Event):
    app: RESTAware = attr.field()
    author: User = attr.field()
    content: str

@bot.command
#custom emojis will not work
@lb.option('emoji','Choose the emoji (Only default emojis allowed)')
@lb.option('role','Choose the role', type=h.Role)
@lb.option('messageid','Copy and paste the message ID')
@lb.option('channelid','Copy and paste the channel ID')
#does not work with custom emojis
@lb.command('react', 'Create reaction roles')
@lb.implements(lb.SlashCommand)
async def AddRole(ctx: h.GuildReactionAddEvent):
    emoji = ctx.options.emoji
    role = ctx.options.role
    message_link = ctx.options.messageid
    channel_link = ctx.options.channelid

    guild = ctx.member.get_guild()
    allroles = await guild.fetch_roles()

    roledict = {
        "message1":{
            "message_id":message_link,
            "emoji":emoji,
            "role_id":role,
            "allroles":allroles
        }
    }

    message = await bot.rest.fetch_message(channel_link, message_link)
    await message.add_reaction(emoji)
    await ctx.respond(f'ChannelID:{channel_link}\nMessageID:{message_link}\nEmoji:{emoji}\nRole:{role}')

    event = SuccessfulAddRoleEvent(
        app=bot, 
        author= ctx.author, 
        content= roledict
    )

    bot.dispatch(event)

@bot.listen()
#time made, unable to unionize two different event classes in listen function
async def library_search(event:SuccessfulAddRoleEvent | h.GuildReactionAddEvent):
    lib = event.content

    messageid = lib["message1"]["message_id"]
    emoji = lib["message1"]["emoji"]
    roleid = lib["message1"]['role_id']
    allroles = lib["message1"]['allroles']

    print(messageid, emoji, roleid, allroles)
    if event.is_for_emoji(emoji) in messageid:
        if roleid in allroles:
            await event.member.remove_role(role = roleid)
        else:
            await event.member.add_role(role = roleid)



bot.run()
