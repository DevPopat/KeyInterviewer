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
import io

app =Flask(__name__)

question_counter = []
#showsreading from a text file

good_words = ["communication", "communicated", "leadership", "leading", "lead", "excited","exciting", "excite", "motivated","motivate", "motivating", "learn", "learning", "learned","team", "teamwork","team player",
              "inspired","responsiblity","responsible", "energize", "energizing", "energized", "enthusiastic", "enthusiatically", "efficient", "efficiently", "organized", "organizing", "organize", "initiative",
              "initiating", "initiated", "initiating", "initiate", "negotiated", "negotiate", "negotiating", "resolve", "resolving", "reslved", "plan", "planned", "planning", "accomplished", "accomplishing",
              "accomplish", "prioritized", "prioritize", "prioriztizing", "hard work", "hard working", "proactive", "proactively", "diversity", "diversify", "empowering", "empower", "empowered", "grow", "grew",
              "streamlined", "streamline", "streamlining", "leverage", "leveraging", "leveraged", "robust", "alignment", "aligning", "aligned", "align", "reached out", "reaching out", "reach out",
              "growth", "reimagine", "reimagined", "reimagining", "accountable", "accountability", "invest", "invested", "investing", "guide", "guiding", "guided", "differentiate", "differentiated", "differeniating",
              "schedule", "scheduling", "scheduled", "engagement", "engaging", "engage", "engaged", "bandwidth", "mission", "mission critical", "cooperation", "cooperating", "cooperated",
              "cooperate", "listen", "listening", "listened", "creative", "visibility", "transparent", "transparency", "agile", "innovating", "innovation", "innovated", "innovate", "scalability", "scalable",
              "manage", "managed", "managing", "machine learning", "blockchain", "robotics", "networked", "networking", "network", "stakeholder", "cross platform", "inspire", "inspired", "inspiring", "grit",
              "metacognition", "thoughtful", "throughput", "curate", "curating", "curated", "automated", "automation", "automate", "AI", "impact", "impactful", "disrupt", "disrupting",
              "communicate", "communicating", "communication", "communicated", "passion", "passionate", "pivot", "pain points", "quality", "repurpose", "repurposed", "repurposing", "purpose",
              "visual", "visualizing", "visualized", "personlization", "VR", "visual reality", "artificial intelligence", "AR", "augmented reality", "XR", "OLED", "haptics", "redesigned", "redesign", "redesigning",
              "design", "designing", "designed", "rethink", "intuitive", "intuition", "responsive", "engineer", "engineered", "engineering", "problem solving", "active", "actively", "secure", "augment",
              "augmenting", "augmented", "supportive", "support", "supporting", "supported", "enhance", "enhancing", "enhanced", "enhansive", "immerse", "immersive", "immersing", "immersed",
              "connection", "connecting", "connect", "overcome", "overcame", "overcoming", "comprehensive", "comprehensively", "interactive", "achieve", "achieving", "achieved", "achievement", "cinematic","adapt","urgent","interested","mission","vision"]
bad_words = ["ummm", "um", "uh", "oh", "huh", "like", "liked", "liking", "so", "I don't", "don't", "do not", "I can't", "can't", "nervous","sorry", "bad", "hated", "hating", "hate", "disgust", "disgusting", "incompetent", "less competent", "sick",
             "bro", "actually", "just", "vacation", "pay", "shit", "shithead", "garbage", "fuck", "fucked", "fucking", "bitch", "ass", "asshole", "not good", "I don't know", "fine", "terrible", "awful", "fag",
             "faggot", "damn", "dammit", "damning","jerk", "jerkoff", "butthole", "angry", "lazy", "crazy", "craziness", "dull", "sluggish", "passive", "passive aggressive", "passively", "coast", "coasting", "coasted",
             "irresponsible", "irresponsibly", "irresponsibility", "ignorant", "ignorantly", "racist", "bigot", "sexist", "homophobic", "transphobic", "divorce", "careless", "care-free", "chill", "kush", "420", "dank", "dope",
             "drunk", "bong", "blunt", "vape", "vaping", "vaped", "OG","oops", "oopsy", "oopsie", "millennial", "synergy", "synergize", "synergizing", "synergized", "lack", "lacking", "lacked", "maybe","I think","money", "income","crap","bothered","incapable","stuff"]

class QuestionCounter():
    def __init__(self):
        self.question = 1;
        self.lastProcessed = ""
        self.recentScore = 0
        self.goodArray = []
        self.badArray = []

    def update(self, x):
        self.lastProcessed = x

    def getIt(self):
        return self.lastProcessed;

    def incrementQuestion(self):
        self.question = self.question + 1;
        if (self.question == 11):
            self.question = 1

    def getQuestion(self):
        return self.question;

    def updateScore(self, x):
        self.recentScore = x;

    def getScore(self):
        return self.recentScore;

    def getArrs(self):
        return [self.badArray, self.goodArray]

    def updateArrs(self, x, y):
        self.goodArray = x
        self.badArray = y



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

        cmd = "ffmpeg -i temp_audio.wav -ac 1 temp_mono.wav"
        subprocess.call(cmd, shell=True)

    else:
        local_path = os.getcwd()
        print ("Normal recording\nMuxing")
        cmd = "ffmpeg -ac 2 -channel_layout stereo -i temp_audio.wav -i temp_video.mp4 -pix_fmt yuv420p " + str(local_path) +"/static/" + filename + ".mp4"
        subprocess.call(cmd, shell=True)

        cmd = "ffmpeg -i temp_audio.wav -ac 1 temp_mono.wav"
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

    if os.path.exists(str(local_path) + "/temp_mono.wav"):
        os.remove(str(local_path) + "/temp_mono.wav")

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
    pointsPos = 0
    files = (os.listdir("D:\SplicedJPEGS"))
    subscription_key = "deedc4397f034fe8b4c97f872ba7b745"
    assert subscription_key
    emotion_recognition_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/detect'
    myArray = []
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
            emotions = (analysis[0]['faceAttributes']['emotion'])
            if not(emotions['happiness'] < 0.8 or emotions['neutral'] > 0.8 or emotions['sadness'] > 0.5):
                pointsPos = pointsPos + 1
                myArray.append(1)
            else:
                myArray.append(0)
        except:
            pass
        # Imports the Google Cloud client library
    firstScore = (5 / len(files)) * pointsPos
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types

    # Instantiates a client
    client = speech.SpeechClient()
    file_name = "temp_mono.wav"
    # Loads the audio into memory
    with io.open(file_name, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code='en-US')

    posPts = 0
    negPts = 0
    # Detects speech in the audio file
    response = client.recognize(config, audio)
    #print(response)
    x = ""
    for result in response.results:
        x = ('Transcript: {}'.format(result.alternatives[0].transcript))
        question_counter.update(x)
    x = x.split()
    for i in x:
        if i in good_words:
            posPts = posPts + 1
        elif i in bad_words:
            negPts = negPts + 1

    otherScore = 0
    try:
        otherScore = (posPts / (posPts + negPts)) * 5
    except:
        otherScore = 0


    question_counter.updateScore(otherScore + firstScore)
    #question_counter.update("One of the reasons I consider myself a suitable candidate for this role is my willingness for continually developing myself.")

    badArray = []
    goodArray = []
    while(len(myArray)>4):
        x = myArray[0:4]
        f = sum(x)
        badArray.append(4-f)
        goodArray.append(f)
        myArray = myArray[4:]
    m = len(myArray)
    k = sum(myArray)
    goodArray.append(k)
    badArray.append(m-k)
    question_counter.updateArrs(goodArray, badArray)
    return render_template("finished.html")

@app.route('/first')
def first():
    number = question_counter.getQuestion()
    question="static/Question" + str(number) +".mp4"
    question_counter.incrementQuestion()
    return render_template("initial_vid.html", question=question)

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

@app.route('/getThat')
def getThat():
    return jsonify([question_counter.getIt(), question_counter.getScore()])

@app.route('/writing')
def writing():
    return render_template("writing.html")

@app.route('/getArrays')
def arrayget():
    return jsonify(question_counter.getArrs())

@app.route('/essayScore')
def essayScore():
    e = request.args['essay']
    e = e.split()
    posPts = 0
    negPts = 0
    for i in e:
        if i in good_words:
            posPts = posPts + 1
        elif i in bad_words:
            negPts = negPts + 1
    otherScore = 0
    try:
        otherScore = (posPts / (posPts + negPts)) * 5
    except:
        otherScore = 0

    return render_template("essayScoring.html", score=otherScore)

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
    question_counter = QuestionCounter()
    app.run(host = '0.0.0.0',port=5000)
