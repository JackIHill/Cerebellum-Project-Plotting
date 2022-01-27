#!/usr/bin/env python3
"""
Create simple and/or logged scatter plots for cerebellum and cerebrum morphology in primates.
"""

import sys
import shutil
import warnings
from pathlib import Path
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

class Scatter():

    ORIGINAL_COLORS = {
                'Hominidae': '#7f48b5',
                'Hylobatidae': '#c195ed',
                'Cercopithecidae': '#f0bb3e',
                'Platyrrhini': '#f2e3bd'
                } 
    new_def_colors = ORIGINAL_COLORS.copy()

    __instances = []
    
    def __init__(
        self, xy=None, colors=None, logged=False, *, figsize=None, grid=None, edgecolor='k', marker='o', 
        title=None, legend_loc='upper left'
        ):
        self.xy = xy
        self.colors = colors
        self.logged = logged
        self._figsize = figsize
        self._grid = grid
        self.edgecolor = edgecolor
        self.marker = marker
        self.title = title
        self.legend_loc = legend_loc

        Scatter.__instances.append(self)
    
    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, xy):
        if xy is None:
            xy = Scatter.var_combinations([4, 3, 1])
        elif all(isinstance(col_index, (int)) for col_index in xy):
            xy = Scatter.var_combinations(xy)
        self._xy = xy

    @property
    def colors(self):
        return self._colors
    
    @colors.setter
    def colors(self, colors):
        if colors is None:
            colors = Scatter.new_def_colors
        else:
            def_copy = Scatter.new_def_colors.copy()
            def_copy.update(colors)
            colors = def_copy
        self._colors = colors

    @property
    def figsize(self):
        """width, height of subplot figure in inches. default fig_width depends on the number of xy pairs."""
        if self._figsize is None:
            fig_height = 4
            if len(self.xy) == 1:
                fig_width = 5.1
            elif len(self.xy) == 2:
                fig_width = 9
            elif len(self.xy) == 3:
                fig_width = 13.5
            else:
                fig_width = 13.5
                fig_height = 8

            self._figsize = fig_width, fig_height
        return self._figsize
    
    @figsize.setter
    def figsize(self, width_height):
        self._figsize = width_height
        
    @property
    def grid(self):
        """Tuple of number of rows and columns of subplot figure. By default, automatically scales with the
        number of xy pairs.
        """
        if self._grid is None:
            if len(self.xy) <= 3:
                num_rows = 1   
                num_cols = len(self.xy)
            else:
                num_rows = 2
                num_cols = int(len(self.xy) // 1.66)
                
            self._grid = num_rows, num_cols
        return self._grid
    
    @grid.setter
    def grid(self, rows_cols):
        if not all(isinstance(coord, int) for coord in rows_cols):
            raise TypeError('All grid row and column values should be integers.')
        if rows_cols[0] * rows_cols[1] < len(self.xy):
            raise ValueError('All plots must be able to fit within the dimensions of the grid.')

        self._grid = rows_cols
    
    @staticmethod
    def var_combinations(cols: list[int]) -> tuple[tuple[str, str], ...]:
        """Get all pairwise combinations (not repeated) for a list of columns. Return nested tuples containing
        these combinations.

        Args:
            cols (list of int): list of integers representing column index values from .csv. 

        Returns:
            tuple: tuple of tuples, each containing independent/dependent variable pairs.
        
        Raises:
            AttributionError: if the number of valid cols in `cols` is lower than 2 (the required minimum for making
            pairwise combinations). 
        """
        try:
            invalid_cols = []
            for col_index in cols:
                if col_index >= len(data.columns) or (data[data.columns[col_index]].dtype != ('float64' or 'int64')):
                    invalid_cols.append(col_index)

            valid_cols = [col_index for col_index in cols if col_index not in invalid_cols]
            
            if len(valid_cols) >= 2:
                if invalid_cols:
                    warnings.warn(
                        f'The following invalid indices were passed to `xy`: {list(set(invalid_cols))}.'
                        f' Combinations were therefore made from the following indices only: {list(set(valid_cols))}.')

                if len(set(valid_cols)) != len(valid_cols):
                    dupes = list(set([x for x in valid_cols if valid_cols.count(x) > 1]))
                    warnings.warn(
                        f'Duplicates of the following valid column indices were ignored to avoid plotting them'
                        f' against one another: {dupes}.\n')
                
                var_combinations = tuple(combinations(data.columns[list(set(valid_cols))], 2))
            else:
                raise AttributeError

        except AttributeError:
            print(
                f'\nNo valid combinations could be made from the list passed to `xy`. '
                f'{"The only valid index was: " + ("".join(str(c) for c in valid_cols)) + "." if valid_cols else ""}'
                f' The default combination [4, 3, 1] was therefore plotted.\n\nFor custom combination-plotting,'
                f' please ensure the list has at least 2 valid indices, where such indices refer to columns'
                f' containing floating-point numbers or integers.\n'
                )
            var_combinations = tuple(combinations(data.columns[[4, 3, 1]], 2))

        return var_combinations
        
    def plot(self, **kwargs):
        # TODO: docstring
        fig, axs = plt.subplots(self.grid[0], self.grid[1], figsize=(self.figsize), squeeze=False)
        axs = axs.flatten()

        for ax_n, (x, y) in enumerate(self.xy):
            axs[ax_n].scatter(
                data[x], data[y],
                c=data.Taxon.map(self.colors),
                edgecolor=self.edgecolor, marker=self.marker, **kwargs
                )
        
            handles = [
                Line2D([0], [0],
                color='w', marker=self.marker, markerfacecolor=color,
                markeredgecolor=self.edgecolor, markeredgewidth='0.5',
                markersize=4, label=species,
                ) for species, color in self.colors.items()
                ]

            ax_legend = axs[ax_n].legend(
                title='Taxon',
                loc=self.legend_loc,
                handles=handles
                )
            ax_legend.get_frame().set_color('white')

            axs[ax_n].set(
                    title=f'{"Logged " if self.logged else ""}Primate {self.xy[ax_n][0]} against\n{self.xy[ax_n][1]}',
                    xlabel=f'{"Log " if self.logged else ""}{self.xy[ax_n][0]}',
                    ylabel=f'{"Log " if self.logged else ""}{self.xy[ax_n][1]}'
                    )
        
            if self.logged:
                axs[ax_n].set_xscale('symlog')
                axs[ax_n].get_xaxis().set_major_formatter(tk.ScalarFormatter())

                axs[ax_n].set_yscale('symlog')   
                axs[ax_n].get_yaxis().set_major_formatter(tk.ScalarFormatter())
                axs[ax_n].set_yticks([10, 25, 50, 100, 250, 500, 1000])

                # These xy values need custom xticks to better represent the range of values.
                tick_list = [5, 10, 25, 50, 100, 200, 400, 1000]
                if (x, y) == ('Cerebrum Volume', 'Cerebellum Volume'):
                    axs[ax_n].set_xticks(tick_list)
                else:
                    axs[ax_n].set_xticks(tick_list[:-1])

                # Remove minor ticks for logged plots. 
                plt.rcParams['xtick.minor.size'] = 0
                plt.rcParams['ytick.minor.size'] = 0

        fig.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)

        if self.title:
            plt.suptitle(self.title, size=16, weight='semibold', x=0.52)
            if self._grid[0] == 1:
                fig.subplots_adjust(top=0.8)
            else:
                fig.subplots_adjust(top=0.88)

        return fig

    def display(self, **kwargs):
        Scatter.plot(self, **kwargs)
        plt.show()

    @classmethod
    def display_all(cls):
        for instance in cls.__instances:
            Scatter.plot(instance)
        plt.show()

    @classmethod
    def set_default_colors(cls, new_colors: dict[str, str] = None, *, originals=False) -> dict[str, str]:
        """Assign custom default species-color map for visualisation. Return new default color map.

        Args:
            new_colors (dict of str:str, optional): species:color dictionary where valid species names are:
                'Hominidae', 'Hylobatidae', 'Cercopithecidae' or 'Platyrrhini' and valid colors are matplotlib
                named colors or hex color codes. Set `new_colors` to ORIGINAL_COLORS (after setting new_defauls)
                to revert color map to original default values. 
                
        Returns:
            new_def_colors (dict of str: str): ORIGINAL_COLORS dict merged with values from new_colors. 

        matplotlib named colors: https://matplotlib.org/stable/gallery/color/named_colors.html
        """
        if originals:
            cls.new_def_colors = Scatter.ORIGINAL_COLORS
        elif new_colors:
            cls.new_def_colors.update(new_colors)
        
        return cls.new_def_colors

    @classmethod
    def current_def_colors(cls):
        print(cls.new_def_colors)

    def save(self):
        Scatter.save_plots(self)

    @classmethod
    def save_plots(cls, *args, every=False) -> None:
        """Saves simple/log plots to respective folders.

        Each figure's save file is named as such:
        '(number of plots in figure) Simple Plot(s) - #(number denoting order in which file was saved).

        SIMPLE_PLOT_DETAILS.txt or LOG_PLOT_DETAILS.txt files also created containing number of plots, save file order, 
        value of `xy`, and time at figure creation. 

        Args:
            *args (plot_variables() object): any number of plot_variables() calls assigned to variables.
        """
        if every:
            figures = [figure for figure in cls.__instances]
        else:
            if not args:
                raise ValueError('save_plots() expected at least 1 figure object argument (0 given)')
            if not all(isinstance(figure, (Scatter, Regression)) for figure in args):
                raise TypeError(
                    f'save_plots expected an instance of Scatter() or Regression().'
                    f'If not saving every plot, ensure that all args are an instance of Scatter() or Regression().'
                    )
            figures = args

        for figure in figures:
            fig = figure.plot()
            
            log_or_simple = "Log" if figure.logged else "Simple"
            default_check = "Default" if figure.xy == Scatter.var_combinations([4, 3, 1]) else log_or_simple
            len_if_custom = str(len(figure.xy)) + " " if figure.xy != Scatter.var_combinations([4, 3, 1]) else ""
            is_len_plural = "s" if len(figure.xy) > 1 else ""
            
            save_folder = Path(Path.cwd(), f'Saved {log_or_simple} Plots')
            if not save_folder.is_dir():
                Path(save_folder).mkdir(parents=True)

            png_id = 1
            while Path(f'Saved {log_or_simple} Plots/{len_if_custom}{default_check} Plot{is_len_plural} - #{png_id:d}.png').exists():
                png_id += 1
            fig.savefig(f'Saved {log_or_simple} Plots/{len_if_custom}{default_check} Plot{is_len_plural} - #{png_id:d}.png')

            var_list = "\n".join(str(x) for x in figure.xy)
            with open(f'Saved {log_or_simple} Plots/{log_or_simple.upper()}_PLOT_DETAILS.txt', 'a') as save_details:
                save_details.write(
                    f'{len_if_custom}{default_check} Plot{is_len_plural} - #{png_id:d} '
                    f'-\n{var_list}\n'
                    f'- Figure Created on {datetime.now().strftime("%d-%m-%Y at %H:%M:%S")}\n'
                    f'------------------------------------------------------\n'
                    )
                
                print(
                    f'- {default_check + " " + log_or_simple if figure.xy == Scatter.var_combinations([4, 3, 1]) else default_check}'
                    f' Plot{is_len_plural} saved to {save_folder}\n'
                    )

    @staticmethod    
    def delete_folder(logged=False) -> None:
        """Deletes simple or log save folder depending on if logged=True is passed as an argument.

        Args:
            logged (bool): determines deletion of simple plot (False), or log plot save folders (True).
        """
        folder = Path(Path.cwd(), f'Saved {"Log" if logged else "Simple"} Plots')

        try:
            shutil.rmtree(folder)
        except FileNotFoundError:
            print(
                f"No '{folder.name}' folder exists in the current directory, "
                f"and so could not be deleted."
                )
