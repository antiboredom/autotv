import random
from glob import glob
import json
import os
import re
from vidpy import Clip, Composition
import vidpy.config
import config
from subprocess import call

vidpy.config.MELT_BINARY = 'melt'

def compose(maxduration=60, thresh=0.2, fade=0.3, duration=4, sections=3, padding=0.5, outname='home.mp4'):
    shots = {}
    allshots = []

    for f in glob('videos/*.shots.json'):
        # if re.search(r'^videos/\d+', f) is None:
        #     continue

        with open(f, 'r') as infile:
            data = json.load(infile)

        f = f.replace('.shots.json', '')

        _shots = [(f, d['time']) for d in data if d['score'] > thresh]
        _shots = [d['time'] for d in data if d['score'] > thresh]
        shots[f] = []
        for i, d in enumerate(_shots):
            if i > 0:
                start = _shots[i-1]
            else:
                start = 0
            end = d
            shots[f].append((start, end))

        # if len(_shots) > 5:
        #     shots[f] = _shots
        #     allshots += _shots

    offset = 0
    clips = []
    while offset < maxduration:
        filename = random.choice(list(shots.keys()))
        if len(shots[filename]) < 5:
            continue
        start, end = random.choice(shots[filename])
        start += padding
        end -= padding
        dur = min(end-start, duration-padding)

        clip = Clip(filename, start=start, end=start+dur, offset=offset)
        # clip.text(filename)
        clip.zoompan([0, 0, '100%', '100%'], ['-25%', '-25%', '150%', '150%'], 0, 100)
        clip.fadein(fade)
        # offset += duration - fade
        offset += dur - fade
        clips.append(clip)


    # if stitch:
    comp = Composition(clips)
    comp.save(outname)


def combine(files=None, maxfiles=1800, outname='home_invader.mp4'):
    '''
    for f in *.mp4; do ffmpeg -n -i $f -q:v 1 $f.ts; done
    ffmpeg -f concat -safe 0 -r 25 -i <(for f in ./*.ts; do echo "file '$PWD/$f'"; done) -c copy output.mp4
    '''
    if files is None:
        files = glob('shots/*.mp4')

    random.shuffle(files)

    files = files[0:maxfiles]

    for f in files:
        if os.path.exists(f + '.ts'):
            continue
        call(['ffmpeg', '-y', '-i', f, '-c', 'copy', '-bsf:v', 'h264_mp4toannexb', '-f', 'mpegts', '-q:v', '1', f + '.ts'])

    files = [f"file '{os.path.abspath(f)}.ts'" for f in files]

    with open('toconcat.txt', 'w') as outfile:
        outfile.write('\n'.join(files))

    call(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'toconcat.txt', '-c', 'copy', '-f', 'mp4', outname])

    return outname



if __name__ == '__main__':
    import sys
    # combine(sys.argv[1:])
    args = sys.argv[1:]
    if len(args) > 0:
        combine(args)
    else:
        combine()

