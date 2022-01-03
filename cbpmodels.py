#!/usr/bin/env python3
"""
This script is used to create simple and logged scatter plots for cerebellum and cerebrum morphology in primates.
You will be given the option to save simple and logged plots (to separate folders).
"""

# TODO:
#  1) Add logging and unit testing
#  2) Could make the tuple of tuples a dict e.g. {independent variable (key), dependent variable (value), indep...}
#  3) add to requirements.txt (numpy)

import os
import sys
import shutil
from itertools import combinations as iter_combinations
from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as tk
from matplotlib.lines import Line2D


try:
    data = pd.read_csv('all_species_values.csv', na_values='', usecols=range(7))
    data = data.dropna(how='all', axis='columns').drop(columns='Source')
    data.rename(columns={
        'Species ': 'Species',
        'CerebellumSurfaceArea': 'Cerebellum Surface Area',
        'CerebrumSurfaceArea': 'Cerebrum Surface Area',
        'CerebellumVolume ': 'Cerebellum Volume',
        'CerebrumVolume': 'Cerebrum Volume'
        }, inplace=True)

except FileNotFoundError:
    print('CSV not found. Please ensure you have the \'all_species_values.csv\' '
          'in the same directory as this program.')
    sys.exit()


# Column 3 (Cerebrum Surface Area) is not plotted due to not enough data.
# Add '2' to col_names list below if want to include that column.
col_names = data.columns[[4, 3, 1]]
var_combinations = tuple(iter_combinations(col_names, 2))

# Assign custom colors to species for visualisation purposes. 
colors = {
    'Hominidae': '#7f48b5',
    'Hylobatidae': '#c195ed',
    'Cercopithecidae': '#f0bb3e',
    'Platyrrhini': '#f2e3bd'
    }

# Give legend markers same color as predefined taxon colors.
handles = [
    Line2D([0], [0],
           color='w', marker='o', markerfacecolor=v,
           markeredgecolor='k', markeredgewidth='0.5',
           markersize=4, label=k,
           ) for k, v in colors.items()
          ]


def plot_variables(xy=var_combinations, logged=False, save=False):
    """
    - Plots brain morphology variables.
    - Pass no arguments to plot 3 default plots.
    - Pass logged=True with no arguments to log these default plots.
    - Pass a tuple containing tuples which contain variable pairs to plot custom variables, like so:
    - plot_variables((('Cerebrum Volume', 'Cerebellum Volume'),)).
    """
    category_size = None
    right_margin = None
    left_margin = None

    # sets scaling properties for each number of axes in a figure.
    if len(xy) == 1:
        category_size = 0.1
        left_margin = 2.5
        right_margin = 2.5
    elif len(xy) == 2:
        category_size = 1.5
        left_margin = 2.5
        right_margin = 3.5
    elif len(xy) == 3:
        category_size = 2
        left_margin = 2.5
        right_margin = 5

    fig_width = left_margin + right_margin + len(xy) * category_size

    # Removes minor x/yticks for logged plots. 
    plt.rcParams['xtick.minor.size'] = 0
    plt.rcParams['ytick.minor.size'] = 0

    fig1, axs1 = plt.subplots(1, (len(xy)), figsize=(fig_width, 4), squeeze=False)
    axs1 = axs1.flatten()

    for i, (x, y) in enumerate(xy):
        axs1[i].scatter(data[x], data[y], c=data.Taxon.map(colors), edgecolor='k')

        ax_legend = axs1[i].legend(
            title='Taxon',
            title_fontsize='9',
            handles=handles,
            loc='upper left',
            fontsize=10
            )
        ax_legend.get_frame().set_color('white')

        if not logged:
            axs1[i].set(
                title=f'Primate {xy[i][0]} against\n{xy[i][1]}',
                xlabel=f'{xy[i][0]}',
                ylabel=f'{xy[i][1]}'
                )
        
        elif logged:
            axs1[i].set(
                title=f'Logged Primate {xy[i][0]} against\n{xy[i][1]}',
                xlabel=f'Logged {xy[i][0]}',
                ylabel=f'Logged {xy[i][1]}'
                )
            
            axs1[i].set_xscale('log')
            axs1[i].get_xaxis().set_major_formatter(tk.ScalarFormatter())

            # These variables need custom xticks to better represent the range of values.
            tick_list = [5, 10, 25, 50, 100, 200, 400, 1000]
            if (x, y) == ('Cerebrum Volume', 'Cerebellum Volume'):
                axs1[i].set_xticks(tick_list)
            else:
                axs1[i].set_xticks(tick_list[:-1])

            axs1[i].set_yscale('log')
            axs1[i].get_yaxis().set_major_formatter(tk.ScalarFormatter())
            axs1[i].set_yticks([10, 25, 50, 100, 250, 500, 1000])

        fig1.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
    
    if save:
        save_plots(fig1, xy, logged)


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

    
def save_plots(figure, xy, logged):
    if not logged:
        while True:
            save_folder = os.path.join(os.getcwd(), r'Saved Simple Plots')
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)

            png_id = 1
            if xy is var_combinations:
                while os.path.exists(f'Saved Simple Plots/Default Simple Plots - #{png_id:d}.png'):
                    png_id += 1
                figure.savefig(f'Saved Simple Plots/Default Simple Plots - #{png_id:d}.png')

                print(f'Default Plots Saved to {os.path.join(os.getcwd(), r"Saved Simple Plots")}')

            else:
                while os.path.exists(f'Saved Simple Plots/{len(xy)} Simple Plot(s) - #{png_id:d}.png'):
                    png_id += 1
                figure.savefig(f'Saved Simple Plots/{len(xy)} Simple Plot(s) - #{png_id:d}.png')

                var_list = [x for x in xy]
                with open(f'Saved Simple Plots/SIMPLE_PLOT_DETAILS.txt', 'a') as save_details:
                    save_details.write(
                        f'{len(xy)} Simple Plot(s) - #{png_id:d}'
                        f' - {*var_list,}\n'
                        f' - Figure Created on {datetime.now().strftime("%d-%m-%Y at %H:%M:%S")}\n\n'
                        )
                    
                    print(f'Simple Plots saved to {os.path.join(os.getcwd(), r"Saved Simple Plots")}')
            break

    elif logged:           
        while True:
            save_folder = os.path.join(os.getcwd(), r'Saved Log Plots')
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)

            png_id = 1
            if xy is var_combinations:
                while os.path.exists(f'Saved Log Plots/Default Log Plots - #{png_id:d}.png'):
                    png_id += 1
                figure.savefig(f'Saved Log Plots/Default Log Plots - #{png_id:d}.png')

                print(f'Default Plots Saved to {os.path.join(os.getcwd(), r"Saved Log Plots")}')

            else:
                while os.path.exists(f'Saved Log Plots/{len(xy)} Log Plot(s) - #{png_id:d}.png'):
                    png_id += 1
                figure.savefig(f'Saved Log Plots/{len(xy)} Log Plot(s) - #{png_id:d}.png')

                var_list = [x for x in xy]
                with open(f'Saved Log Plots/LOG_PLOT_DETAILS.txt', 'a') as save_details:
                    save_details.write(
                        f'{len(xy)} Log Plot(s) - #{png_id:d}'
                        f' - {*var_list,}\n'
                        f' - Figure Created on {datetime.now().strftime("%d-%m-%Y at %H:%M:%S")}\n\n'
                        )
                    
                    print(f'Log Plots saved to {os.path.join(os.getcwd(), r"Saved Log Plots")}')
            break


def delete_folder(logged=False):
    """Deletes simple or log save folder depending on if logged=True is passed as an argument."""
    if not logged:
        folder = os.path.join(os.getcwd(), r'Saved Simple Plots')
    else:
        folder = os.path.join(os.getcwd(), r'Saved Log Plots')

    try:
        shutil.rmtree(folder)
    except FileNotFoundError:
        print(f'No "{os.path.basename(os.path.normpath(folder))}" folder exists in the current directory, '
              f'and so could not be deleted.')

    # if not logged:
    #     try:
    #         folder = os.path.join(os.getcwd(), r'Saved Simple Plots')
    #         shutil.rmtree(folder)
    #     except FileNotFoundError:
    #         print('No "Saved Simple Plots" folder exists in current working directory,'
    #               ' and so could not be deleted.')
    # else:
    #     try:
    #         folder = os.path.join(os.getcwd(), r'Saved Log Plots')
    #         shutil.rmtree(folder)
    #     except FileNotFoundError:
    #         print('No "Saved Log Plots" folder exists in current working directory,'
    #               ' and so could not be deleted.')


def show_plots():
    """Outputs plots to new windows."""
    plt.show()


if __name__ == '__main__':
    # plot_variables((('Cerebellum Surface Area', 'Cerebellum Volume'),), logged=True, save=True)
    # plot_variables((('Cerebellum Surface Area', 'Cerebellum Volume'),))

    # plot_variables(logged=True)
    plot_variables(save=True)

    # plot_regression()
    show_plots()
