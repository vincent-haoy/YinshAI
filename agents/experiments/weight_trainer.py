import sys
import time
sys.path.append('agents/t_032/')
from template import Agent
from ourmodel import YinshGameRule as GameRule
from state_heuristic import cal_heuristic
from agents.experiments.feature_weight import feature_weights
from agents.experiments.feature_weight import Q_value_class as Q_class
import random
THINKINGTIME = 0.93
class myAgent(Agent):
    def __init__(self,_id):
        super().__init__(_id)
        self.game_rule = GameRule(2)
        self.feature_weights = feature_weights(self.game_rule)

    def GetActions(self, state):
        return self.game_rule.getLegalActions(state, self.id)    
        
    def SelectAction(self,actions,game_state):
        if(actions[0]["type"] == 'place ring'):
            return random.choice(actions)
        action = myminimax(self.game_rule,game_state,self.id,True,2,self.feature_weights,returnAction=True)
        return action



def myminimax(game_rule,currentstate, currentid, Ismaxturn,depth, feature_weights,alpha=float("-inf"), beta = float("+inf"),returnAction=False):
    start_time = time.time()
    # if the state do not have Q_value, initialize it as 0

    h = cal_heuristic(currentstate, currentid)
    if depth <=0 :
        # return random.randint(0,5)
        return (h,h)

    # for the action-returning step only
    if returnAction:
        bestvalue = float("-inf")
        bestaction = None
    val, func = (float("-inf"), max) if Ismaxturn else (float("+inf"), min)
    h_max = -9999999999999999
    successorActions = game_rule.getLegalActions(currentstate,currentid)

    '''
    利用还没改变的state计算得到所有legal_action对应的feature和Q并保存
    '''
    if currentid == 0:
        state_Q = Q_class(currentstate,feature_weights,currentid,successorActions,h)

    # return random.choice(successorActions)
    for act_idx in range(0,len(successorActions)):
        successorAction = successorActions[act_idx]

        #modify the state on the fly
        game_rule.generateSuccessor(currentstate,successorAction,currentid)
        val_tmp,h_next = myminimax(game_rule,currentstate,1-currentid, not Ismaxturn,depth-1,feature_weights, alpha, beta)
        val = func(val_tmp,val)
        h_max = max(h_max,h_next)
        '''
        将最终得到的val减去当前state的heuristic，作为reward保存打state_Q里面的y数组
        '''
        if currentid==0:
            reward = state_Q.cal_delta(h_next,h,act_idx)
            state_Q.y[act_idx] = reward

        game_rule.ReverstateByactions(successorAction, currentstate)

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


    if currentid == 0:
        feature_weights.weight_update(state_Q)

    if not returnAction:
        return (val,h_next)
    else:
        bestaction.pop('moveby',None)
        bestaction.pop('sequence remove',None)
        return bestaction

