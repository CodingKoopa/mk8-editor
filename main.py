
"""
Copyright (C) 2015 Yannik Marchand
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY Yannik Marchand ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL Yannik Marchand BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation 
are those of the authors and should not be interpreted as representing
official policies, either expressed or implied, of Yannik Marchand.
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt4 import QtGui, QtCore
from PyQt4.QtOpenGL import *
import os, sys

import byml, fmdl, sarc, yaz0

import datetime
now = datetime.datetime.now

color = 1

class CheckBox(QtGui.QCheckBox):
    def __init__(self,node):
        QtGui.QCheckBox.__init__(self)
        self.stateChanged.connect(self.changed)
        self.node = node

    def changed(self,state):
        self.node.changeValue(state==QtCore.Qt.Checked)

class LineEdit(QtGui.QLineEdit):
    def __init__(self,value,callback):
        QtGui.QLineEdit.__init__(self,str(value))
        self.callback = callback
        self.textChanged[str].connect(self.changed)

    def changed(self,text):
        if text:
            self.callback(self)

def FloatEdit(v,cb):
    edit = LineEdit(v,cb)
    edit.setValidator(QtGui.QDoubleValidator())
    return edit

def IntEdit(v,cb):
    edit = LineEdit(v,cb)
    edit.setValidator(QtGui.QIntValidator())
    return edit

# renames the settings names, not ported to mk8 yet
def SettingName(oldName):
    if oldName == 'Multi2P':
        return '2-Player Related'
    if oldName == 'Multi4P':
        return '4-Player Related'    
    if oldName == 'WiFi':
        return 'WiFi Related'
    if oldName == 'WiFi2P':
        return '2-Player WiFi Related'    
    if oldName == 'ObjId':
        return 'Object ID'
    if oldName == 'UnitIdNum':
        return 'Unit Number'
    if oldName == 'TopView':
        return 'Camera Related??'        
    return oldName

class SettingsWidget(QtGui.QWidget):
    def __init__(self,parent):
        QtGui.QWidget.__init__(self,parent)
        layout = QtGui.QVBoxLayout(self)
        scroll = QtGui.QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        scrollContents = QtGui.QWidget()
        self.layout = QtGui.QVBoxLayout(scrollContents)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        scroll.setWidget(scrollContents)

    def reset(self):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

    def showSettings(self,obj):
        # this was slapped together, is getting ObjID from objflow.byaml and displaying that as the config_lbl
        modelNameMapping = {}
        with open(window.gamePath+'/data/objflow.byaml', 'rb') as f:
            b = byml.BYML(f.read(), True)
            for thing in b.rootNode.subNodes():
                resName = thing.subNodes()['ResName'].subNodes()[0].val
                id = thing['ObjId']
                modelNameMapping[id] = resName
        
        self.current = obj

        self.config_lbl = QtGui.QLabel(obj.fileName) # int to a string
        self.config_lbl.setStyleSheet('font-size: 16px')
        self.layout.addWidget(self.config_lbl)

        self.config_lbl = QtGui.QLabel(str(obj.data['ObjId'])) # int to a string
        self.config_lbl.setStyleSheet('font-size: 16px')
        self.layout.addWidget(self.config_lbl)

        lbl = QtGui.QLabel('Translate:')
        lbl.setStyleSheet('font-size: 14px')
        self.layout.addWidget(lbl)
        self.transx = FloatEdit(obj.posx,self.changed)
        self.transy = FloatEdit(obj.posy,self.changed)
        self.transz = FloatEdit(obj.posz,self.changed)
        self.layout.addWidget(self.transx)
        self.layout.addWidget(self.transy)
        self.layout.addWidget(self.transz)

        lbl = QtGui.QLabel('Rotate:')
        lbl.setStyleSheet('font-size: 14px')
        self.layout.addWidget(lbl)
        self.rotx = FloatEdit(obj.rotx,self.changed)
        self.roty = FloatEdit(obj.roty,self.changed)
        self.rotz = FloatEdit(obj.rotz,self.changed)
        self.layout.addWidget(self.rotx)
        self.layout.addWidget(self.roty)
        self.layout.addWidget(self.rotz)

        lbl = QtGui.QLabel('Scale:')
        lbl.setStyleSheet('font-size: 14px')
        self.layout.addWidget(lbl)
        self.sclx = FloatEdit(obj.sclx,self.changed)
        self.scly = FloatEdit(obj.scly,self.changed)
        self.sclz = FloatEdit(obj.sclz,self.changed)
        self.layout.addWidget(self.sclx)
        self.layout.addWidget(self.scly)
        self.layout.addWidget(self.sclz)

        for key in obj.data.dict:
            vnode = obj.data.getSubNode(key)
            if not key in ['Scale','Translate','Rotate']:
                lbl = QtGui.QLabel(SettingName(key)+':')
                if isinstance(vnode,byml.FloatNode):
                    box = FloatEdit(obj.data[key],self.changed2)
                    box.node = vnode
                elif isinstance(vnode,byml.IntegerNode):
                    box = IntEdit(obj.data[key],self.changed2)
                    box.node = vnode
                elif isinstance(vnode,byml.BooleanNode):
                    box = CheckBox(vnode)
                    if obj.data[key]:
                        box.toggle()
                elif isinstance(vnode,byml.StringNode):
                    box = LineEdit(str(obj.data[key]),self.changed2)
                    box.node = vnode
                    box.setEnabled(False)
                else:
                    box = QtGui.QLineEdit(str(obj.data[key]))
                    box.setEnabled(False)
                self.layout.addWidget(lbl)
                self.layout.addWidget(box)
                
            elif key == 'ObjId':
                lbl = QtGui.QLabel(key+':')
                #box = LineEdit(str(obj.data['UnitConfigName']),self.configNameChanged)
                #box.node = vnode
                box = QtGui.QLineEdit(str(obj.data[key]))
                box.setEnabled(False)
                self.layout.addWidget(lbl)
                self.layout.addWidget(box)
                
            elif key == 'UnitIdNum':
                lbl = QtGui.QLabel(key+':')
                if isinstance(vnode,byml.StringNode):
                    box = LineEdit(str(obj.data['UnitIdNum']),self.modelNameChanged)
                    box.node = vnode
                else:
                    box = QtGui.QLineEdit(str(obj.data['UnitIdNum']))
                    box.setEnabled(False)
                self.layout.addWidget(lbl)
                self.layout.addWidget(box)

    def changed(self,box):
        if self.transx.text() and self.transy.text() and self.transz.text() and self.rotx.text() and self.roty.text() and self.rotz.text() and self.sclx.text() and self.scly.text() and self.sclz.text():
            self.current.posx = float(self.transx.text())
            self.current.posy = float(self.transy.text())
            self.current.posz = float(self.transz.text())
            self.current.rotx = float(self.rotx.text())
            self.current.roty = float(self.roty.text())
            self.current.rotz = float(self.rotz.text())
            self.current.sclx = float(self.sclx.text())
            self.current.scly = float(self.scly.text())
            self.current.sclz = float(self.sclz.text())
            self.current.saveValues()
            window.glWidget.updateGL()

    def changed2(self,box):
        if box.text():
            box.node.changeValue(box.text())

    #def configNameChanged(self,box):
    #    if box.text():
    #        box.node.changeValue(box.text())
    #        self.config_lbl.setText(box.text())
    #        self.current.updateModel()

    def modelNameChanged(self,box):
        if box.text():
            box.node.changeValue(box.text())
            self.current.updateModel()

class LevelObject:
    def __init__(self,obj,dlist,modelName):
        global color
        self.data = obj
        self.color = (color/100/10.0,((color/10)%10)/10.0,(color%10)/10.0)
        color+=1
        self.list = dlist

        self.fileName = modelName
        
        trans = obj['Translate']
        self.posx = trans['X']/100
        self.posy = trans['Y']/100
        self.posz = trans['Z']/100

        rot = obj['Rotate']
        self.rotx = rot['X']
        self.roty = rot['Y']
        self.rotz = rot['Z']

        scale = obj['Scale']
        self.sclx = scale['X']
        self.scly = scale['Y']
        self.sclz = scale['Z']

    def saveValues(self):
        obj = self.data
        trans = obj['Translate']
        if self.posx != trans['X']/100: trans.getSubNode('X').changeValue(self.posx*100)
        if self.posy != trans['Y']/100: trans.getSubNode('Y').changeValue(self.posy*100)
        if self.posz != trans['Z']/100: trans.getSubNode('Z').changeValue(self.posz*100)
            
        rot = obj['Rotate']
        if self.rotx != rot['X']: rot.getSubNode('X').changeValue(self.rotx)
        if self.roty != rot['Y']: rot.getSubNode('Y').changeValue(self.roty)
        if self.rotz != rot['Z']: rot.getSubNode('Z').changeValue(self.rotz)

        scale = obj['Scale']
        if self.sclx != scale['X']: scale.getSubNode('X').changeValue(self.sclx)
        if self.scly != scale['Y']: scale.getSubNode('Y').changeValue(self.scly)
        if self.sclz != scale['Z']: scale.getSubNode('Z').changeValue(self.sclz)

    def draw(self,pick):
        if pick:
            glColor3f(*self.color)
        glPushMatrix()
        glTranslatef(self.posx,self.posy,self.posz)
        glRotatef(self.rotx,1.0,0.0,0.0)
        glRotatef(self.roty,0.0,1.0,0.0)
        glRotatef(self.rotz,0.0,0.0,1.0)
        #glScalef(self.sclx,self.scly,self.sclz)
        glCallList(self.list)
        glPopMatrix()
    # this won't even work right now
    def updateModel(self):
        model = self.data['UnitIdNum']
        if not self.data['UnitIdNum']:
            model = self.data['ObjId']
        if not model in window.glWidget.cache:
            window.glWidget.cache[model] = window.glWidget.loadModel(model)
            #window.glWidget.cache[model] = window.glWidget.loadcourseModel(model)
        self.list = window.glWidget.cache[model]
        window.glWidget.updateGL()

class LevelWidget(QGLWidget):

    objects = []
    cache = {}
    rotx = roty = rotz = 0
    posx = posy = 0
    posz = -300
    picked = None
    
    def __init__(self,parent):
        QGLWidget.__init__(self,parent)

    def reset(self):
        self.objects = []
        self.rotx = self.roty = self.rotz = 0
        self.posx = self.posy =  0
        self.posz = -300

    def pickObjects(self,x,y):
        self.paintGL(1)
        array = (GLuint * 1)(0)
        pixel = glReadPixels(x,self.height()-y,1,1,GL_RGB,GL_UNSIGNED_BYTE,array)
        r,g,b = [round(((array[0]>>(i*8))&0xFF)/255.0,1) for i in range(3)]
        self.picked = None
        window.settings.reset()
        for obj in self.objects:
            if obj.color == (r,g,b):
                self.picked = obj
                break
        if self.picked:
            window.settings.showSettings(self.picked)
        self.updateGL()

    def paintGL(self,pick=0):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(self.posx,self.posy,self.posz)
        glRotatef(self.rotx,1.0,0.0,0.0)
        glRotatef(self.roty,0.0,1.0,0.0)
        glRotatef(self.rotz,0.0,0.0,1.0)
        for obj in self.objects:
            if obj == self.picked:
                glColor3f(1.0,0.0,0.0)
            else:
                glColor3f(1.0,1.0,1.0)
            obj.draw(pick)  

    def resizeGL(self,w,h):
        if h == 0:
            h = 1
            
        glViewport(0,0,w,h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0,float(w)/float(h),0.1,750.0)
        glMatrixMode(GL_MODELVIEW)

    def initializeGL(self):
        glClearColor(0.3,0.3,1.0,0.0)
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_DEPTH_TEST)
        self.generateCubeList()

    def addObject(self,obj,modelName):
        if not modelName in self.cache:
            self.cache[modelName] = self.loadModel(modelName)
            #self.cache[modelName] = self.loadcourseModel(modelName)
        lobj = LevelObject(obj,self.cache[modelName],modelName)
        self.objects.append(lobj)

        # trying to duplicate the function

    # models are loaded through the model name from /mapobj/objectname/objectname.bfres
    def loadModel(self,name):
        if not os.path.isfile(window.gamePath+'/mapobj/{0}/{0}.bfres'.format(name)):
            return self.cubeList
        
        with open(window.gamePath+'/mapobj/{0}/{0}.bfres'.format(name),'rb') as f:
            data = f.read()
        #with open(window.gamePath+'/race_common/{0}/{0}.bfres'.format(name),'rb') as f:
        #    data2 = f.read()            

        model = fmdl.parse(data)
        #model2 = fmdl.parse(data2)
        return self.generateList(model)
        #return self.generateList(model2)
        #return self.cubeList

    #def loadcourseModel(self,name):
    #    #this sucks and should be removed
    #    with open(window.gamePath+'/course/G64_RainbowRoad/course_model.szs','rb') as f:
    #        data = f.read()
    #        bfres = yaz0.decompress(data)
    #        model = fmdl.parse(bfres)
    #        return self.generateList(model)
        #return self.cubeList    
    
    def generateList(self,model):
        displayList = glGenLists(1)
        glNewList(displayList,GL_COMPILE)

        for polygon in model.shapes:

            rotation = polygon.rotation
            triangles = polygon.indices
            vertices = polygon.vertices
            
            glPushMatrix()
            glRotatef(rotation[0],1.0,0.0,0.0)
            glRotatef(rotation[1],0.0,1.0,0.0)
            glRotatef(rotation[2],0.0,0.0,1.0)

            glBegin(GL_TRIANGLES)
            for vertex in triangles:
                glVertex3f(*[vertices[vertex][i]/100 for i in range(3)])
            glEnd()

            glPushAttrib(GL_CURRENT_BIT)
            glColor3f(0.0,0.0,0.0)
            for triangle in [triangles[i*3:i*3+3] for i in range(len(triangles)/3)]:
                glBegin(GL_LINES)
                for vertex in triangle:
                    glVertex3f(*[vertices[vertex][i]/100 for i in range(3)])
                glEnd()
            glPopAttrib()

            glPopMatrix()
        
        glEndList()
        return displayList
    
    def generateCubeList(self):
        displayList = glGenLists(1)
        glNewList(displayList,GL_COMPILE)

        glBegin(GL_QUADS)
        self.drawCube()
        glEnd()

        glBegin(GL_LINES)
        glColor3f(0.0,0.0,0.0)
        self.drawCube()
        glEnd()

        glEndList()

        self.cubeList = displayList

    def drawCube(self):
        glVertex3f( 0.2, 0.2,-0.2)
        glVertex3f(-0.2, 0.2,-0.2)
        glVertex3f(-0.2, 0.2, 0.2)
        glVertex3f( 0.2, 0.2, 0.2)

        glVertex3f( 0.2,-0.2, 0.2)
        glVertex3f(-0.2,-0.2, 0.2)
        glVertex3f(-0.2,-0.2,-0.2)
        glVertex3f( 0.2,-0.2,-0.2)
        
        glVertex3f( 0.2, 0.2, 0.2)
        glVertex3f(-0.2, 0.2, 0.2)
        glVertex3f(-0.2,-0.2, 0.2)
        glVertex3f( 0.2,-0.2, 0.2)

        glVertex3f( 0.2,-0.2,-0.2)
        glVertex3f(-0.2,-0.2,-0.2)
        glVertex3f(-0.2, 0.2,-0.2)
        glVertex3f( 0.2, 0.2,-0.2)
        
        glVertex3f(-0.2, 0.2, 0.2)
        glVertex3f(-0.2, 0.2,-0.2)
        glVertex3f(-0.2,-0.2,-0.2)
        glVertex3f(-0.2,-0.2, 0.2)
        
        glVertex3f( 0.2, 0.2,-0.2)
        glVertex3f( 0.2, 0.2, 0.2)
        glVertex3f( 0.2,-0.2, 0.2)
        glVertex3f( 0.2,-0.2,-0.2)
    
    mousex = mousey = 0
    def mousePressEvent(self,event):
        if event.button() == 1:
            self.pickObjects(event.x(),event.y())

        self.mousex = event.x()
        self.mousey = event.y()

    def mouseMoveEvent(self,event):
        deltax = (event.x()-self.mousex)/2
        deltay = (event.y()-self.mousey)/2
        buttons = event.buttons()
        if buttons & QtCore.Qt.LeftButton:
            self.posx += deltax
            self.posy -= deltay
        if buttons & QtCore.Qt.RightButton:
            self.roty += deltax
            self.rotx += deltay
        self.mousex = event.x()
        self.mousey = event.y()
        self.updateGL()


class MainWindow(QtGui.QMainWindow):

    keyPresses = {0x1000020: 0}
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle("MK8-Editor")
        self.setGeometry(100,100,1080,720)

        self.setupMenu()
        
        self.qsettings = QtCore.QSettings("MrRean / RoadrunnerWMC","MK8 YAML Editor")
        self.restoreGeometry(self.qsettings.value("geometry").toByteArray())
        self.restoreState(self.qsettings.value("windowState").toByteArray())

        self.gamePath = self.qsettings.value('gamePath').toPyObject()
        if not self.isValidGameFolder(self.gamePath):
            self.changeGamePath(True)

        
        self.settings = SettingsWidget(self)
        self.setupGLScene()
        self.resizeWidgets()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateCamera)
        self.timer.start(30)

        self.show()


    def closeEvent(self, event):
        self.qsettings.setValue("geometry", self.saveGeometry())
        self.qsettings.setValue("windowState", self.saveState())

    def setupMenu(self):
        self.openAction = QtGui.QAction("Open",self)
        self.openAction.setShortcut("Ctrl+O")
        self.openAction.triggered.connect(self.showLevelDialog)

        self.saveAction = QtGui.QAction("Save",self)
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAction.triggered.connect(self.saveLevel)
        self.saveAction.setEnabled(False)

        pathAction = QtGui.QAction("Change Game Path",self)
        pathAction.setShortcut("Ctrl+G")
        pathAction.triggered.connect(self.changeGamePath)
        
        self.menubar = self.menuBar()
        fileMenu = self.menubar.addMenu("File")
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        settingsMenu = self.menubar.addMenu("Settings")
        settingsMenu.addAction(pathAction)

    def changeGamePath(self,disable=False):
        path = self.askGamePath()
        if path:
            self.qsettings.setValue('gamePath',path)
        else:
            if disable:
                self.openAction.setEnabled(False)
            QtGui.QMessageBox.warning(self,"Incomplete Folder","The folder you chose doesn't seem to contain the required files.")

    def askGamePath(self):
        QtGui.QMessageBox.information(self,'Game Path',"You're now going to be asked to pick a folder. This folder must include \course, \mapobj\ and \data.")
        folder = QtGui.QFileDialog.getExistingDirectory(self,"Choose Game Path")
        if not self.isValidGameFolder(folder):
            return None
        return folder

    def isValidGameFolder(self,folder):
        if not folder: return 0
        if not os.path.exists(folder+'\course'): return 0
        if not os.path.exists(folder+'\mapobj'): return 0
        if not os.path.exists(folder+'\data'): return 0
        return 1

    def loadStageList(self):
        # just return worldList as nothing, we don't even use it but the funtion needs to be there because another function needs an argument
        #with open(self.gamePath+'\data\objflow.byaml', 'rb') as f:
        #    self.worldList = byml.BYML(f.read(), True)
        self.worldList = None
        
    # edit this to open different types of stages
    def showLevelDialog(self):
        byamlPath = QtGui.QFileDialog.getOpenFileName(self, 'Open Level','course_muunt.byaml','Level Archive (*.byaml)');
        print "path is: "+byamlPath
        with open(byamlPath, 'rb') as f:
            self.levelData = byml.BYML(f.read(), True)
        self.loadLevel(self.levelData.rootNode.subNodes())
            
    def loadLevel(self,levelData):

        global modelNameMapping

        modelNameMapping = {}
        with open(window.gamePath+'/data/objflow.byaml', 'rb') as f: # load objflow to get the model names, and load them
            b = byml.BYML(f.read(), True)
            for thing in b.rootNode.subNodes():
                resName = thing.subNodes()['ResName'].subNodes()[0].val
                id = thing['ObjId']
                modelNameMapping[id] = resName
                
        
        stime = now()
        self.glWidget.reset()
        self.settings.reset()
        amount = len(levelData['Obj'])
        progress = QtGui.QProgressDialog(self)
        progress.setCancelButton(None)
        progress.setMinimumDuration(0)
        progress.setRange(0,amount)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        
        progress.setWindowTitle('Loading...')
        i = 1
        for obj in levelData['Obj'].subNodes():
            progress.setLabelText('Loading object '+str(i)+'/'+str(amount))
            print "loading object "+str(obj)
            progress.setValue(i)
            self.loadObject(obj)
            self.glWidget.updateGL()
            i+=1  
        self.saveAction.setEnabled(True)
        print now()-stime
        print str(amount)+' Objects loaded'

    def loadObject(self,obj):
        modelName = obj['ObjId']
        modelName = modelNameMapping[int(modelName)]
        self.glWidget.addObject(obj,modelName)


    def saveLevel(self):
        fn = QtGui.QFileDialog.getSaveFileName(self,'Save Level','course_muunt.byaml','Level Archive (*.byaml)')
        with open(fn,'wb') as f:
            self.levelData.saveChanges()
            f.write(self.levelData.data)
        print('Track '+str(fn)+' saved.')

    def setupGLScene(self):
        self.glWidget = LevelWidget(self)
        self.glWidget.show()

    def resizeWidgets(self):
        self.glWidget.setGeometry(220,21,self.width(),self.height()-21)
        self.settings.setGeometry(0,21,220,self.height()-21)

    def resizeEvent(self,event):
        self.resizeWidgets()

    def updateCamera(self):
        spd = self.keyPresses[0x1000020]*2+1
        updateScene = False
        for key in self.keyPresses:
            if self.keyPresses[key]:
                if key == ord('I'): self.glWidget.rotx+=spd
                elif key == ord('K'): self.glWidget.rotx-=spd
                elif key == ord('O'): self.glWidget.roty+=spd
                elif key == ord('L'): self.glWidget.roty-=spd
                elif key == ord('P'): self.glWidget.rotz+=spd
                elif key == ord(';'): self.glWidget.rotz-=spd
                elif key == ord('A'): self.glWidget.posx-=spd
                elif key == ord('D'): self.glWidget.posx+=spd
                elif key == ord('S'): self.glWidget.posy-=spd
                elif key == ord('W'): self.glWidget.posy+=spd
                elif key == ord('Q'): self.glWidget.posz-=spd
                elif key == ord('E'): self.glWidget.posz+=spd
                updateScene = True

        if updateScene:
            self.glWidget.updateGL()

    def keyReleaseEvent(self,event):
        self.keyPresses[event.key()] = 0

    def keyPressEvent(self,event):
        self.keyPresses[event.key()] = 1

    def wheelEvent(self,event):
        self.glWidget.posz += event.delta()/15
        self.glWidget.updateGL()

def main():
    global window
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
