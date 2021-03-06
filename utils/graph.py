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

# total size of the generated svg including space for a legend: (x, y) pair
total_size = (1000, 600)

# size of graph: (x, y) pair
graph_size = (700, 300)

# offset from left side and top of image: (x, y) pair
graph_offset = (120, 10)

# the frequency range of the graph in Hz: (a, b) range
freq_range = (20, 20000)

# amplitude range of the graph in dB: (a, b) range
amp_range = (60, 95)

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
            debug=False
        )

        # Create svg drawing groups
        self.background = self.dwg.add(self.dwg.g(id='background'))
        self.scale_lines = self.dwg.add(self.dwg.g(
            id='scale_lines', fill='grey', stroke='grey'))
        self.line_labels = self.dwg.add(
            self.dwg.g(id='line_labels', fill='black'))
        self.trace_labels = self.dwg.add(
            self.dwg.g(id='trace_labels', fill='black'))
        self.clipping_mask = self.dwg.add(self.dwg.mask(id='clipping_mask'))

    def render(self):
        '''
        Create output drawing. Note that the order drawing methods are called in
        represents the order in which they appear.
        '''
        self.draw_background()
        hline_list = self.draw_h_lines()
        vline_list = self.draw_v_lines()

        # Axes and labels
        self.draw_v_labels(vline_list, graph_label_font)

        self.draw_axis_lable('Frequency in Hz',
                             self.graph_size[0] + self.graph_offset[0] + 5,
                             self.graph_size[1] + self.graph_offset[1] + 10,
                             45,
                             **graph_label_font)

        self.draw_h_labels(hline_list, graph_label_font)

        self.draw_axis_lable('Amplitude in dB',
                             self.graph_offset[0] - 90,
                             self.graph_offset[1] + 5,
                             0,
                             **graph_label_font)

        # Create Clipping mask
        self.clipping_mask.add(self.dwg.rect(
            insert=(self.graph_offset[0], self.graph_offset[1]),
            size=(self.graph_size[0], self.graph_size[1]),
            fill="white")
        )

        # Add trace_paths to clipping mask
        self.trace_paths = self.dwg.add(self.dwg.g(id='path', stroke_width=2,
                                                   fill='white', fill_opacity="0", mask="url(#clipping_mask)"))

        self.draw_traces()

    def save(self):
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

    def draw_point(self, x, y, color=''):
        '''
        This function draws a point on the graph. The inputs are in x and y, to plot a
        point based on frequency and amplitude, use the log_scale method to convert it.
        '''

        # Skip points that are out of range
        if (x <= self.graph_offset[0]
            or x >= self.graph_offset[0] + self.graph_size[0]
            or y <= self.graph_offset[1]
                or y >= self.graph_offset[1] + self.graph_size[1]):
            return

        point = self.dwg.circle(center=(x*px, y*px), r='2px',
                                fill=color, stroke=color, stroke_width=2)
        self.background.add(point)

    def draw_h_lines(self):
        '''
        This function draws horizontal markers on the graph based on the range of amplitudes
        plotted. Stroke thickness depends on multiples of 10, 5 and 1. The function returns
        a list of horizontal lines plotted to help figure out where to put a label.
        '''

        line_coords = []
        for a in range(self.amp_range[0], self.amp_range[1]):
            line_start = self.log_scale(self.freq_range[0], a)
            line_end = self.log_scale(self.freq_range[1], a)

            # Add to the list of lines
            line_coords.append([a, (line_start, line_end)])

            # Change the stroke width depending if it's a multiple of 10, 5 or 1
            if a % 10 == 0:
                line = self.dwg.line(
                    start=line_start, end=line_end, stroke_width=1)
            elif a % 5 == 0:
                line = self.dwg.line(
                    start=line_start, end=line_end, stroke_width=.5)
            else:
                line = self.dwg.line(
                    start=line_start, end=line_end, stroke_width=.25)

            # Draw the line
            self.scale_lines.add(line)

        return line_coords

    def draw_v_lines(self):
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
        f = self.freq_range[0]
        while(f <= self.freq_range[1]):
            # figure out which order of magnitude f is in
            power = log10(f)
            power = floor(power)
            # step is used to increment f
            step = pow(10, power)
            freq = ceil(f/step) * step
            if freq < self.freq_range[1]:
                line_coords.append([freq, ])
                vlines.append(freq)
            # increment f to the next frequency of interest
            f = f + step

        for i in range(len(vlines)):
            line_start = self.log_scale(vlines[i], self.amp_range[1])
            line_end = self.log_scale(vlines[i], self.amp_range[0])

            line_coords[i].append((line_start, line_end))

            # use a thicker stroke for powers of 10
            if str(vlines[i]).startswith('10'):
                line = self.dwg.line(
                    start=line_start, end=line_end, stroke_width=1)
            else:
                line = self.dwg.line(
                    start=line_start, end=line_end, stroke_width=.25)
            # draw the line
            self.scale_lines.add(line)

        return line_coords

    def draw_lable(
            self,
            text,
            x,
            y,
            rotate,
            font_family='',
            font_size='',
            font_color=''):

        msg = self.dwg.text(
            text,
            insert=(x, y),
            font_family=font_family,
            font_size=font_size,
            fill=font_color)

        msg.rotate(rotate, (x, y))

        self.line_labels.add(msg)

    def draw_v_labels(self, line_list, label_font):
        '''
        Draw labels for vertical markers
        '''
        for item in line_list:
            text = int(item[0])
            end_point = item[1][1]
            y_offset = 10
            rotation = 45
            if str(text).startswith('1') or str(text).startswith('5'):
                self.draw_lable(
                    text,
                    end_point[0],
                    end_point[1] + y_offset,
                    rotation,
                    **label_font)

    def draw_h_labels(self, line_list, label_font):
        '''
        Draw labels for horizontal markers
        '''
        for item in line_list:
            text = int(item[0])
            start_point = item[1][0]
            x_offset = -24
            y_offset = 4
            rotation = 0
            if text % 5 == 0:
                self.draw_lable(
                    text,
                    start_point[0] + x_offset,
                    start_point[1] + y_offset,
                    rotation,
                    **label_font)

    def draw_axis_lable(
            self,
            text,
            x,
            y,
            rotate,
            font_family='',
            font_size='',
            font_color=''):

        msg = self.dwg.text(
            text,
            insert=(x, y),
            font_family=font_family,
            font_size=font_size,
            fill=font_color)

        msg.rotate(rotate, (x, y))

        self.line_labels.add(msg)

    def draw_traces(self):
        color_generator = get_trace_color(len(self.traces))
        label_start_x = graph_offset[0]
        label_start_y = graph_offset[1] + graph_size[1] + 60

        for trace in self.traces:
            color = next(color_generator)
            log_points = [list(self.log_scale(*pair))
                          for pair in trace["points"]]
            path_string = bspline.make_curve(log_points)
            self.trace_paths.add(self.dwg.path(d=path_string, stroke=color))
            self.draw_trace_label(
                trace['name'], color, label_start_x, label_start_y, 0, **graph_label_font)
            label_start_y += 20

    def draw_trace_label(
            self,
            text,
            trace_color,
            x,
            y,
            rotate,
            font_family='',
            font_size='',
            font_color=''):

        msg = self.dwg.text(
            text,
            insert=(x + 20, y),
            font_family=font_family,
            font_size=font_size,
            fill=font_color)

        self.trace_labels.add(self.dwg.path(
            d=f'M {x} {y - 4.5} L {x + 16} {y - 4.5} z', stroke_width=3, stroke=trace_color))

        msg.rotate(rotate, (x, y))

        self.trace_labels.add(msg)
