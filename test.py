# Brian Lesko
# 06/09/2024
# Classify Images using VGG16 in a web app, fetch the camera feed, preprocess the image, and make a prediction in real-time.

import streamlit as st
import torch
import numpy as np
import torchvision.models as models # contains the the VGG16 pretrained network.
import torchvision.transforms as transforms
import cv2
from PIL import Image
import time
import torch.nn as nn

st.title('Image Model using VGG16')

# Load the custom model
model = models.vgg16()  # Create a new model

# Modify the classifier
input_features = model.classifier[0].in_features
model.classifier = nn.Sequential(
    nn.Linear(input_features, 256),
    nn.ReLU(),
    nn.Dropout(p=0.6),
    nn.Linear(256, 1),
    nn.Tanh() # results in a value between -1 and 1
)

model.load_state_dict(torch.load('model.pth'))  # Load the weights

# Preprocess the image to fit the model
preprocess = transforms.Compose([
    transforms.Resize(224),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])  

model.eval()

# Placeholders for image and predicion
col1, col2, col3, col4 = st.columns([.5, 6, 2, .5])
with col2:
    st.write("Camera Feed")
    ImageSpot = st.empty()
with col3:
    st.write("Preprocessed Image")
    ImageSpot2 = st.empty()
    Prediction = st.empty()
    TimePlaceholder = st.empty()
    Time2Placeholder = st.empty()
    Time3Placeholder = st.empty()

# Use opencv to get the current camera frame
# get the camera feed from the TCP stream at 10.42.0.1:8000
if "camera" not in st.session_state:
    #st.session_state.camera = cv2.VideoCapture(0)
    #st.session_state.camera = cv2.VideoCapture('tcp://10.42.0.1:8000')
    #st.session_state.camera = cv2.VideoCapture('udp://0.0.0.0:8000')
    st.session_state.camera = cv2.VideoCapture('rtsp://10.42.0.1:8554/stream1')
    st.session_state.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    st.session_state.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    st.session_state.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    st.session_state.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUY2')) # faster than MJPG

count=0
start_time = time.time()
while True: 
  try:
    count = count+1
    ret, frame = st.session_state.camera.read()
    ret, jpeg = cv2.imencode('.jpg', frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # show the input image
    frameo = cv2.resize(frame, None, fx=2, fy=2)
    ImageSpot.image(frameo, channels="RGB")

    # Preprocess the image
    time1 = time.time()
    image = Image.fromarray(frame)  # convert OpenCV image to PIL image
    image = preprocess(image)
    # show the preprocess image
    image_disp = transforms.ToPILImage()(image.squeeze(0))
    ImageSpot2.image(image_disp)
    image = image.unsqueeze(0)  # simulate a batch
    Time2Placeholder.write(f'Preprocess Time: {time.time() - time1}')

    # Make a prediction
    time1 = time.time()
    output = model(image)
    Time3Placeholder.write(f'Prediction Time: {time.time() - time1}')
    Prediction.write(f"Prediction: {output.item()}")
    TimePlaceholder.write(f'FPS: {count/(time.time()-start_time)}')
  except: pass