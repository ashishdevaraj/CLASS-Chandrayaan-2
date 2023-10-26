#!/usr/bin/env python
# coding: utf-8

# In[1]:


import glob
import numpy as np
import pandas as pd
from astropy.io import fits
import matplotlib.pyplot as plt


# In[2]:


start = '20230513'
stop = ''
search = start +'*_'+ stop +'*'

specnames = glob.glob('class_data/ch2_cla_l1_'+ search +'.fits')
specnames = sorted(specnames)

sufix = start

total_channels = 2048
ct_combine_img = 40

Energy = np.arange(0,total_channels,1) * 0.0135 #keV, column 1: energy
Channels = np.arange(0,total_channels,1)
Tcounts = np.zeros(total_channels) # Column 2: Counts


ct = 1
filesinfo = []
for sp in specnames:
    print(sp)
    
    if ct > ct_combine_img: # combine only ct_combine_img number of images
        break
    
    hdu = fits.open(sp)
    hdr = hdu[1].header 
    
    
    if hdu[1].header['solarang'] > 90: # removing night side
        print('removed')
        continue
        
    if ct == 0: # Identifying the first image
        first = sp

    scidata = hdu[1].data
    Tcounts = Tcounts + scidata['counts']
    
    #print(ct, sp, hdu[1].header['solarang'])
    ct+=1
    
    filesinfo.append([sp, hdr['solarang'],
                     hdr['V0_LAT'],hdr['V0_LON'],
                     hdr['V1_LAT'],hdr['V1_LON'],
                     hdr['V2_LAT'],hdr['V2_LON'],
                     hdr['V3_LAT'],hdr['V3_LON']])

# Saving Combined spectrum
tbhdu = fits.BinTableHDU.from_columns([fits.Column(name='CHANNEL', format='I', array=Channels),
                                       fits.Column(name='COUNTS', format='E', array=Tcounts),
                                       fits.Column(name='ENERGY', format='E', array=Energy)])
tbhdu.header['HISTORY'] = 'This spectra is a combination of %d files.' %(ct_combine_img)
tbhdu.header['EXPOSURE'] = (8*ct_combine_img, 'Combined exposure time')
#tbhdu.header = fits.open(first)[1].header # Copying the header of the first table to the combined table

tbhdu.writeto('ch2_class_Combined_'+str(8*ct_combine_img)+'s_'+ sufix +'.fits', overwrite=True)


df = pd.DataFrame(filesinfo, columns=["name","solarangle",
                                   "V0_LAT","V0_LON","V1_LAT","V1_LON",
                                   "V2_LAT","V2_LON","V3_LAT","V3_LON",])
df.to_csv('ch2_class_Combined_'+str(8*ct_combine_img)+'s_'+ sufix +'.csv', index=False)


# In[4]:


# Combining background spectrum
Bcounts = np.zeros(total_channels) # Column 2: Counts

ct = 1
filesinfo = []
for sp in specnames:
    
    if ct > ct_combine_img: # combine only ct_combine_img number of images
        break
    
    hdu = fits.open(sp)
    hdr = hdu[1].header
    
    
    if hdu[1].header['solarang'] < 90: # removing night side
        continue
        
    if ct == 0: # Identifying the first image
        first = sp

    background = hdu[1].data
    Bcounts = Bcounts + background['counts']
    
    ct+=1
    
    #print(sp, hdu[1].header['solarang'])
    filesinfo.append([sp, hdr['solarang'],
                     hdr['V0_LAT'],hdr['V0_LON'],
                     hdr['V1_LAT'],hdr['V1_LON'],
                     hdr['V2_LAT'],hdr['V2_LON'],
                     hdr['V3_LAT'],hdr['V3_LON']])

# Saving background spectrum
Btbhdu = fits.BinTableHDU.from_columns([fits.Column(name='CHANNEL', format='I', array=Channels),
                                       fits.Column(name='COUNTS', format='E', array=Bcounts),
                                       fits.Column(name='ENERGY', format='E', array=Energy)])
Btbhdu.header['HISTORY'] = 'This BACKGROUND spectra is a combination of %d files.' %(ct_combine_img)
Btbhdu.header['EXPOSURE'] = (8*ct_combine_img, 'Combined exposure time')
#tbhdu.header = fits.open(first)[1].header # Copying the header of the first table to the combined table

Btbhdu.writeto('ch2_class_Combined_BACKGROUND_'+str(8*ct_combine_img)+'s_'+ sufix +'.fits', overwrite=True)


df = pd.DataFrame(filesinfo, columns=["name","solarangle",
                                   "V0_LAT","V0_LON","V1_LAT","V1_LON",
                                   "V2_LAT","V2_LON","V3_LAT","V3_LON",])
df.to_csv('ch2_class_Combined_BACKGROUND_'+str(8*ct_combine_img)+'s_'+ sufix +'.csv', index=False)


# In[5]:


# Plotting
plt.rcParams.update({'font.size': 20})
plt.rcParams['font.family'] = 'STIXGeneral'
plt.figure(figsize=(15, 10))
plt.tick_params(direction='in', length=8, width=1, top=True,right=True, pad=15)

plt.plot(Energy, Tcounts, 'k-', label='CLASS sample spectrum')
plt.yscale('log')
#plt.xlim(0.4,10.1)
plt.xlabel('Energy (keV)')
plt.ylabel('Counts')
plt.legend()
plt.savefig('ch2_class_Combined_'+str(8*ct_combine_img)+'s_'+ sufix +'.jpg')


# In[ ]:




