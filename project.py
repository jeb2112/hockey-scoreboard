import os
import re
import itertools
import uuid
import numpy as np
from scoreboard import scoreBoard
from penalty import Penalty
from misc import Message,printList,Constants
import warnings

##################
# Project
##################
        
class Project():
    def __init__(self, projectdir,opp):
        self.projectdir = projectdir 
        self.projectname = os.path.split(self.projectdir)[1]+".kdenlive"
        self.project = open(os.path.join(self.projectdir,self.projectname),'r').readlines()
        self.srcdir = '/home/src/tcom'
        self.Tags = dict(goals=[],scorers=[],penalties=[],highlights=[])
        self.framerate = 25 # hard-coded but should get from kdenlive project file
        # times and powerplay attributes should be in scoreboard?
        self.currentTime = 0 # ie game/clock time
        self.trueTime = 0 # video time, including all delays etc
        self.pdur = 15 # hard-coded period duration
        self.res = '1280x720' # for low-res gameON. use '1920x1080' for camcorder
        self.opp = opp
        self.team = 'NYK' # hard-coded
        self.C = Constants(self.opp)
        self.SB = scoreBoard(self.team,self.opp,self.srcdir,self.projectdir,self.C)
        self.P = Penalty(self.team,self.opp,self.C)
        self.M = [] # optional list of highlight messages
        self.w = self.parseGuides("w")
        self.f = self.parseGuides("f")
        self.Tags['Scoring'] = self.parseGuides('goal:')
        self.Tags['Penalties'] = self.parseGuides('penalty:')
        self.Tags['Highlights'] = self.parseGuides('highlight:')
        self.goals = self.Tags['Scoring']
        self.scorers = {}
        self.penalties = self.Tags['Penalties']
        self.highlights = self.Tags['Highlights']

    def makeScoreBoard(self,intervalNum=None):
        # optional IntervalNum list of intervals to process, list is
        # even/stop intervals
        cwd = os.getcwd()

        commandR1 = "ffmpeg -r 1 -s " + self.res + " " # root of a run interval command
        command2 = "-vcodec png -pix_fmt rgba " 

        pIndex,gIndex,hIndex = 0,0,0
        
        # combine all whistles and faceoffs into a single list
        # includes dummy whistle at time 0, ie first interval is a stop interval
        # dummy faceoff at time end, so last interval also a stop.  
        w = [i for p in zip(self.w,self.f) for i in p] 
        nInterval = len(w)-1 
        if intervalNum == None:
            intervalNum = range(0,nInterval,2)
        else: # can be provided as arg to rebuild only a few intervals quickly
            if not hasattr(intervalNum,'__iter__'):
                intervalNum = [intervalNum]
        self.currentTime=0 # game clock time
        self.trueTime = w[0][0] # video time. assumes a dummy tag present at time 0

        # process in pairs of stop/run intervals
        for i in range(0,nInterval,2):
            trunfile = os.path.join('trun',"trun"+str(i).rjust(2,'0')+".mp4")
            
            # process stop interval first
            # only build the scoreboard graphics for requested intervals
            if i in intervalNum:
                doboard = trunfile
                if os.path.exists(trunfile):
                    os.system("rm "+trunfile)
            else:
                doboard = False
            tstop = (w[i+1][0]-w[i][0])
            # check for goal in current stop interval.
            # goal markers should be only flagged in a stop interval
            if gIndex < len(self.goals):
                gIndex,SM = self.checkGoal(tstop,gIndex)
            # check for start of a new powerplay, must be flagged in a stop interval
            if pIndex < len(self.penalties):
                pIndex = self.checkPenalty(tstop,pIndex)

            # build the individual per-second clock graphics
            self.SB.writeTimeFrames(tstop,0,self.currentTime,self.P,SM,self.M,doboard)

            c = commandR1
            c = c + '-start_number ' +str(0) + ' -i ' + os.path.join(self.projectdir,'trun','tpng','ts%03d.png') + ' -vframes ' + str(tstop) + ' '
            c = c + command2 + trunfile + ' 2> /dev/null'

            self.trueTime += tstop
            # only run command if a requested interval
            if i in intervalNum:
                print(c)
                os.system(c)

            # run interval. there is one less run interval than stop interval, check here
            if i < nInterval-1:
                trunfile = os.path.join('trun','trun'+str(i+1).rjust(2,'0')+'.mp4')

                if 'period' in w[i][1]:
                    self.updatePeriod(w[i])
                if i in intervalNum:
                    if os.path.exists(trunfile):
                        os.system("rm "+trunfile)
                trun = (w[i+2][0]-w[i+1][0])

                # check for highlight message. will only be flagged in a
                # run interval by convention.
                if hIndex < len(self.highlights):
                    hIndex = self.checkHighlight(trun,hIndex)

                # build the individual per-second clock graphics
                # TODO: resolve score message, highlight messages into one arg
                self.SB.writeTimeFrames(trun,1,self.currentTime,self.P,SM,self.M,doboard)

                c = commandR1
                c = c + '-start_number ' +str(self.currentTime) + ' -i ' + os.path.join(self.projectdir,'trun','tpng','t%03d.png') + ' -vframes ' + str(trun) + ' '
                c = c + command2 + trunfile + ' 2> /dev/null'
                self.currentTime += trun
                self.trueTime += trun
                if i in intervalNum:
                    print(c)
                    os.system(c)

        print("Done time frames")
        os.chdir(cwd)


    # convenience methods

    def updatePeriod(self,w):
        self.currentTime=0
        if 'period2' in w[1]:
            self.SB.incrementPeriod("2ND")
        elif 'period3' in w[1]:
            self.SB.incrementPeriod("3RD")
        
    def checkPenalty(self,tstop,idx):
        if np.searchsorted([self.trueTime,self.trueTime+tstop],self.penalties[idx][0])==1:
        # time in min is suffix of the text
            self.P.add(self.penalties[idx][1],self.currentTime)
            self.penalties[idx][0] = self.currentTime + (self.SB.period-1)*self.C.pdur*60
            idx += 1
        return idx

    def checkGoal(self,tstop,idx):
        if np.searchsorted([self.trueTime,self.trueTime+tstop],self.goals[idx][0])==1:
            # scorer name to be indicated in goal tag eg 'goal: jim bob #11'
            # and is parsed here. 
            SM = None
            try:
                scoreTeam,scoreMessage = re.search('^([A-Z]{2,4})\s(.*)$',self.goals[idx][1]).group(1,2)
                SM = Message(scoreMessage,mtime=3,xoff=self.C.paneloffsets[scoreTeam])
                self.goals[idx][1] = scoreTeam
            except AttributeError:
                SM = None
            self.SB.incrementScore(self.goals[idx][1])
            # pdur period hard-coded above, make an input arg
            # convert goal time from true time to game time
            self.goals[idx][0] = self.currentTime + (self.SB.period-1)*self.C.pdur*60
            # if powerplay goal, remove penalty
            if self.P.PP:
                self.P.remove(self.getOtherTeam(self.goals[idx][1]))
            idx += 1
            return idx,SM
        else:
            return idx,None   

    # messages other than goals or penalties.
    def checkHighlight(self,trun,idx):
        while idx < len(self.highlights):
            if np.searchsorted([self.trueTime,self.trueTime+trun],self.highlights[idx][0])==1:
                try:
                    team,message = re.search('^([A-Z]{2,4})\s(.*)$',self.highlights[idx][1]).group(1,2)
                except AttributeError:
                    team='none'
                    message=None
                # offset into current run interval
                toff = self.highlights[idx][0] - self.trueTime
                # absolute game time
                gtime = self.currentTime + (self.SB.period-1)*self.C.pdur*60
                gtime_hl = toff + gtime
                self.M.append(Message(message,tstart=gtime_hl,mtime=3,team=team,xoff=self.C.paneloffsets[team]))
                # also record clock time for later summary
                self.highlights[idx][0] = gtime
                idx += 1
            else:
                break
        return idx #,SM
            
    # new xml project format in kdenilve 22.08
    def parseGuides(self,ftext):
        guideTimes=[]
        gflag = False # indicates we are in the Guides property of the .xml file
        I=self.project.__iter__()
        for m in I:
            if gflag:
                if re.search('\/property',m): # closing tag for the guides property
                    break
                # read the guide comment
                s=re.match('^.*comment\"\:\s\"([A-Za-z0-9\s\:\#\-\']*)',m)
                if s and s.group(1).startswith(ftext): # startswith allows for extra text in the tag but this is sloppy
                    # escape single quote if any
                    # can no longer remember all the different thoughts that occurred to work this out
                    # extra escapes are required to run a convert command via the python os.system
                    # convert processes raw strings just like python, but decided to avoid that complication
                    # and try to get it to go without raw stings
                    # in the end, what's written here doesn't match the interactive python command i 
                    # was using in python shell to work out the os.system convert command in scoreboard.py
                    # but the graphic was still correct.
                    sgroup1 = re.sub('\'','\\\\\\\\\'',s.group(1))
                    # remove the : if any
                    sgroup1=re.sub('^.*\:\s','',sgroup1)
                    # if 'penalty' in ftext:
                    # replace opp with actual opponent's text
                    sgroup1 = re.sub('opp|OPP',self.opp,sgroup1)
                    # read frame position from the next line
                    m = I.__next__()
                    s2 = re.match('^.*pos\"\:\s([0-9]{1,6})\,',m)
                    if s2 is None:
                        warnings.warn('Failed to match frame pos for guide {}'.format(s.group(1)))
                        return
                    guideTimes.append([int(round(float(s2.group(1))/self.framerate)),sgroup1])
            elif not re.search('guides',m):
                continue
            else:
                gflag = True # now in the guides property of the project file

        guideTimes = sorted(guideTimes, key=lambda x: x[0])
        return guideTimes 

    def saveProject(self,fname=None):
        if fname==None:
            if os.path.isfile(self.projectname):
                UID = uuid.uuid4()
                os.system("mv "+self.projectname+" "+self.projectname+".backup."+str(UID))
            file = open(self.projectname,'w')
        else:
            if os.path.isfile(self.projectname):
                print("Project already exists")
                return
            file = open(fname,'w')
        file.writelines(self.project)

    # create a short file of goals penalties and highlight comments.
    # add pp or sh for scoring, name
    # not finished or debugged fully
    def createSummary(self,fname=None):
        if fname==None:
            fname = str.split(self.projectname,'.')[0]+".summary"
        else:
            fname = str.split(self.projectname,'.')[0]+fname
            
        file = open(fname,'w')

        # itemDict = dict(Scoring=self.goals,Penalties=self.penalties,Highlights=self.highlights)
        PL=printList()
        for fKey in ['Scoring','Penalties','Highlights']:
            if self.Tags[fKey]:
                PL.printList(file,fKey,self.Tags[fKey])
        file.close()

    # convenience method
    def getOtherTeam(self,team):
        if team==self.team:
            return self.opp
        else:
            return self.team