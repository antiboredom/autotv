from glob import glob
from subprocess import call
import config
import os
import shotdetect
from vidpy import Clip, Composition
import vidpy.config

vidpy.config.MELT_BINARY = 'melt'


def extract_frames(f, shots):
    last_extract = 0
    for shot in shots:
        outname = f.replace('videos/', 'frames/') + '@' + str(shot['time']) + '.jpg'
        if os.path.exists(outname) or shot['score'] <= config.thresh or shot['time'] - last_extract < config.min_duration:
            continue

        call(['ffmpeg', '-ss', str(shot['time']), '-i', f, '-vframes', '1', outname])
        last_extract = shot['time']


def extract_shots(thresh=0.2, duration=4, padding=0.5):
    shots = {}
    allshots = []

    for f in glob('videos/*.shots.json'):

        with open(f, 'r') as infile:
            data = json.load(infile)

        f = f.replace('.shots.json', '')

        _shots = [d['time'] for d in data if d['score'] > thresh]
        for i, d in enumerate(_shots):

            if i > 0:
                start = _shots[i-1]
            else:
                start = 0
            end = d

            start += padding
            end -= padding
            end = min(end, start + duration - padding)

            if end - start < 1:
                continue

            print(start, end)

            outname = 'shots/{}_{}_{}.mp4'.format(f.replace('videos/', ''), start, end)
            if os.path.exists(outname):
                continue

            clip = Clip(f, start=start, end=end)
            clip.zoompan([0, 0, '100%', '100%'], ['-25%', '-25%', '150%', '150%'], 0, 100)
            clip.save(outname)


def main():
    '''Downloads files, finds and extracts shots'''

    for s in config.sources[1:]:
        call(['youtube-dl', s, '-i', '-f', '22', '-o', 'videos/%(id)s.%(ext)s'])

    for f in glob('videos/*.mp4'):
        print('finding shots for', f)
        shots = shotdetect.cached_shots(f, thresh=config.thresh)
        # extract_frames(f, shots)

    extract_shots(thresh=config.thresh)


if __name__ == '__main__':
    main()
