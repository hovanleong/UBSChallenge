import re

def find_flag_in_file(file_path):
    # Regular expression to find the UB5 flag format
    flag_pattern = r'UB5\{.*?\}'
    
    # Read the content of the file
    with open(file_path, 'r') as file:
        content = file.read()
        
    # Search for the flag using regex
    match = re.search(flag_pattern, content)
    
    if match:
        flag = match.group(0)  # Get the matched flag
        return flag
    else:
        return "No flag found."

# Example usage
file_path = 'output'
flag = find_flag_in_file(file_path)
print(f"Found flag: {flag}")
