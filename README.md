# 1D extration scripts for Environment Canada FST files. 
**Overview**

These scripts extract a one-dimensional data point from Envrionment Canada's standard format files (FST). 

There is the functionality to input a set of desired coordinates (longtitude, latitude, x or y), or to query coordinates based on a set of attributes and landcover indicies from geophysical input fields. Once a set of coordinates are selected,  data is queried from *.fst* files containing model outputs.  

Currently, the only method of exporting data is into *.txt* files based on the variable names within the *.fst* files.

-------------------------------------------------------------------------
**Python Dependencies**

- Numpy
- Pandas 
- dateutil 
- rpnpy.lib.rmn.all (Interal to ECCC network)

-------------------------------------------------------------------------
## Examples:

**Determinining a pair of desired coordinates**

In the example script, a pair of pre-determined pair of coordinates is used where the listed ip1 values all equal zero. 

```

ip1 = [1199, 1198, 1197, 1179]
lat = 53.9215087890625
lon = 272.4756774902344
coords = fstgetcoords(input_geophy, ip1 = ip1 ,lat = lat, lon = lon, threshold = 0)

```

**Extracting data** 

Data may be exported using *fstgetdata*. In the example below, the function is used to extract geophysical fields from the GEM_fst file. 

```

final_df = fstgetdata(input_geophy, coords = coords)

```

**Note**: file names for *.fst* files are often incremented by date and time of the experiment. *utctimetofstfname_output* can be used in a loop to increment through various files within the same directory. The example file *SVS_regular_tile_v2.py* contains a more complex data extraction example. This script may be repurposed. 

## License

Unless otherwise noted, the source code of this project is covered under Crown Copyright, Government of Canada, and is distributed under the [MIT License](LICENSE).

The Canada wordmark and related graphics associated with this distribution are protected under trademark law and copyright law. 
No permission is granted to use them outside the parameters of the Government of Canada's corporate identity program. For more information, see [Federal identity requirements](https://www.canada.ca/en/treasury-board-secretariat/topics/government-communications/federal-identity-requirements.html).

