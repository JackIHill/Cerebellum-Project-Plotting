# CerebellumProject
Create plots for cerebellar and cerebral morphology in a range of primates.
Run alongside csv file containing brain morphology.

- Calling the plot_variables() function without passing any arguments will by default:
    - Produce 3 plots (all combinations for the relevant data). 
    - These 3 plots will not be logged. 

- If you wish to log each of the plots, pass logged=True into plot_variables().
- If you want to manually plot data (from the csv), pass in a tuple containing (a) tuple(s) with variable pairs, like so: 
    - plot_variables((
                      ('Cerebrum Volume', 'Cerebellum Volume'),),
                      logged=True
                      )
- Plots will automatically be saved to a png file. One for simple plots, and one for logged plots. 
    - For now, this file will be overwritten each time a function is called.
    - This will be amended in a future update to create new PNG files each time. 


The cerebellum project studies cerebellar evolution at microscopic scale, across several primate species. It aims at creating precise delineations of the pial surface of the cerebellar cortex. With this, we measure the surface area and volume of each cerebellum and cerebrum in each primate brain. We will also attempt to use the annotations to generate 3D volumes and 3D meshes of the gorilla cerebellum. Eventually we will use these surface data to guide segmentation into cerebellar sub-structures with more precise functions.

Primarily, for annotation, we use MicroDraw, available at: https://microdraw.pasteur.fr/

To learn how we annotate each structure, visit: https://docs.google.com/document/d/1gAQIiEM9bAYKqiLpG9vHDmuaBk-LYpSIdsVsISAPzq4/edit

![AnnotationTransparent](https://user-images.githubusercontent.com/73407206/136446208-e2651756-359a-46e8-96cd-c526958828bb.png)

See our prototype reconstruction of an eastern lowland gorilla cerebellum:

![Gorilla3DTransparent](https://user-images.githubusercontent.com/73407206/136446331-42e5afb3-2867-4329-952f-3b5593972e9c.gif)


