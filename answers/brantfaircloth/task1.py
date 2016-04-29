#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
(c) 2016 Brant Faircloth || http://faircloth-lab.org/
All rights reserved.

This code is distributed under a 3-clause BSD license. Please see
LICENSE.txt for more information.

Created on 28 April 2016 14:57 CDT (-0500)
"""

import os
import numpy
import pandas
import argparse

#import pdb


class FullPaths(argparse.Action):
    """Expand user- and relative-paths"""
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))


def get_args():
    """Get arguments from CLI"""
    parser = argparse.ArgumentParser(
        description="""Parse the Amniote CSV database"""
    )
    parser.add_argument(
        "--input",
        action=FullPaths,
        type=str,
        required=True,
        help="""The output file path"""
    )
    parser.add_argument(
        "--parameters",
        nargs='+',
        required=True,
        type=str,
        help="""The parameters to summarize"""
    )
    parser.add_argument(
        "--output",
        action=FullPaths,
        type=str,
        required=True,
        help="""The output file path"""
    )
    return parser.parse_args()


def get_dict_of_classes_and_families(df):
    temp = df[['class', 'order']].drop_duplicates()
    return {item[1].values[1]: item[1].values[0] for item in temp.iterrows()}


def main():
    args = get_args()
    print("Reading CSV file...")
    df = pandas.read_csv(args.input)
    # replace missing data entries
    df = df.replace(-999, numpy.nan)
    classes_and_families = get_dict_of_classes_and_families(df)
    print("Getting Order list...")
    orders = df['order'].unique().tolist()
    # create new data frame to hold results
    new_df = pandas.DataFrame(columns=[
        'class',
        'order',
        'parameter',
        'mean',
        'ci',
        'min',
        'max',
        'median']
    )
    for order in orders:
        print("Processing {}".format(order))
        order_results = {}
        for param in args.parameters:
            # remove errant commas that may come through in param string
            param = param.strip(",")
            series = df[df['order'] == order][param]
            order_results['class'] = classes_and_families[order]
            order_results['order'] = order
            order_results['parameter'] = param
            order_results['mean'] = series.mean()
            order_results['ci'] = 1.96 * (numpy.std(series, ddof=1) / numpy.sqrt(len(series)))
            order_results['min'] = series.min()
            order_results['max'] = series.min()
            order_results['median'] = series.median()
            new_df = new_df.append(order_results, ignore_index=True)
    print("Writing new CSV file...")
    new_df.to_csv(args.output, index=False)

if __name__ == '__main__':
    main()
