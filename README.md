# ChartPlotter
Python library to render NOAA charts

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