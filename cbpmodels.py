#!/usr/bin/env python3
"""
Classes for creating simple Scatter or Regression plots from cerebellum morphology data.
"""

import sys
import shutil
import logging
import warnings
from pathlib import Path
from itertools import combinations
from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as tk
from matplotlib.lines import Line2D

logger = logging.getLogger('cbpmodels.py')

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
    
    def __init__(self, xy=None, colors=None, logged=False, *, figsize=None, grid=None, edgecolor='k', marker='o', 
                title=None, legend_loc='upper left'):
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
        
        matplotlib named colors: https://matplotlib.org/stable/gallery/color/named_colors.html
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

        self.emph_arg = None       
        self.emph_kwargs = None
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
    def xy(self, cols_or_str):
        if cols_or_str is None:
            xy = Scatter.xy_pairs(Scatter.def_pairs)
        else:
            try:
                xy = [[var for var in tuples] for tuples in cols_or_str]
            except TypeError:
                xy = Scatter.xy_pairs(cols_or_str)

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

        matplotlib named colors: https://matplotlib.org/stable/gallery/color/named_colors.html
        """
        return self._colors
    
    @colors.setter
    def colors(self, new_colors):
        if new_colors is None:
            colors = Scatter.new_def_colors
        else:
            colors = Scatter.new_def_colors.copy()
            colors.update(new_colors)

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
                rows_cols = 1, len(self.xy)
            else:
                rows_cols = 2, int(len(self.xy) // 1.66)

        n_axes = rows_cols[0] * rows_cols[1]
        if n_axes < len(self.xy):
            raise ValueError(
                f'All plots must be able to fit within the grid. The specified grid dimensions allow for {n_axes}'
                f' plots; axes for {len(self.xy)} plot(s) required. Grid dimensions should be positive integers.'
                )

        self._grid = int(float(rows_cols[0])), int(float(rows_cols[1]))

    @staticmethod
    def xy_pairs(cols: list[int]) -> tuple[tuple[str, str], ...]:
        """Get all pairwise combinations (not repeated) for a list of columns. Return nested tuples containing
        these combinations.

        Args:
            cols (list of int): list of integers representing column index values from .csv. 

        Returns:
            xy_pairs: tuple of tuples, each containing independent/dependent variable pairs.
        
        Raises:
            ValueError: if list `cols` contains non-digit values.
            ValueError: if the number of valid cols in `cols` is lower than 2 (the required minimum for making
            pairwise combinations). 
        """
        try:
            cols = [int(str(col_idx)) for col_idx in cols]
        except ValueError:
            logger.debug(f'\nValueError: non-int was passed to cols: {cols}')
            raise ValueError('xy_pairs() does not accept float or alpha character values.\n') from None

        invalid_cols = []    
        for col_idx in cols:
            if col_idx >= len(data.columns) or (data[data.columns[col_idx]].dtype != ('float64' or 'int64')) :
                invalid_cols.append(col_idx)

        valid_cols = [col_idx for col_idx in cols if col_idx not in invalid_cols]

        try:
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

                # dict.fromkeys retains order of col indices.
                xy_pairs = tuple(combinations(data.columns[list(dict.fromkeys(valid_cols))], 2))
            else:
                raise ValueError

        except ValueError:
            print(
                f'\nNo valid combinations could be made from the list passed to attribute `xy`. '
                f'{"The only valid index was: " + ("".join(str(c) for c in valid_cols)) + "." if valid_cols else ""}'
                f' The default combination {Scatter.def_pairs} was therefore plotted.\n\n'
                f'Please ensure the list has at least 2 valid indices, where such indices refer to columns'
                f' containing floating-point numbers or integers.\n'
                )
            xy_pairs = tuple(combinations(data.columns[list(dict.fromkeys(Scatter.def_pairs))], 2))
        
        return xy_pairs

    def emphasize(self, species, **kwargs):
        self.emph_arg = species
        self.emph_kwargs = kwargs

    def emphasis_deco(func):
        """highlights the data points exclusive to `species_or_taxon`, by reducing the alpha value of all other 
        points to `alpha_value`, increasing marker size to `s`, and increasing line width to `linewidth`.

        Args:
            species_or_taxon (str): taxon name (e.g. 'Hominidae') or species name (e.g. 'Homo_sapiens')
                from all_species_values.csv to be emphasized.
            with_highlight (bool, optional): enable or disable emphasize behaviour. Defaults to True.
            color (str, optional): the facecolor of emphasised points, where valid colors are matplotlib named colors
                or hex color codes. Defaults to self.color value for respective taxon.
            edgecolor (str, optional): the border color of emphasised point, where valid colors are matplotlib
                named colors or hex color codes. Defaults to self.edgecolor.
            alpha (float, optional): the alpha blending value, between 0 (transparent) and 1 (opaque). If None,
                no transparency. Defaults to 0.2.
            s (float, optional): the marker size in points**2. Defaults to None.
            linewidth (float, optional): marker-edge width. Defaults to 1.5.
            with_arrows (bool, optional): draws arrow towards all `species_or_taxon` points. Defaults to False.
            legend (bool, optional): creates additional legend referring to `species_or_taxon`. Defaults to True.

        matplotlib named colors: https://matplotlib.org/stable/gallery/color/named_colors.html
        """
        def wrap(self, species_or_taxon, with_highlight=True, color=None, edgecolor=None,
            alpha=0.2, s=None, linewidth=1.5, with_arrows=False, legend=True):

            # get the higher class (Species or Taxon) for the lower class passed to `species_or_taxon`.
            # e.g. higher_class = 'Species' when `species_or_taxon` == 'Homo_sapiens'.
            locate_higher_class = data.apply(lambda row: row[row == species_or_taxon], axis=1)
            class_name = ''.join(item[0] for item in locate_higher_class.iteritems())

            species_filt = data[class_name] == species_or_taxon

            if color is None:
                color = ''.join(data[species_filt].Taxon.map(self.colors).unique())
            
            if edgecolor is None:
                edgecolor = self.edgecolor

            # ensure emphasised-Taxon plots update main legend created in plots(). 
            if class_name == 'Taxon':
                color_map = self.colors.copy()
                color_map.update({species_or_taxon: color})     
            else:
                color_map = None

            fig, axs = func(
                self, color_map=color_map,
                emph_taxon=species_or_taxon, 
                emph_edgecol=edgecolor, emph_edgewidth=linewidth,
                alpha=alpha
                )

            for ax_n, (x, y) in enumerate(self.xy):
                if with_highlight:
                    species_x = data.loc[species_filt, x],
                    species_y = data.loc[species_filt, y]

                    axs[ax_n].scatter(
                        species_x, species_y,
                        facecolors=color, edgecolors=edgecolor, marker=self.marker,
                        s=s, linewidth=linewidth, alpha=0.85)

                    # handles for emphasized species legend.
                    handles = [
                        Line2D([0], [0],
                        color='w', marker=self.marker, markerfacecolor=color,
                        markeredgecolor=edgecolor, markersize=4,
                        label=species_or_taxon.replace('_', ' ')
                        )]

                    if legend and class_name != 'Taxon':
                        ax_legend = axs[ax_n].legend(loc=(0.02, 0.55), handles=handles, handletextpad=0.1)
                        ax_legend.get_frame().set_color('white')

                if with_arrows:
                    xmin, xmax = axs[ax_n].get_xlim()
                    ymin, ymax = axs[ax_n].get_ylim()

                    x_range, y_range = (xmax - xmin),  (ymax - ymin)

                    # get data-points which correspond to `species_or_taxon` value.
                    for x, y in zip(data.loc[species_filt, x], data.loc[species_filt, y]):
                        # determine scaling behaviour of arrow-tail co-ordinates for logged or unlogged plots.
                        if self.logged:
                            modifier = 10, - (y_range * 0.02)
                            textcoords = 'offset points'
                        else:
                            modifier = (x + (x_range * 0.2)), (y - (y_range * 0.1))
                            textcoords = None

                        axs[ax_n].annotate(          
                            "", xy=(x, y), xytext=(modifier),
                            arrowprops=dict(arrowstyle="->", shrinkB=5), textcoords=textcoords)

            return fig
        wrap.unemphasized = func
        return wrap

    @emphasis_deco
    def plot(self, color_map=None, emph_taxon=None, emph_edgecol=None, emph_edgewidth=0.5, **kwargs):
        """Plots variables on figure axes with color map, legend, handles matching data-point colors,
        and custom labelling depending on instance variable `logged`.

        Args:
            **kwargs: additional matplotlib.axes.Axes.scatter properties.

        Returns:
            fig (class): matplotlib.figure.Figure object for saving with matplotlib.pyplot.savefig() 
                (each instance passed to save_plots() (and by extension, save()).
            axs (class): array of matplotlib.axes.Axes objects.
        """
        fig, axs = plt.subplots(self.grid[0], self.grid[1], figsize=self.figsize, squeeze=False)
        axs = axs.flatten()
        
        if color_map is None:
            color_map = self.colors

        for ax_n, (x, y) in enumerate(self.xy):
            axs[ax_n].scatter(
                data[x], data[y],
                c=data.Taxon.map(color_map),
                edgecolor=self.edgecolor, marker=self.marker, **kwargs
                )

            handles = [
                Line2D([0], [0],
                color='w', marker=self.marker, markerfacecolor=color,
                markeredgecolor=emph_edgecol if taxon == emph_taxon else self.edgecolor,
                markeredgewidth=emph_edgewidth if taxon == emph_taxon else 0.5,
                markersize=4, label=taxon
                ) for taxon, color in color_map.items()
                ]

            ax_legend = axs[ax_n].legend(
                title='Taxon',
                loc=self.legend_loc,
                handles=handles,
                handletextpad=0.1,
                )
            ax_legend = axs[ax_n].add_artist(ax_legend)
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

        return fig, axs

    def display(self, **kwargs) -> None:
        """Plot and output cbpmodels.Scatter instance to it's own window.

        Args:
            **kwargs: matplotlib.axes.Axes.scatter properties.
        """
        species = self.emph_arg
        emph_kwargs = self.emph_kwargs

        if self.emph_arg:
            Scatter.plot(self, species, **emph_kwargs, **kwargs)
        else:
            Scatter.plot.unemphasized(self, **kwargs)
        plt.show()

    @classmethod
    def display_all(cls) -> None:
        """Plot and simultaneously output all instances of cbpmodels.Scatter to their own windows."""
        for instance in cls.__instances:
            Scatter.display(instance)

    @classmethod
    def set_def_pairs(cls, new_pairs: tuple[int] = None, originals=False) -> tuple[int]:
        """Update default tuple to be passed to Scatter.xy_pairs for plotting without specifying property `xy`.

        Args:
            new_pairs (tuple[int], optional): tuple of integers representing column index values from .csv.
                Defaults to None.
            originals (bool, optional): if True, sets Scatter.def_pairs to it's predetermined values. Defaults to False.
        
        Raises:
            TypeError: if `new_pairs` contains non-int values.
        """
        if originals is True:
            cls.def_pairs = (4, 3, 1)
        else:
            if all(isinstance(col_idx, int) for col_idx in new_pairs):
                cls.def_pairs = tuple(new_pairs)
            else:
                raise TypeError(
                    'Scatter.set_def_pairs() received invalid input. Only integers are valid, and so new default pairs'
                    ' were not set.'
                    )
            
        logger.info(f'\nset_def_pairs() called: new default column indices are {cls.def_pairs}.')

    @classmethod
    def get_def_pairs(cls) -> None:
        """Returns current default tuple to be passed to Scatter.xy_pairs() for plotting without specifying
        property `xy`.
        """
        return(
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

        logger.info(f'\ndefault color map updated to:\n{cls.new_def_colors}\n')

    @classmethod
    def current_def_colors(cls) -> None:
        """Returns current Scatter.new_def_colors dict to act as the default color map for all plots when property
        `colors` is not manually assigned.
        """
        return(cls.new_def_colors)

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
            every (bool, optional): if True, save every object of cbpmodels.Scatter. Defaults to False.
        
        Raises:
            TypeError: if no objects are specified when `every` is False, or when objects passed to save_plots() are not
                an instance of Scatter or Regression.
        """
        if every:
            figures = [figure for figure in cls.__instances]
        else:
            if len(args) == 0:
                raise TypeError('save_plots() expected at least 1 figure object argument (0 given)')
            if not all(isinstance(figure, (Scatter, Regression)) for figure in args):
                raise TypeError(
                    f'save_plots expected only instances of Scatter() or Regression().'
                    f'If not saving every plot, ensure that all args are an instance of Scatter() or Regression().'
                    )
            figures = args

        for figure in figures:
            if figure.emphasized:
                fig = figure.plot(figure.emph_arg, **figure.emph_kwargs)
            else:
                fig = Scatter.plot.unemphasized(figure)[0]
                
            log_or_not = "Log" if figure.logged else "Simple"
            is_custom = "Default" if figure.xy == Scatter.xy_pairs(Scatter.def_pairs) else log_or_not
            len_custom = str(len(figure.xy)) + " " if figure.xy != Scatter.xy_pairs(Scatter.def_pairs) else ""
            is_plural = "s" if len(figure.xy) > 1 else ""
            emph_detail = figure.emph_arg.replace('_', ' ') + " emphasized -" if figure.emph_arg else ""

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
                    f'{len_custom}{is_custom} Plot{is_plural} - #{png_id:d} - {emph_detail}'
                    f'\n{var_list}\n'
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
            print(f"No '{folder.name}' folder exists in the current directory, and so could not be deleted.")

class Regression(Scatter):
    pass
#     def plot_regression():
#             """Plots linear regression line for the volume-against-volume plot."""
#             plot_variables((('Cerebrum Volume', 'Cerebellum Volume'),))
#             data_2 = data[['Cerebellum Volume', 'Cerebrum Volume']].copy(deep=False)

#             data_2.dropna(inplace=True)

#             predict = 'Cerebellum Volume'
#             x = np.array(data_2.drop([predict], axis=1))
#             y = np.array(data_2[predict])

#             model = np.polyfit(x[:, 0], y, 1)
#             predict = np.poly1d(model)

#             x_lin_reg = range(0, 1600)
#             y_lin_reg = predict(x_lin_reg)
#             plt.plot(x_lin_reg, y_lin_reg, c='k')
