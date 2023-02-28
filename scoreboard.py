import os
import numpy as np

######################
# scoreBoard
#####################

class scoreBoard():
    def __init__(self,team,opp,sdir,wdir,C):
        self.C = C
        self.teamScore = 0 # goals for
        self.oppScore = 0 # goals against
        self.opp = opp
        self.team = team
        self.res = self.C.res # '1920x1080' or lower video resolution 
        self.period = 1 # period number is 1-based
        self.wdir = wdir # project (working) directory with source clips
        self.sdir = sdir # source code directory with team logos, fixed sub-graphics etc
        self.xoff = 360 # hard-coded x offset for scoreboard crop to low-res video, or None for default
        self.pwd = os.getcwd()
        self.makeStaticBoard()
        
    def makeStaticBoard(self):
        os.chdir(os.path.join(self.sdir,'logo'))
        # place static box4 and timegraphic
        # note spaces at brackets.
        # note a space after the line break backslash gets interpreted
        # as an extra newline which breaks the string
        # these offsets are currently hard-coded for 1920x1080. cropRes method can be used for low-res video
        c4 = """convert -size """ + '1920x1080' + """ xc:transparent \
        \( box4.png -resize 50% -repage +1508+18 \) \
        \( 1ST.png -resize 50% -repage +1511+21 \) \
        \( box3.png -resize 50% -repage +1320+18 \) \
        \( 0.png -resize 50% -repage +1324+21 \) \
        \( """+self.team+"""_68x34.png -repage +1133+21 \) \
        \( """+self.team+""".png -resize 50% -repage +1203+21 \) \
        \( box2.png -resize 50% -repage +1130+18 \) \
        \( 0.png -resize 50% -repage +1266+21 \) \
        \( """+self.opp+""".png -resize 50% -repage +1374+21 \) \
        \( """+self.opp+"""_68x34.png -repage +1436+21 \) \
        \( box1.png -resize 50% -repage +1078+18 \) \
        \( gthl_92x68.png -resize 50% -repage +1081+21 \) \
        -background transparent -flatten """ + self.wdir + """/trun/staticScoreBoard.png"""
        os.system(c4)
        os.chdir(self.wdir)

    # increments staticScoreBoard assuming a goal is not scored at 0:00
    def incrementScore(self,team):
        os.chdir(os.path.join(self.sdir,'logo'))
        # change score
        if team.startswith(self.team):
            self.teamScore += 1
        elif team == self.opp:
            self.oppScore +=1 
        c3 = "convert " + self.wdir + "/trun/staticScoreBoard.png \
        \( "+str(self.teamScore)+".png -resize 50% -repage +1266+21 \) \
        \( "+str(self.oppScore)+".png -resize 50% -repage +1324+21 \) \
        -background transparent -flatten "+self.wdir+"/trun/staticScoreBoard.png"
        os.system(c3)
        os.chdir(self.wdir)

    def incrementPeriod(self,periodPanel):
        os.chdir(os.path.join(self.sdir,'logo'))
        self.period += 1
        c3 = "convert " + self.wdir + "/trun/staticScoreBoard.png \
        \( "+periodPanel+".png -resize 50% -repage +1511+21 \) \
        -background transparent -flatten "+self.wdir+"/trun/staticScoreBoard.png"
        os.system(c3)
        os.chdir(self.wdir)

    # build one clock frame
    # time: indexes the input fixed graphics for numerals
    # fname,fnamesuffix: index the output graphics for individual clock frames
    def buildBoard(self,time,fname,fnamesuffix,penalty=None,scoreMessage=None,hMessage=None):
        os.chdir(self.sdir) # location of the input fixed graphics for numerals
        tfilename = self.wdir + '/trun/tpng/' + fname + str(fnamesuffix).rjust(3,'0')+'.png'
        c2 = "convert " + self.wdir + "/trun/staticScoreBoard.png \
        \( png/tpng2/t"+str(time).rjust(3,'0')+".png -resize 50% -repage +1554+21 \) "
        if penalty is not None:
            if penalty.PP:
                c2 += " \( logo/"+penalty.pState+penalty.PPTeam+".png -resize 37% -repage +"+str(penalty.panelOffset)+"+59 \) \
                \( png/tpng2/pp"+str(penalty.pStateTime).rjust(3,'0')+".png -resize 50% -repage +"+str(penalty.panelOffset+120)+"+54 \) "
        # need a check for this to override a penalty panel
        if scoreMessage is not None:
            if scoreMessage.mTime and len(scoreMessage.Msg):
                c1 = "convert logo/scorePanel.png -fill white \
            -pointsize 46 -annotate +40+50 \'" + scoreMessage.Msg + "\' \
            -blur 0x1 " + self.wdir + "/trun/tpng/scorePanelAnno.png"
                os.system(c1)
                c2 += " \( " + self.wdir + "/trun/tpng/scorePanelAnno.png -resize 37% -repage +1125+59 \) "
        # need check for this no overlaps with any other message
        if hMessage is not None:
                c1 = "convert logo/scorePanel" + hMessage.team + ".png -fill white \
            -pointsize 46 -annotate +40+50 \"" + hMessage.Msg + "\" \
            -blur 0x1 " + self.wdir + "/trun/tpng/scorePanelAnno.png"
                os.system(c1)
                c2 += " \( " + self.wdir + "/trun/tpng/scorePanelAnno.png -resize 37% -repage +" + str(hMessage.panelOffset) + "+59 \) "

        c2 += " -background transparent -flatten "+ tfilename
        os.system(c2)
        # optionally crop the finished graphic for low-res video
        if int(self.res.split('x')[0]) < 1920:
            self.cropRes(tfilename)
        os.chdir(self.wdir)

    # main method for building a set of scoreboard graphics once per each second of a play
    # interval
    def writeTimeFrames(self,trange,tinc,startTime,penalty,scoreMessage=None,highlight=[],doboard=True):
        for i in range(startTime,startTime+trange):
            t_highlight = i+(self.period-1)*self.C.pdur*60 # highlight message can persist from a run interval into a stop interval
            if tinc:
                t = i
                fnameroot = 't' # root filename for runtime graphics. recycle once per period
                fnamesuffix = t
            else:
                t = startTime
                fnameroot = 'ts' # root filename for stoptime graphics. 
                fnamesuffix = i - startTime # ie recycle filenames at each stop interval
            hMessage = None
            if len(highlight):
                for h in highlight:
                    if t_highlight in h.rTime:
                        hMessage = h.update()
            if doboard:
                self.buildBoard(t,fnameroot,fnamesuffix,penalty,scoreMessage,hMessage)
            if penalty.PP and tinc:
                penalty.update()
            if scoreMessage is not None:
                if scoreMessage.Msg:
                    scoreMessage.update()
            # if len(highlight): # assumption two messages do not overlap in one run interval
            #     for h in highlight:
            #         if h.Msg:
            #             h.update()

    # spacing and positioning above is all hard-coded for hidef video. optional crop for low-res < hidef video
    def cropRes(self,fname):
        xres,yres = self.res.split('x')
        if self.xoff is None:
            xoff = str(int((1920 - int(xres)) * 0.8)) # a default offset for the crop
        else:
            xoff = str(self.xoff) # user offset for crop
        c2 = 'convert -crop ' + self.res  + '+' + xoff + '+0 ' + fname + ' ' + fname
        os.system(c2)

