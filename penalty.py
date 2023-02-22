import re
import numpy as np

###############
# Penalty
###############

class Penalty():
    def __init__(self,team,opp):
        self.opp = opp
        self.team = team
        self.pTime = {self.team:[],self.opp:[]}
        self.PP=False
        # these two variables have not much use
        self.PPTeam=None
        self.penaltyTeam=None 
        self.nP = {self.team:0,self.opp:0}
        self.pState = "pp" # ie prefix of graphic filename indicates the penalty state
        self.pStateTime = 0 # net time remaining in the current penalty state
        self.panelOffset = 1125
        # self.pState = dict(PPflag=None,PPTeam=None,PenaltyTeam=None,pState=None)
        
    # guide text =  eg DMM2 for 2 min penalty
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

    # reduce penalty time by one second
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

    def updateState(self):
        if self.nP[self.team] > self.nP[self.opp]:
            self.penaltyTeam = self.team
            self.PPTeam=self.opp
            self.panelOffset = 1315
        elif self.nP[self.opp] > self.nP[self.team]:
            self.penaltyTeam = self.opp
            self.PPTeam=self.team
            self.panelOffset = 1125
        elif self.nP[self.opp] == self.nP[self.team]:
            self.PPTeam=self.team
            self.penaltyTeam=self.opp
            self.panelOffset = 1220 # 4on4 case. 

        if self.nP[self.team] + self.nP[self.opp] == 1:
            self.pState = "pp"
            self.pStateTime = self.pTime[self.penaltyTeam][0]
        elif self.nP[self.team]*self.nP[self.opp] == 1:
            if self.pTime[self.team][0] == self.pTime[self.opp][0]:
                self.PP = False # ie offsetting penalties
            else:
                self.pState = "4on4"
                self.pStateTime = min(self.pTime[self.penaltyTeam][0],self.pTime[self.PPTeam][0])
        elif np.abs(self.nP[self.team] - self.nP[self.opp]) == 2:
            self.pState = "5on3"
            self.pStateTime = self.pTime[self.penaltyTeam][0]
        elif self.nP[self.team] + self.nP[self.opp] == 3:
            self.pState = "4on3"
            self.pStateTime = min(self.pTime[self.penaltyTeam][0],self.pTime[self.PPTeam][0])
