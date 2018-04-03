from __future__ import unicode_literals
import re
import json
from glob import glob
from collections import OrderedDict
import random
import time
from annoy import AnnoyIndex
import numpy as np
import pickle
from moviepy.editor import VideoFileClip, concatenate
from vidpy import Clip, Composition, config
from tqdm import tqdm
import spacy
nlp = spacy.load('/Users/sam/spacy/en_core_web_lg-2.0.0')

config.MELT_BINARY = 'melt'

# nlp = spacy.load('en_core_web_lg')
# nlp = spacy.load('en')

BASE = '/Volumes/hd_wo_qualities/cooking_show/'

testlines = '''
Call me Ishmael. Some years ago—never mind how long precisely—having
little or no money in my purse, and nothing particular to interest me on
shore, I thought I would sail about a little and see the watery part of
the world. It is a way I have of driving off the spleen and regulating
the circulation. Whenever I find myself growing grim about the mouth;
whenever it is a damp, drizzly November in my soul; whenever I find
myself involuntarily pausing before coffin warehouses, and bringing up
the rear of every funeral I meet; and especially whenever my hypos get
such an upper hand of me, that it requires a strong moral principle to
prevent me from deliberately stepping into the street, and methodically
knocking people’s hats off—then, I account it high time to get to
sea as soon as I can. This is my substitute for pistol and ball. With
a philosophical flourish Cato throws himself upon his sword; I quietly
take to the ship. There is nothing surprising in this. If they but knew
it, almost all men in their degree, some time or other, cherish very
nearly the same feelings towards the ocean with me.

There now is your insular city of the Manhattoes, belted round by
wharves as Indian isles by coral reefs—commerce surrounds it with
her surf. Right and left, the streets take you waterward. Its extreme
downtown is the battery, where that noble mole is washed by waves, and
cooled by breezes, which a few hours previous were out of sight of land.
Look at the crowds of water-gazers there.

Circumambulate the city of a dreamy Sabbath afternoon. Go from Corlears
Hook to Coenties Slip, and from thence, by Whitehall, northward. What
do you see?—Posted like silent sentinels all around the town, stand
thousands upon thousands of mortal men fixed in ocean reveries. Some
leaning against the spiles; some seated upon the pier-heads; some
looking over the bulwarks of ships from China; some high aloft in the
rigging, as if striving to get a still better seaward peep. But these
are all landsmen; of week days pent up in lath and plaster—tied to
counters, nailed to benches, clinched to desks. How then is this? Are
the green fields gone? What do they here?
'''.split('\n')
testlines = [l.strip() for l in testlines if l.strip() != '']


def convert_timespan(timespan):
    """Convert an srt timespan into a start and end timestamp."""
    start, end = timespan.split('-->')
    start = convert_timestamp(start)
    end = convert_timestamp(end)
    return start, end


def convert_timestamp(timestamp):
    """Convert an srt timestamp into seconds."""
    timestamp = timestamp.strip()
    chunk, millis = timestamp.split(',')
    hours, minutes, seconds = chunk.split(':')
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    seconds = seconds + hours * 60 * 60 + minutes * 60 + float(millis) / 1000
    return seconds


def clean_srt(srt):
    """Remove damaging line breaks and numbers from srt files and return a
    dictionary.
    """
    with open(srt, 'r') as f:
        text = f.read()
    text = re.sub(r'^\d+[\n\r]', '', text, flags=re.MULTILINE)
    lines = text.splitlines()
    output = OrderedDict()
    key = ''

    for line in lines:
        line = line.strip()
        if line.find('-->') > -1:
            key = line
            output[key] = ''
        else:
            if key != '':
                output[key] += line + ' '

    return output


def load_annoy():
    # a = AnnoyIndex(384, metric='angular')
    a = AnnoyIndex(300, metric='angular')
    a.load('cooking_lg.ann')
    with open('cooking_lg.pickle', 'rb') as infile:
        map_i_to_description = pickle.load(infile)
    return (a, map_i_to_description)


def build_annoy():
    a = AnnoyIndex(300, metric='angular')

    sentences = []
    for srt in glob(BASE + '*.srt'):
        lines = clean_srt(srt)
        sentences += [lines[k] for k in lines]

    i = 0
    map_i_to_description = {}
    for item in tqdm(sentences):
        mv = meanvector(item)
        # print(np.shape(mv))
        if mv is not None:
            a.add_item(i, mv)
            map_i_to_description[i] = item
            i += 1

    a.build(50)
    a.save('cooking_lg.ann')
    with open('cooking_lg.pickle', 'wb') as outfile:
        pickle.dump(map_i_to_description, outfile)


def meanvector(text):
    '''
    Average of the word vectors in a sentence
    from https://github.com/cvalenzuela/scenescoop/blob/master/make_scene.py
    '''
    s = nlp(text)
    vecs = [word.vector for word in s if word.pos_ in ('NOUN', 'VERB', 'ADJ', 'ADV', 'PROPN', 'ADP') and np.any(word.vector)]  # skip all-zero vectors
    # vecs = [word.vector for word in s if word.pos_ in ('NOUN', 'VERB') and np.any(word.vector)]  # skip all-zero vectors
    # vecs = [word.vector for word in s if word.pos_ in ('NOUN') and np.any(word.vector)]  # skip all-zero vectors
    if len(vecs) == 0:
        return None
        # raise IndexError
    else:
        return np.array(vecs).mean(axis=0)


def nearest_neighbor(data, inp, t):
    '''
    Creates an Annoy index for fast nearest-neighbor lookup
    from: https://github.com/cvalenzuela/scenescoop/blob/master/make_scene.py
    '''
    i = 0
    map_i_to_description = {}
    for item in data:
        # try:
        mv = meanvector(item)
        # print(np.shape(mv))
        # print(item, mv)
        if mv is not None:
            t.add_item(i, mv)
            map_i_to_description[i] = item
            i += 1
        # except IndexError as e:
        #     print(item)
        #     print(e)
        #     continue

    # print('MAP i TO DESCRIPTION', map_i_to_description)
    t.build(50)
    mv = meanvector(inp)
    nearest = t.get_nns_by_vector(mv, n=10)[0]
    return map_i_to_description[nearest]


def closest(seed, lines):
    out = []
    seed = nlp(seed)
    for l in lines:
        doc = nlp(l)
        sim = seed.similarity(doc)
        out.append((l, sim))

    out = sorted(out, key=lambda x: x[1], reverse=True)
    return out[0]


def similar_lines(seed, lines, total=20):
    seedline = seed
    out = [seedline]
    while len(out) < total:
        try:
            lines.remove(seedline)
        except:
            pass
        nextline, sim = closest(seedline, lines)
        print(nextline)
        out.append(nextline)
        seedline = nextline
    return out


def similar_srt_lines(seed, srtfiles, total=20):
    sentences = []
    for srt in srtfiles[0:1]:
        lines = clean_srt(srt)
        sentences += [lines[k] for k in lines]

    for l in similar_lines('mix', sentences):
        print(l)


def similar_srt(seed, srtfiles, total=20):
    t = AnnoyIndex(384, metric='angular')
    sentences = []
    alllines = []
    random.shuffle(srtfiles)
    for srt in srtfiles[0:10]:
        lines = clean_srt(srt)
        sentences += [lines[k] for k in lines]
        alllines += [(k, lines[k], srt) for k in lines]

    out = []
    seedline = seed
    while len(out) < total:
        try:
            sentences.remove(seedline)
        except:
            pass
        nextline = nearest_neighbor(sentences, seedline, t)
        options = [l for l in alllines if l[1].lower().strip() == nextline.lower().strip()]
        print(nextline)
        out.append(options)
        seedline = nextline

    clips = []
    vids = {}

    for o in out:
        ts, text, srt = random.choice(o)
        vid = srt.replace('.srt', '.mp4')
        if vid not in vids:
            vids[vid] = VideoFileClip(vid)
        start, end = convert_timespan(ts)
        clip = vids[vid].subclip(start, end + 0.5)
        clips.append(clip)

    comp = concatenate(clips)
    comp.write_videofile('ok.mp4')


def get_nearest(seed, total=500):
    a, maps = load_annoy()

    out = []
    lastline = seed

    mv = meanvector(lastline)
    neighbors = a.get_nns_by_vector(mv, n=total)
    neighbors = [maps[n] for n in neighbors]
    for n in neighbors:
        print(n)

    # while len(out) < total:
    #     mv = meanvector(lastline)
    #     neighbors = a.get_nns_by_vector(mv, n=total*5)
    #     neighbors = [maps[n] for n in neighbors]
    #     # print([n for n in neighbors if n not in out])
    #     nextline = [n for n in neighbors if n not in out][0]
    #     out.append(nextline)
    #     print(nextline)
    #     lastline = nextline

    return neighbors


def generate_lines(seed, total=30):
    a, maps = load_annoy()

    out = []
    lastline = seed

    # mv = meanvector(lastline)
    # neighbors = a.get_nns_by_vector(mv, n=500)
    # neighbors = [maps[n] for n in neighbors]
    # for n in neighbors:
    #     print(n)

    while len(out) < total:
        mv = meanvector(lastline)
        neighbors = a.get_nns_by_vector(mv, n=total*5)
        neighbors = [maps[n] for n in neighbors]
        # print([n for n in neighbors if n not in out])
        nextline = [n for n in neighbors if n not in out][0]
        out.append(nextline)
        print(nextline)
        lastline = nextline

    return out


def find_line(q, lines):
    print(q)
    results = [l for l in lines if l[1].lower().strip() == q.lower().strip()]
    return results



def find_sub_list(sl, l):
    '''
    from: https://stackoverflow.com/questions/17870544/find-starting-and-ending-indices-of-sublist-in-list
    '''

    results=[]
    sll=len(sl)
    for ind in (i for i,e in enumerate(l) if e==sl[0]):
        if l[ind:ind+sll]==sl:
            results.append((ind,ind+sll-1))

    return results


def find_in_json(q, data):
    results = []
    q = q.split(' ')
    q = [re.sub(r'\W+', '', w) for w in q]
    q = [w for w in q if w != '']
    for k in data:
        words = data[k]
        transcript = [re.sub(r'\W+', '', w['word']) for w in words]
        indices = find_sub_list(q, transcript)
        for s, e in indices:
            try:
                results.append((k, words[s]['start'], words[e]['end']))
            except:
                continue

    # if len(results) == 0:
    #     return None

    # result = random.choice(results)
    return results




def compose(lines, outname='cut.mp4'):
    alllines = {}
    clips = []
    vids = {}

    # for srt in glob(BASE + '*.srt'):
    #     _lines = clean_srt(srt)
    #     alllines += [(k, _lines[k], srt) for k in _lines]

    segments = []

    for jsonfile in glob(BASE + '*.json'):
        with open(jsonfile, 'r') as infile:
            words = json.load(infile)['words']
        alllines[jsonfile] = words

    for l in lines:
        # ts, text, srt = random.choice(find_line(l, alllines))
        # print(ts, text, srt)
        # vid = srt.replace('.srt', '.mp4')
        # # if vid not in vids:
        # #     vids[vid] = VideoFileClip(vid)
        # start, end = convert_timespan(ts)
        # clip = vids[vid].subclip(start, end + 0.5)
        # clips.append(clip)

        results = find_in_json(l, alllines)
        for r in results:
            if r not in segments:
                segments.append(r)
        # segments += results

    for result in segments:
        jsonfile, start, end = result
        vid = jsonfile.replace('.json', '')
        print(vid, start, end)
        # if vid not in vids:
        #     vids[vid] = VideoFileClip(vid)
        # clip = vids[vid].subclip(start, end)
        clip = Clip(vid, start=start, end=end)
        clips.append(clip)

    # comp = concatenate(clips)
    # comp.write_videofile(outname)
    comp = Composition(clips, singletrack=True)
    comp.save(outname)


def compose_hmms():
    eats = []
    for jsonfile in glob(BASE + '*.json'):
        with open(jsonfile, 'r') as infile:
            words = json.load(infile)['words']

            for a in words:
                if a['word'].lower() == 'mmm' and 'end' in a and 'start' in a:
                    eats.append((jsonfile, a['start'], a['end']))
    clips = []
    for i, s in enumerate(eats):
        jsonfile, start, end = s
        vid = jsonfile.replace('.json', '')
        if end - start > 1:
            start = end - 1
        if end - start < 0.1:
            continue
        print(vid, start, end)
        clip = Clip(vid, start=start, end=end)
        # clip.save('eats/{}.mp4'.format(str(i).zfill(4)))
        clips.append(clip)

    outname = 'hmm.mp4'
    comp = Composition(clips, singletrack=True)
    comp.save(outname)


def compose_eats():
    eats = []
    for jsonfile in glob(BASE + '*.json'):
        with open(jsonfile, 'r') as infile:
            words = json.load(infile)['words']

            for a, b in zip(words, words[1:]):
                if b['word'].lower() == 'mmm' and 'end' in a and 'start' in b:
                    eats.append((jsonfile, a['end'], b['start']))
    clips = []
    for i, s in enumerate(eats):
        jsonfile, start, end = s
        vid = jsonfile.replace('.json', '')
        if end - start > 3:
            start = end - 3
        print(vid, start, end)
        clip = Clip(vid, start=start, end=end)
        # clip.save('eats/{}.mp4'.format(str(i).zfill(4)))
        clips.append(clip)

    outname = 'eats.mp4'
    comp = Composition(clips, singletrack=True)
    comp.save(outname)



def compose_silences(min_silence=2, max_silence=4.0, total=None, randomize=True, outname='silences.mp4'):
    silences = []
    for jsonfile in glob(BASE + '*.json'):
        with open(jsonfile, 'r') as infile:
            words = json.load(infile)['words']
            for a, b in zip(words, words[1:]):
                try:
                    dist = b['start'] - a['end']
                    if dist >= min_silence and dist <= max_silence:
                        silences.append((jsonfile, a['end'], b['start']))
                except Exception as e:
                    continue

    if randomize:
        random.shuffle(silences)

    if total is not None:
        silences = silences[0:total]

    clips = []
    for s in silences:
        jsonfile, start, end = s
        vid = jsonfile.replace('.json', '')
        print(vid, start, end)
        clip = Clip(vid, start=start, end=end)
        clips.append(clip)


    comp = Composition(clips, singletrack=True)
    comp.save(outname)



if __name__ == '__main__':
    # line, sim = closest('call me ishamel', testlines)
    # similar_lines('Call me Ishamel', testlines)
    # similar_srt_lines('', glob(BASE + '*.srt'))
    # similar_srt('Salt', glob(BASE + '*.srt'), total=30)
    # t = AnnoyIndex(384, metric='angular')
    # closest_meaning = nearest_neighbor(testlines, 'Hell', t)
    # print(closest_meaning)

    # build_annoy()
    # q = 'Chicken'


    '''generate a bunch of walks'''
    alllines = []
    for srt in glob(BASE + '*.srt'):
        _lines = clean_srt(srt)
        alllines += [_lines[k] for k in _lines]

    for i in range(0, 1):
        '''old way'''
        random.seed(time.time())
        q = random.choice(alllines)
        lines = generate_lines(q, 500)
        for l in lines:
            print(l)

        '''new way?'''
        # print('---------\n\n')
        # q = random.choice(alllines)
        # lines = get_nearest(q, 100)
        # for l in lines:
        #     print(l)
        # compose(lines, q.replace(' ', '_') + '.mp4')


    '''generate silences'''
    # random.seed(time.time())
    # compose_silences(total=30)
    # compose_hmms()
