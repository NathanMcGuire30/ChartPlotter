# ChartPlotter
Python library to render NOAA charts

###Install

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

Also requires NavPY

###Charts:
I use the NOAA vector charts, because they are dropping support for all else. 
I downloaded the zip file from their website for the Woods Hole Passage chart and extracted its contents into a folder called
`ChartPlotter/Charts`.

###Description
Currently, test4.py is my development script.  It rasterizes the charts and saves each layer as a .tiff.