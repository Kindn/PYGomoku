# PYGomoku
 A Gomoku game developed in python.一个简单的用python编写的五子棋小游戏，只支持人机对抗
## 仓库结构
* PYGomoku V1.0/1  是用pyinstaller打包好的可执行文件，exe在文件夹中的dist子文件夹里
* image 存放程序中用到的图片
* Gomoku.py 主模块，定义Gomoku类，代表整个游戏，包括界面和逻辑。用的tkinter库，看着不大好看。。。
* ChessAI.py 该模块定义了一些有关五子棋AI算法的类，具体参考注释吧
## 一些问题
课余无聊写出来的程序，还是存在很多问题。主要未解决问题：
* 用鼠标点击落子后界面上己方棋子和AI棋子要等待AI计算完毕后才一起显示出来，影响体验
* 算法有待优化采用$\alpha-\beta$剪枝法的AI计算时间太长，导致只能把搜索深度设的很低（只有2层），所以AI不够智能
## 参考文献
ChessAI.py 中的打分思路参考了博客https://www.cnblogs.com/webRobot/p/5817740.html中的思路
