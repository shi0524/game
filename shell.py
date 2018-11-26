# -*- coding: utf-8 –*-


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

if len(sys.argv) == 3:
    env = sys.argv[1]
    path = sys.argv[2]
else:
    env = 'local'
    path = '/Users/kaiqigu/my_notebook/game/'
sys.path.insert(0, path)

import settings
settings.set_env(env)
