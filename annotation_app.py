import streamlit as st
from PIL import Image
import io
import os
import google.generativeai as genai
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Google API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash-002")

# Function to generate image descriptions using LLM
def generate_image_descriptions(image, prompt):
    """Send image and prompt to LLM to get descriptions."""
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=image.format)
    img_byte_arr.seek(0)  # Go back to the start of the buffer

    # Generate response using the model
    response = model.generate_content([prompt, image])
    generated_text = response.candidates[0].content.parts[0].text
    return generated_text

 # Function to get prompt based on image type
def get_prompt(image_type):
    """Return the appropriate prompt based on the image type."""
    if image_type == "Product Image":
        return (           
           """**For the Short Description:**

            - Emphasize simplicity and conciseness.
            - Focus on the essential elements: the object's identity, shape (if applicable), function, material, and color.
            - Ensure you keep the description between 8 to 15 words but ensure is under 15 words.
            - Avoid excessive detail and focus on the core attributes.
            - Example: "Cordless vacuum, light blue base, silver-gold handle."

            **For the Long Description:**

            - Provide comprehensive details, including color, material, brand or manufacturer, and additional features.
            - Describe the background of the image including any artistic or design elements.
            - Include any text present on the image or the product itself.
            - Avoid promotional language and focus on objective description for machine learning understanding.
            - Limit details to those observable in the image, excluding information only available from product descriptions.
            - Any positioning should be based on your perspective looking at the image e.g. left, right
            - Ensure you pay attention to the position of the product in the image and include the detail in the decription
            - Finally, ensure you include every details in the image.
            """
        )
    elif image_type == "Lifestyle Image":
        return ("""  For the Short Description of the Lifestyle Image:

                    Emphasize simplicity and conciseness.
                    Focus on key elements: object, shape, function, material, and color.
                    Ensure you keep the description between 8 to 15 words but ensure is under 15 words.
                    Avoid excessive detail and focus on core attributes.
                    Example: "Person using a blue laptop at a cafe."
                    For the Long Description:

                    Provide comprehensive details, including colors, materials, brands, and features.
                    Describe the background if it contains design elements.
                    Include any text present on the image or the product.
                    Avoid promotional language and focus on objective description for machine learning.
                    Limit details to those observable in the image, excluding information from product descriptions.
                    Use a consistent perspective (e.g., left, right) for positioning.
                    Avoid describing feelings or emotions tied to the image.
                    Focus on positions like left, right, centered, etc.
                    Provide detailed descriptions of the person using the product, including color, hairstyle, posture, etc.
                    Ensure the description fully captures the lifestyle context of the image.
                    Any positioning should be based on your perspective looking at the image e.g. left, right
                    - Ensure you pay attention to the position of the product in the image and include the detail in the decription 
                    - if the person in the image is holding any object consider the positioning of the object held interm of wheher rigth or left.
                    - Finally, ensure you include every details in the image.
                 """
        )
    return ""

# Helper function to open an image from URL
def load_image(image_source):
    try:
        if isinstance(image_source, str) and image_source.startswith("http"):
            response = requests.get(image_source)
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content))
        else:
            return Image.open(image_source)
    except Exception:
        st.error("Image not supported or usage limit reached. Please try again or contact the developer.")
        return None

# Streamlit app interface
def main():
    st.title("SBX Image Caption Generator")

    image_type = st.selectbox("Select Image Type", ["Product Image", "Lifestyle Image"])
    image_url = st.text_input("Enter image URL (optional)")
    uploaded_image = st.file_uploader("Or upload an image", type=["jpg", "jpeg", "png", "webp", "avif"])
    
    image_source = uploaded_image or image_url
    
    if image_source:
        image = load_image(image_source)
        
        if image:
            st.image(image, caption='Uploaded Image', width=300)
            prompt = get_prompt(image_type)

            if st.button("Generate Description"):
                try:
                    generated_text = generate_image_descriptions(image, prompt)
                    st.write("**Generated Description:**", generated_text)
                except Exception:
                    st.error("Image not supported or usage limit reached. Please try again or contact the developer.")

if __name__ == "__main__":
    main()








# import streamlit as st
# from PIL import Image
# import io
# import os
# import google.generativeai as genai
# from dotenv import load_dotenv
# #models/gemini-1.5-flash
# #gemini-1.5-pro
# # gemini-1.5-pro-002
# # Load environment variables
# load_dotenv()

# # Google API Configuration
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# genai.configure(api_key=GOOGLE_API_KEY)
# model = genai.GenerativeModel("models/gemini-1.5-flash-002")

# # Function to generate image descriptions using LLM
# def generate_image_descriptions(image, prompt):
#     """Send image and prompt to LLM to get descriptions."""
    
#     # Convert the image to a byte array (Blob)
#     img_byte_arr = io.BytesIO()
#     image.save(img_byte_arr, format=image.format)
#     img_byte_arr.seek(0)  # Go back to the start of the buffer

#     # Prepare the input as content
#     contents = [
#         prompt,  # Pass the prompt as a simple string
#         Image.open(img_byte_arr)  # Pass the image correctly as a PIL image
#     ]

#     # Generate response using the model
#     response = model.generate_content(contents)

#     # Extract the generated content text from the response
    
#     generated_text = response.candidates[0].content.parts[0].text
#     return generated_text

# # Function to get prompt based on image type
# def get_prompt(image_type):
#     """Return the appropriate prompt based on the image type."""
#     if image_type == "Product Image":
#         return (           
#            """**For the Short Description:**

#             - Emphasize simplicity and conciseness.
#             - Focus on the essential elements: the object's identity, shape (if applicable), function, material, and color.
#             - Ensure you keep the description between 8 to 15 words but ensure is under 15 words.
#             - Avoid excessive detail and focus on the core attributes.
#             - Example: "Cordless vacuum, light blue base, silver-gold handle."

#             **For the Long Description:**

#             - Provide comprehensive details, including color, material, brand or manufacturer, and additional features.
#             - Describe the background of the image including any artistic or design elements.
#             - Include any text present on the image or the product itself.
#             - Avoid promotional language and focus on objective description for machine learning understanding.
#             - Limit details to those observable in the image, excluding information only available from product descriptions.
#             - Any positioning should be based on your perspective looking at the image e.g. left, right
#             - Ensure you pay attention to the position of the product in the image and include the detail in the decription
#             - Finally, ensure you include every details in the image.
#             """
#         )
#     elif image_type == "Lifestyle Image":
#         return ("""  For the Short Description of the Lifestyle Image:

#                     Emphasize simplicity and conciseness.
#                     Focus on key elements: object, shape, function, material, and color.
#                     Ensure you keep the description between 8 to 15 words but ensure is under 15 words.
#                     Avoid excessive detail and focus on core attributes.
#                     Example: "Person using a blue laptop at a cafe."
#                     For the Long Description:

#                     Provide comprehensive details, including colors, materials, brands, and features.
#                     Describe the background if it contains design elements.
#                     Include any text present on the image or the product.
#                     Avoid promotional language and focus on objective description for machine learning.
#                     Limit details to those observable in the image, excluding information from product descriptions.
#                     Use a consistent perspective (e.g., left, right) for positioning.
#                     Avoid describing feelings or emotions tied to the image.
#                     Focus on positions like left, right, centered, etc.
#                     Provide detailed descriptions of the person using the product, including color, hairstyle, posture, etc.
#                     Ensure the description fully captures the lifestyle context of the image.
#                     Any positioning should be based on your perspective looking at the image e.g. left, right
#                     - Ensure you pay attention to the position of the product in the image and include the detail in the decription 
#                     - if the person in the image is holding any object consider the positioning of the object held interm of wheher rigth or left.
#                     - Finally, ensure you include every details in the image.
#                  """
#         )
#     return ""

# # Streamlit app interface
# def main():
#     st.title("SBX Image Caption Generator.")

#     # Image type selection
#     image_type = st.selectbox("Select Image Type", ["Product Image", "Lifestyle Image"])

#     # Upload image
#     uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp", "avif"])
    
#     if uploaded_image:
#         # Display uploaded image
      
    
    
      
    
#         image = Image.open(uploaded_image)
#         st.image(image, caption='Uploaded Image', width=300)

#         # Generate the appropriate prompt for the selected image type
#         prompt = get_prompt(image_type)

#         # Button to generate captions
#         if st.button("Generate Description"):
#             generated_text = generate_image_descriptions(image, prompt)
#             st.write("**Generated Description:**", generated_text)

# if __name__ == "__main__":
#     main()


