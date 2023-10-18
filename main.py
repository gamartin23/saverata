import os
import subprocess
import customtkinter as ct
import CTkMessagebox
import sys
import tkinter as tk
from tkinter import *
from tkinter import filedialog, WORD, CHAR
from PIL import Image
from time import sleep
from datetime import datetime
import shutil
import textwrap
import uuid
import traceback
import random

class gui(): #Should be only gui, with all functions in another file and called via saverata.func() but i dont know how pyinstaller handles that
    def __init__(self): #Careful here
        self.consistency=1 #Consistency was deprecated but it is useful when debugging issues present on live. It counts how many times the repo view was re-rendered
        
        ###This block defines a TEAM ID. TEAM ID defines different paths for usage with Virtual machines, where extracted save data can be uploaded to for network usage.
        
        #with open('c:/kovatools/saverata/team.kova','r') as co:
            #self.country=co.read() #This serves team identification purposes, can be changed to team identifiers and deployed with a different TID. Was self.country in the original code but im too lazy to modify it. Disable if needed.
        #print(f'Country code: {self.country}')
        #Depending on the Country or Team ID, different Remote addresses are provided.
        #if self.country=='1':
            #self.vm = r'Team 1 save folder'
            #self.vmsf = r'Team 1 staggered save folder'
        #elif self.country=='2':
            #self.vm = r'Team 2 save folder'
            #self.vmsf = r'Team 2 staggered save folder'
        #print(f'\n===VM Dir===\nGeneral: {self.vm}\nFixed saves: {self.vmsf}\n')
        
        ###
        
        self.savesDir = r'C:/Saves'
        if not os.path.exists(self.savesDir):
            os.makedirs(self.savesDir)
        self.expanded = False #Chinbar status
        
        pathlist=os.getenv("PATH").split(':')
        for el in pathlist:
            if 'CommandLineTools' not in el:
                self.notpath=True
            else:
                self.notpath=False 
                print(f'SDK found in %PATH% at: {el}')
                break
            
        self.notpath=True #disable for shipping// Forces GUI and workarounds for non-path runs
        if self.notpath==True:
            self.toolsDirDir = r'C:/Kovatools/toolsdir.txt' #SDK location for non-path runs gets tored here
            try:
                with open(self.toolsDirDir,'r') as f:
                    self.toolsDir=f.read()
                    self.toolsDir=f'{self.toolsDir}/'
                    print(f'SDK manually set at: {self.toolsDir}')
            except Exception as e:
                print(e)
                traceback.print_exc()
                self.toolsDir = r'C:\Nintendo\SDK1610\NintendoSDK\Tools\CommandLineTools'
                with open(self.toolsDirDir,'w') as fnw:
                    fnw.write(self.toolsDir)
        else:
            self.notpath=False
            self.toolsDir=''  
        print(f'Manual SDK directory input: {self.notpath}')     
        
        self.targetCache = r'C:/Kovatools/target.kova' #This is where the Target Name gets stored
        if os.path.isfile(self.targetCache):
            pass
        else:
            with open(self.targetCache,'w') as fnw:
                fnw.write('')
                
        self.frames=[]
        self.frameId=0
        self.fileNameList = []
        self.descFileList = []
        self.window = ct.CTk()
        try:
            with open('version.kova','r') as f: #version.kova serves update purposes for usage with KovaUpdater 1.2, which is an internal usage only tool. Guess this code just defines the title bar now.
                raw=f.read()
                self.version=f'{raw[0]}.{raw[1:]}'
        except:
            traceback.print_exc()
            version = 'No version file found'
        self.window.title(f'SaveRata {self.version}')
        self.window.resizable(False,False)
        self.window.iconbitmap(self.resourcePath('saverata.ico'))
               
        
        self.mainFrame = ct.CTkFrame(self.window)
        self.mainFrame.grid(row=0,column=0,pady=5,padx=5)
        
        self.underFrame = ct.CTkFrame(self.mainFrame)
        
        self.leftFrame = ct.CTkFrame(self.mainFrame,width=200,fg_color='#4aa5c7')
        self.leftFrame.grid(row=0,column=0,pady=5,padx=5)
        self.leftFrame.grid_rowconfigure((0,1,2,3,4,5,6), weight=1, uniform="column")
        self.importSave = ct.CTkButton(self.leftFrame,text='Extract save',command=lambda: self.importFromConsole(0),width=200)
        self.importSave.grid(row=0,column=0,pady=5,padx=5)
        self.importSave = ct.CTkButton(self.leftFrame,text='Extract fixed save',command=lambda: self.importFromConsole(1),width=200)
        self.importSave.grid(row=1,column=0,pady=5,padx=5)
        self.openFolder = ct.CTkButton(self.leftFrame,text='Open saves folder',command=self.startfolder,width=200)
        self.openFolder.grid(row=2,column=0,pady=5,padx=5)
        ###This block defines the button for the VM GUI. In the VM GUI, the user can see and download all the save data folders uploaded to a certain folder in a Virtual Machine. Enable it or disable it as you prefer
        #self.addSave = ct.CTkButton(self.leftFrame,text='Download save',width=200,command=self.downloadFromVm)
        #self.addSave.grid(row=3,column=0,pady=5,padx=5)     
        self.underFrame.grid_columnconfigure((0,1,2,3,4,5), weight=1, uniform="column")
        if self.notpath:
            self.deleteAll = ct.CTkButton(self.underFrame,text='Delete all save data',command=self.deleteAllSaveData,width=150,fg_color='#292828',border_color='#525252',hover_color='#3b3b3b',border_width=4,height=36)
            self.deleteAll.grid(row=0,column=0,pady=5,padx=5,sticky=EW)
            self.gen1 = ct.CTkButton(self.underFrame,text='Switch kit to Gen 1',command=self.switchToGen1,width=150,fg_color='#292828',border_color='#525252',hover_color='#3b3b3b',border_width=4,height=36)
            self.gen1.grid(row=0,column=1,pady=5,padx=5,sticky=EW)
            self.gen1 = ct.CTkButton(self.underFrame,text='Switch kit to Gen 2',command=self.switchToGen2,width=150,fg_color='#292828',border_color='#525252',hover_color='#3b3b3b',border_width=4,height=36)
            self.gen1.grid(row=0,column=2,pady=5,padx=5,sticky=EW)
            # self.sendAllToVM=ct.CTkButton(self.underFrame,text='Send all saves to VM',command=self.addToVm,width=160,fg_color='#292828',border_color='#525252',hover_color='#3b3b3b',border_width=4,height=36)
            # self.sendAllToVM.grid(row=0,column=3,pady=5,padx=5,sticky=EW)
            self.importfromzipButton=ct.CTkButton(self.underFrame,text='Import from .zip',command=self.importFromZip,width=150,fg_color='#292828',border_color='#525252',hover_color='#3b3b3b',border_width=4,height=36)
            self.importfromzipButton.grid(row=0,column=3,pady=5,padx=5,sticky=EW)
            self.changeToolDir = ct.CTkButton(self.underFrame,text='Change SDK folder',command=self.changeDir,width=150,fg_color='#292828',border_color='#525252',hover_color='#3b3b3b',border_width=4,height=36)
            self.changeToolDir.grid(row=0,column=4,pady=5,padx=5,sticky=EW)
            self.labelAskDir = ct.CTkLabel(self.underFrame,text='Set the path to your CommandLineTools folder')
            self.entryAskDir = ct.CTkEntry(self.underFrame,placeholder_text='C:/Nintendo/SDK1610/NintendoSDK/Tools/CommandLineTools')
            self.sendDir = ct.CTkButton(self.underFrame,text='Ok',command=self.setNewDir,height=35)
            self.about = ct.CTkButton(self.underFrame,text='About',command=self.aboutWindow,width=50,fg_color='#292828',border_color='#525252',hover_color='#3b3b3b',border_width=4,height=36)
            self.about.grid(row=0,column=5,pady=5,padx=5,sticky=EW)
        else:
            self.deleteAll = ct.CTkButton(self.underFrame,text='Delete all save data',command=self.deleteAllSaveData,width=190,fg_color='#292828',border_color='#525252',hover_color='#3b3b3b',border_width=4,height=36)
            self.deleteAll.grid(row=0,column=0,pady=5,padx=5,sticky=EW)
            self.gen1 = ct.CTkButton(self.underFrame,text='Switch kit to Gen 1',command=self.switchToGen1,width=190,fg_color='#292828',border_color='#525252',hover_color='#3b3b3b',border_width=4,height=36)
            self.gen1.grid(row=0,column=1,pady=5,padx=5,sticky=EW)
            self.gen1 = ct.CTkButton(self.underFrame,text='Switch kit to Gen 2',command=self.switchToGen2,width=190,fg_color='#292828',border_color='#525252',hover_color='#3b3b3b',border_width=4,height=36)
            self.gen1.grid(row=0,column=2,pady=5,padx=5,sticky=EW)
            #self.sendAllToVM=ct.CTkButton(self.underFrame,text='Send all saves to VM',command=self.addToVm,width=200,fg_color='#292828',border_color='#525252',hover_color='#3b3b3b',border_width=4,height=36)
            #self.sendAllToVM.grid(row=0,column=3,pady=5,padx=5,sticky=EW)
            self.importfromzipButton=ct.CTkButton(self.underFrame,text='Import from .zip',command=self.importFromZip,width=190,fg_color='#292828',border_color='#525252',hover_color='#3b3b3b',border_width=4,height=36)
            self.importfromzipButton.grid(row=0,column=3,pady=5,padx=5,sticky=EW)
            self.about = ct.CTkButton(self.underFrame,text='About',command=self.aboutWindow,width=50,fg_color='#292828',border_color='#525252',hover_color='#3b3b3b',border_width=4,height=36)
            self.about.grid(row=0,column=4,pady=5,padx=5,sticky=EW)

        
        
        self.powercontrol = ct.CTkSegmentedButton(self.leftFrame,values=['Power on','Shutdown'],command=self.powerSwitch,width=200,selected_color='#149911',selected_hover_color='#014400',dynamic_resizing=False)
        self.powercontrol.grid(row=5,column=0,padx=5,pady=5)
        self.update = ct.CTkButton(self.leftFrame,text='Update',command=self.loadSavesFromFolder,width=200)
        self.update.grid(row=6,column=0,padx=5,pady=5)
        
        self.middleFrame = ct.CTkFrame(self.mainFrame)
        self.middleFrame.grid(row=0,column=1,padx=5,pady=5)
        self.backupShower = ct.CTkSegmentedButton(self.middleFrame,values=['Saves','Backups'],command=self.switchtobackups,width=200,dynamic_resizing=False) #Whenever you delete save data or upload new save data to the console, a backup is created. Alternate between Saves and Backups with this nifty button.
        self.backupShower.grid(row=0,column=0,pady=(5,0),padx=5)
        self.savesF = ct.CTkScrollableFrame(self.middleFrame,width=440,height=240)
        #self.savesF.grid(row=0,column=0,pady=5,padx=5) #do not enable this one here.
        
        self.rightFrame = ct.CTkFrame(self.mainFrame,fg_color='#d14b50')
        self.rightFrame.grid(row=0,column=2,pady=5,padx=5)
        self.saveasd = ct.CTkLabel(self.rightFrame,text='Save selected: None',font=('helvetica',11,'bold'))
        self.saveasd.grid(row=0,column=0,pady=5,padx=3)
        self.aboutSaveF = ct.CTkTextbox(self.rightFrame,height=100)
        self.aboutSaveF.grid(row=1,column=0,pady=5,padx=5)
        self.aboutSaveF.insert(1.0,'Save descriptions go here')
        self.modifyDescription = ct.CTkButton(self.rightFrame,width=200,fg_color='#ab1b11',hover_color='#cc493f',text='Modify description',command=self.modDesc)
        self.modifyDescription.grid(row=2,column=0,pady=5,padx=5)
        self.targetName = ct.CTkEntry(self.rightFrame,placeholder_text='Target name',width=200)
        self.targetName.grid(row=3,column=0,pady=5,padx=5)
        self.sendToConsole = ct.CTkButton(self.rightFrame,text='Send to Console',width=200,height=40,fg_color='#8a0005',hover_color='#52191b',font=('helvetica',18,'bold'),text_color='#ffffff',command=self.sendToConsoleSave)
        self.sendToConsole.grid(row=4,column=0,pady=5,padx=5)
        self.sendToConsole.configure(state='disabled')
        
        self.expander = ct.CTkButton(self.mainFrame,text='▼',command=self.expandDown,fg_color='#292828',border_color='#525252',hover_color='#3b3b3b',border_width=4,height=22)
        self.expander.grid(row=1,column=1,pady=0,padx=4)
        
        if os.path.exists(self.targetCache):
            with open(self.targetCache,'r') as f:
                self.targetName.insert(0,f'{f.read()}')
        else:
            with open(self.targetCache,'w') as f:
                f.write('')
                f.close()
        self.backupShower.set('Saves')
        self.loadSavesFromFolder()
        self.powercontrol.set('Power on')
        
        
        self.window.mainloop()       

    def aboutWindow(self):
        aboutR=ct.CTkToplevel()
        ws=self.window.winfo_screenwidth()
        hs=self.window.winfo_screenheight()
        ws=(ws/2)
        hs=(hs/2)
        c=(ws-150)
        d=(hs-100)
        aboutR.geometry('%dx%d+%d+%d' % (300, 220, c, d))
        aboutR.resizable(False,False)
        randomIQ=random.randint(12,112)
        aboutR.iconbitmap(default='saverata.ico')
        aboutR.title(f'About SaveRata {self.version}')
        letrita=('Helvetica',11)
        labelabout=ct.CTkLabel(master=aboutR,text='Tool made with love in Tucumán.\nCode and UI by Kovadev.\nBatch magic by Lucho Abad')
        labelabout.pack(pady=5,padx=5,side=TOP)        
        aboutRF=ct.CTkFrame(master=aboutR)
        aboutRF.pack(pady=2,padx=2)    
        imageLica=ct.CTkImage(dark_image=Image.open('appicon.png'),size=(70,70))
        buttonimgLica=ct.CTkButton(master=aboutRF,image=imageLica,text='',border_width=0,hover_color='#242424',fg_color='#242424',border_color='#242424',border_spacing=2,width=70)
        buttonimgLica.pack(pady=2,padx=2,side=RIGHT)
        imageKova=ct.CTkImage(dark_image=Image.open('img/kovasp.png'),size=(70,70))
        buttonimgKova=ct.CTkButton(master=aboutRF,image=imageKova,text='',border_width=0,hover_color='#242424',fg_color='#242424',border_color='#242424',border_spacing=2,width=70)
        buttonimgKova.pack(pady=2,padx=2,side=LEFT)
        labelabout2=ct.CTkLabel(master=aboutR,text=f'Kova tools. -{randomIQ} IQ',font=(letrita))
        labelabout2.pack(pady=5,padx=5)
        buttonok=ct.CTkButton(master=aboutR,text='Ok',command=aboutR.destroy)
        buttonok.pack(pady=5,padx=5)
        aboutR.attributes('-topmost',True)
        aboutR.update()
    
    def switchtobackups(self,*args): #Changes Repository view from /Saves to /Saves/Backup
        if self.backupShower.get()=='Saves':
            self.savesDir=r'C:/Saves'
            self.loadSavesFromFolder()
        elif self.backupShower.get()=='Backups':
            self.savesDir=r'C:/Saves/Backup'
            self.loadSavesFromFolder()
        
    def resourcePath(self, relativePath): #Internal function that changes absolute paths into relative paths for image handling
            basePath=getattr(sys,'_MEIPASS',os.path.dirname(os.path.abspath(__file__)))
            return os.path.join(basePath,relativePath)
        
    def startfolder(self): #Opens Saves folder
        os.startfile(self.savesDir)
    
    def loadSavesFromFolder(self): #This is the main loop for showing each line in the repository view
        self.consistency+=1
        print(f'Table frames consistency value: {self.consistency}')
        try:
            with open(self.targetCache,'w') as f:
                f.write(self.targetName.get())
        except:
            traceback.print_exc()
            pass
        self.frames=[]
        self.frameId=0
        self.fileNameList = []
        self.descFileList = []
        self.saveasd.configure(text='Save selected: None')
        self.savesF = ct.CTkScrollableFrame(self.middleFrame,width=450,height=215,)
        self.savesF.grid(row=1,column=0,pady=5,padx=5)
        self.savesF.grid_rowconfigure(0,minsize=0)
        self.savesF.grid_columnconfigure((0,),pad=45, weight=1, uniform="column")
        ### This is not really needed but if you wanna use it, do it.
        #self.spacerText = ct.CTkLabel(self.savesF,text='\t\t\t\t\t\t\t\t\t\t\t\t\t\t',font=('helvetica',2),height=1)
        #self.spacerText.grid(row=0,column=0,pady=0,padx=5)
        self.aboutSaveF = ct.CTkTextbox(self.rightFrame,height=100)
        self.aboutSaveF.grid(row=1,column=0,pady=5,padx=5)
        self.aboutSaveF.insert(1.0,'Save descriptions go here')
        if self.backupShower.get() == 'Saves':
            for (parent_dirpath, dirnames, filenames) in os.walk(self.savesDir):
                for folder in dirnames:
                    fullpath = os.path.join(parent_dirpath, folder)
                    if os.path.isdir(fullpath) and 'Backup' not in fullpath:
                        if 'BackupSaveData' in os.listdir(fullpath):
                            self.fileNameList.append(fullpath)
                            for file in os.listdir(fullpath):
                                if file.endswith('txt'):
                                    pathtxt=str(os.path.join(self.savesDir, folder, file))
                                    pathtxt=pathtxt.replace('\\','/')
                                    with open(pathtxt, 'r') as f:
                                        text = f.read()
                                        if text == '':
                                            self.descFileList.append('No description provided')
                                        else:
                                            self.descFileList.append(text)
                            if len(self.fileNameList) > len(self.descFileList):
                                self.descFileList.append('No description file provided')
        elif self.backupShower.get() == 'Backups':
            for (parent_dirpath, dirnames, filenames) in os.walk(self.savesDir):
                for folder in dirnames:
                    fullpath = os.path.join(parent_dirpath, folder)
                    if os.path.isdir(fullpath):
                        if 'BackupSaveData' in os.listdir(fullpath):
                            self.fileNameList.append(fullpath)
                            for file in os.listdir(fullpath):
                                if file.endswith('txt'):
                                    pathtxt=str(os.path.join(self.savesDir, folder, file))
                                    pathtxt=pathtxt.replace('\\','/')
                                    with open(pathtxt, 'r') as f:
                                        text = f.read()
                                        if text == '':
                                            self.descFileList.append('No description provided')
                                        else:
                                            self.descFileList.append(text)
                            if len(self.fileNameList) > len(self.descFileList):
                                self.descFileList.append('No description file provided')
        for item in self.fileNameList:
            frame = FrameTemplate(self.savesF,self.frameId,self.fileNameList,self.descFileList,self)
            self.frames.append(frame)
            self.frameId += 1
            
    def open(self,content,saveToLoad, idToClick, button): #Handles clicks on the Open button per line in repo view
        self.aboutSaveF.delete(0.0,END)
        self.aboutSaveF.insert(1.0,f'{(content.rstrip())}')
        self.sendToConsole.configure(state='normal',border_color='#ff0008',border_width=4)
        self.whatDoISend=saveToLoad
        self.saveasd.configure(text=f'{self.wrapThisShit(str(os.path.basename(self.whatDoISend)))}')
    
    def openVm(self,content,saveToLoad): #Handles what self.open handles, but on the VM side
        self.frameDescription.delete(0.0,END)
        self.frameDescription.insert(1.0,f'{content}')
        self.whatDoIdownload=saveToLoad
        
    def sendToConsoleSave(self): #Exports selected save to the console. Should use self.whatDoISend as an argument, but since it's in self, why add code when few code do job
        print(f'Sending {self.whatDoISend} to console')
        with open(self.targetCache,'w') as f:
            f.write(self.targetName.get())
        
        #this is the part where the console gets a backup save 
        now = datetime.now()
        nowf = now.strftime("%m-%d-%y %H-%M")
        id = uuid.uuid4().hex[:4]
        savebu = f'C:/Saves/Backup/BU {nowf}_{id}'    
        cmd1 = f'{self.toolsDir}BackupSaveData.exe'
        cmd2 = f'export "{savebu}" --target {self.targetName.get()}'
        cm3= f'{cmd1} {cmd2}'
        print(f'Will execute: {cmd1, cmd2}')
        if self.connectToConsole():
            subprocess.call(cm3)     
            descriptionFile = f'{savebu}/desc.txt'
            with open(descriptionFile,'w') as f:
                f.write(f'{savebu} || \n Backup savedata generated on {nowf}\nUSDID:{id}')       
            
            #check 4 multiple accounts on the save and compare with the console accounts
            accountsSaveData = f'{self.whatDoISend}/BackupSavedata/account.xml'
            modifiedAcc=[]
            with open(accountsSaveData,'r') as initial:
                temporalAcc = initial.readlines()
                modifiedAcc.append(temporalAcc[0])
                modifiedAcc.append(temporalAcc[1])
                modifiedAcc.append(temporalAcc[2])
                modifiedAcc.append(temporalAcc[-1])
            modifiedAccStr = ''.join(modifiedAcc)
            with open(accountsSaveData,'w') as final:
                final.write(modifiedAccStr)
                
            #this is the part where the console gets the juicy rata
            cmd1 = f'{self.toolsDir}BackupSaveData.exe'
            cmd2 = f'import "{self.whatDoISend}" --target {self.targetName.get()} --follow-exist-account'
            cm3= f'{cmd1} {cmd2}'
            print(f'Will execute: {cmd1, cmd2}')
            subprocess.call(cm3)
        else:
            connectionErrorNX=CTkMessagebox.CTkMessagebox(title='NX Devkit not connected',message='Console is not connected. Maybe the Console is not connected, or the Target Name is incorrect?',icon='cancel')
              
    def connectToConsole(self): #Target connection check
        cm3=f'{self.toolsDir}ControlTarget.exe connect -t {self.targetName.get()} -v --timeout 5'
        output = subprocess.run(cm3)
        if output.returncode== 0:
            return True
        else:
            return False
    
    def importFromConsole(self,ind): #Extracts savedata from the console, to a generated folder
        ### Argument "ind" is a modifier. You can create buttons or routines that feed a different ind value to vary the behaviour of this function. I guess that's obvious but i'm just saying.
        self.saveNewSave = r'C:\Saves'
        folder = filedialog.askdirectory(initialdir=self.saveNewSave)
        saveid=uuid.uuid4().hex[:4]
        print(f'Is Fixed: {bool(ind)}')
        self.saveNewRemoteSave=f'VM/{os.path.basename(folder)}' #Replace "VM" with the shared folder path (or mounted drive path) to the VM folder where you want to upload the save after local extraction
        with open(self.targetCache,'w') as f:
            f.write(self.targetName.get())
        cmd1 = f'{self.toolsDir}BackupSaveData.exe'
        cmd2 = f'export "{folder}" --target {self.targetName.get()}'
        cm3= f'{cmd1} {cmd2}'
        #cm3=f'{cmd1}'
        if folder != '':
            print(f'Will execute: {cmd1, cmd2}')
            if self.connectToConsole():
                subprocess.call(cm3)
                self.saveZip(folder)
                self.makeDescription(folder,ind)
                descriptionMaybe=CTkMessagebox.CTkMessagebox(title='Save extracted',message='SaveData has been successfully extracted',icon='check',option_1='Edit description',option_2='No, thanks')
                if descriptionMaybe.get()=='Edit description':
                    os.startfile(f'{folder}/desc.txt')
                else:
                    pass
                ###Disable this in case there's no VM.
                # try:
                #     shutil.copytree(folder,self.saveNewRemoteSave,dirs_exist_ok=True)
                # except Exception as e:
                #     print(e)
                #     traceback.print_exc()
                self.loadSavesFromFolder()
            else:
                connectionErrorNX=CTkMessagebox.CTkMessagebox(title='NX Devkit not connected',message='Console is not connected. Maybe the Console is not connected, or the Target Name is incorrect?',icon='cancel')
        else:
            self.loadSavesFromFolder()
            pass
              
    def makeDescription(self,folder,ind): #Creates a desc.txt file
        descriptionFile = f'{folder}/desc.txt'
        if ind==0:
            with open(descriptionFile,'w') as f:
                f.write(os.path.basename(folder))
        else:
            with open(descriptionFile,'w') as f:
                f.write(f'[FIXED SAVE] {os.path.basename(folder)}')
    
    def deleteAllSaveData(self): #Sends delete all save data command to target
        cmd1= f'{self.toolsDir}ControlTarget.exe'
        cmd2= f'delete-all-savedata'
        cm3= f'{cmd1} {cmd2}'
        confirmation = CTkMessagebox.CTkMessagebox(title='Delete save data',message='Delete save data? Please make sure you have backed up all important saves before doing this',icon='warning',option_1='Yes, delete save data',option_2='No',option_3='Save data and delete')
        if confirmation.get()=='Save data and delete':
            self.importFromConsole()
            print(f'Will execute: {cmd1,cmd2}')
            if self.connectToConsole():
                subprocess.call(cm3)
            else:
                connectionErrorNX=CTkMessagebox.CTkMessagebox(title='NX Devkit not connected',message='Console is not connected. Maybe the Console is not connected, or the Target Name is incorrect?',icon='cancel')
        elif confirmation.get()=='Yes, delete save data':
            print(f'Will execute: {cmd1,cmd2}')
            if self.connectToConsole():
                subprocess.call(cm3)
            else:
                connectionErrorNX=CTkMessagebox.CTkMessagebox(title='NX Devkit not connected',message='Console is not connected. Maybe the Console is not connected, or the Target Name is incorrect?',icon='cancel')
              
    def switchToGen2(self): #Switchs NX kit to gen2
        cmd1=f'{self.toolsDir}ControlTarget.exe'
        cmd2=f'set-target-htc-generation --generation 2'
        cm3=f'{cmd1} {cmd2}'
        print(f'Will execute: {cmd1,cmd2}')
        if self.connectToConsole():
            subprocess.call(cm3)
            confirmation = CTkMessagebox.CTkMessagebox(title='Gen 1',message='Kit successfully switched to Gen 2',icon='check')
        else:
            connectionErrorNX=CTkMessagebox.CTkMessagebox(title='NX Devkit not connected',message='Console is not connected. Maybe the Console is not connected, or the Target Name is incorrect?',icon='cancel')
        
    def switchToGen1(self): #Switchs NX kit to gen1
        cmd1=f'{self.toolsDir}ControlTarget.exe'
        cmd2=f'set-target-htc-generation --generation 1'
        cm3=f'{cmd1} {cmd2}'
        print(f'Will execute: {cmd1,cmd2}')
        if self.connectToConsole():
            subprocess.call(cm3)
            confirmation = CTkMessagebox.CTkMessagebox(title='Gen 2',message='Kit successfully switched to Gen 1',icon='check')
        else:
            connectionErrorNX=CTkMessagebox.CTkMessagebox(title='NX Devkit not connected',message='Console is not connected. Maybe the Console is not connected, or the Target Name is incorrect?',icon='cancel')
    
    def expandDown(self): #Handles lower chinbar for main GUI
        if self.expanded:
            self.underFrame.grid_forget()
            self.expanded=False
        else:
            self.underFrame.grid(row=2,column=0,pady=7,padx=5,columnspan=3,sticky=EW)
            self.underFrame.grid_columnconfigure((0,1,2), weight=1, uniform="column")
            self.expanded=True

    def changeDir(self): #Change self.toolsDir
        self.labelAskDir.grid(row=2,column=0,pady=3,padx=25,columnspan=5)
        self.entryAskDir.grid(row=3,column=0,pady=8,padx=15,sticky=EW,columnspan=5)
        self.sendDir.grid(row=4,column=0,pady=3,padx=3,columnspan=5)
    
    def setNewDir(self): #Was deprecated in favour of %path%, now it's back in action. Works with self.changeDir
        print(f'Old directory: {self.toolsDir}')
        self.toolsDir=f'{self.entryAskDir.get()}'
        print(f'New directory set to: {self.toolsDir}')
        try:
            with open(self.toolsDirDir,'w') as f:
                f.write(self.toolsDir)
            self.labelAskDir.grid_forget()
            self.entryAskDir.grid_forget()
            self.sendDir.grid_forget()
            self.expandDown()
            with open(self.toolsDirDir,'r') as f:
                self.toolsDir=f'{f.read()}/'
        except Exception as e:
            print(e)
            traceback.print_exc()
        
    def saveZip(self,folder): #Generates zip
        print(f'Will zip: {folder}')
        shutil.make_archive(f'C:/Saves/Zip/{os.path.basename(folder)}', 'zip', folder)
        
    def importFromZip(self): #Import save from zip file. Basically extracts it in a subdir of self.saves
        self.saveNewSave = r'C:\Saves'
        file = filedialog.askopenfile(filetypes=[("Zip files", "*.zip")],initialdir=self.saveNewSave)
        print(f'Unzipping: {file.name}')
        finalpath = f'{self.saveNewSave}/{os.path.basename(file.name)[:-4]}'
        shutil.unpack_archive(file.name,finalpath)
        self.loadSavesFromFolder()
      
    def powerSwitch(self,*args): #Handles power toggle for NX kits, works best on SDEV kits since other kits cannot be remotely turned on
        if self.powercontrol.get()=='Power on':
            cmd=f'{self.toolsDir}TargetShell.exe power-on --name={self.targetName.get()}'
            if self.connectToConsole():
                subprocess.call(cmd)
                self.powercontrol.configure(selected_color='#149911',selected_hover_color='#014400')
            else:
                connectionErrorNX=CTkMessagebox.CTkMessagebox(title='NX Devkit not connected',message='Console is not connected. Maybe the Console is not connected, or the Target Name is incorrect?',icon='cancel')
        elif self.powercontrol.get()=='Shutdown':
            cmd=f'{self.toolsDir}TargetShell.exe power-off --name={self.targetName.get()}'
            sure=CTkMessagebox.CTkMessagebox(title='Power off',message='Shut console down?',icon='cancel',option_1='Yes',option_2='No')
            if sure.get()=='Yes':
                if self.connectToConsole():
                    subprocess.call(cmd)
                    self.powercontrol.configure(selected_color='#bb1411',selected_hover_color='#440100')
                else:
                    connectionErrorNX=CTkMessagebox.CTkMessagebox(title='NX Devkit not connected',message='Console is not connected. Maybe the Console is not connected, or the Target Name is incorrect?',icon='cancel')
            else:
                pass

    def downloadFromVm(self): #Handles VM saves view GUI
        self.filterVm = ct.CTk()
        self.filterVm.title(f'Save download')
        self.filterVm.resizable(False,False)
        self.filterVm.iconbitmap(self.resourcePath('saverata.ico'))
        
        self.vmMain = ct.CTkFrame(self.filterVm)
        self.vmMain.grid(row=0,column=0,pady=5,padx=5)
        
        self.leftvm = ct.CTkFrame(self.vmMain,width=800)
        self.leftvm.grid(row=0,column=0,pady=5,padx=5)
        self.labelFiltro = ct.CTkLabel(self.leftvm,text='Filter SaveData by text:')
        self.labelFiltro.grid(row=0,column=0,pady=(5,0),padx=5,columnspan=2)
        self.filtroframe = ct.CTkFrame(self.leftvm)
        self.filtroframe.grid(row=1,column=0,pady=1,padx=1)
        self.entryFiltro = ct.CTkEntry(self.filtroframe,width=200)
        self.entryFiltro.grid(row=0,column=0,pady=5,padx=5)
        self.sendFiltro = ct.CTkButton(self.filtroframe,text=f'{chr(0x1F50D)}',width=80,font=('helvetica',16),command=self.showSavesFromVm)
        self.sendFiltro.grid(row=0,column=1,pady=5,padx=5)
        self.saveTipo = ct.CTkSegmentedButton(self.leftvm,values=['General','Fixed saves'],command=self.showSavesFromVm)
        self.saveTipo.grid(row=2,column=0,columnspan=2,pady=5,padx=5)
        
        self.middlevm = ct.CTkFrame(self.vmMain)
        self.middlevm.grid(row=1,column=0,pady=5,padx=5)
        self.listOfRemoteSaves = ct.CTkScrollableFrame(self.middlevm,width=380)
        
        self.rightvm = ct.CTkFrame(self.vmMain)
        self.rightvm.grid(row=2,column=0,pady=5,padx=5)
        self.descriptionLabel = ct.CTkLabel(self.rightvm,text='Description')
        self.descriptionLabel.grid(row=0,column=0,pady=5,padx=5)
        self.frameDescription = ct.CTkTextbox(self.rightvm,height=150,width=400)
        self.frameDescription.grid(row=1,column=0,pady=5,padx=5)
        self.downloadButton = ct.CTkButton(self.rightvm,text='Download',font=('helvetica',13,'bold'),command=self.downloadSaveDataFromVm)
        self.downloadButton.grid(row=2,column=0,pady=5,padx=5)
        self.saveTipo.set('General')
        self.frameDescription.insert(1.0,'No file selected')
        self.showSavesFromVm(self.entryFiltro.get())
        self.filterVm.mainloop()

    def downloadSaveDataFromVm(self): #Downloads selected save from VM
        print(f'Will download: {self.whatDoIdownload}')
        finaldst = f'{os.path.join(self.savesDir,os.path.basename(self.whatDoIdownload))}'
        shutil.copytree(self.whatDoIdownload,finaldst,dirs_exist_ok=True)
        confirmed=CTkMessagebox.CTkMessagebox(title='Copy completed',message=f'SaveData has been downloaded to {finaldst}',icon='check')
    
    def ignore(self,path,contents): #I dont know why i made a container function with this, but it works and feeding the list directly to the method doesnt.
        return ['Backup','Zip']
    
    def addToVm(self): #Send all saves from self.savesDir to local VM, ignoring whats returned by self.ignore
        shutil.copytree(self.savesDir,self.vm,dirs_exist_ok=True,ignore=self.ignore)
        confirmed=CTkMessagebox.CTkMessagebox(title='Copy completed',message=f'SaveData has been uploaded to the VM',icon='check')
        
    def showSavesFromVm(self,*args): #Handles filtering saves from the local VM. Not used if not in a VM'd environment.
        filtera= self.entryFiltro.get()
        #print(f'Current filter: {filtera}')
        savefolder=self.saveTipo.get()
        ###This block is for multiple folders inside a VM
        if savefolder=='General':
            if self.country=='1':
                self.vmSavesDir=r'Team 1 save folder'
                #self.vmSavesDir=r'C:/Saves' #testing purposes
            elif self.country=='2':
                self.vmSavesDir=r'Team 2 save folder'
        else:
            if self.country=='1':
                self.vmSavesDir=r'Team 1 staggered saves folder'
            elif self.country=='2':
                self.vmSavesDir=r'Team 2 staggered saves folder'
        self.framesVm=[]
        self.frameVmId=0
        self.saveVmList=[]
        self.descVmList=[]
        self.listOfRemoteSaves = ct.CTkScrollableFrame(self.middlevm,width=380)
        self.listOfRemoteSaves.grid(row=0,column=0,pady=5,padx=5)
        self.listOfRemoteSaves.grid_columnconfigure((1),weight=1,uniform='column')
        self.frameDescription=ct.CTkTextbox(self.rightvm,height=150,width=400)
        self.frameDescription.grid(row=1,column=0,pady=5,padx=5)
        self.frameDescription.insert(1.0,'No file selected')
        print(f'Current filter: {filtera}')
        for (parent_dirpath, dirnames, filenames) in os.walk(self.vmSavesDir):
            for folder in dirnames:
                if filtera=='':
                    fullpath = os.path.join(parent_dirpath,folder)
                    if os.path.isdir(fullpath):
                        if 'BackupSaveData' in os.listdir(fullpath):#delete last two conditionals bf shipping
                            self.saveVmList.append(fullpath)
                            for file in os.listdir(fullpath):
                                if file.endswith('txt'):
                                    pathtxt=str(os.path.join(self.vmSavesDir, folder, file))
                                    pathtxt=pathtxt.replace('\\','/')
                                    with open(pathtxt, 'r') as f:
                                        text = f.read()
                                        if text == '':
                                            self.descVmList.append('No description provided')
                                        else:
                                            self.descVmList.append(text)
                            if len(self.saveVmList) > len(self.descVmList):
                                self.descVmList.append('No description file provided')
                else:
                    fullpath = os.path.join(parent_dirpath,folder)
                    if os.path.isdir(fullpath):
                        if filtera.lower() in str(os.path.basename(fullpath)).lower():
                            if 'BackupSaveData' in os.listdir(fullpath):
                                self.saveVmList.append(fullpath)
                                for file in os.listdir(fullpath):
                                    if file.endswith('txt'):
                                        pathtxt=str(os.path.join(self.vmSavesDir, folder, file))
                                        pathtxt=pathtxt.replace('\\','/')
                                        with open(pathtxt, 'r') as f:
                                            text = f.read()
                                            if text == '':
                                                self.descVmList.append('No description provided')
                                            else:
                                                self.descVmList.append(text)
                                if len(self.saveVmList) > len(self.descVmList):
                                    self.descVmList.append('No description file provided')
        for item in self.saveVmList:
            frame = FrameTemplateVm(self.listOfRemoteSaves,self.frameVmId,self.saveVmList,self.descVmList,self)
            self.frames.append(frame)
            self.frameVmId += 1
    
    def wrapThisShit(self,whatDoIWrap): #Wraps text for preview in right joycon
        wrappedShit='\n'.join(textwrap.wrap(whatDoIWrap,width=27,drop_whitespace=True,break_on_hyphens=False))
        return wrappedShit
        
    def modDesc(self): #Modify description and upload to VM
        newdesc=self.aboutSaveF.get(1.0,END)
        try:
            olddescdir=f'{self.whatDoISend}/desc.txt'
            with open(olddescdir,'w') as f:
                f.write(newdesc)
            self.loadSavesFromFolder()
        except AttributeError:
            traceback.print_exc()
            pass
        
        ###This block updates the save data whose description you just modified, but on the Virutal Machine
        
        # if self.country=='1': ###I guess this needs remodelling for different projects
        #     if '[FIXED SAVE]' in newdesc:
        #         self.saveNewRemoteSave=f'Team 1 staggered save folder/{os.path.basename(self.whatDoISend)}'
        #     else:
        #         self.saveNewRemoteSave=f'Team 1 save folder/{os.path.basename(self.whatDoISend)}'
        # elif self.country=='2':
        #     if '[FIXED SAVE]' in newdesc:
        #         self.saveNewRemoteSave=f'Team 2 staggered save folder/{os.path.basename(self.whatDoISend)}'
        #     else:
        #         self.saveNewRemoteSave=f'Team 2 save folder/{os.path.basename(self.whatDoISend)}'
        # try:
        #     shutil.copytree(self.whatDoISend,self.saveNewRemoteSave,dirs_exist_ok=True)
        # except:
        #     traceback.print_exc()
        #     pass
            
class FrameTemplate: #Frame template for each save in repo view
    def __init__(self,parent,frame_id,fileNameList,descFileList,gui):
        self.frame_id = frame_id
        self.gui = gui
        self.parent=parent
            
        self.swicon = ct.CTkImage(light_image=(Image.open(self.resourcePath('sw.png'))),size=(18,18))
        
        frame = ct.CTkFrame(parent)
        frame.grid(row=frame_id+1,column=0,pady=2,padx=5,columnspan=2,sticky=EW)
        frame.grid_columnconfigure((1), weight=1, uniform="column")
        imageSw = ct.CTkButton(frame,image=self.swicon,height=11,width=11,fg_color='#2b2b2b',hover_color='#2b2b2b',text='')
        imageSw.grid(row=0,column=0,pady=2,padx=4,sticky=NS)
        labelTitle = ct.CTkLabel(frame,text=f'{os.path.basename(fileNameList[frame_id])}')
        labelTitle.grid(row=0,column=1,pady=2,padx=5,sticky=W)
        buttonExport = ct.CTkButton(frame,text='Select',height=20,width=70,command=lambda: gui.open(descFileList[frame_id],fileNameList[frame_id],frame_id,buttonExport),fg_color='#2b2b2b',border_color='#00cbff',border_width=3)
        buttonExport.grid(row=0,column=2,pady=2,padx=5,sticky=W)
        divider = ct.CTkLabel(frame,text='',bg_color='#555555',height=0,font=('helvetica',1))
        divider.grid(row=1,column=0,columnspan=3,pady=1,sticky=EW)
        
    def resourcePath(self, relativePath):
            basePath=getattr(sys,'_MEIPASS',os.path.dirname(os.path.abspath(__file__)))
            return os.path.join(basePath,relativePath)
            
class FrameTemplateVm: #Frame template for each save in VM view
    def __init__(self,parent,frame_id,fileNameList,descFileList,gui):
        self.frameVmId = frame_id
        self.gui = gui
        self.parentVm=parent
        
        frame = ct.CTkFrame(parent)
        frame.grid(row=frame_id,column=0,pady=2,padx=5,sticky=EW,columnspan=2)
        frame.grid_columnconfigure((0), weight=1, uniform="column")
        labelTitle = ct.CTkLabel(frame,text=f'{os.path.basename(fileNameList[frame_id])}',font=('Helvetica',11))
        labelTitle.grid(row=0,column=0,pady=2,padx=5,sticky=W)
        buttonExport = ct.CTkButton(frame,text='Select',height=20,width=70,command=lambda: gui.openVm(descFileList[frame_id],fileNameList[frame_id]),fg_color='transparent',border_color='#00cbff',border_width=3)
        buttonExport.grid(row=0,column=1,pady=2,padx=5,sticky=W)
        divider = ct.CTkLabel(frame,text='',bg_color='#555555',height=0,font=('helvetica',1))
        divider.grid(row=1,column=0,columnspan=3,pady=1,sticky=EW)
        
if __name__ == '__main__':
    app = gui()
        