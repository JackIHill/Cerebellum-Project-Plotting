#!/usr/bin/env python3
"""
This script is used to create simple and logged scatter plots for cerebellum and cerebrum morphology in primates.
You will be given the option to save simple and logged plots (to separate folders).
"""

# TODO:
#  1) Add logging and unit testing
#  2) amend module docstring
#  3) implement threading due to plot_variables inner function calls
#  4) use vars to hold information for creating logged save files to minimise repeating myself. 
#  5) amend doc for set_colors to be able to use default colors to revert to normal
#  6) move var_combinations try except into var_combinations func?

import os
import sys
import shutil
from itertools import combinations
from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as tk
from matplotlib.lines import Line2D


try:
    data = pd.read_csv('all_species_values.csv', na_values='', usecols=range(7))
    data = data.dropna(how='all', axis='columns').drop(columns='Source')
    data.rename(
        columns={
            'Species ': 'Species',
            'CerebellumSurfaceArea': 'Cerebellum Surface Area',
            'CerebrumSurfaceArea': 'Cerebrum Surface Area',
            'CerebellumVolume ': 'Cerebellum Volume',
            'CerebrumVolume': 'Cerebrum Volume'
            }, inplace=True)

except FileNotFoundError:
    print(
        "CSV not found. Please ensure you have the \'all_species_values.csv\' "
        "in the same directory as this program."
        )
    sys.exit()

DEFAULT_COLORS = {
            'Hominidae': '#7f48b5',
            'Hylobatidae': '#c195ed',
            'Cercopithecidae': '#f0bb3e',
            'Platyrrhini': '#f2e3bd'
            } 

new_defaults = DEFAULT_COLORS.copy()

def var_combinations(cols: list[int]) -> tuple[tuple[str, str], ...]:
    """Get all combinations (not repeated) for a list of columns.

    Args:
        cols (list of int): list of integers representing column index values from .csv. 

    Returns:
        tuple: tuple of tuples, each containing independent/dependent variable pairs.
    """
    var_combinations = tuple(combinations(data.columns[cols], 2))
    return var_combinations


def set_colors(new_colors: dict[str, str]) -> dict[str, str]:
    """Assign custom colors to species for visualisation purposes.

    Args:
        new_colors (dict of str:str, optional): species:color dictionary where valid species names are:
            'Hominidae', 'Hylobatidae', 'Cercopithecidae' or 'Platyrrhini' and valid colors are matplotlib
            named colors or hex color codes.
            
    Returns:
        new_defaults (dict of str: str): default_colors dict merged with values from new_colors. 

    matplotlib named colors: https://matplotlib.org/stable/gallery/color/named_colors.html
    """
    new_defaults.update(new_colors)
    return new_defaults


def plot_variables(xy=None, colors=None, logged=False, save=False, show=False, **kwargs):
    """Plots brain morphology variables

    Args:
        xy (tuple or list, optional): accepts tuple of tuples, each containing independent/dependent variable pairs, 
            or a list of integers representing column index values from .csv, to be passed to var_combinations().
            Ensure a minimum of two integers are defined. Defaults to var_combinations([4, 3, 1]).
        colors (dict of str: str), optional): species:color dictionary where valid species names are:
            'Hominidae', 'Hylobatidae', 'Cercopithecidae' or 'Platyrrhini' and valid colors are matplotlib
            named colors or hex color codes. Maps the respective colors to each species' plot markers. Defaults to: 
            {'Hominidae': '#7f48b5', 'Hylobatidae': '#c195ed', 'Cercopithecidae': '#f0bb3e', 'Platyrrhini': '#f2e3bd'}.
        logged (bool, optional): produce simple (unlogged, False) or logged plots (True). Defaults to False.
        save (bool, optional): if True, save figure to 'Saved Simple Plots' or 'Saved Log Plots' folders, 
            respective of `logged`. Passes xy (tuple, optional) to save_plots() to provide detailed file names, 
            and SIMPLE/LOG_PLOT_DETAILS.txt files to the respective save folder. Defaults to False.
        show (bool, optional): if True, call plt.show() to output figures to new windows. Defaults to False.
        **kwargs (any): other keyword arguments from matplotlib.pyplot.scatter
    """
    if xy is None:
        xy = var_combinations([4, 3, 1])
    elif any(isinstance(col_index, (int)) for col_index in xy):
        try:
            invalid_indices = []
            for col_index in xy:
                if col_index >= len(data.columns) or (data[data.columns[col_index]].dtype != 'float64'):
                    invalid_indices.append(col_index)
            xy = [col_index for col_index in xy if col_index not in invalid_indices]
            
            if len(xy) >= 2:
                if invalid_indices:
                    print(
                        f'The following invalid indices were passed to `xy`: {invalid_indices}.\n'
                        f'Combinations were therefore made from the following indices only: {xy}.'
                        )
                xy = var_combinations(xy)
            else:
                raise AttributeError     
        except AttributeError:
            print(
                f'\nNo valid combinations could be made from the list passed to `xy`.'
                f' {"The only valid number passed was: " + ("".join(str(x) for x in xy)) + "." if xy else ""}\n'
                f'The default combination [4, 3, 1] was therefore plotted. For custom combination-plotting,'
                f' please ensure the list has at least 2 valid indices, where such indices refer to columns'
                f' containing floating-point numbers or integers.\n'
                )
            xy = var_combinations([4, 3, 1])

    if colors is None:
        colors = new_defaults
    else:
        def_copy = new_defaults.copy()
        def_copy.update(colors)
        colors = def_copy
   
    # Define scaling properties for each number of axes in a figure.
    left_margin = 2.5
    if len(xy) == 1:
        category_size = 0.1
        right_margin = 2.5
    elif len(xy) == 2:
        category_size = 1.5
        right_margin = 3.5
    elif len(xy) >= 3:
        category_size = 2
        right_margin = 5

    fig_width = left_margin + right_margin + len(xy) * category_size

    # Define scaling properties for subplot when more than 3 var combinations are plotted.
    if len(xy) <= 3:
        cols = len(xy)
        rows = 1
    else:
        cols = int(len(xy) // 1.66)
        rows = 2

    # Remove minor ticks for logged plots. 
    plt.rcParams['xtick.minor.size'] = 0
    plt.rcParams['ytick.minor.size'] = 0

    # Give legend markers same color as predefined taxon colors. Marker placed on white line. 
    handles = [
        Line2D([0], [0],
        color='w', marker='o', markerfacecolor=v,
        markeredgecolor='k', markeredgewidth='0.5',
        markersize=4, label=k,
        ) for k, v in colors.items()
        ]
    
    fig, axs = plt.subplots(rows, cols, figsize=(fig_width, 4), squeeze=False)
    axs = axs.flatten()

    for i, (x, y) in enumerate(xy):
        axs[i].scatter(data[x], data[y], c=data.Taxon.map(colors), edgecolor='k', **kwargs)

        ax_legend = axs[i].legend(
            title='Taxon',
            title_fontsize='9',
            handles=handles,
            loc='upper left',
            fontsize=10
            )
        ax_legend.get_frame().set_color('white')

        if not logged:
            axs[i].set(
                title=f'Primate {xy[i][0]} against\n{xy[i][1]}',
                xlabel=f'{xy[i][0]}',
                ylabel=f'{xy[i][1]}'
                )
        
        elif logged:
            axs[i].set(
                title=f'Logged Primate {xy[i][0]} against\n{xy[i][1]}',
                xlabel=f'Log {xy[i][0]}',
                ylabel=f'Log {xy[i][1]}'
                )
            
            axs[i].set_xscale('symlog')
            axs[i].get_xaxis().set_major_formatter(tk.ScalarFormatter())

            axs[i].set_yscale('symlog')   
            axs[i].get_yaxis().set_major_formatter(tk.ScalarFormatter())
            axs[i].set_yticks([10, 25, 50, 100, 250, 500, 1000])

            # These variables need custom xticks to better represent the range of values.
            tick_list = [5, 10, 25, 50, 100, 200, 400, 1000]
            if (x, y) == ('Cerebrum Volume', 'Cerebellum Volume'):
                axs[i].set_xticks(tick_list)
            else:
                axs[i].set_xticks(tick_list[:-1])

        fig.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
    
    if save:
        save_plots(fig, xy, logged)

    if show:
        plt.show()


def plot_regression():
    """Plots linear regression line for the volume-against-volume plot."""
    plot_variables((('Cerebrum Volume', 'Cerebellum Volume'),))
    data_2 = data[['Cerebellum Volume', 'Cerebrum Volume']].copy(deep=False)

    data_2.dropna(inplace=True)

    predict = 'Cerebellum Volume'
    x = np.array(data_2.drop([predict], axis=1))
    y = np.array(data_2[predict])

    model = np.polyfit(x[:, 0], y, 1)
    predict = np.poly1d(model)

    x_lin_reg = range(0, 1600)
    y_lin_reg = predict(x_lin_reg)
    plt.plot(x_lin_reg, y_lin_reg, c='k')

    
def save_plots(figure, xy: tuple[tuple[str, str]], logged) -> None:
    """Saves simple/log plots to respective folders.

    Each figure's save file is named as such:
    '(number of plots in figure) Simple Plot(s) - #(number denoting order in which file was saved).

    SIMPLE_PLOT_DETAILS.txt or LOG_PLOT_DETAILS.txt files also created containing number of plots, save file order, 
    value of `xy`, and figure creation time. 

    Args:
        figure (Matplotlib figure): the current figure object defined within plot_variables().
        xy (tuple): tuple of tuples, each containing independent/dependent variable pairs.
        logged (bool): determines creation of 'Saved Simple Plots' (False), or 'Saved Log Plots' folders (True).
    """
    
    log_or_simple = "Log" if logged else "Simple"
    default_check = "Default" if xy == var_combinations([4, 3, 1]) else log_or_simple
    len_if_custom = str(len(xy)) + " " if xy != var_combinations([4, 3, 1]) else ""
    is_len_plural = "s" if len(xy) > 1 else ""

    save_folder = os.path.join(os.getcwd(), f'Saved {log_or_simple} Plots')
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    png_id = 1
    while os.path.exists(f'Saved {log_or_simple} Plots/{len_if_custom}{default_check} Plot{is_len_plural} - #{png_id:d}.png'):
        png_id += 1
    figure.savefig(f'Saved {log_or_simple} Plots/{len_if_custom}{default_check} Plot{is_len_plural} - #{png_id:d}.png')

    var_list = "\n".join(str(x) for x in xy)
    with open(f'Saved {log_or_simple} Plots/{log_or_simple.upper()}_PLOT_DETAILS.txt', 'a') as save_details:
        save_details.write(
            f'{len_if_custom}{default_check} Plot{is_len_plural} - #{png_id:d} '
            f'-\n{var_list}\n'
            f'- Figure Created on {datetime.now().strftime("%d-%m-%Y at %H:%M:%S")}\n'
            f'------------------------------------------------------\n'
            )
        
        print(
            f'{default_check + " " + log_or_simple if xy == var_combinations([4, 3, 1]) else default_check}'
            f' Plot{is_len_plural} saved to {os.path.join(os.getcwd(), f"Saved {log_or_simple} Plots")}'
            )
        


def delete_folder(logged=False) -> None:
    """Deletes simple or log save folder depending on if logged=True is passed as an argument.

    Args:
        logged (bool): determines deletion of simple plot (False), or log plot save folders (True).
    """
    if not logged:
        folder = os.path.join(os.getcwd(), r'Saved Simple Plots')
    else:
        folder = os.path.join(os.getcwd(), r'Saved Log Plots')

    try:
        shutil.rmtree(folder)
    except FileNotFoundError:
        print(
            f"No '{os.path.basename(os.path.normpath(folder))}' folder exists in the current directory, "
            f"and so could not be deleted.")


if __name__ == '__main__':
    # plot_variables([['Cerebrum Volume', 'Cerebellum Volume'],], logged=True, show=True)

    plot_variables([1, 7, 0, 6, 8], colors={'Hominidae':'lime'}, show=True, alpha=0.5)
   
    # plot_variables(colors={'Hominidae':'Blue'}, show=True, save=True)
    
    # delete_folder(logged=True)
    # plot_regression()
