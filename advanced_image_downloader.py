import os
import requests
from urllib.parse import urlparse, urljoin

def download_image(urls, output_dir="images"):
    """
    Downloads images from the given URLs, handling redirects, authentication, and query parameters.
    
    Args:
        urls (list): List of image URLs to download.
        output_dir (str): Directory to save the downloaded images.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    def get_filename(url, content_type=None):
        """Generate a filename from the URL or Content-Type."""
        parsed_url = urlparse(url)
        base_name = os.path.basename(parsed_url.path).split("?")[0]
        if not base_name:  # Fallback filename
            base_name = "downloaded_image"
        # Add extension based on content-type
        extension = content_type.split("/")[-1] if content_type else "jpg"
        if not base_name.endswith(f".{extension}"):
            base_name += f".{extension}"
        return base_name
    
    def download_single_image(url):
        """Download a single image and save it."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        try:
            # Make the request
            response = requests.get(url, headers=headers, stream=True, timeout=10)
            response.raise_for_status()  # Raise HTTP errors

            # Verify content type is an image
            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                print(f"URL does not point to an image: {url}")
                return

            # Determine filename and save path
            filename = get_filename(url, content_type)
            save_path = os.path.join(output_dir, filename)

            # Write the image data to file
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded: {save_path}")
        except requests.RequestException as e:
            print(f"Failed to download {url}: {e}")
    
    # Process each URL
    for url in urls:
        download_single_image(url)

if __name__ == "__main__":
    image_urls = [
        "https://assets.central.co.th/journal-womenmididresslongsleeves-CDS11915003-5?$JPEG$&wid=550",
        "https://assets.central.co.th/journal-womenlongdresssleevelessprinted-CDS11914839-5?$JPEG$&wid=550",
        "https://assets.central.co.th/journal-womenlongdresssleeveless-CDS11914655-5?$JPEG$&wid=550",
    ]

    download_image(image_urls, output_dir="downloaded_images")
