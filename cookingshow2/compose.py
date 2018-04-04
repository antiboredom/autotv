import sys
import re
import json
from glob import glob
import random
import vtt
import shutil
import spacy
import time
import os
from subprocess import call, Popen
from vidpy import Clip, Composition, config
config.MELT_BINARY = 'melt'
nlp = spacy.load('en')

def download(query, pages=4):
    print(query)
    for i in range(1, pages+1):
        url = 'https://www.youtube.com/results?page={}&search_query=how+to+cook+{},cc'.format(i,query.replace(' ', '+'))
        call(['youtube-dl', url, '-f', '22', '-i', '--write-auto-sub', '--max-filesize', '100m', '-o', 'videos/%(id)s.%(ext)s'])


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def find_sub_list(sl, l):
    results=[]
    sll=len(sl)
    for ind in (i for i,e in enumerate(l) if e==sl[0]):
        if l[ind:ind+sll]==sl:
            results.append((ind,ind+sll-1))

    return results


def pos_regex_matches(doc, pattern, use_pos=False):
    """
    from: https://github.com/chartbeat-labs/textacy/blob/master/textacy/extract.py
    Extract sequences of consecutive tokens from a spacy-parsed doc whose
    part-of-speech tags match the specified regex pattern.
    Args:
        doc (``textacy.Doc`` or ``spacy.Doc`` or ``spacy.Span``)
        pattern (str): Pattern of consecutive POS tags whose corresponding words
            are to be extracted, inspired by the regex patterns used in NLTK's
            `nltk.chunk.regexp`. Tags are uppercase, from the universal tag set;
            delimited by < and >, which are basically converted to parentheses
            with spaces as needed to correctly extract matching word sequences;
            white space in the input doesn't matter.
            Examples (see ``constants.POS_REGEX_PATTERNS``):
            * noun phrase: r'<DET>? (<NOUN>+ <ADP|CONJ>)* <NOUN>+'
            * compound nouns: r'<NOUN>+'
            * verb phrase: r'<VERB>?<ADV>*<VERB>+'
            * prepositional phrase: r'<PREP> <DET>? (<NOUN>+<ADP>)* <NOUN>+'
    Yields:
        ``spacy.Span``: the next span of consecutive tokens from ``doc`` whose
        parts-of-speech match ``pattern``, in order of apperance
    """
    # standardize and transform the regular expression pattern...
    pattern = re.sub(r'\s', '', pattern)
    pattern = re.sub(r'<([A-Z]+)\|([A-Z]+)>', r'( (\1|\2))', pattern)
    pattern = re.sub(r'<([A-Z]+)>', r'( \1)', pattern)

    if use_pos:
        tags = ' ' + ' '.join(tok.pos_ for tok in doc)
    else:
        tags = ' ' + ' '.join(tok.tag_ for tok in doc)

    for m in re.finditer(pattern, tags):
        # yield doc[tags[0:m.start()-5].count(' '):tags[0:m.end()+5].count(' ')]
        yield doc[tags[0:m.start()].count(' '):tags[0:m.end()].count(' ')]


def parse_json(filename):
    with open(filename, 'r') as infile:
        data = json.load(infile)

    out = []
    for frag in data['fragments']:
        item = {'start': frag['begin'], 'end': frag['end'], 'word': ' '.join(frag['lines'])}
        out.append(item)

    return out


def compose_clip(filenames, outname, pat):
    timestamps = []

    for f in filenames:
        try:
            with open(f.replace('.mp4', '.en.vtt'), 'r') as infile:
                data = infile.read()
            sentences = vtt.parse_auto_sub(data)
        except:
            continue

        if 'words' not in sentences[0]:
            continue

        if '<' in pat:
            text = ' '.join([s['text'] for s in sentences])
            doc = nlp(text)

            results = pos_regex_matches(doc, pat)
            results = [r.string.lower().strip() for r in results]
            results = [r for r in results if "'" not in r]
            results = list(set(results))
        else:
            results = pat.split('|')

        allwords = []
        for s in sentences:
            allwords += s['words']

        justwords = [w['word'].lower().strip() for w in allwords]

        for r in results:
            # print(r)
            indices = find_sub_list(r.split(' '), justwords)
            for i in indices:
                start = allwords[i[0]]['start']
                end = allwords[i[1]]['end'] + 0.2
                timestamps.append((f, r, start, end))

    timestamps = sorted(timestamps, key=lambda x: x[1])
    clips = []

    '''create with vidpy'''
    for f, r, start, end in timestamps:
        print(r)
        clip = Clip(f, start=start, end=end)
        clip.text(r, font='Courgette', size=60, valign='bottom', color='#FFFF00', bbox=('1%', '1%', '98%', '98%'))
        clips.append(clip)

    tmpclips = []
    for i, chunk in enumerate(chunker(clips, 60)):
        tmpname = outname + '.tmp.{}.mp4'.format(str(i).zfill(5))
        comp = Composition(chunk, singletrack=True)
        comp.save(tmpname)
        tmpclips.append(tmpname)

    comp = Composition([Clip(t) for t in tmpclips], singletrack=True)
    comp.save(outname)

    for tmpname in tmpclips:
        os.remove(tmpname)

    '''create with ffmpeg'''
    # clipnum = 0
    # for f, r, start, end in timestamps:
    #     tempout = 'shots/' + str(clipnum).zfill(6) + '.mp4'
    #     fontfile = os.path.abspath("Courgette-Regular.ttf")
    #     args = '''ffmpeg -hide_banner -loglevel panic -y -i {} -ss {} -t {} -strict -2 -vf drawtext="fontfile={}:text='{}': fontcolor=yellow: fontsize=30: x=(w-text_w)/2: y=(h-text_h-20)" {}'''.format(f, start, end-start, fontfile, r, tempout)
    #     args = '''ffmpeg -hide_banner -loglevel panic -y -i {} -ss {} -t {} -strict -2 {}'''.format(f, start, end-start, tempout)
    #     with Popen(args, shell=True):
    #         pass
    #     clipnum += 1

    '''create clips with vidpy'''
    # clipnum = 0
    # for f, r, start, end in timestamps:
    #     print(r)
    #     tempout = 'shots/' + str(clipnum).zfill(6) + '.mp4'
    #     clip = Clip(f, start=start, end=end)
    #     clip.text(r, font='Courgette', size=60, valign='bottom', color='#FFFF00', bbox=('1%', '1%', '98%', '98%'))
    #     Composition([clip]).save(tempout, silent=True)
    #     clipnum += 1

    return outname


def main(filenames=None):
    # try:
    #     shutil.rmtree('shots')
    # except:
    #     pass
    #
    # os.makedirs('shots')

    query = ''

    if filenames is None:
        with open('recipes.txt', 'r') as infile:
            recipes = [r.strip() for r in infile.readlines()]
        recipes = [r for r in recipes if r != '']
        query = random.choice(recipes)
        download(query)
        filenames = glob('videos/*.mp4')

    video = [
        ('ingredients',         '(<DT>? <CD>? <JJ>? <NN|NNS>+ <IN> <NN|NNS>+)'),
        ('simple_ingredients',  '(<JJ> <NN|NNS>)'),
        ('simple_ingredients2', '(<JJ>? <NN> <IN> <JJ>? <NN|NNS>)'),
        ('instructions',        '(<RB>? <VB> <DT>? <JJ>? <NN|NNS> <RB>?)'),
        ('instructions2',       '(<VB> <PRP> <RB>? <NN|NNS>?)'),
        ('delicious',           'delicious|incredible|wonderful|amazing'),
        ('hmm',                 'hmm|mmm|yum'),
    ]

    clips = []
    for cat, pat in video:
        outname = cat + '.mp4'
        compose_clip(filenames, outname, pat)
        clips.append(Clip(outname))

    comp = Composition(clips, singletrack=True)
    # finalname = 'cookingshow_' + query + '.mp4'
    finalname = 'cookingshow.mp4'
    comp.save(finalname)
    return finalname


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) > 0:
        main(args)
    else:
        main()
