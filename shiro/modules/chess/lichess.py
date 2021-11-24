import lightbulb
import requests
import flag
import hikari


@lightbulb.command("lichess", "All lichess commands")
@lightbulb.implements(lightbulb.commands.SlashCommandGroup)
async def lichess() -> None:
    """All lichess commands"""


@lichess.child
@lightbulb.option("username", "The username of the profile to look up", str)
@lightbulb.command("profile", "Return information about a profile")
@lightbulb.implements(lightbulb.commands.SlashSubCommand)
async def profile(ctx: lightbulb.context.Context) -> None:
    """Returns information about a Lichess profile

    Args:
        ctx (lightbulb.context.Context): The command's invocation context
    """
    data = requests.get(f"https://lichess.org/api/user/{ctx.options.username}").json()

    try:
        try:
            disabled = data["disabled"]
            await ctx.respond("This account is closed")

        except:
            print(data)
            if(data['online']):
                statemoji = "<:status_online:902261836781613096>" + " (Online)"

            else:
                statemoji = "<:status_offline:902261836794200074>"+ " (Offline)"

            try:
                country = data['profile']['country']
                print(country)
                flag1 = flag.flag(country)
            except:
                flag1 = "<:lichessorg:902423802498121729>"

            count = data["count"]
            blitzrating = str(data['perfs']['blitz']['rating'])
            bulletrating = str(data['perfs']['bullet']['rating'])
            rapidrating = str(data['perfs']['rapid']['rating'])
            classicalrating = str(data['perfs']['classical']['rating'])

            try:
                if(data['perfs']['blitz']['prov'] == True):
                    blitzrating += '?'
            except:
                blitzrating += ''
            try:
                if(data['perfs']['rapid']['prov'] == True):
                    rapidrating += '?'
            except:
                rapidrating += ''
            try:
                if(data['perfs']['bullet']['prov'] == True):
                    bulletrating += '?'
            except:
                bulletrating += ''
            try:
                if(data['perfs']['classical']['prov'] == True):
                    classicalrating += '?'
            except:
                    classicalrating += ''

            Games = ''
            Games = str(count["all"]) +' (' + str(count["win"]) + ' Wins - ' + str(count["draw"]) + ' Draws - ' + str(count["loss"]) + ' Losses)'
            URL = f'https://lichess.org/@{data.get("username")}'
            Description = ''
            try:
                profile = data.get('profile')
                Description = Description + str(profile['bio'])
            except:
                Description += "This user's biography is empty"

            

            embed = (
                hikari.Embed(
                    title=data['username'], 
                    url = URL, 
                    description=''
                )
                .set_thumbnail('https://imgur.com/r3eEAy3.png')
                .add_field(name=  'Status:' , value= statemoji , inline= False)
                .add_field(name="Games", value=Games, inline=False)
                .add_field(name="Bio: ", value=Description, inline=False)
                .add_field(name="Country: ", value=flag1, inline=False)
                
                .add_field(name= '<:blitz:902261836899037234>' +'Blitz ['  + str(data['perfs']['blitz']['games']) + ']', value=blitzrating , inline =True)

                .add_field(name = '<:rapid:902261836789993532>' +'Rapid [' + str(data['perfs']['rapid']['games']) + ']', value = rapidrating , inline=True )

                .add_field(name= '<:classical:902428900020338728>' + 'Classical [' + str(data['perfs']['classical']['games']) + ']', value = classicalrating, inline= True )

                .add_field(name='<:bullet:902261836752240640>' + 'Bullet [' + str(data['perfs']['bullet']['games']) + ']', value=bulletrating , inline= True)      
            )
            
            await ctx.respond(embed)
    except:
         await ctx.respond("Invalid Username")     

    # await ctx.respond(data.__repr__())


def _load(bot: lightbulb.BotApp) -> None:
    bot.command(lichess)
