from single_point_extract_v2 import *
from datetime import datetime
from time import gmtime, strftime
from dateutil import relativedelta as dt, tz, parser as dtparser

#Return coordinates where where ['d'] of the IP1 values are equal to the threshold:
#therefore - this example does not include glacier, inland lake, water, urban
ip1 = [1199, 1198, 1197, 1179]
lat = 53.9215087890625
lon = 272.4756774902344
input_geophy = "/fs/site4/eccc/mrd/rpnenv/ega001/sps/experiments/Ref_SVS1_RDRS_v2/geophy/Gem_geophy.fst"
coords = fstgetcoords(input_geophy, ip1 = ip1 ,lat = lat, lon = lon, threshold = 0)
#coords = (lat,lon)

##########################################################################
#read and export data from geophy.fst
input_geophy = "//fs/site4/eccc/mrd/rpnenv/ega001/sps/experiments/Ref_SVS1_RDRS_v2/geophy/Gem_geophy.fst"
output_path = ''


final_df = fstgetdata(input_geophy, coords = coords)
geophy_subset = final_df.drop(columns = ['ip2'])
geophy_subset = geophy_subset[['nomvar', 'data']]
output_file = os.path.join(output_path, 'geophy_var.txt')
geophy_subset.to_csv(output_file, sep =' ', index = False, header = ['',''])

##########################################################################
# #read and export input data 
# output_path = '/home/brd004/site3/EG_experiment/output/input_SVS_tile'

# #coords = fstgetcoords(input_geophy, ip1 = ip1 ,threshold = 0, lat = lat, lon = lon)

# LOCAL_TIME_ZONE = tz.gettz(u'GMT+0')
# if (LOCAL_TIME_ZONE is None):
	# print('ERROR: The time zone is not supported. The script cannot continue.')
	# exit()

# #  Start date/time.
# START_TIME = datetime(2014, 7, 31, tzinfo = LOCAL_TIME_ZONE)
# # Stop date/time.
# STOP_BEFORE_TIME = datetime(2014, 8, 06, tzinfo = LOCAL_TIME_ZONE)

# FST_RECORD_MINUTES = +1440

# # Check record length is compatible with first date/time.
# # if ((LOCAL_TIME_ZONE.utcoffset(START_TIME).total_seconds()/60.0) % FST_RECORD_MINUTES != 0):
	# # print('ERROR: Time-offset (%d minutes) is incompatible with time-stepping of files (%d minutes). The script cannot continue.' % ((LOCAL_TIME_ZONE.utcoffset(START_TIME).total_seconds()/60.0), FST_RECORD_MINUTES))
	# # exit()

# # Initialize time loop.               
# UTC_STD_OFFSET = LOCAL_TIME_ZONE.utcoffset(START_TIME) - LOCAL_TIME_ZONE.dst(START_TIME)
# FST_START_TIME = START_TIME.astimezone(tz.tzutc()) + LOCAL_TIME_ZONE.dst(START_TIME)
# FST_STOP_BEFORE_TIME = STOP_BEFORE_TIME.astimezone(tz.tzutc()) + LOCAL_TIME_ZONE.dst(STOP_BEFORE_TIME)
# FST_CURRENT_TIME = FST_START_TIME

# #Create list to append data 
# forcing_data = []

# while FST_CURRENT_TIME < FST_STOP_BEFORE_TIME:
    # FRIENDLY_TIME = FST_CURRENT_TIME.replace(tzinfo = None) + UTC_STD_OFFSET
    # #generate list of data paths 
    # fstsrc = utctimetofstfname_CSLM_input(FST_CURRENT_TIME)
    # print('%s %s' % (strftime('%Y/%m/%d %H:%M:%S', FRIENDLY_TIME.timetuple()), fstsrc['path']))
    # #Import data
    # #state_var = True will subset state variables and forcing data into two seperate dataframes
    # forcing_in = fstgetdata(fstsrc['path'], coords = coords, state_var = False)
    # forcing_data.append(forcing_in)
    # FST_CURRENT_TIME += dt.relativedelta(minutes = FST_RECORD_MINUTES)
    # forcing_df = pd.concat(forcing_data, ignore_index = True)

# #drop duplicate dates  
# forcing_df = forcing_df.drop_duplicates(keep = 'last', subset = ['date', 'nomvar'])

# #re-order DataFrame 
# forcing_df = forcing_df[['date', 'data','nomvar']]

# for var in forcing_df.nomvar.unique():
    # df_subset = forcing_df.loc[forcing_df.nomvar == var].drop(columns = ['nomvar'])
    # print(var + ":\n", df_subset)
    # output_file = os.path.join(output_path, var + '.txt')
    # df_subset.to_csv(output_file, sep =' ', index = False, header = [var,''])

##########################################################################
#read and export input data 
output_path = ''

#coords = fstgetcoords(input_geophy, keylist_in = keylist_in, threshold = 0)

LOCAL_TIME_ZONE = tz.gettz(u'GMT+0')
if (LOCAL_TIME_ZONE is None):
	print('ERROR: The time zone is not supported. The script cannot continue.')
	exit()

#  Start date/time.
START_TIME = datetime(2014, 8, 1, tzinfo = LOCAL_TIME_ZONE)
# Stop date/time.
STOP_BEFORE_TIME = datetime(2014, 8, 5, tzinfo = LOCAL_TIME_ZONE)


FST_RECORD_MINUTES = +60

# Initialize time loop.               
UTC_STD_OFFSET = LOCAL_TIME_ZONE.utcoffset(START_TIME) - LOCAL_TIME_ZONE.dst(START_TIME)
FST_START_TIME = START_TIME.astimezone(tz.tzutc()) + LOCAL_TIME_ZONE.dst(START_TIME)
FST_STOP_BEFORE_TIME = STOP_BEFORE_TIME.astimezone(tz.tzutc()) + LOCAL_TIME_ZONE.dst(STOP_BEFORE_TIME)
FST_CURRENT_TIME = FST_START_TIME

#Create list to append data 
appended_data = []
state_data  = []

while FST_CURRENT_TIME < FST_STOP_BEFORE_TIME:
    FRIENDLY_TIME = FST_CURRENT_TIME.replace(tzinfo = None) + UTC_STD_OFFSET
    #states
    fstsrc = utctimetofstfname_CSLM_output(FST_CURRENT_TIME + dt.relativedelta(days = -1), ip2 = 24)
    state_in = fstgetdata(fstsrc['path'], coords = coords)
    state_data.append(state_in)
    #generate list of data paths
    for ip2 in range(24):
        fstsrc = utctimetofstfname_CSLM_output(FST_CURRENT_TIME, ip2 = ip2))
        forcing_in = fstgetdata(fstsrc['path'], coords = coords)
        appended_data.append(forcing_in)
    FST_CURRENT_TIME += dt.relativedelta(days = 1) #(minutes = FST_RECORD_MINUTES)
    final_df = pd.concat(appended_data, ignore_index = True)
    state_df = pd.concat(state_data, ignore_index = True)

#drop duplicate dates  
final_df = final_df.drop_duplicates(keep = 'last', subset = ['date', 'nomvar'])

#re-order DataFrame 
final_df = final_df[['date', 'data','nomvar']]
state_df= state_df[['date', 'data','nomvar']]

for var in state_df.nomvar.unique():
    state_subset = state_df[['date','nomvar', 'data']]
    print(state_subset)
    output_file = os.path.join(output_path, 'state_var.txt')
    state_subset.to_csv(output_file, sep =' ', index = False, header = ['','',''])

for var in final_df.nomvar.unique():
    df_subset = final_df.loc[final_df.nomvar == var].drop(columns = ['nomvar'])
    print(var + ":\n", df_subset)
    output_file = os.path.join(output_path, var + '.txt')
    df_subset.to_csv(output_file , sep =' ', index = False, header = [var,''])
