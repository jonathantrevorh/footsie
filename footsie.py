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
            values = {'right': int(float(parts[0])), 'left': int(float(parts[1]))}
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
            except AttributeError:
                pass
            except Exception as e:
                print e
                traceback.print_exc()

            self.container.after(25, updateUI)

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
        self.parent = parent
        label = tk.Label(self, text='', font=TITLE_FONT)
        label.pack(side='top', fill='x', pady=10)
        w = tk.Canvas(self, width=400, height=300)
        w.pack()
        self.w = w
        button = tk.Button(self, text='Go to the start page', command=lambda: controller.show_frame(StartPage))
        button.pack()
        self.apples = self.generateApples(3)
        self.player_position = 1
        self.trees = None

    def load(self, args):
        self.state = {'points': 0}
        self.drawScene()
        for apple in self.apples:
            self.drawApple(apple)
        self.last_left = 0
        self.last_right = 0

    def updateUI(self):
        # check if teh buttons are being pressed, and updat ethe player position if need be
        leftVal = getLeftValue()
        rightVal = getRightValue()
        if valueIsSufficient(leftVal) and leftVal > self.last_left:
            self.player_position -= 1
            if self.player_position < 0:
                self.player_position = 0
            print 'left'
        if valueIsSufficient(rightVal) and rightVal > self.last_right:
            self.player_position += 1
            if self.player_position > 2:
                self.player_position = 2
            print 'right'
        self.last_left = leftVal
        self.last_right = rightVal

        r = random.randint(0, 600)
        should_drop_an_apple = r == 0
        if should_drop_an_apple:
            which_apple = random.randint(0, len(self.apples) - 1)
            apple = self.apples[which_apple]
            apple['falling'] = True
            self.apples.append(self.generateApple())

        for apple in self.apples:
            if apple['falling']:
                apple['y'] += 0.2
                try:
                    for bit in apple['drawing']:
                        print bit
                        self.w.move(bit, 0, 0.2)
                except Exception as e:
                    print e

            if apple['y'] > 200:
                self.apples.remove(apple)
                if apple['x'] == 100+100*self.player_position:
                    self.state['points'] += 1
                try:
                    for bit in apple['drawing']:
                        bit.destroy()
                except KeyError:
                    pass


        if self.state['points'] > 5:
            controller.show_frame(CongratsPage, {'points': self.state['points']})

        self.drawPlayer()
        self.drawHUD()

    def drawScene(self):
        # clear the background
        self.drawBackground()
        if not self.trees:
            self.trees = [self.drawTree(100, 40), self.drawTree(200, 40), self.drawTree(300, 40)]

    def drawBackground(self):
        return self.w.create_rectangle(0, 0, self.w.winfo_width(), self.w.winfo_height(), fill='blue')

    def drawTree(self, x, y):
        bloom_height = 60
        bloom_width = 60
        trunk = self.rect(x, y+100, 50, 200)
        blooms = [
            self.oval(x-40, y, bloom_width, bloom_height),
            self.oval(x, y-15, bloom_width, bloom_height),
            self.oval(x+30, y-10, bloom_width, bloom_height),
            self.oval(x+20, y+20, bloom_width, bloom_height),
            self.oval(x-20, y+25, bloom_width, bloom_height)
        ]
        return {
            'bloom': blooms,
            'trunk': trunk
        }

    def rect(self, x, y, width, height, fill='brown'):
        return self.w.create_rectangle(x-width/2, y-height/2, x+width/2, y+height/2, fill=fill)

    def oval(self, x, y, width, height, fill='green'):
        return self.w.create_oval(x-width/2, y-height/2, x+width/2, y+height/2, fill=fill)

    def drawApple(self, apple):
        apple_size = 20
        stem = self.rect(apple['x'], apple['y'] + apple_size / 2, apple_size / 5, apple_size * 3 / 4, fill='black')
        oneHalf = self.oval(apple['x'] - apple_size / 5, apple['y'] * 4 / 3, apple_size, apple_size, fill='red')
        twoHalf = self.oval(apple['x'] + apple_size / 5, apple['y'] * 4 / 3, apple_size, apple_size, fill='red')
        drawnBits = [oneHalf, twoHalf, stem]
        apple['drawing'] = drawnBits

    def drawHUD(self):
        points = self.state['points']
        self.w.create_text(20, 20, text=points)

    def generateApple(self):
        apple = {
            'x': 100 + 100*random.randint(0, 2),
            'y': random.randint(20, 80),
            'falling': False
        }
        self.drawApple(apple)
        return apple

    def generateApples(self, n):
        return [self.generateApple() for i in range(0, n)]

    def drawPlayer(self):
        n = self.player_position
        arm_width = 4.0
        leg_width = 5.0
        x = 100 + 100*n
        y = 250
        parts = [self.w.create_line(x - 10, y - 5, x - 25, y + 5, fill="black", width=arm_width),
        self.w.create_line(x + 10, y - 5, x + 25, y + 5, fill="black", width=arm_width),
        self.rect(x, y + 10, 20, 30, fill="black"),
        self.w.create_line(x - 5, y + 25, x - 10, y + 45, fill="black", width=leg_width),
        self.w.create_line(x + 7, y + 25, x + 12, y + 45, fill="black", width=leg_width),
        self.oval(x, y - 10, 15, 15, fill="black")]
        self.play_parts = parts

    def unload(self):
        return

class CongratsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text='Wowzers!', font=TITLE_FONT)
        label.pack(side='top', fill='x', pady=10)
        self.tv = tk.StringVar()
        self.tv.set('')
        label = tk.Label(self, textvariable=self.tv)
        label.pack()
        button = tk.Button(self, text='Play again', command=lambda: controller.show_frame(PlayPage))
        button.pack()
        button1 = tk.Button(self, text='We gucci', command=lambda: controller.show_frame(StartPage))
        button1.pack()

    def load(self, args):
        self.points = args['points']
        self.tv.set(self.points)

    def unload(self):
        return


try:
    reader.start()
    app = Footsie()
    app.mainloop()
finally:
    stopper.set()
    reader.join()
