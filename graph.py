#!/usr/bin/env python
#coding:utf-8
# Author:  lucky_bloop
# Purpose: graphing microphone freqeuncy response
# Created: 03.25.2018

# Adapted from basic_shapes.py script provided with svgwrite-master
#

# try:
#     import svgwrite
# except ImportError:
#     # if svgwrite is not 'installed' append parent dir of __file__ to sys.path
#     import sys, os
#     sys.path.insert(0, os.path.abspath(os.path.split(os.path.abspath(__file__))[0]+'/..'))

import svgwrite
from svgwrite import px

from math import log10, floor, pow, ceil

import datasets

# size of graph
g_size_x = 700
g_size_y = 300

g_offset_x = 120
g_offset_y = 10

# the frequency spread of the graph in Hz
freq_min = 20
freq_max = 20000

# amplitude spread of the graph in dB
amp_min = 60
amp_max = 95

# total size of the generated svg including space for a legend
tot_size_x = 1000
tot_size_y = 600

filename = 'svg_output/graph.svg'

# Graph Labels
graph_label_font = {
'font_family':'sans-serif',
'font_size':'12',
'font_color':'black'
}

color_list = ['red','orange','yellow','green','blue','indigo','violet']

dwg = svgwrite.Drawing(filename=filename, size=(tot_size_x*px, tot_size_y*px), debug=True)

# .g() adds a group of items
shapes = dwg.add(dwg.g(id='shapes'))

trace = dwg.add(dwg.g(id='trace'))

scale_lines = dwg.add(dwg.g(id='scale_lines', fill='grey', stroke='grey'))

line_labels = dwg.add(dwg.g(id='labels', fill='black'))


def log_scale(
    f,
    a,
    f_start=freq_min,
    f_end=freq_max, 
    x_start=g_offset_x, 
    x_end=(g_offset_x+g_size_x), 
    a_min=amp_min, 
    a_max=amp_max, 
    y_start=g_offset_y, 
    y_end=(g_size_y+g_offset_y)):
    '''
    This function takes a frequency (Hz) and amplitude (dB) and outputs an x,y coordinate
    pair as a tuple. 
    '''

    # Scale frequency input to a fraction of the specified spectrum
    x = ((log10(f)-log10(freq_min))/(log10(freq_max) - log10(freq_min)))
    # Apply that fraction to the width of the graph
    x = (x * (x_end-x_start)) + x_start
   

    y = (a - a_min)/(a_max - a_min)
    y = y * (y_end-y_start)
    y = ((y_end-y_start) - y) + y_start
    return (x, y)

def draw_point(
    x,
    y,
    svg_group=trace,
    x_start=g_offset_x, 
    x_end=(g_offset_x+g_size_x),
    y_start=g_offset_y, 
    y_end=(g_offset_y+g_size_y),
    color=''):
    
    # Skip points that are out of range
    if x <= x_start or x >= x_end or y <= y_start or y >= y_end:
        return

    dot = dwg.circle(center=(x*px, y*px), r='2px', fill=color, stroke=color, stroke_width=2)
    svg_group.add(dot)

def draw_background(start_x = g_offset_x, start_y = g_offset_y, x_size = g_size_x, y_size = g_size_y):
    shapes.add(dwg.rect(insert=(start_x*px, start_y*px), size=(x_size*px, y_size*px), fill='#eaeaea', stroke='#000000', stroke_width=1))

def draw_h_lines(amp_min=amp_min, amp_max=amp_max, svg_group=scale_lines, g_offset_x=g_offset_x, g_offset_y=g_offset_y):
    line_coords = []
    for i in range(amp_min,amp_max):
        line_start = log_scale(freq_min,i)
        line_end = log_scale(freq_max,i)
        
        line_coords.append([i,(line_start,line_end)])
        if i % 10 == 0:
            line = dwg.line(start=line_start, end=line_end, stroke_width=1)
            # (str(i), insert=None, x=None, y=None, dx=None, dy=None, rotate=None, **extra)      
        elif i % 5 == 0:
            line = dwg.line(start=line_start, end=line_end, stroke_width=.5)
        else:
            line = dwg.line(start=line_start, end=line_end, stroke_width=.25)        
        svg_group.add(line)
    return line_coords

def draw_v_lines(freq_min=freq_min, freq_max=freq_max, svg_group=scale_lines, g_offset_x=g_offset_x, g_offset_y=g_offset_y):
    vlines = []
    # major lines   
    line_coords = []
    f = freq_min 
    while(f <= freq_max):
        power = log10(f)
        power = floor(power)
        step = pow(10, power)
        freq = ceil(f/step) * step
        if not freq > freq_max:
            line_coords.append([freq,])
            vlines.append(ceil(f/step) * step)

        f = f + step

    # print('Line coords pre loop: ' + str(line_coords))

    for i in range(len(vlines)):
        line_start = log_scale(vlines[i],amp_max)
        # print('start  '+str(line_start))
        line_end = log_scale(vlines[i],amp_min)
        # print('end    '+str(line_end))
        line_coords[i].append((line_start,line_end))
        if str(vlines[i]).startswith('10'): 
            # print('starts with' + str(vlines[i]))
            line = dwg.line(start=line_start, end=line_end, stroke_width=1)
        else: 
            # print('else' + str(vlines[i]))
            line = dwg.line(start=line_start, end=line_end, stroke_width=.25)
        svg_group.add(line)

    return line_coords

    # print('Line coords post loop: ')
    # for l in line_coords: print(l)

def draw_lable(text, x, y, rotate, svg_group=line_labels, font_family='', 
    font_size='', font_color=''):
    msg = dwg.text(
    text,
    insert=(x,y),
    font_family=font_family,
    font_size=font_size,
    fill=font_color)

    msg.rotate(rotate,(x,y))

    svg_group.add(msg)

def add_v_labels(line_list, label_font):
    for item in line_list:
        text = int(item[0])
        end_point = item[1][1]
        y_offset = 10
        rotation = 45
        # print('text: ' + str(text) + ' end_point: ' + str(end_point))
        if str(text).startswith('1') or str(text).startswith('5'):
            draw_lable(text, end_point[0], end_point[1] + y_offset, rotation, **label_font)

def add_h_labels(line_list, label_font):
    for item in line_list:
        text = int(item[0])
        start_point = item[1][0]
        x_offset = -20
        y_offset = 4
        rotation = 0
        # print('text: ' + str(text) + ' end_point: ' + str(end_point))
        if text % 5 == 0:
            draw_lable(text, start_point[0]+x_offset, start_point[1]+y_offset, rotation, **label_font)

def draw_axis_lable(text, x, y, rotate, svg_group=line_labels, font_family='', 
    font_size='', font_color=''):
    msg = dwg.text(
    text,
    insert=(x,y),
    font_family=font_family,
    font_size=font_size,
    fill=font_color)

    msg.rotate(rotate,(x,y))

    svg_group.add(msg)

draw_background()

hline_list = draw_h_lines()

print(hline_list)

vline_list = draw_v_lines()

add_v_labels(vline_list, graph_label_font)

draw_axis_lable('Frequency in Hz', g_size_x + g_offset_x + 30, g_size_y + g_offset_y + 10, 0, **graph_label_font)

add_h_labels(hline_list, graph_label_font)

draw_axis_lable('Amplitude in dB', g_offset_x - 90, g_offset_y + 5, 0, **graph_label_font)


paths = dwg.add(dwg.g(id='path', stroke_width=2, fill='white', fill_opacity="0"))
dots = dwg.add(dwg.g(id='dots', stroke_width=1, stroke='cornflowerblue', fill='cornflowerblue'))


import bspline_maker

def plot_path(dataset):
    log_points = []
    print(dataset)
    for pair in dataset:
        entry = list(log_scale(*pair))
        log_points.append(entry)

    return bspline_maker.make_curve(log_points)

for response in datasets.responses:
    path_string = plot_path(response)
    paths.add(dwg.path(d=path_string,stroke='orange'))


# for pair in datasets.responses[0]:
#     draw_point(*log_scale(*pair), color='orange')

# for pair in datasets.responses[1]:
#     draw_point(*log_scale(*pair), color='blue')



dwg.save()
