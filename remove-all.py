from pathlib import Path
import re
import os

print('\nSTEP 1: Identifying what file to remove')
# link slug
folder = input('Folder to use: ')

#  Blade files that will be found in the folder
blade_files = []

for path in Path(f'../roomroster/resources/views/dashboards/event-owner/event/{folder}').rglob('*.blade.php'):
  blade_files.append(path)

# If it doesnt exist
if len(blade_files) <= 0:
  print('Not a valid folder')
  exit()

# Print the files needed
for blade in blade_files:
  print("Available Blade Files")
  print(f"- {blade}")

# origin blade file
origin = input('Origin point (index): ')

# Set default to index
if len(origin) <= 1:
    origin = 'index'
    print('Switching to the default of "index"')

# Blade file path that is called in controller
index_blade_path = f'dashboards.event-owner.event.{folder}.{origin}'

# Controller
controller_path = False

# Define the document
newdoc = ''


print('STEP 2: Changing controller')
# Finding the controller
for path in Path('../roomroster/app/Http/Controllers/Client/Dashboard/EventOwner/Event').rglob('*.php'):

  # read file
  with open(path, 'r') as reader:
    text = reader.read()

    if index_blade_path in text:
      # Set controller variable
      controller_path = path

      filepath = re.sub(r"\.\.\/roomroster", "", str(controller_path))

      # search_string = "\$compact = [\w\(\),\'\";\-\$\?:\s.]*\",\$compact\)\;"
      search_string = f"\$compact = [\w\(\),\'\";\-\$\?:\s.]*{origin}[\"\']\,[\s]\$compact\)\;"
      # start and end index
      start = re.search(search_string, text)

      if start == None:
        print('Already up to date. Not able to merge to new dashboard')
        print(filepath)
        exit()

       # Compact section
      compactvar = re.search(r"\$compact = compact\([a-zA-Z\s\',]*\)", start.group(0))

      if compactvar == None:
        print('Already up to date. Not able to merge to new dashboard')
        exit()
      compact = re.sub(r"\$compact = ", '', compactvar.group(0))

      # new path for view
      newpathsearch = re.search(r"view\([\"\']events.[\w\.]*", start.group(0))

      if newpathsearch == None:
        print('An Error Occured. Can\'t find new path')
        print(f'Controller: {path}')
        exit()
      newpath = re.sub(r"view\([\'\"]", '', newpathsearch.group(0))
      # text to be replaced
      oldtext = start.group(0)
      newtext = f'return view(\'{newpath}\', {compact});'
      if newpath == None or len(newpath) <= 1:
        print('Already up to date. Not able to merge to new dashboard')
        print(f'Controller: {path}')
        exit()

      # new document
      newdoc = text.replace(oldtext, newtext)
      print('\n')
      print('** New Text Changed **')
      print(newtext)
      print(filepath)

if controller_path:
  with open(controller_path, 'w') as writer:
    writer.write(newdoc)

#############################################################
# Check to see if the @include blade files are used elsewhere
############################################################
removeable_files = []

def fileContains(word, path):
  with open(path, 'r') as reader:
    lines = reader.readlines()
    repeats = 0
    for line in lines:
      if word in line:
          repeats += 1
    return repeats

def yesOrNo(msg):
  loop = True
  while loop:
    answer = input(msg)
    if answer == 'y' or answer == 'yes':
      loop = False
      return True
    elif answer == 'n' or answer == 'no':
      loop = False
      return False
    else:
      print('Please type "y" or "n"')

for blade in blade_files:

  with open(blade, 'r') as reader:
    lines = reader.readlines()
    for line in lines:
      if "@include" in line:
        # Find the path to blade files
        quotedtext = re.search(r"\'(.+?)\'", line)
        # remove the quotes
        result = re.search(r"[^\']*[^\']", quotedtext.group(0))

        # Blade file path
        blade_file = result.group(0)
        # print('- line -')

        occurances = 0
        # Remove the basic template includes
        if blade_file != 'dashboards.event-owner.event.partials.navigation' and blade_file != 'dashboards.event-owner.event.partials.page-title':
          # Check if it has repeats
          for newpath in Path('../roomroster/resources/').rglob('*.blade.php'):
            occurances += fileContains(blade_file, newpath)

          if occurances <= 1 and blade_file not in removeable_files:
            removeable_files.append(blade_file)

# Show files that don't have repeat
if len(removeable_files) <= 0:
  print('\nNote: No need to remove any blade files. All are still being used')
else:
  print('\nBelow blade files are unused and can be removed:')
  for file in removeable_files:
    new_file = re.sub(r"\.", "/", file)
    print(f"    - resources/views/{new_file}")
  # Promt whether the files should be deleted
  answer = yesOrNo('\n\nWould you like to remove these files?: ')
  if answer:
    for file in removeable_files:
      file_name = re.sub(r"\.", "/", file)
      path = f"resources/views/{new_file}"
      os.remove(path)
      print(f"File Deleted. {path}")

######################################################
# Remove blade file that is used
######################################################

# Remove file if needed
origin_blade_file = f"../roomroster/resources/views/dashboards/event-owner/event/{folder}/{origin}.blade.php"

# Check if it exists
if os.path.exists(origin_blade_file):
  answer = yesOrNo('\n\nWould you like to delete the file? (y/n): ')
  if answer:
    os.remove(origin_blade_file)
    print(f"File Deleted. {origin}.blade.php")
    # Remove folder if needed
    if (len(blade_files) + len(removeable_files)) == 1:
      os.rmdir(f'../roomroster/resources/views/dashboards/event-owner/event/{folder}')
      print(f"Folder was empty. Folder Deleted {folder}")
else:
  print("The file does not exist")
