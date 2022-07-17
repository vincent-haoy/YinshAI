# INFORMATION ------------------------------------------------------------------------------------------------------- #

# Author:  Steven Spratley, extending code by Guang Ho and Michelle Blom
# Date:    07/03/22
# Purpose: Implements "Yinsh" for the COMP90054 competitive game environment

# CONSTANTS ----------------------------------------------------------------------------------------------------------#

#On the gameboard, Agent 0's rings and counters are denoted by 1s and 2s. 
#Agent 1's rings and counters are 3s and 4s. Illegal positions are 5.
EMPTY    = 0
RING_0   = 1
CNTR_0   = 2
RING_1   = 3
CNTR_1   = 4
ILLEGAL  = 5
NAMES    = {0:"Teal", 1:"Magenta"}

#List of illegal positions.
ILLEGAL_POS = [(0,0),  (0,1),  (0,2),  (0,3),  (0,4),  (0,5),  (0, 10),
               (1,0),  (1,1),  (1,2),  (1,3),
               (2,0),  (2,1),  (2,2),
               (3,0),  (3,1),
               (4,0),
               (5,0),
               (5,10),
               (6,10),
               (7,9),  (7,10),
               (8,8),  (8,9),  (8,10),
               (9,7),  (9,8),  (9,9),  (9,10),
               (10,0), (10,5), (10,6), (10,7), (10,8), (10,9), (10,10)]

# CLASS DEF ----------------------------------------------------------------------------------------------------------#

# Bundle together an agent's activity in the game for use in updating a policy.
class AgentTrace:
    def __init__(self, pid):
        self.id = pid
        self.action_reward = [] # Turn-by-turn history consisting of (action,reward) tuples.
    
def ActionToString(agent_id, action):
    if action["type"] == "place ring":
        return f"{NAMES[agent_id]} placed a ring at {action['place pos']}."
    elif action["type"] == "place and move":
        if "sequences" not in action:
            return f"{NAMES[agent_id]} placed a counter at {action['place pos']} and moved to {action['move pos']}."
        else:
            return f"{NAMES[agent_id]} placed at {action['place pos']} and moved to {action['move pos']}, creating a sequence for their opponent."
    elif action["type"] == "place, move, remove":
        return f"{NAMES[agent_id]} placed at {action['place pos']}, moved to {action['move pos']}, formed a sequence and removed ring {action['remove pos']}."
    elif action["type"] == "pass":
        return f"{NAMES[agent_id]} has no counters to play, and passes."
    else:
        return "Unrecognised action."

def AgentToString(agent_id, ps):
    desc = "Agent #{} has scored {} rings thus far.\n".format(agent_id, ps.score)
    return desc

def BoardToString(game_state):
    desc = ""
    return desc

# END FILE -----------------------------------------------------------------------------------------------------------#