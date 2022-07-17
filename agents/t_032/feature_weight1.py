EMPTY    = 0
RING_0   = 1
CNTR_0   = 2
RING_1   = 3
CNTR_1   = 4
ILLEGAL  = 5

LINEED_MARKER_WEIGHT = 1

# a class used for calculate weights for features extracted
class feature_weights(object):
    alpha = 0.00001
    feature_lenth = 7
    weights = [46.160094955608024,33.33331402122798,
53.83656471745171,7.482780016001686,
9.981780333901431, 12.559454942161528,
-1.897827782861352]
    update_flag = False

    def __init__(self,game_rule):
        # self.read_in_weights()
        self.game_rule = game_rule


    # update the weights in linear q-learning
    def weight_update(self,state_Q):
        num_instances = len(state_Q.y)
        weight_deltas = [0]*len(self.weights)
        for act_idx in range(0,num_instances):
            y = state_Q.y[act_idx]
            features = state_Q.features[act_idx]
            Q = state_Q.Q_value[act_idx]

            f = open('test.txt', 'a', encoding='utf8')
            for weight_idx in range(0,len(self.weights)):
                weight_deltas[weight_idx] -= 2*features[weight_idx]*(y-Q)
                f.write('weight_delta:'+ str(weight_deltas[weight_idx])+' f:'+str(features[weight_idx]) + ' y:' + str(y)+' Q:'+str(Q)+'\n')

            f.write('\n')
            f.close()

        for idx in range(0,len(self.weights)):
            self.weights[idx] -= weight_deltas[idx]/num_instances*self.alpha

        self.write_to_file()

    # read in pre-trained weights from the weight.txt file
    def read_in_weights(self):
        try:
            file = open('weight.txt', 'r', encoding='utf8')
        except Exception as e:
            file = open('weight.txt', 'w', encoding='utf8')
            for i in range(0, self.feature_lenth):
                file.write('0\n')
        for line in file.readlines():
            self.weights.append(float(line.strip()))
        file.close()

    # write the updated weights to the weight.txt file
    def write_to_file(self):
        file = open('weight.txt', 'w', encoding='utf8')
        file2 = open('weight_history.txt','a+',encoding='utf8')
        for i in self.weights:
            file.write(str(i)+'\n')
            file2.write(str(i)+' ')
        file.close()
        file2.write('\n')
        file2.close()


    # extract defined features from a state-action pair
    def extract_feature(self,state,action):
        if action['type'] != 'place, move, remove' and action['type'] != 'place and move':
            return None

        features = []
        board = state.board
        start_pos = action['place pos']
        end_pos = action['move pos']

        line = 'h' if start_pos[0]==end_pos[0] else 'v' if start_pos[1]==end_pos[1] else 'd'
        my_between_cnt, op_between_cnt = self.count_markers_between(board, start_pos, end_pos, line)

        features.append(self.count_markers_three_line(board, start_pos, only_my_marker=True))
        features.append(self.count_markers_three_line(board, end_pos, only_my_marker=False))
        features.append(state.counters_left)
        features.append(my_between_cnt)
        features.append(op_between_cnt)
        features.append(state.rings_won[0])
        features.append(state.rings_won[1])

        f =  open('feature.log','a+',encoding='utf8')
        f.write(str(features)+'\n')
        f.close()
        return features

    # calculate the markers between two positions on the board
    def count_markers_between(self,board,start_pos,end_pos,line):
        play_positions = sorted([start_pos, end_pos])
        line_positions = sorted(self.game_rule.positionsOnLine(start_pos, line))
        idx1, idx2 = line_positions.index(play_positions[0]), line_positions.index(play_positions[1])
        positions = line_positions[idx1+1:idx2]
        my_cnt = 0
        op_cnt = 0
        for item in positions:
            if board[item] == CNTR_0 :
                my_cnt += 1
            elif board[item] == CNTR_1:
                op_cnt += 1
        return my_cnt,op_cnt

    # calculate Q-value from feature and weights
    def cal_feature_value(self,features):
        result = 0
        for i in range(0,self.feature_lenth):
            result += features[i]*self.weights[i]
        return result

    # count the markers in two positions
    def count_marker_one_line(self,board,positions,pos,start_idx,end_idx,only_my_marker):
        cnt = 0
        op_cnt = 0
        start_cnt = False
        for i in range(start_idx, end_idx):
            marker = board[positions[i]]
            if positions[i] == pos:
                break
            elif start_cnt:
                if marker == CNTR_0:
                    cnt += 1
                elif marker == CNTR_1:
                    op_cnt += 1
            elif marker == EMPTY:
                start_cnt = True
            else:
                cnt = 0
                op_cnt = 0
        if not only_my_marker:
            cnt += op_cnt
        return cnt

    # calculate all the controlled markers influenced in one action
    def count_markers_three_line(self,board,pos,only_my_marker=False,default_line=None):
        cnt = 0
        for line in ['v', 'h', 'd']:
            if line == default_line:
                continue
            line_cnt = 0
            positions = self.game_rule.positionsOnLine(pos, line)
            line_cnt += self.count_marker_one_line(board,positions,pos,0,len(positions),only_my_marker)
            line_cnt += self.count_marker_one_line(board,positions,pos,len(positions)-1,0,only_my_marker)
            if only_my_marker:
                line_cnt += line_cnt*LINEED_MARKER_WEIGHT if only_my_marker and line_cnt>2 else 0
            cnt += line_cnt
        return cnt

# store all factors extracted from the action for q-learning
class Q_value_class(object):
    alpha = 0.1
    gamma = 0.8

    # init the features and Q_value of an action and initialize a array y for storing reward
    def __init__(self,state,feature_weights,agent_id,actions,score):
        self.max_Q_value = 0
        self.Q_value = [0]*(len(actions))
        self.features = []
        self.y = [0]*(len(actions))

        for i in range(0,len(self.Q_value)):
            self.features.append(feature_weights.extract_feature(state,actions[i]))
            self.Q_value[i] = feature_weights.cal_feature_value( self.features[i])

        self.score = score
        self.id = agent_id

    def get_score(self,state,agent_id):
        return state.rings_won[agent_id]-state.rings_won[1-agent_id]

    def __str__(self):
        return 'Q_value: '+str(self.Q_value)+'\n'+'y: '+str(self.y)+'\n'+'\n'

    def cal_delta(self,val,h,act_idx):
        return val - h