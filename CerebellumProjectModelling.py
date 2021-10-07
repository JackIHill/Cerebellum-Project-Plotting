
from matplotlib import pyplot as plt
from matplotlib import ticker as tk
from matplotlib.lines import Line2D
import pandas as pd

"""Simple and logged scatter plots for cerebellum and cerebrum morphology in primates.
Saves simple and logged plots to separate files. Will by default open windows with each figure,
comment out 'plt.show()' at end of file to save only."""

# TODO:
#  make try/except block to check if csv file present

data = pd.read_csv('Cerebellum Project All Species Values.csv', na_values='')
data = data.dropna(how='all', axis='columns').drop(columns='Source')

vol_cerebrum = list(data['CerebellumVolume '].astype(float))
vol_bellum = list(data['CerebrumVolume'].astype(float))
surf_bel = list(data['CerebellumSurfaceArea'].astype(float))
taxon = data['Taxon']
colors = {
    'Hominidae':  '#444470',
    'Hylobatidae': '#5f5c70',
    'Cercopithecidae': '#95919c',
    'Platyrrhini': '#c6c2cc'
    }

# change figsize=(x, y) to suit your monitor/needs.
fig1, (ax, ax1, ax2) = plt.subplots(nrows=1, ncols=3, figsize=(15, 4))
fig2, (ax_logged, ax1_logged, ax2_logged) = plt.subplots(nrows=1, ncols=3, figsize=(15, 4))

# start of normal plotting
ax.scatter(vol_cerebrum, vol_bellum, c=taxon.map(colors), edgecolor='k')

ax.set_title('Primate Cerebellum Volume against\nCerebrum Volume', fontsize=11)
ax.set_xlabel('Cerebellum Volume')
ax.set_ylabel('Cerebrum Volume')

# gives legend markers same color as predefined taxon colors
handles = [Line2D(
    [0], [0],
    marker='o', color='w', markerfacecolor=v,
    label=k, markersize=4, markeredgecolor='k',
    markeredgewidth='0.5'
) for k, v in colors.items()]

ax_legend = ax.legend(
    title='Taxon',
    title_fontsize='9',
    handles=handles,
    loc='upper left',
    fontsize=10
)
ax_legend.get_frame().set_color('white')

ax1.scatter(vol_bellum, surf_bel, c=taxon.map(colors), edgecolor='k')

ax1.set_title('Primate Cerebellum Volume against\nCerebellum Surface Area', fontsize=11)
ax1.set_xlabel('Cerebellum Volume')
ax1.set_ylabel('Cerebellum Surface Area')

ax1_legend = ax1.legend(
    title='Taxon',
    title_fontsize='9',
    handles=handles,
    loc='upper left',
    fontsize=10
)
ax1_legend.get_frame().set_color('w')

ax2.scatter(vol_cerebrum, surf_bel, c=taxon.map(colors), edgecolor='k')

ax2.set_title('Primate Cerebrum Volume against\nCerebellum Surface Area', fontsize=11)
ax2.set_xlabel('Cerebrum Volume')
ax2.set_ylabel('Cerebellum Surface Area')

ax2_legend = ax2.legend(
    title='Taxon',
    title_fontsize='9',
    handles=handles,
    loc='upper left',
    fontsize=10
)
ax2_legend.get_frame().set_color('w')

fig1.savefig('Cerebellum Project Simple Plots.png')

# start of logged plotting
ax_logged.scatter(vol_cerebrum, vol_bellum, c=taxon.map(colors), edgecolor='k')

ax_logged.set_xscale('log')
ax_logged.get_xaxis().set_major_formatter(tk.ScalarFormatter())
ax_logged.set_xticks([1, 5, 10, 20, 40, 80, 160])

ax_logged.set_yscale('log')
ax_logged.get_yaxis().set_major_formatter(tk.ScalarFormatter())
ax_logged.set_yticks([10, 25, 50, 100, 250, 500, 1000])

ax_logged.set_title('Logged Primate Cerebellum Volume against\nCerebrum Volume', fontsize=11)
ax_logged.set_xlabel('Logged Cerebellum Volume')
ax_logged.set_ylabel('Logged Cerebrum Volume')

ax_logged_legend = ax_logged.legend(
    title='Taxon',
    title_fontsize='9',
    handles=handles,
    loc='upper left',
    fontsize=10
)
ax_logged_legend.get_frame().set_color('w')

ax1_logged.scatter(vol_bellum, surf_bel, c=taxon.map(colors), edgecolor='k')

ax1_logged.set_xscale('log')
ax1_logged.get_xaxis().set_major_formatter(tk.ScalarFormatter())
ax1_logged.set_xticks([1, 5, 10, 20, 40, 80, 160, 400])

ax1_logged.set_yscale('log')
ax1_logged.get_yaxis().set_major_formatter(tk.ScalarFormatter())
ax1_logged.set_yticks([10, 25, 50, 100, 200, 400])

ax1_logged.set_title('Logged Primate Cerebellum Volume against\nCerebellum Surface Area', fontsize=11)
ax1_logged.set_xlabel('Logged Cerebellum Volume')
ax1_logged.set_ylabel('Logged Cerebellum Surface Area')

ax1_logged_legend = ax1_logged.legend(
    title='Taxon',
    title_fontsize='9',
    handles=handles,
    loc='upper left',
    fontsize=10
)
ax1_logged_legend.get_frame().set_color('w')

ax2_logged.scatter(vol_cerebrum, surf_bel, c=taxon.map(colors), edgecolor='k')

ax2_logged.set_xscale('log')
ax2_logged.get_xaxis().set_major_formatter(tk.ScalarFormatter())
ax2_logged.set_xticks([1, 5, 10, 20, 40, 60])

ax2_logged.set_yscale('log')
ax2_logged.get_yaxis().set_major_formatter(tk.ScalarFormatter())
ax2_logged.set_yticks([10, 25, 50, 100, 200, 400])

ax2_logged.set_title('Logged Primate Cerebrum Volume against\nCerebellum Surface Area', fontsize=11)
ax2_logged.set_xlabel('Logged Cerebrum Volume')
ax2_logged.set_ylabel('Logged Cerebellum Surface Area')

ax2_logged_legend = ax2_logged.legend(
    title='Taxon',
    title_fontsize='9',
    handles=handles,
    loc='upper left',
    fontsize=10
)
ax2_logged_legend.get_frame().set_color('w')

fig2.savefig('Cerebellum Project Logged Plots.png')

plt.tight_layout()
plt.show()
