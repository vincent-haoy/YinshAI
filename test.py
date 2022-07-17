

from queue import PriorityQueue
import random
import math
import sys
from copy import deepcopy
sys.path.append("agents/t_032/")
from template import Agent
from Yinsh.yinsh_model import YinshState as GameState
from Yinsh.yinsh_model import YinshGameRule as GameRule
from   Yinsh.yinsh_utils import *
#states: set of state where opponents 
# best 1 states? 
class myAgent(Agent):
    def __init__(self,_id):
        super().__init__(_id)
        self.game_rule = GameRule(2)
        self.root = None
    
    def decition(self,node):
        node.parent = None
        self.root = node
    
    def SelectAction(self,actions,game_state):
        rootnode = MCTSNODE(None,game_state, 1 - self.id)
        return random.choice(actions)

def getUCTscore(node,Cp):
    if node.parent:
        parentvisited = node.parent.numberOfVisit
    else:
        parentvisited = 1
    return node.Qvalue + 2 * Cp * math.sqrt( 2 * math.log(parentvisited)/ node.numberOfVisit)
def isnotEndstate(state):
    return max(state.rings_won) < 3 and state.counters_left > 0
    
def QvalueEvaluator(actions, state):
        return [(1,action) for action in actions]

def greedysimulator(state, gamerule, role):
    if isnotEndstate(state):
        avaliabelaction = gamerule.getLegalActions(state,role)
        selectedaction = random.choice(avaliabelaction)
        state2 = gamerule.generateSuccessor(state,selectedaction,role)
        return greedysimulator(state2,gamerule,1-role)
    else:
        return 1

class MCTSTREE:
    def __int__(self,depth, ExpandnodeInPly, gamerule, Nodetoexpand, exploration=False):
        self.depth = depth
        self.ExpandnodeInPly = ExpandnodeInPly
        self.Nodetoexpand = Nodetoexpand
        self.exploration = exploration
        self.root = None
        self.gamerule = gamerule
    
    def buildtree(self,game_state,id):
        self.root = MCTSNODE(None,game_state, 1 - id) 

    def _recursivelyBuildtree(self,node,depth):
        state = node.state
        if depth > 0:
            node.getaction(self,state,self.gamerule)
            node.sortaction()
            for score, action in node.actions[0:self.ExpandnodeInPly]:
                node.generatesucceserByAction(node,state,self.gamerule)
            for successorsnode in node.successors.values():
                self._recursivelyBuildtree(successorsnode,depth-1)
        return 



class MCTSNODE:
    def __init__(self,parent,state,nodeid) :
        self.parent= parent
        self.nodeid=nodeid
        self.state = state
        self.Qvalue = 0
        self.numberOfVisit = 0
        self.discountfactor = 0.98
        self.actions = None
        # your opponents node
        self.successors = {}
        self.isplayerNode = True

    def getaction(self,state,gamerule):
        self.actions = [(score,state) for (score,state) in QvalueEvaluator((gamerule.getLegalActions(state,self.nodeid)),state)]
    
    def generatesucceserByAction(self,action,state,gamerule):
        _, action = action
        newstate = deepcopy(self.state)
        self.successors[frozenset(action.items())] = MCTSNODE(self, deepcopy(self.state),1-self.nodeid)
    
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
        return not self.action

myrule = GameRule(2)
mystate = GameState(2)
rootnode = MCTSNODE(None, mystate,0)
rootnode.getaction(rootnode.state,myrule)
rootnode.generatesucceserByAction(rootnode.actions[0], rootnode.state, myrule)
bestaction = rootnode.getbestaction()