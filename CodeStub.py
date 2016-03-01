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


a = "hello"
print a