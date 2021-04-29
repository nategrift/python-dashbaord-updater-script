from pathlib import Path
import re

# Files that are allowed to be removed
removeable_files = []

def fileContains(word, path):
  with open(path, 'r') as reader:
    lines = reader.readlines()
    repeats = 0
    for line in lines:
      if word in line:
          repeats += 1
    return repeats

for path in Path('../roomroster/resources/views/dashboards/event-owner').rglob('*.blade.php'):

  with open(path, 'r') as reader:
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


for file in removeable_files:
  new_file = re.sub(r"\.", "/", file)
  print(f"resources/views/{new_file}")