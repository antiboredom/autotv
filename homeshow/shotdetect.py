"""
sourced from:
https://github.com/albanie/shot-detection-benchmarks/blob/master/detectors/ffprobe_shots.py
"""
from __future__ import division, print_function
import subprocess
import os
import json
import config


def shots(src_video, threshold=0):
    """
    uses ffprobe to produce a list of shot
    boundaries (in seconds)

    Args:
        src_video (string): the path to the source
            video
        threshold (float): the minimum value used
            by ffprobe to classify a shot boundary

    Returns:
        List[(float, float)]: a list of tuples of floats
        representing predicted shot boundaries (in seconds) and
        their associated scores
    """
    scene_ps = subprocess.Popen(("ffprobe",
                                "-show_frames",
                                "-of",
                                "compact=p=0",
                                "-f",
                                "lavfi",
                                "movie=" + src_video + ",select=gt(scene\," + str(threshold) + ")"),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                encoding='utf8')
    output = scene_ps.stdout.read()
    boundaries = parse_shots(output)
    return boundaries


def parse_shots(output):
    """
    extracts the shot boundaries from the string output
    producted by ffprobe

    Args:
        output (string): the full output of the ffprobe
            shot detector as a single string

    Returns:
        List[(float, float)]: a list of tuples of floats
        representing predicted shot boundaries (in seconds) and
        their associated scores
    """
    boundaries = []
    for line in output.split('\n')[15:-1]:
        try:
            boundary = float(line.split('|')[4].split('=')[-1])
            score = float(line.split('|')[-1].split('=')[-1])
            boundaries.append({'time': boundary, 'score': score})
        except:
            continue
    return boundaries


def cached_shots(filename, overwrite=False, thresh=0):
    outname = filename + '.shots.json'

    if overwrite is False and os.path.exists(outname):
        with open(outname, 'r') as infile:
            boundaries = json.load(infile)
        return boundaries

    boundaries = shots(filename, threshold=thresh)

    with open(outname, 'w') as outfile:
        json.dump(boundaries, outfile)

    return boundaries


if __name__ == '__main__':
    import sys
    for f in sys.argv[1:]:
        print('finding shots for', f)
        cached_shots(f, thresh=config.thresh)
