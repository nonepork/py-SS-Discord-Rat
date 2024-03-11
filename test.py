with open("main-developer.py", "r", encoding="utf-8") as f:
    data = f.readlines()

# lines that requires input:
ltri = [73, 74, 75]
#for i in ltri:

# lines that need to be deleted:
ltntbd = [22, 31, 32, 63, 84, 85, 105, 112, 146, 152, 180, 233, 510, 596]
for i in range(0, len(ltntbd)):
    data.pop(ltntbd[i]-(i+1))

with open("test.txt", "w", encoding="utf-8") as f:
    for line in data:
        f.write(line)
