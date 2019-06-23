#!/usr/bin/python3
# coding=utf-8
#
# Author:  Jared Ellison
# Site:  jaredellison.net
# Purpose: Graph module to render Bode plots into SVG
# Created: 06.22.2019

########################################
#  Dependencies

# external modules
import utils.bspline as bspline
from utils.color import get_trace_color
import svgwrite
from svgwrite import px

# standard library modules
from math import log10, floor, pow, ceil


########################################
#  Default Parameters

# total size of the generated svg including space for a legend (x, y) pair
total_size = (1000, 600)
# tot_size_x = 1000
# tot_size_y = 600

# size of graph (x, y) pair
graph_size = (700, 300)
# g_size_x = 700
# g_size_y = 300

# offset from left side and top of image (x, y) pair
graph_offset = (120, 10)
# g_offset_x = 120
# g_offset_y = 10

# the frequency range of the graph in Hz (x, y) pair
freq_range = (20, 20000)
# freq_min = 20
# freq_max = 20000

# amplitude range of the graph in dB (x, y) pair
amp_range = (60, 95)
# amp_min = 60
# amp_max = 95

# graph label font
graph_label_font = {
    'font_family': 'sans-serif',
    'font_size': '12',
    'font_color': 'black'
}

############################################################
#
#    Graph Class


class Graph:
    def __init__(
        self,
        total_size=total_size,
        graph_size=graph_size,
        graph_offset=graph_offset,
        freq_range=freq_range,
        amp_range=amp_range,
        file_name="./default_output.svg"
    ):
        ####################
        #  Graph attributes

        self.total_size = total_size
        self.graph_size = graph_size
        self.graph_offset = graph_offset
        self.freq_range = freq_range
        self.amp_range = amp_range
        self.traces = []

        ####################
        #  SVG Attributes

        self.file_name = file_name
        # Create drawing object to render to
        self.dwg = svgwrite.Drawing(
            filename=self.file_name,
            size=(self.total_size[0] * px, self.total_size[1] * px),
            # Set debug false for production!
            debug=True
        )
        # Create svg drawing groups
        self.background = self.dwg.add(self.dwg.g(id='background'))
        self.trace_paths = self.dwg.add(self.dwg.g(id='trace_paths'))
        self.scale_lines = self.dwg.add(self.dwg.g(id='scale_lines', fill='grey', stroke='grey'))
        self.line_labels = self.dwg.add(self.dwg.g(id='labels', fill='black'))
        self.clipping_mask = self.dwg.add(self.dwg.mask(id='clipping_mask'))

    def render(self):
        '''
        Create output drawing. Note that the order drawing methods are called in
        represents the order in which they appear.
        '''
        #
        self.draw_background()

        # Create Clipping mask
        self.clipping_mask.add(self.dwg.rect(
            insert=(self.graph_offset[0], self.graph_offset[1]),
            size=(self.graph_size[0], self.graph_size[1]),
            fill="white")
        )

        # Add trace_paths to clipping mask
        # self.trace_paths = self.dwg.add(self.dwg.g(id='path', stroke_width=2,
        #                     fill='white', fill_opacity="0", mask="url(#curveMask)"))

        self.dwg.save()


    ########################################
    #  Data Oriented Methods

    def add_trace(self, trace):
        self.traces.append(trace)

    def log_scale(self, f, a):
        '''
        This function takes a frequency (Hz) and amplitude (dB) and outputs an
         x,y coordinate pair as a tuple.
        '''

        # Scale frequency input to a fraction of the specified spectrum
        x = ((log10(f)-log10(self.freq_range[0])) /
             (log10(self.freq_range[1]) - log10(self.freq_range[0])))

        # Apply that fraction to the width of the graph
        x_end = self.graph_offset[0] + self.graph_size[0]
        x_start = self.graph_offset[0]
        x = (x * (x_end - x_start)) + x_start

        # Scale amplitude input
        y = (a - self.amp_range[0])/(self.amp_range[1] - self.amp_range[0])

        y_end = self.graph_offset[1] + self.graph_size[1]
        y_start = self.graph_offset[1]
        y = y * (y_end - y_start)
        y = ((y_end - y_start) - y) + y_start
        return (x, y)

    ########################################
    #  Render Methods

    def draw_background(self):
        '''
        This function draws a rectangle behind the plotting area.
        Call this function first so it's in the back.
        '''

        background_fill = '#fcfcfc'
        background_stroke = '#000000'
        background_stroke_width = 1

        self.background.add(
            self.dwg.rect(
                insert=(self.graph_offset[0] * px, self.graph_offset[1] * px),
                size=(self.graph_size[0] * px, self.graph_size[1] * px),
                fill=background_fill,
                stroke=background_stroke,
                stroke_width=background_stroke_width
                )
        )

    # def draw_point(
    #         x,
    #         y,
    #         svg_group=trace,
    #         x_start=g_offset_x,
    #         x_end=(g_offset_x+g_size_x),
    #         y_start=g_offset_y,
    #         y_end=(g_offset_y+g_size_y),
    #         color=''):
    #     '''
    #     This function draws a point on the graph. The inputs are in x and y, to plot a
    #     point based on frequency and amplitude, use the log scale function to convert it.
    #     '''

    #     # Skip points that are out of range
    #     if x <= x_start or x >= x_end or y <= y_start or y >= y_end:
    #         return

    #     dot = dwg.circle(center=(x*px, y*px), r='2px',
    #                     fill=color, stroke=color, stroke_width=2)
    #     svg_group.add(dot)

    # def draw_h_lines(
    #         amp_min=amp_min,
    #         amp_max=amp_max,
    #         svg_group=scale_lines,
    #         g_offset_x=g_offset_x,
    #         g_offset_y=g_offset_y):
    #     '''
    #     This function draws horizontal markers on the graph based on the range of amplitudes
    #     plotted. Stroke thickness depends on multiples of 10, 5 and 1. The function returns
    #     a list of horizontal lines plotted to help figure out where to put a label.
    #     '''

    #     line_coords = []
    #     for a in range(amp_min, amp_max):
    #         line_start = log_scale(freq_min, a)
    #         line_end = log_scale(freq_max, a)

    #         # Add to the list of lines
    #         line_coords.append([a, (line_start, line_end)])

    #         # Change the stroke width depending if it's a multiple of 10, 5 or 1
    #         if a % 10 == 0:
    #             line = dwg.line(start=line_start, end=line_end, stroke_width=1)
    #         elif a % 5 == 0:
    #             line = dwg.line(start=line_start, end=line_end, stroke_width=.5)
    #         else:
    #             line = dwg.line(start=line_start, end=line_end, stroke_width=.25)

    #         # Draw the line
    #         svg_group.add(line)

    #     return line_coords

    # def draw_v_lines(
    #         freq_min=freq_min,
    #         freq_max=freq_max,
    #         svg_group=scale_lines,
    #         g_offset_x=g_offset_x,
    #         g_offset_y=g_offset_y):
    #     '''
    #     This function draws vertical markers on the graph based on the range of frequencies
    #     plotted. For a bode plot with a logarithmic scale, we're interested in major markers at
    #     powers of 10 and minor markers at integer multiples of that power of 10 leading up
    #     to the next marker:
    #     10^n * 1, 10^n * 2, 10^n * 3 ... 10^n+1 * 1
    #     Strokes are thicker at powers of 10. The function returns a list of vertical lines
    #     plotted to help figure out where to put a label.
    #     '''

    #     # list of frequencies to mark with vertical lines
    #     vlines = []

    #     # a list to track the frequencies plotted and the start and end points of the line
    #     # this is for figuring out where to draw a label
    #     line_coords = []

    #     # Start with the minimum frequency
    #     f = freq_min
    #     while(f <= freq_max):
    #         # figure out which order of magnitude f is in
    #         power = log10(f)
    #         power = floor(power)
    #         # step is used to increment f
    #         step = pow(10, power)
    #         freq = ceil(f/step) * step
    #         if freq < freq_max:
    #             line_coords.append([freq, ])
    #             vlines.append(freq)
    #         # increment f to the next frequency of interest
    #         f = f + step

    #     for i in range(len(vlines)):
    #         line_start = log_scale(vlines[i], amp_max)
    #         line_end = log_scale(vlines[i], amp_min)

    #         line_coords[i].append((line_start, line_end))

    #         # use a thicker stroke for powers of 10
    #         if str(vlines[i]).startswith('10'):
    #             line = dwg.line(start=line_start, end=line_end, stroke_width=1)
    #         else:
    #             line = dwg.line(start=line_start, end=line_end, stroke_width=.25)
    #         # draw the line
    #         svg_group.add(line)

    #     return line_coords

    # def draw_lable(
    #         text,
    #         x,
    #         y,
    #         rotate,
    #         svg_group=line_labels,
    #         font_family='',
    #         font_size='',
    #         font_color=''):

    #     msg = dwg.text(
    #         text,
    #         insert=(x, y),
    #         font_family=font_family,
    #         font_size=font_size,
    #         fill=font_color)

    #     msg.rotate(rotate, (x, y))

    #     svg_group.add(msg)

    # def add_v_labels(line_list, label_font):
    #     '''
    #     This function draws labels for vertical markers.
    #     '''
    #     for item in line_list:
    #         text = int(item[0])
    #         end_point = item[1][1]
    #         y_offset = 10
    #         rotation = 45
    #         if str(text).startswith('1') or str(text).startswith('5'):
    #             draw_lable(text, end_point[0], end_point[1] +
    #                     y_offset, rotation, **label_font)

    # def add_h_labels(line_list, label_font):
    #     '''
    #     This function draws labels for horizontal markers.
    #     '''
    #     for item in line_list:
    #         text = int(item[0])
    #         start_point = item[1][0]
    #         x_offset = -20
    #         y_offset = 4
    #         rotation = 0
    #         if text % 5 == 0:
    #             draw_lable(
    #                 text, start_point[0]+x_offset, start_point[1]+y_offset, rotation, **label_font)

    # def draw_axis_lable(
    #         text,
    #         x,
    #         y,
    #         rotate,
    #         svg_group=line_labels,
    #         font_family='',
    #         font_size='',
    #         font_color=''):

    #     msg = dwg.text(
    #         text,
    #         insert=(x, y),
    #         font_family=font_family,
    #         font_size=font_size,
    #         fill=font_color)

    #     msg.rotate(rotate, (x, y))

    #     svg_group.add(msg)
