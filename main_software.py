import streamlit as st
from PIL import Image
import io
import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash-002")

# Predefined password
APP_PASSWORD = os.getenv("APP_PASSWORD")  # Load password from environment variables

# Function to download and convert image from URL to a PIL image
def download_image_from_url(image_url):
    """Downloads image from a URL and converts it to a PIL image."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.bivouac.co.nz/"
    }
    try:
        response = requests.get(image_url, headers=headers)
        response.raise_for_status()  # Raise an error for invalid URLs
        img = Image.open(io.BytesIO(response.content))
        return img
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")
    return None

# Function to generate image descriptions using LLM
def generate_image_descriptions(image, prompt):
    """Send image and prompt to LLM to get descriptions."""
    try:
        response = model.generate_content([prompt, image])
        generated_text = response.candidates[0].content.parts[0].text
        return generated_text
    except Exception as e:
        return "Usage limit reached or an error occurred."

# Function to get prompt based on image type
def get_prompt(image_type):
    """Return the appropriate prompt based on the image type."""
    
    if image_type == "Product Image short desc":
        return """        
        
        Prompt for Short Description:
        You are an expert image annotatator. You have the task is to give a concise description of the product image.
        Ensure your description is in human tone note like a machine wrote it.
        Ensure you make the description basic making fit to train a machine model

        Ensure you adhere to the further instructions below:
              
        - Length: Aim for 8 to 15 words.
        - Focus: Highlight the essential attributes:
            - Object identity
            - Shape (if applicable)
            - Function
            - Material
            - Color
        - Tone: Keep it simple and avoid excessive detail.

        here is an Example for context understanding: 

        "Cordless vacuum, light blue base, silver-gold handle."
        """

    elif image_type == "Product Image long desc":
        return """   
        
        Prompt for Long Description:
        You are an expert image annotatator. You have the task is to give a detailed description of the product image.
        Ensure your description is in human tone, very basic english, not like a machine wrote it.
        Ensure you make the description basic making it fit to train a machine model

        Ensure you adhere to further instruction below:
        
        1. Details to Include:
            - Brand or manufacturer
            - Additional features
         - Do not describe the background color of the product image
         - Text: Include any text visible on the product or image itself.
         - Tone: Avoid promotional language; focus on objective observations.
         - Observable Details: Limit descriptions to those observable in the image, excluding product information not visible.
         - Positioning: Mention the position of the product in the image (e.g., left, right) and capture all relevant visual details.
           details.
         - Only describe the product when a lifestyle image is used as a product image.
         - Include much details in your description 


        2. Ensure you avoid the below in your description:
          - Avoid “The image shows” or "The image showcases”, "the image appears to be …” instead Start with "A …’
          - Do not include the words "depicted", or "minimalistic" in your description.
          - There is no need to include this  “There is no visible brand or manufacturer information on the product.  There is no text present on the product or image.”.
          - Avoid describing persons or objects not visible in the image. e.g "There is no shadow present in the image. The image is well lit"
          - do not include sentence like this "The overall design aesthetic is minimalist and modern, with a focus on clean lines and neutral tones. No people are present in the image."
          - do not inlude suggestion from your end or any functions in the image in your description e.g "The entire scene is uncluttered and suggests a well-maintained and stylish living space."
          - Avoid describing background color for the product image.
          - Avoid Short description for the product image, make your description long.

         3. For accuracy in your product image description, check the below images link, AI Description and the Human feedback as 	    correction 

        First Image: 

        image link: https://img5.su-cdn.com/cdn-cgi/image/width=1000,height=1000,format=webp/mall/file/2024/04/16/8c2f9f95bb1a73499047b909f285258f.jpg
        
        AI Description for Product image:

        - "The image shows a round coffee table with a white marble top and a dark wood base. The table is 
        partially open, revealing an empty compartment inside. It is supported by a gold, triangular-shaped base.
        Two crescent-shaped gray fabric ottomans are positioned on the right side of the table, while a matching 
        ottoman is placed to the left. The background is a solid white. There is no visible branding or 
        manufacturer information in the image.”

        Human Feedback as correction for the product image: 
        - Avoid “The image shows”
        - Remove “The background is a solid white. There is no visible branding or manufacturer information in the image.”

        Second Image:

        Image Link: https://img5.su-cdn.com/cdn-cgi/image/width=1000,height=1000,format=webp/mall/file/2023/10/23/0ee4fafd2f4bff74cddfe2ac1c850e90.jpg       
        
        AI Description for Product image:

        "The image shows a coffee table with a brown wooden top and white sides and bottom. The table has two 
         compartments, one on each side. The compartments have a white front and a brown wooden frame. The table is
         positioned in the center of the image, with a white background. The table is positioned at an angle.
         There is no visible brand or manufacturer information on the product.  There is no text present on the 
         product or image."

        Human Feedback as correction for the product image:
        - Avoid “The image shows”
        - Remove “white background”
        - Remove the words “There is no visible brand or manufacturer information on the product.  There is no text present on the product or image.”

        Third Image:

        Image Link: https://img5.su-cdn.com/cdn-cgi/image/width=1000,height=1000,format=webp/mall/file/2022/04/28/a177a1169cb83b42fc30bc4357e2238f.jpg

        AI Description for Product image:

        "The image shows a white square coffee table with a glossy finish. Three drawers are positioned on the 
        bottom of the table, and one of the drawers is pulled out to reveal a light-colored wood interior. The 
        table has a thin gold trim bordering the top surface. The table is situated on a light-colored carpet in 
        a room that has a beige couch with a patterned pillow on the left side. A bouquet of white flowers is on
        the table in a clear glass vase. A stack of books sits behind the vase. An orange armchair is on the 
        left side of the image with a portion of a white curtain visible in the background.  A portion of a 
        black side table is visible behind the couch.  There is no brand or manufacturer information visible in
        the image. "

        Human Feedback as correction for the product image:
        - Avoid “The image shows”
        - Use “two drawers” instead of “three drawers”
        - Use “the two drawers are drawn out” in place of “one of the drawers is drawn out”
        - Only describe the product when a lifestyle image is used as a product image.

        """

    elif image_type == "Lifestyle Image long desc":
        return """
        
        Prompt for Lifestyle Image Long Description:
        You are an expert image annotatator. You have the task is to give a detailed description of the lifestyle image.
        Ensure your description is in human tone, very basic english, not like a machine wrote it.
        Ensure you make the description basic making it fit to train a machine model

        Ensure you adhere to the further instructions below:
        
        1. Details to include: 
            - color.
            - Context: Describe the context and surroundings.
            - Focus on Subjects: Detail the person using the product:
            - Appearance
            - Clothing
            - Posture
          - Objects: Describe any objects being held, including their positions.
          - Environment: Include details of the background elements and any relevant interactions.
          - Tone: Capture every visual detail without inferring emotions or marketing implications.
          - Include much details in your description. 

        2. Ensure you avoid the below in your description:
          - Avoid “The image shows” or  "The image showcases”, "the image appears to be …” instead Start with "A …’
          - There is no need to include this  “There is no visible brand or manufacturer information on the product.  There is no text present on the product or image.”.
          - Avoid Short description for the product image, make your description long.
          - Do not include the words "depicted", or "minimalistic" in your description.
          - Avoid describing persons or objects not visible in the image. e.g "There is no shadow present in the image. The image is well lit"
          - do not include sentence like this "The overall design aesthetic is minimalist and modern, with a focus on clean lines and neutral tones. No people are present in the image."
          - do not inlude suggestion from your end or any functions in the image in your description e.g "The entire scene is uncluttered and suggests a well-maintained and stylish living space."
          - Avoid describing background color for the product image.
          - Avoid Short description for the product image, make your description long.

        3. For accuracy in your lifestyle image description, check the below images link, AI Description and the Human feedback as correction 

        First Image: 

        Image Link:https://img5.su-cdn.com/cdn-cgi/image/width=1000,height=1000,format=webp/mall/file/2024/04/15/21c00a2b1876f20c3fc04ecd9a08d497.jpg
        
        AI Description for Lifestyle image:

        "The image shows a living room with a large window overlooking a green space and a cityscape in the
        distance. Sheer white curtains hang on a rod to the left of the window, and thick gray curtains are to
        the right of the window. A large beige area rug covers most of the hardwood floor. A wooden coffee table
        with a round white marble top sits on the rug. The coffee table has a dark brown wooden base and brass
        legs. A closed book is laying on the table. Two gray ottomans are positioned on either side of the coffee
        table, and one more ottoman is placed behind the coffee table. A partially visible beige sofa sits in the
        left foreground. There is a wicker chair with wooden arms in the background near the window. To the right
        of the window, a small, leafy green plant is potted in a square, light-colored container on the hardwood
        floor. A flat screen television sits in the background on the right side of the image, mounted on a 
        light-colored wall."

        Human Feedback as correction for the Lifestyle image: 
        - Remove “The image shows”
        - Use “golden legs” in place of “brass legs”
        - Use “open book” in place of “closed book”


        Second Image:

        Image Link: https://img5.su-cdn.com/cdn-cgi/image/width=1000,height=1000,format=webp/mall/file/2023/10/23/a00583c8fded2a29dcb4a2e353ef62b6.jpg     

        AI Description for Lifestyle image:

        "The image shows a modern living room with a large, flat-screen television mounted on the wall above a
        long, white media console with a wooden base. The media console is situated in front of a wall panel
        consisting of vertical, wooden slats.  A rectangular, brown coffee table with a white top is placed on a
        beige rug. The coffee table features a shelf on the lower portion of the brown side.  A small bouquet of
        dried flowers in a black vase is placed on the top of the table, along with a white candle.  A rectangular
        tray with a black bowl, a white candle, and a small, white book is placed in the center of the white
        section of the coffee table.  The room is brightly lit and appears to be empty, except for the furniture
        and decor."

        Human Feedback as correction for the Lifestyle image: 
        - Remove "The image shows a”

        """
    return ""


# Function to verify user login
def login(password_input):
    """Simple function to verify the password."""
    if password_input == APP_PASSWORD:
        st.session_state["logged_in"] = True
        st.success("Login successful! You can now use the app.")
    else:
        st.error("Incorrect password. Please try again.")

# Streamlit app interface
def main():
    st.title("SBX Image Caption Generator")

    # Instructional Dropdown
    with st.expander("ℹ️ How to Use the App", expanded=False):
        st.write("""
        1. Input the **Product Image URL** in the first column and **Lifestyle Image URL** in the second column.
        2. Click the 'Generate Description' button to generate an image description.
        3. Edit the generated description in the text box if necessary and copy it for your use.
                 
        **Note:**
        1. The Image Caption Tool may not support sensitive images.
        2. If the usage limit is reached, an error message will be displayed.
        """)

    # Sidebar for login
    with st.sidebar:
        st.subheader("Login")
        password_input = st.text_input("Enter the application password:", type="password")
        if st.button("Login"):
            login(password_input)

    # Check if the user is logged in
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        # Initialize session state variables for persistence
        if "product_description" not in st.session_state:
            st.session_state["product_description"] = ""
        if "lifestyle_description" not in st.session_state:
            st.session_state["lifestyle_description"] = ""

        # Create two columns for product and lifestyle image URLs
        col1, col2 = st.columns([1, 1], gap="large")

        # Column 1: Product Image Section
        with col1:
            st.subheader("Product Image")
            product_url = st.text_input("Enter Product Image URL")

            if product_url:
                try:
                    product_image = download_image_from_url(product_url)
                    st.image(product_image, caption='Product Image', width=300)

                    if st.button("Generate Product Description"):
                        prompt = get_prompt("Product Image")
                        st.session_state["product_description"] = generate_image_descriptions(product_image, prompt)

                except Exception as e:
                    st.error(f"Error loading product image: {str(e)}")

            # Display product description with persistence
            st.text_area("Product Description", st.session_state["product_description"], height=150)

        # Column 2: Lifestyle Image Section
        with col2:
            st.subheader("Lifestyle Image")
            lifestyle_url = st.text_input("Enter Lifestyle Image URL")

            if lifestyle_url:
                try:
                    lifestyle_image = download_image_from_url(lifestyle_url)
                    st.image(lifestyle_image, caption='Lifestyle Image', width=300)

                    if st.button("Generate Lifestyle Description"):
                        prompt = get_prompt("Lifestyle Image")
                        st.session_state["lifestyle_description"] = generate_image_descriptions(lifestyle_image, prompt)

                except Exception as e:
                    st.error(f"Error loading lifestyle image: {str(e)}")

            # Display lifestyle description with persistence
            st.text_area("Lifestyle Description", st.session_state["lifestyle_description"], height=150)

    else:
        st.warning("Please log in to use the application.")

if __name__ == "__main__":
    main()
