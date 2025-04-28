import sys
import os
import re
import requests
import hashlib
import argparse

parser = argparse.ArgumentParser(description="Extract dealer code")
parser.add_argument("--generate", type=int, default=100000000, help="Number to generate")
parser.add_argument("--produce", type=int, default=500, help="Number to produce")
parser.add_argument("--nodealer", type=bool, default=False, help="Ignore dealer code")
args = parser.parse_args()
generate = args.generate
produce = args.produce
nodealer = args.nodealer
if generate:
    sys.stderr.write("generating " + str(generate)+ "\n")
if produce:
    sys.stderr.write("producing " + str(produce)+ "\n")

# Directory containing the files
directory_path = './../../PBS'

# Regular expression pattern to match text enclosed in backticks spanning multiple lines
pattern = r'`(.*?)`'

# Function to find and process text enclosed in backticks and save to a .dlr file

def calculate_seed(input):
    # Calculate the SHA-256 hash
    hash_object = hashlib.sha256(input.encode())
    hash_bytes = hash_object.digest()

    # Convert the first 4 bytes of the hash to an integer and take modulus
    hash_integer = int.from_bytes(hash_bytes[:4], byteorder='big') % (2**32 - 1)
    return hash_integer

def extract_text_in_backticks(file_path):
    sys.stderr.write(f"{file_path}\n")
    with open(file_path, 'r') as file:
        content = file.read()
        # Pattern to find text in double quotes following a comma and a space
        quotes_pattern = r',\s*"([^"]+)"'
        quotes_matches = re.findall(quotes_pattern, content)
        dealer = None
        if len(quotes_matches) > 0:
            if quotes_matches[0] == "N":
                dealer = "north"
            if quotes_matches[0] == "S":
                dealer = "south"
            if quotes_matches[0] == "E":
                dealer = "east"
            if quotes_matches[0] == "W":
                dealer = "west"
        matches = re.findall(pattern, content, re.DOTALL)
        for i, match in enumerate(matches, 1):
            # Process the extracted text
            processed_text = process_extracted_text(match, dealer)
            output_file_path = os.path.splitext(os.path.basename(file_path))[0].replace(" ", "-").replace("(", "").replace(")", "").replace("&", "and").replace("+", "_") + ".dlr"
            output_file_path = os.path.join("./dlr", output_file_path).replace('\\', '/')
            with open(output_file_path, 'w') as output_file:
                # Save the processed text to the .dlr file
                seed = calculate_seed(file_path)
                # We seed based on filename, then we have reproduceale results, but different seed pr, file
                output_file.write(processed_text)
                print(f'echo dealerv2 {output_file_path}  -s {seed} ')
                print(f'./../../../Dealer-Version-2-/Prod/dealerv2  {output_file_path} -s  {seed} > ./pbn/{ os.path.splitext(os.path.basename(file_path))[0].replace(" ","-").replace("(", "").replace(")", "").replace("&", "and").replace("+", "_")}.pbn ', end="\n")

# Function to process the extracted text


def process_extracted_text(extracted_text, dealer):
    processed_text = []
    
    action = False
    condition = False
    generate_added = False
    produce_added = False

    lines = extracted_text.split('\n')
    # Remove all comments
    lines = [line for line in lines if not line.strip().startswith('#')]
    # Remove all blank lines
    lines = [line for line in lines if line.strip() != ''] 

    for line in lines[:]:  # Iterate through a copy of the original list
        ## Check if there is a generate that should be overwritten
        if "generate" in line:
            if generate is not None:
                processed_text.append(f"generate {generate}\n")
            else:
                processed_text.append(line)
            lines.remove(line)      
            generate_added = True   
    if not generate_added:        
        if generate is not None:
            processed_text.append(f"generate {generate}\n")
        else:
            processed_text.append(f"generate 20000000\n")

    for line in lines[:]:  # Iterate through a copy of the original list
        ## Check if there is a generate that should be overwritten
        if "produce" in line:
            if produce is not None:
                processed_text.append(f"produce {produce}\n")
            else:
                processed_text.append(line)
            lines.remove(line)    
            produce_added = True   
    if not produce_added:        
        if produce is not None:
            processed_text.append(f"produce {produce}\n")
        else:
            processed_text.append(f"produce 100\n")

    if dealer != None and not nodealer :
        processed_text.append(f"dealer {dealer}\n")


    removerest = False
    for line in lines[:]:  # Iterate through a copy of the original list
        if removerest:
            lines.remove(line)             
        if line.startswith("predeal "):
            processed_text.append(line)
            lines.remove(line)             
        if line.startswith("dealer "):
            if not nodealer and dealer is None:
                processed_text.append(line)
            lines.remove(line)             
        if line.startswith("vulnerable "):
            processed_text.append(line)
            lines.remove(line)             
        if line.startswith("opener "):
            processed_text.append(line)
            lines.remove(line)             
        if line.startswith("action ") or line == "action":
            lines.remove(line)             
            removerest = True
            

    for line in lines[:]:  # Iterate through a copy of the original list
        if "action" in line:
            action = True
        if "condition" in line:
            condition = True
        # We want to have all assignments before the condition statement         
        if ' = ' in line:
            processed_text.append(line)
            lines.remove(line)      

        if line.startswith("Import"):
            # Splitting the string by comma to get the URL
            split_string = line.replace("github.com","raw.githubusercontent.com").replace("blob/", "").split(',').trim()
            url = split_string[1]  # Assuming the URL is at index 1 after splitting
            # Fetching the content from the URL
            response = requests.get(url)            
            # Checking if the request was successful (status code 200)           
            if response.status_code == 200:
                content = response.text  # Content of the URL
                processed_text.append(content)
            else:
                sys.stderr.write(f"Error : {line} \n")
                sys.stderr.write(f"Error fetching URL: {url} code={response.status_code}\n")
                
            lines.remove(line) 

    if not condition:
        processed_text.append("\ncondition\n")

    for line in lines:
        processed_text.append(line)
    processed_text.append("\n")
    
    # For ben we ignore all previous actions
    #if not action:
    processed_text.append("action printpbn\n")
    #else:
    #    processed_text.append("printpbn\n")
    return '\n'.join(processed_text)


# List all files in the directory
n_files = 0
for filename in os.listdir(directory_path):
    #if filename == "Forcing_NT":
    file_path = os.path.join(directory_path, filename)
    extract_text_in_backticks(file_path)
    n_files = n_files + 1
sys.stderr.write(f"number of .dlr files = {str(n_files)}\n")