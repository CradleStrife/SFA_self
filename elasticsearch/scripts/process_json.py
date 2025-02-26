import json
import sys

def recursive_date_check(data):
    if isinstance(data, list):
        return [recursive_date_check(item) for item in data]
    elif isinstance(data, dict):
        return {key: recursive_date_check(value) for key, value in data.items()}
    elif data == 'NaT':
        return '1900-01-01'
    return data

if __name__ == "__main__":
    input_file = sys.argv[1]
    
    # Read the JSON data from the file
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Process the JSON data
    processed_data = recursive_date_check(data)
    
    # Write the processed data back to the file
    with open(input_file, 'w', encoding='utf-8') as file:
        json.dump(processed_data, file, indent=2)

    print(f"Processed file: {input_file}")
