#!/usr/bin/python3
# coding=utf-8
#
# Author:  Jared Ellison
# Site:  jaredellison.net
# Purpose: Generate an evenly distributed collection of colors
# Created: 06.23.2019

########################################
#  Color Utilities
from colorsys import hls_to_rgb


def angle_to_hex_triplet(rotation, saturation=.5, luminance=.6):
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
