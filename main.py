from discord_components.interaction import Interaction
import discord
import sqlite3
from discord_components import DiscordComponents, Button, ButtonStyle, Interaction


token = ''

client = discord.Client()

DiscordComponents(client)

def serching_guild(id : int):
    con = sqlite3.connect('main.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM guilds WHERE id == ?;', (id,))
    info = cur.fetchone()
    con.close()
    if info is None:
        return False
    else:
        return info

@client.event
async def on_message(msg):
    if msg.author.bot:
        return

    if msg.content == '!등록':
        if msg.guild.owner_id == msg.author.id:
            if not serching_guild(msg.guild.id):
                con = sqlite3.connect('main.db')
                cur = con.cursor()
                cur.execute('INSERT INTO guilds VALUES(?, ?, ?);', (msg.guild.id, msg.guild.owner_id, 1))
                con.commit()
                con.close()
                await msg.channel.send('등록되었습니다.\n인증서버를 생성하신 후 !연동 [서버아이디]로 연동해주세요.')

            else:
                await msg.channel.send('이미 등록되어있는 서버입니다.')
        else:
            await msg.channel.send('당신은 서버 소유주가 아닙니다.')

    if msg.content.startswith('!연동 '):
        try:
            parent = msg.content[4:]
            print(parent)
            if not parent.isdigit():
                raise TypeError
        except:
            return await msg.channel.send('연동할 부모 서버 아이디를 입력해주세요.')
        
        result = serching_guild(parent)

        if result:
            if result[1] == msg.author.id:
                con = sqlite3.connect('main.db')
                cur = con.cursor()
                cur.execute('INSERT INTO guilds VALUES(?, ?, ?);', (msg.guild.id, msg.guild.owner_id, parent))
                con.commit()
                con.close()
                return await msg.channel.send('연동이 완료되었습니다.')
            else:
                return await msg.channel.send('부모 서버의 소유주 아이디와 본인의 아이디가 같아야합니다.')
        else:
            return await msg.channel.send('연동할 부모 서버를 찾지 못했습니다.')

    if msg.content == '!생성':
        if msg.guild.owner_id == msg.author.id:
            await msg.channel.send(content='아래 버튼을 눌러 본 서버에 입장하세요.', components=[[Button(label='인증', id='verify', style=ButtonStyle.blue)]])

@client.event
async def on_button_click(interaction: Interaction):
    if interaction.user.bot:
        return

    if interaction.component.custom_id == 'verify':
        result = serching_guild(interaction.guild_id)

        if result:
            try:
                guild = client.get_guild(int(result[2]))
                for i in list(guild.channels):
                    try:
                        
                        invitelink = await i.create_invite(max_uses=1, max_age=60)
                        break
                    except:
                        pass
                await interaction.respond(content=f'초대링크가 생성되었습니다.\n60초 내에 접속하지 않을시 초대링크가 만료됩니다.\n{invitelink}')
            except Exception as e:
                print(e)
                await interaction.respond(content='초대링크 생성에 실패했습니다.')
        else:
            return


client.run(token)