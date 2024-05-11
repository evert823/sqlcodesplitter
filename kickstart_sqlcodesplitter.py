from sqlcodesplitter import sqlcodesplitter

def gettestcase():
    mylines = ['SELECT * FROM ', '/* select my data */', 'MYSCHEMA.MYTABLE;']
    return mylines

mysp = sqlcodesplitter()
mytestlist = gettestcase()
mytestresult = mysp.splitsqlcode(mytestlist)
print(mytestresult)
