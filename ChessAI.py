# coding:utf-8

# 有关五子棋AI的各个类,参考资料：https://www.cnblogs.com/webRobot/p/5817740.html

import numpy as np 
import re

#---------------------------------------------------------------------------
# 评估类
#---------------------------------------------------------------------------
class evaluator:
    def __init__(self):
        # 棋形  0:空位，1:当前选手的棋，2:对手的棋
        FIVE = 0
        FOUR = 1
        THREE = 2
        TWO = 3
        SFOUR = 4
        STHREE = 5
        STWO = 6
        # 'x'用来给单个字符串组成元组
        self.chessShape = {}
        self.chessShape[FIVE] = ('11111', 'x')                                                                                             #长连
        self.chessShape[FOUR] = ('011110', 'x')                                                                                            #活四
        self.chessShape[THREE] = ('001110', '011010', '010110', 'x')                                                                        #活三
        self.chessShape[TWO] = ('0110', '01010', '010010', 'x')                                                                            #活二
        self.chessShape[SFOUR] = ('211110', '011112', '11101', '10111', '11011', 'x')                                                      #冲四
        self.chessShape[STHREE] = ('21110', '01112', '211010', '010112', '210110', '011012', '11001', '10011', '10101', '2011102', 'x')    #眠三
        self.chessShape[STWO] = ('2110', '0112', '21010', '01012', '210010', '010012', '10001', 'x')                                       #眠二
        
        self.pos_weight = [[(7 - max(abs(7 - i), abs(7 - j))) for j in range(15)] for i in range(15)]  # 位置权重，中心位置为7，每往外一圈-1

        self.shape_cnt = np.zeros((2, 7))  # 当前走法黑白两子各棋形的计数 ，0：黑子，1：白子

        self.record = np.zeros((15, 15, 4))                 # record[i][j][方向]记录点(i, j)在该方向上是否扫描过 WE:0,NS:1,NE2SW:2,NW2SE:3


    # 复位
    def reset(self):
        for i in range(2):
            for j in range(7):
                self.shape_cnt[i][j] = 0
        for i in range(15):
            for j in range(15):
                for k in range(4):
                    self.record[i][j][k] = 0

    # 评估当前棋形得分
    def evaluate(self, board, side, area):
        FIVE, FOUR, THREE, TWO = 0, 1, 2, 3
        SFOUR, STHREE, STWO = 4, 5, 6
        BLACK, WHITE = 0, 1

        # 复位
        self.reset()
        
        #tmp_board = board  错误搞法，因为传递的是引用，board也会变！！！
        tmp_board = np.copy(board)
        record = self.record
        
        # 扫描棋盘计数棋形
        for pos in area:
            if self.shape_cnt[WHITE][FIVE] > 0: break
            if self.shape_cnt[BLACK][FIVE] > 0: break
            if self.shape_cnt[WHITE][FOUR] > 0: break
            if self.shape_cnt[BLACK][FOUR] > 0: break
            if self.shape_cnt[WHITE][THREE] > 1: break
            if self.shape_cnt[BLACK][THREE] > 1: break
            if self.shape_cnt[BLACK][SFOUR] > 0: break
            if self.shape_cnt[WHITE][SFOUR] > 0:break
            i = pos[0]
            j = pos[1]
            if record[i][j][0] == 0: self.search_WE(tmp_board, i, j)
            if record[i][j][1] == 0: self.search_NS(tmp_board, i, j)
            if record[i][j][2] == 0: self.search_NE2SW(tmp_board, i, j)
            if record[i][j][3] == 0: self.search_NW2SE(tmp_board, i, j)
        # 评分
        
        
        b, w = 0, 0    # 黑白棋得分
        count = self.shape_cnt
        # 打分
        # 如果有两个冲四，则相当于一个活四
        if count[WHITE][SFOUR] >= 2:
            count[WHITE][FOUR] += 1
        if count[BLACK][SFOUR] >= 2:
            count[BLACK][FOUR] += 1

        if side == WHITE:
            if count[WHITE][FIVE]: return 10000
            if count[BLACK][FIVE]: return -10000
            if count[BLACK][SFOUR]: return -9000
            if count[WHITE][FOUR]: return 9990
            if count[BLACK][FOUR]: return -9980
            if count[BLACK][SFOUR] and count[BLACK][THREE]: return -9970
            
            if count[WHITE][SFOUR]: return 9960
            if count[WHITE][THREE] >= 2 and count[BLACK][SFOUR] == 0: return 9960
            if count[BLACK][THREE] and count[WHITE][SFOUR] == 0:# and\
                                       #count[WHITE][THREE] == 0 and\
                                       #count[WHITE][STHREE] == 0:
                return -9950
            if count[WHITE][THREE] and count[BLACK][SFOUR] == 0: return 9940
            
            if count[WHITE][THREE] > 1:
                w += 2000
            elif count[WHITE][THREE]:
                w += 600
            if count[BLACK][THREE] > 1:
                b += 500
            elif count[BLACK][THREE]:
                b += 200

            if count[WHITE][TWO] or count[WHITE][STHREE]:
                w += count[WHITE][TWO] * 4 + count[WHITE][STHREE] * 10
            if count[BLACK][TWO] or count[BLACK][STHREE]:
                b += count[BLACK][TWO] * 4 + count[BLACK][STHREE] * 10
            if count[WHITE][TWO] and count[WHITE][STWO]:
                w += count[WHITE][TWO]   
            if count[BLACK][TWO] and count[BLACK][STWO]:
                b += count[BLACK][TWO]
        else:
            if count[BLACK][FIVE]: return 10000
            if count[WHITE][FIVE]: return -10000
            if count[WHITE][SFOUR]: return -9000
            if count[BLACK][FOUR]: return 9990
            if count[WHITE][FOUR]: return -9980
            if count[WHITE][SFOUR] and count[WHITE][THREE]: return -9970
            
            if count[BLACK][SFOUR]: return 9960
            if count[BLACK][THREE] >= 2 and count[WHITE][SFOUR] == 0: return 9960
            if count[WHITE][THREE] and count[BLACK][SFOUR] == 0:# and\
                                       #count[BLACK][THREE] == 0 and\
                                       #count[BLACK][STHREE] == 0:
                return -9950
            if count[BLACK][THREE] and count[WHITE][SFOUR] == 0: return 9940
            
            if count[BLACK][THREE] > 1:
                b += 1000
            elif count[BLACK][THREE]:
                b += 500
            if count[WHITE][THREE] > 1:
                w += 400
            elif count[WHITE][THREE]:
                w += 200

            if count[WHITE][TWO] or count[WHITE][STHREE]:
                w += count[WHITE][TWO] * 10 + count[WHITE][STHREE] * 15
            if count[BLACK][TWO] or count[BLACK][STHREE]:
                b += count[BLACK][TWO] * 10 + count[BLACK][STHREE] * 15
            if count[WHITE][TWO] and count[WHITE][STWO]:
                w += count[WHITE][TWO] * 8
            if count[BLACK][TWO] and count[BLACK][STWO]:
                b += count[BLACK][TWO] * 8

        # 加上位置权重
        for i in range(15):
            for j in range(15):
                if board[i][j] == WHITE:
                    w += self.pos_weight[i][j]
                elif board[i][j] == BLACK:
                    b += self.pos_weight[i][j]
            
        if side == WHITE:
            return w - b
        else:
            return b - w

    # 仅对自己的棋子进行评估
    def evaluate_myself(self, board, side, area):
        # 复位
        self.reset()
        
        #tmp_board = board  错误搞法，因为传递的是引用，board也会变！！！
        tmp_board = np.copy(board)
        record = self.record
        
        # 扫描棋盘计数棋形
        for pos in area:
            i = pos[0]
            j = pos[1]
            if record[i][j][0] == 0: self.search_WE(tmp_board, i, j)
            if record[i][j][1] == 0: self.search_NS(tmp_board, i, j)
            if record[i][j][2] == 0: self.search_NE2SW(tmp_board, i, j)
            if record[i][j][3] == 0: self.search_NW2SE(tmp_board, i, j)
        # 评分
        FIVE, FOUR, THREE, TWO = 0, 1, 2, 3
        SFOUR, STHREE, STWO = 4, 5, 6

        BLACK, WHITE = 0, 1

        b, w = 0, 0    # 黑白棋得分
        count = self.shape_cnt
        # 打分
        # 如果有两个冲四，则相当于一个活四
        if count[side][SFOUR] >= 2:
            count[side][FOUR] += 1
    
        
        if count[side][FIVE]: return 10000
        if count[side][FOUR]: return 9990
        if count[side][SFOUR]: return 9960
        if count[side][THREE] >= 2 and count[BLACK][SFOUR] == 0: return 9960

        return 0
            

    # 模式匹配
    def match(self, s, side):
        FIVE, FOUR, THREE, SFOUR = 0, 1, 2, 4
        if self.shape_cnt[side][FIVE] == 0 and \
                   self.shape_cnt[side][FOUR] == 0 and \
                   self.shape_cnt[side][THREE] <= 1 and\
                   self.shape_cnt[side][SFOUR] == 0:
            for sh in range(7):  
                    for k in range(len(self.chessShape[sh]) - 1):
                        regex = re.compile(self.chessShape[sh][k])
                        mo = regex.search(s)
                        if mo != None:
                            self.shape_cnt[side][sh] += 1  
                            break

    # 横向搜索 --
    def search_WE(self, board, i, j):
        line = []      # 这个方向上的数据
        for x in range(15):
            line.append(board[x][j])
            self.record[i][j][0] = 1
        
        BLACK, WHITE = 0, 1

        s = ''
        for x in range(len(line)):
            s += str(line[x])
        # 匹配黑棋
        self.match(s, BLACK)

        for x in range(len(line)):
            if line[x] == 1: line[x] = 2
            elif line[x] == 2: line[x] = 1
        s = ''
        for x in range(len(line)):
            s += str(line[x])
        # 匹配白棋
        self.match(s, WHITE)

    # 纵向搜索 |
    def search_NS(self, board, i, j):
        line = []      # 这个方向上的数据
        for y in range(15):
            line.append(board[i][y])
            self.record[i][j][1] = 1
        
        BLACK, WHITE = 0, 1

        s = ''
        for x in range(len(line)):
            s += str(line[x])
        # 匹配黑棋
        self.match(s, BLACK)

        for y in range(len(line)):
            if line[y] == 1: line[y] = 2
            elif line[y] == 2: line[y] = 1
        s = ''
        for x in range(len(line)):
            s += str(line[x])
        # 匹配白棋
        self.match(s, WHITE)

    # 撇向搜索 /
    def search_NE2SW(self, board, i, j):
        # 确定边界
        xr, yu = i, j   # 右上边界
        xl, yd = i, j   # 左下边界
        while xr < 14 and yu > 0:
            xr += 1
            yu -= 1
        while xl > 0 and yd < 14:
            xl -= 1
            yd += 1
        
        line = []
        for i in range(xr - xl + 1):
            line.append(board[xr - i][yu + i])
            self.record[xr - i][yu + i][2] = 1

        BLACK, WHITE = 0, 1

        s = ''
        for x in range(len(line)):
            s += str(line[x])
        # 匹配黑棋
        self.match(s, BLACK)

        for x in range(len(line)):
            if line[x] == 1: line[x] = 2
            elif line[x] == 2: line[x] = 1
        s = ''
        for x in range(len(line)):
            s += str(line[x])
        # 匹配白棋
        self.match(s, WHITE)
        

    # 捺向搜索 \
    def search_NW2SE(self, board, i, j):
        # 确定边界
        xr, yd = i, j   # 右下边界
        xl, yu = i, j   # 左上边界
        while xr < 14 and yd < 14:
            xr += 1
            yd += 1
        while xl > 0 and yu > 0:
            xl -= 1
            yu -= 1
        
        line = []
        for i in range(xr - xl + 1):
            line.append(board[xr - i][yd - i])
            self.record[xr - i][yd - i][3] = 1

        BLACK, WHITE = 0, 1

        s = ''
        for x in range(len(line)):
            s += str(line[x])
        # 匹配黑棋
        self.match(s, BLACK)

        for x in range(len(line)):
            if line[x] == 1: line[x] = 2
            elif line[x] == 2: line[x] = 1
        s = ''
        for x in range(len(line)):
            s += str(line[x])
        # 匹配白棋
        self.match(s, WHITE)


#---------------------------------------------------------------------------
# alpha-beta剪枝决策类
#---------------------------------------------------------------------------
class ChessAI:
    def __init__(self, side, depth):
        self.side = side  # 决策方，0：黑方，1：白方
        self.maxDepth = depth   # 博弈树深度
        self.__evaluator = evaluator()   # 评分器
        self.best_pos = None             # 最佳落子点

    # 产生当前棋局走法
    def generate_moves(self, board, area):
        moves = []           # 每个元素为走法的坐标元组，(x, y)
        around = []
        # 生成搜索区域     
        # 这个地方要注意是不是周围每个可走点都被扫到
        for i in range(len(area)):
            for j in range(-1, 2, 1):
                for k in range(-1, 2, 1):
                    pos = (area[i][0] + j, area[i][1] + k)
                    if pos[0] >= 0 and pos[0] <= 14 and pos[1] >= 0 and pos[1] <= 14:
                        around.append(pos)
            
        for p in around:
            x = p[0]
            y = p[1]
            if board[x][y] == 0:
                moves.append((x, y))

        return moves
 
    # 遍历过程,求当前节点得分
    def alpha_beta_pruning(self, board, side, depth, area, alpha=-0xffffff, beta=0xffffff):
        # 如果博弈树深度为0，则对当前棋盘评分
        if depth <= 0:
            return self.__evaluator.evaluate(board, side, area)
        # 如果已经有五连珠，则直接返回
        score = self.__evaluator.evaluate(board, side, area)
        if abs(score) >= 10000 and depth < self.maxDepth:
            return score
        # 生成新走法
        next_moves = self.generate_moves(board, area)
        if next_moves == []:   # 棋盘已满
            return -0xffffff
        best_move = None
        # 对每个新走法（子节点），进行dfs
        # 更替turn
        new_turn = not side
        # 优先搜索刚下的点附近
        for (x, y) in next_moves[::-1]:  
            board[x, y] = side + 1
            area.append((x, y))
            # dfs
            score = -self.alpha_beta_pruning(board, new_turn, depth - 1, area, -beta, -alpha)
            # 还原board和area
            board[x, y] = 0
            area.remove((x,y))
            # 更新alpha
            if score > alpha:
                alpha = score
                best_move = (x, y)
                if alpha >= beta:
                    break       
        # 得到最佳走法
        if depth == self.maxDepth and best_move:
            self.best_pos = best_move
            #print(alpha)

        # 返回最高分
        return alpha

    # 找自己的棋子评分最高的点下
    def move_by_my_chess(self, board, side, area):
        # 生成新走法
        next_moves = self.generate_moves(board, area)
        if next_moves == []:   # 棋盘已满
            return -0xffffff
        best_move = None
        maxScore = 0
        for (x, y) in next_moves:
            board[x, y] = side + 1
            area.append((x, y))
            score = self.__evaluator.evaluate_myself(board, side, area)
            if score > maxScore:
                maxScore = score
                best_move = (x, y)
            area.remove((x, y))

        self.best_pos = best_move

        return maxScore


    # alpha-beta剪枝法得到最佳走法
    def search(self, board, area):
        # 防止推理过程中棋盘被填满
        ind = np.argwhere(board == 0)
        tmp_board = np.copy(board)
        depth = min(self.maxDepth, ind.shape[0])
        # 进行dfs
        maxScore = self.alpha_beta_pruning(tmp_board, self.side, depth, area)
        # 如果发现走哪里都对自己很不利，那就只着眼于眼前
        if maxScore <= -9000:
            depth = self.maxDepth
            self.maxDepth = 1
            maxScore = self.alpha_beta_pruning(tmp_board, self.side, 1, area)
            self.maxDepth = depth
        # 如果发现已无法阻止玩家五连（即得分依然小于-9000），则努力寻求平局
        if maxScore <= -9000:
            maxScore = self.move_by_my_chess(tmp_board, self.side, area)

        print(maxScore,self.best_pos)
        # 返回得分最高点的坐标及得分
        return self.best_pos, maxScore

#---------------------------------------------------------------------------
# 位置打分类
#---------------------------------------------------------------------------
class MovebyPos:
    def __init__(self):
        self.__evaluator = evaluator()
        self.best_pos = None

    # 对所有可落子点打分，进攻分+防守分
    def search(self, board, area):
        moves = []
        # 这个地方要注意是不是周围每个可走点都被扫到
        for i in range(len(area)):
            for j in range(-1, 2, 1):
                for k in range(-1, 2, 1):
                    pos = (area[i][0] + k, area[i][1] + j)
                    if (pos[0] in range(14)) and (pos[1] in range(14)):
                        if board[pos[0], pos[1]] == 0:
                            moves.append(pos)
        
        maxScore = -0xffffff
        tmp_board = np.copy(board)
        for p in moves[::-1]:
            pos_x, pos_y = p[0], p[1]
            area.append(p)
            if tmp_board[pos_x, pos_y] == 0:
                # 进攻分
                tmp_board[pos_x, pos_y] = 2
                offensive_score =self.__evaluator.evaluate(tmp_board, 1, area)
                tmp_board[pos_x, pos_y] = 0
                # 防守分
                if offensive_score < 10000:
                    tmp_board[pos_x, pos_y] = 1
                    defensive_score =self.__evaluator.evaluate(tmp_board, 0, area) * 0.85
                    tmp_board[pos_x, pos_y] = 0
                else:
                    maxScore = offensive_score
                    self.best_pos = (pos_x, pos_y)
                    break
                #总分
                score = offensive_score * 0.45 + defensive_score * 0.55

                if score >= maxScore:
                    maxScore = score
                    do_score = (offensive_score, defensive_score)
                    self.best_pos = (pos_x, pos_y)
            area.remove(p)
            
        print(maxScore)
        print(do_score)
        return self.best_pos, maxScore
       


if __name__ == '__main__':

    i = 6
    j = 7
    # 确定边界
    xr, yu = i, j   # 右上边界
    xl, yd = i, j   # 左下边界
    while xr < 14 and yu > 0:
        xr += 1
        yu -= 1
    while xl > 0 and yd < 14:
        xl -= 1
        yd += 1
    board = np.zeros((15, 15))
    for i in range(xr - xl + 1):
        board[xr - i][yu + i] = 1
    
    print(board)