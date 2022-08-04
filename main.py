import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import os 
from keyboard import read_key
import threading
import serial
from Xlib.display import Display

class App:
    def __init__(self, window : tkinter.Tk, window_title, video_source=0, loop_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.loop_source = loop_source

        # Get rid of the cursor, for this window
        window.config(cursor='none')

        # Open loop source and video source
        self.loop = MyVideoCapture(self.loop_source, loop=True)
        self.vid = MyVideoCapture(self.video_source)

        # The video currently playing will reference either vid or loop
        self.currently_playing = self.loop

        # Find the screen width and height
        screen = Display(':0').screen()
        self.screen_width = screen.width_in_pixels
        self.screen_height = screen.height_in_pixels

        # Create a canvas that can fit the above video source size
        self.border_color = 'black'
        self.bg_color = 'black'

        self.canvas = tkinter.Canvas(window, width = self.screen_width, height = self.screen_height, bg=self.bg_color,highlightbackground=self.border_color)
        self.canvas.pack()

        # Make the window fullscreen
        self.window.attributes('-fullscreen', True)

        # Creates a thread to enable listeners - currently it's keyboard listeners but could be sensor listeners.
        input_thread = threading.Thread(target=self.add_input)
        input_thread.daemon = True #<-- makes the thread destroyable
        input_thread.start()

        sensor_thread = threading.Thread(target=self.add_distance_check)
        sensor_thread.daemon = True #<-- makes the thread destroyable
        sensor_thread.start()

        # Stores the last pressed key, but can store last event, e.g. sensor input
        self.last_input = ''

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 13
        self.update()

        self.window.mainloop()

    def update(self):

        # If the thread determines the user pressed esc, kill the app
        if self.last_input == 'esc':
            exit()

        # If the thread determines the user pressed space, launch the video.
        if self.last_input == 'space':
            self.currently_playing = self.vid
            self.last_input = ''

        # Else, get a frame from the video source and business as usual
        ret, frame = self.currently_playing.get_frame()

        # Resize the frame to fit the screen
        frame = self.resize_frame(frame)

        # If the current frame happens to be the last one, restart the video and move to loop
        # Fyi, if the current frame happens to be the last one, it restarts the video and sets it to the loop
        if self.currently_playing.current_frame == self.currently_playing.total_frame_count:
            self.currently_playing.restart_video()
            self.currently_playing = self.loop

        # If the video frame is obtained successfully, render it on screen
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(self.window.winfo_width() / 2, self.window.winfo_height() / 2, image=self.photo, anchor=tkinter.CENTER)

        self.window.after(self.delay, self.update)

    def add_input(self):
        # Creates a listener that (for now) registers all keyboard events
        while True:
            self.last_input = read_key()
            #print(self.last_input)

    def add_distance_check(self):
        # Creates a listener that registers the distance of the object
        # that the UltraSound sensor had detected
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        ser.reset_input_buffer()

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                min_distance = 50

                #print(line)

                if self.currently_playing == self.loop and int(line) <= min_distance:
                    # Change to the video
                    self.currently_playing = self.vid

    def resize_frame(self, frame):
        width_ratio = self.screen_width / self.currently_playing.width
        height_ratio = self.screen_height / self.currently_playing.height

        # Chosen ratio we are gonna go with
        chosen_ratio = min(width_ratio, height_ratio)

        return cv2.resize(frame, [int(self.currently_playing.width * chosen_ratio), int(self.currently_playing.height * chosen_ratio)])

class MyVideoCapture:
    def __init__(self, video_source=0, loop=False):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        self.loop = loop

        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.total_frame_count = self.vid.get(cv2.CAP_PROP_FRAME_COUNT)
        self.current_frame = 0

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()

            # Looper part of the function
            # Taken from here: https://stackoverflow.com/a/27890487
            self.current_frame += 1

            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, frame)
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Set video source to 0th frame
    def restart_video(self):
        self.current_frame = 0 
        self.vid.set(cv2.CAP_PROP_POS_FRAMES, 0)
        

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

if __name__ == '__main__':
    # Create a window and pass it to the Application object
    #
    # NOTE: GIF files break everything, for some reason,
    #       Frame counts are broken as fuck
    video_source = os.getcwd() + "/text_short.mp4"
    loop_source = os.getcwd() + "/arrow.mp4"

    App(tkinter.Tk(), video_source, video_source=video_source, loop_source=loop_source)