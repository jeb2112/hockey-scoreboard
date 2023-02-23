import sys
import os
import numpy as np
from misc import *
from project import Project

######
# main
######

# original mode. game recorded single cam as separate clips, starting and stopping at each whistle
# this mode is currently broken by directory reorganization that was started with the new mode.
# 1. load clips on video 1, then alternate every 2nd clip onto video 2. load the title page at the start of video2
# 2. run preprocess to overlap the raw clips.
# 3. tag the timeline. goal: DMM|opp scorername number. during stop interval
#                      penalty: DMM2|opp4. during stop interval
#                      Guide: period2 on both ends of the stop interval
# 4. run makeclock to make the time clips trun??.mp4 in the project dir
# 5. load time clips into project on video 3
# 6. render at crf=17

# new mode. multiple cams one continuous clip entire game.
# new directory structure. all fixed sub-component graphics are now in repo in the source directory.
# all dynamically assembled interim sub-graphics go into trun/tpng dir of the project working directory
# 1. load clips on video 1,2,3. align clips by the audio.
# 2. tag the timeline with 'w','f' for each start/stoppage including periods goals and penalties. include period2,3 in 'w' tag for period-ending whistle
# 2a. tag a dummy 'w' at time 0, and a dummy 'f' at time end.
# 3. tag goals and penalties separately in between a 'w','f' pair. 
# 4. run makeclock to make the time clips trun ??.mp4 in the project dir
# 5. load time clips into project on video 4
# 6. render at crf=17

# fname. top level directory for a hockey game, ie aeros_12feb
def main(datadir,process,**kwargs):

    print("main")
    cwd = os.getcwd()
    # original directory structure
    # kdendir = "/home//kdenlive/"
    # outdir = kdendir+fname+"/"
    # workdir = kdendir+fname+"/"
    # clipdir = "/media//Data/video/"+fname+"/"
    # new directory structure
    srcdir = '/home/src/python/tcom'
    if not os.path.isdir(datadir):
        print('Data directory {} not found'.format(datadir))
        return
    os.chdir(datadir)

    # run once per installation. hasn't been re-tested since new directory structure
    if process == 'makenumeral':
        tN=timeNumeral(0,'/home/src/tcom/tpng/')
        # if numeral == None:
        tN.makeTimeAll(kdendir+'/tcom/tpng/')
        #else:
        #    timeNumeral.makeTimeNumeral(numeral)

    # intended to replace cli usage of ffmpeg. not finished
    elif process == 'grabfootage':
        duration=kwargs['duration']
        cameraNumber=kwargs['cameraNumber']
        print(duration,cameraNumber)
        sc = tcom.screenCapture(3000,2,'/media/jbishop/Data/video/tmpproj')
        sc=screenCapture()
        sc.runCapture()

    # old code for separate clips per play action
    # currently running this with the project file placed in
    # ~/kdenlive/iceraiders_03feb8/iceraiders_03fen18.kdenlive
    # note that %run ipython command line doesn't require quotes
    # %run -m tcom iceraiders_03feb18 preprocess SCR
    # for strings because args are string by default
    # bug. shifts 1st blank on vid1 under title.
    # bug. manual long fade-in on 1st clip vid1 breaks with /entry tag
    # bug. at first load, the dissolves don't show in monitor. but editing
    # first dissolve down to audio 1, seemed to work for all.
    elif process == 'preprocess':
        project = Project(datadir,kwargs['opp'])
        print("shifting...")
        project.shiftOverlap()
        af = audioFade(kdendir+'/tcom/audiofade.xml',kdendir+'/tcom/audiofilter.xml')
        di = Dissolve(kdendir+'/transitions/dissolve.xml')
        print("adding audio...")
        project.addAudioFilter(af)
        project.addAudioFade(af.audioFade)
        print("adding transitions...")
        project.addTransitions(di)
        project.saveProject()
        return
    
    # main option for building score clock
    # if using specified interval numbers give the begin and end intervals,
    # where the beginning is a stop interval (ie even, intervals
    # are zero-based numbering)
    elif process == 'makeclock':
        project = Project(datadir,kwargs['opp'])
        project.makeScoreBoard(kwargs['intervalNum'])
        project.createSummary()
        project.saveProject()
        pass

    return



if __name__=="__main__":
    
    #input_fn = sys.argv[1]
    filename = sys.argv[1]
    process = sys.argv[2] # makenumeral, preprocess, makeclock
    numeral= None
    interval=None
    cameraNumber=None
    kwargs={}
    if process == 'makenumeral':
        if len(sys.argv)==4:
            numeral = int(sys.argv[3])
            kwargs = dict(numeral=numeral)
    # %run -m tcom iceraiders_03feb18 makeclock SCR
    if process == 'makeclock':
        opp = sys.argv[3]
        kwargs = dict(opp=opp,intervalNum=None)
        if len(sys.argv)==6:
            # has to start on even
            intervalStart = int(sys.argv[4])
            intervalStop = int(sys.argv[5])
            kwargs['intervalNum']=range(intervalStart,intervalStop,2)
    if process == 'grabfootage':
        if len(sys.argv)==5:
            duration = int(sys.argv[3])
            cam = int(sys.argv[4])
            kwargs=dict(duration=duration,cameraNumber=cam)
    # %run -m tcom iceraiders_03feb18 preprocess SCR
    if process == 'preprocess':
        opp = sys.argv[3]
        kwargs=dict(opp=opp)
    print(kwargs)
    main(filename,process,**kwargs)

