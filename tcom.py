import sys
import math
import os
import io
import re
import itertools
import uuid
import numpy as np

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
        print command
        os.system(command)
        
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
    def setNumeral(value):
        self.timeMinSec = value

    def setTime(time):
        self.time = time

    # output a graphic
    def makeTimeGraphic(self):
        # original command
        # command = "convert -size 1920x1080 -pointsize 70 -fill red -channel RGBA -background transparent label:" + tstr + " "+outdir+"/t"+str(self.time)+".png"
        # new command
        command = "convert -size 122x68 -font DejaVu-Sans -pointsize 38 -fill white -channel RGBA xc:\"rgb(35,54,81)\" -annotate +7+47 '" + self.timeMinSec + "' -gaussian-blur 1x1 " +self.outdir+"/t"+str(self.time).rjust(3,'0')+".png"
        print command
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
        
# for tidying up the system commands    
class ffParams():
    def __init__(self,**kwargs):
        pass


######################
# scoreBoard
#####################

class scoreBoard():
    def __init__(self,opp):
        self.dmScore = 0
        self.opp = opp
        self.oppScore = 0
        self.period = 1
        self.wdir = "/home/jbishop/kdenlive/logo/"
        self.pwd = os.getcwd()
        self.makeStaticBoard()
        
    def makeStaticBoard(self):
        os.chdir(self.wdir)
        # place static box4 and timegraphic
        # note spaces at brackets.
        # note a space after the line break backslash gets interpreted
        # as an extra newline which breaks the string
        c4 = """convert -size 1920x1080 xc:transparent \
        \( box4.png -resize 50% -repage +1508+18 \) \
        \( 1ST.png -resize 50% -repage +1511+21 \) \
        \( box3.png -resize 50% -repage +1320+18 \) \
        \( 0.png -resize 50% -repage +1324+21 \) \
        \( DMM_68x34.png -repage +1133+21 \) \
        \( DMM.png -resize 50% -repage +1203+21 \) \
        \( box2.png -resize 50% -repage +1130+18 \) \
        \( 0.png -resize 50% -repage +1266+21 \) \
        \( """+self.opp+""".png -resize 50% -repage +1374+21 \) \
        \( """+self.opp+"""_68x34.png -repage +1436+21 \) \
        \( box1.png -resize 50% -repage +1078+18 \) \
        \( gthl_92x68.png -resize 50% -repage +1081+21 \) \
        -background transparent -flatten ../tcom/tpng2/staticBoard.png"""
        os.system(c4)
        c4 = "cp ../tcom/tpng2/staticBoard.png ../tcom/tpng2/staticScoreBoard.png"
        os.system(c4)
        os.chdir(self.pwd)

    # increments staticScoreBoard assuming a goal is not scored at 0:00
    def incrementScore(self,team):
        os.chdir(self.wdir)
        # change score
        if team.startswith("DMM"):
            self.dmScore += 1
        # note previously hard-coded lower case opp. 
        # changing parseGuide to sub actual opponent text from Project.opp
        # attribute
        # elif team == "opp":
        elif team == self.opp:
            self.oppScore +=1 
        kdendir = "/home/jbishop/kdenlive/"
        c3 = "convert " + self.wdir + "../tcom/tpng2/staticScoreBoard.png \
        \( "+str(self.dmScore)+".png -resize 50% -repage +1266+21 \) \
        \( "+str(self.oppScore)+".png -resize 50% -repage +1324+21 \) \
        -background transparent -flatten "+self.wdir+"../tcom/tpng2/staticScoreBoard.png"
        os.system(c3)
        os.chdir(self.pwd)

    def incrementPeriod(self,periodPanel):
        os.chdir(self.wdir)
        self.period += 1
        c3 = "convert " + self.wdir + "../tcom/tpng2/staticScoreBoard.png \
        \( "+periodPanel+".png -resize 50% -repage +1511+21 \) \
        -background transparent -flatten "+self.wdir+"../tcom/tpng2/staticScoreBoard.png"
        os.system(c3)
        os.chdir(self.pwd)

    # write a single time frame clock
    def addBoardTime(self,time):
        os.chdir(self.wdir)
        c2 = "convert " + self.wdir + "../tcom/tpng2/staticScoreBoard.png \
        \( ../tcom/tpng2/t"+str(time).rjust(3,'0')+".png -resize 50% -repage +1554+21 \) \
        -background transparent -flatten "+ self.wdir+ "../tcom/t"+str(time).rjust(3,'0')+".png"
        os.system(c2)
        os.chdir(self.pwd)

    # write a single time frame clock, with power play clock
    # should call from addBOardTime instead of duplicating
    # new version for penalty class
    def addBoardTimePPNew(self,time,penalty):
        # print "addBoardTime: ",time
        os.chdir(self.wdir)
        if penalty.PPTeam == "DMM":
            panelOffset = 1125
        elif penalty.penaltyTeam == "DMM":
            panelOffset = 1315
        if penalty.panelPrefix == '4on4':
            panelOffset = 1220 # 4on4 case
        c2 = "convert " + self.wdir + "../tcom/tpng2/staticScoreBoard.png \
        \( ../tcom/tpng2/t"+str(time).rjust(3,'0')+".png -resize 50% -repage +1554+21 \) \
        \( "+penalty.panelPrefix+penalty.PPTeam+".png -resize 37% -repage +"+str(panelOffset)+"+59 \) \
        \( ../tcom/tpng2/pp"+str(penalty.pTime[penalty.penaltyTeam][0]).rjust(3,'0')+".png -resize 50% -repage +"+str(panelOffset+120)+"+54 \) \
        -background transparent -flatten "+ self.wdir+ "../tcom/t"+str(time).rjust(3,'0')+".png"
        os.system(c2)
        os.chdir(self.pwd)

    # write a single time frame clock, with power play clock
    # should call from addBOardTime instead of duplicating
    def addBoardTimePP(self,time,ppTeam=None,ppTime=None):
        os.chdir(self.wdir)
        if ppTeam == "DMM":
            panelOffset = 1125
        else:
            panelOffset = 1315
            ppTeam = self.opp
        c2 = "convert " + self.wdir + "../tcom/tpng2/staticScoreBoard.png \
        \( ../tcom/tpng2/t"+str(time).rjust(3,'0')+".png -resize 50% -repage +1554+21 \) \
        \( pp"+ppTeam+".png -resize 37% -repage +"+str(panelOffset)+"+59 \) \
        \( ../tcom/tpng2/pp"+str(ppTime).rjust(3,'0')+".png -resize 50% -repage +"+str(panelOffset+120)+"+54 \) \
        -background transparent -flatten "+ self.wdir+ "../tcom/t"+str(time).rjust(3,'0')+".png"
        os.system(c2)
        os.chdir(self.pwd)

    # replacement to handle both penalty and regular
    # need to use for stop interval as well
    def buildBoard(self,time,penalty=None,scoreMessage=None):
        os.chdir(self.wdir)
        c2 = "convert " + self.wdir + "../tcom/tpng2/staticScoreBoard.png \
        \( ../tcom/tpng2/t"+str(time).rjust(3,'0')+".png -resize 50% -repage +1554+21 \) "
        if penalty is not None:
            if penalty.PP:
                c2 += " \( "+penalty.panelPrefix+penalty.PPTeam+".png -resize 37% -repage +"+str(penalty.panelOffset)+"+59 \) \
                \( ../tcom/tpng2/pp"+str(penalty.pTime[penalty.penaltyTeam][0]).rjust(3,'0')+".png -resize 50% -repage +"+str(penalty.panelOffset+120)+"+54 \) "
        # need a check for this to override a penalty panel
        if scoreMessage is not None:
            if scoreMessage.mTime:
                c1 = "convert scorePanel.png -fill white \
            -pointsize 46 -annotate +40+50 \'" + scoreMessage.Msg + "\' \
            -blur 0x1 scorePanelAnno.png"
                os.system(c1)
                c2 += " \( scorePanelAnno.png -resize 37% -repage +1125+59 \) "
        c2 += " -background transparent -flatten "+ self.wdir+ "../tcom/t"+str(time).rjust(3,'0')+".png"
        os.system(c2)
        os.chdir(self.pwd)


    # for run interval
    def writeTimeFrames(self,trun,currentTime,penalty,scoreMessage=None):
        for t in range(currentTime,currentTime+trun):
            if penalty.PP:
                penalty.update()
            self.buildBoard(t,penalty,scoreMessage)
            if scoreMessage is not None:
                if scoreMessage.Msg is not None:
                    scoreMessage.update()


class Message():
    def __init__(self,msg,time):
        self.Msg=msg
        self.mTime=time

    def update(self):
        self.mTime -= 1
        if self.mTime==0:
            self.Msg=None
        
###############
# Penalty
###############

class Penalty():
    def __init__(self,opp):
        self.pTime = {'DMM':[],opp:[]}
        self.PP=False
        # these two variables have not much use
        self.PPTeam=None
        self.penaltyTeam=None 
        self.nP = {'DMM':0,opp:0}
        self.panelPrefix = "pp"
        self.opp = opp
        self.panelOffset = 1125
        # self.pState = dict(PPflag=None,PPTeam=None,PenaltyTeam=None,panelPrefix=None)
        
    # guide text =  DMM2 for 2 min penalty
    def add(self,teamtime,currentTime):
        (team,time) = re.search('([A-Z]{3,4})([0-9])',teamtime).group(1,2)
        self.pTime[team].append(int(time)*60)
        self.nP[team] += 1
        self.PP=True
        self.updateState()

    def remove(self,team):
        if self.nP[team]:
            self.pTime[team].pop(0)
            self.nP[team] -= 1
            self.PP = any(self.pTime.values())
            self.updateState()

    # reduce penalty time by one second
    def update(self):
        for team in self.pTime.keys():
            for i,v in enumerate(self.pTime[team]):
                self.pTime[team][i] -= 1
                if self.pTime[team][0] == 0:
                    self.pTime[team].pop(0)
                    if self.nP[team]:
                        self.nP[team] -= 1
        self.PP = any(self.pTime.values())

        self.updateState()

    def updateState(self):
        if self.nP['DMM'] > self.nP[self.opp]:
            self.penaltyTeam = 'DMM'
            self.PPTeam=self.opp
            self.panelOffset = 1315
        elif self.nP[self.opp] > self.nP['DMM']:
            self.penaltyTeam = self.opp
            self.PPTeam='DMM'
            self.panelOffset = 1125
        elif self.nP[self.opp] == self.nP['DMM']:
            self.PPTeam='DMM'
            self.penaltyTeam=self.opp
            self.panelOffset = 1220 # 4on4 case. 

        if self.nP['DMM'] + self.nP[self.opp] == 1:
            self.panelPrefix = "pp"
        elif self.nP['DMM']*self.nP[self.opp] == 1:
            self.panelPrefix = "4on4"
        elif np.abs(self.nP['DMM'] - self.nP[self.opp]) == 2:
            self.panelPrefix = "5on3"
        elif self.nP['DMM'] + self.nP[self.opp] == 3:
            self.panelPrefix = "4on3"

            
##################
# Project
##################
        
class Project():
    def __init__(self, projectfilename,opp):
        self.projectdir = projectfilename
        self.projectname = projectfilename+".kdenlive"
        self.project = open(self.projectname,'r').readlines()
        self.Tags = dict(goals=[],scorers=[],penalties=[],highlights=[])
        self.playlists = ['playlist3','playlist4']
        self.transitionList = self.parseTransitions() # existing transition numbers
        self.producerIDList = self.parseProducerIDs() # existing producers id
        self.framerate = 29.97
        # times and powerplay attributes should be in scoreboard?
        self.currentTime = 0
        self.trueTime = 0
        self.opp = opp
        self.SB = scoreBoard(opp)
        self.P = Penalty(opp)
        self.guides = self.parseGuides("Guide")
        self.Tags['Scoring'] = self.parseGuides('goal:')
        self.Tags['Penalties'] = self.parseGuides('penalty:')
        self.Tags['Highlights'] = self.parseGuides('highlight:')
        self.goals = self.Tags['Scoring']
        self.scorers = {}
        self.penalties = self.Tags['Penalties']
        self.highlights = self.Tags['Highlights']

    # bug: use of intervalNum starting > 0 doesn't process penalties correctly
    # eg leaside 09jan18 trun 42,43
    def makeScoreBoard(self,intervalNum=None):
        # optional IntervalNum list of intervals to process, list is
        # even/stop intervals
        cwd = os.getcwd()
        kdendir = "/home/jbishop/kdenlive/"
        os.chdir(kdendir+self.projectdir)

        commandS1 = "ffmpeg -loop 1 -s 1920x1080 "
        commandR1 = "ffmpeg -r 1 -s 1920x1080 "
        command2 = "-vcodec png -pix_fmt rgba " 

        # should these be self. attributes.
        scorerMessage=None
        scorerMessageTime=0
        pIndex,gIndex,hIndex = 0,0,0
        
        w=self.guides # should be even for odd number of intervals
        nInterval = len(w)-1 # intervals start and end with stopped clock
        if intervalNum == None:
            intervalNum = range(0,nInterval+1,2)
        else:
            if not hasattr(intervalNum,'__iter__'):
                intervalNum = [intervalNum]
        self.currentTime=0 # game clock time
        self.trueTime = w[0][0] # video time
        for i in range(0,nInterval+1,2):
            trunfile = "trun"+str(i).rjust(2,'0')+".mp4"
            # process stop interval
            # goal markers should be in a stop interval
            if i in intervalNum:
                if os.path.exists(trunfile):
                    os.system("rm "+trunfile)
            tstop = (w[i+1][0]-w[i][0])
            # check for goal in current stop interval. goals are flagged in stops.
            if gIndex < len(self.goals):
                gIndex,SM = self.checkGoal(tstop,gIndex)
            # check for start of a new powerplay, must be flagged in a stop interval
            if pIndex < len(self.penalties):
                pIndex = self.checkPenalty(tstop,pIndex)
            # need to merge addBoardTime into one function
            if self.P.PP:
                self.SB.addBoardTimePPNew(self.currentTime,self.P)
            else:
                self.SB.addBoardTime(self.currentTime)

            c = commandS1
            c = c + " -t "+str(tstop)+" -i ../tcom/t"+str(self.currentTime).rjust(3,'0')+".png "+ command2 + "trun"+str(i).rjust(2,'0') +".mp4 2> /dev/null"
            self.trueTime += tstop
            if i in intervalNum:
                print c
                os.system(c)

            # run interval
            if i < nInterval-2:
                if 'period' in w[i][1]:
                    self.updatePeriod(w[i])
                trunfile = "trun"+str(i+1).rjust(2,'0')+".mp4"
                if i in intervalNum:
                    if os.path.exists(trunfile):
                        os.system("rm "+trunfile)
                trun = (w[i+2][0]-w[i+1][0])
                # check for scorer message. will be flagged in a
                # run interval by convention.


                # converting this to process scorer from Tags['goals']
                # score message now created in checkGoal
                # ultimately should play for 3 seconds starting 1sec
                # into the stop interval
                    

                if self.scorers:
                    if np.searchsorted([self.trueTime,self.trueTime+trun],self.scorers[0][0])==1:
                        SM = Message(self.scorers[0][1],3)
                        self.scorers.pop(0)
                    else:
                        SM=None
                # check for highlight message. will be flagged in a
                # run interval by convention.
                if hIndex < len(self.highlights):
                    hIndex = checkHighlight(trun,hIndex)
                if i in intervalNum:
                    self.SB.writeTimeFrames(trun,self.currentTime,self.P,SM)
                c = commandR1
                c = c + "-start_number " +str(self.currentTime) + " -i ../tcom/t%03d.png -vframes "+ str(trun) + " "
                c = c + command2 + "trun"+str(i+1).rjust(2,'0') +".mp4 2> /dev/null"
                self.currentTime += trun
                self.trueTime += trun
                if i in intervalNum:
                    print c
                    os.system(c)

        print "Done time frames"
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
            self.penalties[idx][0] = self.currentTime + (self.SB.period-1)*12*60
            idx += 1
        return idx

    def checkGoal(self,tstop,idx):
        if np.searchsorted([self.trueTime,self.trueTime+tstop],self.goals[idx][0])==1:
            # scorer name has been moved from self.scorers to to self.goals
            # and is parsed here. this should leave only the team name in
            # self.goals[][1]. not working yet.
            # the goals do tally correctly though.
            # and to move goals,penalties into one dict
            try:
                scoreTeam,scoreMessage = re.search('^([A-Z]{2,4})\s(.*)$',self.goals[idx][1]).group(1,2)
                SM = Message(scoreMessage,3)
                self.goals[idx][1] = scoreTeam
            except AttributeError:
                SM = None
            self.SB.incrementScore(self.goals[idx][1])
            # 12 minute period hard-coded here. make function for this
            # convert goal time from true time to game time
            self.goals[idx][0] = self.currentTime + (self.SB.period-1)*12*60
            # if powerplay goal, remove penalty
            # logic for short-handed goal?
            if self.P.PP:
                self.P.remove(self.getOtherTeam(self.goals[idx][1]))
            idx += 1
            return idx,SM
        else:
            return idx,None   

    def checkHighlight(self,trun,idx):
        if np.searchsorted([self.trueTime,self.trueTime+trun],self.highlights[idx][0])==1:
            self.highlights[idx][0] = self.currentTime + (self.SB.period-1)*12*60
            idx += 1
        return idx,SM

    # by default video 2 playlist 4 will get the dissolve transitions
    # find the start and end of all blanks in video 2 playlist 4
    # probably rename parseBlanks
    def parseOverlaps(self):
        for p in self.playlists: # currently just processing playlist4
            blankEnd=[]
            blankStart=[]
            self.currentTime = 1
            pindex = [self.project.index(m) for m in iter(self.project) if re.search('playlist id\=\"'+p+'\"\>$',m)][0]
            I=itertools.islice(self.project.__iter__(),pindex,len(self.project))
            for m2 in I:
                if not re.search('^\s*\<\/playlist\>',m2):
                    s2 = re.search('blank length\=\"([0-9]{1,5})',m2)
                    if s2:
                        blankStart.append(self.currentTime)
                        self.currentTime += int(s2.group(1)) + 1
                        blankEnd.append(self.currentTime)
                        continue
                    s2 = re.search('\<entry out\=\"([0-9]{1,5})\" producer=\"[0-9]{1,2}',m2)
                    if s2:
                        self.currentTime += int(s2.group(1)) + 0
                        continue
                else:
                    break

        return (blankStart,blankEnd)

    # return Blanks from a particular playlist
    def parseBlanks(self,playlist):
        blankEnd=[]
        blankStart=[]
        self.currentTime = 1
        pindex = [self.project.index(m) for m in iter(self.project) if re.search('playlist id\=\"'+playlist+'\"\>$',m)][0]
        I=itertools.islice(self.project.__iter__(),pindex,len(self.project))
        for m2 in I:
            if not re.search('^\s*\<\/playlist\>',m2):
                s2 = re.search('blank length\=\"([0-9]{1,5})',m2)
                if s2:
                    blankStart.append(self.currentTime)
                    self.currentTime += int(s2.group(1)) + 1
                    blankEnd.append(self.currentTime)
                    continue
                s2 = re.search('\<entry out\=\"([0-9]{1,5})\" producer=\"[0-9]{1,2}',m2)
                if s2:
                    self.currentTime += int(s2.group(1)) + 0
                    continue
            else:
                break

        return (blankStart,blankEnd)

    def parseTransitions(self):
        transitionList=[]
        I=self.project.__iter__()
        for m in I:
            s=re.search('transition id\=\"transition([0-9]{1,3})',m)
            if s:
                # print m
                transitionList.append(int(s.group(1)))
        # transitionList = sorted(transitionList, key=lambda x: x[0])
        # print transitionList
        return transitionList

    def parseProducerIDs(self):
        IDList=[]
        I=self.project.__iter__()
        for m in I:
            s=re.search('producer id\=\"([0-9]{1,2})\"',m)
            if s:
                # print m
                IDList.append(int(s.group(1)))
        IDList.sort()
        return IDList

    def parseList(self,retext):
        fList=[]
        I=self.project.__iter__()
        for m in I:
            s=re.search(retext,m)
            if s:
                # print m
                fList.append(int(s.group(1)))
        return fList
        
    # bug: need to check for accidental duplicate tags here
    def parseGuides(self,ftext):
        guideTimes=[]
        I=self.project.__iter__()
        for m in I:
            if re.search('xml_retain',m):
                break
            if re.search('guide',m):
                m = re.sub(',','',m)
            s=re.match('^.*guide\.([0-9]{1,5}\.?[0-9]{0,5})\"\>([A-Za-z0-9\s\:\#\-]*)',m)
            if s and ftext in s.group(2):
                # remove keyword : if any
                sgroup2=re.sub('^.*\:\s','',s.group(2))
                # if 'penalty' in ftext:
                # replace opp with actual opponent's text
                sgroup2 = re.sub('opp|OPP',self.opp,sgroup2)
                guideTimes.append([int(round(float(s.group(1)))),sgroup2])
        guideTimes = sorted(guideTimes, key=lambda x: x[0])
        return guideTimes 

    def shiftOverlap(self):
        startShift=0
        shiftInc=24
        for p in self.playlists:
            startShift+=12
            currentShift=startShift
            s1=[m for m in iter(self.project) if re.search('playlist id\=\"'+p+'\"\>$',m)]
#            if p=='playlist3': # skip first blank
#                I = itertools.islice(self.project.__iter__(),self.project.index(s1[0]),len(self.project))
            I=itertools.islice(self.project.__iter__(),self.project.index(s1[0]),len(self.project))
            for m2 in I:
                # print m2
                if not re.search('^\s*\<\/playlist\>',m2):
                    s2 = re.search('blank length\=\"([0-9]{1,4})',m2)
                    if s2:
                        s2 = re.sub('[0-9]{1,4}',str(int(s2.group(1))-currentShift),m2,count=1)
                        self.project[self.project.index(m2)] = s2
                        if currentShift == 12:
                            currentShift = 24
                        continue
                    s2 = re.search('\<entry out\=\"([0-9]{1,4})\" producer=\"[0-9]{1,2}\_',m2)
                    if s2:
                        s2 = re.sub('[0-9]{1,4}',str(int(s2.group(1))-currentShift),m2,count=1)
                        #self.project[self.project.index(m2)] = s2               
                        #currentShift += 5
                        continue
                else:
                    break
                        
    def addAudioFade(self,af):
        m1=[m for m in iter(self.project) if re.match('^\s\<playlist id\=\"main bin',m)][0] # extract list to string
        I2=itertools.islice(self.project.__iter__(),self.project.index(m1),len(self.project))
        for m2 in I2:
            if re.search('^\s*\<\/playlist\>',m2):
                break
        self.project[self.project.index(m2):self.project.index(m2)] = af

    def addAudioFilter(self,af):
        for p in self.playlists:
            m1=[m for m in iter(self.project) if re.match('^\s\<playlist id\=\"'+p+'\"\>',m)][0]
            m2=m1
            next_index = self.project.index(m2)
            producer=True
            while producer:
                I2=itertools.islice(self.project.__iter__(),next_index,len(self.project))
                for m2 in I2:
                    if not re.search('^\s*\<\/playlist\>',m2):
                        s2=re.search('entry\sout\=\"([0-9]{1,4})\"\sproducer\=\"[0-9]{1,2}\_'+p,m2)
                        if s2:
                            s2a = re.sub('\/>','>',m2)
                            # can't get insert to work, inserts whole list as 1 item
                            # and the below errors.
                            # self.project = [self.project.insert(self.project.index(m2),x) for x in af]
                            af.setFadeOut(int(s2.group(1)))
                            self.project.insert(self.project.index(m2)+1,'  </entry>\n')
                            self.project[self.project.index(m2)+1:self.project.index(m2)+1] = af.audioFilter # due to +1 /entry inserted, now 1 less (m2)
                            next_index=self.project.index(m2)+1
                            self.project[self.project.index(m2)]=s2a
                            break
                    else:
                        producer=False
                        break
                
    def addTransitions(self,transition):
        (blankStart,blankEnd) = self.parseOverlaps()
        tractor = ' </tractor>\n'
        for i in range(0,len(blankStart)): 
            if i>0: # start of first blank is the intro title slide
                self.transitionList.append(self.transitionList[-1]+1)
                transition.setID(self.transitionList[-1])
                transition.setOutIn(blankStart[i]-1,blankStart[i]-12)
                transition.setReverse(1)
                self.project[self.project.index(tractor):self.project.index(tractor)]=transition.transition

            self.transitionList.append(self.transitionList[-1]+1)
            transition.setID(self.transitionList[-1])
            # this should be +12 +1, but had to change for 05nov17??
            # probably needed to switch back again for 25nov westhill, but
            # fixed manually
            transition.setOutIn(blankEnd[i]+10,blankEnd[i]-1)
            # at the blank end, transition from track 3 to 4 is not reversed
            # self.project[self.project.index(tractor):self.project.index(tractor)]=transition.transition
            transition.setReverse(0)
            self.project[self.project.index(tractor):self.project.index(tractor)]=transition.transition
        pass

    def saveProject(self,fname=None):
        if fname==None:
            if os.path.isfile(self.projectname):
                UID = uuid.uuid4()
                os.system("mv "+self.projectname+" "+self.projectname+".backup."+str(UID))
            file = open(self.projectname,'w')
        else:
            if os.path.isfile(self.projectname):
                print "Project already exists"
                return
            file = open(fname,'w')
        file.writelines(self.project)

    # add pp or sh for scoring, name
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

    def getOtherTeam(self,team):
        if team=='DMM':
            return self.opp
        else:
            return 'DMM'
        
# convenience class of functions for creating game summary
# just an exercise in using a class __dict__ would be
# better as an ordinary dict.
# not working in partial range makeclock, or at all
class printList:
    def __init__(self):
        self.printStr=''
    def fScoring(self,fTime,*args):
        printStr = " "+args[0]+" "+fTime+" "+args[1]+"\n"
        return printStr
    def fPenalties(self,fTime,*args):
        (team,time) = re.search('([A-Z]{3})([0-9])',args[0]).group(1,2)
        printStr = " "+team+" "+fTime+" ("+str(time)+':00)\n'
        return printStr
    def fHighlights(self,fTime,*args):
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
        psuffix=['st','nd','rd']
        period=0
        pstr=str(period+1)+psuffix[period]
        file.write('\n'+pCommand+'\n'+pstr+' Period\n')
        for fItem in fList:
            (m,s) = divmod(fItem[0],60)
            # hardcoded 12 minute period here
            p = m//12
            if p>period:
                period=p
                pstr=str(period+1)+psuffix[period]
                file.write(pstr+' Period\n')
            msTime = str(np.mod(m,12))+':'+str(s).rjust(2,'0')
            printStr = self.pFunc(pCommand,msTime,fItem[1])
            file.write(printStr)
        
# create a text string on a transparent background
class TextMessage():
    pass

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
    print "main"
    cwd = os.getcwd()
    kdendir = "/home/jbishop/kdenlive/"
    outdir = kdendir+fname+"/"
    workdir = kdendir+fname+"/"
    clipdir = "/media/jbishop/Data/video/"+fname+"/"
    if not os.path.isdir(workdir):
        os.mkdir(workdir)
    else:
        print "Project already exists"
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
        print duration,cameraNumber
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
        print "shifting..."
        project.shiftOverlap()
        af = audioFade(kdendir+'/tcom/audiofade.xml',kdendir+'/tcom/audiofilter.xml')
        di = Dissolve(kdendir+'/transitions/dissolve.xml')
        print "adding audio..."
        project.addAudioFilter(af)
        project.addAudioFade(af.audioFade)
        print "adding transitions..."
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
    print kwargs
    main(filename,process,**kwargs)

