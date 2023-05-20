#!/usr/bin/env python3

import hashlib
import os
import shutil
import subprocess

from PIL import Image


def calculate_file_hash(file_path, hash_algorithm='sha256'):
    # return none if file does not exist
    if not os.path.isfile(file_path):
        return None

    # Initialize the hash object
    hash_object = hashlib.new(hash_algorithm)

    # Open the file in binary mode
    with open(file_path, 'rb') as file:
        # Read the file in chunks to handle large files
        for chunk in iter(lambda: file.read(4096), b''):
            # Update the hash object with the chunk of data
            hash_object.update(chunk)

    # Get the final hash value
    file_hash = hash_object.hexdigest()

    return file_hash

def calculate_dictionary_hash(dictionary, hash_algorithm='sha256'):
    # Initialize the hash object
    hash_object = hashlib.new(hash_algorithm)

    # Read the dictionary in chunks to handle large files
    for key, value in dictionary.items():
        # Update the hash object with the chunk of data
        hash_object.update(key.encode('utf-8'))
        hash_object.update(str(value).encode('utf-8'))

    # Get the final hash value
    dictionary_hash = hash_object.hexdigest()

    return dictionary_hash

def save_dict_to_file(dictionary, file_path):
    with open(file_path, 'w') as file:
        for key, value in dictionary.items():
            file.write(f"{key}={value}\n")

def load_dict_from_file(file_path):
    dictionary = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.split("=", 1)
            dictionary[key] = value.rstrip("\n")
    return dictionary

def resize_image(image: Image, length: int) -> Image:
    """
    Resize an image to a square. Can make an image bigger to make it fit or smaller if it doesn't fit. It also crops
    part of the image.

    :param self:
    :param image: Image to resize.
    :param length: Width and height of the output image.
    :return: Return the resized image.
    """

    """
    Resizing strategy : 
     1) We resize the smallest side to the desired dimension (e.g. 1080)
     2) We crop the other side so as to make it fit with the same length as the smallest side (e.g. 1080)
    """
    if image.size[0] < image.size[1]:
        # The image is in portrait mode. Height is bigger than width.

        # This makes the width fit the LENGTH in pixels while conserving the ration.
        resized_image = image.resize((length, int(image.size[1] * (length / image.size[0]))))

        # Amount of pixel to lose in total on the height of the image.
        required_loss = (resized_image.size[1] - length)

        # Crop the height of the image so as to keep the center part.
        resized_image = resized_image.crop(
            box=(0, required_loss / 2, length, resized_image.size[1] - required_loss / 2))

        # We now have a length*length pixels image.
        return resized_image
    else:
        # This image is in landscape mode or already squared. The width is bigger than the heihgt.

        # This makes the height fit the LENGTH in pixels while conserving the ration.
        resized_image = image.resize((int(image.size[0] * (length / image.size[1])), length))

        # Amount of pixel to lose in total on the width of the image.
        required_loss = resized_image.size[0] - length

        # Crop the width of the image so as to keep 1080 pixels of the center part.
        resized_image = resized_image.crop(
            box=(required_loss / 2, 0, resized_image.size[0] - required_loss / 2, length))

        # We now have a length*length pixels image.
        return resized_image

# Source and destination directories
base_directory = "./"
cache_path = os.path.join(base_directory, "__cache__")

# Create the cache directory if it doesn't exist
if not os.path.isdir(cache_path):
    os.makedirs(cache_path)

# load the cache dictionary
cache_dict = {}
cache_dict_path = os.path.join(cache_path, "cache.dict")
if os.path.isfile(cache_dict_path):
    cache_dict = load_dict_from_file(cache_dict_path)

# Process each album directory
for album_dir in os.listdir(base_directory):
    album_path = os.path.join(base_directory, album_dir)
    if not os.path.isdir(album_path):
        continue

    # Ignore the cache directory
    if album_dir in ("__cache__", "__pycache__", ".git"):
        continue

    # Get album name
    album_name = album_dir
    album_year = album_name[:4]
    if album_year.isdigit():
        album_year = int(album_year)
        if album_year < 1900 or album_year > 2200:
            album_year = None
    else:
        album_year = None

    # Skip if not a valid year
    if album_year is None:
        print(f"Skipping album: {album_name} (invalid year)")
        continue

    input_dir = os.path.join(album_path, "in")
    output_dir = os.path.join(album_path, "out")

    # Clear the output directory
    os.makedirs(output_dir, exist_ok=True)

    dont_delete_set = set()

    # Process WAV files in the input directory
    for wav_file in os.listdir(input_dir):
        if not wav_file.endswith(".WAV"):
            print(f"Skipping file: {wav_file} (not a WAV file)")
            continue

        wav_path = os.path.join(input_dir, wav_file)

        # Parse track information from the file name
        try:
            order, rest = wav_file.split(" ", 1)
            song_name, composer = rest.split(" - ", 1)
            order = int(order)
            composer = composer[:-4]  # Remove the ".WAV" extension
        except ValueError:
            print(f"Skipping file: {wav_file} (incorrect file name format)")
            continue

        # Transcode WAV to AAC
        output_filename = f"{order:02d} {song_name} - {composer}.m4a"
        output_file_path = os.path.join(output_dir, output_filename)

        dont_delete_set.add(output_filename)

        # Check if the file has already been transcoded and is in the cache
        art_file_path = os.path.join(album_path, "art.png")
        art_file_hash = calculate_file_hash(art_file_path)
        cache_key = calculate_file_hash(wav_path)
        metadata = {
            "title": song_name,
            "artist": "Jordan Jantschulev",
            "album": album_name,
            "composer": composer,
            "year": album_year,
            "track": order,
            "arthash": art_file_hash,
            "wavhash": cache_key,
        }
        metadata_hash = calculate_dictionary_hash(metadata)
        if metadata_hash in cache_dict:
            existing_file_hash = calculate_file_hash(output_file_path)
            if existing_file_hash == cache_dict[metadata_hash]:
                print(f"Found in cache: {output_filename}")
                continue

        # Delete the file if it exists
        if os.path.isfile(output_file_path):
            os.remove(output_file_path)

        cache_file_path = os.path.join(cache_path, cache_key + ".m4a")
        if not os.path.isfile(cache_file_path):
            # Transcode the file
            print(f"Transcoding: {output_filename}")
            subprocess.run(["ffmpeg", "-i", wav_path, "-c:a", "aac", "-b:a", "320k", cache_file_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


        # Update metadata using FFmpeg
        added_image = []
        art_file_path_bmp = None
        if os.path.isfile(art_file_path):
            # Convert PNG to JPEG
            img = Image.open(art_file_path).convert("RGB")
            img = resize_image(img, 512)
            art_file_path_bmp = art_file_path.replace(".png", ".jpg")
            img.save(art_file_path_bmp, "BMP")
            added_image = ["-i", art_file_path_bmp, "-map", "0", "-map", "1", "-c:v", "copy", "-disposition:v", "attached_pic"]
           
        cmd = [
            "ffmpeg", "-i", cache_file_path, *added_image,
            "-metadata", f"title={song_name}", 
            "-metadata", f"artist=Jordan Jantschulev",
            "-metadata", f"album={album_name}", 
            "-metadata", f"composer={composer}",
            "-metadata", f"year={album_year}",
            "-metadata", f"track={order}", 
            "-c:a", "copy", "-map_metadata", "0", output_file_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # remove the jpg if created: 
        if art_file_path_bmp and os.path.isfile(art_file_path_bmp):
            os.remove(art_file_path_bmp)

        # Add the transcoded file to the cache
        cache_dict[metadata_hash] = calculate_file_hash(output_file_path)

        print(f"Processed {output_filename}")

    # Delete all the files in output that are not in the dont_delete_set
    for f in os.listdir(output_dir):
        if f not in dont_delete_set:
            os.remove(os.path.join(output_dir, f))


# save the cache dictionary
save_dict_to_file(cache_dict, cache_dict_path)