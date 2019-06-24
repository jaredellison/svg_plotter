# svg_plotter

> Drawing frequency response bode plots from Room EQ Wizard data in SVG with Python.

![example-illustration](documentation/example-illustration.png)

This script takes information exported from Room EQ Wizard measurements and draws a graph in an SVG file with a smooth curve for each data set and labels for the frequency and amplitude axes.

## Inspiration

I love making and recording music. One question that comes up often in the recording studio is: which microphone should I use? There are a number of characteristics that differentiate microphones (polar response, sensitivity, transducer hysteresis, etc) but frequency response is among the most useful when choosing one microphone over another: it tells you whether a microphone sounds more bassy or bright.

Manufacturers supply frequency response plots the datasheets that come with new microphones but it isn't so easy to compare the frequency response of different microphones from different manufacturers. The scale of these plots is often different and can be skewed to make a microphone appear to have a flatter response. When comparing many microphones it would be helpful to view the frequency response of each mic all in the same graph with the same scale.

The free audio test software Room EQ Wizard makes it easier than ever to make frequency response measurements and compare measurements but the only option for sharing these measurements is to export a raster image of the plot.

Room EQ Wizard does allow exporting a list of data points and this list can be used to create an SVG file that can be embedded on the web and styled with CSS.

## Better plotting methods?

I began this project as a way to learn some new tools but if you're looking for a nice way to plot some data, there are probably some easier more flexible ways. If you're set on using Python check out: [Matplotlib](https://matplotlib.org/), [Seaborn](https://seaborn.pydata.org/) and [Bokeh](https://bokeh.pydata.org/). If your project is all about the web, it might make sense to do everything in javascript with: [D3.js](https://d3js.org/).

## Work In Progress!

This project is very much a work in progress. Work to do includes finding a way to keep graph traces in bounds of the plotting area, exporting SVG plots with appropriate SVG classes and ids for stlying with css and more.

## Tools Used

* [Room EQ Wizard](https://www.roomeqwizard.com) - Free Audio Test software to make measurements and export data to plot
* [svgwrite](https://pypi.org/project/svgwrite/) - SVG Module for Python
* [numpy](http://www.numpy.org/) - For matrix objects for making smooth spline curves

## Authors

* **Jared Ellison** - [jaredellison.net](http://jaredellison.net)

## Acknowledgments

* **John Mulcahy** - *Excellent free audio test suite* - [Room EQ Wizard](https://www.roomeqwizard.com)
* **Nash Vail** - *Clear explanation of cubic bezier curves* - [Nerding Out with Bezier Curves](https://medium.freecodecamp.org/nerding-out-with-bezier-curves-6e3c0bc48e2f)
* **Kirby A. Baker** - *UCLA Math Dept.* - [Awesome handout on Bsplines](http://www.math.ucla.edu/~baker/149.1.02w/handouts/dd_splines.pdf)
* **David Morrin** - *SVG Drawing Inspiration* - [davidmorrin.com](https://www.davidmorrin.com/)
* **Billie Thompson** - *Github Readme Template* - [PurpleBooth](https://github.com/PurpleBooth)
* **Hendrick Wade Bode** - *Eponymous Plotting Style* - [Hendrick Wade Bode](https://en.wikipedia.org/wiki/Hendrik_Wade_Bode)
