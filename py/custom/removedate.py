import sys
import os
import re

# Define the directory containing your files
directory = "./pbn"

# Define the pattern to search for
pattern_date = r'\[Date\s*"\d{4}\.\d{2}\.\d{2}"\]'
pattern_end = r'Generated\s+\d+\s+hands\s*[\r\n]+Produced\s+\d+\s+hands\s*[\r\n]+Initial random seed\s+\d+\s*[\r\n]+Time needed\s+\d+\.\d+\s+sec\s*[\r\n]+'

# Define the replacement strings
replacement_date = '[Date ""]'
replacement_end = ''

n_files = 0
# Loop through each file in the directory
for filename in os.listdir(directory):
    filepath = os.path.join(directory, filename)
    # Skip directories
    if os.path.isdir(filepath):
        continue
    # Open the file for reading
    with open(filepath, 'r') as file:
        filedata = file.read()
    # Perform the replacements
    filedata = re.sub(pattern_date, replacement_date, filedata)
    filedata = re.sub(pattern_end, replacement_end, filedata)
    # Write the modified content back to the file
    with open(filepath, 'w') as file:
        file.write(filedata)
        n_files = n_files + 1


sys.stderr.write(f"Date removed from {n_files} files\n")