#!/usr/bin/env python

#This is an Interface to the MSR device.
#To use this the kernel module "msr" needs to be loaded.
#It gets the actual VID and FID and the target VID and FID

# Licence: GPL
# 2008,2009 cmichael/the-fallen

from time import sleep
import os, sys
###some offsets
MSR_IA32_PERF_STATUS=int(0x198)
MSR_IA32_PERF_CTL=int(0x199)
MSR_IA32_ABS_VAL=int(0xce)		#absolute Minimum(SLFM) and Maximum(IDA) Values stored here
MSR_IA32_MISC_ENABLE=int(0x1a0)		#some features are stored here - not well known to us

MSR_IA32_MISC_ENABLE=int(0x1a0)		#some features are stored here - not well known to us

MSR_FSB_FREQ=int(0xCD);			#an Index of possible FSB's is stored here

INTEL_FID_MASK = int(0x1f)		#00111111  - first 5 Bits define the FID
INTEL_DID_MASK = int(0x40)		#01000000  - 2nd highest Bit defines the DID
INTEL_HID_MASK = int(0x80)		#10000000  - highest Bit defines the HID
INTEL_VID_MASK = int(0x3f)		#bit 7 and 8 are reserved, Bits 1-6 are VID

INTEL_MISC_IDA_MASK=int(0x40)
INTEL_MISC_EIST_MASK=int(0x01)

INTEL_MSR_FSB_MASK=int(0x07)		#first three bits are intex of a FSB

READMSR_VERSION= "0.2pre-3"

"""
Table found on :

  Intel 64 and IA-32 Architectures
    Software Developers Manual
          Volume 3B:
  System Programming Guide, Part 2
"""

FSB_TABLE= {		#dict with values:   index:(CPU BUS Rate, FSB Value)
5: (100,400), 		#101 Binary
1: (133,533),		#001 Binary
3: (167,667),		#011 Binary
2: (200,800),		#010 Binary
0: (267,1067),		#000 Binary
4: (333,1333),		#100 Binary
6: (400,1600)		#110 Binary
}


class msr_interface():
	basepath = '/sys/devices/system/cpu/'
	iface_afids = 'phc_available_fids'
	iface_versn = 'phc_version'
	sysfs_maxfq = 'cpuinfo_max_freq'
	sysfs_minfq = 'cpuinfo_min_freq'
	sysfs_trlat = 'cpuinfo_transition_latency' # transition latency in nanoseconds

	def __init__(self):	
		print "MSRTOOL V"+READMSR_VERSION+" started...\n"
		if len(sys.argv) < 2:				#no parameters given - print helpline
			self.print_help()
		elif sys.argv[1] == "--cpuinfo":	#print available fids from interface
			self.prepare_run()
			self.print_cpuinfos()
		elif sys.argv[1] == "--availfids":	#print available fids from interface
			self.prepare_run()
			self.print_availfids()
		elif sys.argv[1] == "--readmsr":	#print msr data
			self.prepare_run()
			self.print_msrinfo()
		elif sys.argv[1] == "--cvolt":		#convert a given VID to a Voltage
			self.prepare_run()
			self.convert_vid() #sys.argv[2]
		elif sys.argv[1] == "--fsb":		#try to get FSB from MSR
			self.prepare_run()
			self.print_fsb()
		else:
			self.print_help()
		

	def prepare_run(self):
	#check if we meet all conditions (msr loaded, etc) and try to fix problems
	#cody partitially taken from hw_pstaty_ctrl.py by DavidG
		if not os.path.exists('/dev/cpu/0/msr'):
			print "trying to load msr module"
			try:
				print os.popen('modprobe msr').read()
			except:
				print "unable to load msr module"
			sleep(0.5)
			#check again
			if not os.path.exists('/dev/cpu/0/msr'):
				sys.exit(0)
		if not os.path.exists(self.basepath):
			print "Unable to find sysfs directory: "+self.basepath
			sys.exit(0)
			
		if os.geteuid() != 0:
			print "You need to be root to run this function. Please re-run with sudo or as root."
			sys.exit(0)



				
	def print_help(self):
		print "MSRTOOL V",READMSR_VERSION
		print "This Tool belongs to www.linux-phc.org and is licensed under GPL\n"
		print "Usage:"
		print sys.argv[0]," <function> <[arguments]>"
		print "Functions may be:"
		print "\t--cpuinfo : print information about available CPUs"
		print "\t--availfids : print out all available fids [needs phc-intel >= 0.4]"
		print "\t--readmsr : print out some interesting register values"
		#print "\t--cvolt [VID] : convert the VID to a voltage value"
		print "\t--fsb : read FSB and CPU Bus Clock rate"
		print "\t--help : print out this help"




	def print_fsb(self):
		#Read the Index of FSB from MSR
		for f in os.listdir(self.basepath):				#iterate the sysfs directory
			pathname = os.path.join(self.basepath, f)		#
       			if os.path.isdir(pathname+'/cpufreq'):		#Just to make sure its a cpu-directory
				cpustring = str(f)			#String of CPU (like "cpu0")
				cpunr=cpustring[3:]			#Number of the CPU (like "0")
				if self.cpu_have_msr(cpunr):		#msr interface found?
					try:
						msrfile = os.open("/dev/cpu/"+str(cpunr)+"/msr", os.O_RDONLY)
					except:
						print "Cannot read file \"/dev/cpu/"+str(cpunr)+"/msr. Are you root?"
						return
					os.lseek(msrfile, MSR_FSB_FREQ, 0);	##jump to where the value is
					value = os.read(msrfile, 8)			##read 1 byte
					fsb_index = (ord(value[0]) & INTEL_MSR_FSB_MASK)
					print "[cpu%s] CPU Bus Speed: %sMHz , FSB: %s" %(cpunr, FSB_TABLE[fsb_index][0], FSB_TABLE[fsb_index][1])
					os.close(msrfile)

				else:
					print "CPU "+cpustring+" is having no msr interface."
		return









	def print_availfids(self):
		for f in os.listdir(self.basepath):				#iterate the sysfs directory
			if os.path.isdir(self.basepath+f+'/cpufreq'):
				print f
				phcver = self.get_phcver(f)
				if int(phcver[0]) == 0 and int(phcver[1]) < 4:
					print "Your PHC Version is < 0.4 - the available_fids interface is not supported"
				else:
					filename = self.basepath+f+'/cpufreq/'+self.iface_afids
					if os.path.exists(filename):
						print "\VIDs: ",int(os.popen('cat '+filename).read().strip())
					else:
						print self.iface_afids+" not found. But it should be available in your phc version. Strange..."


	def convert_vid(self):
		print "Function not yet supported. "


	def print_cpuinfos(self):
		#what to display:	CPU type, CPU Date (stepping), Max Freq,
		for f in os.listdir(self.basepath):				#iterate the sysfs directory
			if os.path.isdir(self.basepath+f+'/cpufreq'):
				print f
				filename = self.basepath+f+'/cpufreq/'+self.sysfs_maxfq
				if os.path.exists(filename):
					print "\thighest frequency: ",int(os.popen('cat '+filename).read().strip())/1000,"MHz"

				filename = self.basepath+f+'/cpufreq/'+self.sysfs_minfq
				if os.path.exists(filename):
					print "\tlowest frequency: ",int(os.popen('cat '+filename).read().strip())/1000,"MHz"

				filename = self.basepath+f+'/cpufreq/'+self.sysfs_trlat
				if os.path.exists(filename):
					print "\ttransition latency: ",int(os.popen('cat '+filename).read().strip()),"ns"
					
				phcver= self.get_phcver(f)
				if phcver[3] != "" :
					print "\tPHC Version: ",phcver[0]+"."+phcver[1]+"."+phcver[2]+":"+phcver[3]
				else:
					print "\tPHC Version: ",phcver[0]+"."+phcver[1]+"."+phcver[2]
				
	def get_phcver(self, cpu):
		if os.path.isdir(self.basepath+cpu+'/cpufreq'):
			filename = self.basepath+cpu+'/cpufreq/'+self.iface_versn
			phcver=os.popen('cat '+filename).read().strip()
			phcver=phcver.split('.')
			major = phcver[0]
			minor = phcver[1]
			if phcver[2].find(':') > 0:
				revision = phcver[2].split(':')
				build=revision[1]
				revision=revision[0]
			else:	#no build version
				revision = phcver[2]
				build=""
			return [major,minor,revision,build]
			
			
	def print_msrinfo(self):
		#try to find cpus that are providing PHC interfaces
		for f in os.listdir(self.basepath):				#iterate the sysfs directory
			pathname = os.path.join(self.basepath, f)		#
       			if os.path.isdir(pathname+'/cpufreq'):		#Just to make sure its a cpu-directory
				cpustring = str(f)			#String of CPU (like "cpu0")
				cpunr=cpustring[3:]			#Number of the CPU (like "0")
				if self.cpu_have_msr(cpunr):		#msr interface found?
					msr_vals = self.read_msr(cpunr)
					self.show_data(msr_vals, cpustring)	#displaying data in a beautiful way
				else:
					print "CPU "+cpustring+" is having no msr interface."
		return


	def cpu_have_msr(self, cpunr):
		if os.path.exists("/dev/cpu/"+str(cpunr)+"/msr"):	
			return 1
		else:
			return 0


	def read_msr(self, cpu):
		msr_values={}
		try:
			msrfile = os.open("/dev/cpu/"+str(cpu)+"/msr", os.O_RDONLY)
			os.lseek(msrfile, MSR_IA32_PERF_STATUS, 0);	##jump to where current values are
			value = os.read(msrfile, 8)			##read 8 bytes
			msr_values['curV']=ord(value[0])		##current voltage Identifer
			msr_values['curF']=ord(value[1]) 		##current FID DID HID
			msr_values['hfmV']=ord(value[4])		##HFM Voltage ID
			msr_values['hfmF']=ord(value[5]) 		##HFM FID DID HID
			msr_values['lfmV']=ord(value[6])		##LFM Voltage ID
			msr_values['lfmF']=ord(value[7]) 		##LFM FID DID HID

			os.lseek(msrfile, MSR_IA32_PERF_CTL, 0);	##jump to where target values are
			value = os.read(msrfile, 8)			##read 8 bytes
			msr_values['tgtV']=ord(value[0])		##target voltage Identifer
			msr_values['tgtF']=ord(value[1])		##target FID DID HID

			os.lseek(msrfile, MSR_IA32_ABS_VAL, 0);	##jump to where target values are
			value = os.read(msrfile, 8)			##read 8 bytes
			msr_values['minV']=ord(value[0])		##absolute minimum VID
			msr_values['minF']=ord(value[1])		##absolute minimum FID DID HID
			msr_values['maxV']=ord(value[4])		##absolute minimum VID
			msr_values['maxF']=ord(value[5])		##absolute minimum FID DID HID

			os.lseek(msrfile, MSR_IA32_MISC_ENABLE, 0);	##jump to where features are
			value = os.read(msrfile, 8)			##read 8 bytes
			msr_values['EIST']=ord(value[2])		##I-EST (Enhanged Intel SpeedStep enabled?)
			msr_values['IDA']=ord(value[4])		##IDA (Intel Dynamic Accelleration enabled?)

			os.close(msrfile)
		except:
			print "Cannot read file \"/dev/cpu/"+str(cpu)+"/msr. Are you root?"
		return msr_values

	def show_data(self, msr_vals, cpustr):
 		# Displaing the data from the dictionary "msr_vals"

		print "[%s] [CURRENT] FID:%s HID:%s DID:%s VID:%s " % (
				cpustr,msr_vals['curF']&INTEL_FID_MASK, 
				int((msr_vals['curF']&INTEL_HID_MASK) > 7),
				int((msr_vals['curF']&INTEL_DID_MASK) > 7),
				msr_vals['curV'] )

		print "[%s] [TARGET]  FID:%s HID:%s DID:%s VID:%s " % (
				cpustr,msr_vals['tgtF']&INTEL_FID_MASK, 
				int((msr_vals['tgtF']&INTEL_HID_MASK) > 7),
				int((msr_vals['tgtF']&INTEL_DID_MASK) > 7),
				msr_vals['tgtV'] )

		print "[%s] [HIGHEST] FID:%s (HID:%s DID:%s) VID:%s (not sure if they exist here)" % (
				cpustr,msr_vals['hfmF']&INTEL_FID_MASK, 
				int((msr_vals['hfmF']&INTEL_HID_MASK) > 7),
				int((msr_vals['hfmF']&INTEL_DID_MASK) > 7),
				msr_vals['hfmV'] )

		print "[%s] [LOWEST]  FID:%s (HID:%s DID:%s) VID:%s (not sure if they exist here)" % (
				cpustr,msr_vals['lfmF']&INTEL_FID_MASK, 
				int((msr_vals['lfmF']&INTEL_HID_MASK) > 7),
				int((msr_vals['lfmF']&INTEL_DID_MASK) > 7),
				msr_vals['lfmV'] )

		print "[%s] [SLFM]    FID:%s VID:%s " % (
				cpustr,msr_vals['minF']&INTEL_FID_MASK, 
				msr_vals['minV'] )

		print "[%s] [IDA]     FID:%s VID:%s " % (
				cpustr,msr_vals['maxF']&INTEL_FID_MASK, 
				msr_vals['maxV'] )

		print "[%s] [CURRENTLY ACTIVE FEATURES] IDA:%s EIST:%s"%(
				cpustr, 
				int(msr_vals['IDA']&INTEL_MISC_IDA_MASK), 		#not sure about that
				int(msr_vals['EIST']&INTEL_MISC_EIST_MASK) )		#not sure about that
		print("")
msrtool = msr_interface()



