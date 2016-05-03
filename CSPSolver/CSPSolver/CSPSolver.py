from random import randint, random
from operator import add
import copy
from JsonLoader import JsonLoader





class CSP(object):
    def __init__(self, path = None, varDict = None, domDict = None, constraintDict = None):
        if path == None:
            if varDict == None:
                self.varDict = dict()
            else:
                self.varDict = varDict
            if domDict == None:
                self.domDict = dict()
            else:
                self.domDict = domDict
            if constraintDict == None:
                self.constraintDict = dict()
            else:
                self.constraintDict = constraintDict
        else:
            data = JsonLoader.GetInputData(path)
            self.varDict = data["Vars"]
            self.domDict = dict()
            for currVar in data["Domains"]:
                currDomDict = data["Domains"][currVar]
                currVarDomList = []
                for currAttr in currDomDict:
                     currVarDomList.append( Domain(currDomDict[currAttr]["Ranges"],
                                                   currDomDict[currAttr]["Values"],
                                                   currAttr))
                self.domDict[currVar] = currVarDomList
            self.constraintDict = dict()
            for currVar in data["Constraints"]:
                formattedFuncDict = dict()
                formattedChecksDict = dict()
                for f in data["Constraints"][currVar]["FuncList"]:
                    formattedFuncDict[f["Name"]] = str(f["Function"])
                for c in data["Constraints"][currVar]["CheckList"]:
                    formattedChecksDict[c["Name"]] = c["ArgList"]
                self.constraintDict[currVar] = Constraint(self.varDict, currVar, formattedFuncDict, formattedChecksDict)
        self.fitness_history = []

    def solve(self, algorithm):
        if algorithm == "Genetic":
            return self.SolveGenetic()
    #     if algorithm == "BackTrack":
    #         return self.SolveBackTrack()
    #
    # def SolveBackTrack(self):
    #     Solution = copy.deepcopy(self.varDict)
    #     return self.BackTrack(Solution)
    #
    # def BackTrack(self,Solution):
    #     if all(dict(Solution).values()):
    #         return Solution
    #     u_var=self.selectUnassignedVar()
    #     for v in self.domDict[u_var]:
    #         self.constraintDict[v].
    #     return  None
    #
    # def selectUnassignedVar(self):
    #     return None

    #Genetic Algorithm based solution implementation method
    def SolveGenetic(self, popSize=100):
        pop = self.population(popSize)
        isSolved = False
        for _ in xrange(100):
            pop = self.evolve(pop)
            for p in pop:
                self.fitness_history.append(self.GlobalValidate(p))
            if any([datum == 0 for datum in self.fitness_history]):
                print "Solution found"
                isSolved = True
                break
        if isSolved:
            Solution = pop[0]
            for k, v in Solution.iteritems():
                print "{0}:{1}".format(k,v['Color'])

            return Solution
        else:
            for datum in self.fitness_history:
                print "**{0}".format([datum])



    def grade(self,pop):
        # 'Find average fitness for a population.'
        summed = reduce(add, (self.GlobalValidate(x) for x in pop), 0)
        return summed / (len(pop) * 1.0)

    def evolve(self, pop, retain=0.2, random_select=0.5, mutate=0.2):
        graded = []
        for x in pop:
            graded.append((self.GlobalValidate(x), x))
        print "********************"

        graded = [x[1] for x in sorted(graded)]
        print graded
        print "********************"
        retain_length = int(len(graded)*retain)
        parents = graded[:retain_length]
        # for parent in parents:
        #     for k,v in parent.iteritems():
        #         print k,v.Color
        #     print "--------------------------------"


        # randomly add other individuals to promote genetic diversity
        for X in graded[retain_length:]:
            if random_select > random(): #random_select-0.01:
                parents.append(X)

        # mutate some individuals
        for parent in parents:
            # if 1==1:
            if mutate > random():
                randomkey = list(parent.keys())[randint(0,len(list(parent.keys()))-1)]
                for currDom in self.domDict[randomkey]:
                    parent[randomkey][currDom.AttributeInVar] = self.getRandomValue(currDom)

        # crossover parents to create children
        parents_length = len(parents)
        desired_length = len(pop) - parents_length
        print "parents_length: {0}".format(parents_length)
        print "desired_length: {0}".format(desired_length)

        children = []
        while len(children) < desired_length:
            male = randint(0, parents_length-1)
            female = randint(0, parents_length-1)
            if male != female:
                male = parents[male]
                female = parents[female]
                # malehalf = dict(male.items()[len(male)/2:])
                # femalehalf = dict(female.items()[:len(female)/2])

                malehalf = copy.deepcopy(male.items()[len(male)/2:])
                femalehalf = copy.deepcopy(female.items()[:len(female)/2])
                malehalf.extend(femalehalf)
                child = dict(malehalf)
                #
                # child = dict(malehalf).update(femalehalf)
                children.append(child)
        print "B:Parents Length: {0}".format(len(parents))
        print "children: {0}".format(children)
        parents.extend(children)
        print "A:Parents Length: {0}".format(len(parents))

        graded = []
        for x in parents:
            graded.append((self.GlobalValidate(x), x))
        print "********************"

        graded = [x[1] for x in sorted(graded)]

        return graded

    def population(self,length):
        pop = []
        # Generate a population of above stated size
        for i in range(0,length):
            individual = copy.deepcopy(self.varDict) #clone variables
            # for each individual generate random values for his variables
            for varName in individual:
                # foreach domain of the current variable
                for currDom in self.domDict[varName]:
                    individual[varName][currDom.AttributeInVar] = self.getRandomValue(currDom)
            pop.append(individual)
        return pop

    # Generates a random value from a given domain
    def getRandomValue(self, domain):

        # Decide (randomly if possible) if the random value will
        # be selected from a values list of a range list
        import time
        time.sleep(0.01)
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
        if sum ==None:
            print "From GlobalValidate None found"

        return sum

    def Randomize(self):
        pass

    def Next(self):
        pass

class Constraint(object):
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
                code = "code="+self.funcList[k]
                exec code
                if(code(varValue, individual[currVal]) == False):
                    counter += 1

        return counter

class Domain(object):
    def __init__(self, Ranges, Values, AttributeInVar):
        self.Ranges = Ranges
        self.Values = Values
        self.AttributeInVar =AttributeInVar


# Create and init the Australian Map CSP
global a
a = CSP("data.json")

result = a.solve("Genetic")

JsonLoader.SaveOutputData(result)


# class var(object):
#     def __init__(self, value):
#         self.Value = value
#
# a.varDict["max"] = var(None)
# a.varDict["adir"] = var(None)
# a.varDict["shalom"]  = var(None)
# a.varDict["shlomo"] = var(None)
# a.varDict["sharon"]= var(None)
#
# # # Populate Variables
# # a.varDict["WA"] = var(None)
# # a.varDict["NT"] = var(None)
# # a.varDict["Q"]  = var(None)
# # a.varDict["SA"] = var(None)
# # a.varDict["NSW"]= var(None)
# # a.varDict["V"]  = var(None)
# # a.varDict["T"]  = var(None)
# #
# dom = Domain(None,["1","2"],"Value")
# a.domDict["max"] =   [dom]
# a.domDict["adir"] =   [dom]
# a.domDict["shalom"]  =   [dom]
# a.domDict["shlomo"] =   [dom]
# a.domDict["sharon"]=   [dom]
#
#
# # # Domains
# # dom = Domain(None,["Red","Green","Blue"],"Color")
# # a.domDict["WA"] =   [dom]
# # a.domDict["NT"] =   [dom]
# # a.domDict["Q"]  =   [dom]
# # a.domDict["SA"] =   [dom]
# # a.domDict["NSW"]=   [dom]
# # a.domDict["V"]  =   [dom]
# # a.domDict["T"]  =   [dom]
# #
# diffFuncList = {"Different": lambda x,y: x.Value != y.Value}
# a.constraintDict["shalom"] = Constraint(a.varDict,"shalom",diffFuncList,{"Different":["max"]})
# a.constraintDict["adir"] = Constraint(a.varDict,"adir",diffFuncList)
# a.constraintDict["max"] = Constraint(a.varDict,"max",diffFuncList,{"Different":["shalom"]})
# a.constraintDict["shlomo"] = Constraint(a.varDict,"shlomo",diffFuncList,{"Different":["sharon"]})
# a.constraintDict["sharon"] = Constraint(a.varDict,"sharon",diffFuncList,{"Different":["shlomo"]})
#
#
# # diffFuncList = {"Different": lambda x,y: x.Color!=y.Color}
# # a.constraintDict["WA"] = Constraint(a.varDict,"WA",diffFuncList,{"Different":["NT","SA"]})
# # a.constraintDict["NT"] = Constraint(a.varDict,"NT",diffFuncList,{"Different":["WA","SA","Q"]})
# # a.constraintDict["Q"]  = Constraint(a.varDict,"Q",diffFuncList,{"Different":["NT","SA","NSW"]})
# # a.constraintDict["SA"] = Constraint(a.varDict,"SA",diffFuncList,{"Different":["WA","NT","Q","NSW","V"]})
# # a.constraintDict["NSW"]= Constraint(a.varDict,"NSW",diffFuncList,{"Different":["Q","SA","V"]})
# # a.constraintDict["V"]  = Constraint(a.varDict,"V", diffFuncList,{"Different":["SA","NSW"]})
# # a.constraintDict["T"]  = Constraint(a.varDict,"T", diffFuncList)
#
# #a.GlobalValidate()
# result = a.solve("Genetic")
#
# JsonLoader.SaveOutputData(result)
