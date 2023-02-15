import os
import numpy as np

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
