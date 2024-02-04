import os
with open('newfile', 'wb') as f:
    f.seek(26000000)
    f.write(b'\0')

print(os.stat('newfile').st_size)
