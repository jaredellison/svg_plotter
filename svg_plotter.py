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
from utils.extract import get_data
import os

############################################################
#
#    Main

if __name__ == "__main__":
    #  Initialize graph
    g = Graph(amp_range=(75,105),file_name='svg_output/data_plot.svg')

    source_dir = './data'

    for path in os.listdir(source_dir):
        # Igore hidden files
        if (path.startswith('.')):
            continue
        # Extract
        data = get_data(os.path.join(source_dir, path))
        g.add_trace(data)

    g.render()
    g.save()
