"""Command Line Program to List Advertised Natlink Exensions."""
import sys
from importlib.metadata import entry_points
import argparse

def main():
    parser=argparse.ArgumentParser(description="Enumerate natlink extension momdules.")
    args=parser.parse_args()

    discovered_extensions=entry_points(group='natlink_extensions')

    for extension in discovered_extensions:
        n=extension.name
        ep=extension.value
        try:
            pathfn=extension.load()
            path=pathfn()

        except Exception as e:
            path = e   

        print(f"{n} {path}")
    return 0
 
if '__main__' == __name__:
    main()