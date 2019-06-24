#!/usr/bin/python3
# coding=utf-8
#
# Author:  Jared Ellison
# Site:  jaredellison.net
# Purpose: Transform a 2D list of points into a SVG format bezier curve moving
#          through each point on the curve.
# Created: 06.23.2019

'''
######################
# Overview
######################

This script uses a procedure outlined in the following paper for fitting
a cubic spline to a list of coordinates:

http://www.math.ucla.edu/~baker/149.1.02w/handouts/dd_splines.pdf

Roughly, the prodecure is to work with 5 points at a time and produce
segments of curves that can be glued together at the end points. If the
second derivative at the end point of two curves is equal, they can be
glued together seamlessly.

This script works with relaxed uniform cubic B-spline curves. Each curve
is determined by a series of points that are on the curve (S), a series
of control points off the curve (B) and a series of division points.
The script uses the second derivative of the B-spline curves to find the
B control points and then uses geometry to find the division points (D) that
are 1/3 and 2/3 of the way between consecutive B points.

######################
# Finding the B and D Points
######################
The first and last B points are the same as the first and last
S points but the middle B points are found based on this equation.
(subscript is denoted by an underscore and curly bracket):
B_{i-1} + 4*B_{i} + B_{i+1} = 6*S_{i}

The "1 4 1" and "6" cooeficents from this equation are used to create an
algebraic equation using matrices.

  [ 4 , 1 , 0 ]   [B_{1}]   [( 6*S_{1} - S_{0} )]
  [ 1 , 4 , 1 ] * [B_{2}] = [(      6*S_{2}    )]
  [ 0 , 1 , 4 ]   [B_{3}]   [( 6*S_{3} - S_{4} )]

The inverse of the "1 4 1" matrix [m] can then be multiplied by the S point
matrix [S] to solve for the B middle points [B].

[m]^-1 * [S] = [B]

With a full list of 5 B points, 8 division points can be found. This is
done by finding the points 1/3 and 2/3 of the way between B points.
D_{0} = B_{1} - B_{0} * 1/3 + B_{0}
D_{1} = B_{1} - B_{0} * 2/3 + B_{0}
D_{2} = B_{2} - B_{1} * 1/3 + B_{1}

######################
# Plotting with SVG
######################

To plot the curve, a list of points can be constructed to generate an
svg path. In an SVG file the starting point of path is specified by
"moving" to a specific point M and then begining a cubic bezier curve
with a starting point is specified after the letter "M". The letter "C"
specifies a cubic bezier curve and is followed by two division points
which control the curve and an ending point. Given our points S, and D
from above, this takes the form of a string:

M S_{0 X} S_{0 Y} C D_{0 X},D_{0 Y} D_{1 X},D_{1 Y} S_{0 X},S_{0 Y}

The type of bezier curve we have generated has relaxed endpoints,
meaning the second derivative of the curve is 0 at the end points.
The full sequence of points we've generated is:
S_{0}, D_{0}, D_{1}, S_{1}, D_{2}, D_{3},
S_{2}, D_{4}, D_{5}, S_{3}, D_{6}, D_{7}, S_{4}

To generate a smoother curve for along sequence of S points, we will
stitch together the mid section of this curve between S_{1} and S_{3}.
For the begining of the curve we will use relaxed start point with the
sequence:
S_{0}, D_{0}, D_{1}, S_{1}, D_{2}, D_{3}, S_{2}, D_{4}, D_{5}, S_{3}

For the middle parts of the curve we will stich together segements with
the following points:
S_{1}, D_{2}, D_{3}, S_{2}, D_{4}, D_{5}, S_{3}

And at the end we will also use the relaxed end point:
S_{1}, D_{2}, D_{3}, S_{2}, D_{4}, D_{5}, S_{3}, D_{6}, D_{7}, S_{4}

'''


import numpy as np
from numpy.linalg import inv


def mul_pair(pair, x):
    ''' This function multiplies a pair of coordinates by x'''
    pair = pair[:]
    result = []
    for i in pair:
        result.append(i*x)
    return result


def sub_pair(pair_a, pair_b):
    ''' This function subtracts pair of coordinates b from pair a'''
    pair_a = pair_a[:]
    pair_b = pair_b[:]
    result = []
    i = 0
    while i < len(pair_a):
        result.append(pair_a[i]-pair_b[i])
        i += 1
    return result


def dist_pair(pair_a, pair_b, percent, debug=False):
    ''' This function returns a point that is a percentage of the distance from a to b'''
    pair_a = pair_a[:]
    pair_b = pair_b[:]
    result = []
    i = 0
    if debug:
        print('pair_a, pair_b, percent: ', pair_a, pair_b, percent)
    while i < len(pair_a):
        computation = ((pair_b[i]-pair_a[i])*percent)+pair_a[i]
        if debug:
            print('computation', computation)
        result.append(computation)
        i += 1
    return result


def rotate_list(list_in):
    list_out = list_in[:]
    list_out = [list_out[-1]]+list_out[:-1]
    return list_out


def make_curve(point_list):
    # list of 5 s_points that will be on the curve
    s_points = point_list[:]

    ################################
    # Creating matrix m
    #   [ 4 , 1 , 0 ]
    #   [ 1 , 4 , 1 ]
    #   [ 0 , 1 , 4 ]
    #################################

    # Size of matrix
    m_rows = len(s_points) - 2

    m_components = [1, 4, 1]

    # The matrix m consists of rows that include
    # numbers 1 4 1 and 0s. The extended row includes
    # one more column than the matrix has.
    ext_m_row = []

    # Add the matrix compents to the list.
    for item in m_components:
        ext_m_row.append(item)

    # Fill in zeros depending on the size of the matrix
    while len(ext_m_row) < m_rows + 1:
        ext_m_row.append(0)

    m_list = []

    # Create the matrix m.
    for i in range(m_rows):
        m_list.append(ext_m_row[1:])
        ext_m_row = rotate_list(ext_m_row)

    # Convert 2D list into numpy matrix
    m = np.array(m_list)

    # print('m matrix: \n', m)

    # Finding the inverse of the matrix m with inv from the numpy linalg module
    m_inv = inv(m)

    ################################
    # Creating the s_matrix:
    # [( 6*S_{1} - S_{0}   )]
    # [(      6*S_{...}    )]
    # [( 6*S_{n-1} - S_{n} )]
    ################################

    s_list = []

    i = 0
    while i < len(s_points):
        # First set of coordinates
        if i == 0:
            s_list.append(sub_pair(mul_pair(s_points[i+1], 6), s_points[i]))
            i += 2
        # Next to last set of coordinates
        elif i == len(s_points)-2:
            s_list.append(sub_pair(mul_pair(s_points[i], 6), s_points[i+1]))
            break
        # Coordinates in the middle
        else:
            s_list.append(mul_pair(s_points[i], 6))
            i += 1

    # Convert to a numpy matrix
    s_matrix = np.matrix(s_list)

    # print('s matrix: \n', s_matrix)
    ################################
    #
    #    Solving to find b points
    #
    ################################

    # Multiplying the inverse of matrix m by the s_matrix to find the middle b points
    b_matrix = np.matmul(m_inv, s_matrix)
    # print('b matrix:')
    # print(b_matrix)

    # Creating a list of b points. The first and last points are the same as the first
    # and last of the s_points. The middle points are stored in the b_matrix
    b_points = []
    b_points.append(s_points[0])
    for b in b_matrix:
        b_points = b_points + b.tolist()
    b_points.append(s_points[-1])

    # Creating a list of division points:

    # print('b_points')
    # for point in b_points:
    #     print(point)

    d_points = []

    i = 0
    while i < len(b_points) - 1:
        d_points.append(dist_pair(b_points[i], b_points[i+1], (1/3)))
        d_points.append(dist_pair(b_points[i], b_points[i+1], (2/3)))
        i += 1

    # print('s_points')
    # for point in s_points:
    #     print(point)

    # print('d_points')
    # for point in d_points:
    #     print(point)

    # print('d_points[0][0]')
    # print(d_points[0][0])

    # Create a string in svg format to describe the path.
    path_string = ''
    s_count = 0
    d_count = 0
    while s_count < len(s_points)-1:
        path_list = [
            s_points[s_count][0],
            s_points[s_count][1],
            d_points[d_count][0],
            d_points[d_count][1],
            d_points[d_count+1][0],
            d_points[d_count+1][1],
            s_points[s_count+1][0],
            s_points[s_count+1][1]
        ]
        # print('path_list: ')
        # for item in path_list:
        #     print(item)
        path_string += 'M %f %f C %f,%f %f,%f %f,%f ' % tuple(path_list)
        s_count += 1
        d_count += 2

    return path_string
