
import sys
import itertools
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as tk
from matplotlib.lines import Line2D

"""Simple and logged scatter plots for cerebellum and cerebrum morphology in primates.
Saves simple and logged plots to separate files. Will by default open windows with each figure,
comment out 'plt.show()' at end of file to save only."""

try:
    data = pd.read_csv('all_species_values.csv', na_values='')
    data = data.dropna(how='all', axis='columns').drop(columns='Source')
    data.rename(columns={
        'Species ': 'Species',
        'CerebellumSurfaceArea': 'Cerebellum Surface Area',
        'CerebrumSurfaceArea': 'Cerebrum Surface Area',
        'CerebellumVolume ': 'Cerebellum Volume',
        'CerebrumVolume': 'Cerebrum Volume'
        }, inplace=True)

except FileNotFoundError:
    print('Please ensure you have the \'all_species_values.csv\' '
          'in the same directory as this program.')
    sys.exit()

vol_cerebrum = tuple(data['Cerebellum Volume'].astype(float))
vol_bellum = tuple(data['Cerebrum Volume'].astype(float))
surf_bel = tuple(data['Cerebellum Surface Area'].astype(float))

taxon = data['Taxon']
colors = {
    'Hominidae':  '#7f48b5',
    'Hylobatidae': '#c195ed',
    'Cercopithecidae': '#f0bb3e',
    'Platyrrhini': '#f2e3bd'
    }

col_names = [list(data.columns)[4], list(data.columns)[3], list(data.columns)[1]]
col_combinations_test = list(itertools.combinations(col_names, 2))

# Gives legend markers same color as predefined taxon colors
handles = [
    Line2D([0], [0],
           color='w', marker='o', markerfacecolor=v,
           markeredgecolor='k',  markeredgewidth='0.5',
           markersize=4, label=k,
           ) for k, v in colors.items()
        ]


def create_plot(col_combinations, logged=False):
    plt.rcParams['xtick.minor.size'] = 0
    plt.rcParams['xtick.minor.width'] = 0
    plt.rcParams['ytick.minor.size'] = 0
    plt.rcParams['ytick.minor.width'] = 0

    if not logged:
        fig1, axs1 = plt.subplots(1, (len(col_combinations)), figsize=(16, 5))

        for i, (x, y) in enumerate(col_combinations):
            axs1[i].scatter(data[x], data[y], c=taxon.map(colors), edgecolor='k')

            axs1[i].set(
                title=f'Primate {col_combinations[i][0]} against\n{col_combinations[i][1]}',
                xlabel=f'{col_combinations[i][0]}',
                ylabel=f'{col_combinations[i][1]}'
            )

            ax_legend = axs1[i].legend(
                title='Taxon',
                title_fontsize='9',
                handles=handles,
                loc='upper left',
                fontsize=10
            )
            ax_legend.get_frame().set_color('white')

            fig1.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
            fig1.savefig('Simple Cerebellum Project Plots.png', bbox_inches='tight')

    elif logged:
        fig2, axs2 = plt.subplots(1, len(col_combinations), figsize=(16, 5))

        for i, (x, y) in enumerate(col_combinations):
            axs2[i].scatter(data[x], data[y], c=taxon.map(colors), edgecolor='k')

            axs2[i].set(
                title=f'Logged Primate {col_combinations[i][0]} against\n{col_combinations[i][1]}',
                xlabel=f'Logged {col_combinations[i][0]}',
                ylabel=f'Logged {col_combinations[i][1]}'
            )

            axs2[i].set_xscale('log')
            axs2[i].get_xaxis().set_major_formatter(tk.ScalarFormatter())
            axs2[i].set_xticks([1, 5, 10, 25, 50, 100, 200, 400])

            axs2[i].set_yscale('log')
            axs2[i].get_yaxis().set_major_formatter(tk.ScalarFormatter())
            axs2[i].set_yticks([10, 25, 50, 100, 250, 500, 1000])

            fig2.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
            fig2.savefig('Logged Cerebellum Project Plots.png', bbox_inches='tight')


create_plot(col_combinations_test, logged=True)
create_plot(col_combinations_test, logged=False)

plt.show()
