"""

MSC FST Data extractor 

A 1D extraction tool for FST files created by MSC

Created: Oct 12th, 2021

Contributors:
    Brenden Disher
    Daniel Princz

"""

# ============================================================================
import rpnpy.librmn.all as rmn
import numpy as np 
import os, sys
import pandas as pd
from os import path
from dateutil import relativedelta as dt, parser as dtparser
# ============================================================================
''' 

configuration
    
    configure the paths required for the functions; utctimetofstfname_input and utctimetofstfname_output
    
    Options
    ----------
    path_input: path 
        path to folder containing input data
    path_output: path 
        path to folder containing output data
        
    
'''
## Required for time functions below
#path for input data 
path_input = '/home/ega001/store4/sps/experiments/CAN_10K_SPS61/pilot'
#path for output data 
path_output = '/home/brd004/site3/CSLM_experiment/SPS_5.9.9_CSLM_exp5/output'

#-----------------------------------------

def fstgetip1(inpufst, ip1_list):
    
    """
    Generates list of keys based on a list of IP1 values. 
    
    Parameters
    ----------
       inputfst: path
            path to FST file.
       ip1: list 
            list of ip1 value(s) for the desired tile. 
    
    Returns
    ----------
            list of keys based on ip1 values 
 
    """
    
    #check if the file is FST
    if not rmn.isFST(inputfst):
       raise rmn.FSTDError("Not an FSTD file: %s " % inputfst)

    try:
        fileId = rmn.fstopenall(inputfst, rmn.FST_RO)
    except:
        sys.stderr.write("Problem opening the file: %s\n" % inputfst)
     
    #Set the interpolation method 
    rmn.ezsetopt(rmn.EZ_OPT_INTERP_DEGREE, rmn.EZ_INTERP_NEAREST)
    
    key_list = []
    
    for i in ip1_list:
         var = rmn.fstlir(fileId, ip1 = i)
         var_key = var['key']
         key_list.append(var_key)
         print(var['nomvar'], var['key'])
    return key_list
#-----------------------------------------
    
def fstgetcoords(inputfst, nomvar = ' ', threshold = None, ip1 = None, ip2 = -1, ip3 = -1, etiket = ' ', lat = None, lon = None, x = None, y = None):
    """
    extracts a pair or coordinates based on parameters or threshold values. 
    
    Parameters
    ----------
       inputfst: path
            path to FST file. (required)
       nomvar: list 
            list of nomvar for each tile (optional)
       threshold: int 
            value ranging from 1 to 0. Can be used to isolate specific tiles. (required)
       ip1: list 
            list of ip1 value(s) for the desired tile. (optional)
       ip2: int
            ip2 value (optional)
       ip3: int 
            ip3 value (optional)
       etiket:  
            eticket value (optional)
       lat: int
            latitude of desired coordinate (optional)
       lon: int
            longitude of desired coordinate (optional)
       x: int 
            'x' grid value of desired coordinate (optional)
       y: int
            'x' grid value of desired coordinate (optional)
            
    Returns
    ----------
            list containing array of coordinates that met conditions within function
            
            ex: (array([57.588123], dtype=float32), array([272.76974], dtype=float32))

    """

    #check if the file is FST
    if not rmn.isFST(inputfst):
       raise rmn.FSTDError("Not an FSTD file: %s " % inputfst)

    try:
        fileId = rmn.fstopenall(inputfst, rmn.FST_RO)
    except:
        sys.stderr.write("Problem opening the file: %s\n" % inputfst)
     
    #Set the interpolation method 
    rmn.ezsetopt(rmn.EZ_OPT_INTERP_DEGREE, rmn.EZ_INTERP_NEAREST)
    
    if threshold is None:
        raise sys.stderr.write("No threshold value entered")
    else: 
        pass
    
    #generate array if nomvar is used instead of IP1
    #loop through and append arrays for each variable -- then produce an array of tuples where each array is equal to the threshold
    if ip1 is None:
        data = []
        for i in nomvar:
            var = rmn.fstlir(fileId, nomvar = i)
            data_grid = rmn.readGrid(fileId, var)
            var_array = var['d']
            data.append(var_array)
    else:
    #loop through and append arrays for each variable -- then produce an array of tuples where each array is equal to the threshold
        data = []
        for i in ip1:  ### use ip1 instead 
            var = rmn.fstlir(fileId, ip1 = i)
            data_grid = rmn.readGrid(fileId, var)
            var_array = var['d']
            data.append(var_array)
            
    #search for matching values based on threshold -- if matching values are found,    
    val_len = len(ip1)
    array_z = []
    counter = val_len
    for n in data:
        counter = counter -1 
        if counter != val_len:
            temp_array = np.argwhere((data[counter] == float(threshold)))
            array_z.append(temp_array)
            print("Finding Matching data")
        else:
            break
        array_fin = np.vstack(array_z)
        u,c = np.unique(array_fin, axis = 0, return_counts = True )
        array_q = u[c == val_len]
    
    #exit if no matching values are found/ 
    if len(array_q) == 0:
        print("No values found")
        exit()
    else:
        pass
            
    array_x = array_q[0].astype(np.float32)
    array_y = array_q[1].astype(np.float32)
       
    # determine lat/lon coordinates if x/y are input into the function 
    if not (lat and lon) is None:   
        coord_xy = rmn.gdllfxy(data_grid, array_x +1, array_y +1)
        if [lat in coord_xy['lat'] and lon in coord_xy['lon']]:
            coord = rmn.gdxyfll(data_grid, lat = lat, lon= lon)
            print("The coordinates (lat)(lon) are", coord['lat'][0],coord['lon'][0])
        else:
            print("Warning: coordinates not found in threshold array")
            exit()
    # determine x/y coordinates if lat/lon are input into the function 
    elif not (x and y) is None:
        x = x + 1
        y = y + 1
        if (x in array_x and y in array_y):
            coord = rmn.gdllfxy(data_grid, x, y)
            print("The coordinates (x)(y) are", coord['lat'][0],coord['lon'][0])
        else:
            print("Warning: coordinates not found in threshold array")
            exit()
    #generates random coordinates that match the conditions if none are input into the function. 
    else:  
        array_random = tuple(np.random.permutation(array_q)[0])
        lat = (array_random[0]+1).tolist()
        lon = (array_random[1]+1).tolist()
        coord = rmn.gdllfxy(data_grid, lat, lon)
        print("The random coordinates (x)(y) are", coord['lat'][0],coord['lon'][0])
           
    #spilt lat lon into seperate arrays
    lat_coord = coord['lat']
    lon_coord = coord['lon']

    #close the file 
    rmn.fstcloseall(fileId)
    
    #return coordinates 
    return(lat_coord,lon_coord)

    print('\nProcessing has completed.')

#-----------------------------------------

def fstgetdata(inputfst, coords = None, ip2 =-1, etiket ='', lat = None, lon = None, state_var = False):
    """
    extracts data based on coordinates input 
    
    Parameters
    ----------
       inputfst: path
            path to FST file. (required)
       coords: 
       ip2: int 
            value ranging from 1 to 0. Can be used to isolate specific tiles. (optional)
       eticket: list 
            list of ip1 value(s) for the desired tile. (optional)
       lat: int
            latitude of desired coordinate (optional)
       lon: int
            longitude of desired coordinate (optional)
       state_var: bool 
            true or false: if true, a seperate 'state_var' dataframe will be established
            containing state variables (ip2 = 24) within the FST file. 

    Returns
    ----------
            Pandas dataframe. 
        
            Index | data | date | ip2 |nomvar
            _____________________________________________________________________________________________________________
            
            0 |
            1 |
            2 |
            .
            .
            .
            n |

    """

#check if the file is FST
    if not rmn.isFST(inputfst):
       raise rmn.FSTDError("Not an FSTD file: %s " % inputfst)

    try:
        fileId = rmn.fstopenall(inputfst, rmn.FST_RO)
    except:
        sys.stderr.write("Problem opening the file: %s\n" % inputfst)
        
    if (lat and lon) is None:
        lat_in = coords[0]
        lon_in = coords[1]
    else:
        lat_in = lat 
        lon_in = lon 
    
    print("The coordinates (lat)(lon) are",lat_in ,lon_in)

    #Set the interpolation method 
    rmn.ezsetopt(rmn.EZ_OPT_INTERP_DEGREE, rmn.EZ_INTERP_NEAREST)
        
    #generate keylist 
    keylist = rmn.fstinl(fileId)

    #generate
    var_list  = []
    data_list = [] 
    date_list = []
    ip2_list  = []
    var_df_state = None
    var_df_forcing = None

    for k in keylist:
        var = rmn.fstluk(k)
        var_grid = rmn.readGrid(fileId, var)
        if (var['typvar'].strip() != 'X'): 
            (ip1, ip2, ip3) = rmn.DecodeIp(var['ip1'], var['ip2'], var['ip3'])
            if (ip1.kind in [rmn.KIND_SIGMA, rmn.KIND_HYBRID]):
                level = "%f" % (ip1.v1)
                level = level.replace(' ','_').replace('.','p')
            else:
                level = '%d' % ip1.v1
            if (ip1.v1 != -1):
                if (ip1.v1  >0):
                    ip1_level = ('_%s' % level) 
                else:
                    ip1_level = ''
                if var['datev'] > 0:
                    (yyyymmdd,hhmmsshh) = rmn.newdate(rmn.NEWDATE_STAMP2PRINT,var['datev'])
                    datev = "%08d%08d" % (yyyymmdd,hhmmsshh)
                    datev = pd.to_datetime(datev, format = '%Y%m%d%H%M%S00')
                else:
                    datev = None
                if (var['nomvar'].strip().lower() == 'uu' or var['nomvar'].strip().lower() == 'u8') :
                    xy = rmn.gdxyfll(var_grid, lat = lat_in, lon = lon_in)
                    if (var['nomvar'].strip().lower() == 'uu'):
                        uu_data = rmn.fstlir(fileId, nomvar = 'UU', datev=var['datev'], etiket=var['etiket'], ip1=var['ip1'], ip2=var['ip2'], ip3=var['ip3'], typvar=var['typvar'])
                        vv_data = rmn.fstlir(fileId, nomvar = 'VV', datev=var['datev'], etiket=var['etiket'], ip1=var['ip1'], ip2=var['ip2'], ip3=var['ip3'], typvar=var['typvar'])
                        var_list.append('UU' + ip1_level) 
                        var_list.append('UV' + ip1_level) 
                        var_list.append('WD' + ip1_level) 
                        var_list.append('VV' + ip1_level) 
                    else: 
                        uu_data = rmn.fstlir(fileId, nomvar = 'U8', datev=var['datev'], etiket=var['etiket'], ip1=var['ip1'], ip2=var['ip2'], ip3=var['ip3'], typvar=var['typvar'])
                        vv_data = rmn.fstlir(fileId, nomvar = 'V8', datev=var['datev'], etiket=var['etiket'], ip1=var['ip1'], ip2=var['ip2'], ip3=var['ip3'], typvar=var['typvar'])
                        var_list.append('U8' + ip1_level) 
                        var_list.append('UV8' + ip1_level) 
                        var_list.append('WD8' + ip1_level) 
                        var_list.append('V8' + ip1_level) 
                        #if wswd is True:
#                    from gdxywdval import gdxywdval
#                    (uv,wd) = gdxywdval(var_grid, xy['x'], xy['y'], uu_data['d'], vv_data['d'])
                        #else:
#                    (uu,vv) = rmn.gdxyvval(var_grid, xy['x'], xy['y'], uu_data['d'], vv_data['d'])
                        #if (var['nomvar'].strip().lower() == 'uu'):
                    (uv,wd) = rmn.gdllwdval(var_grid, lat_in, lon_in, uu_data, vv_data)
                    (uu,vv) = rmn.gdllvval(var_grid, lat_in, lon_in, uu_data, vv_data)
                    data_list.append(uu[0])
                    data_list.append(uv[0])
                    data_list.append(wd[0])
                    data_list.append(vv[0])
                    for i in range(4):
                        date_list.append(datev)
                        ip2_list.append(var['ip2'])
                elif (var['nomvar'].strip().lower() != 'vv' and var['nomvar'].strip().lower() != 'v8') :
#                if (True):
                    data_q =  rmn.gdllsval(var_grid, lat_in, lon_in, var['d'])
                    data_list.append(float(data_q))
                    date_list.append(datev) 
                    var_list.append(var['nomvar'].strip() + ip1_level) 
                    ip2_list.append(var['ip2'])
            var_df = pd.DataFrame({'nomvar': var_list, 'data': data_list, 'date': date_list, 'ip2': ip2_list})
            if state_var is True:
                var_df_state = var_df.loc[var_df.ip2 == 24]
                var_df_forcing = var_df.loc[var_df.ip2 != 24]
            else:
                pass
    
    #close the file 
    rmn.fstcloseall(fileId)
    
    #Generate separate arrays if state variables are extracted. 
    if state_var is True:
        return var_df_state,var_df_forcing
    else:
        return var_df
    print('\nProcessing has completed.')

#-----------------------------------------

def utctimetofstfname_input(utctime, ip2 = None):

    """
    determines file names based on the desired time range for input files and returns a path. 
    
    Parameters
    ----------
        utctime: datetime
            datetime object containing the utc time for the input file.
            
            ex: datetime.datetime(2016, 8, 4, 0, 0, tzinfo=tzutc())
        
    Returns
    ----------
        dictionary containing the path and ip2 of the file based on utctime. 
        
        {'ip2': --, 'path': ''}
        
        

    """

    # 00:00->23:00
    filetime = utctime
    if (not ip2 is None):
        fileip2 = ip2
    else:
        fileip2 = filetime.hour
    filefcst = 12
    fstsrcpath = path_input + ('/%04d%02d%02d%02d_forcing' % (filetime.year, filetime.month, filetime.day, filefcst))

    # Stop if the path does not exist.
    if (not path.exists(fstsrcpath)):
        print('ERROR: Path does not exist. Script cannot continue. ' + fstsrcpath)
        exit()

    # Return file path and adjust ip2.
    # 01:00->24:00
    return { 'path': fstsrcpath, 'ip2': fileip2 }

#-----------------------------------------

def utctimetofstfname_output(utctime, ip2 = None):

    """
    determines file names based on the desired time range for input files and returns a path. 
    
    Parameters
    ----------
        utctime: datetime
            datetime object containing the utc time for the input file.
            
            ex: datetime.datetime(2016, 8, 4, 0, 0, tzinfo=tzutc())
        
    Returns
    ----------
        dictionary containing the path and ip2 of the file based on utctime. 
        
        {'ip2': --, 'path': ''}

    """

    # 00:00->23:00
    filetime = utctime
    if (not ip2 is None):
        fileip2 = ip2
    else:
        fileip2 = filetime.hour
    #dummy varible to account for extra 0's in the file naming
    filedummy = 0
    filefcst = 12

    dirpath = path_output +  ('/output_%04d%02d%02d%02d/analysis' % (filetime.year, filetime.month, filetime.day, filefcst))
    fstsrcpath = dirpath + ('/pm%04d%02d%02d%02d%04d-%02d-%02d_%04d%02dh' % (filetime.year, filetime.month, filetime.day, filefcst, filedummy, filedummy, filedummy, filedummy, fileip2))

    # Stop if the path does not exist.
    if (not path.exists(fstsrcpath)):
        print('ERROR: Path does not exist. Script cannot continue. ' + fstsrcpath)
        exit()

    # Return file path and adjust ip2.
    # 01:00->24:00
    return { 'path': fstsrcpath, 'ip2': fileip2 }

#-----------------------------------------
