import rpnpy.librmn.all as rmn
import numpy as np 
import os, sys
import pandas as pd
from os import path
from dateutil import relativedelta as dt, parser as dtparser

## Required for time functions below
#path for input data 
#path_input = '/home/ega001/store4/sps/experiments/CAN_10K_SPS61/pilot'
#path for output data 
path_output = '/home/brd004/site3/CSLM_experiment/SPS_5.9.9_CSLM_exp5/output'

def fstgetip1(inpufst, ip1_list):
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
    
def fstgetcoords(inputfst, nomvar = ' ', threshold = None, ip1 = None, ip2 = -1, ip3 = -1, etiket = ' ', lat = None, lon = None, x = None, y = None):

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

    if ip1 is None:
        data = []
        for i in nomvar
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
    #search for matching values    
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
    if len(array_q) == 0:
        print("No values found")
        exit()
    else:
        pass
    # else:
        # pass
    array_x = array_q[0].astype(np.float32)
    array_y = array_q[1].astype(np.float32)
    # else:  
        # data = rmn.fstlir(fileId, ip1 = ip1, ip2 = ip2, ip3 = ip3, nomvar = nomvar, etiket = etiket) 
        # array = data['d']
        # #derive the grid 
        # data_grid = rmn.readGrid(fileId, data)
        # #determine x and y locations where the threshold is met 
        # array_q = np.where(array == float(threshold))
        # array_x = array_q[0].astype(np.float32)
        # array_y = array_q[1].astype(np.float32)
        
    if not (lat and lon) is None:   
        coord_xy = rmn.gdllfxy(data_grid, array_x +1, array_y +1)
        if [lat in coord_xy['lat'] and lon in coord_xy['lon']]:
            coord = rmn.gdxyfll(data_grid, lat = lat, lon= lon)
            print("The coordinates (lat)(lon) are", coord['lat'][0],coord['lon'][0])
        else:
            print("Warning: coordinates not found in threshold array")
            exit()
    elif not (x and y) is None:
        x = x + 1
        y = y + 1
        if (x in array_x and y in array_y):
            coord = rmn.gdllfxy(data_grid, x, y)
            print("The coordinates (x)(y) are", coord['lat'][0],coord['lon'][0])
        else:
            print("Warning: coordinates not found in threshold array")
            exit()
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
    
    return(lat_coord,lon_coord)

    print('\nProcessing has completed.')


def fstgetdata(inputfst, coords = None, ip2 =-1, etiket ='', lat = None, lon = None, state_var = False, keylist_in = None, wswd = False):

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

    # if keylist_in is None:
        # pass
    # else:
        # keylist = [x for x in keylist_in if x in keylist]

    var_list  = []
    data_list = [] 
    date_list = []
    ip2_list = []
    #uuvv = []
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
    
    if state_var is True:
        return var_df_state,var_df_forcing
    else:
        return var_df
    print('\nProcessing has completed.')
            
def utctimetofstfname_input(utctime):

    # 00:00->23:00
    filetime = utctime
    filefcst = 12
    fstsrcpath = path_input + ('/%04d%02d%02d%02d_forcing' % (filetime.year, filetime.month, filetime.day, filefcst))

    # Stop if the path does not exist.
    if (not path.exists(fstsrcpath)):
        print('ERROR: Path does not exist. Script cannot continue. ' + fstsrcpath)
        exit()

    # Return file path - ip2 (hour) not needed - daily files
    return {'path': fstsrcpath}

def utctimetofstfname_output(utctime, ip2 = None):

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


