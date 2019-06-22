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

from utils.graph import Graph

# project specific modules
import datasets

# output file name
filename = 'svg_output/output_plot.svg'

# list of colors to be applied to traces
color_list = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']

############################################################
#
#    Main

if __name__ == "__main__":
    ####################
    #  Initialize graph

    # Create a dwg object
    dwg = svgwrite.Drawing(filename=filename, size=(
        tot_size_x*px, tot_size_y*px), debug=True)

    # Add groups to the dwg object
    shapes = dwg.add(dwg.g(id='shapes'))

    trace = dwg.add(dwg.g(id='trace'))

    scale_lines = dwg.add(dwg.g(id='scale_lines', fill='grey', stroke='grey'))

    line_labels = dwg.add(dwg.g(id='labels', fill='black'))

    # Add clip mask to bound traces
    mask = dwg.mask(id='curveMask')

    mask.add(dwg.rect(
        insert=(g_offset_x, g_offset_y),
        size=(g_size_x, g_size_y),
        fill="white"))

    dwg.add(mask)

    # Establish trace colors
    trace_colors = get_trace_color(len(datasets.responses))

    ####################
    #  Render graph

    # Background
    draw_background()

    hline_list = draw_h_lines()
    vline_list = draw_v_lines()

    # Axes and labels
    add_v_labels(vline_list, graph_label_font)

    draw_axis_lable('Frequency in Hz', g_size_x + g_offset_x + 30,
                    g_size_y + g_offset_y + 10, 0, **graph_label_font)

    add_h_labels(hline_list, graph_label_font)

    draw_axis_lable('Amplitude in dB', g_offset_x - 90,
                    g_offset_y + 5, 0, **graph_label_font)

    # Clipping mask
    paths = dwg.add(dwg.g(id='path', stroke_width=2,
                        fill='white', fill_opacity="0", mask="url(#curveMask)"))

    # Traces mask
    def plot_path(dataset):
        log_points = []
        for pair in dataset:
            entry = list(log_scale(*pair))
            log_points.append(entry)

        return bspline.make_curve(log_points)

    for response in datasets.responses:
        path_string = plot_path(response)
        d = "M"
        point_list = [d+e for e in path_string.split(d) if e]

        paths.add(dwg.path(d=path_string, stroke=next(trace_colors)))

    dwg.save()
