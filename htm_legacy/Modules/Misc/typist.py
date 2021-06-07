import pygame, sys
from pygame.locals import *

k_pressed = False
m_pressed = False


def check_press(k):
    global k_pressed
    pressed = pygame.key.get_pressed()
    if not k_pressed and pressed[k]:
        k_pressed = True
    elif k_pressed and (not pressed[k]):
        k_pressed = False
        return True
    return False

def check_click(obj):
    global m_pressed
    if not m_pressed and pygame.mouse.get_pressed()[0]:
        if obj.collidepoint(pygame.mouse.get_pos()):
            m_pressed = True
            return True
    elif m_pressed and (not pygame.mouse.get_pressed()[0]):
        m_pressed = False
    return False
