#!/usr/bin/env python3
"""
Classes for creating simple Scatter or Regression plots from cerebellum morphology data.
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
    """Class for creating fully-constructed scatter plots with matplotlib.pyplot as a basis, intended for use with the
    Cerebellum Project. Facilitates creation of mutliple plots at once, with autonomous axes label and legend creation.
    Also facilitates plotting of pairwise variable combinations. Includes methods for saving individual or
    multitudinal plots to their respective 'Logged' or 'Simple' save folders, containing save-details text files.

    Attributes:
        ORIGINAL_COLORS: default species:color map {'Hominidae': '#7f48b5', 'Hylobatidae': '#c195ed',
            'Cercopithecidae': '#f0bb3e', 'Platyrrhini': '#f2e3bd'}.
        new_def_colors: user-updated default species:color map. Defaults to copy of ORIGINAL_COLORS.
        def_pairs: Default list of column indices from which to make pairwise combinations with Scatter.xy_pairs.
            Used when no arguments are passed to property `xy`, or variables cannot be plotted/combined with those
            arguments.
        __instances: list of class instances, for use when displaying or saving all instances.
    """

    ORIGINAL_COLORS = {
                'Hominidae': '#7f48b5',
                'Hylobatidae': '#c195ed',
                'Cercopithecidae': '#f0bb3e',
                'Platyrrhini': '#f2e3bd'
                } 
    new_def_colors = ORIGINAL_COLORS.copy()
    def_pairs = (4, 3, 1)
    __instances = []
    
    def __init__(
        self, xy=None, colors=None, logged=False, *, figsize=None, grid=None, edgecolor='k', marker='o', 
        title=None, legend_loc='upper left'
        ):
        """Construct object to be plotted with matplotlib.pyplot.

        Args:
            xy (tuple, optional): tuple of integers representing column index values from .csv, to be passed to
                `Scatter.xy_pairs()`, or tuple of tuples with each containing independent/dependent variable names to be
                plainly plotted. Ensure a minimum of two integers or column names are defined.
            colors (dict of str: str, optional): species:color dictionary where valid species names are:
                'Hominidae', 'Hylobatidae', 'Cercopithecidae' or 'Platyrrhini' and valid colors are matplotlib
                named colors or hex color codes. Maps the respective colors to each species' plot markers. Defaults to
                Scatter.DEFAULT_COLORS.
            logged (bool, optional): produce unlogged (False) or logged plots (True). Defaults to False.
            figsize (tuple of float, float, optional): width, height of figure in inches. Defaults to Scatter.figsize.
            grid (tuple of int, optional): Number of rows/columns of the subplot grid. Defaults to Scatter.grid.
            edgecolor (str, optional): The border color of each data-point. Defaults to 'k'.
            marker (str, optional): The marker style of each data-point. Defaults to 'o'.
            title (str, optional): Main title of the figure. Defaults to None.
            legend_loc (str, optional): Location of the legend on each plot. Defaults to 'upper left'.
        """
        self.xy = xy
        self.colors = colors
        self.logged = logged
        self.figsize = figsize
        self.grid = grid
        self.edgecolor = edgecolor
        self.marker = marker
        self.title = title
        self.legend_loc = legend_loc

        Scatter.__instances.append(self)
    
    @property
    def xy(self) -> tuple[tuple[str, str], ...]:
        """Gets or sets current xy pairs. Defaults to pairwise combinations of Scatter.def_pairs, otherwise,
        plots column-name string pairs or combinations of custom pairs.

        Args:
            cols_or_pairs (tuple): tuple of integers representing column index values from .csv, to be passed to
            `Scatter.xy_pairs()`, or tuple of tuples with each containing independent/dependent variable names to be
            plainly plotted. Ensure a minimum of two integers or column names are defined.

        Returns:
            self._xy (tuple): tuple of tuples with each containing independent/dependent variable pairs.
        """
        return self._xy

    @xy.setter
    def xy(self, cols_or_pairs):
        if cols_or_pairs is None:
            xy = Scatter.xy_pairs(Scatter.def_pairs)
        elif all(isinstance(col_index, (int)) for col_index in cols_or_pairs):
            xy = Scatter.xy_pairs(cols_or_pairs)
        else:
            xy = cols_or_pairs
        self._xy = xy

    @property
    def colors(self) -> dict[str, str]:
        """Gets or sets (updates) current plot color map. Defaults to scatter.new_def_colors.

        Args:
            new_colors (dict of str:str): species:color dictionary where valid
                species names are: 'Hominidae', 'Hylobatidae', 'Cercopithecidae' or 'Platyrrhini' and valid colors are
                matplotlib named colors or hex color codes. Maps the respective colors to each species' plot markers.

        Returns:
            self._colors (dict of str:str): default or updated species:color map.
        """
        return self._colors
    
    @colors.setter
    def colors(self, new_colors):
        if new_colors is None:
            colors = Scatter.new_def_colors
        else:
            def_copy = Scatter.new_def_colors.copy()
            def_copy.update(new_colors)
            colors = def_copy
        self._colors = colors

    @property
    def figsize(self) -> tuple[float, float]:
        """Gets or sets width, height of subplot figure in inches. Default figsize depends on number of xy pairs.
        
        Args:
            width_height (tuple of float, float): width, height of subplot figure in inches.
        
        Raises:
            ValueError: if height or width values are less than or equal to 0.
        """
        return self._figsize
    
    @figsize.setter
    def figsize(self, width_height):
        if width_height is None:
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

            figsize = fig_width, fig_height
        else:
            if any(size <= 0 for size in width_height):
                raise ValueError('Attribute `figsize` must contain only positive integers.')
            figsize = width_height

        self._figsize = figsize
        
    @property
    def grid(self) -> tuple[int, int]:
        """Gets or sets number of rows and columns of subplot figure. By default, automatically scales with the
        number of xy pairs (1 row for 3 plots or less, 2 rows for more than 3 plots, with columns according to the
        number of plots).

        Args:
            rows_cols (tuple of int, int): rows, cols of axes drawn on matplotlib.figure.Figure object.

        Raises:
            ValueError: if rows and columns are unable to fit the minimum number of plots determined by property `xy`.
        """
        return self._grid
    
    @grid.setter
    def grid(self, rows_cols):
        if rows_cols is None:
            if len(self.xy) <= 3:
                num_rows = 1   
                num_cols = len(self.xy)
            else:
                num_rows = 2
                num_cols = int(len(self.xy) // 1.66)

            rows_cols = num_rows, num_cols

        rows_cols = int(float(rows_cols[0])), int(float(rows_cols[1]))
        n_axes = rows_cols[0] * rows_cols[1]

        if n_axes < len(self.xy):
            raise ValueError(
                f'All plots must be able to fit within the grid. The specified grid dimensions allow for {n_axes}'
                f' plots; axes for {len(self.xy)} plot(s) required. Grid dimensions should be positive integers.'
                )

        self._grid = rows_cols

    @staticmethod
    def xy_pairs(cols: list[int]) -> tuple[tuple[str, str], ...]:
        """Get all pairwise combinations (not repeated) for a list of columns. Return nested tuples containing
        these combinations.

        Args:
            cols (list of int): list of integers representing column index values from .csv. 

        Returns:
            xy_pairs: tuple of tuples, each containing independent/dependent variable pairs.
        
        Raises:
            ValueError: if the number of valid cols in `cols` is lower than 2 (the required minimum for making
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
                        f'The following invalid indices were passed to attribute `xy`: {list(set(invalid_cols))}.'
                        f' Combinations were therefore made from the following indices only: {list(set(valid_cols))}.'
                        )
   
                if len(set(valid_cols)) != len(valid_cols):
                    dupes = list(set([x for x in valid_cols if valid_cols.count(x) > 1]))
                    warnings.warn(
                        f'Duplicates of the following valid column indices were ignored to avoid plotting them'
                        f' against one another: {dupes}.\n'
                        )
                
                xy_pairs = tuple(combinations(data.columns[list(dict.fromkeys(valid_cols))], 2))
            else:
                raise ValueError

        except ValueError:
            print(
                f'\nNo valid combinations could be made from the list passed to attribute `xy`. '
                f'{"The only valid index was: " + ("".join(str(c) for c in valid_cols)) + "." if valid_cols else ""}'
                f' The default combination {Scatter.def_pairs} was therefore plotted.\n\n'
                f' Please ensure the list has at least 2 valid indices, where such indices refer to columns'
                f' containing floating-point numbers or integers.\n'
                )
            xy_pairs = tuple(combinations(data.columns[Scatter.def_pairs], 2))

        return xy_pairs
        
    def plot(self, **kwargs):
        """Plots variables on figure axes with color map, legend, handles matching data-point colors,
        and custom labelling depending on instance variable `logged`.

        Args:
            **kwargs: additional matplotlib.axes.Axes.scatter properties.

        Returns:
            fig (matplotlib.figure.Figure object): figure object for saving with matplotlib.pyplot.savefig()) 
                each instance passed to save_plots() (and by extension, save()).
        """
        fig, axs = plt.subplots(self.grid[0], self.grid[1], figsize=self.figsize, squeeze=False)
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
            if self.grid[0] == 1:
                fig.subplots_adjust(top=0.8)
            else:
                fig.subplots_adjust(top=0.88)

        return fig

    def display(self, **kwargs) -> None:
        """Plot and output cbpmodels.Scatter instance to it's own window.

        Args:
            **kwargs: matplotlib.axes.Axes.scatter properties.
        """
        Scatter.plot(self, **kwargs)
        plt.show()

    @classmethod
    def display_all(cls) -> None:
        """Plot and output instances of cbpmodels.Scatter to their own windows."""
        for instance in cls.__instances:
            Scatter.plot(instance)
        plt.show()

    @classmethod
    def set_def_pairs(cls, new_pairs: tuple[int] = None, originals=False) -> tuple[int]:
        """Update default tuple to be passed to Scatter.xy_pairs for plotting without specifying property `xy`.

        Args:
            new_pairs (tuple[int], optional): tuple of integers representing column index values from .csv.
                Defaults to None.
            originals (bool, optional): if True, sets Scatter.def_pairs to it's predetermined values. Defaults to False.
        """
        if originals is True:
            cls.def_pairs = (4, 3, 1)
        else:
            cls.def_pairs = new_pairs

    @classmethod
    def get_def_pairs(cls) -> None:
        """Prints current default tuple to be passed to Scatter.xy_pairs() for plotting without specifying
        property `xy`.
        """
        print(
            f'Current default variable combinations are {cls.def_pairs}, equivalent to'
            f' {Scatter.xy_pairs(cls.def_pairs)} '
            )

    @classmethod
    def set_def_colors(cls, new_colors: dict[str, str] = None, *, originals=False) -> dict[str, str]:
        """Assign custom default species-color map for visualisation. Return new default color map.

        Args:
            new_colors (dict of str:str, optional): species:color dictionary where valid species names are:
                'Hominidae', 'Hylobatidae', 'Cercopithecidae' or 'Platyrrhini' and valid colors are matplotlib
                named colors or hex color codes. Assign `new_colors` to ORIGINAL_COLORS (after setting new_defauls)
                to revert color map to original default values. 
                
        Returns:
            new_colors (dict of str: str): ORIGINAL_COLORS dict merged with values from new_colors. 
            originals (bool, optional): if True, sets Scatter.new_def_colors to it's predetermined values.
                Defaults to False.


        matplotlib named colors: https://matplotlib.org/stable/gallery/color/named_colors.html
        """
        if originals:
            cls.new_def_colors = cls.ORIGINAL_COLORS
        elif new_colors:
            cls.new_def_colors.update(new_colors)

    @classmethod
    def current_def_colors(cls) -> None:
        """Prints current Scatter.new_def_colors dict to act as the default color map for all plots when property
        `colors` is not manually assigned.
        """
        print(cls.new_def_colors)

    def save(self) -> None:
        """Save instance of cbpmodels.Scatter instance using Scatter.save_plots()."""
        Scatter.save_plots(self)

    @classmethod
    def save_plots(cls, *args, every=False) -> None:
        """Saves simple/log plots to respective folders.

        Each figure's save file is named as such:
        '(number of plots in figure) Simple Plot(s) - #(number denoting order in which file was saved).

        SIMPLE_PLOT_DETAILS.txt or LOG_PLOT_DETAILS.txt files also created containing number of plots, save file order, 
        value of attribute `xy`, and time at figure creation. 

        Args:
            *args (cbpmodels.Scatter instance): any number of cbpmodels.Scatter instances.
            every (bool, optional): if True, save every object of cbpmodels.Scatter.
        """
        if every:
            figures = [figure for figure in cls.__instances]
        else:
            if not args:
                raise TypeError('save_plots() expected at least 1 figure object argument (0 given)')
            if not all(isinstance(figure, (Scatter, Regression)) for figure in args):
                raise TypeError(
                    f'save_plots expected only instances of Scatter() or Regression().'
                    f'If not saving every plot, ensure that all args are an instance of Scatter() or Regression().'
                    )
            figures = args

        for figure in figures:
            fig = figure.plot()
            
            log_or_not = "Log" if figure.logged else "Simple"
            is_custom = "Default" if figure.xy == Scatter.xy_pairs(Scatter.def_pairs) else log_or_not
            len_custom = str(len(figure.xy)) + " " if figure.xy != Scatter.xy_pairs(Scatter.def_pairs) else ""
            is_plural = "s" if len(figure.xy) > 1 else ""
            
            save_folder = Path(Path.cwd(), f'Saved {log_or_not} Plots')
            if not save_folder.is_dir():
                Path(save_folder).mkdir(parents=True)

            png_id = 1
            while Path(f'Saved {log_or_not} Plots/{len_custom}{is_custom} Plot{is_plural} - #{png_id:d}.png').exists():
                png_id += 1
            fig.savefig(f'Saved {log_or_not} Plots/{len_custom}{is_custom} Plot{is_plural} - #{png_id:d}.png')

            var_list = "\n".join(str(x) for x in figure.xy)
            with open(f'Saved {log_or_not} Plots/{log_or_not.upper()}_PLOT_DETAILS.txt', 'a') as save_details:
                save_details.write(
                    f'{len_custom}{is_custom} Plot{is_plural} - #{png_id:d} '
                    f'-\n{var_list}\n'
                    f'- Figure Created on {datetime.now().strftime("%d-%m-%Y at %H:%M:%S")}\n'
                    f'------------------------------------------------------\n'
                    )
                
                print(
                    f'{is_custom + " " + log_or_not if figure.xy == Scatter.xy_pairs(Scatter.def_pairs) else is_custom}'
                    f' Plot{is_plural} saved to {save_folder}\n'
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
