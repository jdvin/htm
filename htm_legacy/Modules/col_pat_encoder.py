import pygame, sys
from pygame.locals import *
import numpy as np
from Modules.Misc import colours as col
from Modules.Misc import typist
from Modules import master_values as mv
from Modules.Misc.shape import shape

class col_pat_encoder():

    m_pressed = False

    #is this making all a pointer to the first one?
    #try building the list through appending an empty initial list (see input space)
    # patterns = [[col_tile([100,50], [50,50], col.BLACK)]*4]*5

    patterns = [
               [shape("rect",[100,50], [50,50], col.BLACK),
                shape("rect", [175,50], [50,50], col.BLACK),
                shape("rect", [250,50], [50,50], col.BLACK),
                shape("rect", [325,50], [50,50], col.BLACK)],

               [shape("rect", [100,125], [50,50], col.BLACK),
                shape("rect", [175,125], [50,50], col.BLACK),
                shape("rect", [250,125], [50,50], col.BLACK),
                shape("rect", [325,125],[50,50], col.BLACK)],

               [shape("rect", [100,200], [50,50], col.BLACK),
                shape("rect", [175,200], [50,50], col.BLACK),
                shape("rect", [250,200], [50,50], col.BLACK),
                shape("rect", [325,200],[50,50], col.BLACK)],

               [shape("rect", [100,275], [50,50], col.BLACK),
                shape("rect", [175,275], [50,50], col.BLACK),
                shape("rect", [250,275], [50,50], col.BLACK),
                shape("rect", [325,275],[50,50], col.BLACK)],

               [shape("rect", [100,350], [50,50], col.BLACK),
                shape("rect", [175,350], [50,50], col.BLACK),
                shape("rect", [250,350], [50,50], col.BLACK),
                shape("rect", [325,350],[50,50], col.BLACK)],
               ]

    is_active = [
                 [shape("rect", [0,0], [20,20], col.BLACK), False],
                 [shape("rect", [0,0], [20,20], col.BLACK), False],
                 [shape("rect", [0,0], [20,20], col.BLACK), False],
                 [shape("rect", [0,0], [20,20], col.BLACK), False],
                 [shape("rect", [0,0], [20,20], col.BLACK), False]
                ]

    actv = []
    origin = [0, 0]
    current_bucket = [0, 0]

    buckets = []


    def __init__(self):
        b_size = mv.ip_size / mv.n_cols
        for i in np.arange(0, mv.ip_size, b_size):
            t_bucket = np.arange(i, i+b_size)
            self.buckets.append([int(n) for n in t_bucket])

        for i in range(len(self.patterns)):
            self.is_active[i][0].rect[0] = 25
            self.is_active[i][0].rect[1] = self.patterns[i][0].rect[1]+int(self.patterns[i][0].rect[2]/3.5)

        #o_pos = self.patterns[0][0].rect.copy()
        # y = o_pos[1]
        # for i in range(len(self.patterns)):
        #     x = o_pos[0]
        #     for j in range(len(self.patterns[i])):
        #         self.patterns[i][j].rect[0] = x
        #         self.patterns[i][j].rect[1] = y
        #         print(self.patterns[i][j].rect)
        #         x += 75

    def cycle_active(self):
        for i in range(len(self.is_active)):
            if typist.check_click(self.is_active[i][0].rect):
                self.is_active[i][1] = not self.is_active[i][1]

    def iterate_col(self, t):
        if t.col == col.BLACK:
            return col.RED
        elif t.col == col.RED:
            return col.GREEN
        elif t.col == col.GREEN:
            return col.BLUE
        elif t.col == col.BLUE:
            return col.YELLOW
        elif t.col == col.YELLOW:
            return col.BLACK

    def cycle_tile(self):
        for i in range(len(self.patterns)):
            for j in range(len(self.patterns[i])):
                t = self.patterns[i][j]
                if typist.check_click(t.rect):
                    t.col = self.iterate_col(t)

    def iterate(self, c_b):
        #c_b[0] = index in 'actv'
        #c_b[1] = patterns[actv[c_b[0]]][i]

        if c_b == self.origin:
            self.actv = [i for i, x in enumerate(self.is_active) if x[1]]
            if len(self.actv) > 0:
                self.origin = [self.actv[0], 0]
            else:
                return [0,0]
        if c_b[1] == (len(self.patterns[self.actv[c_b[0]]])-1):
            c_b[0] += 1
            c_b[1] = 0
            if c_b[0] == (len(self.actv)):
                return self.origin
        else:
            c_b[1] += 1
        ret = [self.actv[c_b[0]], c_b[1]]
        return ret

    def encode(self, c_b, p, bs):
        if self.is_active[c_b[0]][1]:
            if p[c_b[0]][c_b[1]].col == col.RED:
                b = 0
            elif p[c_b[0]][c_b[1]].col == col.YELLOW:
                b = 1
            elif p[c_b[0]][c_b[1]].col == col.GREEN:
                b = 2
            elif p[c_b[0]][c_b[1]].col == col.BLUE:
                b = 3
            i_v = [0] * mv.ip_size
            for i in range(len(bs[b])):
                i_v[bs[b][i]] = 1
            return i_v

    def get_next_bucket(self):
        self.current_bucket = self.iterate(self.current_bucket)
        return(self.encode(self.current_bucket, self.patterns, self.buckets))

    def update(self):
        self.cycle_active()
        self.cycle_tile()

    def draw(self, display):
        ct = self.patterns[self.current_bucket[0]][self.current_bucket[1]]
        highlight_rect = Rect(ct.rect[0]-5, ct.rect[1]-5, 60, 60)
        pygame.draw.rect(display, col.GREY, highlight_rect)
        for i in range(len(self.patterns)):
            if self.is_active[i][1]:
                t_col = col.GREEN
            else:
                t_col = col.BLACK

            pygame.draw.rect(display, t_col, self.is_active[i][0].rect)
            for j in range(len(self.patterns[i])):
                pygame.draw.rect(display, self.patterns[i][j].col, self.patterns[i][j].rect)
