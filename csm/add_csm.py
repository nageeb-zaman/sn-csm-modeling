"""Attach a circumstellar medium (CSM) to a STELLA input model.

Reads the ejecta hydro/abundance profiles written by MESA for STELLA
(mesa.hyd / mesa.abn), appends CSM zones, and writes new profiles
(mesa_csm_v5.hyd / mesa_csm_v5.abn) that STELLA can run directly.

Three CSM density structures are supported via `density_profile`:
    'wind'           steady wind, rho = Mdot / (4 pi r^2 v_csm)
    'gaussian'       Gaussian shell of total mass csm_mass between csm_r_in
                     and csm_r_out
    'wind+gaussian'  steady wind with a Gaussian density bump of peak density
                     `height` between r_i and r_f

Edit the "INPUTS (CSM parameters)" block below, then run
    python add_csm.py
from the folder that holds mesa.hyd and mesa.abn (see csm/README.md).

Author: Nageeb Zaman (LSU)
"""
import numpy as np
import matplotlib.pyplot as plt 
from math import floor

write_hyd_profile = False                # Set to True if we want hydro profile written
write_abn_profile = False                # Set to True if we want hydro profile written
plot_graph = False                       # Set to True if we want to see graph of the hydro and abundance profiles

write_hyd_profile = True 
write_abn_profile = True           
plot_graph = True                       

# Input Filenames
input_hyd_file = "mesa.hyd"
input_abn_file = "mesa.abn"

# Output filenames
hyd_filename = 'mesa_csm_v5.hyd'
abn_filename = 'mesa_csm_v5.abn'

# Reading the ejectra profiles
zero, num_zones, mass_ib, radius_ib, density_ib = np.loadtxt(input_hyd_file,usecols=(0,1,2,3,4),unpack = True)
num,mass_i,radius,density,temp,velocity,pressure,zeros,en,ent,op,tau,v_div_csound = np.loadtxt(input_hyd_file,usecols=(0,1,2,3,4,5,6,7,8,9,10,11,12),skiprows=1,unpack = True)
mass_,dm,radius_,h1,he3_he4,c12,n14,o16,ne20,na23,mg24,al27,si28,s32,ar36,ca40,fe52_54_56,skip,co56_ni56 = np.loadtxt(input_abn_file,usecols=(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19),unpack = True)

num_zones = int(num_zones[0])
ejecta_r_out = radius[-1]               # Outer radius of the progenitor
ejecta_m_out = mass_i[-1]            # Outer mass of the progenitor
ejecta_density_out = density[-1]   # Outer  density of the progenitor

m_sun = 2e33            # Conversion factor: Msun to gram
yr_sec = 3.16e7         # Conversion factor: years to sec

# Some global variables........#
global h,r_o,std_d,csm_mass
adjust_density_floor = False
temp_zones = 0
#..............................#


####....................INPUTS (CSM parameters)......................####
# These are the CSM parameters that need to be tuned to get the desired CSM.

# density_profile = 'gaussian'
density_profile = 'wind+gaussian'
# density_profile = 'wind'
csm_mass = 0.1                 # Mass of the CSM in solar mass units (will be ignored for wind csm case)
csm_r_in = ejecta_r_out         # Inner radius of the CSM is set to be equal to the outer boundary of ejecta.
# csm_r_in = 1.019e13           # Alternatively set the inner radius of the CSM manually. (cm)
csm_r_out = 1.57e15             # Outer radius of the CSM (cm)
v_csm = 100.00                  # wind velocity of the CSM in (km/s)
t_csm = 0.1*temp[-1]            # Temperature of the CSM is set to 0.1 times the temperature of the outer zone of ejecta.
m_dot = 1.0                     # Mass loss rate in M_sun/year (Only used in the Wind CSM case will be ignored for Gaussian CSM case)
csm_zones = 400                 # Number of zones for CSM

v_csm = v_csm * 1e5             # coverting from km/s to cm/s
m_dot = m_dot*m_sun/yr_sec


#...................Gaussian profile parameters for "wind+gaussian" option.............#
if(density_profile == 'wind+gaussian'):
    r_i = 1.0e14                    # Starting radius of the Gaussian profile on the wind
    r_f = 1.0e15                    # End radius of the Gaussian profile on the wind
    height = 1.0e-11                # Peak density for the Gaussian profile
####...............................................................####







m_csm = 0.0  

if(density_profile == 'gaussian'):
    std_d = (csm_r_out-csm_r_in)/10.0             # Standard deviation of the Gaussian Curve. The curve can me made thinner or broader by changing the dividing factor  
    r_o = (csm_r_out+csm_r_in)/2                  # Mean of the Gaussian curve, which is set ot the center of the CSM. 
    norm_fac = (csm_r_out - csm_r_in)/csm_zones           # Normalization factor so that the area under the curve is unity.
    vol_csm = (4/3 * np.pi * (csm_r_out**3 - csm_r_in**3))
    h = 1/(np.sqrt(2*np.pi)*std_d) * norm_fac     # Height of the Gaussian curve which is dependent on the normalization factor. 

    # The Gaussian CSM will not start form zero along the y axis. The base of the Gaussian CSM is going to be the outer density of the ejecta
    # Thats why need to adjust the CSM mass so that the mass contribution form the base is considered. 
    csm_r_in = csm_r_in*1.02
    density_floor = ejecta_density_out
    print("Initial density floor: %1.6E g/cm"%density_floor)
    mass_density_floor = (density_floor* vol_csm) / m_sun 
    print("Initial mass_density_floor: %1.6E m_sun\n"%mass_density_floor)
    mass_w = ejecta_m_out + (4*np.pi*density_floor*csm_r_in**2*(csm_r_in-ejecta_r_out))/m_sun
    adjust_density_floor = False
    if(mass_density_floor > csm_mass):

        adjust_density_floor = True
        mass_density_floor = 10**(floor(np.log10(csm_mass - csm_mass*0.01)))
        density_floor = mass_density_floor *m_sun / vol_csm 
        mass_density_floor = (density_floor* vol_csm) / m_sun
        temp_zones = int((np.log10(ejecta_density_out) - np.log10(density_floor))*10)
        rw_temp = np.linspace(ejecta_r_out,csm_r_in,temp_zones)
        rho_temp = np.linspace(ejecta_density_out,density_floor,temp_zones)
        mass_temp = np.linspace(ejecta_m_out,mass_w,temp_zones)
        rw_temp = rw_temp[1:]
        rho_temp = rho_temp[1:]
        mass_temp = mass_temp[1:]
        temp_zones = temp_zones -1
    csm_mass = csm_mass - mass_density_floor

    total_zones = num_zones+csm_zones+temp_zones
    rw_wind  = [0] * total_zones
    rho_wind = [0] * total_zones
    mass = [0] * total_zones

    r = np.linspace(csm_r_in,csm_r_out,csm_zones+1)
    if(adjust_density_floor):
        rw_old = rw_temp[-1]
        mass_here = mass_temp[-1]
    else:
        rw_old = ejecta_r_out
        mass_here = ejecta_m_out

    for i in range(num_zones+temp_zones,total_zones):
        
        rw_wind[i] = r[i-num_zones-temp_zones+1]
        # rho_wind[i] = density_floor + (mass_gaussian(0.5*(rw_wind[i]+rw_old)) *m_sun / (4 * np.pi * rw_wind[i]**2 *(rw_wind[i] - rw_old))) 
        m = csm_mass * h * np.exp(-((0.5*(rw_wind[i]+rw_old))-r_o)**2/(2*std_d**2)) 
        rho_wind[i] = density_floor + (m *m_sun / (4 * np.pi * rw_wind[i]**2 *(rw_wind[i] - rw_old))) 

        mass_here = mass_here + (4*np.pi * rho_wind[i] * rw_wind[i]**2 * (rw_wind[i] - rw_old))/m_sun
        m_csm = mass_here - ejecta_m_out
        mass[i] = mass_here
        rw_old = rw_wind[i]

if(density_profile== 'wind'):
    adjust_density_floor = True

    rwi = csm_r_in*1.02
    rho_w = m_dot/4.0/np.pi/v_csm/(csm_r_in*1.02)**2
    temp_zones = int(abs(np.log10(ejecta_density_out) - np.log10(rho_w))*15.0)
    mass_w = ejecta_m_out + (4*np.pi*rho_w*rwi**2*(rwi-ejecta_r_out))/m_sun

    total_zones = num_zones+csm_zones+temp_zones
    rw_wind  = [0] * total_zones
    rho_wind = [0] * total_zones
    mass = [0] * total_zones

    rw_temp = np.linspace(csm_r_in,rwi,temp_zones)
    rho_temp = np.linspace(ejecta_density_out,rho_w,temp_zones)
    mass_temp = np.linspace(ejecta_m_out,mass_w,temp_zones)
    rw_temp = rw_temp[1:]
    rho_temp = rho_temp[1:]
    mass_temp = mass_temp[1:]
    temp_zones = temp_zones -1
    dr = (csm_r_out/rwi)**(1.0/csm_zones)
    rw_old = csm_r_in
    mass_here = ejecta_m_out

    for i in range(num_zones+temp_zones,total_zones):
        rw_wind[i] = rwi * dr ** (i+1-num_zones-temp_zones)
        rho_wind[i] = m_dot/(4.0*np.pi*v_csm*(rw_wind[i]**2))
        mass_here = mass_here + (4*np.pi * rho_wind[i] * rw_wind[i]**2 * (rw_wind[i] - rw_old))/m_sun
        mass[i] = mass_here
        rw_old = rw_wind[i]
        m_csm = mass_here - ejecta_m_out
        
if(density_profile== 'wind+gaussian'):
    adjust_density_floor = True
    # Gaussian profile parameters
    std_d = (r_f-r_i)/10.0             # Standard deviation of the Gaussian Curve. The curve can me made thinner or broader by changing the dividing factor  
    r_o = (r_f+r_i)/2                  # Mean of the Gaussian curve, which is set ot the center of the CSM. 
    
    rwi = csm_r_in*1.02
    rho_w = m_dot/4.0/np.pi/v_csm/(csm_r_in*1.02)**2
    temp_zones = int(abs(np.log10(ejecta_density_out) - np.log10(rho_w))*15.0)
    mass_w = ejecta_m_out + (4*np.pi*rho_w*rwi**2*(rwi-ejecta_r_out))/m_sun

    total_zones = num_zones+csm_zones+temp_zones
    rw_wind  = [0] * total_zones
    rho_wind = [0] * total_zones
    mass = [0] * total_zones

    rw_temp = np.linspace(csm_r_in,rwi,temp_zones)
    rho_temp = np.linspace(ejecta_density_out,rho_w,temp_zones)
    mass_temp = np.linspace(ejecta_m_out,mass_w,temp_zones)
    rw_temp = rw_temp[1:]
    rho_temp = rho_temp[1:]
    mass_temp = mass_temp[1:]
    temp_zones = temp_zones -1
    dr = (csm_r_out/rwi)**(1.0/csm_zones)
    rw_old = csm_r_in
    mass_here = ejecta_m_out
    zones_gaussian = [0] * total_zones
    for i in range(num_zones+temp_zones,total_zones):
        rw_wind[i] = rwi * dr ** (i+1-num_zones-temp_zones)
        rho_wind[i] = m_dot/(4.0*np.pi*v_csm*(rw_wind[i]**2))
        if(rw_wind[i] >= r_i and rw_wind[i] <= r_f):
            rho_wind[i] = rho_wind[i] + (height*np.exp(-(rw_wind[i]-r_o)**2/(2*std_d**2)))
        mass_here = mass_here + (4*np.pi * rho_wind[i] * rw_wind[i]**2 * (rw_wind[i] - rw_old))/m_sun
        mass[i] = mass_here
        rw_old = rw_wind[i]
        m_csm = mass_here - ejecta_m_out
    
    # num_gaussian_zones = np.count_nonzero(zones_gaussian)
    # norm_fac = (r_f-r_i)/num_gaussian_zones
    
    # for j in zones_gaussian:
    #     if j != 0.0:
    #         rho_wind[i] = rho_wind[i] + (height*np.exp(-(rw_wind[i]-r_o)**2/(2*std_d**2)))
            
print("CSM Mass: %1.6f M_sun" % (m_csm))

##................................Writing Hydro Profile....................................##
if(write_hyd_profile):
    file1 = open(hyd_filename,"w")
    file1.write("%1.6E\t %d\t %1.6E\t %1.6E\t %1.6E\n" % (zero[0], total_zones, mass_ib[0], radius_ib[0], density_ib[0]))
    for i in range(0,num_zones):
        file1.write("%4d\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\n" % (i+1,mass_i[i],radius[i],density[i],temp[i],velocity[i],pressure[i],zeros[i],en[i],ent[i],op[i],tau[i],v_div_csound[i]))
    j = i+1
    if (adjust_density_floor):
            for i in range(j,j+temp_zones):
                file1.write("%4d\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\n" % (i+1,mass_temp[i-j],rw_temp[i-j],rho_temp[i-j],temp[-1],velocity[-1],zeros[0],zeros[0],zeros[0],zeros[0],zeros[0],zeros[0],zeros[0]))
    j = i+1
    for i in range(j,total_zones):
            file1.write("%4d\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\t %1.16E\n" % (i+1,mass[i],rw_wind[i],rho_wind[i],t_csm,v_csm,zeros[0],zeros[0],zeros[0],zeros[0],zeros[0],zeros[0],zeros[0]))

    file1.close()
##...........................................................................................##



##................................Writing Abundance Profile....................................##
#Parameters to be written in file
# mass_,dm,r_,h1,he3_he4,c12,n14,o16,ne20,na23,mg24,al27,si28,s32,ar36,ca40,fe52_54_56,skip,co56_ni56

if(write_abn_profile):
    file2 = open(abn_filename,"w")
    for i in range(0,num_zones):
        file2.write("%4d\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\n" % (i+1,mass_[i],dm[i],radius_[i],h1[i],he3_he4[i],c12[i],n14[i],o16[i],ne20[i],na23[i],mg24[i],al27[i],si28[i],s32[i],ar36[i],ca40[i],fe52_54_56[i],skip[i],co56_ni56[i]))
    j = i+1
    mass_old = mass_[-1]
    if (adjust_density_floor):
            for i in range(j,j+temp_zones):
                dm = mass_temp[i-j]-mass_old
                file2.write("%4d\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\n" % (i+1,mass_temp[i-j],dm,rw_temp[i-j],h1[-1],he3_he4[-1],c12[-1],n14[-1],o16[-1],ne20[-1],na23[-1],mg24[-1],al27[-1],si28[-1],s32[-1],ar36[-1],ca40[-1],fe52_54_56[-1],skip[-1],co56_ni56[-1]))
                mass_old = mass_temp[i-j]
    j = i+1
    for i in range(j,total_zones):
        dm = mass[i]-mass_old
        file2.write("%4d\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\t%1.8E\n" % (i+1,mass[i],dm,rw_wind[i],h1[-1],he3_he4[-1],c12[-1],n14[-1],o16[-1],ne20[-1],na23[-1],mg24[-1],al27[-1],si28[-1],s32[-1],ar36[-1],ca40[-1],fe52_54_56[-1],skip[-1],co56_ni56[-1]))
        mass_old = mass[i]
##...........................................................................................##


# ............................... Plotting ......................................#
if(plot_graph):
    mass,r,density,temp,velocity,pressure = np.loadtxt(hyd_filename,usecols=(1,2,3,4,5,6),skiprows=1,unpack = True)
    # mass_,dm,r_,h1,he3_he4,c12,n14,o16,ne20,na23,mg24,al27,si28,s32,ar36,ca40,fe52_54_56,skip,co56_ni56 = np.loadtxt(abn_filename,usecols=(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19),skiprows=1,unpack = True)


    plt.figure(figsize=(8,6))
    plt.title('Density Profile\n  $M_{csm}=%1.4fM_{\odot}$' % (m_csm))
    plt.xlabel('Radius (cm)')
    plt.ylabel('Density (g/cm^3)')
    #plt.plot(mass,density)
    # plt.plot(r,mass_gaussian(r),'o-')
    plt.loglog(r[num_zones:-1],density[num_zones:-1],'o-',label='Added CSM',color='red')
    plt.loglog(r[0:num_zones],density[0:num_zones],'*-',label='',color='black')
    # plt.plot(r[num_zones:450],density[num_zones:450],'o-',label='Added CSM',color='red')
    # plt.plot(r[390:num_zones],density[390:num_zones],'*-',label='Ejecta',color='black')
    plt.legend()
    # plt.plot(plot_r,plot_rho,'o-')
    plt.savefig("Density_profile.png")
    plt.show()
    
# ...............................................................................#