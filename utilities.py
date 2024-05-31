import sqlite3
from datetime import datetime
import os
import json
import inspect
import logging
logger = logging.getLogger('discord')
#-------------------------------------------------------------
# utilities.py
# This module contains miscellaneous support functions, terminal commands, init setup files.
#-------------------------------------------------------------

SQL = 'chat_history.db'#SQL data base location.
CONFIG = 'config.json'#config.json location.

#-------------------------------------------------------------
# add_admin
# This is a terminal command for adding amin user id.
#-------------------------------------------------------------
def add_admin(*userIds):
    with open(CONFIG, 'r') as f:
        data = json.load(f)

    for each in userIds:
        data['admins'].append(each)

    with open(CONFIG, 'w') as f:
        json.dump(data, f, indent = '\t', ensure_ascii=False)
    print(f'added user {userIds} as admins')
    return

#-------------------------------------------------------------
# set_openai_key
# This is a terminal command for setting openai api key
#-------------------------------------------------------------
def set_openai_key(key):
    with open(CONFIG, 'r') as f:
        data = json.load(f)

    data['openAI-api'] = key

    with open(CONFIG, 'w') as f:
        json.dump(data, f, indent = '\t', ensure_ascii=False)
    print(f'Changed key.')
    return

#-------------------------------------------------------------
# set_claude_key
# This is a terminal command for setting claude3 api key
#-------------------------------------------------------------
def set_claude_key(key):
    with open(CONFIG, 'r') as f:
        data = json.load(f)
        
    data['claude3-api'] = key

    with open(CONFIG, 'w') as f:
        json.dump(data, f, indent = '\t', ensure_ascii=False)
    print(f'Changed key.')
    return

#-------------------------------------------------------------
# set_sys_prompt
# This is a terminal command for setting system prompt for AI services
#-------------------------------------------------------------
def set_sys_prompt(prompt):
    with open(CONFIG, 'r') as f:
        data = json.load(f)

    data['systemPrompt'] = prompt

    with open(CONFIG, 'w') as f:
        json.dump(data, f, indent = '\t')
    print(f'Changed system prompt to: {prompt}', ensure_ascii=False)
    return

#-------------------------------------------------------------
# set_model
# This is a terminal command for setting AI models
#-------------------------------------------------------------
def set_model(model):
    with open(CONFIG, 'r') as f:
        data = json.load(f)

    data['model'] = model

    with open(CONFIG, 'w') as f:
        json.dump(data, f, indent = '\t', ensure_ascii=False)
    print(f'Changed model to: {model}')
    return

#-------------------------------------------------------------
# set_context_len
# This is a terminal command for setting AI context length
#-------------------------------------------------------------
def set_context_len(len):
    with open(CONFIG, 'r') as f:
        data = json.load(f)
    
    data['normalModeContextLength'] = len

    with open(CONFIG, 'w') as f:
        json.dump(data, f, indent = '\t', ensure_ascii=False)
    print(f'Changed Context Length to: {len}')
    return

#-------------------------------------------------------------
# getAPIs
# This is a support function to get api keys and discord token.
#-------------------------------------------------------------
def getAPIs():
    with open(CONFIG, 'r') as file:
        data = json.load(file)
    return {
        'openAI':data['openAI-api'],
        'claude3':data['claude3-api'],
        'token':data['discord-token'],
        'admin':data['admins']
    }

#-------------------------------------------------------------
# logRequest
# This is a support function to log.
#-------------------------------------------------------------
def logRequest(ctx, requests=''):
    stack = inspect.stack()
    caller = stack[1]
    caller_name = caller.function
    rq = f'from user {str(ctx.author.display_name)}:{str(ctx.author.id)} in channel {str(ctx.channel.id)}; func: {caller_name}; content: {requests}'
    logger.info(rq)
    return rq

#-------------------------------------------------------------
# isAdmin
# This is a support function to check if a user is admin.
#-------------------------------------------------------------
def isAdmin(userId):
    with open(CONFIG,'r') as file:
        data = json.load(file)
    return userId in data['admins']

#-------------------------------------------------------------
# checkSQL
# This is a support function to check if SQL file exists.
#-------------------------------------------------------------
def checkSQL():
    return os.path.isfile(SQL)

#-------------------------------------------------------------
# checkJson
# This is a support function to check if config file exists.
#-------------------------------------------------------------
def checkJson():
    return os.path.isfile(CONFIG)

#-------------------------------------------------------------
# save_guild_message
# This is a support function to save AI chat history.
#-------------------------------------------------------------
def save_guild_message(channel_id, guild_id, user_id, text):
    sql = sqlite3.connect(SQL)
    c = sql.cursor()
    created_at = datetime.now().isoformat()
    c.execute('INSERT INTO message (channel_id, guild_id, user_id, text, created_at) VALUES (?, ?, ?, ?, ?)',
              (channel_id, guild_id, user_id, text, created_at))
    sql.commit()
    return 1

#-------------------------------------------------------------
# get_latest_guild_messages
# This is a support function to get AI chat history.
#-------------------------------------------------------------
def get_latest_guild_messages(channel_id, guild_id, context_len):
    sql = sqlite3.connect(SQL)
    c = sql.cursor()
    query = '''
    SELECT user_id, text, created_at 
    FROM message 
    WHERE channel_id = ? AND guild_id = ? 
    ORDER BY created_at DESC
    '''
    if context_len != -1:
        query += ' LIMIT ?'
        c.execute(query, (channel_id, guild_id, context_len))
    else:
        c.execute(query, (channel_id, guild_id))

    result = c.fetchall()
    sql.close()
    return result

#-------------------------------------------------------------
# initSQL
# This is a support function to generate SQL databse.
#-------------------------------------------------------------
def initSQL():
    sql = sqlite3.connect(SQL)
    c = sql.cursor()
    c.execute('''
CREATE TABLE guild (
    id TEXT PRIMARY KEY,
    name TEXT
);''')
    c.execute('''
CREATE TABLE channel (
    id TEXT PRIMARY KEY,
    guild_id TEXT,
    name TEXT,
    FOREIGN KEY (guild_id) REFERENCES guild(id)
);''')
    c.execute(
'''CREATE TABLE message (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id TEXT,
    guild_id TEXT,
    user_id TEXT,
    text TEXT,
    created_at TEXT,
    FOREIGN KEY (channel_id) REFERENCES channel(id),
    FOREIGN KEY (guild_id) REFERENCES guild(id)
);''')
    c.execute(
'''CREATE TABLE dm_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    text TEXT,
    created_at TEXT
);''')
    return sql.close()

#-------------------------------------------------------------
# SYSTEMPROMPT
# This is default system prompt.
#-------------------------------------------------------------
SYSTEMPROMPT = '''你是一个discord bot，你的名字叫远江, 你是一个女生，说话语气可爱，你会回答用户们的问题并且和用户们聊天。
每次输入的开头中'<@numbers>'即是用户的名字id，每次回复都必须严格按照'<@numbers>'的格式提及用户。
除非用户特别说明，应以用户使用的语言回复。'''

#-------------------------------------------------------------
# initJson
# This is a support function to generate config.json file.
#-------------------------------------------------------------
def initJson(token, claude3, openai, admin):
    data = {
        'openAI-api':openai,
        'claude3-api':claude3,
        'discord-token':token,
        'systemPrompt': SYSTEMPROMPT,
        'model': 'gpt-3.5-turbo',
        'normalModeContextLength':'5',
        'threadModeContextLength':'-1',
        'admins':[admin],
        'commands': [
            {'command':'help', 'description':'```/help```\tHelp'},
            {'command':'newchat', 'description':'```/newchat```\tClear context history, start a new chat.'},
            {'command':'totomi', 'description':'```/totomi <propmt>```\tStart chat with Totomi!'},
            {'command':'imgtotomi', 'description':"```/imgtotomi <prompt> <img>```\tAsk totomi about a picture!\n\tOnly models with vision capability can use this.\n\tVISION_MODELS = ['gpt-4o', 'gpt-4-turbo', 'claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307']"},
            {'command':'dalle_totomi', 'description':'```/dalle_totomi <prompt> *<style>* *<size>* *<quality>*```\tGenerate images using DALL-E-3\n\tStars are optional parameters.\n\t<style> must be vivid/natural. default vivid.\n\t<size> must be 1024x1024, 1792x1024 or 1024x1792. default 1024x1024.\n\t<quality> must be standard/hd. default hd'},
            {'command':'usemodel', 'description':'```/usemodel <model name>```\tChange LLM model.\n\tAvailable models: gpt-3.5-turbo, gpt-4o, gpt-4-turbo, ollama, claude-3-opus, claude-3-sonnet, claude-3-haiku'},
            {'command':'set_context_length', 'description':'```/set_context_length <mode> <length>```\t\"thread\" mode or \"normal\" mode\n\tSet the context length of your chat.'},
            {'command':'check_model', 'description':'```/check_model```\tPrints current using LLM model plus all available models.'},
            {'command':'set_system_prompt', 'description':'```/set_system_prompt <prompt>```\tSet system prompt for AI chat. Prompt engineers start your magic!'},
            {'command':'play', 'description':'```/play <url>```\tPlay youtube videos.\n\tSupport playlists and song ques.'},
            {'command':'skip', 'description':'```/skip```\tSkip current song.'},
            {'command':'leave', 'description':'```/leave```\tAsk bot to leave voice channel.'}
        ]
    }
    with open(CONFIG, 'w') as file:
        json.dump(data, file, indent = '\t', ensure_ascii=False)