# this program is only used for mcts experiment
import random
import math
import sys
import time
sys.path.append("agents/t_032/")
from state_heuristic import cal_heuristic
from template import Agent
from feature_weight import *
from ourmodel import YinshGameRule as GameRule
from copy import deepcopy
THRESHOLD = 1
#states: set of state where opponents 
# best 1 states? 
class myAgent(Agent):
    def __init__(self,_id):
        super().__init__(_id)
        self.game_rule = GameRule(2)
        self.root = None
        self.feature_weight = feature_weights(self.game_rule)
    
    def decition(self,node):
        node.parent = None
        self.root = node
    
    def SelectAction(self,actions,game_state):
        starttime = time.time()
        if(actions[0]["type"] == 'place ring') or len(actions) <= 1:
            return random.choice(actions)
        tree = MCTSTREE(2,30,self.game_rule,1000,self.feature_weight)
        tree.buildtree(game_state,self.id)
        
        starttime = time.time()
        epoch = 0
        while time.time() - starttime <= THRESHOLD:
            #Selection
            currentnode = tree.root
            while not currentnode.Isleaf():
                currentnode = max(currentnode.successors,key = lambda x: getUCTscore(x,1.414))
            #expansion
            #simulation
            simulatestate = deepcopy(currentnode.state)
            result = greedysimulator(simulatestate,self.game_rule,self.id,self.feature_weight)
            # result is calculated on teal, times -1 if magenta
            if self.id == 1: result = result*-1
            #backup
            currentnode.backwardPropragration(result)
            epoch += 1
            #start the next iteration
        # selection from the node
        highest_child = max(tree.root.successors,key = lambda x: x.Qvalue)
        #some mystery bug here. The code seems useless here but do not remove
        f = open('time.txt','a',encoding='utf8')
        f.write(str(time.time()-starttime)+'\n')
        f.close()
        if tree.root.actions == []:
            return random.choice(actions)
        return highest_child.actionTohere

        

def getUCTscore(node,Cp):
    if node.parent:
        parentvisited = node.parent.numberOfVisit+1
    else:
        parentvisited = 1
    if (node.numberOfVisit == 0):
        return float('inf')

    return node.Qvalue + 2 * Cp * math.sqrt( 2 * math.log(parentvisited)/ (node.numberOfVisit+1))

def isnotEndstate(state):
    return state.counters_left > 1 and max(state.rings_won) < 3
    
def QvalueEvaluator(actions, state,feature_weight):
    # gamerlue = GameRule(2)
    # feature_weight = feature_weights(gamerlue)
    scorelist = []
    for action in actions:
        if action["type"] == "pass":
            scorelist.append(0)
            continue
        g = feature_weight.cal_feature_value(feature_weight.extract_feature(state,action))
        scorelist.append(g) if g else scorelist.append(0)
    i = 0
    for action in actions:
        scorelist[i] = (scorelist[i],action)
        i += 1
    return scorelist

def greedysimulator(state, gamerule, role,feature_weight):
    sequencefound = 0
    while isnotEndstate(state) and sequencefound != 0:
        avaliabelaction = gamerule.getLegalActions(state,role)
        if len(avaliabelaction) <= 1: return 0
        scoredaction = QvalueEvaluator(avaliabelaction,state,feature_weight)
        _, selectedaction = max(scoredaction, key = lambda x :x[0])
        
        for action in avaliabelaction:
            if action.get('sequences',[None,None]) != [None,None]:
                sequencefound = 1000 if action['sequences'][0] != None else -1000
        gamerule.generateSuccessor(state,selectedaction,role)
        role = 1 - role
    if not isnotEndstate(state):
        return 500
    else: 
        return sequencefound
class MCTSTREE:
    def __init__(self,depth, ExpandnodeInPly, gamerule, Nodetoexpand, feature_weight,exploration=False):
        self.depth = depth
        self.ExpandnodeInPly = ExpandnodeInPly
        self.Nodetoexpand = Nodetoexpand
        self.exploration = exploration
        self.root = None
        self.gamerule = gamerule
        self.feature_weight = feature_weight
    
    def buildtree(self,game_state,id):
        self.root = MCTSNODE(None,game_state, id,None)
        self.root.hscore = cal_heuristic(game_state,id)
        self._recursivelyBuildtree(self.root,self.depth,id)

    def _recursivelyBuildtree(self,node,depth,id):
        state = node.state
        if depth > 0:
            node.getaction(state,self.gamerule,self.feature_weight)
            node.sortaction()
            #building successors
            for i in range(0,self.ExpandnodeInPly): 
                try:
                    firstelement =  node.actions.pop(0)
                    node.generatesucceserByAction(firstelement,state,self.gamerule)
                except IndexError:
                    break
            for successorsnode in node.successors:
                successorsnode.hscore = cal_heuristic(successorsnode.state,id)
                successorsnode.reward = successorsnode.hscore - successorsnode.parent.hscore
                self._recursivelyBuildtree(successorsnode,depth-1,id)
        return 



class MCTSNODE:
    def __init__(self,parent,state,nodeid,ActionToHere):
        self.hscore = 0    
        self.parent= parent
        self.nodeid=nodeid
        self.state = state
        self.Qvalue = 0
        self.numberOfVisit = 0
        self.discountfactor = 0.98
        self.reward = 0
        self.actions = None
        # your opponents node
        self.successors = []
        self.isplayerNode = True
        self.actionTohere = ActionToHere

    def getaction(self,state,gamerule,feature_weight):
        allactions = gamerule.getLegalActions(state,self.nodeid)
        scored_action = QvalueEvaluator(allactions,state,feature_weight)
        assert(len(allactions) == len(scored_action))
        self.actions = scored_action
    
    def Isleaf(self):
        return self.successors == []
    
    def generatesucceserByAction(self,action,state,gamerule):
        (_ , action) = action
        statecpy = deepcopy(self.state)
        gamerule.generateSuccessor(statecpy,action,self.nodeid)
        self.successors.append(MCTSNODE(self, statecpy,1-self.nodeid,action))
    
    def sortaction(self):
        self.actions.sort(key = lambda x:x[0])
    
    def getbestaction(self):
        result =  max(self.actions, key=lambda x:x[0])
        return result
    
    def update(self,leaf_value):
        self.numberOfVisit += 1
        self.Qvalue += (self.reward + leaf_value - self.Qvalue) / self.numberOfVisit
        
    def backwardPropragration(self,leaf_value):
        if self.parent != None:
            self.parent.backwardPropragration(self.discountfactor * leaf_value)
        self.update(leaf_value)
    
    def Isfullyexpanded(self):
        return self.actions == []