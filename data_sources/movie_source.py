from imdb import IMDb
import json
from types import MappingProxyType
import dateparser
'''
title:
release date:
rating:
runtime:
director:
writer:
categories:
plot:
'''
import readline

def input_with_prefill(prompt, text):
    def hook():
        readline.insert_text(text)
        readline.redisplay()
    readline.set_pre_input_hook(hook)
    result = input(prompt)
    readline.set_pre_input_hook()
    return result

def serialize(o):
    blacklist = []
    x = {'k':'v'}
    if type(o) == type(MappingProxyType(x)):
        return None
    print(type(o))
    return o.__dict__
def select_plot(plots,num=None):
    tmp = plots[1]
    plots[1] = plots[0]
    plots[0] = tmp
    plots = [p.split('::')[0] for p in plots]
    if num != None:
        return plots[num-1]
    
    for i, plot in enumerate(plots[:8]):
        print(i+1)
        print(plot)
    
    n = input('SELECT PLOT NUMBER > ')
    if '+' in n:
        n = n.replace('+','')
        t=plots[int(n)-1]
        return input_with_prefill('',t)
    return plots[int(n)-1]
def retrieve_movie_details(q, plot=None):
    imdb = IMDb()
    movieid = list(filter(lambda x: x['kind'] != 'episode', imdb.search_movie(q)))[0].movieID
    movie_details = imdb.get_movie(movieid)
    # print(json.dumps(movie_details,indent=2, default=serialize))
    
    print(movie_details['title']+'\n')
    rated = list(filter(lambda x: 'United States' in x and 'ABC' not in x and 'TV' not in x and 'MA' not in x, movie_details['certificates']))
    director_key = 'directors'
    writers_key = 'writers'
    if movie_details['kind'] == 'tv series':
        print('This is a TV Show')
        director_key = 'creator'
        writers_key = 'writer'
        released = movie_details['series years']
        rated = ['']
        time_text = str(movie_details['seasons']) + ' season'
        if movie_details['seasons'] > 1:
            time_text += 's'        
    else:
        released = dateparser.parse(movie_details.get('original air date').split('(')[0].strip(), date_formats=['%d %b %Y']).strftime('%B %-d %Y')
        h,m = divmod(int(movie_details['runtimes'][0]), 60)
        if m == 0:
            time_text = f'{h}h'
        else:
            time_text = f'{h}h {m}min'

        if movie_details['kind'] == 'tv mini series':
            director_key = 'director'
            writers_key = 'writer'
            rated = ['']
    data = {
        'title': movie_details['title'],
        'released': released,
        'year': str(movie_details['year']),
        'runtime': time_text,
        'director': movie_details[director_key][0]['name'],
        'writers': list(set(list(filter(lambda x:x != None, [w.get('name') for w in movie_details[writers_key]]))))[:4],
        'genres': movie_details['genres'][:3],
        'plot': select_plot(movie_details['plot'],num=plot),
        'id': movieid,
        'cast': [x['name'] for x in movie_details['cast'][:5]],
        'rated': rated[0].replace('United States:','').lower(),
    }
    return data
