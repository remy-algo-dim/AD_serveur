
from cx_Freeze import setup, Executable

# Include the name of all folder or files in your project folder that are nessesary for the project excluding your main flask file.
# If there are multiple files, you can add them into a folder and then specify the folder name.

includefiles = [ 'Config', 'apply_filters.py', 'main_robot_2.py', 'premium_filters.py', 'mysql_functions.py', 'premium_functions.py']
#includes = [ 'jinja2' , 'jinja2.ext'] 

setup(
 name='Linkedin Flask App',
 version = '0.1',
 description = 'Algo Linkedin',
 options = {'build_exe':   {'include_files':includefiles}},
 executables = [Executable('main_robot_2.py')]
)

# In place of main.py file add your main flask file name