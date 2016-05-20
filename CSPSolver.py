from random import randint, random, choice, sample
from operator import add
import copy
from JsonLoader import JsonLoader
from dateutil.rrule import *
from datetime import datetime, timedelta
import time
import calendar
import xml.etree.ElementTree as etree
import os

global perfIterCount
def strToTime(str):
    return datetime.strptime(str, '%b %d %Y %H:%M')
def strToDay(str):
    return datetime.strptime(str, '%b %d %Y %H:%M').replace(hour=0, minute=0)
def timeToStr(t):
    return t.strftime("%b %d %Y %H:%M")
"""
Function to handle date ranges
Input is a tuple of this form: (start date, end date, interval in minutes, excluded week days, work hours, work minutes)
    The first 3 are mandatory, first 2 will have this form:
        mmm dd YYYY HH:MM
        for example: 'Jun 7 2016  9:00'
    The third will be a the number of minutes separating each value in the output range list.
        Example: 60 will give a value for every hour
    The forth member is a comma separated list of days to exclude, for example : "SA, FR"
        The following short week day names must be used: SU, MO, TU, WE, TH, FR, SA
    The fifth member is a a string of the form "HH-HH" the represents business
    hours range in 24 hour format. range includes end hour.
        Example: '9-18'
    The last one is similar to work hours and defines minutes after start hour and end hour
"""
def getdaterangegen(timerange, cache=None):
    start_date = strToTime(timerange[0]) #datetime.strptime(timerange[0], '%b %d %Y %H:%M')
    end_date = strToTime(timerange[1]) #datetime.strptime(timerange[1], '%b %d %Y %H:%M')
    interval = timerange[2]
    week_days = {"SU": SU, "MO": MO, "TU": TU, "WE": WE, "TH": TH, "FR": FR, "SA": SA}
    if len(timerange) > 3 and timerange[3]:
        for day in [x.replace(" ", "") for x in str(timerange[3]).split(",")]:
            del week_days[day]
    hours = range(0, 24)
    if len(timerange) > 4 and timerange[4]:
        rangebounds = [int(x) for x in str(timerange[4]).split("-")]
        hours = range(rangebounds[0], rangebounds[1]+1)
    minutes = range(0, 60)
    if len(timerange) > 5 and timerange[5]:
        rangebounds = [int(x) for x in str(timerange[5]).split("-")]
        minutes = range(rangebounds[0], rangebounds[1] + 1)
    times = rrule(MINUTELY,
                  dtstart=start_date,
                  until=end_date,
                  byweekday=week_days.values(),
                  byhour=hours,
                  byminute=minutes,
                  interval= interval, cache=True)
    for single_date in times:
        yield timeToStr(single_date)#single_date.strftime("%b %d %Y %H:%M")

def getdaterange(timerange, cache=None):
        key = timerange[0] + timerange[1]
        if cache and len(cache) > 0:            
            if cache[key]:
                return cache[key]

        res = [x for x in getdaterangegen(timerange)]
        if cache == {} or (cache and len(cache) > 0):
            cache[key] = copy.deepcopy(res)
        return copy.deepcopy(res)

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
        self.dateRangeCache = {}

    def solve(self, algorithm, single = False, forward_checking = True, MaxSteps = 1000):
        if algorithm == "Genetic":
            return self.SolveGenetic()
        if algorithm == "BackTrack":
            return self.SolveBackTrack(forward_checking, single)
        if algorithm == "MinConflicts":
            return self.MinConflicts(MaxSteps)

    def SolveBackTrack(self, forward_checking, single):        
        return self.BackTrack([], copy.deepcopy(self.varDict),copy.deepcopy(self.domDict), forward_checking, single)

    #region bactrack
    def BackTrack(self,Solutions, assignment, domains, forward_checking, single, max_solutions = 100):
        global perfIterCount
        perfIterCount+=1
        # Check if solution found
        if all([all(i.values()) for i in assignment.values()]):
            Solutions.append(copy.deepcopy(assignment))
            print "solution {0} found!".format(len(Solutions))
            return Solutions

        # Calculate the total number of possible values from all of the domains for each variable
        domSizes = {}
        # for each variable
        for var in domains:
            domSizes[var] = 0
            # for each domain of that variable
            for dom in domains[var]:
                # for values and ranges seperately
                if dom.Values:
                    domSizes[var]+= len(dom.Values)
                if dom.Ranges:
                    # for each range
                    for r in dom.Ranges:
                        try:
                            int (r[0])
                            domSizes[var]+=len(range(r[0],r[1]))
                        except ValueError:
                            domSizes[var]+=len(getdaterange(r, self.dateRangeCache))

        # same idea for constraints
        checkSizes = {}
        # for each variable
        for var in self.constraintDict:
            checkSizes[var] = 0
            # for each "checklist"
            for chk in self.constraintDict[var].checklist:
                checkSizes[var]+= len(self.constraintDict[var].checklist[chk])
        
        # Mix the Degree and Minimum Remaining Values (MRV) heuristics
        lst = [(-checkSizes[var],domSizes[var],var) for var in domSizes]
        lst.sort()
        lst = [x[-1] for x in lst]        

        # get a un-assigned variable to assign
        u_var = None
        for var in lst:
            if not all(assignment[var].values()):
                u_var = var
                break

        # attempt to find a suitable assignment
        allDomValues = self.getAllDomValues(u_var,domains)
        # for each key (attribute in variable) and variable list in all domain values
        for k,l in allDomValues.iteritems():
            # and for each variable in that list
            for val in l:
                # Check the assignment
                testAssignment = copy.deepcopy(assignment)
                testAssignment[u_var][k] = val
                result = self.constraintDict[u_var].Validate(testAssignment)

                # if value fits ( no violations )
                if result == 0:                    
                    assignment[u_var][k] = val
                    
                    # do forward checking domain optimitation
                    domains_new = copy.deepcopy(domains)
                    if forward_checking:
                        # for each variable
                        for X in assignment:
                            # for each of it's connected variables
                            for conkey in self.constraintDict[X].checklist:
                                for Y in self.constraintDict[X].checklist[conkey]:
                                    # if it's not assigned
                                    if Y!= "*" and not any(assignment[Y].values()):
                                        domvals = self.getAllDomValues(Y,domains_new)
                                        # for each value in domain test if it will work now...
                                        for key, vallist in domvals.iteritems():
                                            for val in vallist:
                                                # Check the assignment
                                                testAssignment = copy.deepcopy(assignment)
                                                testAssignment[Y][key] = val
                                                result = self.constraintDict[Y].Validate(testAssignment)
                                                
                                                # remove from domains
                                                if result > 0:
                                                    # find the domain in new domain structure
                                                    for dom in domains_new[Y]:
                                                        if dom.AttributeInVar == key:
                                                            # remove the value
                                                            if dom.Values and val in dom.Values:
                                                                dom.Values.remove(val)
                                                            elif dom.Ranges:
                                                                # re-shape ranges to exclude the value                                                                
                                                                for r in dom.Ranges:
                                                                    if r[0] > val and [1] < val:
                                                                        bkp = copy.deepcopy(r)
                                                                        dom.Ranges.remove(r)
                                                                        dom.Ranges.append((bkp[0],val))
                                                                        dom.Ranges.append((val,bkp[1]))
                                                            #print "assignment:{0}, new domain for {1} is {2}".format([(i, assignment[i]['Color']) for i in assignment if assignment[i]['Color']], Y, dom.Values)

                                    
                                
                    result = self.BackTrack(Solutions,assignment,domains_new,forward_checking,single)
                    if Solutions and (single or len(Solutions) == max_solutions):
                        return Solutions
                    else:
                        assignment[u_var][k] = None
        return Solutions
    def getAllDomValues(self, u_var ,domains):
        for dom in domains[u_var]:
            allDomValues = {}
            allDomValues[dom.AttributeInVar] = []
            if dom.Values:
                allDomValues[dom.AttributeInVar] = copy.deepcopy(dom.Values)
            if dom.Ranges:
                for r in dom.Ranges:
                    try:
                        int(r[0])
                        for i in range(r[0], r[1]):
                            allDomValues[dom.AttributeInVar].append(i)
                    except ValueError:
                        allDomValues[dom.AttributeInVar] = getdaterange(r, self.dateRangeCache)
        return allDomValues

    #endregion

    #region MinConflicts
    def MinConflicts(self,MaxSteps = 1000):
        # Generate some assignment
        assignment = copy.deepcopy(self.varDict)
        for varName in assignment:
            for currDom in self.domDict[varName]:
                assignment[varName][currDom.AttributeInVar] = self.getRandomValue(currDom)
        # Do up to MaxSteps iterations of the algorithm
        for _ in xrange(MaxSteps):
            global perfIterCount
            perfIterCount+=1
            # Check if assignment is valid
            confVarlist = self.GlobalValidate(assignment,True)
            print "Conflicts:{0}".format(len(confVarlist))
            if len(confVarlist) == 0:
                return assignment
            else:
                # select a random variable to cahnge
                rndConfVar = choice(confVarlist)
                # try all values form his domain and try if the cause less conflicts
                allDomValues = self.getAllDomValues(rndConfVar,self.domDict)
                min = 999
                minvalues = {}
                for k,valList in allDomValues.iteritems():
                    for val in valList:
                        testAssignment = copy.deepcopy(assignment)
                        testAssignment[rndConfVar][k] = val
                        result = self.constraintDict[rndConfVar].Validate(testAssignment)
                        if result == min:
                            if not minvalues[k]:
                                minvalues[k] = []
                            minvalues[k].append(val)
                        if result < min:
                            min = result
                            minvalues = {}
                            minvalues[k] = []
                            minvalues[k].append(val)
                            
                minatt = choice(minvalues.keys())
                minval = choice(minvalues[minatt])
                # assign the new, less conflictd value
                assignment[rndConfVar][minatt] = minval            

        return None
    #endregion

    #region genetic    
    def SolveGenetic(self, popSize=100):
        pop = self.population(popSize)
        isSolved = False
        for _ in xrange(1000):
            global perfIterCount
            perfIterCount+=1
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
                print "{0}:{1}".format(k,v.values())

            return Solution
        else:
            for datum in self.fitness_history:
                print "**{0}".format([datum])

    def grade(self,pop):
        # 'Find average fitness for a population.'
        summed = reduce(add, (self.GlobalValidate(x) for x in pop), 0)
        return summed / (len(pop) * 1.0)

    def evolve(self, pop, retain=0.2, random_select=0.5, mutate=0.5):
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
        for X in graded[retain_length:2*retain_length]:
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

                malehalf = copy.deepcopy(sorted(male.items())[len(male)/2:])
                femalehalf = copy.deepcopy(sorted(female.items())[:len(female)/2])
                # malehalf = sample(copy.deepcopy(male.items()),len(male)/2)
                # femaleCopy = copy.deepcopy(female.items())
                # for x in femaleCopy:
                #     if not malehalf.__contains__(x):
                #         malehalf.append(x)



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
            print "Generated {0}".format(len(pop))
        return pop
    #endregion

#region universal methods
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
            r = domain.Ranges[randint(0, len(domain.Ranges)-1)]
            try:
                test = int(r[0])
                r= range(r[0],r[1]+1)
                val = r[randint(0, len(r)-1)]
            except ValueError:
                times = getdaterange(r, self.dateRangeCache)
                val = times[randint(0, len(times)-1)]
        else:
            val = domain.Values[randint(0,len(domain.Values)-1)]

        return val

    # Call all variables validation methods and collect results
    def GlobalValidate(self, individual = None, getConflictedList=False):
        if (individual == None):
            individual = copy.deepcopy(self.varDict)
        sum = 0
        clist = []
        for k,val in self.constraintDict.iteritems():
            ret = val.Validate(individual)
            sum += ret
            if ret > 0:
                clist.append(k)
        if getConflictedList:
            return clist
        print "Individual violation Count {0}".format(sum)
        return sum

#endregion

class Constraint(object):
    def __init__(self, varDict, varKey, funcList=None, checklist=None):
        self.varDict = varDict
        self.varKey = varKey
        self.funcList = funcList if funcList else dict()
        self.checklist = checklist if checklist else dict()

    def Validate(self, individual = None):
        counter = 0
        varValue = individual[self.varKey]
        allOthers = copy.deepcopy(individual)
        del allOthers[self.varKey]


        if (individual == None):
            individual = self.varDict


        #Run all requriered checks (check functions)
        for k, values in self.checklist.iteritems():
            code = "code=" + self.funcList[k]
            exec code
            #if checks are in raletion to other variables
            if values and values[0] != "*":
                #check for each variable related
                for currVal in values:
                    if(code(varValue, individual[currVal]) == False):
                        counter += 1
            # if in relation to all others
            elif values and values[0] == "*":
                counter += code(varValue, allOthers.values())
            #if checks are considering only the this variable
            elif code:
                if (code(varValue) == False):
                    counter += 1

        return counter

class Domain(object):
    def __init__(self, Ranges, Values, AttributeInVar):
        self.Ranges = Ranges
        self.Values = Values
        self.AttributeInVar =AttributeInVar


def DisplayCalendar(result, csp):
    if isinstance(result, list):
        result = result[randint(0, len(result) - 1)]
    start_date_str = csp.domDict.popitem()[1][0].Ranges[0][0]
    end_date_str = csp.domDict.popitem()[1][0].Ranges[0][1]
    start_date = strToTime(start_date_str)
    end_date = strToTime(end_date_str)
    months = [(x.year, x.month) for x in
              rrule(MONTHLY, dtstart=start_date.replace(day=1), until=end_date.replace(day=1))]
    allmonhtml = ""
    for mon in months:
        # Generate basic calendar html string
        myCal = calendar.HTMLCalendar(calendar.SUNDAY)
        htmlStr = myCal.formatmonth(mon[0], mon[1])
        htmlStr = htmlStr.replace("&nbsp;", " ")

        # Explore generated html elements
        root = etree.fromstring(htmlStr)
        # for each subject
        for subject, assign in result.iteritems():
            for attribute, value in assign.iteritems():
                # get the assigned time
                if attribute == "Time":
                    currTime = strToTime(value)
                    # loop through calendar cells
                    for elem in root.findall("*//td"):
                        # If Week day matches
                        if elem.get("class") == currTime.strftime("%a").lower():
                            # If month day matches and it's actually the same month (and not by chance)
                            if int(elem.text) == currTime.day and currTime.month == mon[1]:
                                br = etree.SubElement(elem, "br")
                                br.tail = subject + "<br/>" + "(year " + str(
                                    result[subject]["Year"]) + ")" + "<br/>" + currTime.strftime("%H:%M")

        if allmonhtml != "":
            allmonhtml += "<br/>"
        allmonhtml += etree.tostring(root).replace("&lt;", "<").replace("&gt;", ">"). \
            replace("border=\"0\" cellpadding=\"0\" cellspacing=\"0\"",
                    "border=\"1\" cellpadding=\"1\" cellspacing=\"1\" "). \
            replace("<td ", "<td height = \"100\" width = \"200\" valign=\"Top\"")
    calfile = open("cal.html", "w")
    calfile.write(allmonhtml)
    calfile.close()
    os.system("cal.html")

def DisplayStyledCalendar(result,csp):
    if isinstance(result, list):
        result = result[randint(0, len(result) - 1)]
    start_date_str = csp.domDict.popitem()[1][0].Ranges[0][0]
    start_date = strToTime(start_date_str)
    defaultDateString = "'"+start_date.strftime("%Y-%m-%d")+"'"
    EventArray = "[\n"
    for title in result:
        stime = strToTime(result[title]["Time"]).strftime("%Y-%m-%dT%H:%M:%S")
        etime = (strToTime(result[title]["Time"]) + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%S")
        sItem = "\t{\n\t\ttitle: '" + title + "',\n\t\tstart: '" + stime + "',\n\t\tend: '" + etime + "'\n\t}"
        EventArray+= sItem+",\n"
    EventArray = EventArray[:-2] + "\n]"

    template = open("fullcalendar\demos\CSPResultTemplate.html","r")
    htmldata = template.read()
    template.close()
    htmldata = htmldata.replace("DEFAULTDATE",defaultDateString).replace("EVENTARRAY",EventArray)
    out = open("fullcalendar\demos\ResultCal.html","w")
    out.write(htmldata)
    out.close()
    os.system("fullcalendar\demos\ResultCal.html")


def DisplayUSMap(result):
    if isinstance(result, list):
        result = result[randint(0, len(result) - 1)]
    US_COUNTRIES = ["HI", "AK", "FL", "SC", "GA", "AL", "NC", "TN", "RI", "CT", "MA", "ME", "NH", "VT", "NY", "NJ",
                    "PA", "DE", "MD", "WV",
                    "KY", "OH", "MI", "WY", "MT", "ID", "WA", "TX", "CA", "AZ", "NV", "UT", "CO", "NM", "OR", "ND",
                    "SD", "NE", "IA", "MS",
                    "IN", "IL", "MN", "WI", "MO", "AR", "OK", "KS", "LA", "VA"]

    STATE_TO_COLOR = {}
    for x in result:
        STATE_TO_COLOR[x] = result[x]["Color"]
    print STATE_TO_COLOR

    new_style = 'font-size:12px;fill-rule:nonzero;stroke:#FFFFFF;stroke-opacity:1;stroke-width:0.1;stroke-miterlimit:4;stroke-dasharray:none;stroke-linecap:butt;marker-start:none;stroke-linejoin:bevel;fill:'

    tree = etree.parse('us-map.svg')
    root = tree.getroot()
    for child in root:
        if 'id' in child.attrib and child.attrib['id'] in US_COUNTRIES:
            child.attrib['style'] = new_style + STATE_TO_COLOR[child.attrib['id']]

    tree.write('counties_new.svg')
    os.system('results.html')

global perfIterCount
perfIterCount = 0
myCSP = CSP(path="DemoInputs\ExamsShort.json")
DisplayStyledCalendar(myCSP.solve("BackTrack"),myCSP)

# testOutput = ""
# BackTrackSingle = False
# DispalyGraphicOutput = True
# SampleCount = 1
# for alg in ["MinConflicts"]:
#     probCnt = 1
#     for tst in ["examdata.json"]:
#         r = range(SampleCount)
#         if tst =="examdata2.json" and alg in ["Genetic", "MinConflicts"]:
#             r = []
#         if tst == "USAData.json" and alg == "Genetic":
#             r= [0]
#         for i in r:
#             global a
#             #"examdata2.json"
#             a = CSP(tst)#("data.json")
#
#             #alg = "BackTrack"
#             #alg = "Genetic"
#             #alg = "MinConflicts"
#             global perfIterCount
#             perfIterCount = 0
#             perfStartTime = time.time()
#             if alg != "BackTrack":
#                 result = a.solve(alg)#("Genetic")
#             else:
#                 result = a.solve("BackTrack",BackTrackSingle)
#             perfEndTime = time.time()
#             print "Execution Time (Sec) : {0}".format(perfEndTime - perfStartTime)
#             print "Number Of Iterations : {0}".format(perfIterCount)
#
#             if result and DispalyGraphicOutput:
#                 if tst in ("examdata2.json","examdata.json"):
#                     DispalyStyledCalendar(result,a)
#                 elif tst == "USAData.json":
#                     DisplayUSMap(result)
#             JsonLoader.SaveOutputData(result)
#             print result
#             testOutput+= "Algorithm {0} ,Problem {1}, Sample {2}:\nTime (Sec): {3}\nIterations: {4}\n".format(alg, probCnt, i+1, perfEndTime - perfStartTime,perfIterCount)
#             # print testOutput
#             # try:
#             #     input("Press Enter to continue...")
#             # except Exception:
#             #     pass
#             global perfIterCount
#             perfIterCount = 0
#         testOutput+= "-----------------------------------------------------------------\n"
#         probCnt+=1
#     testOutput += "=================================================================\n"
#
# print testOutput