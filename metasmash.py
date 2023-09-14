import sys
import os
import magic
import exiftool
import PIL.ExifTags
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

def extract_metadata(file_path, extract_gps=False):
    """
    Extracts metadata and exif data from a media file.
    """
    with exiftool.ExifToolHelper() as et:
        if extract_gps:
            metadata = et.get_metadata(file_path, SENSITIVE_TAGS)
        else:
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

def main():
    """
    Prompts the user for a file location and extracts sensitive metadata and exif data.
    """
    
    parser = argparse.ArgumentParser(description="MetaSmash to get all the metas.")
    parser.add_argument('-g', '--extract-gps', help='Extract GPS data', action='store_true')
    parser.add_argument('file_path', help='Path to the file from which to extract MetaData')  
    args = parser.parse_args()

    mime = magic.Magic(mime=True)
    file_type = mime.from_file(args.file_path)

    if "image" in file_type or "pdf" in file_type or "video" in file_type or "audio" in file_type or "ms-office" in file_type or "officedocument" in file_type or "msword" in file_type:
        metadata = extract_metadata(args.file_path, args.extract_gps)
        formatted_metadata = format_metadata(metadata)
        print(formatted_metadata)
    else:
        print(f"Error: {file_type} is not a supported file type.")

if __name__ == "__main__":
    main()
