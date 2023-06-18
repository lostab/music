# -*- coding: utf-8 -*-

import bottle
import os
import random
import json

root_dir = os.path.dirname(os.path.realpath(__file__))
 
@bottle.route('/')
def main():
  return bottle.static_file('app.html', root=root_dir)

@bottle.route('/favicon.ico')
def icon():
  return bottle.static_file('music.ico', root=root_dir)

@bottle.route('/m/:m#.*#')
def music(m):
    q = bottle.request.query.q.strip()
    musics = []
    for music in os.listdir(root_dir + '/music'):
        if music.endswith('.mp3'):
            if not q or q in music:
                musics.append(music)
    if musics:
        random_id = random.randint(0, len(musics) - 1)
        random_music = musics[random_id]
        if not m:
            result = {
                'id': random_id,
                'music': random_music.rstrip('.mp3')
            }
            return json.dumps(result, ensure_ascii=False)
        else:
            if len(m.split('?')) > 1:
                m = m.split('?')[0]
            music_id  = int(m)
            if music_id < len(musics):
                music = musics[music_id]
                return bottle.static_file(music, root=root_dir + '/music')
            else:
                return None
    else:
        return None

bottle.run(host='0.0.0.0', port=8787, reloader=True)
