import psutil

ra = int(round(psutil.virtual_memory().total / (1024 ** 3)))
ca = int(psutil.cpu_count(logical=False))

if ra < 2 and ca < 2:
    print('sandbox detected')
else:
    print(' im in ')
