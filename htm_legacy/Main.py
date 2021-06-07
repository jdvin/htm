import pygame, sys
from pygame.locals import *
from brain import brain
from Modules.Misc import colours as col

pygame.init()
form_dim = (1500, 1000)
fps = 60
fps_clock = pygame.time.Clock()
display = pygame.display.set_mode(form_dim)

brain = Brain()

def main():
    sim_run = True
    while sim_run:
        # Pygame junk
        for event in pygame.event.get():
            if event.type == QUIT:
                sim_run = False
                break

        # Update
        brain.update(fps)

        # Visual
        display.fill(col.WHITE)
        brain.draw(display, fps)

        # Step
        pygame.display.update()
        fps_clock.tick(fps)

if __name__ == "__main__":
    main()
