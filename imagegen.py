import openai
import os

# Set your API key
openai.api_key = "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"

# Function to generate an image using the OpenAI API
def generate_image(image_prompt):
    image_data = openai.Image.create(
        prompt=image_prompt,
        n=1,
        size="1024x1024",
        response_format="url"
    )
    return image_data

# Main script
if __name__ == "__main__":
    # Ask for text input
    user_input = input("Enter a description for the image you'd like to generate: ")

    # Generate the raw response
    response = generate_image(user_input)

    # Display the raw response
    print("Raw response:", response)
