from random import randint
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

    def solve(self, algorithm):
        if algorithm == "Genetic":
            self.SolveGenetic()


    #Genetic Algorithm based solution implementation method
    def SolveGenetic(self):
        popSize = 100

        # Generate a population of above state size
        for i in range(0,popSize):
            individual = dict(self.varDict) #clone variables
            # for each individual generate random values for his variables
            for varName in individual:
                individual[varName]= self.getRandomValue()

    # Generates a random value from a given domain
    def getRandomValue(self,domain):

        # Decide (randomly if possible) if the random value will
        # be selected from a values list of a range list
        rangeOrValue = "Values"
        if domain.Ranges and domain.Values:
            rangeOrValue = "Ranges" if randint(1,2) == 1 else "Values"
        elif domain.Ranges:
            rangeOrValue == "Ranges"

        if rangeOrValue == "Ranges":
            range = domain.Ranges[randint(0,len(domain.Ranges)-1)]
            val = range[randint(0,len(range)-1)]
            return val
        else:
            val = domain.Values[randint(0,len(domain.Values)-1)]


    # Call all variables validation methods and collect results
    def GlobalValidate(self):
        for k,val in self.constraintDict.iteritems():
           print val.Validate()
            
    def Randomize(self):
        pass
        
    def Next(self):
        pass

class Constraint(object):
    def __init__(self, varDict,varValue,funcList=None, checklist=None):
        self.varDict = varDict
        self.varValue = varValue
        self.funcList = funcList if funcList else dict()
        self.checklist = checklist if checklist else dict()
    
    def Validate(self):  
        for k,values in self.checklist.iteritems():
            for currVal in values:
                if(self.funcList[k](self.varValue,self.varDict[currVal]) == False):
                    return False
        return True

class Domain(object):
    def __init__(self, Ranges, Values, AttributeInVar):
        self.Ranges = Ranges
        self.Values = Values
        self.AttributeInVar =AttributeInVar


# Create and init the Australian Map CSP
global a 
a = CSP()

# Populate Variables
a.varDict["WA"] = None
a.varDict["NT"] = None
a.varDict["Q"]  = None
a.varDict["SA"] = None
a.varDict["NSW"]= None
a.varDict["V"]  = None
a.varDict["T"]  = None

# Domains
dom = Domain(None,["Red","Green","Blue"],"Color")
a.domDict["WA"] =   [dom]
a.domDict["NT"] =   [dom]
a.domDict["Q"]  =   [dom]
a.domDict["SA"] =   [dom]
a.domDict["NSW"]=   [dom]
a.domDict["V"]  =   [dom]
a.domDict["T"]  =   [dom]

diffFuncList = {"Differant": lambda x,y: x!=y}
a.constraintDict["WA"] = Constraint(a.varDict,a.varDict["WA"],diffFuncList,{"Differant":["NT","SA"]})
a.constraintDict["NT"] = Constraint(a.varDict,a.varDict["NT"],diffFuncList,{"Differant":["WA","SA","Q"]})
a.constraintDict["Q"]  = Constraint(a.varDict,a.varDict["Q"],diffFuncList,{"Differant":["NT","SA","NSW"]})
a.constraintDict["SA"] = Constraint(a.varDict,a.varDict["SA"],diffFuncList,{"Differant":["WA","NT","Q","NSW","V"]})
a.constraintDict["NSW"]= Constraint(a.varDict,a.varDict["NSW"],diffFuncList,{"Differant":["Q","SA","V"]})
a.constraintDict["V"]  = Constraint(a.varDict,a.varDict["V"], diffFuncList,{"Differant":["SA","NSW"]})
a.constraintDict["T"]  = Constraint(a.varDict,a.varDict["T"], diffFuncList)

a.GlobalValidate()

