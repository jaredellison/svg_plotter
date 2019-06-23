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

# list of colors to be applied to traces
color_list = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']

############################################################
#
#    Main

if __name__ == "__main__":
    #  Initialize graph
    g = Graph(file_name='svg_output/output_plot.svg')

    g.add_trace({"points": datasets.responses[0], "name": "test"})

    g.render()
    g.save()
