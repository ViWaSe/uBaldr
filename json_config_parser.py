# Config-Parser for .json config files
# Can be used to parse data from a json-file
# Currently 1 and 2 json-layers are supported, 2 means that the file is structured like >>>{"Example-Group": [{"example param": "example string"], "example-Group 2": [{"Example int-data": 2, ....<<<
# To parse a json-file, create a config()-Object and get the data you want with the get()-function. (t.ex example=config(file='example.json', layers=2) ==> example.get('group', 'param'))
# use the save-param()-function to save or update data the same way as getting it with the get()-function (t.ex. example.save_param('group', 'param', 'new value'))

version = '2.0'

import json

class config(object):
    
    def __init__(
            self, 
            file='config.json', 
            layers=2
    ):
        self.file   = file
        self.layers = layers

        with open(self.file) as f:
            self.conf = json.load(f)
    
# get any data by the original name in the json-file   
    def get(
            self, 
            group=None, 
            param=None
    ):
        if self.layers==1:
            return self.conf[param]
        elif self.layers==2:
            section = self.conf[group]
            setting = section[0]
            par = setting[param]
            return par

# Save parameter
    def save_param(
            self, 
            group=None, 
            param=None, 
            data=None
    ):
        if self.layers == 1:
            self.conf[param] = data
        elif self.layers == 2:
            section = self.conf[group]
            setting = section[0]
            setting[param] = data

        with open(self.file, 'w') as file:
            json.dump(self.conf, file)

# Update the whole json-file with a python-lib
    def save_lib(self, lib, filename):
        with open(filename, 'w') as f:
            json.dump(lib, f)

