import sys

# Dependency check
try:
    import specklepy
    import pandas
    import numpy
    import trimesh
    import openpyxl

except:
    print('One of the required modules cannot be found.')
    user_prompt = input('\nInstall all dependencies (y/n)? ')
    user_prompt = user_prompt.lower() # For case-sensitive work-around
    if user_prompt == 'y':
        import subprocess
        try:
            subprocess.call('python -m pip install --upgrade pip')
            subprocess.call('python -m pip install specklepy pandas numpy trimesh openpyxl --user')
        except:
            print('WARNING: Installation of modules failed!')
            input('Press Enter to exit...')
            sys.exit()
    else:
        print('Input not recognized')
        sys.exit()
