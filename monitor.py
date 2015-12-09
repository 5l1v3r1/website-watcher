#-*- coding:utf-8 -*-
import os,shutil
import datetime
import pyinotify
import logging
import backupFunc
import diffFiles
import re
import time
class MyEventHandler(pyinotify.ProcessEvent):
    logging.basicConfig(level=logging.INFO,filename='monitor.log')
    
    logging.info("Starting monitor...")
    def __init__(self,mode,path,excpath,filesuffix):
        self.mode=mode
        self.remove=False
        self.create=False
        self.modify=False
        self.deleteFold=False
        self.path=path
        self.excpath=excpath
        self.filesuffix=filesuffix.split(',')
        
        self.diff=diffFiles.fileDiff()
    def parsePath(self,path,mode):
        pre_path=path[:path.rfind('/')+1]
        filename=path[path.rfind('/')+1:]
        index=filename.find('.')
        flag=False
        if index==-1:
            filesuffix=''
        else: 
            filesuffix=filename[index+1:]
            
            for fs in filesuffix.split('.'):
                if fs in self.filesuffix:
                    flag=True
                    break
        flag1=False
        for exc in self.excpath.split(','):
            if pre_path == exc or pre_path == (exc+'/'):
                flag1=True
                break
        print "pre_path:%s,filename:%s,filesuffix:%s" % (pre_path,filename,filesuffix)
        if flag1:
            if mode == 'create':
                if not filesuffix or flag:
                    
                    return False
                else:
                    return True
            else:
                return True
        else:
            return False
    def process_IN_ACCESS(self, event): # file be accessed
        print "\033[0;33;40mACCESS event:%s\033[0m" % (event.pathname)
        logging.info("\033[0;33;40m[MEDIUM]ACCESS event : %s  %s\033[0m" % (os.path.join(event.path,event.name),datetime.datetime.now()))
     
    def process_IN_ATTRIB(self, event):  # meta data be modified
        print "\033[0;33;40mATTRIB event:%s\033[0m" % (event.pathname)
        logging.info("\033[0;33;40m[MEDIUM]IN_ATTRIB event : %s  %s\033[0m" % (os.path.join(event.path,event.name),datetime.datetime.now()))
     
    def process_IN_CLOSE_NOWRITE(self, event): # not w file be closed
        print "\033[0;32;40mCLOSE_NOWRITE event:%s\033[0m" % (event.pathname)
        logging.info("\033[0;32;40m[LOW]CLOSE_NOWRITE event : %s  %s\033[0m" % (os.path.join(event.path,event.name),datetime.datetime.now()))
     
    def process_IN_CLOSE_WRITE(self, event): # w file be closed 
        print "\033[0;32;40mCLOSE_WRITE event:%s\033[0m" % (event.pathname)
        logging.info("\033[0;32;40m[LOW]CLOSE_WRITE event : %s  %s\033[0m" % (os.path.join(event.path,event.name),datetime.datetime.now()))
     
    def process_IN_CREATE(self, event): # file be created
        print "\033[0;31;40mCREATE event:%s    %s\033[0m" % (event.pathname,datetime.datetime.now())
        if self.deleteFold:
            print "deleteFold create"
            return False
        if not self.parsePath(event.pathname,'create'):
            if self.mode == 'safe':
                
                if not self.create:
                    print "\033[0;31;40mCREATE event:%s   %s\033[0m" % (event.pathname,datetime.datetime.now())
                    for path in self.path.split(','):
                        if path in event.pathname:
                            self.backup=backupFunc.backupAndRestore(path)
                            break                    
                    flag=self.backup.bakPathIsExist(event.pathname)
                    if flag == 'noexist':
                        print "\033[0;31;40mYou can\'t create %s,it has deleted!   %s\033[0m" % (event.pathname,datetime.datetime.now())
                        self.remove=True
                        if os.path.isdir(event.pathname):
                            shutil.rmtree(event.pathname)
                        elif os.path.isfile(event.pathname):
                            os.remove(event.pathname)
                    logging.info("\033[0;31;40m[HIGH][DEALED]CREATE event : %s  %s\033[0m" % (os.path.join(event.path,event.name),datetime.datetime.now()))
                else:
                    self.create=False
                    print "create machine do"
            elif self.mode == 'human':
                print "\033[0;31;40mCREATE event:%s\033[0m" % (event.pathname)
                logging.info("\033[0;31;40m[HIGH]CREATE event : %s  %s\033[0m" % (os.path.join(event.path,event.name),datetime.datetime.now()))
        else:
            print "\033[0;31;40mCREATE event(white list):%s\033[0m" % (event.pathname)
            logging.info("\033[0;31;40m[HIGH][EXCPATH]CREATE event : %s  %s\033[0m" % (os.path.join(event.path,event.name),datetime.datetime.now()))
    def process_IN_DELETE(self, event): # file be deleted
        if self.deleteFold:
            print "deleteFold delete"
            return False        
        if not self.parsePath(event.pathname,'delete'):
            if self.mode == 'safe':
                if not self.remove:
                    for path in self.path.split(','):
                        if path in event.pathname:
                            self.backup=backupFunc.backupAndRestore(path)
                            break
                    print "\033[0;31;40mDELETE event:%s  %s\033[0m" % (event.pathname,datetime.datetime.now())
                    flag=self.backup.bakPathIsExist(event.pathname)  
                    if flag == 'dictionary':
                        self.create=True
                        if not os.path.exists(event.pathname):
                            self.deleteFold=True
                            self.create=True
                            self.modify=True
                            self.backup.runResFold(event.pathname)
                            time.sleep(2)
                            self.create=False
                            self.modify=False                            
                            self.deleteFold=False
                    elif flag=='file':
                        print "\033[0;31;40mYou can\'t delete %s,it has recovered!  %s\033[0m" % (event.pathname,datetime.datetime.now())
                        content=self.backup.getDecompress(event.pathname)
                        self.create=True
                        self.modify=True
                        try:
                            with open(event.pathname,'w') as file:
                                file.write(content)   
                        except:
                            print "can't open %s" % (event.pathname)
                    else:
                        print "backup file %s is not exist,you can delete it!   %s" % (event.pathname,datetime.datetime.now())
                    logging.info("\033[0;31;40m[HIGH][DEALED]DELETE event : %s  %s\033[0m" % (os.path.join(event.path,event.name),datetime.datetime.now()))
                else:
                    self.remove=False
                    print "delete machine do"
            elif self.mode  == 'human':
                print "\033[0;31;40mDELETE event:%s    %s\033[0m" % (event.pathname,datetime.datetime.now())
                logging.info("\033[0;31;40m[HIGH]DELETE event : %s  %s\033[0m" % (os.path.join(event.path,event.name),datetime.datetime.now()))
        else:
            print "\033[0;31;40mDELETE event(white list):%s   %s\033[0m" % (event.pathname,datetime.datetime.now())
            logging.info("\033[0;31;40m[HIGH][EXCPATH]DELETE event : %s  %s\033[0m" % (os.path.join(event.path,event.name),datetime.datetime.now()))
    def process_IN_MODIFY(self, event): # file be modified
        if self.deleteFold:
            return False         
        if not self.parsePath(event.pathname,'modify'):
            for path in self.path.split(','):
                if path in event.pathname:
                    self.backup=backupFunc.backupAndRestore(path)
                    break            
            if self.mode == 'safe':
                if self.modify == True:
                    self.modify=False
                else:
                    print "\033[0;31;40mMODIFY event:%s   %s\033[0m" % (event.pathname,datetime.datetime.now())
                                        
                    if self.backup.bakPathIsExist(event.pathname) == 'file':
                        print "\033[0;31;40mYou can\'t Modify %s,it has recovered!    %s\033[0m" % (event.pathname,datetime.datetime.now())
                        content=self.backup.getDecompress(event.pathname)
                        self.create=True
                        self.modify=True
                        with open(event.pathname,'w') as file:
                            file.write(content)
                logging.info("\033[0;31;40m[HIGH][DEALED]MODIFY event : %s  %s\033[0m" % (os.path.join(event.path,event.name),datetime.datetime.now()))
            if self.mode == 'human':
                if not self.modify:
                    self.modify=True
                    print "\033[0;31;40mMODIFY event:%s   %s\033[0m" % (event.pathname,datetime.datetime.now())
                    content=self.backup.getDecompress(event.pathname)
                    with open(event.pathname,'r') as file:
                        compare=file.read()
                    diff_content=self.diff.run(content, compare)
                    
                    with open('./diff.log','a') as file:
                        file.write("\033[0;31;40mFile %s had changed at %s\033[0m\n" % (os.path.join(event.path,event.name),datetime.datetime.now()))
                        file.write(diff_content)
                        file.write("\n\n\n")
                    logging.info("\033[0;31;40m[HIGH][LOG]MODIFY event : %s  %s\033[0m" % (os.path.join(event.path,event.name),datetime.datetime.now()))
                else:
                    self.modify=False
                    print "modify machine do"
        else:
            print "\033[0;31;40mMODIFY event(white list):%s   %s\033[0m" % (event.pathname,datetime.datetime.now())
            logging.info("\033[0;31;40m[HIGH][EXCPATH]MODIFY event : %s  %s\033[0m" % (os.path.join(event.path,event.name),datetime.datetime.now())) 
    def process_IN_OPEN(self, event): # file be opened
        print "\033[0;32;40mOPEN event:%s\033[0m" % (event.pathname)
        logging.info("\033[0;32;40m[LOW]OPEN event : %s  %s\033[0m" % (os.path.join(event.path,event.name),datetime.datetime.now()))
     
class monitor:
    def __init__(self,path,mode,excpath,filesuffix):
        self.path=path
        self.mode=mode
        self.excpath=excpath
        self.filesuffix=filesuffix
    def run(self):
        # watch manager
        wm = pyinotify.WatchManager()
        
        wm.add_watch(self.path.split(','), pyinotify.ALL_EVENTS, rec=True)
            
        # event handler
        eh = MyEventHandler(self.mode,self.path,self.excpath,self.filesuffix)
         
        # notifier
        notifier = pyinotify.Notifier(wm, eh)
        notifier.loop()        
 
if __name__ == '__main__':
    pass