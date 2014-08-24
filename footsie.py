import serial
import Tkinter as tk
import threading
import traceback
import random

stopper = threading.Event()

def readData(arg1, port, rate, poop, stop_event):
    ser = serial.Serial(port, rate)
    while not stop_event.is_set():
        try:
            line = ser.readline()
            parts = line.split(',')
            if len(parts) < 2:
                continue
            values = {'left': int(float(parts[0])), 'right': int(float(parts[1]))}
            poop['data'] = values
        except ValueError:
            pass

def startbuttonClick():
    print 'click'

poop = {'listener': None, 'data': None}
def getLeftValue():
    return poop['data']['left']
def getRightValue():
    return poop['data']['right']
def valueIsSufficient(value):
    suffices = value > 575 # yay magic numbers!
    return suffices

reader = threading.Thread(target=readData, args=(1, '/dev/ttyACM0', 9600, poop, stopper))

TITLE_FONT = ('Helvetica', 18, 'bold')
class Footsie(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.container = container

        self.frame = None

        self.frames = {}
        for f in (StartPage, MeasurePage, PlayPage, CongratsPage):
            frame = f(container, self)
            self.frames[f] = frame
            frame.grid(row=0, column=0, sticky='nsew')
            frame.is_active = False

        self.show_frame(StartPage)

    def show_frame(self, c, params={}):
        if self.frame:
            self.frame.is_active = False
            try:
                self.frame.unload()
            except AttributeError:
                pass
        self.frame = self.frames[c]
        self.frame.tkraise()
        self.frame.is_active = True
        def updateUI():
            if not self.frame.is_active:
                print 'no is_active, so not updateUI'
                return
            try:
                self.frame.updateUI()
            except Exception as e:
                print e
                traceback.print_exc()

            self.container.after(5, updateUI)

        try:
            self.frame.load(params)
        except AttributeError:
            pass
        try:
            if self.frame.updateUI:
                updateUI()
        except AttributeError:
            pass

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text='Footsie', font=TITLE_FONT)
        label.pack(side='top', fill='x', pady=10)

        button1 = tk.Button(self, text='Start', command=lambda: controller.show_frame(MeasurePage))
        button1.pack()

    def unload(self):
        return


class MeasurePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        label = tk.Label(self, text='Try Outs', font=TITLE_FONT)
        label.pack(side='top', fill='x', pady=10)
        button = tk.Label(self, text='Test your footsie-bilities')
        button.bind('<Button-1>', lambda e: controller.show_frame(StartPage))
        button.pack()
        self.tv = tk.StringVar()
        self.tv.set('asdf')
        label = tk.Label(self, textvariable=self.tv)
        label.pack()
        self.continuebutton = tk.Button(self, text='Continue', command=lambda: controller.show_frame(PlayPage))
        self.continuebutton.pack_forget()

    def load(self, params):
        self.state = {'left': False, 'right': False}

    def updateUI(self):
        # update internal state
        leftVal = getLeftValue()
        rightVal = getRightValue()
        if valueIsSufficient(leftVal):
            self.achieveLeft()
        if valueIsSufficient(rightVal):
            self.achieveRight()

        print '{} {}'.format(leftVal, rightVal)
        # apply it to the ui
        message = ''
        if not self.hasLeft() and not self.hasRight():
            message = 'Press your left foot'
        elif self.hasLeft() and not self.hasRight():
            message = 'Now press your right foot'
        elif self.hasLeft() and self.hasRight():
            message = 'Superb! Let\'s play!'
            self.showContinueButton()
        self.tv.set(message)

    def hasLeft(self):
        return self.state['left']

    def hasRight(self):
        return self.state['right']

    def achieveLeft(self):
        self.state['left'] = True

    def achieveRight(self):
        self.state['right'] = True

    def unload(self):
        self.state = {}

    def showContinueButton(self):
        self.continuebutton.pack()

class PlayPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text='', font=TITLE_FONT)
        label.pack(side='top', fill='x', pady=10)
        w = tk.Canvas(self, width=400, height=300)
        w.pack()
        self.w = w
        button = tk.Button(self, text='Go to the start page', command=lambda: controller.show_frame(StartPage))
        button.pack()
        self.apples = self.generateApples(3)
        self.drawScene()
        self.drawPlayer(1)

    def updateUI(self):
        return

    def drawScene(self):
        # clear the background
        self.drawBackground()
        self.drawTree(100, 40)
        self.drawTree(200, 40)
        self.drawTree(300, 40)
        for apple in self.apples:
            self.drawApple(apple);

    def drawBackground(self):
        self.w.create_rectangle(0, 0, self.w.winfo_width(), self.w.winfo_height(), fill='blue')

    def drawTree(self, x, y):
        bloom_height = 60
        bloom_width = 60
        self.rect(x, y+100, 50, 200)
        self.oval(x-40, y, bloom_width, bloom_height)
        self.oval(x, y-15, bloom_width, bloom_height)
        self.oval(x+30, y-10, bloom_width, bloom_height)
        self.oval(x+20, y+20, bloom_width, bloom_height)
        self.oval(x-20, y+25, bloom_width, bloom_height)

    def rect(self, x, y, width, height, fill='brown'):
        self.w.create_rectangle(x-width/2, y-height/2, x+width/2, y+height/2, fill=fill)

    def oval(self, x, y, width, height, fill='green'):
        self.w.create_oval(x-width/2, y-height/2, x+width/2, y+height/2, fill=fill)

    def drawApple(self, apple):
        apple_size = 20
        self.rect(apple['x'], apple['y'] + apple_size / 2, apple_size / 5, apple_size * 3 / 4, fill='black')
        self.oval(apple['x'] - apple_size / 5, apple['y'] * 4 / 3, apple_size, apple_size, fill='red')
        self.oval(apple['x'] + apple_size / 5, apple['y'] * 4 / 3, apple_size, apple_size, fill='red')
        return

    def generateApple(self):
        return {
            'x': 100 + 100*random.randint(0, 2),
            'y': random.randint(20, 80)
        }

    def generateApples(self, n):
        return [self.generateApple() for i in range(0, n)]

    def drawPlayer(self, n):
        # use some polygons
        return

    def unload(self):
        return

class CongratsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text='Wowzers!', font=TITLE_FONT)
        label.pack(side='top', fill='x', pady=10)
        button = tk.Button(self, text='Play again', command=lambda: controller.show_frame(PlayPage))
        button.pack()
        button1 = tk.Button(self, text='We gucci', command=lambda: controller.show_frame(StartPage))
        button1.pack()

    def unload(self):
        return


try:
    reader.start()
    app = Footsie()
    app.mainloop()
finally:
    stopper.set()
    reader.join()
