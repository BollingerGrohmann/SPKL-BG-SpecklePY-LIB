import sys

# Dependency check
try:
    import specklepy
    import pandas
    import numpy
    import trimesh

except:
    print('One of the required modules is not installed in your Python env.')
    user_prompt = input('\nDo you want to install all dependencies and check all their versions (y/n)? ')
    user_prompt = user_prompt.lower()
    if user_prompt == 'y':
        import subprocess
        try:
            subprocess.call('python -m pip install --upgrade pip')
            subprocess.call('python -m pip install specklepy pandas numpy trimesh --user')
        except:
            print('WARNING: Installation of modules failed!')
            print('Please use command "python -m pip install specklepy pandas numpy trimesh --user" in your Command Prompt.')
            input('Press Enter to exit...')
            sys.exit()
    else:
        input('Press Enter to exit...')
        sys.exit()