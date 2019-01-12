import requests
subscription_key = "deedc4397f034fe8b4c97f872ba7b745"
assert subscription_key
emotion_recognition_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/detect'
image_path = "Training/thumb0001.jpg"
image_path_2 = "Training/thumb0002.jpg"
image_data = {open(image_path, "rb").read(), open(image_path_2, "rb").read()}
params = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'emotion',
}
headers  = {'Ocp-Apim-Subscription-Key': subscription_key, "Content-Type": "application/octet-stream" }
response = requests.post(emotion_recognition_url, params=params, headers=headers, data=image_data)
response.raise_for_status()
analysis = response.json()
print(analysis[0]['faceAttributes']['emotion'])
