#!/usr/bin/env python
# coding: utf-8

#Copyright 2023 CLASS team
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.


# In[ ]:


import os
import sys
import glob
import shutil
import zipfile
import numpy as np
import pandas as pd
from astropy.io import fits
from datetime import datetime, timedelta


# In[ ]:


if len(sys.argv) > 1:
    zip_file_path = sys.argv[1]
else:
    zip_file_path = input("Enter a ZIP path with file name: ")


# ### Unzipping the CLASS L1 zip file and finding fits files within

# In[ ]:


PWD = os.getcwd()
extract_to_path = PWD+'/fits_files/'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to_path)

fits_files = []
# Recursive search for all files with a .fits extension
for root, dirs, files in os.walk(extract_to_path):
    fits_files.extend(glob.glob(os.path.join(root, '*.fits')))


# ### Function to read fits file and retrieve the following
# 1. total counts, 2. Start time, and 3. End time

# In[ ]:


def read_FITS(fits_file_path):
  
    # Open the FITS file
    with fits.open(fits_file_path) as hdul:
        # Get the header from the primary HDU
        header = hdul[1].header
        data = hdul[1].data
        total_counts = np.sum(data['counts'])
        
        # Check if the keyword is present in the header
        if 'startime' in header:
            start = header['startime']
        else:
            start = 'Not found'
            
        if 'endtime' in header:
            end = header['endtime']
        else:
            end = 'Not found'
            
        return total_counts, start, end


# ### Function to estimate the mid time when start time and end time are given

# In[ ]:


def calculate_mid_time(start_time_str, end_time_str):
    
    if (start_time_str == 'Not found' or end_time_str == 'Not found'):
        return 'Not found in FITS'
    else:
        # Parse the start and end time strings
        start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S.%f")
        end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M:%S.%f")

        # Calculate the time difference between start and end times
        time_difference = end_time - start_time

        # Calculate the mid time as half of the time difference added to the start time
        mid_time = start_time + time_difference / 2

        return mid_time


# ### Generating CLASS light curve

# In[ ]:


Counts = []
time = []

for f in fits_files:
    c, s, e = read_FITS(f)
    m = calculate_mid_time(s, e)
    
    Counts = np.append(Counts, c.astype('float'))
    time = np.append(time, m.strftime('%Y-%m-%dT%H:%M:%S.%f'))
    
light_curve = np.column_stack([time, Counts.astype('float')])
lc = pd.DataFrame(light_curve, columns=['time', 'total_counts'])
lc['time'] = pd.to_datetime(lc.time)
lc_sorted = lc.sort_values(by='time', ascending=True)
lc_sorted.to_csv('LightCurve.csv', index=False)


# ### Removing temporary files

# In[ ]:


if os.path.exists(extract_to_path):
    try:
        shutil.rmtree(extract_to_path)  # Use this if the directory is empty
    except OSError as e:
        pass


# In[ ]:

print('LightCurve.csv saved in current directory.')

