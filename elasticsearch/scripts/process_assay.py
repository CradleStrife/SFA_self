import json
import sys
import os, re
import requests
from datetime import datetime

# Define the fields that should be kept in the JSON files (top-level only)
allowed_fields = {
    "pmid", "pmcid", "title", "abstract", "authors", "journal", "year", "url", "doi",
    "key_words", "filename", "isolate_id", "isolate_source", "isolate_date",
    "isolate_country", "serotype", "mlst", "ast_data", "spi", "amr", "plasmid",
    "snp", "virulence genes", "accession numbers", "final_cleaned_text", "accession numbers_merge", "latitude", "longitude"
}

def normalize_ast_data(ast_data, pmcid):
    """
    Normalize the ast_data to ensure it follows the proper structure, lowercase the serotype field, but keep the values intact.
    """
    if not isinstance(ast_data, list):
        ast_data = []

    normalized_data = []

    for entry in ast_data:
        if isinstance(entry, dict):
            serotype = entry.get('serotype', 'NA')  # Keep serotype's original value
            antibiotics = entry.get('antibiotics', [])
            if not isinstance(antibiotics, list):
                antibiotics = []

            normalized_antibiotics = []
            for antibiotic in antibiotics:
                if isinstance(antibiotic, dict):
                    normalized_antibiotics.append({
                        "name": antibiotic.get("name", "NA"),  # Keep value's original case
                        "mic": antibiotic.get("mic", "NA"),    # Keep value's original case
                        "interpretation": antibiotic.get("interpretation", "NA")  # Keep value's original case
                    })
                else:
                    normalized_antibiotics.append({
                        "name": "NA",
                        "mic": "NA",
                        "interpretation": "NA"
                    })

            normalized_data.append({
                "serotype": serotype,  # Keep serotype's original value
                "antibiotics": normalized_antibiotics
            })
        else:
            normalized_data.append({
                "serotype": "NA",
                "antibiotics": [{
                    "name": "NA",
                    "mic": "NA",
                    "interpretation": "NA"
                }]
            })

    return normalized_data

def transform_keys(obj, filter_allowed=False):
    """
    Transform all keys in the object to lowercase.
    Optionally apply the allowed fields filter only at the top level if 'filter_allowed' is True.
    """
    if isinstance(obj, dict):
        if filter_allowed:
            # Apply the allowed_fields filter only at the top level
            return {k.lower(): transform_keys(v, False) for k, v in obj.items() if k.lower() in allowed_fields}
        else:
            # Transform keys at deeper levels without filtering
            return {k.lower(): transform_keys(v, False) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [transform_keys(item, False) for item in obj]
    else:
        return obj

def convert_lat_lon_to_location(data):
    """
    Converts latitude and longitude fields into a location field with 'lat' and 'lon',
    and retrieves the country name using reverse geocoding.
    """
    # lat = data.pop('latitude', None)
    # lon = data.pop('longitude', None)

    # if lat and lon:
    #     try:
    #         lat = float(lat)
    #         lon = float(lon)
    #         data['location'] = {"lat": lat, "lon": lon}
            
    #         # Call the reverse geocoding API to get the country name
    #         country_name = get_country_name_from_lat_lon(lat, lon)
    #         if country_name:
    #             data['countryname'] = country_name  # Add the country name to the document
            
    #     except ValueError:
    #         print(f"Invalid latitude or longitude format in {data.get('pmcid', 'unknown_pmcid')}")
    # else:
    #     print(f"Missing latitude or longitude in {data.get('pmcid', 'unknown_pmcid')}")
    if 'countryname' in data:
        return  # Skip if the countryname already exists in the data

    # Check if location or lat/lon is available
    location = data.get('location', None)

    if location and 'lat' in location and 'lon' in location:
        lat = location['lat']
        lon = location['lon']
        
        # Perform reverse geocoding using the API
        try:
            country_name = get_country_name(lat, lon)
            if country_name:
                data['countryname'] = country_name  # Add the country name to the data
            else:
                print(f"Could not retrieve country name for lat: {lat}, lon: {lon}")
                data['countryname'] = "NA"  # Set to "NA" if no country name is found
        except ValueError:
            print(f"Invalid latitude or longitude format in {data.get('pmcid', 'unknown_pmcid')}")
            data['countryname'] = "NA"
    else:
        # If no lat/lon or location is available, set countryname to "NA"
        print(f"Missing location data in {data.get('pmcid', 'unknown_pmcid')}")
        data['countryname'] = "NA"

def get_country_name(lat, lon):
    """
    Uses BigDataCloud reverse geocoding API to get the country name from latitude and longitude.
    """
    url = "https://api.bigdatacloud.net/data/reverse-geocode-client"
    try:
        response = requests.get(url, params={
            'latitude': lat,
            'longitude': lon,
            'localityLanguage': 'en'
        })
        if response.status_code == 200:
            data = response.json()
            return data.get('countryName', 'Unknown')  # Return 'Unknown' if no country name found
        else:
            print(f"Failed to get country name for {lat},{lon}: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error during reverse geocoding: {e}")
    
    return 'Unknown'


def normalize_isolate_date(isolate_date):
    """
    Normalize the isolate_date field to extract only the years and handle ranges.
    """
    # 1. **Check if isolate_date is already in the correct format (a list of valid years)**
    if isinstance(isolate_date, list):
        # Check if every item in the list is a valid year (4 digits)
        if all(isinstance(year, str) and re.match(r'^\d{4}$', year) for year in isolate_date):
            # If the list is already a valid list of years, return it without modification
            return isolate_date
        # If the list contains non-standard dates, process the first entry
        elif len(isolate_date) > 0:
            isolate_date = isolate_date[0]  # Use the first date in the list (or customize as needed)
        else:
            return ["1900"]  # If the list is empty, return a default year

    # 2. **Check if isolate_date is a string**
    if not isinstance(isolate_date, str):
        print(f"Invalid isolate_date format: {isolate_date}. Expected a string.")
        return ["1900"]

    if not isolate_date or isolate_date.strip() in ["NA", "", "0000"]:
        return ["1900"]  # Default year for "NA" or empty fields

    isolate_date = isolate_date.strip()  # Remove leading/trailing whitespace

    # 3. **Processing the string to extract years**
    # Case: Handle ranges like "1969 to 2012" or "March 1969 to March 2012"
    if "to" in isolate_date or "-" in isolate_date:
        years = extract_years(isolate_date)
        if len(years) == 2:
            start_year, end_year = years
            return [str(year) for year in range(int(start_year), int(end_year) + 1)]  # Return list of years
        elif len(years) == 1:
            return [years[0]]  # If only one year found, return it
        else:
            return ["1900"]

    # Case: "2 months before March 11, 2015" -> Extract just 2015
    if "before" in isolate_date:
        years = extract_years(isolate_date)
        return [years[0]] if years else ["1900"]

    # Case: "between 1st April 2014 and 31st March 2015" -> Extract range [2014, 2015]
    if "between" in isolate_date and "and" in isolate_date:
        years = extract_years(isolate_date)
        if len(years) == 2:
            start_year, end_year = years
            return [str(year) for year in range(int(start_year), int(end_year) + 1)]  # List of years from start to end
        elif len(years) == 1:
            return [years[0]]
        else:
            return ["1900"]

    # Case: "2016-05-03" or "05/08/2015" or "11.11.2015" -> Extract just the year
    if re.match(r'\d{1,2}[-/.]\d{1,2}[-/.]\d{4}', isolate_date):
        return [isolate_date[-4:]]  # Extract the last 4 digits (the year)

    # Case: "19/5" -> Set to 1900 if it's missing the year
    if re.match(r'\d{1,2}[/]\d{1,2}', isolate_date):
        return ["1900"]  # Missing year, default to 1900

    # Case: "2012/2013 and 2013/2014" -> Extract 2012, 2013, 2014
    if "/" in isolate_date or "and" in isolate_date:
        years = extract_years(isolate_date)
        if len(years) > 0:
            return sorted(set(years))  # Return sorted distinct years
        else:
            return ["1900"]

    # Case: Single years like "March 2017" -> Extract just 2017
    years = extract_years(isolate_date)
    if len(years) > 0:
        return [years[0]]

    # If no format matches, print a message and return default "1900"
    print(f"Unknown isolate_date format: {isolate_date}")
    return ["1900"]


def extract_years(date_str):
    """
    Extract all the valid 4-digit years from a date string.
    """
    return re.findall(r'\b\d{4}\b', date_str)  # Find all 4-digit numbers in the string



def process_json(file_path):
    """
    Process the JSON file: normalize keys, check unrecognized fields, normalize ast_data, convert lat/lon, and apply other transformations.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    
    data = transform_keys(data)
    
   
    convert_lat_lon_to_location(data)


    pmcid = data.get('pmcid', 'unknown_pmcid')

    # Normalize the ast_data field if it exists
    if 'ast_data' in data:
        data['ast_data'] = normalize_ast_data(data['ast_data'], pmcid)
    else:
        data['ast_data'] = [{
            "serotype": "NA",
            "antibiotics": [{
                "name": "NA",
                "mic": "NA",
                "interpretation": "NA"
            }]
        }]

    # Step 3: Date reformatting and unnecessary fields removal
    def reformat_dates(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, str):
                    try:
                        obj[k] = datetime.strptime(v, '%Y-%m-%d').strftime('%Y-%m-%d')
                    except ValueError:
                        pass
                elif isinstance(v, (dict, list)):
                    reformat_dates(v)
        elif isinstance(obj, list):
            for item in obj:
                reformat_dates(item)

    if 'isolate_date' in data:
        data['isolate_date'] = normalize_isolate_date(data['isolate_date'])

    # Save the transformed JSON back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 process_json.py <path_to_json_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    if not os.path.isfile(json_file):
        print(f"File not found: {json_file}")
        sys.exit(1)
    
    process_json(json_file)
    print(f"Processed {json_file}")
