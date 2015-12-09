import difflib

class fileDiff:
    def __init__(self):
        pass
    def run(self,content,compare):
        self.content=content.splitlines() # website backup file content
        self.compare=compare.splitlines() # website online file content        
        # compare files
        diff=difflib.ndiff(self.content, self.compare)
        diff=list(diff)
        res=[]
        for line in diff:
            if line[0] == '-':
                line='old:'+line
                res.append(line)
            elif line[0] == '+':
                line='new:'+line
                res.append(line)                
            elif line[0] == '?':
                line='    '+line
                res.append(line)
        return '\n'.join(res)
if __name__=="__main__":
    path1="""this is a test!123
    this is same"""
    path2="""this is a test!456
    this is same"""
    f=fileDiff()
    print f.run(path1,path2)
    #with open('./test','a') as file:
        #file.write('123')