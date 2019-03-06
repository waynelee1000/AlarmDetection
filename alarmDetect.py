#!/usr/bin/python

# open a microphone in pyAudio and listen for taps

import pyaudio
import struct
import math
import tkinter as tk
import smtplib

def EmailClient(value):
    if value:
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            print("Connected to Gmail")
            FROM = ""
            TO = ""
            SUBJECT = "Grandma"
            TEXT = "Grandma needs help"

            # Prepare actual message
            message = """From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

            server.login("", " ")
            server.sendmail(FROM, TO, message)
            server.close()
            print ('successfully sent the mail')
        except:
            print ('Something went wrong...')

INITIAL_TAP_THRESHOLD = 0.1
FORMAT = pyaudio.paInt16
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 2
RATE = 44100
INPUT_BLOCK_TIME = 0.05
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)

def get_rms( block ):
    # RMS amplitude is defined as the square root of the
    # mean over time of the square of the amplitude.
    # so we need to convert this string of bytes into
    # a string of 16-bit samples...

    # we will get one short out for each
    # two chars in the string.
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, block )

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768.
        # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    return math.sqrt( sum_squares / count )

class TapTester(object):
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()
        self.tap_threshold = INITIAL_TAP_THRESHOLD
        self.errorcount = 0

    def stop(self):
        self.stream.close()

    def find_input_device(self):
        device_index = None
        for i in range( self.pa.get_device_count() ):
            devinfo = self.pa.get_device_info_by_index(i)
            print( "Device %d: %s"%(i,devinfo["name"]) )

            for keyword in ["mic","input"]:
                if keyword in devinfo["name"].lower():
                    print( "Found an input: device %d - %s"%(i,devinfo["name"]) )
                    device_index = i
                    return device_index

        if device_index == None:
            print( "No preferred input found; using default input device." )

        return device_index

    def open_mic_stream( self ):
        device_index = self.find_input_device()

        stream = self.pa.open(   format = FORMAT,
                                 channels = CHANNELS,
                                 rate = RATE,
                                 input = True,
                                 input_device_index = device_index,
                                 frames_per_buffer = INPUT_FRAMES_PER_BLOCK)

        return stream

    def tapDetected(self):
        print ("Tap!")
        EmailClient(True)

    def listen(self):
        try:
            block = self.stream.read(INPUT_FRAMES_PER_BLOCK)
        except IOError as e:

            # dammit.
            self.errorcount += 1
            print( "(%d) Error recording: %s"%(self.errorcount,e) )
            return

        amplitude = get_rms( block )
        if amplitude > self.tap_threshold:
            # noisy block
            self.tapDetected()


root = tk.Tk()

root.title("AudioDetect")
frame = tk.Frame(root)
frame.pack()
global running
running = True

def Start():
    global running
    running = True
def Stop():
    global running
    running = False
    print ("STOP!!!")

def Process():
    if (running):
        tt = TapTester()
        tt.listen()
    root.after(1000, Process)

button = tk.Button(frame,
   text="Quit",
   fg="red",
   command= Stop)
button.pack(side=tk.LEFT)
slogan = tk.Button(frame,
    text="Start",
    command= Start)
slogan.pack(side=tk.LEFT)

root.after(100, Process)
root.mainloop()
