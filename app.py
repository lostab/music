# -*- coding: utf-8 -*-

import bottle
import os
import random
import json
import requests
import hashlib
import urllib.parse
from waitress import serve

root_dir = os.path.dirname(os.path.realpath(__file__))
 
@bottle.route('/')
def main():
  return bottle.static_file('app.html', root=root_dir)

@bottle.route('/favicon.ico')
def icon():
  return bottle.static_file('music.ico', root=root_dir)

@bottle.route('/m/:m#.*#', method=['GET', 'POST'])
def music(m):
    q = urllib.parse.unquote(bottle.request.query.q.strip().lower())
    s = bottle.request.query.s.strip().lower()
    t = bottle.request.query.t.strip()
    p = bottle.request.forms.p.strip()
    recent = bottle.request.forms.recent
    if recent:
        try:
            recent = json.loads(recent)
        except Exception as e:
            with open(root_dir + '/error.log', 'a+') as f:
                f.write(recent + '\n')
                f.write(str(e) + '\n')
            recent = [p]
    else:
        recent = [p]
    likes = []
    for like in os.listdir(root_dir + '/like'):
        likes.append(like)
    loves = []
    for love in os.listdir(root_dir + '/love'):
        loves.append(love)
    musics = []
    for music in os.listdir(root_dir + '/music'):
        if music.endswith('.mp3'):
            if t == 'like' and likes:
                if (not q and music in likes) or (q and (q in music.lower() or q in music.lower().replace(' - ', '-', 1) or q.replace(' - ', '-', 1) in music.lower() or q.replace(' - ', '-', 1) in music.lower().replace(' - ', '-', 1))):
                    musics.append(music)
            elif t == 'love' and loves:
                if (not q and music in loves) or (q and (q in music.lower() or q in music.lower().replace(' - ', '-', 1) or q.replace(' - ', '-', 1) in music.lower() or q.replace(' - ', '-', 1) in music.lower().replace(' - ', '-', 1))):
                    musics.append(music)
            else:
                if not q or (q and s != 'true' and (q in music.lower() or q in music.lower().replace(' - ', '-', 1) or q.replace(' - ', '-', 1) in music.lower() or q.replace(' - ', '-', 1) in music.lower().replace(' - ', '-', 1))) or (q and s == 'true' and (q == music[:-4].lower() or q == music[:-4].lower().replace(' - ', '-', 1) or q.replace(' - ', '-', 1) == music[:-4].lower() or q.replace(' - ', '-', 1) == music[:-4].lower().replace(' - ', '-', 1))):
                    musics.append(music)
    if musics:
        if not m:
            random_id = random.randint(0, len(musics) - 1)
            random_music = musics[random_id]
            #while len(musics) > 1 and random_music[:-4] == p:
            while len(musics) > len(recent) and random_music[:-4] in recent:
                random_id = random.randint(0, len(musics) - 1)
                random_music = musics[random_id]
            result = {
                'id': random_id,
                'music': random_music[:-4],
                'like': 'like' if (random_music in likes) else 'unlike',
                'love': 'love' if (random_music in loves) else 'unlove'
            }
            return json.dumps(result, ensure_ascii=False)
        else:
            if len(m.split('?')) > 1:
                m = m.split('?')[0]
            if m == 'r':
                music_id = random.randint(0, len(musics) - 1)
            else:
                music_id  = int(m)
            if music_id < len(musics):
                music = musics[music_id]
                return bottle.static_file(music, root=root_dir + '/music')
            else:
                return json.dumps({}, ensure_ascii=False)
    else:
        return json.dumps({}, ensure_ascii=False)

def auth(p):
    try:
        with open(root_dir + '/password.ini', 'r') as f:
            password = hashlib.md5(f.read().strip().encode()).hexdigest()
            if p == password:
                return True
            else:
                return False
    except Exception as e:
        return False

@bottle.route('/like', method=['GET', 'POST'])
def like():
    m = bottle.request.query.m.strip()
    n = bottle.request.query.n.strip()
    p = bottle.request.query.p.strip()
    if not auth(p):
        result = {
            'stat': 0
        }
    else:
        if len(root_dir + '/music/' + m + '.mp3') > 128:
            result = {
                'stat': 2
            }
        else:
            if n == 'like' and not os.path.exists(root_dir + '/like/' + m + '.mp3'):
                os.symlink(root_dir + '/music/' + m + '.mp3', root_dir + '/like/' + m + '.mp3')
            if n == 'unlike' and os.path.exists(root_dir + '/like/' + m + '.mp3'):
                os.unlink(root_dir + '/like/' + m + '.mp3')
                if os.path.exists(root_dir + '/love/' + m + '.mp3'):
                    os.unlink(root_dir + '/love/' + m + '.mp3')
            result = {
                'stat': 1
            }
    return json.dumps(result, ensure_ascii=False)

@bottle.route('/love', method=['GET', 'POST'])
def love():
    m = bottle.request.query.m.strip()
    n = bottle.request.query.n.strip()
    p = bottle.request.query.p.strip()
    if not auth(p):
        result = {
            'stat': 0
        }
    else:
        if len(root_dir + '/music/' + m + '.mp3') > 128:
            result = {
                'stat': 2
            }
        else:
            if n == 'love':
                if not os.path.exists(root_dir + '/love/' + m + '.mp3'):
                    os.symlink(root_dir + '/music/' + m + '.mp3', root_dir + '/love/' + m + '.mp3')
                if not os.path.exists(root_dir + '/like/' + m + '.mp3'):
                    os.symlink(root_dir + '/music/' + m + '.mp3', root_dir + '/like/' + m + '.mp3')
            if n == 'unlove' and os.path.exists(root_dir + '/love/' + m + '.mp3'):
                os.unlink(root_dir + '/love/' + m + '.mp3')
            result = {
                'stat': 1
            }
    return json.dumps(result, ensure_ascii=False)

def getbgimg():
    try:
        url = 'https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN'
        r = requests.get(url).json()
        return 'https://cn.bing.com' + r['images'][0]['url']
    except:
        return ''

def geticimg(w):
    w = w + ' 封面'
    url = "https://image.baidu.com/search/acjson"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Referer': 'https://image.baidu.com/'
    }
    params = {
        'tn': 'resultjson_com', 'logid': ' xxxxxxxxxxxxxxxxxxx', 'ipn': 'rj', 'ct': 'xxxxxxxxx', 'is': '', 'fp': 'result', 'queryWord': w, 'cl': '2', 'lm': '-1', 'ie': 'utf-8', 'oe': 'utf-8', 'adpicid': '', 'st': '', 'z': '', 'ic': '', 'hd': '', 'latest': '', 'copyright': '', 'word': w, 's': '', 'se': '', 'tab': '', 'width': '', 'height': '', 'face': '', 'istype': '', 'qc': '', 'nc': '1', 'fr': '', 'expermode': '', 'force': '', 'cg': 'star', 'pn': '0', 'rn': '1', 'gsm': '1e'
    }
    image_urls = []
    try:
        response = requests.get(url, headers=headers, params=params)
        response_json = json.loads(response.text, strict=False)
        for data in response_json["data"]:
            if "thumbURL" in data:
                image_urls.append(data["thumbURL"])
    except:
        pass
    if len(image_urls) > 0:
        return image_urls[0]
    else:
        return ''

@bottle.route('/i')
def img():
    w = urllib.parse.unquote(bottle.request.query.w.strip())
    result = {
        'bgimg': getbgimg(),
        'icimg': geticimg(w)
    }
    return json.dumps(result, ensure_ascii=False)

#bottle.run(host='0.0.0.0', port=8787, reloader=True)
app = bottle.default_app()
serve(app, host='0.0.0.0', port=8787)
