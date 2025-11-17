import os
import requests
from instagrapi import Client

def load_drive_links():
    links = []
    with open("drive_links.txt", "r") as f:
        for line in f:
            link = line.strip()
            if link:
                links.append(link)
    return links


def download_from_drive(url, filename):
    r = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def upload_to_instagram(video_path, caption):
    cl = Client()
    cl.load_settings("session.json")
    cl.login_by_sessionid("78321171209%3AoKDzPkMGGW2OTB%3A5%3AAYi_nmLcYhDDom6eVZ444AHX-yDjMBBmv3LzHjOkig")

    cl.clip_upload(video_path, caption)
    print("Uploaded:", video_path)


def main():
    links = load_drive_links()

    for index, link in enumerate(links):
        video_file = f"video_{index}.mp4"

        print("Downloading:", link)
        download_from_drive(link, video_file)

        print("Uploading:", video_file)
        upload_to_instagram(video_file, f"Reel {index + 1} 🎥")

        os.remove(video_file)
        print("Deleted:", video_file)


if __name__ == "__main__":
    main()
