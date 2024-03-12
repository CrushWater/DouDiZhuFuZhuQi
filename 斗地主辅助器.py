import pygame
from pygame.locals import *
import sys


"""
owner:
    0:本家
    1:下家
    2:上家
    
按键:
    r:重新开始
    Enter:出牌
    
state:
    0:选择地主
    1:选择Player0的牌
    2:轮换出牌
"""


WIDTH, HEIGHT = 1000, 600
cards_width = int(WIDTH * 0.8)
cards_height = int(HEIGHT * 0.7 / 15)
card_width, card_height = cards_height - 5, cards_height - 5
font_size = card_height - 2
player_0_pos = (10, HEIGHT-80)
player_1_pos = (WIDTH-90, 10)
player_2_pos = (10, 10)
player_0_cards_pos = (player_0_pos[0]+80, player_0_pos[1]-card_height)
all_cards_pos = (int(WIDTH * 0.1), 30)


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("斗地主辅助器")
font = pygame.font.Font("阿里妈妈刀隶体.ttf", font_size)
clock = pygame.time.Clock()

card_dict = [3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10,
             'J', 'J', 'J', 'J', 'Q', 'Q', 'Q', 'Q', 'K', 'K', 'K', 'K',
             'A', 'A', 'A', 'A', 2, 2, 2, 2, "小王", "大王"]
card_dict_2 = {3:0, 4:1, 5:2, 6:3, 7:4, 8:5, 9:6, 10:7, 'J':8, 'Q':9, 'K':10, 'A':11, 2:12, "小王":13, "大王":14}
card_dict_3 = ['3', '4', '5', '6', '7', '8', '9', "10", 'J', 'Q', 'K', 'A', '2', "小王", "大王"]

class Card:
    def __init__(self, value, width, height, owner, p):
        self.value = value
        self.width = width
        self.height = height
        self.img = font.render(str(value), True, (0, 0, 0))
        self.owner = owner
        self.p = p

    def change_owner(self, owner):
        self.owner = owner

    def change_p(self, p):
        self.p = p


class All_cards:
    def __init__(self, other_cards):
        self.all_cards = []
        other_card_num = [0] * 15
        for i in range(len(other_cards)):
            if other_cards[i]:
                other_card_num[card_dict_2[card_dict[i]]] += 1
        for i in range(15):
            if i < 13:
                self.all_cards.append(Cards(i, cards_width, cards_height, 4-other_card_num[i]))
            else:
                self.all_cards.append(Cards(i, cards_width, cards_height, 1-other_card_num[i]))

    def landowner_cards(self, cards, landowner):
        for i in range(len(cards)):
            if cards[i]:
                self.all_cards[card_dict_2[card_dict[i]]].change_to_landowner(landowner)

    def show(self, screen, pos):
        for i in range(15):
            self.all_cards[i].show(screen, (pos[0], pos[1] + i * cards_height))
        pygame.draw.rect(screen, (0, 0, 0), (pos[0], pos[1], cards_width, cards_height * 15), 1)
        for i in range(1, 7):
            pygame.draw.line(screen, (0, 0, 0), (int(i * cards_width / 7)+pos[0], pos[1]),
                             (int(i * cards_width / 7)+pos[0], cards_height * 15+pos[1]))

    def choose(self, x, y, is_selected):
        self.all_cards[y // cards_height].choose(x, is_selected)

    def run(self, player):
        running_cards = []
        for i in range(15):
            self.all_cards[i].run(running_cards, player)
        return running_cards

    def change_p(self, card, value, player, index):
        # 参数1：要改变概率的牌
        # 参数2：要改变的概率
        # 参数3：出牌的人
        # 参数4：要改变的牌的 state 值的大小顺序
        if player == 1:
            self.all_cards[card].change_p(value, index)
        else:
            self.all_cards[card].change_p(-value, -index-1)


class Cards:
    def __init__(self, value, width, height, num):
        self.value = value
        self.card_font = font.render(str(card_dict_3[value]), True, (0, 0, 0))
        self.width = width
        self.height = height
        self.num = num
        self.state = [3.] * num
        self.selecting = [0] * num
        """
        state:
            0:上家已出
            1：一定属于上家
            2-2.9：可能属于上家
            3：未知
            4-4.9：可能属于下家
            5：一定属于下家
            6：下家已出
        """
        self.surface = pygame.Surface((cards_width, cards_height))
        self.update_surface()

    def change_to_landowner(self, landowner):
        for i in range(self.num):
            if self.state[i] == 3:
                self.state[i] = 5 if landowner == 1 else 1
                self.update_surface()
                break

    def show(self, screen, pos):
        screen.blit(self.surface, pos)

    def update_surface(self):
        now_area = -1
        self.surface.fill((255, 255, 255))
        for i in range(self.num):
            if now_area != int(self.state[i]):
                now_area = int(self.state[i])
                pos_x = 0
            else:
                pos_x += card_width

            self.surface.blit(self.card_font, (int(now_area * cards_width / 7 + pos_x), 0))
            if self.selecting[i]:
                pygame.draw.rect(self.surface, (0, 0, 255), (int(now_area * cards_width / 7 + pos_x), 0, 20, 20), 1)

    def sort(self):
        for i in range(self.num):
            for j in range(self.num - 1):
                if self.state[j] > self.state[j + 1]:
                    self.state[j], self.state[j + 1] = self.state[j + 1], self.state[j]
                    self.selecting[j], self.selecting[j + 1] = self.selecting[j + 1], self.selecting[j]
        self.update_surface()

    def choose(self, x, is_selected):
        choose_area = x // (cards_width / 7)
        for i in range(self.num):
            if int(self.state[i]) >= choose_area:
                break
        i += int((x % (cards_width / 7)) / card_width)
        if i < self.num and int(self.state[i]) == choose_area and choose_area != 0 and choose_area != 6:
            self.selecting[i] = is_selected
        self.update_surface()

    def run(self, running_cards, player):
        for i in range(self.num):
            if self.selecting[i]:
                running_cards.append(self.value)
                self.selecting[i] = 0
                if player == 1:
                    self.state[i] = 6
                elif player == 2:
                    self.state[i] = 0
        self.sort()

    def change_p(self, value, index):
        i = 0
        if index >= 0:
            for i in range(self.num):
                if self.state[i] != 0:
                    if (0 <= i + index < self.num) and 2 <= self.state[i + index] < 5:
                        self.state[i + index] += value
                        if self.state[i + index] >= 5:
                            self.state[i + index] = 4.9
                        if self.state[i + index] < 2:
                            self.state[i + index] = 2
                        if 3 < self.state[i + index] < 4:
                            if value > 0:
                                self.state[i + index] += 0.9
                            elif value < 0:
                                self.state[i + index] -= 0.9
                    break
        else:
            for i in range(self.num - 1, -1, -1):
                if self.state[i] != 6:
                    index += 1
                    if (0 <= i + index < self.num) and 2 <= self.state[i + index] < 5:
                        self.state[i + index] += value
                        if self.state[i + index] >= 5:
                            self.state[i + index] = 4.9
                        if self.state[i + index] < 2:
                            self.state[i + index] = 2
                        if 3 < self.state[i + index] < 4:
                            if value > 0:
                                self.state[i + index] += 0.9
                            elif value < 0:
                                self.state[i + index] -= 0.9
                    break

        self.sort()


class Player:
    def __init__(self, player, is_landowner):
        self.player = player
        self.card_num = 20 if is_landowner else 17
        self.is_landowner = is_landowner
        self.surface = pygame.Surface((80, 60))
        self.update_surface()
        self.run_cards = []  # 已经出过的牌

    def update_surface(self):
        self.surface.fill((255, 255, 255))
        self.surface.blit(font.render("Player_"+str(self.player), True, (0 ,0 , 0)), (0, 0))
        self.surface.blit(font.render(str(self.card_num), True, (0, 0, 0)), (0, 30))
        if self.is_landowner:
            self.surface.blit(font.render("地主", True, (0, 0, 0)), (40, 30))

    def show(self, screen, pos, turn):
        screen.blit(self.surface, pos)
        if turn == self.player:
            pygame.draw.rect(screen, (0, 0, 255), (pos[0], pos[1], 80, 60), 3)
        for i in range(len(self.run_cards)):
            screen.blit(font.render(self.run_cards[i], True, (0, 0, 0)), (pos[0], pos[1]+i*20+70))

    def run(self, all_cards):
        # 出牌
        running_cards = all_cards.run(self.player)
        self.card_num -= len(running_cards)
        self.update_surface()

        s = ""
        for i in range(len(running_cards)):
            s += card_dict_3[running_cards[i]]
        self.run_cards.append(s)

        # 检测出牌类型，并修改概率
        cards_hash = [0] * 15
        for i in range(len(running_cards)):
            cards_hash[running_cards[i]] += 1
        nums_hash = [0] * 5
        for i in range(15):
            nums_hash[cards_hash[i]] += 1

        # 单张
        if nums_hash[1] == 1 and nums_hash[2] == 0 and nums_hash[3] == 0 and nums_hash[4] == 0:
            for i in range(13):
                if cards_hash[i]:
                    all_cards.change_p(i, -0.1, self.player, 0)
                    break
            if cards_hash[13]:
                all_cards.change_p(14, -0.1, self.player, 0)
            if cards_hash[14]:
                all_cards.change_p(13, -0.1, self.player, 0)
        # 对子
        if nums_hash[1] == 0 and nums_hash[2] == 1 and nums_hash[3] == 0 and nums_hash[4] == 0:
            for i in range(13):
                if cards_hash[i]:
                    all_cards.change_p(i, -0.1, self.player, 0)
                    all_cards.change_p(i, -0.1, self.player, 1)
                    break

        # 三带一
        if nums_hash[1] == 1 and nums_hash[2] == 0 and nums_hash[3] == 1 and nums_hash[4] == 0:
            for i in range(13):
                if cards_hash[i] == 3:
                    all_cards.change_p(i, -0.3, self.player, 0)
                if cards_hash[i] == 1:
                    all_cards.change_p(i, -0.1, self.player, 0)

        # 三带二
        if nums_hash[1] == 0 and nums_hash[2] == 1 and nums_hash[3] == 1 and nums_hash[4] == 0:
            for i in range(13):
                if cards_hash[i] == 3:
                    all_cards.change_p(i, -0.3, self.player, 0)
                if cards_hash[i] == 2:
                    all_cards.change_p(i, -0.1, self.player, 0)
                    all_cards.change_p(i, -0.1, self.player, 1)

        # 顺子
        if nums_hash[1] >= 5 and nums_hash[2] == 0 and nums_hash[3] == 0 and nums_hash[4] == 0:
            for i in range(8):  # 最多就是从10开始
                if cards_hash[i]:
                    if i > 0:
                        all_cards.change_p(i-1, -0.1, self.player, 0)
                    if i+nums_hash[1] < 12:
                        all_cards.change_p(i+nums_hash[1], -0.1, self.player, 0)
                    break

        # 连对
        if nums_hash[1] == 0 and nums_hash[2] >= 3 and nums_hash[3] == 0 and nums_hash[4] == 0:
            for i in range(10):  # 最多就是从Q开始
                if cards_hash[i]:
                    all_cards.change_p(i, -0.1, self.player, 0)


class Player_0(Player):
    def __init__(self, player, is_landowner, selected_cards):
        super(Player_0, self).__init__(player, is_landowner)
        self.cards = []
        self.cards_surface = pygame.Surface((WIDTH-player_0_cards_pos[0], cards_height))
        self.cards_surface_begin_pos_x = [-1] * 54
        for i in range(54):
            if selected_cards[i]:
                self.cards.append(card_dict[i])
        self.selecting_cards = [0] * len(self.cards)
        self.update_cards_surface()

    def remove_selected_cards(self):
        for i in range(len(self.selecting_cards)-1, -1, -1):
            if self.selecting_cards[i]:
                self.cards.pop(i)
                self.card_num -= 1
        self.selecting_cards = [0] * len(self.cards)
        self.update_cards_surface()
        self.update_surface()

    def update_cards_surface(self):
        self.cards_surface.fill((255, 255, 255))
        cards_draw_begin_pos_x = 0
        self.cards_surface_begin_pos_x = [-1] * (len(self.cards) + 2)
        i = 0
        for i in range(len(self.cards)):
            self.cards_surface.blit(font.render(str(self.cards[i]), True, (0, 0, 0)), (cards_draw_begin_pos_x + 5, 0))
            self.cards_surface_begin_pos_x[i] = cards_draw_begin_pos_x
            if self.cards[i] == 10:
                if self.selecting_cards[i]:
                    pygame.draw.rect(self.cards_surface, (0, 0, 0), (cards_draw_begin_pos_x, 0, card_width + 10, card_height), 1)
                cards_draw_begin_pos_x += card_width + 10
            elif self.cards[i] == "小王" or self.cards[i] == "大王":
                if self.selecting_cards[i]:
                    pygame.draw.rect(self.cards_surface, (0, 0, 0), (cards_draw_begin_pos_x, 0, card_width + 30, card_height), 1)
                cards_draw_begin_pos_x += card_width + 30
            else:
                if self.selecting_cards[i]:
                    pygame.draw.rect(self.cards_surface, (0, 0, 0), (cards_draw_begin_pos_x, 0, card_width, card_height), 1)
                cards_draw_begin_pos_x += card_width
        self.cards_surface_begin_pos_x[i + 1] = cards_draw_begin_pos_x

    def show_cards(self, screen, pos):
        screen.blit(self.cards_surface, pos)

    def show(self, screen, pos, turn):
        screen.blit(self.surface, pos)
        if turn == self.player:
            pygame.draw.rect(screen, (0, 0, 255), (pos[0], pos[1], 80, 60), 3)
        self.show_cards(screen, player_0_cards_pos)

    def choose(self, pos_x, is_selected):
        i = 0
        for i in range(len(self.cards)+1):
            if pos_x < self.cards_surface_begin_pos_x[i]:
                self.selecting_cards[i-1] = 1 if is_selected else 0
                break
        self.update_cards_surface()


# 开始
def state_0():
    running = True
    selected_cards = [0] * 54
    selected_cards_landowner = [0] * 54
    mouse_left_down = False
    mouse_left_change_to = 1
    now_selected_card = -1
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_left_down = True
                    if now_selected_card != -1:
                        if selected_cards[now_selected_card]:
                            mouse_left_change_to = 0
                        else:
                            mouse_left_change_to = 1
                    else:
                        mouse_left_change_to = 1
                elif event.button == 3:
                    selected_cards_landowner[now_selected_card] = 1 - selected_cards_landowner[now_selected_card]
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_left_down = False

                    if 55 < event.pos[0] < 110 and 200 < event.pos[1] < 230:
                        running = False
                        state_1(selected_cards, selected_cards_landowner)
                    if 115 < event.pos[0] < 170 and 200 < event.pos[1] < 230:
                        for i in range(54):
                            selected_cards[i] = 0
                    if 175 < event.pos[0] < 305 and 200 < event.pos[1] < 230:
                        running = False

        pos = pygame.mouse.get_pos()
        if 60 < pos[1] < 180:
            if 10 < pos[0] < 660:
                now_selected_card = (pos[0]-10)//50*4+(3-(pos[1]-60)//30)
            if 660 < pos[0] < 720:
                if 150 < pos[1] < 180:
                    now_selected_card = 52
                elif 120 < pos[1] < 150:
                    now_selected_card = 53
        else:
            now_selected_card = -1

        if mouse_left_down:
            if now_selected_card != -1:
                selected_cards[now_selected_card] = mouse_left_change_to

        screen.fill((255, 255, 255))
        screen.blit(font.render("选择牌（左键选择自己牌，右键选择地主的3张牌）", True, (0, 0, 0)), (20, 20))
        screen.blit(font.render("确定", True, (0, 0, 0)), (60, 200))
        screen.blit(font.render("重选", True, (0, 0, 0)), (120, 200))
        screen.blit(font.render("返回上一步", True, (0, 0, 0)), (180, 200))
        pygame.draw.rect(screen, (0, 0, 0), (55, 200, 55, 30), width=2)
        pygame.draw.rect(screen, (0, 0, 0), (115, 200, 55, 30), width=2)
        pygame.draw.rect(screen, (0, 0, 0), (175, 200, 130, 30), width=2)

        # 显示每张牌
        for i in range(54):
            if i < 52:
                if selected_cards[i] == 1:
                    pygame.draw.rect(screen, (128, 128, 128), (10 + i // 4 * 50, 150 - i % 4 * 30, 40, 25))
                if selected_cards_landowner[i] == 1:
                    pygame.draw.rect(screen, (0, 0, 255), (10 + i // 4 * 50, 150 - i % 4 * 30, 40, 25), 6)
                pygame.draw.rect(screen, (0, 0, 0), (10 + i // 4 * 50, 150 - i % 4 * 30, 40, 25), width=2)
            else:
                if selected_cards[i] == 1:
                    pygame.draw.rect(screen, (128, 128, 128), (10 + i // 4 * 50, 150 - i % 4 * 30, 60, 25))
                if selected_cards_landowner[i] == 1:
                    pygame.draw.rect(screen, (0, 0, 255), (10 + i // 4 * 50, 150 - i % 4 * 30, 60, 25), 6)
                pygame.draw.rect(screen, (0, 0, 0), (10 + i // 4 * 50, 150 - i % 4 * 30, 60, 25), width=2)
            screen.blit(font.render(str(card_dict[i]), True, (0, 0, 0)), (20 + i // 4 * 50, 150 - i % 4 * 30))

        # 刷新屏幕
        pygame.display.flip()
        clock.tick(60)


def state_1(selected_cards, selected_cards_landowner):
    running = True
    landowner = -1
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                # 如果点击按钮，就更改地主
                if 150 <= event.pos[0] <= 250:
                    if 200 <= event.pos[1] <= 250:
                        landowner = 0
                    elif 250 <= event.pos[1] <= 300:
                        landowner = 1
                    elif 300 <= event.pos[1] <= 350:
                        landowner = 2

                # 如果点击开始，就进入下一个状态
                if 20 <= event.pos[0] <= 125 and 500 <=  event.pos[1] <= 545:
                    if landowner != -1:
                        state_2(landowner, selected_cards, selected_cards_landowner)

        screen.fill((255, 255, 255))
        screen.blit(font.render("斗地主辅助器", True, (0, 0, 0)), (20, 20))
        screen.blit(font.render("选择地主", True, (0, 0, 0)), (20, 200))

        # 高亮地主填充红色
        if landowner == 0:
            pygame.draw.rect(screen, (255, 0, 0), (150, 200, 100, 50))
        elif landowner == 1:
            pygame.draw.rect(screen, (255, 0, 0), (150, 250, 100, 50))
        elif landowner == 2:
            pygame.draw.rect(screen, (255, 0, 0), (150, 300, 100, 50))

        # 绘制三个按钮来选择地主
        screen.blit(font.render("本家", True, (0, 0, 0)), (180, 210))
        screen.blit(font.render("下家", True, (0, 0, 0)), (180, 260))
        screen.blit(font.render("上家", True, (0, 0, 0)), (180, 310))
        pygame.draw.rect(screen, (0, 0, 0), (150, 200, 100, 50), 2)
        pygame.draw.rect(screen, (0, 0, 0), (150, 250, 100, 50), 2)
        pygame.draw.rect(screen, (0, 0, 0), (150, 300, 100, 50), 2)

        # 绘制开始游戏按钮
        screen.blit(font.render("开始游戏", True, (0, 0, 0)), (30, 510))
        pygame.draw.rect(screen, (0, 0, 0), (20, 500, 105, 45), 2)

        # 更新屏幕
        pygame.display.flip()
        clock.tick(60)


def state_2(landowner, selected_cards, selected_cards_landowner):
    """"
    功能：
        中间部分显示cards
        顶部显示“出牌”按钮，也可以用Enter键代替；还有退出至state_0按钮，也可以用Esc键代替#######################################
        其他时间可以选择cards里的牌并记录
    """

    player_0 = Player_0(0, (landowner == 0), selected_cards)
    player_1 = Player(1, (landowner == 1))
    player_2 = Player(2, (landowner == 2))
    all_cards = All_cards(selected_cards)
    if landowner != 0:
        all_cards.landowner_cards(selected_cards_landowner, landowner)

    turn = landowner
    mouse_left_down = False
    mouse_right_down = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    state_0()
                if event.key == K_RETURN:
                    if turn == 0:
                        player_0.remove_selected_cards()
                    elif turn == 1:
                        player_1.run(all_cards)
                    elif turn == 2:
                        player_2.run(all_cards)
                    turn = (turn + 1) % 3
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_left_down = True
                if event.button == 3:
                    mouse_right_down = True
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_left_down = False
                if event.button == 3:
                    mouse_right_down = False

        pos = pygame.mouse.get_pos()
        if player_0_cards_pos[0] < pos[0] and player_0_cards_pos[1] < pos[1] < pos[1] + cards_height:
            if mouse_left_down:
                player_0.choose(pos[0] - player_0_cards_pos[0], 1)
            if mouse_right_down:
                player_0.choose(pos[0] - player_0_cards_pos[0], 0)
        if all_cards_pos[0] < pos[0] < all_cards_pos[0] + cards_width and \
           all_cards_pos[1] < pos[1] < all_cards_pos[1] + cards_height * 15:
            if mouse_left_down:
                all_cards.choose(pos[0] - all_cards_pos[0], pos[1] - all_cards_pos[1], 1)
            if mouse_right_down:
                all_cards.choose(pos[0] - all_cards_pos[0], pos[1] - all_cards_pos[1], 0)

        screen.fill((255, 255, 255))

        player_0.show(screen, player_0_pos, turn)
        player_1.show(screen, player_1_pos, turn)
        player_2.show(screen, player_2_pos, turn)
        all_cards.show(screen, all_cards_pos)

        pygame.display.flip()
        clock.tick(60)


state_0()
