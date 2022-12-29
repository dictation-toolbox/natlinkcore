"""Command Line Program to List Advertised Natlink Exensions."""
import sys
from importlib.metadata import entry_points
import argparse

def extensions_and_folders():
    discovered_extensions=entry_points(group='natlink.extensions')

    for extension in discovered_extensions:
        n=extension.name
        ep=extension.value
        try:
            pathfn=extension.load()
            path=pathfn()

        except Exception as e:
            path = e
        yield n,path
    

def main():
    parser=argparse.ArgumentParser(description="Enumerate natlink extension momdules.")
    args=parser.parse_args()
    for n,path in extensions_and_folders():
        print(f"{n} {path}")
    return 0
 
if '__main__' == __name__:
    main()