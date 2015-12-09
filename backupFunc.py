#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import zlib
import hashlib
class backupAndRestore: 
    fileCount=0
    projectPath=""
    projectName=''
    bakPath=''
    curBakPath=''
    resPath=''
    curResPath=''
    
    fileNameInfo=''
    def __init__(self,projectPath):
        if projectPath[-1]=='/':
            projectPath=projectPath[0:-1]
        self.projectPath=projectPath
        if not os.path.exists(self.projectPath):
            print "The project is not exist !\nInit unsuccessfully !"   
            return
        self.projectName=projectPath.split('/')[-1]
        self.bakPath=os.getcwd()+'/.bak/'+self.projectName+'/'
        self.curBakPath=self.bakPath
        self.resPath=os.getcwd()+'/.res/'+self.projectName+'/'
        self.curResPath=self.resPath
        if not os.path.exists(os.getcwd()+'/.bak/'):
            os.mkdir(os.getcwd()+'/.bak/')
        if not os.path.exists(self.bakPath):
            os.mkdir(self.bakPath)
        if not os.path.exists(os.getcwd()+'/.res/'):
            os.mkdir(os.getcwd()+'/.res/')
        if not os.path.exists(self.resPath):
            os.mkdir(self.resPath)        
        print "Init successfully !" 
     #   os.system("cd "+self.filePath +" &&ls")  #~/Desktop
     

    def compress(self,inFile, ouFile, level=9):
        inFile = open(inFile, 'rb')
        ouFile = open(ouFile, 'wb')
        compress = zlib.compressobj(level)
        data = inFile.read(1024)
        while data:
            ouFile.write(compress.compress(data))
            data = inFile.read(1024)
        ouFile.write(compress.flush())
        inFile.close();
        ouFile.close();
        
    def decompress(self,inFile, ouFile):
        inFile = open(inFile, 'rb')
        ouFile = open(ouFile, 'wb')
        decompress = zlib.decompressobj()
        data = inFile.read(1024)
        while data:
            ouFile.write(decompress.decompress(data))
            data = inFile.read(1024)
        ouFile.write(decompress.flush())
        inFile.close();
        ouFile.close();        
        
    def readfile(self,dirPath):
        if not os.path.exists(dirPath):
            print "The dirPath is not exist !"
            return         
        for i in os.listdir(dirPath):
            file=os.path.join(dirPath,i)
            if os.path.isdir(file):
                self.readfile(file)
            elif os.path.isfile(file):
                print "file is : " + file
    
    def _runCompress(self,projectPath):
        for i in os.listdir(projectPath):
            file=os.path.join(projectPath,i)
            fileName=file.split("/")[-1]
            md5=hashlib.md5(file.encode('utf-8')).hexdigest()[0:16]       
            if os.path.isdir(file): 
                self.curBakPath=self.curBakPath+md5+"/"
                if not os.path.exists(self.curBakPath):
                    os.mkdir(self.curBakPath)                
                self.fileNameInfo=self.fileNameInfo+"fold:"+md5+":"+file+"\n"
                self._runCompress(file)
                self.curBakPath=self.curBakPath[0:-17]
            elif os.path.isfile(file): 
                self.curBakPath=self.curBakPath+md5
                self.fileNameInfo=self.fileNameInfo+"file:"+md5+":"+file+"\n"
                self.compress(file, self.curBakPath)
                self.curBakPath=self.curBakPath[0:-16]
                self.fileCount+=1
    
    def runCompress(self):     
        print "\nInit backuping ..."  
        if not os.path.exists(self.projectPath):
            print "The project is not exist !\nInit unsuccessfully !"
            return 
        print "Backuping project ..."  
        self._runCompress(self.projectPath)
        print "Backup successfully !  Totally backup %d file !\nCreating the flag ..."  %self.fileCount
        self._toFlagFile()
        print "Create the flag successfully !\nCompress successfully !"  
    
    def _runDeompress(self,projectPath):
        flagFile = open(self.bakPath+'.flag.txt', 'r')
        self.fileCount=0
        pathLen=0
        i=0
        self.curBakPath=self.curBakPath[:-1]
        while(1):
            flagLineText=flagFile.readline()
            if flagLineText:
                aTemp=flagLineText[0:4]
                bTemp=flagLineText[5:21]
                cTemp=self.resPath+flagLineText[22:-1][len(self.projectPath)+1:]
                if len(cTemp.split('/'))>pathLen:
                    self.curBakPath=self.curBakPath+'/'+bTemp
                    pathLen=len(cTemp.split('/'))
                elif len(cTemp.split('/'))<pathLen:
                    i=pathLen-len(cTemp.split('/'))+1
                    self.curBakPath=self.curBakPath[0:-17*i]+'/'+bTemp
                    pathLen=len(cTemp.split('/'))      
                else :
                    self.curBakPath=self.curBakPath[0:-17]+'/'+bTemp                     
                if aTemp=="fold":
                    if not os.path.exists(cTemp):
                        os.mkdir(cTemp)
                elif aTemp=="file":
                    self.fileCount+=1
                    self.decompress(self.curBakPath, cTemp)                  
            else:
                break  
        flagFile.close( )       
    
    def runDecompress(self):
        print "\nInit restoring ..."  
        if not os.path.exists(self.bakPath):
            print "The project is not exist !\nInit unsuccessfully !"
            return         
        if not os.path.exists(self.bakPath+'.flag.txt'):
            print "The flag file is not exist !\nInit unsuccessfully !"
            return                     
        print "Init successfully !\nRestoring project ..."  
        self._runDeompress(self.bakPath)
        print "Restore successfully !  Totally restore %d file !"  %self.fileCount
        print "Decompress successfully !" 
    
    def _toFlagFile(self):
        output = open(self.bakPath+'.flag.txt', 'w')
        output.write(self.fileNameInfo)
        output.close( )        
        
    def getDecompress(self,filePath):
        flagFile=open(self.bakPath+'.flag.txt','r')
        projectPathLen=len(self.projectPath)+1
        bTemp=self.projectPath+'/'
        maxI=len(filePath[projectPathLen:].split('/'))
        dirHash=''
        for i in range(0,maxI):
            linecount=0
            bTemp=bTemp+filePath[projectPathLen:].split('/')[i]   
            while(1):
                flagLineText=flagFile.readline()
                if flagLineText:
                    linecount+=1
                    aTemp=flagLineText[22:-1]
                    if not cmp(aTemp, bTemp):
                        dirHash=dirHash+'/'+flagLineText[5:21]
                        break;
                else :
                    break
            bTemp=bTemp+'/'
        bakFilePath=self.bakPath[:-1]+dirHash
        fileText=''
        inFile = open(bakFilePath, 'rb')
        decompress = zlib.decompressobj()
        data = inFile.read(1024)
        while data:
            fileText += decompress.decompress(data)
            data = inFile.read(1024)
        inFile.close();    
        return fileText
                    

    def pathIsExist(self,path):
        if path[0]!='/':
            path='/'+path
        pathArr=path.split("/")
        tempPath=''
        for i in range(1,len(pathArr)-1):
            if not pathArr[i]=='':
                tempPath=tempPath+'/'+pathArr[i]
                print tempPath
                if not os.path.isdir(tempPath): 
                    return  "noexist"                   
            else:
                return "noexist"
        tempPath=tempPath+'/'+pathArr[len(pathArr)-1]
        if os.path.exists(tempPath):
            if  os.path.isfile(tempPath): 
                return "file"            
            elif os.path.isdir(tempPath):
                return "dictionary"
        else:
            return "noexist"

    def bakPathIsExist(self,filePath):
        
        flagFile=open(self.bakPath+'.flag.txt','r')
        projectPathLen=len(self.projectPath)+1
        bTemp=filePath
        while(1):
            flagLineText=flagFile.readline()
            if flagLineText:
                aTemp=flagLineText[22:-1]
                if not cmp(aTemp, bTemp):
                    fileInfo=flagLineText[0:4]
                    if fileInfo=="fold":
                        return "dictionary"
                    elif fileInfo=="file":
                        return "file"
                    else:
                        return "noexist" 
            else :
                return "noexist" 
                
    def runResFold(self,path) :
        print "Init Restoring ..."    
        if path[0]!='/':
            path='/'+path 
        if path[-1]=='/':
            path=path[:-1]          
        if path[1]=='/':
            print "The fold is not exist! \nInit unsuccessfully !"
            return             
        temp=''
        for x in range(1,len(path.split('/'))-1):
            temp+='/'+path.split('/')[x]
        if not os.path.exists(temp):
            print "The fold is not exist! \nInit unsuccessfully !"
            return 
        if not os.path.exists(path):
            os.mkdir(path)        
        flagFile = open(self.bakPath+'.flag.txt', 'r')
        self.tempCurBakPath=self.bakPath[:-1]
        self.tempCurResPath=path
        curPath=self.projectPath+"/"+path[len(self.projectPath)+1:].split('/')[0]
        i=0
        j=0
        flag=0
        pathLen=0
        self.fileCount=0
        print "Init successfully !\nRestoring fold ..."  
        while(1):
            flagLineText=flagFile.readline()
            if flagLineText:   
                if flag==0:
                    if curPath==flagLineText[22:-1]:
                        self.tempCurBakPath += '/'+flagLineText[5:21]
                        if i< len(path[len(self.projectPath)+1:].split('/'))-1:
                            i+=1
                            curPath=curPath+"/"+path[len(self.projectPath)+1:].split('/')[i]
                        elif i==len(path[len(self.projectPath)+1:].split('/'))-1:
                            flag=1
                            self.tempCurResPath=curPath
                elif flag==1:
                    if curPath==flagLineText[22:-1][:len(curPath)]:
                        aTemp=flagLineText[0:4]
                        bTemp=flagLineText[5:21]                     
                        cTemp=flagLineText[22:-1]
                        if len(cTemp.split('/'))>pathLen:
                            self.tempCurBakPath=self.tempCurBakPath+'/'+bTemp
                            pathLen=len(cTemp.split('/'))
                        elif len(cTemp.split('/'))<pathLen:
                            j=pathLen-len(cTemp.split('/'))+1
                            self.tempCurBakPath=self.tempCurBakPath[0:-17*j]+'/'+bTemp
                            pathLen=len(cTemp.split('/'))      
                        else :
                            self.tempCurBakPath=self.tempCurBakPath[0:-17]+'/'+bTemp                     
                        if aTemp=="fold":
                            if not os.path.exists(cTemp):
                                os.mkdir(cTemp)
                        elif aTemp=="file":
                            self.fileCount+=1
                            self.decompress(self.tempCurBakPath, cTemp)    
            else:
                if flag==0:
                    print "The bak fold is not exist !\nRestore unsuccessfully !"       
                else : 
                    print "Restore successfully !  Totally restore %d file !"  %self.fileCount
                break

        
if __name__=='__main__':
    
    a=backupAndRestore('/home/gmfork/Desktop/myblog')
    
    #backup project file 
    a.runCompress()
    
    #get a characteristic backup file and restore 
    #for example: 
    #a.getDecompress("/home/gmfork/Desktop/myblog/ThinkPHP/Library/Vendor/spyc/examples/yaml-load.php")
    
    #restore project file 
    a.runDecompress()
    
    #text=a.bakPathIsExist("/home/gmfork/Desktop/myblog/Public")
    #print text
