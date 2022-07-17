import sys
sys.path.append('agents/t_032/')

EMPTY    = 0
RING_0   = 1
CNTR_0   = 2
RING_1   = 3
CNTR_1   = 4
ILLEGAL  = 5


MARKER_WEIGHT = 10
RING_WEIGHT = 100000
CONTROLED_MARKER_WEIGHT = 1

def define_roles(role):
    if role == 0:
        my_marker = CNTR_0
        op_marker = CNTR_1
    else:
        my_marker = CNTR_1
        op_marker = CNTR_0
    return my_marker,op_marker

def count_markers(state,role):
    my_marker, op_marker = define_roles(role)
    board = state.board
    result = 0

    for line in board:
        for i in line:
            if i == my_marker:
                result+=MARKER_WEIGHT
            elif i == op_marker:
                result-=MARKER_WEIGHT
    return result

def count_rings(state,role):
    result = state.rings_won[role]*RING_WEIGHT
    result -= state.rings_won[1-role]*RING_WEIGHT*1.1
    #assert(state.rings_won[role]<=3 and state.rings_won[1-role]<=3)

    if state.rings_won[role] >= 3:
        return 999999999999
    elif state.rings_won[1 - role] >= 3:
        return -999999999999
    return result

def cal_heuristic(state,role):

    result2 = count_rings(state,role)
    result3 = count_markers(state,role)
    final_result = result2+result3

    return final_result



