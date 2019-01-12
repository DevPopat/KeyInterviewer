subscription_key = "deedc4397f034fe8b4c97f872ba7b745"
assert subscription_key
face_api_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/detect'
image_url = 'https://how-old.net/Images/faces2/main007.jpg'
import requests

headers = { 'Ocp-Apim-Subscription-Key': subscription_key }

params = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
}

image_path = "Training/thumb0001.jpg"
image_data = open(image_path, "rb").read()

response = requests.post(face_api_url, params=params, headers=headers, json={"data": image_data})
print(response)
faces = response.json()
print(faces[1]['faceAttributes']['emotion'])
