import json

class JsonLoader:

    @staticmethod
    def GetInputData(file_name=None):
        """
        Get the input data from format Json.
        :param file_name: The path to the input json file (Default: 'data.json').
        :return: The input data as Dictionary.
        """
        if file_name is None or type(file_name) is not str or file_name == '':
            file_name = 'data.json'

        with open(file_name) as data_file:
            data = json.load(data_file)
            return data

    @staticmethod
    def SaveOutputData(obj, file_name=None):
        """
        Saves the output Data to a Json file
        :param obj: The object as dictionary to be saved.
        :param file_name: The path to the output json file (Default: 'result.json').
        :return:
        """
        if file_name is None or type(file_name) is not str or file_name == '':
            file_name = 'result.json'

        with open(file_name, 'w') as fp:
            json.dump(obj, fp, default=lambda o: o.__dict__, sort_keys=True, indent=4)
