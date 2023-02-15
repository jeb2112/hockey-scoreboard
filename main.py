import sys
import os
import numpy as np
from misc import *
from project import Project

###############
# main
##############

# 1. load clips on video 1, then alternate every 2nd clip onto video 2. load the title page at the start of video2
# 2. run preprocess to overlap the raw clips.
# 3. tag the timeline. goal: DMM|opp scorername number. during stop interval
#                      penalty: DMM2|opp4. during stop interval
#                      Guide: period2 on both ends of the stop interval
# 4. run makeclock to make the time clips trun??.mp4 in the project dir
# 5. load time clips into project on video 3
# 6. render at crf=17

def main(fname,process,**kwargs):

    import numpy as np
    print("main")
    cwd = os.getcwd()
    kdendir = "/home/jbishop/kdenlive/"
    outdir = kdendir+fname+"/"
    workdir = kdendir+fname+"/"
    clipdir = "/media/jbishop/Data/video/"+fname+"/"
    if not os.path.isdir(workdir):
        os.mkdir(workdir)
    else:
        print("Project already exists")
        # return
    os.chdir(workdir)


    if process == 'makenumeral':
        tN=timeNumeral(0,'/home/jbishop/kdenlive/tcom/tpng/')
        # if numeral == None:
        tN.makeTimeAll(kdendir+'/tcom/tpng/')
        #else:
        #    timeNumeral.makeTimeNumeral(numeral)
    elif process == 'grabfootage':
        duration=kwargs['duration']
        cameraNumber=kwargs['cameraNumber']
        print(duration,cameraNumber)
        sc = tcom.screenCapture(3000,2,'/media/jbishop/Data/video/tmpproj')
        sc=screenCapture()
        sc.runCapture()

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
        project = Project(fname,kwargs['opp'])
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
    # if using interval numbers give the begin end intervals,
    # where the beginning is a stop interval (ie even, intervals
    # are zero-based numbering)
    # %run -m tcom 'iceraiders_03feb18 makeclock' 8 11
    # pdb.runcall(tcom.main,'iceraiders_03feb18','makeclock',**dict(opp='SCR',intervalNum=range(10,11)))
    elif process == 'makeclock':
        project = Project(fname,kwargs['opp'])
        # project.guides = project.parseGuides("Guide")
        # project.goals = project.parseGuides("goal:")
        # project.penalty = project.parseGuides("penalty:")
        # project.scorers = project.parseGuides("scorer:")
        # project.highlights = project.parseGuides("highlight:")
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

