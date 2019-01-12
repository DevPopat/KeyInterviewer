import numpy as np
from flask import Flask, render_template, request, jsonify, redirect
from flask_mail import Message
import requests
import pickle
import cv2
import pyaudio
import wave
import threading
import time
import subprocess
import os
import shutil
import stat

app =Flask(__name__)


class VideoRecorder():
    # Video class based on openCV
    def __init__(self):

        self.open = True
        self.device_index = 0
        self.fps = 15             # fps should be the minimum constant rate at which the camera can
        self.fourcc = "MJPG"       # capture images (with no decrease in speed over time; testing is required)
        self.frameSize = (640,480) # video formats and sizes also depend and vary according to the camera used
        self.video_filename = "temp_video.mp4"
        self.video_cap = cv2.VideoCapture(self.device_index)
        self.video_writer = cv2.VideoWriter_fourcc(*self.fourcc)
        self.video_out = cv2.VideoWriter(self.video_filename, self.video_writer, self.fps, self.frameSize)
        self.frame_counts = 1
        self.start_time = time.time()


    # Video starts being recorded
    def record(self):

#		counter = 1
        timer_start = time.time()
        timer_current = 0


        while(self.open==True):
            ret, video_frame = self.video_cap.read()
            if (ret==True):

                self.video_out.write(video_frame)
#					print str(counter) + " " + str(self.frame_counts) + " frames written " + str(timer_current)
                self.frame_counts += 1
#					counter += 1
#					timer_current = time.time() - timer_start
                time.sleep(0.10)

    # Uncomment the following three lines to make the video to be
    # displayed to screen while recording

                #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                cv2.imshow('video_frame', video_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break

    # 0.16 delay -> 6 fps
    #


    # Finishes the video recording therefore the thread too
    def stop(self):

        if self.open==True:

            self.open=False
            self.video_out.release()
            self.video_cap.release()
            cv2.destroyAllWindows()
        else:
            pass


    # Launches the video recording function using a thread
    def start(self):
        video_thread = threading.Thread(target=self.record)
        video_thread.start()





class AudioRecorder():


    # Audio class based on pyAudio and Wave
    def __init__(self):

        self.open = True
        self.rate = 44100
        self.frames_per_buffer = 1024
        self.channels = 2
        self.format = pyaudio.paInt16
        self.audio_filename = "temp_audio.wav"
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      frames_per_buffer = self.frames_per_buffer)
        self.audio_frames = []


    # Audio starts being recorded
    def record(self):

        self.stream.start_stream()
        while(self.open == True):
            data = self.stream.read(self.frames_per_buffer)
            self.audio_frames.append(data)
            if self.open==False:
                break


    # Finishes the audio recording therefore the thread too
    def stop(self):

        if self.open==True:
            self.open = False
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()

            waveFile = wave.open(self.audio_filename, 'wb')
            waveFile.setnchannels(self.channels)
            waveFile.setsampwidth(self.audio.get_sample_size(self.format))
            waveFile.setframerate(self.rate)
            waveFile.writeframes(b''.join(self.audio_frames))
            waveFile.close()

        pass

    # Launches the audio recording function using a thread
    def start(self):
        audio_thread = threading.Thread(target=self.record)
        audio_thread.start()





def start_AVrecording(filename):

    global video_thread
    global audio_thread

    video_thread = VideoRecorder()
    audio_thread = AudioRecorder()

    audio_thread.start()
    video_thread.start()

    return filename

def start_video_recording(filename):

    global video_thread

    video_thread = VideoRecorder()
    video_thread.start()

    return filename

def start_audio_recording(filename):

    global audio_thread

    audio_thread = AudioRecorder()
    audio_thread.start()

    return filename


def stop_AVrecording(filename):

    audio_thread.stop()
    frame_counts = video_thread.frame_counts
    elapsed_time = time.time() - video_thread.start_time
    recorded_fps = frame_counts / elapsed_time
    totalFrameString = "total frames " + str(frame_counts)
    elapseTimeString = "elapsed time " + str(elapsed_time)
    recordedFpsString = "recorded fps " + str(recorded_fps)
    print (totalFrameString)
    print (elapseTimeString)
    print (recordedFpsString)
    video_thread.stop()

    time.sleep(0.5)


#	 Merging audio and video signal

    if abs(recorded_fps - 6) >= 0.01:    # If the fps rate was higher/lower than expected, re-encode it to the expected

        print ("Re-encoding")
        cmd = "ffmpeg -r " + str(recorded_fps) + " -i temp_video.mp4 -pix_fmt yuv420p -r 6 temp_video2.mp4"
        subprocess.call(cmd, shell=True)

        local_path = os.getcwd()

        print ("Muxing")


        cmd = "ffmpeg -ac 2 -channel_layout stereo -i temp_audio.wav -i temp_video2.mp4 -pix_fmt yuv420p "+ str(local_path) + "/static/" + filename + ".mp4"
        subprocess.call(cmd, shell=True)

    else:
        local_path = os.getcwd()
        print ("Normal recording\nMuxing")
        cmd = "ffmpeg -ac 2 -channel_layout stereo -i temp_audio.wav -i temp_video.mp4 -pix_fmt yuv420p " + str(local_path) +"/static/" + filename + ".mp4"
        subprocess.call(cmd, shell=True)

        print ("..")


def spliceImages():
    local_path = os.getcwd()
    cmd = "ffmpeg -i temp_video.mp4 -vf fps=1/2 D:\SplicedJPEGS/thumb%04d.jpg -hide_banner"
    subprocess.call(cmd, shell=True)


# Required and wanted processing of final files
def file_manager(filename):

    local_path = os.getcwd()

    if os.path.exists("D:\SplicedJPEGS"):
        os.chmod("D:\SplicedJPEGS", 0o777)
        shutil.rmtree("D:\SplicedJPEGS")
        os.mkdir("D:\SplicedJPEGS")


    if os.path.exists(str(local_path) + "/temp_audio.wav"):
        os.remove(str(local_path) + "/temp_audio.wav")

    if os.path.exists(str(local_path) + "/temp_video.mp4"):
        os.remove(str(local_path) + "/temp_video.mp4")

    if os.path.exists(str(local_path) + "/temp_video2.mp4"):
        os.remove(str(local_path) + "/temp_video2.mp4")

    if os.path.exists(str(local_path) + "/static/" + filename + ".mp4"):
        os.remove(str(local_path) + "/static/" + filename + ".mp4")

@app.route('/')
def live():
    return render_template("landing.html")

@app.route('/final')
def final():
    files = (os.listdir("D:\SplicedJPEGS"))
    subscription_key = "deedc4397f034fe8b4c97f872ba7b745"
    assert subscription_key
    emotion_recognition_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/detect'

    for x in files:
        image_data = open("D:\SplicedJPEGS\\" + x, "rb").read()
        params = {
            'returnFaceId': 'true',
            'returnFaceLandmarks': 'false',
            'returnFaceAttributes': 'emotion',
        }
        headers  = {'Ocp-Apim-Subscription-Key': subscription_key, "Content-Type": "application/octet-stream" }
        response = requests.post(emotion_recognition_url, params=params, headers=headers, data=image_data)
        response.raise_for_status()
        analysis = response.json()
        try:
            (analysis[0]['faceAttributes']['emotion'])
        except:
            pass

    return render_template("finished.html")

@app.route('/first')
def first():
    return render_template("initial_vid.html")

@app.route('/finished')
def finished():
    return render_template("finished.html")

@app.route('/countdown')
def countdown():
    return render_template("countdown.html")

@app.route('/recording')
def recording():
    return render_template("recording.html")

@app.route('/analysis')
def analysis():
    return render_template("analysis.html")

@app.route('/recordingStart')
def recordingStart():

    filename = "Default_user"
    file_manager(filename)
    start_AVrecording(filename)
    time.sleep(10)
    stop_AVrecording(filename)
    spliceImages()
    print("Done")
    return "5"

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0',port=5000)
