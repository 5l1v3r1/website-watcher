import diffFiles,monitor
import json
import backupFunc
import sys
import os
class coreHandle:
    def __init__(self):
        self.websitePath=''
        self.excFilePath=''
        self.fileSuffix=''
        self.backup='false'
    def check(self):
        '''
        check settings
        '''
        self.getSettings()
        line="{:<15}{:<"+str(self.getMaxPath()+5)+"}{:<10}{:<20}"
        print line.format("Name","Current Setting","Required","Description")
        print line.format("----","---------------","--------","-----------")
        print line.format("WEBSITEPATH",self.websitePath,"YES","website file paths")
        print line.format("BACKUPSTAT",self.backup,"No","stat backup")
        print line.format("EXCFILEPATH",self.excFilePath,"YES","White List:excption file path")
        print line.format("FILESUFFIX",self.fileSuffix,"YES","Black List:file suffix for monitor")
    def getMaxPath(self):
        length=[len(self.websitePath),len(self.backup),len(self.excFilePath),len(self.fileSuffix)]
        Max=-1
        for l in length:
            if l > Max:
                Max=l
                
        return Max
    def setWebsitePath(self,websitePath):
        # set website file path
        self.websitePath=websitePath
        length=len(self.websitePath)
        if self.websitePath[length-1:] == '/':
            self.websitePath=self.websitePath[:length-1]
        print "{} => {}".format("WEBSITEPATH",self.websitePath)
        self.save('websitePath',self.websitePath)
    def setExcFilePath(self,excFilePath):
        # set exception file path
        self.excFilePath=excFilePath
        print "{} => {}".format("EXCFILEPATH",self.excFilePath)
        self.save('excFilePath',self.excFilePath)
    def setFileSuffix(self,fileSuffix):
        # set file suffix for monitor
        self.fileSuffix=fileSuffix
        print "{} => {}".format("FILESUFFIX",self.fileSuffix)
        self.save('fileSuffix',self.fileSuffix)
    def recover(self,path):
        print "recover %s:doing..." % (path)
        self.backupFc=backupFunc.backupAndRestore(path)
        self.backupFc.runDecompress()
        print "recover %s:done..." % (path)
    def save(self,key,value):
        try:
            settings={}
            if os.path.exists("setting"):
                setFile=open("setting","r")
                content=setFile.read()
                setFile.close()
            else:
                content=''
            setFile=open("setting",'w')
            if content:
                settings=json.loads(content) 
            else:
                settings["websitePath"]=''
                settings["excFilePath"]=''
                settings["fileSuffix"]=''
                settings["backup"]='false'
            settings[key]=value
            setFile.write(json.dumps(settings))            
            setFile.close()
        except:
            pass
    def backup_func(self):
        print 'Backup file doing...'
        self.getSettings()
        if self.websitePath:
            # call backup function
            # backup end and save self.backup=True and save others
            webPath=self.websitePath.split(',')
            for path in webPath:
                self.backupFc=backupFunc.backupAndRestore(path)
                self.backupFc.runCompress()
            self.save("backup",'true')
            print 'Backup file done...'
        else:
            print "\033[0;31;40mWebsite file Path not give!\033[0m"
        
    def run(self,mode):
        print "Settings display:"
        self.check()
        if self.excFilePath == '' or self.fileSuffix == '' or self.websitePath == '':
            print "\033[0;31;40mSetting is not complete!\033[0m"
            sys.exit(0)
        # backup file option
        if self.backup == 'false':
            print "\033[0;31;40mWebsite files is not backup!\033[0m"
            sys.exit(0)
        # monitor files start
        #try:
        self.monitor=monitor.monitor(self.websitePath,mode,self.excFilePath,self.fileSuffix)
        self.monitor.run()
        #except:
            #print "Something error!"
        # monitor files end
    def getSettings(self):
        try:
            setFile=open("setting","r")
            content=setFile.read()
            if content:
                settings=json.loads(content)
                self.websitePath=settings["websitePath"]
                self.excFilePath=settings["excFilePath"]
                self.fileSuffix=settings["fileSuffix"]
                self.backup=settings["backup"]  
            setFile.close()
        except:
            pass       
if __name__=="__main__":
    coreHandle=coreHandle()
    #coreHandle.setFileSuffix("php,jsp")
    #coreHandle.setBackupPath("strestet")
    #coreHandle.check()
    coreHandle.backup_func()