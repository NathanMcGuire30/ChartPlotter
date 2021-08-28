# ChartPlotter
Python library to render NOAA charts

## Install

Install GDAL:
https://mothergeo-py.readthedocs.io/en/latest/development/how-to/gdal-ubuntu-pkg.html

~~~
sudo add-apt-repository ppa:ubuntugis/ppa && sudo apt-get update
sudo apt update
sudo apt install gdal-bin
sudo apt install libgdal-dev
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
pip3 install GDAL
~~~


`sudo apt install python3-gdal` also seems to work

Also requires NavPY and shapley

## Charts:
I use the NOAA vector charts, because they are dropping support for all else. 
I downloaded the zip file from their website for the Woods Hole Passage chart and extracted its contents into a folder called
`ChartPlotter/Charts`.

## Description
Currently, test4.py is my development script.  It rasterizes the charts and saves each layer as a .tiff.

Reference layers from Woods Hole Passage
- 4: Bridges
- 5: Buildings
- 7: Buoys
- 12: Edges
- 13: Towers on rocks in woods hole
- 14: Depth areas
- 15: Depth contours
- 16: Channels
- 17: Channels v2
- 21: Land
- 23: Marsh
- 29: Shallow, near shore stuff
- 34: Water
- 36: Shallow stuff v2
- 39: Rocky edges?
- 41: Depth soundings
- 42: Rocks

0 DSID  
1 ACHARE  
2 BCNLAT  
3 BCNSPP  
4 BRIDGE  
5 BUISGL  
6 BUAARE  
7 BOYLAT  
8 BOYSPP  
9 CBLARE  
10 CTNARE  
11 CGUSTA  
12 COALNE  
13 DAYMAR  
14 DEPARE  
15 DEPCNT  
16 DRGARE  
17 FAIRWY  
18 FOGSIG  
19 HRBFAC  
20 LAKARE  
21 LNDARE  
22 LNDELV  
23 LNDRGN  
24 LNDMRK  
25 LIGHTS  
26 MAGVAR  
27 MORFAC  
28 NAVLNE  
29 OBSTRN  
30 PILPNT  
31 PIPSOL  
32 PONTON  
33 RECTRC  
34 RESARE  
35 RIVERS  
36 SNDWAV  
37 SEAARE  
38 SBDARE  
39 SLCONS  
40 SILTNK  
41 SOUNDG  
42 UWTROC  
43 VEGATN  
44 WEDKLP  
45 WRECKS  
46 M_COVR  
47 M_NPUB  
48 M_NSYS  
49 M_QUAL  
50 C_AGGR  
