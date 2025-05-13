# TMDB Backdrops Downloader

A Python script to download high-quality backdrop images from The Movie Database (TMDB) for movies and TV shows.

## Features

- Search for movies and TV shows by name
- Downloads all available backdrop images in original quality
- Asynchronous downloads for better performance
- Automatically cleans up previously downloaded images
- Progress tracking during downloads

## Requirements

- Python 3.7+
- TMDB API key
- Required Python packages (see requirements.txt)

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with:
   ```
   TMDB_API_KEY=your_api_key_here
   WALLPAPERS_PATH=/path/to/save/wallpapers/
   ```
