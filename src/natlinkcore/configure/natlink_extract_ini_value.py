import argparse
import sys
from natlinkcore.configure.natlinkconfigfunctions import NatlinkConfig
import configparser
from pathlib import Path
import configparser

def get_config_value(config, section, key):
    if not config.has_section(section):
        raise configparser.NoSectionError(section)
    if not config.has_option(section, key):
        raise configparser.NoOptionError(key, section)
    return config.get(section, key)
 
def main():
    parser = argparse.ArgumentParser(description=
        f"""prints the value for the key in the section of natlink.ini to standard out.  You can also ask for the full path to the ini file.  
        for example, to get the dragonflyuserdirectory key in the directories section:
        {sys.argv[0]} --section 'directories' --key dragonflyuserdirectory
        """)
    parser.add_argument('-i', "--ini_file",action='store_true',  help='print the full path to the natlink.ini file')
 


    parser.add_argument('-s', '--section', type=str,  help='Section name')
    parser.add_argument('-k', '--key', type=str, help='Key name')

    args = parser.parse_args()


    try:
        config=NatlinkConfig()
        config_path=config.natlinkconfig_path
        config_file=Path(config_path)/"natlink.ini"
        if args.ini_file:
            print(config_file)
            exit(0)
        if not (args.key and args.section):
            raise Exception("Must supply key and section or -i/--ini_file")
        config=configparser.ConfigParser()
        config.read(config_file)
        v=get_config_value(config,args.section,args.key)
        print(f"{v}")
    except Exception as e:
        print(e)
        exit(-1)


if __name__ == "__main__":
    main()
