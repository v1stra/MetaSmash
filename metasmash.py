import os
import re
import magic
import exiftool
import requests
import tempfile
import PIL.Image
import argparse

SENSITIVE_TAGS = [
    "EXIF:GPSLatitude",
    "EXIF:GPSLongitude",
    "EXIF:GPSAltitude",
    "EXIF:GPSImgDirection",
    "EXIF:GPSDestLatitude",
    "EXIF:GPSDestLongitude",
    "EXIF:GPSDestBearing",
    "EXIF:GPSDateStamp",
    "EXIF:GPSDifferential",
    "EXIF:GPSHPositioningError",
    "EXIF:UserComment"
]

FILE_TYPES = [
    "application/vnd.ms-excel",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/pdf"
]

def check_http_url(s):
    """ Checks if provided string is a URL """
    pattern = r'^https?://'
    return bool(re.match(pattern, s))


def download_file(url, destination_dir):
    """ Downloads a file, storing it in the destination directory """
    # Exctract the file name from the url
    filename = os.path.basename(url)

    # Ensure the directory exists; if not, create it
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    filepath = os.path.join(destination_dir, filename)

    try:
        response = requests.get(url)
    except:
        return ""

    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            
    print(f'File URL: {url}')
    return filepath
    
    
def extract_metadata(file_path):
    """
    Extracts metadata and exif data from a media file.
    """
    with exiftool.ExifToolHelper() as et:
        metadata = et.get_metadata(file_path)
    return metadata


def format_metadata(metadata_list):
    """
    Formats metadata output to be more human-readable.
    """
    formatted_metadata = ""
    for metadata in metadata_list:
        for key, value in metadata.items():
            # if key in SENSITIVE_TAGS:
            formatted_key = key.replace(":", " ").title()
            formatted_value = str(value).replace("\\n", "\n")
            formatted_metadata += f"{formatted_key}: {formatted_value}\n"
        if not formatted_metadata:
            formatted_metadata = "No sensitive metadata found."
    return formatted_metadata


def go(f, directory):
    
    print('------------------------------------------------------------------------')
    mime = magic.Magic(mime=True)
        
    if check_http_url(f):
        _file = download_file(f, directory)
    else:
        _file = f
    
    if _file and os.path.exists(_file):
        file_type = mime.from_file(_file)

        if file_type in FILE_TYPES:
            metadata = extract_metadata(_file)
            formatted_metadata = format_metadata(metadata)
            print(formatted_metadata)
        else:
            print(f"Error: {file_type} is not a supported file type.")
        

def main():
    """
    Prompts the user for a file location and extracts sensitive metadata and exif data.
    """
    
    parser = argparse.ArgumentParser(description="MetaSmash to get all the metas.")
    parser.add_argument('-f', '--file', help='Path to the file from which to extract MetaData') 
    parser.add_argument('-l', '--list', help='List of URLs or files to parse.')
    parser.add_argument('-d', '--directory', help='Directory to output files', default='/tmp')

    args = parser.parse_args()

    file_list = []
    if args.list:
        with open(args.list, 'r') as f:
            file_list = f.readlines()
            for f in file_list:
                go(f.strip(), args.directory)
    
    if args.file:
        go(args.file, args.directory)

if __name__ == "__main__":
    main()
