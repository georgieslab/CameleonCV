import requests

url = "https://georgieslab--cameleon-cv-transform-cv.modal.run"

print("Sending request... (first run takes ~60s to load model)")

response = requests.post(url, json={
    "cv_text": "I did a lot of data analysis stuff and made some reports for the team.",
    "style": "Playful",
    "section_type": "Work Experience"
})

print("\nResponse:")
print(response.json())