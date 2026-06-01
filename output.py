#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 14:47:49 2026

@author: richard
"""

def output_position(x, y)->None:
    """
    TODO: Output via I2C
    
    Parameters
    ----------
    x : TYPE
        ball x-coordinate.
    y : TYPE
        Ball y-coordinate.

    Returns
    -------
    None.

    """
    # Write output to command line:
    print(f"Ball at x={x} y={y}")
    
    # TODO Output via I2C: