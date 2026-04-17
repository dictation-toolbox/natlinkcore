"""
Update as of 19-02-2023

The update to the below script is now alive as a Python package by the same author. You can install it from PyPi, which lives at https://pypi.org/project/pyuac/, and the source code/home page is located at https://github.com/Preston-Landers/pyuac. Install it using:

pip install pyuac
pip install pypiwin32
Direct usage of the package is:
"""

import pyuac

def main():
    print("Do stuff here that requires being run as an admin.")
    # The window will disappear as soon as the program exits!
    input("Press enter to close the window. >")

if __name__ == "__main__":
    if not pyuac.isUserAdmin():
        print("Re-launching as admin!")
        pyuac.runAsAdmin()
    else:        
        main()  # Already an admin here.