#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\unionTypes\generate.py
import os
import yaml
PATH = '../../eve/staticData/uniontypes'
if __name__ == '__main__':
    keys = []
    output = 'class UnionTypes:\n'
    for file_name in os.listdir(PATH):
        data = yaml.load(open(os.path.join(PATH, file_name)))
        output += '    # {}\n'.format(file_name.split('.')[0])
        for k in sorted(data.keys()):
            output += '    {} = "{}"\n'.format(k, k)

        output += '\n'

    f = open('__init__.py', 'w')
    f.write(output)
    f.close()
