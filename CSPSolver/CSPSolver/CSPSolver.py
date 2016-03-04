class CSP(object):
    def __init__(self, varDict, domDict, constraintDict):
        self.varDict = varDict
        self.domDict = domDict
        self.constraintDict = constraintDict
    
    def __init__(self, path):
        
        self.varDict = None
        self.domDict = None
        self.constraintDict = None
        
        # TODO: Add load data from XML to class Data Members
    
    def __init__(self):
        self.varDict = dict()
        self.domDict = dict()
        self.constraintDict = dict()
    # test comment
    def Solve(self):        
        pass
    
    def GlobalValidate():
        for i in constraintDict:
            i.Validate
            
    def Randomize(self):
        pass
        
    def Next(self):
        pass

class Constraint(object):
    def __init__(self, varName,funcList=None, checklist=None):
        self.myVarName = varName
        self.funcList = funcList if funcList else dict()
        self.checklist = checklist if checklist else dict()
    
    def Validate(self, constaName, *args):    
           
        #return all([self.funcList[i](*args) for i in checklist])        

class Domain(object):
    def __init__(self, Ranges, Values, AttributeInVar):
        self.Ranges = Ranges
        self.Values = Values
        self.AttributeInVar =AttributeInVar


# Create init the Australian Map CSP
global a 
a = CSP()

# Populate Variables
a.varDict["WA"]=None
a.varDict["NT"]=None
a.varDict["Q"]=None
a.varDict["SA"]=None
a.varDict["NSW"]=None
a.varDict["V"]=None
a.varDict["T"]=None

# Domains
a.domDict["WA"] =   ["Red","Green","Blue"]
a.domDict["NT"] =   ["Red","Green","Blue"]
a.domDict["Q"]  =   ["Red","Green","Blue"]
a.domDict["SA"] =   ["Red","Green","Blue"]
a.domDict["NSW"]=   ["Red","Green","Blue"]
a.domDict["V"]  =   ["Red","Green","Blue"]
a.domDict["T"]  =   ["Red","Green","Blue"]

diffFuncList = {"Differant": lambda x,y: x!=y}
a.constraintDict["WA"] = Constraint("WA",diffFuncList,{"Differant":["NT","SA"]})
a.constraintDict["NT"] = Constraint("NT",diffFuncList,{"Differant":["WA","SA","Q"]})
a.constraintDict["Q"]  = Constraint("Q",diffFuncList,{"Differant":["NT","SA","NSW"]})
a.constraintDict["SA"] = Constraint("SA",diffFuncList,{"Differant":["WA","NT","Q","NSW","V"]})
a.constraintDict["NSW"]= Constraint("NSW",diffFuncList,{"Differant":["Q","SA","V"]})
a.constraintDict["V"]  = Constraint("V", diffFuncList,{"Differant":["SA","NSW"]})
a.constraintDict["T"]  = Constraint("T", diffFuncList)

print "kaki"

