import sys
import time
sys.path.append('agents/t_032/')
from template import Agent
from ourmodel import YinshGameRule as GameRule
from state_heuristic import cal_heuristic
import random
THINKINGTIME = 0.93

class myAgent(Agent):
    def __init__(self,_id):
        super().__init__(_id)
        self.game_rule = GameRule(2)

    def GetActions(self, state):
        return self.game_rule.getLegalActions(state, self.id)    
        
    def SelectAction(self,actions,game_state):
        if(actions[0]["type"] == 'place ring'):
            return random.choice(actions)
        # 50^2 = 2500; 5^4 = 1296
        lookahead = 2 if len(actions) > 5 else  4
        action = myminimax(self.game_rule,game_state,self.id,True,lookahead,returnAction=True)
        return action

def myminimax(game_rule,currentstate, currentid, Ismaxturn,depth, alpha=float("-inf"), beta = float("+inf"),returnAction=False):   
    start_time = time.time()
    if depth <=0 :
        # return random.randint(0,5)
        return cal_heuristic(currentstate,currentid)

    # for the action-returning step only
    if returnAction:
        bestvalue = float("-inf")
        bestaction = None
    val, func = (float("-inf"), max) if Ismaxturn else (float("+inf"), min)

    successorActions = game_rule.getLegalActions(currentstate,currentid)
    # return random.choice(successorActions)
    for successorAction in successorActions: 
        #predict qvalue
        
        #modify the state on the fly
        game_rule.generateSuccessor(currentstate,successorAction,currentid)
        val = func(myminimax(game_rule,currentstate,1-currentid, not Ismaxturn,depth-1, alpha, beta), val)
        #verify and update

        #
        game_rule.ReverstateByactions(successorAction,currentstate)
        # for the action-returning step only
        if returnAction:
            if val >bestvalue:
                bestaction = successorAction
                bestvalue = val
            if time.time() - start_time >=THINKINGTIME:
                bestaction.pop('moveby',None)
                bestaction.pop('sequence remove',None)
                return bestaction
        if Ismaxturn:
            alpha = max(alpha, val)
        else:
            beta = min(beta, val)
        if (Ismaxturn and 0 >= beta - val) or (not Ismaxturn and 0 <= alpha-val):
            break
    if not returnAction:
        return val
    else:
        bestaction.pop('moveby',None)
        bestaction.pop('sequence remove',None)        
        return bestaction