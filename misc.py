import os
import re
import numpy as np

#########################
# miscellaneous classes
#######################

# intended to run in conjunction with a gameON stream instead of using bash ffmpeg command line directly
# not finished yet
class screenCapture():
    def __init__(self,duration,cameraNumber,outdir):
        self.duration = duration # seconds
        self.outdir = outdir
        self.cameraNumber = cameraNumber
        self.outputfile = outdir + "camera"+str(cameraNumber)+".mp4"
        self.inputfile = ''
        
    def runCapture(self):
        frames  = self.duration * 30
        # command = "ffmpeg -video_size 1920x1080 -framerate 29.97 -f x11grab -i :0.0+00,00 -frames 600 -preset ultrafast -pix_fmt yuv444p -qp 0 output.mp4"
        command = "ffmpeg -t "+str(self.duration)+" -video_size 1920x1080 -framerate 30 -f x11grab -i :0.0+00,00 -f alsa -ac 2 -i pulse  -frames "+str(frames)+" -preset ultrafast -pix_fmt yuv444p -crf 10 -vcodec libx264rgb -acodec aac "+self.outputfile
        if os.path.exists(self.outputfile):
            os.system("rm "+self.outputfile)
        os.system(command)

    def compressCapture(self):
        self.inputfile = self.outputfile
        self.outputfile = re.sub(r'(^.*[1-5])(.mp4)',r'\1_compressed\2',self.inputfile)
        command = "ffmpeg -i "+self.inputfile+" -framerate 30 -vcodec libx264 -crf 10 -acodec aac "+self.outputfile
        
        if os.path.exists(self.outputfile):
            os.system("rm "+self.outputfile)
        print(command)
        os.system(command)
        
# for generating fixed graphics of temporal numerals. run one-time only
class timeNumeral():
    # passing output directory like this is awkward 
    def __init__(self,outputdir,time=None):
        self.time = time # a time in seconds
        self.outdir = outputdir
        if self.time is not None:
            m = int(np.floor(self.time/60))
            s = int(time - m*60)
            self.timeMinSec = str(m).rjust(2,'0')+":"+str(s).rjust(2,'0')
        else:
            self.timeMinSec = None

    # set the minuates:seconds
    def setNumeral(self,value):
        self.timeMinSec = value

    def setTime(self,time):
        self.time = time

    # output a graphic
    def makeTimeGraphic(self):
        # original command
        # command = "convert -size 1920x1080 -pointsize 70 -fill red -channel RGBA -background transparent label:" + tstr + " "+outdir+"/t"+str(self.time)+".png"
        # new command
        command = "convert -size 122x68 -font DejaVu-Sans -pointsize 38 -fill white -channel RGBA xc:\"rgb(35,54,81)\" -annotate +7+47 '" + self.timeMinSec + "' -gaussian-blur 1x1 " +self.outdir+"/t"+str(self.time).rjust(3,'0')+".png"
        print(command)
        os.system(command)

    # create a complete set of time graphics
    def makeTimeGraphicAll(self):
        for m in range(0,17):
            for s in range(0,60):
                fstr = str(s+m*60).rjust(3,'0')
                tstr = str(m).rjust(2,'0')+":"+str(s).rjust(2,'0')
                # original command
                # command = "convert -size 1920x1080 -pointsize 70 -fill red -channel RGBA -background transparent label:" + tstr + " "+self.outdir+"/t"+fstr+".png"
                # new command
                command = "convert -size 122x68 -font DejaVu-Sans -pointsize 38 -fill white -channel RGBA xc:\"rgb(35,54,81)\" -annotate +7+47 '" + tstr + "' -gaussian-blur 1x1  " +self.outdir + "/t"+fstr + ".png"
                # print command
                os.system(command)

    # create a complete set of powerplay time graphics
    def makePPTimeGraphicAll(self):
        for m in range(0,5):
            for s in range(0,60):
                fstr = str(s+m*60).rjust(3,'0')
                tstr = str(m).rjust(2,'0')+":"+str(s).rjust(2,'0')
                command = "convert -size 122x68 -font DejaVu-Sans-Bold -pointsize 32 -fill white -channel RGBA xc:transparent -annotate +7+47 '" + tstr + "' -gaussian-blur 1x1  " +self.outdir + "/pp"+fstr + ".png"
                # print command
                os.system(command)

# a text string and an associated range of game time in seconds, to display it
# eg 3 seconds at start of game by default.
class Message():
    def __init__(self,msg,team=None,tstart=0,mtime=3,xoff=1125):
        self.Msg=msg
        self.team = team
        self.rTime=range(tstart,tstart+mtime,1) # run time of message in absolute game time
        self.mTime = mtime + 1 # for 1-based durations
        self.panelOffset = xoff

    def update(self):
        self.mTime -= 1
        if self.mTime<=0:
            self.Msg=None
            return None
        else:
            return self

# create a text string on a transparent background
class TextMessage():
    pass

# miscellanceous hard-coded values, edit accordingly
class Constants():
    def __init__(self,opp):
        self.pdur = 15 # period duration
        self.paneloffsets = {'NYK':1125,opp:1315,'none':1220} # x offset for displaying message tag under appropriate team
        self.res = '1280x720' # for low-res gameON. use '1920x1080' for camcorder

# convenience class of functions for creating game summary
# just an exercise in using a class __dict__ would be
# better as an ordinary dict.
# mostly working but not quite debugged
class printList:
    def __init__(self):
        self.printStr=''
    def fScoring(self,fTime,*args):
        printStr = " "+args[0]+" "+fTime+" "+"\n"
        return printStr
    def fPenalties(self,fTime,*args):
        (team,time) = re.search('([A-Z]{3})([0-9])',args[0]).group(1,2)
        printStr = " "+team+" "+fTime+" ("+str(time)+':00)\n'
        return printStr
    def fHighlights(self,fTime,*args):
        hTime = ''
        printStr = " "+hTime+" "+args[0]+"\n"
        return printStr
    # avoiding making a dictionary explicitly, avoiding variable
    # name introspection. note instance.__dict__ is not populated
    # until method calls are actually made on that instance so using
    # class.__dict__. thus also pass self explicitly
    def pFunc(self,command,t,*args):
        printStr = printList.__dict__.get('f'+command)(self,t,*args)
        return printStr
    
    def printList(self,file,pCommand,fList):
        psuffix=['st','nd','rd','th','th']
        pdur = 15 # hardcoded 15 minute period here
        period=0
        pstr=str(period+1)+psuffix[period]
        file.write('\n'+pCommand+'\n'+pstr+' Period\n')
        for fItem in fList:
            (m,s) = divmod(fItem[0],60)
            # TODO: this kludge broken by flood intermission. calculate period properly
            p = m//pdur
            if p>period:
                period=p
                pstr=str(period+1)+psuffix[period]
                file.write(pstr+' Period\n')
            msTime = str(np.mod(m,pdur))+':'+str(s).rjust(2,'0')
            printStr = self.pFunc(pCommand,msTime,fItem[1])
            file.write(printStr)
        
# use a kdenlive title page
class Title():
    def __init__(self,fname):
        self.title = open(fname).readlines()

    def __str__(self):
        return ''.join(self.title)

    def setText(self,ftext):
        cindex = [self.title.index(m) for m in iter(self.title) if re.search('templatetext',m)][0]
        # no backslash for < > on re.sub?
        self.title[cindex] = re.sub('>[a-zA-Z0-9\s\:\-]*<','>'+ftext+'<',self.title[cindex])

    def setOutIn(self,out,inn):
        self.title[0] = re.sub('out="[0-9]+','out="'+str(out),self.title[0])
        self.title[0] = re.sub('in="[0-9]+','in="'+str(inn),self.title[0])
        self.title[1] = re.sub('[0-9]{2,4}',str(out-inn+1),self.title[1])
        self.title[10] = re.sub('[0-9]{2,4}',str(out-inn+1),self.title[10])

    def setID(self,id):
        self.title[0] = re.sub('id="[0-9]{1,2}','id="'+str(id),self.title[0])

    def setFileHash(self):
        pass
        
class Transition():
    def __init__(self,**kwargs):
        self.Params = dict(**kwargs)
        self.transition = []

    def __str__(self):
        return ''.join(self.transition)
        
# for automatically inserting transitions in a kdenlive project from separate clips of each play action
# no longer needed in new mode of continuous clips
class Dissolve(Transition):
    def __init__(self,fname):
        self.transition=open(fname).readlines()

    def setTrack(self,a=3,b=4):
        aindex = [self.transition.index(m) for m in iter(self.transition) if re.search('a_track',m)]
        bindex = [self.transition.index(m) for m in iter(self.transition) if re.search('b_track',m)]
        
        self.transition[aindex] = re.sub('[0-9]',a,self.transition[aindex])
        self.transition[bindex] = re.sub('[0-9]',b,self.transition[bindex])

    def setID(self,id):
        
        self.transition[0] = re.sub('transition[0-9]{1,3}','transition'+str(id),self.transition[0])

    def setReverse(self,r=1):
        rindex = [self.transition.index(m) for m in iter(self.transition) if re.search('reverse',m)][0]
        self.transition[rindex] = re.sub('-{0,1}[0-9]',str(r),self.transition[rindex])

    def setOutIn(self,out,inn):
        self.transition[0] = re.sub('out="[0-9]+','out="'+str(out),self.transition[0])
        self.transition[0] = re.sub('in="[0-9]+','in="'+str(inn),self.transition[0])

# for automatically inserting transitions in a kdenlive project from separate clips of each play action
# no longer needed in new mode of continuous clips      
class audioFade(Transition):
    def __init__(self,fname_fade,fname_filter):
        self.audioFilter=open(fname_filter,'r').readlines()
        self.audioFade=open(fname_fade,'r').readlines()
        # WKP-25849

    def setFadeOut(self,out):
        m1 = [m for m in self.audioFilter if re.search('fadeout',m)]
        s1 = re.sub('out="[0-9]{1,4}','out="'+str(out),m1[0])
        s2 = re.sub('in="[0-9]{1,4}','in="'+str(out-15),s1)
        self.audioFilter[self.audioFilter.index(m1[0])] = s2
        
