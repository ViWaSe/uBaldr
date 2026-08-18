# v2.2.0
import json
import sys

with open('params/versions.json', 'r') as v:
    versions = json.load(v)

platform = sys.platform

modules = []
for name in versions:
    modules.append(name)

def by_module(module):
    sub = versions[module]
    if type(sub) is list:
        if len(sub) < 4:
            return str(f'{sub[0]}.{sub[1]}.{sub[2]}')
        else:
            return str(f'{sub[0]}.{sub[1]}.{sub[2]}{sub[3]}')
    else:
        return versions[module]

def all():
    return versions

def version_string(sub):
    return str(f'{sub[0]}.{sub[1]}.{sub[2]}')