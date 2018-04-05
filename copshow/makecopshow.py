import os
import sys
import random
import json
from subprocess import call
from shutil import copyfile, rmtree
from vidpy import Clip, Text, Composition
import vidpy.config

PROFILE = 'atsc_720p_25'
MELT_BINARY = vidpy.config.MELT_BINARY = 'melt'

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def generate_affine(frame, maxr=160):
    r = random.randint(100, maxr)
    x = random.randint(-int((r-100)/2), 0)
    y = random.randint(-int((r-100)/2), 0)
    # x = -(maxr-100)/2
    # y = -(maxr-100)/2

    transition = '{}={}%,{}%:{}%x{}%'.format(frame, x, y, r, r)
    return transition


def simple_slideshow(foldername, ttl=10):
    outname = 'simple_slideshow.xml'
    args = [
        MELT_BINARY,
        '-profile', PROFILE,
        os.path.join(foldername, '.all.jpg'),
        'ttl={}'.format(ttl),
        '-consumer', 'xml:{}'.format(outname)
    ]
    call(args)
    return outname


def anxious_slideshow(foldername, ttl=16, interval=100):
    outname = 'anxious_slideshow.xml'

    args = [MELT_BINARY, '-profile', PROFILE]
    while ttl > 1:
        args += [os.path.join(foldername, '.all.jpg'), 'ttl={}'.format(ttl), 'out={}'.format(interval)]
        ttl = ttl/2

    args += ['-consumer', 'xml:{}'.format(outname)]
    call(args)
    return outname


def kenburns(foldername, ttl=75, total_transitions=3, transition=25):
    outname = 'kenburns.xml'
    # outname = 'slides.mp4'

    cycle = total_transitions * ttl
    transitions = []
    for i in range(0, total_transitions+1):
        frame = i * ttl

        if i > 0:
            transition = generate_affine(frame-1)
            transitions.append(transition)

        if i < total_transitions:
            transition = generate_affine(frame)
            transitions.append(transition)

    transitions = ';'.join(transitions)

    args = [
        MELT_BINARY,
        '-profile', PROFILE,
        os.path.join(foldername, '.all.jpg'),
        'ttl={}'.format(ttl),
        '-attach', 'crop', 'center=1',
        '-attach', 'affine',
        'transition.cycle={}'.format(cycle),
        'transition.geometry="{}"'.format(transitions),
        '-filter', 'luma', 'cycle={}'.format(ttl), 'duration={}'.format(transition),
        '-consumer', 'xml:{}'.format(outname)
        # '-consumer', 'avformat:{}'.format(outname)
    ]
    call(args)
    return outname


# def slideshow_params(foldername, slide_duration=75, fade=25):
#     '''melt -profile atsc_720p_25 images/.all.jpg ttl=75 -attach crop center=1 -attach affine transition.cycle=225 transition.geometry="0=0,0:100%x100%;74=-100,-100:120%x120%;75=-60,-60:110%x110%;149=0:0:110%x110%;150=0,-60:110%x110%;224=-60,0:110%x110%" -filter luma cycle=75 duration=25'''

def compose(datafile, outname, total_duration=3600, slide_duration=20, fade=2):
    people = []

    with open(datafile, 'r') as infile:
        data = json.load(infile)

    for p in data:
        pid = p['memberId']
        img = 'images/{}.jpg'.format(pid)
        if os.path.exists(img):
            p['image'] = img
            people.append(p)

    total_duration = 60*60
    slide_duration = 20
    fade = 2

    random.shuffle(people)
    people = people[0:int(total_duration/slide_duration)]

    allclips = []

    for chunknum, chunk in enumerate(chunker(people, 10)):
        try:
            rmtree('slideimages')
        except:
            pass

        os.makedirs('slideimages')

        tmpoutname = str(chunknum).zfill(5) + '.mp4'

        for i, p in enumerate(chunk):
            tmpname = 'slideimages/{}.jpg'.format(str(i).zfill(5))
            call(['convert', p['image'], '-resize', '1280x720', '-ordered-dither', 'h4x4o', tmpname])
            # call(['convert', tmpname + '.gif' p['image'], '-resize', '1280x720', '-ordered-dither', 'h4x4o', tmpname + '.gif'])
            # copyfile(p['image'], tmpname)

        slides = kenburns('slideimages', ttl=slide_duration*25, total_transitions=10, transition=fade*25)
        # call(['melt', slides, 'out={}'.format(len(chunk)*slide_duration*25), '-consumer', 'avformat:{}'.format(tmpoutname)])

        clips = [Clip(slides, end=len(chunk)*slide_duration)]
        textpad = 2
        offset = 0

        for p in chunk:
            txt = p.get('formattedName', '').split(' ')[0] + '\n' + p.get('title', '') + '\n'+p.get('location', '')
            clip = Text(txt, start=0, end=slide_duration-textpad, offset=offset+textpad, halign="left", valign="bottom", color="#ff0000", font='OCR A Std', bbox=('5%', '5%', '90%', '90%'))
            clip.fadein(fade)
            clip.fadeout(fade)
            offset += slide_duration
            clips.append(clip)

        comp = Composition(clips, bgcolor='#000000')
        call(str(comp) + ' -consumer avformat:{}'.format(tmpoutname), shell=True)
        allclips.append(tmpoutname)

    comp = Composition([Clip(c, start=0.5) for c in allclips], singletrack=True).save(outname)
    return outname
    # comp.preview()


def gen_web_slides(datafiles):
    items = []
    for i in range(0, 10):
        item = {
          "image": str(i).zfill(5)+'.jpg',
          "duration": 20000,
          "transitionNext": { "duration": 2000 },
          "kenburns": {
            "from": [0.8, [0.5,0.5]],
            "to": [1, [0.5,0.5]]
          },
        }
        items.append(item)
    out = {'timeline': items}
    with open('webslide/diaporama.json', 'w') as outfile:
        json.dump(out, outfile, indent=2)




if __name__ == '__main__':
    # compose('cops.json', 'copshow.mp4')
    gen_web_slides('cops.json')

