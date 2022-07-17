import sys
import time
sys.path.append('agents/t_032/')
from template import Agent
from ourmodel import YinshGameRule as GameRule
from Yinsh.yinsh_utils import *
from state_heuristic import cal_heuristic
import random
THINKINGTIME = 0.97
class myAgent(Agent):
    def __init__(self,_id):
        super().__init__(_id)
        self.game_rule = GameRule(2)

    def GetActions(self, state):
        return self.game_rule.getLegalActions(state, self.id)    
        
    def SelectAction(self,actions,game_state):
        if(actions[0]["type"] == 'place ring'):
            if game_state.board[(5,5)]==EMPTY:# per-set decision
                return {'type': 'place ring', 'place pos':(5,5)}
            elif predecidedAction(game_state)!=None:
                actions_list = predecidedAction(game_state)
                if actions_list != []:
                    return random.choice(actions_list)
                else:
                    return random.choice(actions)
        # set different depth with different situations
        lookahead = 2 if len(actions) > 5 else 4
        if len(actions)<3:lookahead = 6
        action = myminimax(self.game_rule,game_state,self.id,True,lookahead,returnAction=True)
        return action

def predecidedAction(game_state):
    actions = []
    # per-set positions at the beginning
    pos = [(4,5),(4,6),(5,4),(5,6),(6,4),(6,5)]
    for i in range(0,6):
        if game_state.board[pos[i]] == EMPTY:
            actions.append({'type': 'place ring', 'place pos':pos[i]})
    return actions

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
        
        #modify the state on the fly
        game_rule.generateSuccessor(currentstate,successorAction,currentid)
        val = func(myminimax(game_rule,currentstate,1-currentid, not Ismaxturn,depth-1, alpha, beta), val)
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