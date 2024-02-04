import os
from filesplit.merge import Merge

for i in os.listdir('output'):
    if i != 'manifest':
        os.rename('output/' + i, 'output/' + i[:-6])

Merge('output', os.getcwd(), 'test').merge()
