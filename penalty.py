import re
import numpy as np

###############
# Penalty
###############

class Penalty():
    def __init__(self,team,opp,C):
        self.C = C
        self.opp = opp #opponent team
        self.team = team # home team
        self.pTime = {self.team:[],self.opp:[]} # lists of time remaining of all current penalties
        self.PP=False # flag indicating a power play
        self.PPTeam=None # team with advantage
        self.penaltyTeam=None # team down a player
        self.nP = {self.team:0,self.opp:0} # tally of the number of all current penalties
        self.pState = "pp" # ie the current state of penalties, doubles as prefix of graphic filename
        self.pStateTime = 0 # net time remaining in the current penalty state
        # self.panelOffset = 1125 # x offset for displaying penalty tag under appropriate team
        
    # guide text =  eg tag a guide 'penalty: DMM2' for 2 min penalty
    def add(self,teamtime,currentTime):
        plist = re.findall('([A-Z]{3,4})([0-9])',teamtime)
        for p in plist:
            self.pTime[p[0]].append(int(p[1])*60)
            self.nP[p[0]] += 1
            self.PP=True
        self.updateState()

    def remove(self,team):
        if self.nP[team]:
            self.pTime[team].pop(0)
            self.nP[team] -= 1
            self.PP = any(self.pTime.values())
            self.updateState()

    # reduce all penalty times by one second
    def update(self):
        for team in self.pTime.keys():
            # iterate in reverse order here to modify the list of penalties
            for i in range(len(self.pTime[team])-1,-1,-1):
                self.pTime[team][i] -= 1
                if self.pTime[team][i] == 0:
                    self.pTime[team].pop(i)
                    if self.nP[team]:
                        self.nP[team] -= 1
        self.PP = any(self.pTime.values())
        self.updateState()

    # recalculate the state of current set of penalties
    # offsets are hard-coded for 1920x1080 hidef case
    def updateState(self):
        if self.nP[self.team] > self.nP[self.opp]:
            self.penaltyTeam = self.team
            self.PPTeam=self.opp
            self.panelOffset = self.C.paneloffsets[self.opp]
        elif self.nP[self.opp] > self.nP[self.team]:
            self.penaltyTeam = self.opp
            self.PPTeam=self.team
            self.panelOffset = self.C.paneloffsets[self.team]
        elif self.nP[self.opp] == self.nP[self.team]:
            self.PPTeam=self.team
            self.penaltyTeam=self.opp
            self.panelOffset = self.C.paneloffsets['none'] # 4on4 case. 

        # regular power play
        if self.nP[self.team] + self.nP[self.opp] == 1:
            self.pState = "pp"
            self.pStateTime = self.pTime[self.penaltyTeam][0]
        # offsetting penalties, or 4 on 4
        elif self.nP[self.team]*self.nP[self.opp] == 1:
            if self.pTime[self.team][0] == self.pTime[self.opp][0]:
                self.PP = False
            else:
                self.pState = "4on4"
                self.pStateTime = min(self.pTime[self.penaltyTeam][0],self.pTime[self.PPTeam][0])
        # 5 on 3
        elif np.abs(self.nP[self.team] - self.nP[self.opp]) == 2:
            self.pState = "5on3"
            self.pStateTime = self.pTime[self.penaltyTeam][0]
        # 4 on 3
        elif self.nP[self.team] + self.nP[self.opp] == 3:
            self.pState = "4on3"
            self.pStateTime = min(self.pTime[self.penaltyTeam][0],self.pTime[self.PPTeam][0])
