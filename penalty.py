import re
import numpy as np

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
