from PIL import Image   

# Use the wxPython backend of matplotlib
import matplotlib       
matplotlib.use('WXAgg')

# Matplotlib elements used to draw the bounding rectangle
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# Wxpython
import wx
import os

# OpenCV
import cv2
import numpy as np


class MyDialog(wx.Panel):
    def __init__(self, parent, pathToImage=None):
        
        # Use English dialog
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        
        # Initialise the parent
        wx.Panel.__init__(self, parent)

        # Intitialise the matplotlib figure
        #self.figure = plt.figure(facecolor='gray')
        self.figure = Figure(facecolor='gray')

        # Create an axes, turn off the labels and add them to the figure
        self.axes = plt.Axes(self.figure,[0,0,1,1])      
        self.axes.set_axis_off() 
        self.figure.add_axes(self.axes)
        

        
        # Add the figure to the wxFigureCanvas
        self.canvas = FigureCanvas(self, -1, self.figure)
        


        # Add Button and Progress Bar
        self.openBtn=wx.Button(self,-1,"Open",pos=(680,50),size=(70,40))
        self.saveBtn=wx.Button(self,-1,"Save",pos=(680,150),size=(70,40))
        self.frontBtn=wx.Button(self,-1,"Front",pos=(680,200),size=(70,40))
        self.nextBtn=wx.Button(self,-1,"Next",pos=(790,200),size=(70,40))
        self.gauge=wx.Gauge(self,-1,100,(00,520),(640,50))


        


        # Attach button with function
        self.Bind(wx.EVT_BUTTON,self.load,self.openBtn)
        self.Bind(wx.EVT_BUTTON,self.save,self.saveBtn)
        self.Bind(wx.EVT_BUTTON,self.front,self.frontBtn)
        self.Bind(wx.EVT_BUTTON,self.next,self.nextBtn)


        # Show dialog path
        self.pathText=wx.TextCtrl(self,-1,"",pos=(680,100),size=(175,30),)

        # Check box
        self.check=wx.CheckBox(self,-1,"Check",pos=(790,50),size=(70,20))
        self.check.Bind(wx.EVT_CHECKBOX,self.onCheck)


        self.area_text = wx.TextCtrl(self, -1, u'记录',pos=(680,255),size=(200,200),style=(wx.TE_MULTILINE))
        self.area_text.AppendText('\n记录')
        self.area_text.AppendText('\n记录')
        self.area_text.AppendText('\n记录')
        self.area_text.AppendText('\n记录')
        self.area_text.AppendText('\n记录')
        self.area_text.AppendText('\n记录车')
        self.area_text.AppendText('\n记录')
        self.area_text.AppendText('\n矩形:(1,10,10,10)')
        self.area_text.AppendText('\n矩形:(1,10,10,10)')
        self.area_text.AppendText('\n矩形:(1,10,10,10)')
        self.area_text.AppendText('\n矩形:(1,10,10,10)')
        self.area_text.AppendText('\n矩形:(1,10,10,10)')
        #self.area_text.SetInsertionPoint(0) 

        # Initialise the rectangle
        self.rect = Rectangle((0,0), 0, 0, facecolor='None', edgecolor='red')
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.axes.add_patch(self.rect)


        # The list of the picture(absolute path)
        self.fileList=[]

        # Picture name
        self.picNameList=[]

        # Picture index in list
        self.count=0 
    
        # Cut from the picture of the rectangle
        self.cut_img=None

        
        # Connect the mouse events to their relevant callbacks
        self.canvas.mpl_connect('button_press_event', self._onPress)
        self.canvas.mpl_connect('button_release_event', self._onRelease)
        self.canvas.mpl_connect('motion_notify_event', self._onMotion)
        
        
        # Lock to stop the motion event from behaving badly when the mouse isn't pressed
        self.pressed = False

        # If there is an initial image, display it on the figure
        if pathToImage is not None:
            self.setImage(pathToImage)



        
        
    # GetFilesPath with the end with .jpg or .png
    def getFilesPath(self,path):
        filesname=[]
        dirs = os.listdir(path)
        for i in dirs:
            if os.path.splitext(i)[1] == ".jpg" or os.path.splitext(i)[1] == ".png":
                filesname+=[path+"/"+i]
                self.picNameList+=[i[:-4]]
        return filesname


    # Load Picture button function
    def load(self,event):
        dlg = wx.DirDialog(self,"Choose File",style=wx.DD_DEFAULT_STYLE)  
        if dlg.ShowModal() == wx.ID_OK:
            self.count=0           
            self.fileList=self.getFilesPath(dlg.GetPath())
            if self.fileList:
                self.setImage(self.fileList[0])
                self.gauge.SetValue((self.count+1)/len(self.fileList)*100)
                self.pathText.Clear()
                self.pathText.AppendText(dlg.GetPath())
            else:
                print("List Null")
        dlg.Destroy()


    # Save Picture button function
    def save(self,event):
        if self.cut_img is None:
            print("Please Draw Area")
            return
        else:
            cv2.imwrite(self.picNameList[self.count]+'_rect.jpg',self.cut_img)
            print("Save Successful")
            


    # The front picture button function
    def front(self,event):
        self.count-=1
        self.cut_img=None
        if self.fileList:
            if self.count<0:
                self.count+=1
                print("Null Pic")
            else:
                self.setImage(self.fileList[self.count])
                self.gauge.SetValue((self.count+1)/len(self.fileList)*100)
                #print(self.count,self.fileList[self.count])
            
        else:
            print("Please Choose File")
            return 
        
       
    # The next picture button function        
    def next(self,event):
        self.count+=1
        self.cut_img=None
        if self.fileList:
            if self.count>(len(self.fileList) - 1):
                self.count-=1
                print("Null Pic")
            else:
                self.setImage(self.fileList[self.count])
                self.gauge.SetValue((self.count+1)/len(self.fileList)*100)
                #print(self.count,self.fileList[self.count])

        else:
            print("Please Choose File")
            return 
        

    # CheckBox
    def onCheck(self,event):
        wx.MessageBox(str(self.check.GetValue()),"Check?",wx.YES_NO|wx.ICON_QUESTION)

        
    

    def _onPress(self, event):
        ''' Callback to handle the mouse being clicked and held over the canvas'''
        # Check the mouse press was actually on the canvas
        if event.xdata is not None and event.ydata is not None:

            # Upon initial press of the mouse record the origin and record the mouse as pressed
            self.pressed = True
            self.rect.set_linestyle('dashed')
            self.x0 = event.xdata
            self.y0 = event.ydata


    def _onRelease(self, event):
        '''Callback to handle the mouse being released over the canvas'''
        # Check that the mouse was actually pressed on the canvas to begin with and this isn't a rouge mouse 
        # release event that started somewhere else
        if self.pressed:

            # Upon release draw the rectangle as a solid rectangle
            self.pressed = False
            self.rect.set_linestyle('solid')

            # Check the mouse was released on the canvas, and if it wasn't then just leave the width and 
            # height as the last values set by the motion event
            if event.xdata is not None and event.ydata is not None:
                self.x1 = event.xdata
                self.y1 = event.ydata

            # Set the width and height and origin of the bounding rectangle
            self.boundingRectWidth =  self.x1 - self.x0
            self.boundingRectHeight =  self.y1 - self.y0
            self.bouningRectOrigin = (self.x0, self.y0)

            # Draw the bounding rectangle
            self.rect.set_width(self.boundingRectWidth)
            self.rect.set_height(self.boundingRectHeight)
            self.rect.set_xy((self.x0, self.y0))
            self.canvas.draw()

            
            # OpenCV cut picture(all number shoudle be integer)
            x=int(self.x0)
            y=int(self.y0)
            width=int(self.boundingRectWidth)
            height=int(self.boundingRectHeight)
            if  self.fileList and width:
                org = cv2.imread(self.fileList[self.count])
                self.cut_img = org[y:y+height, x:x+width]
                cv2.imshow('cut_image', self.cut_img)
            else:
                print("Draw Null Rectangle")
                return
            
            
            

    def _onMotion(self, event):
        '''Callback to handle the motion event created by the mouse moving over the canvas'''
        # If the mouse has been pressed draw an updated rectangle when the mouse is moved so 
        # the user can see what the current selection is
        if self.pressed:
            # Check the mouse was released on the canvas, and if it wasn't then just leave the width and 
            # height as the last values set by the motion event
            if event.xdata is not None and event.ydata is not None:
                self.x1 = event.xdata
                self.y1 = event.ydata
            
            # Set the width and height and draw the rectangle
            self.rect.set_width(self.x1 - self.x0)
            self.rect.set_height(self.y1 - self.y0)
            self.rect.set_xy((self.x0, self.y0))
            self.canvas.draw()

        # Show Picture
    def setImage(self, pathToImage):
        '''Sets the background image of the canvas'''
        # Clear the rectangle in front picture
        self.axes.text(100,100,'',None)
        self.rect.set_width(0)
        self.rect.set_height(0)
        self.rect.set_xy((0, 0))
        self.canvas.draw()
        #plt.cla()
        #self.initCanvas()
      
        

        
        # Load pic by OpenCV
        #image=cv2.imread(pathToImage,1)
        
        # Load the image into matplotlib and PIL
        image = matplotlib.image.imread(pathToImage)
        
        imPIL = Image.open(pathToImage) 

        # Save the image's dimensions from PIL
        self.imageSize = imPIL.size

        '''
        self.imageSize = image.shape
        print(pathToImage)
        print("It's width and height:")
        print(self.imageSize)
        
        print("------------------------")

        # OpenCV add text on pic
        str1='(%s,%s)' % (str(self.imageSize[0]),str(self.imageSize[1]))
        rev=wx.StaticText(self,-1,str1,(670,400))
        #rev.SetForegroundColour('white')
        #rev.SetBackgroundColour('black')
        #rev.SetFont(wx.Font(15,wx.DECORATIVE,wx.ITALIC,wx.NORMAL))
        cv2.putText(image,str1,(10,200), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,0,0),2)
        '''

        str1='%s,%s' % (str(self.imageSize[0]),str(self.imageSize[1]))
        rev=wx.StaticText(self,-1,str1,(680,550))
        
        # Add the image to the figure and redraw the canvas. Also ensure the aspect ratio of the image is retained.
        self.axes.imshow(image,aspect='equal')
  
        self.canvas.draw()


       

if __name__ == "__main__":

    # Create an demo application
    app = wx.App()
    # Create a frame and a RectangleSelectorPanel
    frame = wx.Frame(None, -1,"Show",size=(900,650))
    panel = MyDialog(frame)
    

    # Start the demo app
    frame.Show()
    app.MainLoop()
    app.OnExit()
