#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 14:47:49 2026

@author: richard
"""

def output_position(ballpos_mm, fieldSize_mm)->None:
    """
    TODO: Output via I2C
    
    Parameters
    ----------
    ballpos_mm : tuple(int, int)
        The current ball position measured in millimeters from the center position
    fieldSize_mm : tuple(int, int)
        The size of the playing field measures in millimeters. The default is (1200, 680) or 120cm x 68cm.

    Returns
    -------
    None.

    """
    # Write output to command line:
    print(f"Ball at x={ballpos_mm[0]} y={ballpos_mm[1]}")
    
    # TODO Output via I2C: