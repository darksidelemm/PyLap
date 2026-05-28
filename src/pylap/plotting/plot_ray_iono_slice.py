#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 20:49:47 2020

@author: williamliles
"""

#M
#M Name :
#M   plot_ray_iono_slice.m
#M
#M Purpose:
#M   Plots ionospheric slice in an arc (to preserve curved Earth geometry)
#M   and overplots rays
#M
#M Calling sequence:
#M   plot_ray_iono_slice(iono_grid, start_range, end_range, ...
#M           range_inc, start_height, end_height, height_inc, ray)
#M
#M   [axis_handle, ray_handle] = plot_ray_iono_slice(iono_grid, start_range,
#M           end_range, range_inc, start_height, end_height, height_inc, ray)
#M
#M Inputs:
#M   iono_grid    - grid (height, ground range) of ionospheric plasma
#M                    frequencies (MHz)
#M   start_range  - starting ground range of iono_grid (km)
#M   end_range    - final ground range of iono_grid (km)
#M   range_inc    - ground range increment of iono_grid (km)
#M   start_height - starting height of iono_grid (km)
#M   end_height   - final height of iono_grid (km)
#M   height_inc   - height increment of iono_grid (km)
#M   ray          - structure containing ray information:
#M     ray(N).ground_range  = ground range vector for Nth ray
#M     ray(N).height        = height vector for Nth ray
#M
#M     Notes:
#M     1. The ground range of the rays can also be input with ray(N).gndrng .
#M        However, if both of the gndrng and ground_range fields are defined,
#M        then the latter will be used.
#M     2. If rays are not required to be plotted, set ray = []
#M
#M Optional Inputs:
#M   The required inputs can be followed by parameter/value pairs to specify
#M   additional properties of the rays. These parameter/value pairs are any
#M   that are accepted by the MATLAB inbuilt plot function. For example,
#M
#M   plot_ray_iono_slice(iono_pf_subgrid, start_range, end_range, range_inc, ...
#M        start_ht, end_ht, height_inc, ray(8:9), 'color', 'w', 'linewidth', 2)
#M
#M   will create white rays with line width of 2 points.
#M
#M Outputs:
#M   axis_handle  - the handle of the plot axis
#M   ray_handle   - vector containing handle for each ray
#M
#M Modification History:
#M   14/05/2008  V1.0  M. A. Cervera
#M     Initial Version.
#M
#M   24/06/2009  V1.1  M. A. Cervera
#M     Minor modification to font sizes to improve display on small screens
#M
#M   06/07/2015  V1.2  M. A. Cervera
#M      Minor modification to limit the size of the displayed figure window on
#M      large screens when using software opengl. This is to mitigate framebuffer
#M      issues.
#M

import numpy as np
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
import sys
import platform
from qtpy.QtWidgets import QApplication


def plot_ray_iono_slice(iono_grid, start_range, end_range, range_inc,
                start_height, end_height, height_inc, ray,
                axis_font_scale=0.55, bottom_margin_scale=0.05,
                colorbar_y=0.31, **kwargs):

    
    #M Input consistency and error checking
 
    iono_grid_size = iono_grid.shape
  
   
    heights = np.linspace(start_height, end_height, int((end_height-start_height) / height_inc),True,False,int)
    no_heights = heights.size + 1
  
    if no_heights != iono_grid_size[0]:
            print('start_height, end_height and height_inc inconsistent '
                  'with iono_grid in plot_ray_iono_slice')
            sys.exit()
    ranges = np.linspace(start_range, end_range, int(((end_range - start_range)
                         + 1) / range_inc))
    no_ranges = ranges.size + 1
    if no_ranges != iono_grid_size[1]:
            print('start_range, end_range and range_inc inconsistent with '
                  'iono_grid in plot_ray_iono_slice')
            sys.exit()


    for rayID in range(0, len(ray)):
        if 'ground_range' in ray[rayID].keys():
          ray[rayID]['gndrng'] = ray[rayID]['ground_range']

    for ii in range(len(ray)):
      if(~np.isnan(np.all(ray[ii]['gndrng']))):
        np.nan_to_num(ray[ii]['gndrng'],False,0.0)
      if len(ray[ii]['height']) != len(ray[ii]['gndrng']):
        print('ray height and ground range vectors have diffent lengths' +
                  ' in plot_ray_iono_slice')
        sys.exit()


    
    app = QApplication.instance() or QApplication(sys.argv)
    screen = app.screens()[0]
    dpi= screen.physicalDotsPerInch()
    scrsz = screen.geometry()
    scrsz_height = int(scrsz.height() * 0.6)
    scrsz_width = int(scrsz.width() * 0.9)
    op_sys = platform.system()
    screen_height_in = int(scrsz_height/dpi)  # leave 1/2 inch margins
    screen_width_in = int(scrsz_width/dpi)  # leave 1/2 inch margins
    # vert_label_corr is to center height label
    if op_sys == 'Windows':
        fontsize1 = 13
        fontsize2 = 15
        vert_label_corr = 0
    elif op_sys == 'Darwin':   # True is Apple Mac
        fontsize1 = 16
        fontsize2 = 18
        vert_label_corr = 0
        if scrsz.width() < 1400:
            fontsize1 = 12
            fontsize2 = 14
            vert_label_corr = 0
    elif op_sys == 'Linux':
        fontsize1 = 10
        fontsize2 = 12
        vert_label_corr = 100
    else:                    # default
        fontsize1 = 16
        fontsize2 = 16
        vert_label_corr = 0

    fontsize1 = max(1, fontsize1 * axis_font_scale)
    fontsize2 = max(1, fontsize2 * axis_font_scale)
    #M initialize the figure

    max_range = end_range - start_range
    
    #M determine how the display window should be sized
    ypos = scrsz.height() * 0.25
    xsize = scrsz.width() * 0.95
    ysize = scrsz.height() * 0.5
    
 
    
    #M
    #M set up the axes and plot the ionosphere
    #M
    
    #M convert the coodinate frame to curved Earth geometry
    max_range_idx = max_range / range_inc + 1
    rad_earth = 6371.  # earth radius in km
    r = np.add(rad_earth, np.linspace(start_height, end_height, 
                    int(((end_height - start_height) + 1) / height_inc) + 1))
    gnd_range = np.linspace(0, max_range, int((max_range +1) / range_inc) + 1)
    theta = np.divide( np.subtract(gnd_range, max_range /2), rad_earth)
    rt = r.reshape((-1, 1))  # doing the transpose
    iono_X = np.multiply(rt, np.sin(theta))
    iono_Y = np.multiply(rt, np.cos(theta))
    
    #M plot the ionospheric slice
    fig = plt.figure(figsize=(max(screen_width_in, 8), max(screen_height_in, 5)))
    ax = fig.add_axes([0.12, 0.30, 0.78, 0.58])
    ax.axis('off')  # turn off rectangler suround box and tic marks
    image = ax.pcolormesh(
        iono_X, iono_Y, iono_grid, shading='gouraud', vmin=0, vmax=14
    )
    ax.set_aspect('equal')
    ax.axis('off')  # turn off rectangler suround box and tic marks
   
    l, b, w, h = ax.get_position().bounds
    #M set the axis to take up most of the horizontal extent - leave some space
 
    min_X = iono_X.min()
    max_X = iono_X.max()
    min_Y = iono_Y.min()
    max_Y = iono_Y.max()
    hspace_for_ticks = (max_X - min_X) / 40
    vspace_for_ticks = (max_Y - min_Y) / 25
      
    #M find horizontal size of axis in pixels and calculate data-to-pixel ratio
   
    l, b, w, h = ax.get_position().bounds
    w_pixel = scrsz.width() * w
    pix_ratio = w / (max_X - min_X)
    #M determine the vertical size of axis in pixels
  
    pixels_height = pix_ratio * (max_Y - min_Y)
           #M leave space for colourbar
    b_pixel = scrsz.height() * b
    pixels_bottom = 50
 
    
    #M determine the vertical size of figure in pixels required to fit axes,
    #M colorbar and a margin and set the figure accordingly
    
    top = pixels_bottom + pixels_height
    l, b, w, h = ax.get_position().bounds
    pos_height = top + 15
  
    #M handle of the axes
    #M display ground-range ticks
    
    acceptable_tick_stepsize = np.array([100, 150, 200, 250, 500, 1000])
    tick_stepsize = max_range / 8
    pp = np.argmin(np.abs(acceptable_tick_stepsize - tick_stepsize))
    tick_stepsize = acceptable_tick_stepsize[pp]

    tick_gndrng = np.multiply(np.linspace(0, int(max_range / tick_stepsize),
                                  int(max_range / tick_stepsize) + 1),
                                tick_stepsize)
    tick_theta = np.divide(np.subtract(tick_gndrng, max_range / 2), rad_earth)
    tick_len = (max_range / 30000) * 200
    tick_r = rad_earth + start_height
    for idx in range(0, len(tick_theta)):
        tick_X1 = tick_r * np.sin(tick_theta[idx])
        tick_X2 = (tick_r - tick_len) * np.sin(tick_theta[idx])
        tick_Y1 = tick_r * np.cos(tick_theta[idx])
        tick_Y2 = (tick_r - tick_len) * np.cos(tick_theta[idx])
        xpts = np.array([tick_X1, tick_X2])
        ypts = np.array([tick_Y1, tick_Y2])
        ax.plot(xpts, ypts, 'k', linewidth=2)
        tick_label_X = (tick_r - 3 * tick_len) * np.sin(tick_theta[idx])
        tick_label_Y = (tick_r - 3 * tick_len) * np.cos(tick_theta[idx])
        tick_label = str(int(tick_gndrng[idx] + start_range))
        ax.text(
            tick_label_X, tick_label_Y, tick_label,
            horizontalalignment='center', verticalalignment='top',
            fontsize=fontsize1
        )
    #M display the 'ground range - axis' label
    text_theta = 0
    xlabel_X = rad_earth * np.sin(text_theta)
    xlabel_Y = rad_earth * np.cos(text_theta) - tick_len * 6
    
    ax.text(
        xlabel_X, xlabel_Y, 'Ground Range (km)', fontsize=fontsize2,
        horizontalalignment='center', verticalalignment='top'
    )
         
    #M
    #M display the height ticks
    #M
    num_ticks = int(75 * (end_height - start_height) / max_range)
    num_ticks = np.min(np.array([9, num_ticks]))
    num_ticks = np.max(np.array([2, num_ticks]))
    
    acceptable_tick_stepsize = np.array([50, 100, 200, 250, 300,
                                         400, 500, 600, 1000])
    tick_stepsize = (end_height - start_height) / (num_ticks - 1)
    pp  = np.argmin(np.abs(acceptable_tick_stepsize - tick_stepsize))
    tick_stepsize = acceptable_tick_stepsize[pp]
    if ((num_ticks - 1) * tick_stepsize) < end_height:
        if ((num_ticks - 1) * tick_stepsize) < end_height - tick_stepsize:
            if pp < len(acceptable_tick_stepsize):
               tick_stepsize = acceptable_tick_stepsize[pp+1]
        else:
             num_ticks = num_ticks + 1
    
  
    while ((num_ticks - 1) * tick_stepsize) > end_height:
      num_ticks = num_ticks - 1
  
    tick_theta =  (0 - max_range / 2) / rad_earth
    tick_len = max_range / 150
    
    for idx in range(0, num_ticks):
        tick_X1 = (rad_earth + idx * tick_stepsize) * np.sin(tick_theta)
        tick_X2 = tick_X1 - tick_len * np.cos(np.abs(tick_theta))
        tick_Y1 = (rad_earth + idx * tick_stepsize) * np.cos(tick_theta)
        tick_Y2 = tick_Y1 - tick_len * np.sin(np.abs(tick_theta))
        xpts = np.array([tick_X1, tick_X2])
        ypts = np.array([tick_Y1, tick_Y2])
        ax.plot(xpts, ypts, 'k', linewidth=2)
        tick_label = str(tick_stepsize * idx)
        tick_label_X = tick_X2 - tick_len / 2
        tick_label_Y = tick_Y2
        ax.text(
            tick_label_X, tick_label_Y, tick_label,
            horizontalalignment='right', verticalalignment='center',
            fontsize=fontsize1
        )
      #M display the 'height - axis' label
      
    # the constant 0.007 is to increase speration of label from values
    text_theta = (0 - max_range / 2) / rad_earth
    text_rot = -text_theta * 180 / np.pi + 90
    
    pos_adjust = tick_len * ((end_height - start_height) / 400 + 7.5) # 5
    r_dist = (rad_earth + (end_height - start_height) / 2) - vert_label_corr
    ylabel_X = r_dist * np.sin(text_theta)  - pos_adjust \
                   * np.cos(np.abs(tick_theta))
    ylabel_Y = r_dist * np.cos(text_theta) - pos_adjust \
                   * np.sin(np.abs(tick_theta))
    
    ylabel_X = ylabel_X - 100
    ax.text(
        ylabel_X, ylabel_Y, 'Altitude (km)', rotation=text_rot,
        horizontalalignment='center', verticalalignment='center',
        fontsize=fontsize2
    )

    # Text artists do not expand data limits automatically. Reserve space for
    # the hand-drawn range/height scales so labels do not overlap the image.
    x_margin = max((max_X - min_X) * 0.08, 140)
    y_margin_bottom = max((max_Y - min_Y) * bottom_margin_scale, tick_len * 4)
    y_margin_top = max((max_Y - min_Y) * 0.05, 25)
    ax.set_xlim(min(min_X, ylabel_X) - x_margin, max_X + x_margin)
    ax.set_ylim(min_Y - y_margin_bottom, max_Y + y_margin_top)
    
    #M
    #M set up the colourbar
    #M
    
    cax = fig.add_axes([0.30, colorbar_y, 0.40, 0.04])
    cbar = fig.colorbar(
        image, cax=cax, orientation='horizontal',
        label='Plasma Frequency (MHz)'
    )
    cbar.ax.tick_params(labelsize=fontsize1)
    cbar.ax.xaxis.label.set_size(fontsize2)
    
    
    #M
    #M now plot the rays
    #M
    ray_kwargs = kwargs.copy()
    if 'linewidth' in ray_kwargs:
        ray_kwargs['linewidth'] = ray_kwargs['linewidth'] * 0.5
    elif 'lw' in ray_kwargs:
        ray_kwargs['lw'] = ray_kwargs['lw'] * 0.5
    else:
        ray_kwargs['linewidth'] = plt.rcParams['lines.linewidth'] * 0.5

    ray_handle = []
    # not the code below assumes that the loop will not execute  print(ray[idx].keys())is ray is
    # an empy list
    for idx in range(len(ray)):
      if len(ray[idx]['gndrng'])!=0:
        #M resample ray at a finer step size
        no_points = int((ray[idx]['gndrng'][-1] 
                     - ray[idx]['gndrng'][0]) /
                        0.1) + 1
        ray_gndrng = np.linspace(ray[idx]['gndrng'][0], 
                                 ray[idx]['gndrng'][-1], no_points)
        ray_height = np.interp(ray_gndrng, ray[idx]['gndrng'],
                               ray[idx]['height'])
    
        #M mask out the ray where it lies outside the ionosphere image
        ray_gndrng[ray_gndrng < start_range] = np.nan
        ray_gndrng[ray_gndrng > end_range] = np.nan
        ray_height[ray_height < start_height] = np.nan
        ray_height[ray_height > end_height] = np.nan
        #M determine the coodinates of the ray in the image and plot it
        ray_r = ray_height + rad_earth
        ray_theta = (ray_gndrng - start_range - max_range/2) / rad_earth
        ray_X = ray_r * np.sin(ray_theta)
        ray_Y = ray_r * np.cos(ray_theta)
        h = ax.plot(ray_X, ray_Y, **ray_kwargs)
        ray_handle.append(h)
        
        import os

        script_dir = os.path.dirname(__file__)
        results_dir = os.path.join(script_dir, 'results/')
        sample_file_name = "sample10"

        if not os.path.isdir(results_dir):
          os.makedirs(results_dir) 
          
        # break


    # plt.scatter([440],[6571],s=500,marker='*',color='red',ec='k',zorder=100,clip_on=False,)
    # ipdb.set_trace()
    return ax, ray_handle
    
