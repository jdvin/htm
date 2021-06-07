import pygame, sys
from pygame.locals import *
import math as m
from Modules import master_values as mv
from Modules.Misc import colours as col
from Modules.Misc import supporting_functions as s_f

class display_tile():

    def __init__(self, pos, dim, col):
        self.rect = Rect(pos[0], pos[1], dim[0], dim[1])
        self.pos = pos
        self.col = col

class visualiser():

    input_space = []

    spatial_pool = []

    output_pool = []

    v_p_synapses = []

    distal_synapses = []

    ADC_vis = []

    def __init__(self):
        #initialise input space
        #divide the total size of the input space by the square root of the number of input tiles to dive size of each tile
        ip_tile_size = int(mv.input_space_size/m.sqrt(mv.ip_size))
        x,y = mv.input_space_location[0], mv.input_space_location[1]
        for i in range(mv.ip_size):
            self.input_space.append(display_tile([x,y], [ip_tile_size, ip_tile_size], col.BLACK))
            x += ip_tile_size
            if x - mv.input_space_location[0] > mv.input_space_size:
                y += ip_tile_size
                x = mv.input_space_location[0]

        # #initialise spatial pool
        # sp_tile_size = int(mv.sp_layer_size/m.sqrt(mv.spl_cols))
        # for i in range(mv.col_depth):
        #     x,y = mv.sp_layer_location[i][0], mv.sp_layer_location[i][1]
        #     for j in range(mv.spl_cols):
        #         self.spatial_pool.append(display_tile([x,y], [sp_tile_size, sp_tile_size], col.BLACK))
        #         x += sp_tile_size
        #         if x - mv.sp_layer_location[i][0] > mv.sp_layer_size:
        #             y += sp_tile_size
        #             x = mv.sp_layer_location[i][0]

        sp_tile_size = int(mv.sp_layer_size/m.sqrt(mv.spl_cols))
        x,y = mv.sp_layer_location[0][0], mv.sp_layer_location[0][1]
        for j in range(mv.spl_cols):
            self.spatial_pool.append(display_tile([x,y], [sp_tile_size, sp_tile_size], col.BLACK))
            x += sp_tile_size
            if x - mv.sp_layer_location[0][0] > mv.sp_layer_size:
                y += sp_tile_size
                x = mv.sp_layer_location[0][0]

        #initialise output pool
        output_tile_size = int(mv.sp_layer_size/m.sqrt(mv.spl_cols))
        x,y = mv.sp_layer_location[2][0], mv.sp_layer_location[2][1]
        for j in range(mv.spl_cols):
            self.output_pool.append(display_tile([x,y], [output_tile_size, output_tile_size], col.BLACK))
            x += sp_tile_size
            if x - mv.sp_layer_location[2][0] > mv.sp_layer_size:
                y += sp_tile_size
                x = mv.sp_layer_location[2][0]

        #initialise ADC visualisation
        ADC_tile_size = int(mv.ADC_vis_size/m.sqrt(mv.spl_cols))
        x,y = mv.ADC_vis_location[0], mv.ADC_vis_location[1]
        for i in range(mv.spl_cols):
            self.ADC_vis.append(display_tile([x,y], [ADC_tile_size, ADC_tile_size], col.BLACK))
            x += ADC_tile_size
            if x - mv.ADC_vis_location[0] > mv.ADC_vis_size:
                y += ADC_tile_size
                x = mv.ADC_vis_location[0]

    #initialise v_p_synapses as a 3D array which contains:
    #[0(column number in pool), 1(synapse number in column), 2(colour)]
    def init_prox_synapses(self, pool):
        for i in range(len(pool)):
            for j in pool[i].p_synapses:
                self.v_p_synapses.append([i, j, col.RED])
    #assign colour values to synapses dependent on their connection to
    #activated input and corresponding pool tiles
    def update_prox_synapses(self, _pool, _active_cortex):
        # FOR column[i] in  _pool
        for i in range(len(_pool)):
            #index of current position in _pool[i].p_synapses
            _j = 0
            for j in _pool[i].p_synapses:
                #columnOfSynapseToChange = numSynapsesIn(currentColumn)*indexOfColumn)+indexCurrentSynapse
                n = (len(_pool[i].p_synapses)*i) + _j
                _j+=1
                if self.input_space[j].col == col.GREEN and s_f.is_active([i], _active_cortex[0]):
                    self.v_p_synapses[n][2] = col.GREEN
                else:
                    self.v_p_synapses[n][2] = col.RED

    def update_space(self, _input):
        for i in range(len(_input)):
            if _input[i] == 0:
                self.input_space[i].col = col.BLACK
            else:
                self.input_space[i].col = col.GREEN

    #UPDATE VISUALISER TO REFLECT NEW ACTIVATION REPRESENTATONS (AS INDEXES)
    def update_pool(self, _pool, _active_cortex):
        # for i in range(mv.col_depth):
        #     for j in range(len(_pool)):
        #         n = (mv.spl_cols*i)+j
        #         #print("layer", i, "column", j, "visualiser", n)
        #         if s_f.is_active([j], _active_cortex[0]):
        #             self.spatial_pool[n].col = col.BLUE
        #         else:
        #             self.spatial_pool[n].col = col.BLACK

        for i in range(len(_pool)):
            #print("layer", i, "column", j, "visualiser", n)
            if s_f.is_active([i], _active_cortex[0]):
                self.spatial_pool[i].col = col.BLUE
            else:
                self.spatial_pool[i].col = col.BLACK

    def update_output_pool(self, _pool, _active_segments):
        for i in range(len(_pool)):
            if len(s_f.segments_in_col(i, _active_segments[0])) > 0:
                self.output_pool[i].col = col.RED
            else:
                self.output_pool[i].col = col.BLACK


    def update_ADC(self, _pool):
        for i in range(len(_pool)):
            g_val = (_pool[i].boost / mv.max_boost) * 255
            r_val = (-255 *(_pool[i].boost / mv.max_boost) + 255)
            self.ADC_vis[i].col = (r_val, g_val, 0)

    def update(self, _input, _pool, _active_cortex, _active_segments):
        self.update_space(_input)
        self.update_pool(_pool, _active_cortex)
        self.update_output_pool(_pool, _active_segments)
        self.update_prox_synapses(_pool, _active_cortex)
        self.update_ADC(_pool)

    def draw(self, display):
        [pygame.draw.line(display, ds[2], self.spatial_pool[ds[0]].pos, self.input_space[ds[1]].pos) for ds in self.v_p_synapses if ds[2] == col.GREEN]
        [pygame.draw.rect(display, i.col, i.rect) for i in self.input_space]
        for s in self.spatial_pool:
            if s.col == col.BLUE:
                pygame.draw.rect(display, s.col, s.rect)
            else:
                pygame.draw.rect(display, s.col, s.rect, 1)
        for o in self.output_pool:
            if o.col == col.RED:
                pygame.draw.rect(display, o.col, o.rect)
            else:
                pygame.draw.rect(display, o.col, o.rect, 1)
        for i in range(len(self.ADC_vis)):
            pygame.draw.rect(display, self.ADC_vis[i].col, self.ADC_vis[i].rect)
        #[pygame.draw.rect(display, a.col. a.rect) for a in self.ADC_vis]
        #[pygame.draw.rect(display, s.col, s.rect) for s in self.spatial_pool]
