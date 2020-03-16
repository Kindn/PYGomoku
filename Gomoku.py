from tkinter import *
import numpy as np 
from ChessAI import *
from PIL import Image, ImageTk

#-----------------------Global Parameters--------------------------------
ORIGINAL_POINT = {'x':25, 'y':25}  # 棋盘原点坐标
LINE_INTERVAL = 30                 # 棋盘线条间距
LINE_NUM = 15                      # 棋盘大小：LINE_NUM X LINE_NUM
SIDE_LEN = LINE_INTERVAL * (LINE_NUM - 1)  # 棋盘边长

#-----------------------------Window--------------------------------------
'''
 所有坐标均以横向向右为x轴，纵向向下为y轴
 代表棋盘的矩阵要转置才看着像棋盘
'''

class Gomoku(Toplevel):
    # 创建游戏界面
    def __init__(self, AI, var):
        super().__init__()                      # 调用父类构造函数

        self.ORIGINAL_POINT = {'x':40, 'y':40}  # 棋盘原点坐标
        self.LINE_INTERVAL = 30                 # 棋盘线条间距
        self.LINE_NUM = 15                      # 棋盘大小：LINE_NUM X LINE_NUM
        self.SIDE_LEN = LINE_INTERVAL * (LINE_NUM - 1)  # 棋盘边长
        self.CHESS_COLOR = {'player':'black', 'AI':'white'}  # 双方棋子颜色

        self.PLAYER_FIVE_FLAG = 0     # 玩家五连标志，用于判断玩家胜还是平局
        
        self.MAP = np.zeros((self.LINE_NUM, self.LINE_NUM), dtype=np.int)   # 记录落子情况，无子为0，玩家棋子（黑子）为1，AI棋子（白子）为2
        self.occupied_ind = []    # 元素(x, y)为已有棋子的格点坐标
        

        self.AI = AI

        self.TURN = 0   # 轮到玩家为0，轮到电脑为1，游戏结束为-1
        self.step_num = 0

        self.title('奥里给！')
        self.geometry('700x500')

        # 绘制棋盘
        self.board = Canvas(self, bg='orange', height=500, width=500)
        self.board.pack(side=LEFT)

        self.board.bind("<Button-1>", self.player_move)

        self.chess_id = []

        for i in range(LINE_NUM):
            startx = self.ORIGINAL_POINT['x'] + i * self.LINE_INTERVAL
            starty = self.ORIGINAL_POINT['y']
            self.board.create_line(startx, starty, startx, starty + self.SIDE_LEN)
            startx = self.ORIGINAL_POINT['x']
            starty = self.ORIGINAL_POINT['y'] + i * self.LINE_INTERVAL
            self.board.create_line(startx, starty, startx + self.SIDE_LEN, starty)

        # 双方信息界面
        self.player_img = Image.open('images\\Mr_Panda.jpg')
        if var == 1:
            self.AI_img = Image.open('images\\Mr_Banana.jpg')
        else:
            self.AI_img = Image.open('images\\Mr_ZhuGe.jpg')
        self.player_img = ImageTk.PhotoImage(self.player_img)
        self.AI_img = ImageTk.PhotoImage(self.AI_img)

        self.side_label1 = Label(self, bg='blue', fg='yellow', text='黑方（我）')
        self.side_label1.pack(side=TOP)
        self.c1 = Canvas(self, height=185, width=185)
        self.c1.pack(side=TOP)
        self.c1.create_image(0, 0, anchor='nw', image=self.player_img)
        self.l1 = Label(self, bg='green', fg='yellow',width=200, text='敢不敢来跟我搞一盘儿？')
        self.l1.pack(side=TOP)

        self.side_label2 = Label(self, bg='blue', fg='yellow', text='白方（AI）')
        self.side_label2.pack(side=TOP)
        self.c2 = Canvas(self, height=185, width=185)
        self.c2.pack(side=TOP)
        self.c2.create_image(0, 0, anchor='nw', image=self.AI_img)
        self.l2 = Label(self, bg='green', fg='yellow',width=200, text='来撒！老子还怕你？')
        self.l2.pack(side=TOP)


        self.btn = Button(self, text='重开一局', command=self.reset)
        self.btn.pack()


    # 复位
    def reset(self):
        for id in self.chess_id:
            self.board.delete(id)
        self.chess_id = []
        for i in range(self.LINE_NUM):
            for j in range(self.LINE_NUM):
                self.MAP[i][j] = 0
        self.step_num = 0
        self.TURN = 0
        self.occupied_ind = []
        self.PLAYER_FIVE_FLAG = 0
        self.l1.config(text='敢不敢来跟我搞一盘儿？')
        self.l2.config(text='来撒！老子还怕你？')

    # 落子  pos_x,pos_y:0~14
    def draw_chess(self, pos_x, pos_y, color='black'):
        x = self.ORIGINAL_POINT['x'] + pos_x * self.LINE_INTERVAL
        y = self.ORIGINAL_POINT['y'] + pos_y * self.LINE_INTERVAL
       
        id = self.board.create_oval(x - 13, y - 13, x + 13, y + 13, fill=color)
        self.chess_id.append(id)
        if color == 'black':
            self.MAP[pos_x, pos_y] = 1
        else:
            self.MAP[pos_x, pos_y] = 2

        self.occupied_ind.append((pos_x, pos_y))

        e = evaluator()
        if color == 'black':
            self.l1.config(text='落子点：' + '(' + str(pos_x) + ',' + str(pos_y) + ')  ' + '评分：' + str(e.evaluate(self.MAP, 0, self.occupied_ind)))
        else:
            self.l2.config(text='落子点：' + '(' + str(pos_x) + ',' + str(pos_y) + ')  ' + '评分：' + str(e.evaluate(self.MAP, 1, self.occupied_ind)))
        # 轮到对方
        self.TURN = not self.TURN
        ind = np.argwhere(self.MAP == 0)
        if ind.shape[0] == 0:
            self.l1.config(text='wor满哒!')
            self.l2.config(text='还蛮蕉♂灼咧!')
            self.TURN = -1

    # 玩家走棋
    def player_move(self, event):
        if event.x < self.ORIGINAL_POINT['x'] - self.LINE_INTERVAL / 2 or \
            event.x > self.ORIGINAL_POINT['x'] + self.SIDE_LEN + self.LINE_INTERVAL / 2  or \
           event.y < self.ORIGINAL_POINT['y'] - self.LINE_INTERVAL / 2 or \
            event.y > self.ORIGINAL_POINT['y'] + self.SIDE_LEN + self.LINE_INTERVAL / 2 or self.TURN != 0:
            return
        # 寻找离点击处最近的格点落子
        pos_x = int((event.x - self.ORIGINAL_POINT['x'] + self.LINE_INTERVAL / 2) / self.LINE_INTERVAL)
        pos_y = int((event.y - self.ORIGINAL_POINT['y'] + self.LINE_INTERVAL / 2) / self.LINE_INTERVAL)
        self.draw_chess(pos_x, pos_y)

        self.step_num += 1
        # 判断胜负
        if self.get_result(pos_x, pos_y, color=self.CHESS_COLOR['player']):
            self.PLAYER_FIVE_FLAG = 1
            

        # 轮到对方
        #self.TURN = not self.TURN
        self.AI_move()

    # 电脑走棋
    def AI_move(self):
        if self.TURN != 1:
            return

        # 决策走哪儿
        p, score= self.AI.search(self.MAP, self.occupied_ind)
        pos_x, pos_y = p[0], p[1]

        self.draw_chess(pos_x, pos_y, color='white')

        self.step_num += 1
        # 判断胜负
        if self.get_result(pos_x, pos_y, color=self.CHESS_COLOR['AI']):
            if self.PLAYER_FIVE_FLAG == 1:
                self.l1.config(text='老子赢哒!')
                self.l2.config(text='放*，明明是平了么!')
            else:
                self.l2.config(text='老子赢哒!牛不牛批？')
                self.l1.config(text='呦呵!算你儿狠！')
                self.TURN = -1
        elif self.PLAYER_FIVE_FLAG == 1:
            self.l1.config(text='老子赢哒!牛不牛批？')
            self.l2.config(text='呦呵!算你儿狠！')
            return

        # 轮到对方
        #self.TURN = not self.TURN

    # 判断胜负。x,y刚下的棋子坐标
    def get_result(self, x, y, color='black'):
        # 当前所要判断的棋子颜色
        if color == 'black':
            myChess = 1     # 玩家
        else:
            myChess = 2     # AI

        count = 0           # 连珠棋子数

        # 横向搜索 --
        for i in range(6):
            if x - i >= 0:
                if self.MAP[x - i, y] == myChess:
                    count += 1
                else:
                    break
            else:
                break
        for i in range(6):
            if x + i + 1 <= 14:               
                if self.MAP[x + i + 1, y] == myChess:
                    count += 1
                else:
                    break
            else:
                break
        if count >= 5:
            return 1       # 被判断方胜利
        else:
            count = 0

        # 纵向搜索 |
        for i in range(6):
            if y - 1 >= 0:
                if self.MAP[x, y - i] == myChess:
                    count += 1
                else:
                    break
            else:
                break
        for i in range(6):
            if y + i + 1 <= 14:
                if self.MAP[x, y + i + 1] == myChess:
                    count += 1
                else:
                    break
            else:
                break
        if count >= 5:
            return 1       # 被判断方胜利
        else:
            count = 0

        # 撇向搜索 /
        for i in range(6):
            if x - i >= 0 and y - i >= 0:
                if self.MAP[x - i, y - i] == myChess:
                    count += 1
                else:
                    break
            else:
                break
        for i in range(6):
            if x + i + 1 <= 14 and y + i + 1 <= 14:
                if self.MAP[x + i + 1, y + i + 1] == myChess:
                    count += 1
                else:
                    break
            else:
                break
        if count >= 5:
            return 1       # 被判断方胜利
        else:
            count = 0

        # 捺向搜索 \
        for i in range(5):
            if x + i <= 14 and y - i >= 0:
                if self.MAP[x + i, y - i] == myChess:
                    count += 1
                else:
                    break
            else:
                break
        for i in range(5):
            if x - i - 1 >= 0 and y + i + 1 <= 14:
                if self.MAP[x - i - 1, y + i + 1] == myChess:
                    count += 1
                else:
                    break
            else:
                break
        if count >= 5:
            return 1       # 被判断方胜利
        else:
            return 0       # 未分出胜负

        self.TURN = -self.TURN    # 轮换


if __name__ == "__main__":

    AI = None
    choice = None  # 选择圈的id

    # AI
    AI1 = MovebyPos()       
    AI2 = ChessAI(1, 2)

    def set_AI():
        global AI, choice
        ai = var.get()
        if ai == 1:
            AI = AI1
            if choice != None:
                cv.delete(choice)
            choice = cv.create_oval(50, 0, 250, 200, fill=None, outline='yellow')
        else:
            AI = AI2
            if choice != None:
                cv.delete(choice)
            choice = cv.create_oval(250, 0, 450, 200, fill=None, outline='yellow')

    def start_game():
        global AI, var
        Gomoku(AI, var.get())

    root = Tk()
    root.title('PYGomoku V1.0')
    root.geometry('500x500')

    lb1 = Label(root, text='来一局紧张刺激的五子棋！', bg='#d3fbfb', fg='red', font=('华文新魏', 32), width=23, height=2, relief=GROOVE)
    lb1.place(x=0, y=0)

    cv = Canvas(root, bg='blue', width=500, height=220)
    cv.place(x=0, y=100)
    AI1_img = Image.open('images\\Mr_Banana.jpg')
    AI2_img = Image.open('images\\Mr_ZhuGe.jpg')
    AI1_img = ImageTk.PhotoImage(AI1_img)
    AI2_img = ImageTk.PhotoImage(AI2_img)
    cv.create_image(50, 7.5, anchor='nw', image=AI1_img)
    cv.create_text(50, 190, anchor='nw', font=('Arial', 12), fill='white', text='Mr.Banana')
    cv.create_text(50, 205, anchor='nw', font=('华文新魏', 12), fill='white', text='攻防凶猛，快准稳狠')
    cv.create_image(264, 7.5, anchor='nw', image=AI2_img)
    cv.create_text(264, 190, anchor='nw', font=('Arial', 12), fill='white', text='Mr.ZhuGe')
    cv.create_text(264, 205, anchor='nw', font=('华文新魏', 12), fill='white', text='深谋远虑，落子谨慎')

    lb2 = Label(root, text='你的目标是打败对手，而不是平手！', bg='white', fg='red', font=('华文新魏', 20), width=35, height=2, relief=GROOVE)
    lb2.place(x=0, y=325)

    l = Label(root, text='请选择你的对手：')
    l.place(x=0, y=380)

    var = IntVar()
    rd1 = Radiobutton(root, text='Mr.Banana', variable=var, value=1, command=set_AI)
    rd1.place(x=100, y=380)
    rd1 = Radiobutton(root, text='Mr.ZhuGe', variable=var, value=2, command=set_AI)
    rd1.place(x=200, y=380)

    btn = Button(root, text='开始游戏', bg='green', fg='red', font=('华文新魏', 25), width=10, height=2, command=start_game)
    btn.place(x=170, y=400)
    root.mainloop()
