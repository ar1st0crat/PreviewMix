# -*- coding: utf-8 -*-

##########################################################################
# Created by ar1st0crat
# PreviewMix
# ver. 0.10
#
# A script for making the previews of musical albums or any tracklists.
# The script is basically an ffmpeg wrapper.
# 
# Note: ffmpeg executable should be located in the script folder
# 	    or included in the system path.
# 
# Parameters:
#	--source (-s)
#		The source folder containing album tracks
#		(required)
#	--destination (-d)
#		The destination mp3 file that will contain preview mix
#		(by default: '100-preview.mp3' in the source folder)
#	--count (-c)
#		The number of tracks to include into preview mix
#		(by default: all tracks in the source folder)
#	--framesize (-f)
#		The size of a segment to crop from each track
#		(by default: 25 seconds)
#	--log (-l)
#		Show progress
#		(by default: False)
#
# Usage example:
#	previewmix --source "C:\Music\2000 - Album" --count 5 --frame 15 -l
#
##########################################################################

import os
import sys
import errno
import subprocess
import argparse


DEFAULT_FRAMESIZE = 25
DEFAULT_STARTINGTIME = 60
DEFAULT_FADESIZE = 2
DEFAULT_BITRATE = '320k'
DEFAULT_OUTPUTNAME = '100-preview.mp3'


def silent_remove(filename):
    """ helper function that removes a file if it exists """
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


# Setup and checks:

# 1) create argument parser and parse command line parameters:
parser = argparse.ArgumentParser(
    description='Script to learn basic argparse')
parser.add_argument('-s', '--source',
                    help='the source folder containing album tracks',
                    required='True')
parser.add_argument('-d', '--destination',
                    help='the destination mp3 file with preview mix',
                    default='none')
parser.add_argument('-c', '--count',
                    help='the number of tracks to include into preview mix',
                    default='all')
parser.add_argument('-f', '--framesize',
                    help='the size of a segment to crop from each track',
                    default=str(DEFAULT_FRAMESIZE))
parser.add_argument('-l', '--log',
                    help='show progress',
                    action='store_true')
params = parser.parse_args(sys.argv[1:])


# 2) set script parameters according to command line arguments:
folder = params.source

# check and prepare destination file
if params.destination == 'none':
    outputfile = os.path.join(folder, DEFAULT_OUTPUTNAME)
    print('The preview mix will be written to %s' % outputfile)
else:
    outputfile = params.destination
    if os.path.dirname(outputfile) != '':
        os.makedirs(os.path.dirname(outputfile), exist_ok=True)

# check and prepare framesize
try:
    framesize = int(params.framesize)
except ValueError:
    framesize = DEFAULT_FRAMESIZE
    print('Wrong framesize format! Set to default: %d sec' % DEFAULT_FRAMESIZE)

# create main mp3-list for further processing
mp3tracks = [os.path.join(folder, file) for file in os.listdir(folder)
             if file.endswith('mp3')]

# check and prepare track count
if params.count == 'all':
    trackcount = len(mp3tracks)
else:
    try:
        trackcount = int(params.count)
        if trackcount > len(mp3tracks):
            trackcount = len(mp3tracks)
            print('Too many tracks! Set trackcount to %d' % trackcount)
    except ValueError:
        trackcount = len(mp3tracks)
        print('Wrong trackcount format! Set trackcount to %d' % trackcount)

showprogress = params.log


# 3) additional setup:
ffmpegpath = 'ffmpeg'
try:
    subprocess.Popen([ffmpegpath], stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)
except Exception:
    print("""Could not run ffmpeg!
Please add ffmpeg to current directory or to the system path""")
    exit()

startingtime = DEFAULT_STARTINGTIME
fadesize = DEFAULT_FADESIZE
tracktemp = 'temp.mp3'


# main track processing loop
trackpreviews = []
trackno = 1
try:
    # it's possible that preview mix file has already been created before.
    # in that case just remove the previous version
    silent_remove(outputfile)

    for track in mp3tracks[:trackcount]:
        if showprogress:
            print(' --- processing file: %s' % track)

        # ffmpeg command for cropping mp3:
        # ffmpeg -ss 10 -t 6 -i file.mp3 [-acodec copy] temp.mp3
        subprocess.check_call([ffmpegpath,
                               '-ss', str(startingtime),
                               '-t', str(framesize),
                               '-i',
                               track,
                               '-acodec', 'copy',
                               tracktemp],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)

        # ffmpeg command for adding the 'fade in / fade out' effect:
        # ffmpeg -i temp.mp3 -af 'afade=t=in:ss=0:d=2,afade=t=out:st=23:d=2' temp1.mp3
        trackpreview = 'temp%d.mp3' % trackno
        fadeoption = 'afade=t=in:ss=0:d={0},afade=t=out:st={1}:d={0}'.format(
            fadesize, framesize - fadesize)
        subprocess.check_call([ffmpegpath,
                               '-i',
                               tracktemp,
                               '-af',
                               fadeoption,
                               '-ab', DEFAULT_BITRATE,
                               trackpreview],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)

        trackpreviews.append(trackpreview)
        # remove intermediate temporary file
        # so that ffmpeg won't ask us to do that
        os.remove(tracktemp)
        trackno += 1

    # ffmpeg command for concatenating mp3 files:
    # ffmpeg -i concat:"atemp1.mp3|atemp2.mp3" -acodec copy mix.mp3
    concatfiles = '|'.join(trackpreviews)
    subprocess.check_call([ffmpegpath,
                           '-i',
                           'concat:%s' % concatfiles,
                           '-acodec', 'copy',
                           outputfile],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)
    if showprogress:
        print(' === done!')

# catch any exception
except Exception as e:
    print('Could not create a preview mix: %s' % e)
finally:
    # clean up temp files
    silent_remove(tracktemp)
    for tmp in trackpreviews:
        os.remove(tmp)
