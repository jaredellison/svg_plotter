#!/usr/bin/python3
# coding=utf-8
#
# Author:  Jared Ellison
# Site:  jaredellison.net
# Purpose: Extract module to retrieve the data points a measurment name from a
#          text file exported from Room EQ Wizard file
# Created: 06.23.2019

def get_data(path):
    result = {
        'name':'',
        'points':[]
    }

    f = open(path, 'r')

    for line in f:
        # Extract name from line like:
        # "* Measurement: Shure SM-57"
        if line.startswith('* Measurement:'):
            result['name'] = line.replace('* Measurement: ', '').rstrip()

        # Extract frequency and amplitude from line like:
        # 2.102, 35.533, -113.200
        if not line.startswith('*'):
            values = line.split(',')[:2]
            values = [float(value) for value in values]
            values = tuple(values)
            result['points'].append(values)

    f.close()

    return result