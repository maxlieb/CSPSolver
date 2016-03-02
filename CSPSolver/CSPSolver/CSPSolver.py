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
        
    def Solve(self):
        pass
    
    def Randomize(self):
        pass
        
    def Next(self):
        pass

class Constraint(object):
    def __init__(self, funcList):
        self.funcList = funcList
        self.Oparation = dict()
    
    def Validate(self):
        pass

class Domain(object):
    def __init__(self, Ranges, Values, AttributeInVar):
        self.Ranges = Ranges
        self.Values = Values
        self.AttributeInVar =AttributeInVar


# Create init the Australian Map CSP
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

a.constraintDict["WA"] = 
a.constraintDict["NT"] =
a.constraintDict["Q"]  =
a.constraintDict["SA"] =
a.constraintDict["NSW"]=
a.constraintDict["V"]  =
a.constraintDict["T"]  =


print a.varDict["T"]
print a.domDict["T"][1]
