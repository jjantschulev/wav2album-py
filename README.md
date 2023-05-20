# Audio Transcoding Script

This script is designed to transcode WAV audio files to AAC format using FFmpeg. It processes WAV files in a specified directory, extracts metadata from the file names, converts the WAV files to AAC format, and updates the metadata of the transcoded files using FFmpeg. The script also supports resizing and converting album art images to JPEG format.

## Prerequisites

To run this script, you need to have the following installed:

- Python (version 3 or higher)
- FFmpeg (command-line tool for audio/video processing)
- Pillow (Python library for image processing)
- hashlib (Python library for hashing)
- shutil (Python library for file operations)
- subprocess (Python library for running shell commands)

Make sure that FFmpeg is added to your system's PATH environment variable so that it can be executed from the command line.

## Usage

1. Place the script file in the directory where your WAV files are located.
2. Open a terminal or command prompt and navigate to the directory containing the script.
3. Run the script using the command `python script.py`.
4. The script will process the WAV files in the "in" directory of each album directory within the base directory.
5. The transcoded AAC files will be saved in the "out" directory of each album directory.
6. The script will also create a cache dictionary file "**cache**/cache.dict" to store information about transcoded files to improve performance on subsequent runs.

## Customization

You can customize the behavior of the script by modifying the following variables:

- `base_directory`: The base directory where your album directories are located. By default, it is set to the current directory.
- `cache_path`: The path to the cache directory. By default, it is set to "**cache**" within the base directory.
- `resize_image(image, length)`: This function is responsible for resizing album art images. You can modify the resizing strategy according to your requirements.

## Important Notes

- The script expects the following directory structure for each album:
  ```
  - Album Directory
    |-- in (input directory containing WAV files)
    |-- out (output directory for transcoded AAC files)
    |-- art.png (optional album art image in PNG format)
  ```
- The script only processes files with the ".WAV" extension in the "in" directory of each album.
- The script expects the WAV file names to be in the format: "{track_number} {song_name} - {composer}.WAV". For example, "01 My Song - Composer.WAV".
- The script requires FFmpeg to be installed and available in the system's PATH environment variable.
- The script uses FFmpeg to transcode WAV files to AAC format. You can modify the FFmpeg command arguments (`cmd` list) to customize the transcoding settings.
- The script uses Pillow to resize album art images to a maximum size of 512x512 pixels in JPEG format. You can modify the resizing strategy in the `resize_image` function.
- The script uses a cache dictionary to store the hash values of transcoded files and avoids reprocessing them on subsequent runs. The cache dictionary is saved to the "**cache**/cache.dict" file.

Please ensure that you have a backup of your original WAV files before running this script as it modifies and deletes files in the process.

**Disclaimer:** This script is provided as-is without any warranty. Use it at your own risk.

Feel free to customize and enhance the script according to your specific needs.
