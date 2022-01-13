# Cerebellum Project Data Visualisation
Create plots for cerebellar and cerebral morphology in a range of primates.
Run alongside csv file containing brain morphological data from a range of studies.
CSV will be updated in the future as the project progresses.

- [About the Cerebellum Project](#about-the-cerebellum-project)

## Usage
```import cbpmodels as cbp```
<br>
### <ins>Functions<ins>
<br>
```plot_variables()```: Plots brain morphology variables with a legend and data point colours mapped to taxa.
<br>
<br>
Calling ```plot_variables()``` without specifying a) a tuple of tuples containing indepdent and dependent variable pairs or b) a list of .csv column indices, will create a default figure containing plots derived from pairwise, non-repeated combinations of csv columns 4, 3 and 1 (ordered for aesthetic purposes) - those with sufficient data points. Thus:
<br>

```python
cbp.plot_variables(show=True)
```
Produces: 

![default_plot_variables](https://user-images.githubusercontent.com/73407206/148590626-292c2844-1c0c-40e0-817a-452dde6c739f.png)

<br>

Specifying n number of variable combination tuples will plot n number of plots on the figure. ```logged=True``` can also be passed, to log every plot in the figure. Thus:

```python
cbp.plot_variables(
    (('Cerebrum Volume', 'Cerebellum Volume'),),  
    logged=True, show=True
    )  
```

Produces:
<br>
<br>
![logged_cbvol_cbllum_vol](https://user-images.githubusercontent.com/73407206/148590809-855fe955-aaf0-42dd-8a32-b8e9736cbae8.png)

<br>
Specify a list of column indices to plot all non-repeated combinations of the variables those columns represent.

```python
cbp.plot_variables([1, 2, 3, 4], show=True)
```

will therefore produce 6 plots; variable combinations:
```(1, 2)```, ```(1, 3)```, ```(1, 4)```, ```(2, 3)```, ```(2, 4)```, ```(3, 4)``` where:

<br>

column index 1 = Cerebellum Surface Area <br>
column index 2 = Cerebrum Surface Area <br>
column index 3 = Cerebellum Volume <br>
column index 4 = Cerebrum Volume <br>

<br>

Manually change the color map for the current plot using the ```colors``` keyword. Pass a dictionary containing a taxon name key and a color value, where valid taxa are 'Hominidae', 'Hylobatidae', 'Cercopithecidae' and 'Platyrrhini' and valid colors are [matplotlib named colors](https://matplotlib.org/stable/gallery/color/named_colors.html) or hex color codes. Thus:

```python
cbp.plot_variables(colors={'Hominidae':'blue'}, show=True)
``` 

will modify the color map for the taxon Hominidae, leaving all other taxon color maps as their default, as such:

![default_plot_colored_diff](https://user-images.githubusercontent.com/73407206/148591146-3494d9ef-c56a-4fcd-90a9-a2fac7fb887f.png)

<br>

To set custom color maps for any or all taxon for all subsequent plots, pass a dictionary of 'taxon_name':'color' to ```set_colors()```:

```python
cbp.plot_variables(show=True) # plot all taxon with module-defined default color map

cbp.plot_variables(colors={'Hylobatidae':'blue'}, show=True) # change plot's Hylobatidae colors, other taxa have default colors

cbp.set_colors({'Hominidae':'red'}) # set default color for Hominidae plot points, for all subsequent plots. 
    
cbp.plot_variables(show=True) # default color for Hominidae is red, all other colors are original (Hylobatidae no longer blue). 

cbp.set_colors(DEFAULT_COLORS) # set default colors to module-defined default color map
```

<br>

```plot_variables()``` also takes arbitrary keyword arguments from [matplotlib.pyplot.scatter](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.scatter.html)

<br>

Passing ```save=True``` to ```plot_variables()``` will create a new directory inside the current directory, and store the current figure in 'Saved Simple Plots' or 'Saved Log Plots' depending on if ```logged``` is True. SIMPLE / LOG_PLOT_DETAILS.txt files will be created simultaneously, providing information for each figure on the number of plots, save file order, variables used for each plot, and the time at figure creation. 

<br>

You can save a 'batch' of figures using ```save_plots(fig1, fig2, ...)``` after assigning objects to calls of ```plot_variables()```, like so:

```
plot1 = cbp.plot_variables([['Cerebrum Volume', 'Cerebellum Volume'],])
plot2 = cbp.plot_variables([1, 2, 3, 4])

cbp.save_plots(plot1, plot2)
```


To easily delete these folders, ```delete_folders(logged=True)``` for the 'Saved Log Plots' directory, and ```delete_folders()``` for the 'Saved Simple Plots' directory.

<br>

```plot_regression()``` plots linear regression line for the volume-against-volume plot.

## About the Cerebellum Project

The cerebellum project studies cerebellar evolution at microscopic scale, across several primate species. It aims at creating precise delineations of the pial surface of the cerebellar cortex. With this, we measure the surface area and volume of each cerebellum and cerebrum in each primate brain. We will also attempt to use the annotations to generate 3D volumes and 3D meshes of the gorilla cerebellum (for now, with more species to come). Eventually we will use these surface data to guide segmentation into cerebellar sub-structures with more precise functions.

Primarily, for annotation, we use MicroDraw, available at: https://microdraw.pasteur.fr/ and https://github.com/r03ert0/microdraw

To learn how we annotate each structure, visit: https://docs.google.com/document/d/1gAQIiEM9bAYKqiLpG9vHDmuaBk-LYpSIdsVsISAPzq4/edit

![AnnotationTransparent](https://user-images.githubusercontent.com/73407206/136446208-e2651756-359a-46e8-96cd-c526958828bb.png)

See our prototype reconstruction of an eastern lowland gorilla cerebellum:

![Gorilla3DTransparent](https://user-images.githubusercontent.com/73407206/136446331-42e5afb3-2867-4329-952f-3b5593972e9c.gif)
