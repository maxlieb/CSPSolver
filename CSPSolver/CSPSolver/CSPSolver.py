from random import randint, random
class CSP(dict):
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
    def SolveGenetic(self, popSize=100):
        pop = self.population(popSize)
        self.evolve(pop)

    def evolve(self, pop, retain=0.2, random_select=0.5, mutate=0.2):
        graded = [(self.GlobalValidate(x),x) for x in pop]
        graded = [ x[1] for x in sorted(graded)]
        retain_length = int(len(graded)*retain)
        parents = graded[:retain_length]

        for parent in parents:
            for k,v in parent.iteritems():
                print k,v.Color
            print "--------------------------------"

        # randomly add other individuals to promote genetic diversity
        for X in graded[retain_length:]:
            if random_select > random(): #random_select-0.01:
                parents.append(X)

        # mutate some individuals
        for parent in parents:
            if 1==1:
            #if mutate > random():
                randomkey = list(parent.keys())[randint(0,len(list(parent.keys()))-1)]
                for currDom in self.domDict[randomkey]:
                    setattr(parent[randomkey], currDom.AttributeInVar, self.getRandomValue(currDom))

        # crossover parents to create children
        parents_length = len(parents)
        desired_length = len(pop) - parents_length

        children = []
        while len(children) < desired_length:
            male = randint(0, parents_length-1)
            female = randint(0, parents_length-1)
            if male != female:
                male = parents[male]
                female = parents[female]
                malehalf = dict(male.items()[len(male)/2:])
                femalehalf = dict(female.items()[:len(female)/2])
                child = dict(malehalf).update(femalehalf)
                children.append(child)
        parents.extend(children)
        print len(parents)
        return parents

    def population(self,length):
        pop = []
        # Generate a population of above stated size
        for i in range(0,length):
            individual = dict(self.varDict) #clone variables
            # for each individual generate random values for his variables
            for varName in individual:
                # foreach domain of the current variable
                for currDom in self.domDict[varName]:
                    setattr(individual[varName], currDom.AttributeInVar, self.getRandomValue(currDom))
            pop.append(individual)
        return pop

    # Generates a random value from a given domain
    def getRandomValue(self, domain):

        # Decide (randomly if possible) if the random value will
        # be selected from a values list of a range list
        rangeOrValue = "Values"
        if domain.Ranges and domain.Values:
            rangeOrValue = "Ranges" if randint(1,2) == 1 else "Values"
        elif domain.Ranges:
            rangeOrValue = "Ranges"

        if rangeOrValue == "Ranges":
            range = domain.Ranges[randint(0,len(domain.Ranges)-1)]
            val = range[randint(0,len(range)-1)]
        else:
            val = domain.Values[randint(0,len(domain.Values)-1)]

        return val

    # Call all variables validation methods and collect results
    def GlobalValidate(self, individual = None):
        if (individual == None):
            individual = self.varDict

        sum = 0

        for k,val in self.constraintDict.iteritems():
            sum += val.Validate(individual)
            #print k, val.Validate(individual)

        return sum
            
    def Randomize(self):
        pass
        
    def Next(self):
        pass

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

class Constraint(dict):
    def __init__(self, varDict, varKey, funcList=None, checklist=None):
        self.varDict = varDict
        self.varKey = varKey
        self.funcList = funcList if funcList else dict()
        self.checklist = checklist if checklist else dict()
    
    def Validate(self, individual = None):
        counter = 0
        varValue = individual[self.varKey]

        if (individual == None):
            individual = self.varDict

        # pass over the functions to check (e.g "Different")
        for k,values in self.checklist.iteritems():
            # pass over the given arguments for the current function (e.g ["NT","SA"])
            for currVal in values:
                if(self.funcList[k](varValue, individual[currVal]) == False):
                    counter += 1
        return counter

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

class Domain(dict):
    def __init__(self, Ranges, Values, AttributeInVar):
        self.Ranges = Ranges
        self.Values = Values
        self.AttributeInVar =AttributeInVar

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

# Create and init the Australian Map CSP
global a 
a = CSP()

class var(dict):
    def __init__(self, Color):
        self.Color = Color

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value
# Populate Variables
a.varDict["WA"] = var(None)
a.varDict["NT"] = var(None)
a.varDict["Q"]  = var(None)
a.varDict["SA"] = var(None)
a.varDict["NSW"]= var(None)
a.varDict["V"]  = var(None)
a.varDict["T"]  = var(None)

# Domains
dom = Domain(None,["Red","Green","Blue"],"Color")
a.domDict["WA"] =   [dom]
a.domDict["NT"] =   [dom]
a.domDict["Q"]  =   [dom]
a.domDict["SA"] =   [dom]
a.domDict["NSW"]=   [dom]
a.domDict["V"]  =   [dom]
a.domDict["T"]  =   [dom]

diffFuncList = {"Different": lambda x,y: x!=y}
a.constraintDict["WA"] = Constraint(a.varDict,"WA",diffFuncList,{"Different":["NT","SA"]})
a.constraintDict["NT"] = Constraint(a.varDict,"NT",diffFuncList,{"Different":["WA","SA","Q"]})
a.constraintDict["Q"]  = Constraint(a.varDict,"Q",diffFuncList,{"Different":["NT","SA","NSW"]})
a.constraintDict["SA"] = Constraint(a.varDict,"SA",diffFuncList,{"Different":["WA","NT","Q","NSW","V"]})
a.constraintDict["NSW"]= Constraint(a.varDict,"NSW",diffFuncList,{"Different":["Q","SA","V"]})
a.constraintDict["V"]  = Constraint(a.varDict,"V", diffFuncList,{"Different":["SA","NSW"]})
a.constraintDict["T"]  = Constraint(a.varDict,"T", diffFuncList)

#a.GlobalValidate()

# example for saving the results to json file
from JsonLoader import JsonLoader
JsonLoader.SaveOutputData(a)

a.solve("Genetic")
