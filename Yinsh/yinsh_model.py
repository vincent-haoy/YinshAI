# INFORMATION ------------------------------------------------------------------------------------------------------- #

# Author:  Steven Spratley, extending code by Guang Ho and Michelle Blom
# Date:    07/03/22
# Purpose: Implements "Yinsh" for the COMP90054 competitive game environment

# IMPORTS ------------------------------------------------------------------------------------------------------------#


import re, itertools, numpy, time, random
from   Yinsh.yinsh_utils import *
from   template import GameState, GameRule


# CLASS DEF ----------------------------------------------------------------------------------------------------------#       


#Represents game as agents playing on a board.
class YinshState(GameState):           
    def __init__(self, num_agents):
        #Board is stored as a numpy array of ints (the meanings of which are explained in Yinsh.yinsh_utils).
        self.board = numpy.zeros((11,11), dtype=numpy.int8)
        for pos in ILLEGAL_POS:
            self.board[pos] = ILLEGAL
        #Ring_pos stores ring positions for each agent.
        self.ring_pos  = [[], []]
        self.counters_left = 51
        self.rings_to_place = 10
        self.rings_won = [0, 0]
        self.agents = [self.AgentState(i) for i in range(num_agents)]
        self.agent_to_move = 0
            
    class AgentState:
        def __init__(self, _id):
            self.id     = _id
            self.score  = 0
            self.passed = False
            self.agent_trace = AgentTrace(_id)
            self.last_action = None
        

#Implements game logic.
class YinshGameRule(GameRule):
    def __init__(self,num_of_agent):
        super().__init__(num_of_agent)
        self.private_information = None #Yinsh is a perfect-information game.
        
    #Returns the list of board positions found by drawing a line through a given played position.
    def positionsOnLine(self, pos, line):
        if line=='h':
            return [(pos[0], i) for i in range(11)]
        if line=='v':
            return [(i, pos[1]) for i in range(11)]
        return [(pos[0]+i, pos[1]-i) for i in range(-10, 11) if (0 <= pos[0]+i <= 10 and 0 <= pos[1]-i <= 10)]
    
    #Returns the list of board positions between two play positions.
    def positionsPassed(self, start_pos, end_pos, include_start_and_end=False):
        line = 'h' if start_pos[0]==end_pos[0] else 'v' if start_pos[1]==end_pos[1] else 'd'
        play_positions = sorted([start_pos, end_pos])
        line_positions = sorted(self.positionsOnLine(start_pos, line))
        idx1,idx2 = line_positions.index(play_positions[0]),line_positions.index(play_positions[1])
        return line_positions[idx1:idx2+1] if include_start_and_end else line_positions[idx1+1:idx2]

    #Flips a counter (if present).
    def flip(self, board, pos):
        board[pos] = EMPTY if board[pos]==EMPTY else CNTR_0 if board[pos]==CNTR_1 else CNTR_1
        
    #Checks the board, given recent changes, for possible new sequences. 
    #Returns a list of sequences, indexed by agent ID, with a maximum 1 sequence per agent.
    def sequenceCheck(self, board, changes):
        sequences = [None, None]
        details = None
        lines = ['v','h','d']
        #If multiple counters flipped, start by sequence-checking the line that connects them.
        if len(changes)>1:
            ys,xs  = list(zip(*changes))
            line   = 'v' if len(set(xs))==1 else 'h' if len(set(ys))==1 else 'd'
            posits = self.positionsOnLine(changes[0], line)
            cntrs  = ''.join([str(board[pos]) for pos in posits])
            lines.remove(line) #Remove this line from lines list to avoid checking it twice.
            seq0_start,seq1_start = cntrs.find(str(CNTR_0)*5),cntrs.find(str(CNTR_1)*5)
            if not seq0_start==-1:
                sequences[0] = posits[seq0_start : seq0_start+5]
                details = (board, cntrs, line, seq0_start)
            if not seq1_start==-1:
                sequences[1] = posits[seq1_start : seq1_start+5]
                details = (board, cntrs, line, seq1_start)
        for pos in changes:
            for line in lines:
                posits = self.positionsOnLine(pos, line)
                cntrs  = ''.join([str(board[pos]) for pos in posits])
                seq0_start,seq1_start = cntrs.find(str(CNTR_0)*5),cntrs.find(str(CNTR_1)*5)
                if not seq0_start==-1:
                    sequences[0] = posits[seq0_start : seq0_start+5]
                    details = (board, cntrs, line, seq0_start)
                if not seq1_start==-1:
                    sequences[1] = posits[seq1_start : seq1_start+5]
                    details = (board, cntrs, line, seq1_start)
        return sequences, details
    
    #Returns a list of legal positions to move a ring (at pos) along a given line.
    #First, get all positions along this line (not including ring's current position). Then, for each position, get a 
    #string representing the rings and counters passed. If that string is valid, as checked by a regular expression
    #(i.e. no rings jumped, and only one group of counters jumped), add position to list to return.
    def movementsAlongLine(self, game_state, pos, line):
        valid_movements = []
        positions = self.positionsOnLine(pos, line) 
        positions.remove(pos) 
        #Regex: Pass through 0 or more empty spaces, followed by 0 or more counters, then one empty space.
        regex = re.compile(f"{EMPTY}*[{CNTR_0}{CNTR_1}]*{EMPTY}"+'{1}') 
        for p in positions:
            passed = self.positionsPassed(pos, p, include_start_and_end=True)
            passed = passed if passed[0]==pos else list(reversed(passed))
            p_str  = ('').join([str(game_state.board[i]) for i in passed[1:]])
            if re.fullmatch(regex, p_str):
                valid_movements.append(p)
        return valid_movements
    
    def initialGameState(self):
        return YinshState(self.num_of_agent)
    
    #Takes a game state and and action, and returns the successor state.
    def generateSuccessor(self, state, action, agent_id):
        agent,board = state.agents[agent_id],state.board
        opponent_id = 1 if agent_id==0 else 0
        agent.last_action = action #Record last action such that other agents can make use of this information.
        score = 0
        changes = []
        
        #Check for pass first.
        if action["type"] == "pass":
            agent.passed = True
            return state
        
        #Place and remove symbols on the board representing rings and counters, as necessary.
        ring,cntr = (RING_0,CNTR_0) if agent_id==0 else (RING_1,CNTR_1)
        if action["type"] == "place ring":
            board[action["place pos"]] = ring
            state.ring_pos[agent_id].append(action["place pos"])
            state.rings_to_place -= 1
        elif action["type"] == "place and move":
            board[action["place pos"]]  = cntr
            board[action["move pos"]]   = ring
            state.ring_pos[agent_id].append(action["move pos"])
            state.ring_pos[agent_id].remove(action["place pos"])
            state.counters_left -= 1
        else:
            board[action["place pos"]]  = cntr
            board[action["move pos"]]   = ring
            board[action["remove pos"]] = EMPTY
            for pos in action["sequences"][agent_id]:
                board[pos] = EMPTY
            state.ring_pos[agent_id].append(action["move pos"])
            state.ring_pos[agent_id].remove(action["place pos"])
            state.ring_pos[agent_id].remove(action["remove pos"])
            score += 1
            state.rings_won[agent_id] += 1
            state.counters_left -= 1
            
        #If a ring was moved, flip counters in its path.
        if "move pos" in action:
             [self.flip(board, pos) for pos in self.positionsPassed(action["place pos"],  action["move pos"])]
        
        #If this action sets up a sequence for the opponent, remove it, along with a random ring of theirs.
        opp_id = 0 if agent_id==1 else 1
        if "sequences" in action and action["sequences"][opp_id]:
            for pos in action["sequences"][opp_id]:
                state.board[pos] = EMPTY
            ring_pos = random.choice(state.ring_pos[opp_id])
            state.ring_pos[opp_id].remove(ring_pos)
            state.rings_won[opp_id] += 1
            state.agents[opp_id].score += 1
            board[ring_pos] = EMPTY
            
        #Log this turn's action and any resultant score. Return updated gamestate.
        agent.agent_trace.action_reward.append((action,score))
        agent.score += score
        return state
    
    #Game ends if any agent possesses 3 rings. As a rare edge case, poor playing agents might encounter a game where 
    #none are able to proceed. Game also ends in this case.
    def gameEnds(self):
        deadlock = 0
        for agent in self.current_game_state.agents:
            deadlock += 1 if agent.passed else 0
            if agent.score == 3:
                return True
        return deadlock==len(self.current_game_state.agents)

    #Return final score for this agent.
    def calScore(self, game_state, agent_id):
        return game_state.agents[agent_id].score

    #Return a list of all legal actions available to this agent in this gamestate.
    def getLegalActions(self, game_state, agent_id):
        actions,agent = [],game_state.agents[agent_id]
        
        #A given turn consists of the following:
        #  1. Place a counter of an agent's colour inside one of their rings.
        #  2. Move that ring along a line to an empty space. 
        #     - Any number of empty spaces may be jumped over.
        #     - Any number of counters may be jumped over. Those jumped will be flipped to the opposite colour.
        #     - Once a section of counters is jumped, the ring must take the next available empty space.
        #     - Rings may not be jumped.
        #  3. If a sequence is formed in this process, the game will remove it, along with the agent's chosen ring.
        #     - If multiple sequences are formed, the first one found will be removed (the agent does not decide).
        #     - If an opponent's sequence is formed, it will be removed and credited to their score on their turn.
        
        #Since the gamestate does not change during an agent's turn, all turn parts are able to be planned for at once.
        #Actions will always take the form of one of the following four templates:
        # {'type': 'place ring',          'place pos': (y,x)}
        # {'type': 'place and move',      'place pos': (y,x), 'move pos': (y,x)}
        # {'type': 'place, move, remove', 'place pos': (y,x), 'move pos': (y,x), 'remove pos':(y,x), 'sequences': []}
        # {'type': 'pass'} You cannot voluntarily pass, but there may be scenarios where the agent cannot legally move.
        #Note that the 'sequences' field is a list of sequences, indexed by agent ID. This is to cover cases where an
        #agent creates a sequence for the opponent, or even creates sequences for both players simultaneously.
        #In the case that the agent completes an opponent's sequence, but does not also create their own, the
        #'sequences' field will appear in a 'place and move' action.
        
        if game_state.rings_to_place: #If there are rings still needing to be placed,
            for y in range(11): #For all positions on the board,
                for x in range(11):
                    if game_state.board[(y,x)]==EMPTY: #If this position is empty,
                        actions.append({'type': 'place ring', 'place pos':(y,x)}) #Generate a 'place ring' action.
        
        elif not game_state.counters_left: #Agent has to pass if there are no counters left to play.
            return [{'type':'pass'}]
        
        #For all of the agent's rings, search outwards and ennumerate all possible actions.
        #Check each action for completed sequences. If a sequence can be made, create the action type accordingly.
        else:
            for ring_pos in list(game_state.ring_pos[agent_id]):
                for line in ['v', 'h', 'd']:
                    for pos in self.movementsAlongLine(game_state, ring_pos, line):
                        #Make temporary changes to the board state, for the purpose of sequence checking.
                        changes = []
                        cntr,ring = (CNTR_0,RING_0) if agent_id==0 else (CNTR_1,RING_1)
                        game_state.board[ring_pos] = cntr
                        game_state.board[pos] = ring
                        game_state.ring_pos[agent_id].remove(ring_pos)
                        game_state.ring_pos[agent_id].append(pos)
                        
                        #Append a new action to the actions list, given whether or not a sequence was made.
                        start_pos,end_pos = tuple(sorted([ring_pos, pos]))
                        changes.append(ring_pos)
                        for p in self.positionsPassed(start_pos, end_pos):
                            self.flip(game_state.board, p)
                            changes.append(p)
                        sequences,details = self.sequenceCheck(game_state.board, changes)
                        if sequences[agent_id]:
                            for r_pos in game_state.ring_pos[agent_id]:
                                actions.append({'type':'place, move, remove', 'place pos':ring_pos, 'move pos':pos, \
                                                'remove pos':r_pos, 'sequences': sequences})
                        elif sequences[0 if agent_id==1 else 1]:
                            for r_pos in game_state.ring_pos[agent_id]:
                                actions.append({'type':'place and move', 'place pos':ring_pos, 'move pos':pos, \
                                                'sequences': sequences})                            
                        else:
                            actions.append({'type': 'place and move', 'place pos':ring_pos, 'move pos':pos})
                        
                        #Remove temporary changes to the board state.
                        [self.flip(game_state.board, p) for p in self.positionsPassed(start_pos, end_pos)]
                        game_state.board[ring_pos] = ring
                        game_state.board[pos] = EMPTY
                        game_state.ring_pos[agent_id].remove(pos)
                        game_state.ring_pos[agent_id].append(ring_pos)
                      
        return actions


# END FILE -----------------------------------------------------------------------------------------------------------#
