
import sys,os.path,re,os
import easygui
import glob
import subprocess , shutil
import os, re
from os.path import basename
from unidecode import unidecode


ISO=False #boorlan , true if input from iso file, false if dvd
try:	
	
	
	try:
	  isofile=sys.argv[1]
	  ISO=True
	except:
	  
	  	choices = ["Iso file","DVD"]
	 	reply = easygui.choicebox("Witch support do you want to use?", choices=choices)
	
		if reply == "Iso file":  
		  isofile=easygui.fileopenbox()
		  ISO=True
		elif "DVD":
			try:  
				PowerShell='PowerShell Get-Volume'
				prompt=subprocess.check_output(PowerShell,shell=True)
				DriveList=[ line[0:29].strip() for line in prompt.split('\n') if "CD-ROM" in line ]
				if len(DriveList) > 1:
				  choice = easygui.choicebox("Select the drive to use:", "Drive selection", DriveList)
				  mounteddrive=choice[0]+':\\'
				else:
					mounteddrive=DriveList[0]+':\\'
					
			except :
				raise 		  
		  	#destfolder=easygui.diropenbox()
		  	destfolder='d:\\Extract'
		else:
		  	raise NameError('Canceled by user')
	if ISO:  #ISO shall be mounted as drive for dvddecripter 
		#get list of existing drives
		before=re.findall(r"[A-Z]+:.*$",os.popen("mountvol /").read(),re.MULTILINE)
		  
		# mount iso file  
		try:  
			PowerShell='PowerShell Mount-DiskImage ' + os.path.realpath(isofile)
			prompt=subprocess.check_output(PowerShell,shell=True)
		except :
			raise 
		# mount iso file  
		       
		#use "powershell Get-Volume -DriveLetter <drive>" : to get volume name 
		after=re.findall(r"[A-Z]+:.*$",os.popen("mountvol /").read(),re.MULTILINE)
		mounteddrive=list(set(after)-set(before))[0]
		PowerShell='PowerShell Get-Volume   -DriveLetter ' + mounteddrive[0]
		prompt=subprocess.check_output(PowerShell,shell=True)		
		prefix=prompt.split('\n')[3].split()[1]
			
		destfolder=os.path.join(os.path.dirname(isofile),os.path.splitext(os.path.basename(isofile))[0])
		if not os.path.exists(destfolder):
			os.makedirs(destfolder)
		try:  
			PowerShell='PowerShell DisMount-DiskImage ' + mounteddrive
			prompt=subprocess.check_output(PowerShell,shell=True)
		except :
			pass 
	else:
		try:  
			PowerShell='PowerShell Get-Volume   -DriveLetter ' + mounteddrive[0]
			prompt=subprocess.check_output(PowerShell,shell=True)
			mounteddrive=prompt.split('\n')[3].split()[0]+':\\'
			prefix=prompt.split('\n')[3].split()[1]
			if (not prefix) or (prefix == "DVD_VIDEO") or prefix.isdigit() :
			   raise NameError('No DVD in Drive')
			destfolder=os.path.join(destfolder,prefix)
			if not os.path.exists(destfolder):
			  os.mkdir(destfolder)
		except :
		    prefix=easygui.enterbox("File prefix to use:")  
		    if (not prefix) :
		    	raise NameError("Canceled by user")
		    destfolder=os.path.join(destfolder,prefix)
		    if not os.path.exists(destfolder):
				os.mkdir(destfolder)
	#extract chapters from mounted device     
	try:
	  DVDDecrypter='"C:\Program Files (x86)\Video\DVD Decrypter\DVDDecrypter.exe" /MODE IFO /SPLIT CHAPTER /SRC '+str(mounteddrive)+' /DEST '+ destfolder +' /START /CLOSE'
	  prompt=subprocess.check_output(DVDDecrypter,shell=True)
	except :
		pass   
	 
		 
	
	if 0:
		#stream info*
		StreamInfo=os.path.join(destfolder,"VTS_01 - Stream Information.txt")
		f = open(StreamInfo, 'r+')
		AudioStreams = f.readlines()
		f.close()
		
		msg ="Which stream do keep?"
		title = "Streams available"
		choices = AudioStreams
		Audiochoice = easygui.choicebox(msg, title, choices)
		indexAudio=AudioStreams.index(Audiochoice)
	
	VobList=glob.glob(destfolder+'\*.VOB')
	VobList.sort()
		
	choices = ["Text file","Paste and Edit"]
	reply = easygui.choicebox("How do you want to give title names for "+prefix+"? ("+str(len(VobList))+")", choices=choices)
	FileNames=''
	if reply == "Text file":
		TextfileName=easygui.fileopenbox()
		f = open(TextfileName, 'r+')
		FileNames = f.readlines()
		f.close()
		if FileNames[0][0:7] == 'CHAPTER':
			FileNames=[ re.sub('CHAPTER\d\dNAME=\d+\.','',(lig).strip() ) for lig in FileNames if lig[9:13]=="NAME"]
	elif reply=="Paste and Edit":
		
		while len(FileNames) != len(VobList):
			if FileNames:
				easygui.msgbox("Number of titles (%d) shall match the number of vob files (%d)" % (len(FileNames),len(VobList)),'Tracks files names')
		 	lines=easygui.codebox()	
		 	FileNames=[ re.sub('\A\d+\s*[\.]*\s*\t*',"",unidecode(lig).strip()) for lig in lines.split('\n')]
		 		  
			VobList=glob.glob(destfolder+'\*.VOB')
			VobList.sort()
	
	else:
	  	raise NameError('Canceled by user')
	  
	
	
	for i in range(len(FileNames)):
		mkvname=os.path.join(destfolder,prefix+"_"+re.sub("[^\w._]","_",FileNames[i].strip())+".mkv")
		vob=VobList[i]
		#print ("Convert %s in %s" % (os.path.basename(vob),os.path.basename(mkvname)))
		#ffmpegLine=FFMPEVobListG+" -fflags +genpts -i %s  -c:v copy -c:a copy %s" %(vob,mkvname)
		#ffmpegLine=FFMPEG+" -y  -fflags +genpts -i %s  -c:v copy -c:a %s -map 0:a:%d  %s" %(vob,Audiochoice.split()[4].lower(),indexAudio,mkvname)     
		"""ffmpegLine=FFMPEG+" -y  -fflags +genpts -i %s  -c:v copy  -c:a:%d copy %s" %(vob,indexAudio,mkvname)     
		try:
		 	prompt=subprocess.check_output(ffmpegLine,shell=True)
		except:
			raise"""
		newname=name=os.path.join(destfolder,prefix+"_"+str(i+1)+"_"+re.sub("[^\w._]","_",FileNames[i].strip())+".vob")	
		shutil.copyfile(vob,newname )
	[ os.remove(vobfile) for vobfile in VobList ]
	easygui.msgbox(prefix+" Terminated ok :o, see "+destfolder)
except :
	 easygui.exceptionbox()   