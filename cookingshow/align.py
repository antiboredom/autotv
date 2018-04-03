from subprocess import call
import sys
import requests
import json
import re
import os
from collections import OrderedDict


def convert_srt(srt):
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

    output = ' '.join([output[k].strip() for k in output])
    return output


def align(audiofile, wordfile):
    outname = audiofile + '.json'
    if os.path.exists(outname):
        return True

    params = (
        ('async', 'false'),
    )

    files = [
        ('audio', open(audiofile, 'rb')),
        ('transcript', open(wordfile, 'rb')),
    ]

    results = requests.post('http://localhost:8765/transcriptions', params=params, files=files)
    data = results.json()

    with open(outname, 'w') as outfile:
        json.dump(data, outfile)



def align_with_subtitle(audiofile):
    subtitle_file = audiofile.replace('.mp4', '.srt')
    justtext = convert_srt(subtitle_file)
    wordfile = subtitle_file.replace('.srt', '.txt')
    with open(wordfile, 'w') as outfile:
        outfile.write(justtext)

    align(audiofile, wordfile)


if __name__ == '__main__':
    for f in sys.argv[1:]:
        align_with_subtitle(f)
