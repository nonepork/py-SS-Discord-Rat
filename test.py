with open("main-developer.py", "r", encoding="utf-8") as f:
    data = f.readlines()

# lines that requires input:
ltri = [73, 74, 75]
for i in ltri:
    data[i-1] = data[i-1].replace("''", "'test'") # very ugly, very nice xD

# lines that need to remove value:
ltntrv = [77]
for i in ltntrv:
    line = data[i-1].split("=")
    data[i-1] = line[0] + " ''\n"

# lines that need indent once:

# lines that need indent twice:

# lines that need to be deleted:
#ltntbd = [22, 31, 32, 63, 84, 85, 105, 112, 146, 152, 180, 233, 510, 596]
#for i in range(0, len(ltntbd)):
#    data.pop(ltntbd[i]-(i+1))

with open("test.txt", "w", encoding="utf-8") as f:
    for line in data:
        f.write(line)
