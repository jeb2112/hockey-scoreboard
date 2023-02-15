import os
import re
import itertools
import uuid
import numpy as np
from scoreboard import scoreBoard
from penalty import Penalty
from misc import Message

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
                print(c)
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
                    hIndex = self.checkHighlight(trun,hIndex)
                if i in intervalNum:
                    self.SB.writeTimeFrames(trun,self.currentTime,self.P,SM)
                c = commandR1
                c = c + "-start_number " +str(self.currentTime) + " -i ../tcom/t%03d.png -vframes "+ str(trun) + " "
                c = c + command2 + "trun"+str(i+1).rjust(2,'0') +".mp4 2> /dev/null"
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
        return idx #,SM

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
                print("Project already exists")
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