# INFORMATION ------------------------------------------------------------------------------------------------------- #


# Author:  Steven Spratley
# Date:    04/01/2021
# Purpose: Implements an example breadth-first search agent for the COMP90054 competitive game environment.


# IMPORTS AND CONSTANTS ----------------------------------------------------------------------------------------------#


import time, random
from Yinsh.yinsh_model import YinshGameRule 
from copy import deepcopy
from collections import deque
import pickle
THINKTIME = 5


# FUNCTIONS ----------------------------------------------------------------------------------------------------------#
def copy(dict):
    d = pickle.loads(pickle.dumps(dict))
    assert type(d)== type(dict)
    return d

# Defines this agent.
class myAgent():
    def __init__(self, _id):
        self.id = _id # Agent needs to remember its own id.
        self.game_rule = YinshGameRule(2) # Agent stores an instance of GameRule, from which to obtain functions.
        # More advanced agents might find it useful to not be bound by the functions in GameRule, instead executing
        # their own custom functions under GetActions and DoAction.

    # Generates actions from this state.
    def GetActions(self, state):
        return self.game_rule.getLegalActions(state, self.id)
    
    # Carry out a given action on this state and return True if reward received.
    def DoAction(self, state, action):
        score = state.agents[self.id].score
        state = self.game_rule.generateSuccessor(state, action, self.id)
        return state.agents[self.id].score > score

    # Take a list of actions and an initial state, and perform breadth-first search within a time limit.
    # Return the first action that leads to reward, if any was found.
    def SelectAction(self, actions, rootstate):
        start_time = time.time()
        queue      = deque([ (copy(rootstate),[]) ]) # Initialise queue. First node = root state and an empty path.
        
        # Conduct BFS starting from rootstate.
        while len(queue) and time.time()-start_time < THINKTIME:
            state, path = queue.popleft() # Pop the next node (state, path) in the queue.
            new_actions = self.GetActions(state) # Obtain new actions available to the agent in this state.
            
            for a in new_actions: # Then, for each of these actions...
                next_state = copy(state)              # Copy the state.
                next_path  = path + [a]                   # Add this action to the path.
                reward     = self.DoAction(next_state, a) # Carry out this action on the state, and note any reward.
                if reward:
                    print(f'Move {len(next_path)}, path found:', next_path)
                    return next_path[0] # If this action was rewarded, return the initial action that led there.
                else:
                    queue.append((next_state, next_path)) # Else, simply add this state and its path to the queue.
        
        return random.choice(actions) # If no reward was found in the time limit, return a random action.
        
    
# END FILE -----------------------------------------------------------------------------------------------------------#
