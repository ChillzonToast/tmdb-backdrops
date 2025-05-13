import os
import glob
from dotenv import load_dotenv
import aiohttp
import asyncio
from typing import Dict
import sys

load_dotenv()
api_key = os.getenv('TMDB_API_KEY')

wallpapers_path = os.getenv("WALLPAPERS_PATH")

# Global counter for downloaded images
downloaded_count = 0
async_step = 25

async def fetch_json(session: aiohttp.ClientSession, url: str) -> Dict:
    async with session.get(url) as response:
        return await response.json()

async def download_image(session: aiohttp.ClientSession, image_url: str, save_path: str, total_images: int):
    global downloaded_count
    async with session.get(image_url) as response:
        if response.status == 200:
            data = await response.read()
            with open(save_path, "wb") as f:
                f.write(data)
            downloaded_count += 1
            print(f"Progress: [{downloaded_count}/{total_images}] Downloaded: {os.path.basename(save_path)}\r", end="")

async def get_images(tmdb_name: str):
    global downloaded_count
    downloaded_count = 0
    print(f"\nSearching for '{tmdb_name}'...")
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                search_url = f"https://api.themoviedb.org/3/search/multi?query={tmdb_name}&api_key={api_key}"
                response = await fetch_json(session, search_url)
                results = response["results"]
                results = [movie for movie in results if "vote_count" in movie]
                results = sorted(results, key=lambda i: int(i['vote_count'])*float(i['popularity']), reverse=True)
                tmdb_id = results[0]["id"]
                tmdb_type = results[0]["media_type"]
                title = results[0].get("title", results[0].get("name"))
                print(f"Found: {title} (ID: {tmdb_id}, Type: {tmdb_type})")
                break
            except Exception as e:
                print(f"Error during search: {e}")
                continue

        while True:
            try:
                print("Fetching available images...")
                if tmdb_type == "movie":
                    images_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/images?include_image_language=null&api_key={api_key}"
                else:
                    images_url = f"https://api.themoviedb.org/3/tv/{tmdb_id}/images?include_image_language=null&api_key={api_key}"
                
                data = await fetch_json(session, images_url)
                break
            except Exception as e:
                print(f"Error fetching images: {e}")
                continue

        images = data["backdrops"]
        total_images = len(images)
        print(f"\nFound {total_images} backdrop images. Starting download...")
        
        tasks = []
        for i, image in enumerate(images):
            image_url = f"https://image.tmdb.org/t/p/original{image['file_path']}"
            save_path = f"{wallpapers_path}tscript_{tmdb_id}_{i+1}.jpg"
            task = asyncio.create_task(download_image(session, image_url, save_path, total_images))
            tasks.append(task)
        
        for i in range(0, len(tasks), async_step):
            batch = tasks[i:i+async_step]
            await asyncio.gather(*batch)
        print(f"\nDownload complete! {total_images} images saved to {wallpapers_path}")

def delete_images():
    files = glob.glob(os.path.join(wallpapers_path, "tscript_*.jpg"))
    for file in files:
        try:
            os.remove(file)
        except Exception as e:
            print(f"Error deleting {file}: {e}")
    
    print(f"Deleted {len(files)} images")


async def main():
    if len(sys.argv) < 2:
        print("Please provide a title as a command line argument")
        sys.exit(1)
        
    title = " ".join(sys.argv[1:])
    delete_images()
    await get_images(title)
    
if __name__ == "__main__":
    asyncio.run(main())