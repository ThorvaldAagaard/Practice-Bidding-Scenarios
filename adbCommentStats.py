# Reads all .pbn files from directory /pbn and makes the statistic lines comments

import os

def process_file(files):
    nFiles = 0
    for filename in files:
        nFiles = nFiles + 1


        print('\n ' + str(nFiles) + ' ------ ' + filename + ' ------ ')
        if filename.lower().endswith('.pbn'):
                      
            with open('./pbn/' + filename, 'r') as i_file:
                # Split the string into individual lines
                content = i_file.read()
                lines = content.strip().split('\n')

                # Prepend '# ' to each line that is not a blank line or a pbn keyword/value [...]
                processed_lines = []
                for line in lines:
                    if not (line.startswith('[') or line.strip() == ''):
                        if not line.startswith('#'):
                            line = '# ' + line
                        print(line)
                    processed_lines.append(line)

            with open('./pbn/' + filename, 'w') as o_file:
                # Join the processed lines back into a single string

                result = '\n'.join(processed_lines)
                o_file.write(result)


def scan_for_pbn(directory_path):
    # Use os.listdir() to get files in the current directory only
    current_directory_files = os.listdir(directory_path)
    process_file(current_directory_files)

    print(f"# Scan is complete!")

def main():

    scan_for_pbn("./pbn")

if __name__ == "__main__":
    main()