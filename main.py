import argparse  
from coreHandle import coreHandle

class argHandle:
    def __init__(self):
        self.corehandle=coreHandle()
        self.parser=argparse.ArgumentParser(description="Website Monitor System")
        self.argSet()
        self.handle()
        
    def argSet(self):
        self.parser.add_argument('--backup', action="store_true",help='Backup files', required=False)
        self.parser.add_argument('--recover', action="store", metavar="websitePath",help='recover backup files', required=False)
        self.parser.add_argument('-c','--check', action="store_true",help='Check Settings', required=False)
        self.parser.add_argument('--run', action="store_true",help='Run the program', required=False)
        self.parser.add_argument('--mode', action="store",choices=['safe','human'],help='Choose run mode for monitor', required=False)
        self.parser.add_argument('-r','--remove', action="store_true",help='Remove ALL Backup Files on local disk', required=False) 
        self.parser.add_argument('--set-websitePath', metavar="websitePath",action="store",nargs="+",help='set website local file path FOR Monitor', required=False)
        self.parser.add_argument('--set-excFilePath', metavar="excFilePath",action="store",nargs="+",help='set website local exception file path FOR Monitor', required=False)
        #self.parser.add_argument('--set-fileSuffix', metavar="FileSuffix",nargs="?",default="html,php,jsp,js,asp,php4,php5,cer",help='set file suffix FOR Monitor', required=False)
        self.parser.add_argument('--set-fileSuffix', metavar="FileSuffix",action="store",help='set file suffix FOR Monitor', required=False)
    def handle(self):
        args=self.parser.parse_args()
        
        if args.check:
            self.corehandle.check()
        else:
            if args.set_fileSuffix != None:
                if type(args.set_fileSuffix) == type([]):
                    self.corehandle.setFileSuffix(','.join(args.set_fileSuffix))
                else:
                    self.corehandle.setFileSuffix(args.set_fileSuffix) 
            if args.set_websitePath != None:
                if type(args.set_websitePath) == type([]):
                    self.corehandle.setWebsitePath(','.join(args.set_websitePath))
                else:
                    self.corehandle.setWebsitePath(args.set_websitePath)
            if args.set_excFilePath != None:
                if type(args.set_excFilePath) == type([]):
                    self.corehandle.setExcFilePath(','.join(args.set_excFilePath))
                else:
                    self.corehandle.setExcFilePath(args.set_excFilePath)
  
        if args.run and args.mode == 'safe':
            self.corehandle.run(args.mode)
        elif args.run and args.mode == 'human':
            self.corehandle.run(args.mode)
        elif args.run:
            print "\033[0;31;40mplease choose running mode(etc. --run --mode safe)\033[0m"
        if args.backup:
            self.corehandle.backup_func()
        if args.recover !=None:
            self.corehandle.recover(args.recover)
if __name__=="__main__":
    ahandle=argHandle()