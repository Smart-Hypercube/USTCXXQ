# coding=utf-8

import random
import requests
import os

from smart_qq_bot.config import CONFIG

# on_all_message, on_group_message, on_private_message, on_discuss_message
from smart_qq_bot.signals import on_group_message, on_private_message

REPLY_PREFIX = [
    '喵～',
    '喵呜～',
    '唔喵～',
    '喵~ ',
    '喵呜~ ',
    '唔喵~ ',
    '喵，',
    '喵呜，',
    '呜喵，',
]
REPLY_POSTFIX = [
    '～',
    '！',
    '~',
    '!',
]
REPLYS = [
    '要上墙的话，以“蔷蔷”为开头在群里发消息就好啦',
    '“上墙”可不是指对蔷蔷做奇怪的事情哦',
    '文明上墙，请不要实名挂人或者求约～',
    '蔷蔷才不是老司机呢！',
    '私聊给蔷蔷发消息也可以上墙的',
]
TEX_TEMPLATE = r"""\documentclass[12pt]{slides}
\usepackage{ctex}
\usepackage[paperheight=5in,paperwidth=5in,margin=0.25in]{geometry}
\linespread{1}
\begin{document}
%s
\end{document}
"""
LOGS = set()
PART = 2


def markov_create_table(l):
    table = {}
    for s in l:
        for i in range(len(s) - PART):
            table.setdefault(s[i:i+PART], [])
            table[s[i:i+PART]].append(s[i+PART])
        table.setdefault(s[-PART:], [])
        table[s[-PART:]].append(None)
        table.setdefault(None, [])
        table[None].append(s[:PART])
    return table


def markov_output(t, s=None):
    if s and len(s) >= PART:
        if s[-PART:] in t:
            state = s[-PART:]
            s = ''
        elif s[:PART] in t:
            state = s[:PART]
            s = state
        else:
            return ''
    else:
        state = random.choice(t[None])
        s = state
    while True:
        ns = random.choice(t[state])
        if ns is None:
            break
        s += ns
        state = state[1:] + ns
    return s


@on_private_message(name='xxq[private_post]')
def p_post(msg, bot):
    import os
    if os.path.exists('noreplyp'):
        return
    with open('test.tex', 'w') as f:
        f.write(TEX_TEMPLATE % msg.content)
    os.system('yes "" | xelatex test.tex')
    os.system('convert -density 200 test.pdf test.png')
    with open('test.png', 'rb') as f:
        requests.post('https://api.telegram.org/bot%s/sendPhoto' % CONFIG['telegram_bot_token'],
                      data={'chat_id': CONFIG['telegram_admin']}, files={'photo': f})
    return bot.reply_msg(msg, random.choice(REPLY_PREFIX) + '蔷蔷收到啦' + random.choice(REPLY_POSTFIX))


@on_group_message(name='xxq[group_post]')
def g_post(msg, bot):
    # if msg.group_code != 1549208662:
    #     return
    if msg.content.startswith('蔷蔷收到啦'):
        return
    if msg.content.startswith('蔷蔷'):
        with open('test.tex', 'w') as f:
            f.write(TEX_TEMPLATE % msg.content)
        os.system('yes "" | xelatex test.tex')
        os.system('convert -density 250 test.pdf test.png')
        with open('test.png', 'rb') as f:
            requests.post('https://api.telegram.org/bot%s/sendPhoto' % CONFIG['telegram_bot_token'],
                          data={'chat_id': CONFIG['telegram_admin']}, files={'photo': f})
        return bot.reply_msg(msg, random.choice(REPLY_PREFIX) + '蔷蔷收到啦' + random.choice(REPLY_POSTFIX))
    if '蔷蔷' in msg.content or '羞羞蔷' in msg.content:
        return bot.reply_msg(msg, random.choice(REPLY_PREFIX) + random.choice(REPLYS))
    if '馒' in msg.content or '立方体' in msg.content:
        requests.post('https://api.telegram.org/bot%s/sendMessage' % CONFIG['telegram_bot_token'],
                      data={'chat_id': CONFIG['telegram_admin'], 'text': msg.content})
    if '想' in msg.content and \
            '杀' not in msg.content and \
            '死' not in msg.content and \
            '残' not in msg.content and \
            '想就去做呀' not in msg.content and \
            '那就想想吧' not in msg.content:
        return bot.reply_msg(msg, random.choice(('想就去做呀',) + (('那就想想吧',)*(9 if '蔷' in msg.content else 1))) + random.choice(REPLY_POSTFIX))
    LOGS.add(msg.content)
    if msg.content and random.choice(range(50)) == 0:
        with open('logs.repr', encoding='utf8') as f:
            logs = eval(f.read())
        logs.update(LOGS)
        with open('logs.repr', 'w', encoding='utf8') as f:
            f.write(repr(logs))
        t = markov_create_table(logs)
        s = markov_output(t, msg.content)
        if s and s != msg.content:
            requests.post('https://api.telegram.org/bot%s/sendMessage' % CONFIG['telegram_bot_token'],
                          data={'chat_id': CONFIG['telegram_admin'], 'text': 'reply:' + msg.content + ' -- ' + s})
        return
