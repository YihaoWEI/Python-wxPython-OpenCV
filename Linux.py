# coding:utf-8
from PIL import Image   

# Use the wxPython backend of matplotlib
import matplotlib       
matplotlib.use('WXAgg')

# Matplotlib elements used to draw the bounding rectangle
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.patches import Rectangle
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Wxpython
import wx
import os

# OpenCV
import cv2
import numpy as np

# Thread
import threading

# Time
import time

import sys
reload(sys)
sys.setdefaultencoding('utf-8')



class MyDialog(wx.Panel):
    def __init__(self, parent, pathToImage=None):
        
        # Use English dialog
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        
        # Initialise the parent
        wx.Panel.__init__(self, parent)

        # Intitialise the matplotlib figure
        #self.figure = plt.figure(facecolor='gray',figsize=(10.5, 8))
        self.figure = Figure(facecolor='gray',figsize=(10.5, 8))

        # Create an axes, turn off the labels and add them to the figure
        self.axes = plt.Axes(self.figure,[0,0,1,1])    
         
 
        self.axes.set_axis_off() 
        self.figure.add_axes(self.axes)
        
        self.panel=wx.Panel(self,-1,pos=(10,10),size=(1390,940))
        
        # Add the figure to the wxFigureCanvas
        self.canvas = FigureCanvas(self.panel, -1, self.figure)
          

        # Height,width
        #self.picSize=wx.TextCtrl(self,-1,"",pos=(1100,800),size=(100,30),style=wx.TE_READONLY)


      
        # Check box
        self.check=wx.CheckBox(self.panel,-1,u"批量处理全部图片",pos=(1080,50),size=(100,20))
        self.check.Bind(wx.EVT_CHECKBOX,self.onCheck)
     

        # StaticText
        wx.StaticText(self.panel,-1,u"图像文件所在目录：",pos=(1080,90))

        # Show dialog path
        self.pathText=wx.TextCtrl(self.panel,-1,"",pos=(1080,130),size=(190,30))

        # Add Button 
        self.openBtn=wx.Button(self.panel,-1,u">>",pos=(1280,130),size=(90,30))
        self.frontBtn=wx.Button(self.panel,-1,u"上一张",pos=(1080,830),size=(90,50))
        self.saveBtn=wx.Button(self.panel,-1,u"保存本帧结果",pos=(1190,830),size=(100,50))
        self.nextBtn=wx.Button(self.panel,-1,u"下一张",pos=(1300,830),size=(90,50))
        self.workBtn=wx.Button(self.panel,-1,u"开始处理/暂停处理",pos=(1080,760),size=(290,40))
        # Progress Bar
        self.gauge=wx.Gauge(self.panel,-1,1000,(10,830),(1050,50))
        #self.gauge.SetValue(2)
     
        # StaticText
        wx.StaticText(self.panel,-1,u"耗时：",pos=(1080,723))
        # Show time
        self.timeText=wx.TextCtrl(self.panel,-1,"",pos=(1140,720),size=(230,30),style=wx.TE_READONLY)
        
    

        # Attach button with function
        self.Bind(wx.EVT_BUTTON,self.load,self.openBtn)
        self.Bind(wx.EVT_BUTTON,self.save,self.saveBtn)
        self.Bind(wx.EVT_BUTTON,self.front,self.frontBtn)
        self.Bind(wx.EVT_BUTTON,self.next,self.nextBtn)
        self.Bind(wx.EVT_BUTTON,self.work,self.workBtn)



        self.area_text = wx.TextCtrl(self, -1, u'小轿车',pos=(1080,175),size=(290,535),style=(wx.TE_MULTILINE))
        self.area_text.AppendText('\n大货车')
        self.area_text.AppendText('\n大货车')
        self.area_text.AppendText('\n大货车')
        self.area_text.AppendText('\n大货车')
        self.area_text.AppendText('\n大货车')
        self.area_text.AppendText('\n大货车')
        self.area_text.AppendText('\n大货车')
        self.area_text.AppendText('\n矩形:(1,10,10,10)')
        self.area_text.AppendText('\n矩形:(1,10,10,10)')
        self.area_text.AppendText('\n矩形:(1,10,10,10)')
        self.area_text.AppendText('\n矩形:(1,10,10,10)')
        self.area_text.AppendText('\n矩形:(1,10,10,10)')
      

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
                self.gauge.SetValue((self.count+1.0)/len(self.fileList)*1000.0)
                self.pathText.Clear()
                self.pathText.AppendText(dlg.GetPath())
            else:
                print "List Null"
        dlg.Destroy()


    # Save Picture button function
    def save(self,event):
        if self.cut_img is None:
            print "Please Draw Area"
            return
        else:
            cv2.imwrite(self.picNameList[self.count]+'_rect.jpg',self.cut_img)
            print "Save Successful"
            


    # The front picture button function
    def front(self,event):
        self.count-=1
        self.cut_img=None
        if self.fileList:
            if self.count<0:
                self.count+=1
                print "Null Pic"
            else:
                self.setImage(self.fileList[self.count])
                self.gauge.SetValue((self.count+1.0)/len(self.fileList)*1000.0)
                print self.count,self.fileList[self.count]
            
        else:
            print "Please Choose File" 
            return 
        
       
    # The next picture button function        
    def next(self,event):
        self.count+=1
        self.cut_img=None
        if self.fileList:
            if self.count>(len(self.fileList) - 1):
                self.count-=1
                print "Null Pic"
            else:
                self.setImage(self.fileList[self.count])
                self.gauge.SetValue((self.count+1.0)/len(self.fileList)*1000.0)
                print self.count,self.fileList[self.count]

        else:
            print "Please Choose File"
            return 
      
    # The work button,start thread
    def work(self,event):
          t = MyThread(1,self)
          t.start()
          #t.join()
         

    # CheckBox
    def onCheck(self,event):
        #wx.MessageBox(str(self.check.GetValue()),"Check?",wx.YES_NO|wx.ICON_QUESTION)
        if self.check.GetValue():
            self.frontBtn.Enable(False)
            self.saveBtn.Enable(False)
            self.nextBtn.Enable(False)
        else:
            self.frontBtn.Enable(True)
            self.saveBtn.Enable(True)
            self.nextBtn.Enable(True)

         

        
    

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
                print "Draw Null Rectangle"
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
        
        # Load pic by OpenCV
        image=cv2.imread(pathToImage)
        '''
        # Load the image into matplotlib and PIL
        image = matplotlib.image.imread(pathToImage)
        imPIL = Image.open(pathToImage) 
        # Save the image's dimensions from PIL
        self.imageSize = imPIL.size
        '''
        
        self.imageSize = image.shape
        print pathToImage
        print "It's width and height:"
        print self.imageSize
        print "------------------------"

        # OpenCV add text on pic
        str1='(%s,%s)' % (str(self.imageSize[0]),str(self.imageSize[1]))
        #rev=wx.StaticText(self,-1,str1,(670,400))
        cv2.putText(image,str1,(10,200), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,0,0),2)
        
        # Add the image to the figure and redraw the canvas. Also ensure the aspect ratio of the image is retained.
        self.axes.imshow(image,aspect='auto')
        self.canvas.draw()


#inherit from threading.Thread function
class MyThread(threading.Thread):
    def __init__(self, num,frame ): 
        threading.Thread.__init__(self)
        self.num = num
        self.frame=frame
     
    # Thread function
    def run(self):
        for i in range(self.num):
            for index in self.frame.fileList:
                print 'I am %s.num:%s，%s' % (self.getName(), i,index)
                self.frame.gauge.SetValue((self.frame.count+1.0)/len(self.frame.fileList)*1000.0)
                self.frame.count+=1
                time.sleep(2)
    def pause(self):
        self._flag#.clear()

       

if __name__ == "__main__":

    # Create an demo application
    app = wx.App()
    # Create a frame and a RectangleSelectorPanel
    frame = wx.Frame(None, -1,"Show Demo",size=(1400,950))
    panel = MyDialog(frame)

    # Start the demo app
    frame.Show()
    app.MainLoop()
