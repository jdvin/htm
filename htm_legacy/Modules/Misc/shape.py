import pygame, sys
from pygame.locals import *

class shape():
    def __init__(self, shape, pos, dim, col):
        self.pos = pos
        self.dim = dim
        if shape == "rect":
            self.rect = Rect(self.pos[0], self.pos[1], self.dim[0], self.dim[1])
        elif shape == "circ":
            self.circ = [[self.pos[0], self.pos[1]], self.dim]
        self.col = col
