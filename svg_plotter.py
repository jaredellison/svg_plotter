#!/usr/bin/env python
#coding:utf-8
#
# Author:  Jared Ellison
# Site:  jaredellison.net
# Purpose: Drawing frequency response bode plots from Room EQ Wizard data in SVG
# Created: 03.25.2018
#
# Adapted from basic_shapes.py script provided with svgwrite-master module

# requirements.txt file is provided to install proper modules
# run pip command in project directory to install everything:
# pip install -r requirements.txt

import svgwrite
from svgwrite import px

from math import log10, floor, pow, ceil

import datasets

# size of graph
g_size_x = 700
g_size_y = 300

# offset from left side and top of image
g_offset_x = 120
g_offset_y = 10

# the frequency range of the graph in Hz
freq_min = 20
freq_max = 20000

# amplitude range of the graph in dB
amp_min = 60
amp_max = 95

# total size of the generated svg including space for a legend
tot_size_x = 1000
tot_size_y = 600

# output file name
filename = 'svg_output/output_plot.svg'

# graph label font
graph_label_font = {
'font_family':'sans-serif',
'font_size':'12',
'font_color':'black'
}

# list of colors to be applied to traces
color_list = ['red','orange','yellow','green','blue','indigo','violet']

# main drawing object to be modified
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
    '''
    This function draws a point on the graph. The inputs are in x and y, to plot a
    point based on frequency and amplitude, use the log scale function to convert it.
    '''
    
    # Skip points that are out of range
    if x <= x_start or x >= x_end or y <= y_start or y >= y_end:
        return

    dot = dwg.circle(center=(x*px, y*px), r='2px', fill=color, stroke=color, stroke_width=2)
    svg_group.add(dot)

def draw_background(
    start_x = g_offset_x, 
    start_y = g_offset_y, 
    x_size = g_size_x, 
    y_size = g_size_y):
    '''
    This function draws a rectangle behind the plotting area.
    Call this function first so it's in the background.
    '''

    background_fill = '#eaeaea'
    background_stroke = '#000000'
    background_stroke_width = 1

    shapes.add(dwg.rect(
        insert=(start_x*px, start_y*px),
        size=(x_size*px, y_size*px),
        fill=background_fill,
        stroke=background_stroke,
        stroke_width=background_stroke_width))

def draw_h_lines(
    amp_min=amp_min, 
    amp_max=amp_max,
    svg_group=scale_lines,
    g_offset_x=g_offset_x,
    g_offset_y=g_offset_y):
    '''
    This function draws horizontal markers on the graph based on the range of amplitudes
    plotted. Stroke thickness depends on multiples of 10, 5 and 1. The function returns
    a list of horizontal lines plotted to help figure out where to put a label.
    '''

    line_coords = []
    for a in range(amp_min,amp_max):
        line_start = log_scale(freq_min,a)
        line_end = log_scale(freq_max,a)
        
        # Add to the list of lines
        line_coords.append([a,(line_start,line_end)])

        # Change the stroke width depending if it's a multiple of 10, 5 or 1
        if a % 10 == 0:
            line = dwg.line(start=line_start, end=line_end, stroke_width=1) 
        elif a % 5 == 0:
            line = dwg.line(start=line_start, end=line_end, stroke_width=.5)
        else:
            line = dwg.line(start=line_start, end=line_end, stroke_width=.25)        

        # Draw the line
        svg_group.add(line)

    return line_coords

def draw_v_lines(
    freq_min=freq_min, 
    freq_max=freq_max, 
    svg_group=scale_lines, 
    g_offset_x=g_offset_x, 
    g_offset_y=g_offset_y):
    '''
    This function draws vertical markers on the graph based on the range of frequencies
    plotted. For a bode plot with a logarithmic scale, we're interested in major markers at
    powers of 10 and minor markers at integer multiples of that power of 10 leading up
    to the next marker:
    10^n * 1, 10^n * 2, 10^n * 3 ... 10^n+1 * 1
    Strokes are thicker at powers of 10. The function returns a list of vertical lines 
    plotted to help figure out where to put a label.
    '''

    # list of frequencies to mark with vertical lines
    vlines = []

    # a list to track the frequencies plotted and the start and end points of the line
    # this is for figuring out where to draw a label
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
        line_end = log_scale(vlines[i],amp_min)

        line_coords[i].append((line_start,line_end))

        # use a thicker stroke for powers of 10
        if str(vlines[i]).startswith('10'): 
            line = dwg.line(start=line_start, end=line_end, stroke_width=1)
        else: 
            line = dwg.line(start=line_start, end=line_end, stroke_width=.25)

        svg_group.add(line)

    return line_coords

    # print('Line coords post loop: ')
    # for l in line_coords: print(l)

def draw_lable(
    text, 
    x, 
    y, 
    rotate, 
    svg_group=line_labels, 
    font_family='', 
    font_size='', 
    font_color=''):

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

def draw_axis_lable(
    text, 
    x, 
    y, 
    rotate, 
    svg_group=line_labels, 
    font_family='', 
    font_size='', 
    font_color=''):

    msg = dwg.text(
    text,
    insert=(x,y),
    font_family=font_family,
    font_size=font_size,
    fill=font_color)

    msg.rotate(rotate,(x,y))

    svg_group.add(msg)

# Draw graph background first
draw_background()

# Draw markers and capture the lists of lines drawn
hline_list = draw_h_lines()
vline_list = draw_v_lines()

# Label makers and axes
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