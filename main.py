import sys
import os
from misc import *
from project import Project

######
# main
######

# input clips. multiple cams each with one continuous clip entire game.
# directory structure. all fixed sub-component graphics are now in repo in the source directory.
# all dynamically assembled interim sub-graphics go into trun/tpng dir of the project working directory
# 1. load clips on video channels 1,2,3 etc. align clips by the audio.
# 2. tag the timeline with 'w','f' for each start/stoppage including periods goals and penalties. include period2,3 in 'w' tag for period-ending whistle
# 2a. tag a dummy 'w' at time 0, and a dummy 'f' at time end.
# 3. tag goals and penalties separately during stoppage in between a 'w','f' pair. 
# 4. run makeclock to make the time clips trun ??.mp4 in the project dir
# 5. load time clips into project on video 4
# 6. render at crf=17

def main(datadir,process,**kwargs):

    print("main")
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
    print(kwargs)
    main(filename,process,**kwargs)

