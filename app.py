# -*- coding: utf-8 -*-

import bottle
import os
import random

root_dir = os.path.dirname(os.path.realpath(__file__))
 
@bottle.route('/')
def main():
  return bottle.static_file('app.html', root=root_dir)

@bottle.route('/m/:m#.*#')
def music(m):
    musics = []
    for music in os.listdir(root_dir + '/music'):
        if music.endswith('.mp3'):
            musics.append(music)
    random_music = musics[random.randint(0, len(musics) - 1)]
    if not m:
        print(random_music)
        return bottle.static_file(random_music, root=root_dir + '/music')
    else:
        searchs = m.split(' ')
        results = []
        for music in musics:
            fit = True
            for search in searchs:
                if search in music and music not in results:
                    results.append(music)
                else:
                    fit = False
            if fit:
                return bottle.static_file(music, root=root_dir + '/music')
        if results:
            return bottle.static_file(results[0], root=root_dir + '/music')
        else:
            return bottle.static_file(random_music, root=root_dir + '/music')

bottle.run(host='127.0.0.1', port=8787, reloader = True)
