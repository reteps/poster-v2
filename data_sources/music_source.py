import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import dateparser
import json
import math
import re
import collections
import os
import copy

# data should just be json
'''
title:
artist:
label:
songs:
    name
    length
release date

album_number
'''
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="bbcde58d680d405b943a4098e0dbaa72",
                                                           client_secret="5d5395d4ec2d472e97ab3b585670400a"))

def select_album(query, album):
    possible_matches = sp.search(q=query, type='album')['albums']['items']
    if album != None:
        return possible_matches[album-1]['id']
    for i, m in enumerate(possible_matches):
        name = m['name']
        artist = m['artists'][0]['name']
        num_song = m['total_tracks']
        release_date = m['release_date']
        print(f'{i+1:2d}|{artist:30s}|{num_song:2d}|{name:10s}')
    while True:
        try:
            if len(possible_matches) == 1:
                return possible_matches[0]['id']
            n = int(input('CORRECT ALBUM NUM > '))
            if n < 1 or n > len(possible_matches):
                raise ValueError('nooo')
            return possible_matches[n-1]['id']
        except Exception:
            pass
def album_details(id):
    album = sp.album(id)
    album_songs = sp.album_tracks(id)['items']
    artist = album['artists'][0]

    data = {
        'title': album['name'],
        'artist': artist['name'],
        'release_date': album['release_date'],
        'songs': [{'name': song['name'], 'time': math.floor(song['duration_ms'] / 1000)} for song in album_songs],
        'label': album['label']
    }
    return data

def display_overview(d):
    song_table = ''
    for i, song in enumerate(d['songs']):
        m,s = divmod(song['time'], 60)
        song_table += f'{i+1:2d} | {m:02d}:{s:02d} | {song["name"]}\n'
    os.system('clear')
    print(f'''
{song_table.rstrip()}

{d['title']}
{d['artist']}
{d['label']} {d['release_date']}
''')

def string_mod(s, song=False, secondary_option=None, song_list=False):
    strip_paren = lambda x: re.sub(r'\(.+\)', '', x).strip()
    strip_brace = lambda x: re.sub(r'\[.+\]', '', x).strip()
    strip_dash = lambda x: x.split('-')[0].split('–')[0].split('—')[0].strip()
    funcs = collections.OrderedDict([
        ('Strip All', lambda x: strip_paren(strip_brace(strip_dash(x)))),
        ('Strip Dash', strip_dash),
        ('Strip Paren', strip_paren),
        ('Strip Brace', strip_brace)
    ])
    if song:
        funcs['Delete'] = lambda x: None
    if song_list:
        funcs['Append New Song'] = 'INSERT'
        funcs['Filter Songs'] = 'FILTER'
    else:
        funcs['Overwrite'] = lambda x: input('NEW > ')
    
    if secondary_option == None:
        for i, key in enumerate(funcs):
            print(f'({i}) {key}')
        secondary_option = int(input('>> '))
    func = list(funcs.values())[secondary_option]

    if song_list:
        if isinstance(func, str):
            if func == 'INSERT':
                s.append({'name': input('NAME > '), 'time': int(input('LENGTH > '))})
            elif func == 'FILTER':
                minimum_time = int(input('MINIMUM TIME > '))
                s = list(filter(lambda song: song['time'] > minimum_time, s))
        else:
            for song in s:
                song['name'] = func(song['name'])
    else:
        s = func(s)
    
    return s
def ultimate_modifier(data=None):
    if data == None:
        return 'FIRST_LOAD'
    display_overview(data)
    keys = ['title', 'artist', 'release_date', 'label']

    print('0. Multiple Songs')
    print('1 N. Single Song')
    for i, k in enumerate(keys):
        print(f'{i+2}. {k}', end=' ')
    
    option = input('\n> ')
    if option == '':
        return data
    elif option == 'reset':
        return 'RESET'
    elif option == 'select':
        return 'SELECT'
    elif option.startswith('1'):
        n = int(option.split(' ')[1])
        res = string_mod(data['songs'][n-1]['name'], song=True)
        if res == None:
            del data['songs'][n-1]
        else:
            data['songs'][n-1]['name'] = res

    secondary_option = None
    if ' ' in option:
        parts = option.split(' ')[:2]
        option = int(parts[0])
        secondary_option = int(parts[1])
    else:
        option = int(option)
    
    if option == 0:
        data['songs'] = string_mod(data['songs'], secondary_option=secondary_option, song_list=True)
    elif option >= 2:
        selected_key = keys[option-2]
        data[selected_key] = string_mod(data[selected_key], secondary_option=secondary_option)
    return 'CONTINUE'
def retrieve_spotify_data(query, album):
    original_data = album_details(select_album(query, album))
    data = None
    while True:
        status = ultimate_modifier(data)
        if status == 'FIRST_LOAD':
            data = copy.deepcopy(original_data)
        elif status == 'RESET':
            data = copy.deepcopy(original_data)
        elif status == 'CONTINUE':
            pass
        elif status == 'SELECT':
            original_data = album_details(select_album(input('ALBUM > '), None))
        else:
            return data