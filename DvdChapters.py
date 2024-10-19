# -*- coding: utf-8 -*-
"""
package DvdChapter.py

 Description : extract chapter from a dvd as individuals vob files

 Set of common module: including message management (to file and stdout)
 Error code began by 200
 Output:
   return Code  : 0 if ok
                  1 otherwise """
                  
__version__ = "2.0"
__date__ = "2024/19/10"
__author__ = "jmpi"

#-------------------- Import part -------------------------------------
# module importation 
#--------------------------------------------------------------------------
from sys import stdout
import sys, os.path, re, os
import easygui
import glob
import subprocess , shutil
import os, re
from os.path import basename
from unidecode import unidecode
import configparser

config = configparser.ConfigParser()
config.read('DvdChapters.cfg')
updateConfigFile = False
DVDDecrypter = ""
Destfolder = ""
DefaultDir = ""
ISO = False  # boorlan , true if input from iso file, false if dvd
src_cmd = ""
isofile = None
mounteddrive = ""
DriveList =""

try:    
    if 'PARAMETERS' not in config : 
      config['PARAMETERS'] = {}
    if 'DVDDecrypter' not in config['PARAMETERS'] or \
      not os.path.isfile(config['PARAMETERS']['DVDDecrypter']) :
        updateConfigFile = True    
        if 'DVDDecrypter' not in config['PARAMETERS']:
            prompt = subprocess.run(['where', 'DVDDecrypter'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if prompt.returncode == 0:
              DVDDecrypter = prompt.stdout.decode("utf8").strip()
            while not os.path.isfile(DVDDecrypter):
                DVDDecrypter = easygui.fileopenbox("Select DVDDecrypter Executable file", "Finding DVDDecrypter", default=os.path.join(os.environ['userprofile'], "*.exe"))

            config['PARAMETERS']['DVDDecrypter'] = DVDDecrypter 
    else:
        DVDDecrypter = config['PARAMETERS']['DVDDecrypter'] 
        

    if  'Destfolder' not in config['PARAMETERS'] or \
      not os.path.isdir(config['PARAMETERS']['Destfolder']) :
        updateConfigFile = True
        if 'Destfolder' not in config['PARAMETERS']:
           while not os.path.isdir(Destfolder):
                Destfolder = easygui.diropenbox("Select destination folder ", "Destination folder", default=os.environ['userprofile'])
            config['PARAMETERS']['Destfolder'] = Destfolder
    else:
        Destfolder = config['PARAMETERS']['Destfolder'] 
      
    if  'DefaultDir' not in config['PARAMETERS'] or \
      not os.path.isdir(config['PARAMETERS']['DefaultDir']) :
        updateConfigFile = True
        if 'DefaultDir' not in config['PARAMETERS']:
            while not os.path.isdir(DefaultDir):
                DefaultDir = easygui.diropenbox("Select default directory for search ", "Default folder", default=os.environ['userprofile'])
            config['PARAMETERS']['DefaultDir'] = DefaultDir
    else:
        DefaultDir = config['PARAMETERS']['DefaultDir'] 
    TextfileName = easygui.fileopenbox(default=DefaultDir)
    if TextfileName == None:
      raise NameError('Canceled by user')

    if updateConfigFile :     
        with open('DvdChapters.cfg', 'w') as configfile:
                config.write(configfile)            
    
    try:
      isofile = sys.argv[1]
      ISO = True
    except:
      
        choices = ["Iso file", "DVD"]
        reply = easygui.choicebox("Witch support do you want to use?", choices=choices)
    
        if reply == "Iso file":  
          isofile = easygui.fileopenbox(default=DefaultDir+'/*.iso')
          ISO = True
        elif "DVD":
            try:  
                PowerShell = 'PowerShell Get-Volume'    
                prompt = subprocess.check_output(PowerShell, shell=True)
                DriveList = [ line[0:29].strip() for line in str(prompt).split('\\n') if "CD-ROM" in line ]
                if len(DriveList) > 1:
                  choice = easygui.choicebox("Select the drive to use:", "Drive selection", DriveList)
                  if choice == None:
                      raise NameError('Canceled by user')
                  mounteddrive = choice[0] + ':\\'
                else:
                    mounteddrive = DriveList[0][0] + ':\\'
                    
            except :
                raise           
        else:
              raise NameError('Canceled by user')
    if ISO:  # ISO shall be mounted as drive for dvddecripter 
        # get list of existing drives
        before = re.findall(r"[A-Z]+:.*$", os.popen("mountvol /").read(), re.MULTILINE)
          
        # mount iso file  
        try:  
            PowerShell = 'PowerShell Mount-DiskImage ' + "'" + os.path.realpath(isofile) + "'"
            prompt = subprocess.check_output(PowerShell, shell=True)
        except :
            raise 
        # mount iso file  
               
        # use "powershell Get-Volume -DriveLetter <drive>" : to get volume name 
        after = re.findall(r"[A-Z]+:.*$", os.popen("mountvol /").read(), re.MULTILINE)
        mounteddrive = list(set(after) - set(before))[0]
        PowerShell = 'PowerShell Get-Volume   -DriveLetter ' + mounteddrive[0]
        prompt = subprocess.check_output(PowerShell, shell=True)        
        prefix = prompt.decode("utf8").split('\n')[3].split()[1]
        prefix=easygui.enterbox ("Give the prefix of vob file witch must be the title of the dvd","Prefix selection", prefix)
        if prefix == None:
            raise NameError('Canceled by user')
        Destfolder = os.path.join(os.path.dirname(isofile), os.path.splitext(os.path.basename(isofile))[0])
        if not os.path.exists(Destfolder):
            os.makedirs(Destfolder)
        
    else:
        try:  
            PowerShell = 'PowerShell Get-Volume   -DriveLetter ' + mounteddrive[0]
            prompt = subprocess.check_output(PowerShell, shell=True)
            mounteddrive = prompt.split('\n')[3].split()[0] + ':\\'
            prefix = prompt.split('\n')[3].split()[1]
            if (not prefix) or (prefix == "DVD_VIDEO") or prefix.isdigit() :
               raise NameError('No DVD in Drive')
            Destfolder = os.path.join(Destfolder, prefix)
            if not os.path.exists(Destfolder):
              os.mkdir(Destfolder)
        except :
            prefix = easygui.enterbox("File prefix to use:")  
            if prefix == None :
                raise NameError("Canceled by user")
            Destfolder = os.path.join(Destfolder, prefix)
            if not os.path.exists(Destfolder):
                os.mkdir(Destfolder)
    # extract chapters from mounted device     
    cmdline = '"'+DVDDecrypter+'"'+' /MODE IFO /SPLIT CHAPTER /SRC ' + str(mounteddrive) + ' /DEST ' + Destfolder + ' /START /CLOSE'
    print(cmdline)
    prompt = subprocess.check_output(cmdline, shell=True)
    
    if ISO:
        try:  
            PowerShell = 'PowerShell DisMount-DiskImage ' + "'" + os.path.realpath(isofile) + "'"
            prompt = subprocess.check_output(PowerShell, shell=True)
        except :
            pass 
    if 0:
        # stream info*
        StreamInfo = os.path.join(Destfolder, "VTS_01 - Stream Information.txt")
        f = open(StreamInfo, 'r+')
        AudioStreams = f.readlines()
        f.close()
        
        msg = "Which stream do we keep?"
        title = "Streams available"
        choices = AudioStreams
        Audiochoice = easygui.choicebox(msg, title, choices)
        indexAudio = AudioStreams.index(Audiochoice)
    
    VobList = glob.glob(Destfolder + r'\*.VOB')
    VobList.sort()
        
    choices = ["Text file", "Paste and Edit"]
    reply = easygui.choicebox("How do you want to give title names for " + prefix + "? (" + str(len(VobList)) + ")", choices=choices)
    if reply == None:
      raise NameError('Canceled by user')
    FileNames = ''
    if reply == "Text file":
        TextfileName = easygui.fileopenbox(default=DefaultDir+'/*.txt')
        if TextfileName == None:
            raise NameError('Canceled by user')
        f = open(TextfileName, 'r+')
        FileNames = f.readlines()
        f.close()
        if FileNames[0][0:7] == 'CHAPTER':
            FileNames = [ re.sub(r'CHAPTER\d\dNAME=\d+\.', '', (lig).strip()) for lig in FileNames if lig[9:13] == "NAME"]
    elif reply == "Paste and Edit":
        
        while len(FileNames) != len(VobList):
            if FileNames:
                easygui.msgbox("Number of titles (%d) shall match the number of vob files (%d)" % (len(FileNames), len(VobList)), 'Tracks files names')
            lines = easygui.codebox("Number of titles (%d) for <%s>" % (len(VobList),isofile))    
            FileNames = [ re.sub(r'\A\d+\s*[\.]*\s*\t*', "", unidecode(lig).strip()) for lig in lines.split('\n')]
                   
            VobList = glob.glob(Destfolder + r'\*.VOB')
            VobList.sort()
    
    else:
          raise NameError('Canceled by user')
        
    for i in range(len(FileNames)):
        vobname=os.path.join(Destfolder,prefix+"_"+re.sub(r'[^\w._]',"_",FileNames[i].strip())+".vob")
        vob=VobList[i]
        print ("Convert %s in %s" % (os.path.basename(vob),os.path.basename(vobname)))
        newname=name=os.path.join(Destfolder,prefix+"_"+str(i+1)+"_"+re.sub(r'[^\w._]',"_",FileNames[i].strip())+".vob")	
        shutil.copyfile(vob,newname )
    #[ os.remove(vobfile) for vobfile in VobList ]
    easygui.msgbox(prefix + " Terminated ok :o, see " + Destfolder)
except NameError as e :
      easygui.msgbox(e , "DvdChapter", "End")
except :
     easygui.exceptionbox()   
   
