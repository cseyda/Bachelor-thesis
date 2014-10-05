#!/usr/bin/env python

#This is an Interface to the MSR device.
#To use this the kernel module "msr" needs to be loaded.
#It gets the actual VID and FID and the target VID and FID

# Licence: GPL
# 2008,2009 cmichael/the-fallen

import os, sys, tempfile, glob, re
from subprocess import *

acpi_path = "/sys/firmware/acpi/tables/"
acpi_path_old = "/proc/acpi/"

#check if root
if os.geteuid() != 0:
	print "You need to be root to run this function. Please re-run with sudo or as root."
	sys.exit( 0 )
	
#check if sys-folder for acpi is present
if not os.path.exists( acpi_path ):
	if os.path.exists( acpi_path_old ):
		acpi_path = acpi_path_old
	else:
		print "unable to find ACPI folder"
		sys.exit( 0 )

#gathering DSDT and SSDT tables
tables = list()
tables.extend( glob.glob( acpi_path + '*SSDT' ) )
tables.extend( glob.glob( acpi_path + '*DSDT' ) )

if os.path.exists( acpi_path + 'dynamic/' ):
	tables.extend( glob.glob( acpi_path + 'dynamic/SSDT*' ) )

#save all dsdt and ssdt to tmp-folder (in tempfile), compile them and save to tables
tempfile = tempfile.NamedTemporaryFile()
dc_tables = list()

for table in tables:
	cat = Popen( 'cat ' + table +' > ' + tempfile.name, shell=True, stdout=PIPE )
	cat.wait()
	Popen( 'iasl -d ' + tempfile.name, shell=True ).wait()
	f = open( tempfile.name + '.dsl' )
	#delete newlines and whitspaces
	dc_tables.append( f.read().replace(' ', '').replace( '\n', '' ) )
	f.close()
tempfile.close()

#check with regualar expression and extract the matchings
for table in dc_tables:
	m = re.findall( r'_PSS,Package\(0x03\).*?\{.*?\}\)', table, re.DOTALL )
	if m:
		for sub in m:
			p = re.findall(r'Package\(0x06\){(\w+),(\w+),(\w+),(\w+),(\w+),(\w+)\}', sub, re.DOTALL )
			for tuple in p:
				print 'f:\t' + tuple[0] + "(hex) = " + str( int( tuple[0], 16 ) )
				print 'P:\t' + tuple[1] + "(hex) = " + str( int( tuple[1], 16 ) )
				
				print 'v/f id:\t' + tuple[4]
				print 'vid:\t' + tuple[4][-2:] + "(hex) = " + str( int( tuple[4][-2:], 16 ) )#last 2
				print 'fid:\t' + tuple[4][-4:-2] + "(hex) = " + str( int( tuple[4][-4:-2], 16 ) )#last 4-2
				
				print '\n'
	
#search for
#Name (_PSS, Package (0x03)
#        { *  })

# and then:
#Package (0x06)
#{
#	0x00000535, 
#	0x00004E20, 
#	0x0000000A, 
#	0x0000000A, 
#	0x0000081C, 
#	0x0000081C
#}
