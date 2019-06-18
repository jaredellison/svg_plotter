#!/usr/bin/python3
# coding:utf-8
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

# external modules
import bspline_maker
import svgwrite
from svgwrite import px
import numpy as np

# standard library modules
from math import log10, floor, pow, ceil
from colorsys import hls_to_rgb

# project specific modules
import datasets

##################################
#
#   Parameters
#
##################################

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
    'font_family': 'sans-serif',
    'font_size': '12',
    'font_color': 'black'
}

# list of colors to be applied to traces
color_list = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']

# main drawing object to be modified
dwg = svgwrite.Drawing(filename=filename, size=(
    tot_size_x*px, tot_size_y*px), debug=True)

# .g() adds a group of items
shapes = dwg.add(dwg.g(id='shapes'))

trace = dwg.add(dwg.g(id='trace'))

scale_lines = dwg.add(dwg.g(id='scale_lines', fill='grey', stroke='grey'))

line_labels = dwg.add(dwg.g(id='labels', fill='black'))

# set up clip mask to
mask = dwg.mask(id='curveMask')

mask.add(dwg.rect(
        insert=(g_offset_x, g_offset_y),
        size=(g_size_x, g_size_y),
        fill="white"))

dwg.add(mask)


##################################
#
#   Function Definitions
#
##################################


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

    dot = dwg.circle(center=(x*px, y*px), r='2px',
                     fill=color, stroke=color, stroke_width=2)
    svg_group.add(dot)


def draw_background(
        start_x=g_offset_x,
        start_y=g_offset_y,
        x_size=g_size_x,
        y_size=g_size_y):
    '''
    This function draws a rectangle behind the plotting area.
    Call this function first so it's in the background.
    '''

    background_fill = '#fcfcfc'
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
    for a in range(amp_min, amp_max):
        line_start = log_scale(freq_min, a)
        line_end = log_scale(freq_max, a)

        # Add to the list of lines
        line_coords.append([a, (line_start, line_end)])

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

    # Start with the minimum frequency
    f = freq_min
    while(f <= freq_max):
        # figure out which order of magnitude f is in
        power = log10(f)
        power = floor(power)
        # step is used to increment f
        step = pow(10, power)
        freq = ceil(f/step) * step
        if freq < freq_max:
            line_coords.append([freq, ])
            vlines.append(freq)
        # increment f to the next frequency of interest
        f = f + step

    for i in range(len(vlines)):
        line_start = log_scale(vlines[i], amp_max)
        line_end = log_scale(vlines[i], amp_min)

        line_coords[i].append((line_start, line_end))

        # use a thicker stroke for powers of 10
        if str(vlines[i]).startswith('10'):
            line = dwg.line(start=line_start, end=line_end, stroke_width=1)
        else:
            line = dwg.line(start=line_start, end=line_end, stroke_width=.25)
        # draw the line
        svg_group.add(line)

    return line_coords


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
        insert=(x, y),
        font_family=font_family,
        font_size=font_size,
        fill=font_color)

    msg.rotate(rotate, (x, y))

    svg_group.add(msg)


def add_v_labels(line_list, label_font):
    '''
    This function draws labels for vertical markers.
    '''
    for item in line_list:
        text = int(item[0])
        end_point = item[1][1]
        y_offset = 10
        rotation = 45
        if str(text).startswith('1') or str(text).startswith('5'):
            draw_lable(text, end_point[0], end_point[1] +
                       y_offset, rotation, **label_font)


def add_h_labels(line_list, label_font):
    '''
    This function draws labels for horizontal markers.
    '''
    for item in line_list:
        text = int(item[0])
        start_point = item[1][0]
        x_offset = -20
        y_offset = 4
        rotation = 0
        if text % 5 == 0:
            draw_lable(
                text, start_point[0]+x_offset, start_point[1]+y_offset, rotation, **label_font)


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
        insert=(x, y),
        font_family=font_family,
        font_size=font_size,
        fill=font_color)

    msg.rotate(rotate, (x, y))

    svg_group.add(msg)


def angle_to_hex_triplet(rotation, saturation=.5, luminance=.7):
    '''
    This function takes an angle between 0 and 360 and outputs a string of hex for use
    as an html color.

    Rotation is in degrees, saturation and luminance are floats between 0 and 1.

    For example:
    Rotation =   0, Luminance = 0, Saturation = 0 ---> 000000
    Rotation =   0, Luminance = 1, Saturation = 0 ---> FFFFFF
    Rotation =   0, Luminance = .5, Saturation = 1 ---> FF0000
    Rotation = 120, Luminance = .5, Saturation = 1 ---> 00FF00
    Rotation = 240, Luminance = .5, Saturation = 1 ---> 0000FF
    Rotation = 360, Luminance = .5, Saturation = 1 ---> FF0000
    '''

    # Result to return
    res = ''
    rgb_tup = hls_to_rgb((rotation/360), luminance, saturation)
    # print ('rgb_tup', rgb_tup)

    for i in rgb_tup:
        i = int(i * 255)
        hex_s = ''
        hex_s += hex(i)
        if (i * 255) < 16:
            hex_s = '0' + hex_s[-1]
            res += hex_s
        else:
            res += hex_s[-2:]

    return '#' + res


def get_trace_color(total_traces):
    '''
    This generator function is used to establish a sequence of colors that are
    as far away from each other as the size of the dataset allows. Pass it the
    total number of traces in the graph and it will return the next color in html
    hex triplet style every time it is passed to next().
    '''

    for trace in range(total_traces):
        yield angle_to_hex_triplet(trace*(360/total_traces))


##################################
#
#   Main Action
#
##################################

trace_colors = get_trace_color(len(datasets.responses))

# Draw graph background first
draw_background()

# Draw markers and capture the lists of lines drawn
hline_list = draw_h_lines()
vline_list = draw_v_lines()

# Label markers and axes
add_v_labels(vline_list, graph_label_font)

draw_axis_lable('Frequency in Hz', g_size_x + g_offset_x + 30,
                g_size_y + g_offset_y + 10, 0, **graph_label_font)

add_h_labels(hline_list, graph_label_font)

draw_axis_lable('Amplitude in dB', g_offset_x - 90,
                g_offset_y + 5, 0, **graph_label_font)

paths = dwg.add(dwg.g(id='path', stroke_width=2,
                      fill='white', fill_opacity="0", mask="url(#curveMask)"))

# dots = dwg.add(dwg.g(id='dots', stroke_width=1,
#                      stroke='cornflowerblue', fill='cornflowerblue'))

def plot_path(dataset):
    log_points = []
    for pair in dataset:
        entry = list(log_scale(*pair))
        log_points.append(entry)

    return bspline_maker.make_curve(log_points)


# def diagnostic_path(dataset):
#     '''
#     This function is a linear parallel to the plot_path function for troubleshooting.
#     It aims to pass the original dataset values to the bspline_maker.make_curve() function.
#     '''
#     lin_points = []
#     for pair in dataset:
#         print(pair)
#         entry = pair
#         lin_points.append(entry)

#     return bspline_maker.make_curve(lin_points)


# def split_path_string(
#     string_in,

#     ):
#     '''
#     This function takes an svg formated string of control points
#     '''

for response in datasets.responses:
    path_string = plot_path(response)
    d = "M"
    point_list = [d+e for e in path_string.split(d) if e]
    print('log point_list: ')
    [print(segment) for segment in point_list]

    paths.add(dwg.path(d=path_string, stroke=next(trace_colors)))
    # for point in response:
    #     draw_point(*log_scale(*point))


# #
# # This area is for troubleshooting, it does the same as above but just prints
# # the list of points, it doesn't
# for response in datasets.responses:
#     path_string = diagnostic_path(response)
#     d = "M"
#     point_list = [d+e for e in path_string.split(d) if e]
#     print('lin point_list: ')
#     [print(segment) for segment in point_list]

#     # paths.add(dwg.path(d=path_string,stroke=next(trace_colors)))
#     # for point in response:
#     #     draw_point(*log_scale(*point))


# paths.add(dwg.path(d="M 212.852669 395.714286 C 229.336193,396.602517 253.006439,288.809348 260.480665,224.285714",
    # stroke="green"))


#
#
# M 50.000000 50.000000 C 61.182443,49.896373 80.106218,62.472243 80.000000,70.000000

# Take Y values and plug into equation:
# B(t)_y = ((1-t)^3)*P0_y + 3((1-t)^2)*t*P1_y + 3(1-t)(t^2)P2_y + (t^3)*P3_y
# B(t)_y = ((1-t)^3)*50 + 3((1-t)^2)*t*49.896373 + 3(1-t)(t^2)*62.472243 + (t^3)*70
# Used wolframalpha.com to solve for t... t = 0.612255

# Plug t into x side of cubic bezier function to find B(t)_x
# B(t)_x = ((1-t)^3)*P0_x + 3((1-t)^2)*t*P1_x + 3(1-t)(t^2)P2_x + (t^3)*P3_x
# B(t)_x = ((1-t)^3)*50 + 3((1-t)^2)*t*61.182443 + 3(1-t)(t^2)*80.106218 + (t^3)*80  where t = .612255
# Used wolframalpha.com to solve for B(0.612255)_x = 73.101


##################################
#
#   Keeping B Splines In Bounds
#
##################################

'''
Depending on the range of the plot, parts of the plotted bezier curve may be outside
the graph perimeter. We need to figure out where the plotted curve intersects with the
perimter and slice the curve at those points.

'''

test_curve = [[50.000000, 50.000000], [61.182443, 49.896373],
              [80.106218, 62.472243], [80.000000, 70.000000]]

# Take Y values and plug into equation:
# B(t)_y = ((1-t)^3)*P0_y + 3((1-t)^2)*t*P1_y + 3(1-t)(t^2)P2_y + (t^3)*P3_y
# B(t)_y = ((1-t)^3)*50 + 3((1-t)^2)*t*49.896373 + 3(1-t)(t^2)*62.472243 + (t^3)*70
# Used wolframalpha.com to solve for t... t = 0.612255

# Plug t into x side of cubic bezier function to find B(t)_x
# B(t)_x = ((1-t)^3)*P0_x + 3((1-t)^2)*t*P1_x + 3(1-t)(t^2)P2_x + (t^3)*P3_x
# B(t)_x = ((1-t)^3)*50 + 3((1-t)^2)*t*61.182443 + 3(1-t)(t^2)*80.106218 + (t^3)*80  where t = .612255
# Used wolframalpha.com to solve for B(0.612255)_x = 73.101


def find_intersect(y, bez):
    '''
    This function finds the intersection point between a horizontal line and a bezier curve.

    Args:
        y (float) -> the y interesction of the horizontal line
        bez (list) -> a list of lists containing 4 control
            points for a cubic bezier curve using the format:
            [[P0x1 - 2 t + t^2, P0y], [P1x, P1y], [P2x, P2y], [P3x, P3y]]

    Returns:
        intersect (list) -> the point of intersection: [x, y]
    --------------------------------------------------------------------
    '''

    '''
    The general equation for a bezier curve is:
    B(t) = ((1-t)^3)*P0 + 3((1-t)^2)*t*P1 + 3(1-t)(t^2)P2 + (t^3)*P3

    When expanded that can be written as:
    B(t) =
    P0( -t^3 + 3t^2 - 3t + 1 ) +
    P1( 3t^3 - 6t^2 + 3t + 0 ) +
    P2(-3t^3 + 3t^2 -  0 + 0 ) +
    P3(  t^3 +    0 -  0 + 0 )

    To find the intersection point, we first need to solve to find the value of t
    where B(t)_y is equal to the y intercept.

    Numpy's roots function can be used to solve to find the value of t. It takes a
    list cooeficients A,B,C,D as its parameter. To find these we can multiply the
    y value of each bezier control point through each expanded polynomial and sum
    the coefficient preceding each element to find A,B,C,D.
    '''
    A = -1*bez[0][1] + 3*bez[1][1] + -3*bez[2][1] + 1*bez[3][1]
    B = 3*bez[0][1] + -6*bez[1][1] + 3*bez[2][1] + 0*bez[3][1]
    C = -3*bez[0][1] + 3*bez[1][1] + 0*bez[2][1] + 0*bez[3][1]
    D = 1*bez[0][1] + 0*bez[1][1] + 0*bez[2][1] + 0*bez[3][1]

    '''
    The fourth element is D-y because we need to find where the roots are zero.
    This is the quivalent of subtracting the Y offset from both sides:
    y = ((1-t)^3)*P0 + 3((1-t)^2)*t*P1 + 3(1-t)(t^2)P2 + (t^3)*P3
    0 = ((1-t)^3)*P0 + 3((1-t)^2)*t*P1 + 3(1-t)(t^2)P2 + (t^3)*P3 - y

    '''
    print('A,B,C,D:', A, ',', B, ',', C, ',', D)

    coeff = [A, B, C, D-y]

    t_params = np.roots(coeff)

    for t in t_params:
        if t > 0 and t < 1:
            print('t :', t)
    # Plug t into x side of cubic bezier function to find B(t)_x
            x = (((1-t)**3)*bez[0][0]) + (bez[1][0]*(3*t - 6*t**2 + 3*t**3)
                                          ) + ((3*t**2 - 3*t**3)*bez[2][0]) + ((t**3)*bez[3][0])

            return (x, y)


# print(find_intersect(60,test_curve))


def interpolate_points(total_points, bez=test_curve):
    '''
    This function plots a number of points along a bezier curve.

    Args:
        bez (list) -> a list of lists containing 4 control
            points for a cubic bezier curve using the format:
            [[P0x1 - 2 t + t^2, P0y], [P1x, P1y], [P2x, P2y], [P3x, P3y]]
        total_points (int) -> how many points to return

    Returns:
        b_points (list of lists) -> the point of intersection: [x, y]
    '''

    # Create a list of points T between 0 and 1 based on the number of total_points
    t_points = []

    t_step = 1/total_points
    t_count = 0

    while t_count <= 1:
        t_points.append(t_count)
        t_count += t_step

    b_points = []

    # Plug t values into expanded form of bezier curve function.
    for t in t_points:
        x = (((1-t)**3)*bez[0][0]) + (bez[1][0]*(3*t - 6*t**2 + 3*t**3)
                                      ) + ((3*t**2 - 3*t**3)*bez[2][0]) + ((t**3)*bez[3][0])
        y = (((1-t)**3)*bez[0][1]) + (bez[1][1]*(3*t - 6*t**2 + 3*t**3)
                                      ) + ((3*t**2 - 3*t**3)*bez[2][1]) + ((t**3)*bez[3][1])
        b_points.append([x, y])

    return b_points


# draw_point(*log_scale(73.101,60.00001))
dwg.save()
