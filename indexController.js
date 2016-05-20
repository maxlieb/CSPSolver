angular.module('cspApp', ['ui.bootstrap.datetimepicker'])
  .controller('indexController', ['$filter', function ($filter) {
      var ctrl = this;
      ctrl.propertyTypes = ['String', 'Number'];
      ctrl.tabs = ['Variables', 'Domains', 'Constraints'];
      ctrl.currentTab = ctrl.tabs[0];

      ctrl.varStructure = [];
      ctrl.variables = {};
      ctrl.domainValues = [];

      // {variableName: {variableProperty: {Ranges: {}, Values: []}}}
      ctrl.domains = {};
      ctrl.selectedDomain = null;

      ctrl.selectedVarName = '';
      ctrl.selectedVarProperty = '';
      ctrl.varStructureDict = {};
      ctrl.selectedDomainValueType = 'text';

      ctrl.constraints = {};
      ctrl.globalChecks = [];
      ctrl.globalFuncs = [];
      ctrl.selectedConstraint = null;
      // 'FuncList' or 'CheckList'
      ctrl.selectedConstraintProperty = null;

      ctrl.selectTab = function (tab) {
          ctrl.currentTab = tab;

          if (ctrl.currentTab == ctrl.tabs[1]) {
              ctrl.domains = {};
              ctrl.selectedDomain = null;
              angular.forEach(ctrl.variables, function (variable, variableName) {
                  ctrl.domains[variableName] = {};
                  angular.forEach(ctrl.varStructure, function (property) {
                      ctrl.domains[variableName][property.propertyName] = {
                          'Ranges': {
                              'startDate': null,
                              'endDate': null,
                              'hoursJump': null,
                              'skipDays': [],
                              'hoursRange': null,
                              'minutesRange': null
                          },
                          'Values': null
                      }
                  });
              });

              ctrl.varStructureDict = {};
              angular.forEach(ctrl.varStructure, function (property) {
                  ctrl.varStructureDict[property.propertyName] = property.propertyType;
              });

              //console.log(ctrl.domains);
          } else if (ctrl.currentTab == ctrl.tabs[2]) {
              ctrl.constraints = {};
              ctrl.selectedConstraint = null;
              ctrl.selectedConstraintProperty = null;
              angular.forEach(ctrl.variables, function (variable, variableName) {
                  ctrl.constraints[variableName] = { 'FuncList': [], 'CheckList': [] };
              });
              //console.log(ctrl.constraints);
          }
      }

      ctrl.addStructure = function () {
          var emptyPropertyStructure = { propertyName: '', propertyType: ctrl.propertyTypes[0] };
          ctrl.varStructure.push(emptyPropertyStructure);
      }

      ctrl.removeStructure = function (propertyStructure) {
          var indexToRemove = ctrl.varStructure.indexOf(propertyStructure);
          ctrl.varStructure.splice(indexToRemove, 1);
      }

      ctrl.addVariable = function (variableName) {
          ctrl.variables[variableName] = {};
      }

      ctrl.removeVariable = function (variableName) {
          delete (ctrl.variables[variableName]);
      }

      ctrl.setCurrentVar = function (propertyName, domain) {
          ctrl.selectedDomain = domain;
          ctrl.selectedDomainValueType = ctrl.varStructureDict[propertyName] == 'Number' ? 'number' : 'text';
      }

      ctrl.addDomainValue = function (domainValueToAdd) {
          if (!ctrl.selectedDomain.Values) {
              ctrl.selectedDomain.Values = [];
          }

          if (typeof domainValueToAdd == 'string') {
              var listOfValues = domainValueToAdd.split(',');
              angular.forEach(listOfValues, function (value) {
                  var trimedValue = value.trim();
                  if (ctrl.selectedDomain.Values.indexOf(trimedValue) == -1) {
                      ctrl.selectedDomain.Values.push(trimedValue);
                  }
              });
          } else if (ctrl.selectedDomain.Values.indexOf(domainValueToAdd) == -1) {
              ctrl.selectedDomain.Values.push(domainValueToAdd);
          }
      }

      ctrl.removeDomainValue = function (domainValue) {
          var index = ctrl.selectedDomain.Values.indexOf(domainValue);
          if (index != -1) {
              ctrl.selectedDomain.Values.splice(index, 1);
          }
      }

      ctrl.setDay = function (day) {
          index = ctrl.selectedDomain.Ranges.skipDays.indexOf(day);
          if (index >= 0) {
              ctrl.selectedDomain.Ranges.skipDays.splice(index, 1);
          } else {
              ctrl.selectedDomain.Ranges.skipDays.push(day);
          }
      }

      ctrl.setCurrentConst = function (property, constraint) {
          ctrl.selectedConstraint = constraint;
          ctrl.selectedConstraintProperty = property;
      }

      ctrl.removeItemFrom = function (item, array) {
          var index = array.indexOf(item);
          if (index != -1) {
              array.splice(index, 1);
          }
      }

      ctrl.addItemTo = function (item, array) {
          if (typeof item == 'string') {
              var listOfValues = item.split(',');
              angular.forEach(listOfValues, function (value) {
                  var trimedValue = value.trim();
                  if (array.indexOf(trimedValue) == -1) {
                      array.push(trimedValue);
                  }
              });
          } else if (array.indexOf(item) == -1) {
              array.push(item);
          }
      }

      ctrl.addGlobalConstraintCheck = function (globalConstraintCheckToAdd) {
          angular.forEach(ctrl.constraints, function (varConstraint) {
              varConstraint.CheckList.push(globalConstraintCheckToAdd);
          });

          ctrl.globalChecks.push(globalConstraintCheckToAdd);
      }

      ctrl.removeGlobalConstraintCheck = function (check) {
          var globalIndex = ctrl.globalChecks.indexOf(check);
          if (globalIndex != -1) {
              ctrl.globalChecks.splice(globalIndex, 1);
          }

          angular.forEach(ctrl.constraints, function (varConstraint) {
              var index = varConstraint.CheckList.indexOf(check);
              if (index != -1) {
                  varConstraint.CheckList.splice(index, 1);
              }
          });
      }

      ctrl.addGlobalConstraintFunc = function (globalConstraintFuncToAdd) {
          angular.forEach(ctrl.constraints, function (varConstraint) {
              varConstraint.FuncList.push(globalConstraintFuncToAdd);
          });

          ctrl.globalFuncs.push(globalConstraintFuncToAdd);
      }

      ctrl.removeGlobalConstraintFunc = function (func) {
          var globalIndex = ctrl.globalFuncs.indexOf(func);
          if (globalIndex != -1) {
              ctrl.globalFuncs.splice(globalIndex, 1);
          }

          angular.forEach(ctrl.constraints, function (varConstraint) {
              var index = varConstraint.FuncList.indexOf(func);
              if (index != -1) {
                  varConstraint.FuncList.splice(index, 1);
              }
          });
      }

      ctrl.saveToPc = function (data, filename) {

          if (!data) {
              console.error('No data');
              return;
          }

          if (!filename) {
              filename = 'download.json';
          }

          if (typeof data === 'object') {
              data = JSON.stringify(data, undefined, 2);
          }

          var blob = new Blob([data], { type: 'text/json' }),
            e = document.createEvent('MouseEvents'),
            a = document.createElement('a');

          a.download = filename;
          a.href = window.URL.createObjectURL(blob);
          a.dataset.downloadurl = ['text/json', a.download, a.href].join(':');
          e.initEvent('click', true, false, window,
              0, 0, 0, 0, 0, false, false, false, false, 0, null);
          a.dispatchEvent(e);
      };

      ctrl.test = function () {
          var a = 0;
          ctrl.getCSP();
          //console.log(ctrl.variables);
          //console.log(JSON.stringify(ctrl.variables));
          //console.log($filter('date')(domain.Ranges.startDate, 'MMM d yyyy H:mm'));
      }

      ctrl.getCSP = function () {
          var csp = {
              Vars: {},
              Domains: {},
              Constraints: {}
          };

          csp.Vars = ctrl.variables;
          csp.Domains = ctrl.domains;
          csp.Constraints = ctrl.constraints;

          angular.forEach(csp.Vars, function (variable, variableName) {
              angular.forEach(ctrl.varStructure, function (property) {

                  if (csp.Vars[variableName][property.propertyName] == undefined) {
                      csp.Vars[variableName][property.propertyName] = null;
                  }
              });
          });

          angular.forEach(csp.Domains, function (domainVariable) {
              angular.forEach(domainVariable, function (variableProperty) {
                  variableProperty.Ranges = ctrl.parseDomainRange(variableProperty.Ranges);
              });
          });

          console.log(csp);

          return csp;
      }

      ctrl.parseDomainRange = function (range) {
          if (!range) return null;
          if (!range.startDate && !range.endDate && !range.hoursJump && !range.hoursRangeStart && !range.hoursRangeEnd &&
              !range.minutesRangeStart && !range.minutesRangeEnd && (!range.skipDays || range.skipDays.length == 0)) return null;

          var startDate = '';
          var endDate = '';
          var hoursJump = '';
          var hoursRange = '';
          var minutesRange = '';
          var skipDays = [];

          if (range.startDate) startDate = $filter('date')(range.startDate, 'MMM d yyyy H:mm');
          if (range.endDate) endDate = $filter('date')(range.endDate, 'MMM d yyyy H:mm');
          if (range.hoursJump) hoursJump = '' + range.hoursJump;

          if (!range.hoursRangeStart && range.hoursRangeEnd) range.hoursRangeStart = 0;
          if (!range.hoursRangeEnd && range.hoursRangeStart) range.hoursRangeEnd = 23;
          if (range.hoursRangeStart) hoursRange = '' + range.hoursRangeStart + '-' + range.hoursRangeEnd;

          if (!range.minutesRangeStart && range.minutesRangeEnd) range.minutesRangeStart = 0;
          if (!range.minutesRangeEnd && range.minutesRangeStart) range.minutesRangeEnd = 60;
          if (range.minutesRangeStart) minutesRange = '' + range.minutesRangeStart + '-' + range.minutesRangeEnd;

          if (range.skipDays.length) skipDays = range.skipDays;

          return [startDate, endDate, hoursJump, hoursRange, minutesRange, skipDays];
      }

      ctrl.saveCSP = function () {
          var csp = ctrl.getCSP();
          ctrl.saveToPc(csp, 'data.json');
      }
  }]);
