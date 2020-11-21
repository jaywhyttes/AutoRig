"""
+---------------------------------------------------------------------------------------------------------------+
|   Spine Auto Rig:v1 -  Enmore Tafe                                                                            |
|   By Jason Whyttes  -  20/11/2020                                                                             |
----------------------------------------------------- USAGE ----------------------------------------------------+
|   1)  Use the Create Fit Rig button to create a system you can use to position on your character.             |
|       a)  Root control (white circle) to adjust the world position, rotate and scale.                         |
|       b)  Hip and Chest control (yellow boxes) to adjust where the hip/chest ik controllers will be created.  |
|       c)  Hip and Chest locators (pink locators) to adjust where the spine joint chain is created.            |
|   2)  Adjust the amount of joints the spine will have.                                                        |
|   3)  Use the Create Rig to convert the Fit Rig into a Spine Rig.                                             |
+----------------------------------------------- Trouble Shooting ----------------------------------------------+
|   Make sure to add a character name to the first text field.                                                  |
|   Make sure to create a fit rig first.                                                                        |
|   The amount value can be anything. If it is not a positive integer it will default to 0                      |
+---------------------------------------------------------------------------------------------------------------+
"""
import maya.cmds as cmds
from maya import OpenMayaUI
from shiboken2 import wrapInstance
from collections import OrderedDict
import sys
from PySide2.QtWidgets import (QLineEdit, QPushButton, QApplication, QWidget,
    QVBoxLayout, QDialog)
def checkExists(nodeName):
    """handles the naming of items
    
    checks if the object exits inside maya and if it does iterate the suffix until a empty name is found
    
    Arguments:
        nodeName {string} -- input node name to check
    
    Returns:
        string -- output string for the given node
    """
    n = 1
    nodeNameOut = nodeName + '_{:02d}'.format(n)            #adds 01 to the end of the input
    while True:
        if cmds.objExists(nodeNameOut):                     #while the name exists in Maya
            nodeNameOut = nodeName + '_{:02d}'.format(n)    #apply the same rule
            n += 1                                          #increment the value
        else:
            break
    return nodeNameOut
class MakeNodes():
    """handles the creation of nodes.
    
    A collection of functions that help create nodes needed for the AutoRig.
    """
    def circleCtrl(self,charName,crvPrefix,nodeUse,amount,padding,radius,sweep):
        """Create cirlces.
        
        Creates 1 or more circles of a specified radius, sweep and uses padding to stack them.
        It then parents the shape nodes under one transform.
        
        Arguments:
            charName {string} -- The characters name.
            crvPrefix {string} -- A prefix for the circle.
            nodeUse {string} -- A suffix to say the node use.
            amount {int} -- The amount of circles created.
            padding {int} -- The space between circles.
            radius {int} -- The size (radius) of the circle.
            sweep {int} -- How much of the circumference is created.
        
        Returns:
            string -- Return the shape name.
        """
        self.charName = charName
        self.crvPrefix = crvPrefix
        self.nodeUse = nodeUse
        self.amount = amount
        self.padding = padding
        self.radius = radius
        self.sweep = sweep
        circle01Name = checkExists('{}_{}_{}'.format(self.charName,self.crvPrefix,self.nodeUse))  #get valid name
        circle01 = cmds.circle(n = circle01Name,c=(0,0,0),nr=(0,1,0),sw=self.sweep,r=self.radius,d=3,s=8,ch=0)[0]  #create circle
        if amount > 1:  #if multiple circles to be made
            for i in range(1,self.amount):
                newShapeName = circle01Name + '_' + chr(i+65)  #adds A,B ect to end of shape node.
                newCircle = cmds.circle(n = newShapeName,c=(0,0,0),nr=(0,1,0),sw=self.sweep,r=self.radius,d=3,s=8,ch=0)[0]  #create circle
                circle02Shape = cmds.listRelatives(newCircle)  #get the shape node
                cmds.xform(newCircle,translation=(0,self.padding * (i),0))  #move the circle up
                cmds.makeIdentity(newCircle,a=1,t=1,r=1,s=1,n=0,pn=1)  #freeze its transforms
                cmds.parent(circle02Shape,circle01,r=1,s=1)  #parent its shape to the original circle created outside the loop
                cmds.delete(newCircle)  #delete the left over transform node
        cmds.xform(circle01,cp=1)  #center the circles pivot
        piv = cmds.xform(circle01,q=1,piv=1)[1]  #get the location of the pivot
        cmds.xform(circle01,translation=(0,piv*-1,0))  #multiply that location by -1 and move it in that direction (putting it back in world center)
        cmds.select(cl=1)  #clear selection
        return circle01
    def createCurve(self,charName,shape,crvPrefix,nodeUse):
        """Create custom curves.
        
        Uses predefined point locations to create custom curve shapes.
        Good for character controlleres.
        
        Arguments:
            charName {string} -- The characers name.
            shape {string} -- Select the shape type, 'help' returns a list of avaiable shapes.
            crvPrefix {string} -- Adds a prefix to the shape node.
            nodeUse {string} -- Adds a suffix to say the nodes use.
        
        Returns:
            string -- Returns the shape node.
        """
        self.charName = charName
        self.shape = shape
        self.crvPrefix = crvPrefix
        self.nodeUse = str(nodeUse)
        shapeName = checkExists('{}_{}_{}'.format(self.charName,self.crvPrefix,self.nodeUse))  #validate name
        sh01 = {    "points": [ (-1.5,1.5,1.5),  #a dictionary containing the custom shapes points and knot values
                    (1.5,1.5,1.5),               #data was extracted from a shape using a xform over the nodes cvs and returning those values here
                    (1.5,-1.5,1.5),              #knot range is len(cv) + d - 1
                    (1.5,-1.5,-1.5),
                    (1.5,1.5,-1.5),
                    (-1.5,1.5,-1.5),
                    (-1.5,-1.5,-1.5),
                    (-1.5,-1.5,1.5),
                    (-1.5,1.5,1.5),
                    (-1.5,1.5,-1.5),
                    (-1.5,-1.5,-1.5),
                    (1.5,-1.5,-1.5),
                    (1.5,1.5,-1.5),
                    (1.5,1.5,1.5),
                    (1.5,-1.5,1.5),
                    (-1.5,-1.5,1.5) ],
                    "knots": range(0,16)}
        sh02 = {    "points": [ (-4.0,0.2,-4.0),
                    (-4.0,-0.2,-4.0),
                    (4.0,-0.2,-4.0),
                    (4.0,0.2,-4.0),
                    (4.0,0.2,4.0),
                    (4.0,-0.2,4.0),
                    (-4.0,-0.2,4.0),
                    (-4.0,0.2,4.0),
                    (-4.0,0.2,-4.0),
                    (-4.0,-0.2,-4.0),
                    (-4.0,-0.2,4.0),
                    (-4.0,0.2,4.0),
                    (4.0,0.2,4.0),
                    (4.0,-0.2,4.0),
                    (4.0,-0.2,-4.0),
                    (4.0,0.2,-4.0),
                    (-4.0,0.2,-4.0) ],
                    "knots": range(0,17)}
        sh03 = {    "points": [ (-1,0,-8.74228e-08),
                    (0,2,0),
                    (1.31134e-07,0,-1),
                    (-1,0,-8.74228e-08),
                    (-4.37114e-08,0,1),
                    (0,2,0),
                    (1,0,0),
                    (-4.37114e-08,0,1),
                    (0,2,0),
                    (1.31134e-07,0,-1),
                    (1,0,0) ],
                    "knots": range(0,11)}
        sh04 = {    "points": [ (0.934487, 1.275837, 2.01658e-008 ),
                    (0.932697, 1.247176, -0.35686 ),
                    (0.920752, 1.172835, -0.686003 ),
                    (0.891476, 1.068829, -0.978435 ),
                    (0.840076, 0.946678, -1.231929 ),
                    (0.763591, 0.814991, -1.445766 ),
                    (0.661715, 0.681111, -1.621424 ),
                    (0.537155, 0.551427, -1.765671 ),
                    (0.387617, 0.433133, -1.880322 ),
                    (0.209586, 0.33878, -1.961541 ),
                    (0, 0.297363, -1.993747 ),
                    (-0.209586, 0.33878, -1.961541 ),
                    (-0.387617, 0.433133, -1.880322 ),
                    (-0.537155, 0.551427, -1.765671 ),
                    (-0.661715, 0.681111, -1.621424 ),
                    (-0.763591, 0.814991, -1.445766 ),
                    (-0.840076, 0.946678, -1.231929 ),
                    (-0.891476, 1.068829, -0.978435 ),
                    (-0.920752, 1.172835, -0.686003 ),
                    (-0.932697, 1.247176, -0.35686 ),
                    (-0.934487, 1.275837, 2.01658e-008 ),
                    (-0.917572, 1.470617, 0 ),
                    (-0.856971, 1.657129, 0 ),
                    (-0.758916, 1.826965, 0 ),
                    (-0.627692, 1.972704, 0 ),
                    (-0.469036, 2.087974, 0 ),
                    (-0.28988, 2.167739, 0 ),
                    (-0.0980551, 2.208513, 0 ),
                    (0.0980551, 2.208513, 0 ),
                    (0.28988, 2.167739, 0 ),
                    (0.469036, 2.087974, 0 ),
                    (0.627692, 1.972704, 0 ),
                    (0.758916, 1.826965, 0 ),
                    (0.856971, 1.657129, 0 ),
                    (0.917572, 1.470617, 0 ),
                    (0.934487, 1.275837, 2.01658e-008 ),
                    (0.932697, 1.247176, 0.35686 ),
                    (0.920752, 1.172834, 0.686003 ),
                    (0.891476, 1.06883, 0.978435 ),
                    (0.840076, 0.946678, 1.23193 ),
                    (0.763591, 0.814992, 1.445765 ),
                    (0.661715, 0.68111, 1.621426 ),
                    (0.537155, 0.55143, 1.765669 ),
                    (0.387617, 0.433127, 1.880326 ),
                    (0.209586, 0.338788, 1.961536 ),
                    (0, 0.297318, 1.993775 ),
                    (-0.209586, 0.338788, 1.961536 ),
                    (-0.387617, 0.433127, 1.880326 ),
                    (-0.537155, 0.55143, 1.765669 ),
                    (-0.661715, 0.68111, 1.621426 ),
                    (-0.763591, 0.814992, 1.445765 ),
                    (-0.840076, 0.946678, 1.23193 ),
                    (-0.891476, 1.06883, 0.978435 ),
                    (-0.920752, 1.172834, 0.686003 ),
                    (-0.932697, 1.247176, 0.35686 ),
                    (-0.934487, 1.275837, 2.01658e-008) ],
                    "knots": range(0,56)}
        sh05 = {    "points": [ (0,0,4),
                    (0,-2,1),
                    (0,-1,1),
                    (0,-1,-4),
                    (0,1,-4),
                    (0,1,1),
                    (0,2,1),
                    (0,0,4) ],
                    "knots": range(0,8)}
        sh06 = {    "points": [ (0,0,0),
                    (0,1,0) ],
                    "knots": range(0,2)}
        sh07 = {    "points": [ (2.57253,0,0),
                    (3.235575,0,-0.738488),
                    (2.552484,0,-0.738488),
                    (2,0,-0.105773),
                    (-2.457426,0,-0.102784),
                    (-2,0,-1),
                    (-4,0,0),
                    (-2,0,1),
                    (-2.457426,0,0.0956313),
                    (2,0,0.0956313),
                    (2.552484,0,0.738488),
                    (3.235575,0,0.738488),
                    (2.57253,0,0) ],
                    "knots":range(0,13)}
        sh08 = {    "points": [(3.9925971031188965, -0.7687759399414062, 0.0),
                    (3.985194206237793, -0.6989054679870605, -0.7656424641609192),
                    (3.9303150177001953, -0.5181548595428467, -1.5109076499938965),
                    (3.795288562774658, -0.2553844451904297, -2.2154181003570557),
                    (3.553771495819092, 0.03586721420288086, -2.8310279846191406),
                    (3.1794209480285645, 0.3020601272583008, -3.3095905780792236),
                    (2.6914026737213135, 0.5162158012390137, -3.6496047973632812),
                    (2.108882188796997, 0.6513543128967285, -3.8495688438415527),
                    (1.451664686203003, 0.734534740447998, -3.9495849609375),
                    (0.739555299282074, 0.7928156852722168, -3.9897541999816895),
                    (0.0, 0.8157315254211426, -3.994877576828003),
                    (-0.739555299282074, 0.7928156852722168, -3.9897541999816895),
                    (-1.451664686203003, 0.734534740447998, -3.9495849609375),
                    (-2.108882188796997, 0.6513543128967285, -3.8495688438415527),
                    (-2.6914026737213135, 0.5162158012390137, -3.6496047973632812),
                    (-3.1794209480285645, 0.3020601272583008, -3.3095905780792236),
                    (-3.553771495819092, 0.03586721420288086, -2.8310279846191406),
                    (-3.795288562774658, -0.2553844451904297, -2.2154181003570557),
                    (-3.9303150177001953, -0.5181548595428467, -1.5109076499938965),
                    (-3.985194206237793, -0.6989054679870605, -0.7656424641609192),
                    (-3.9925971031188965, -0.7687759399414062, 0.0),
                    (-3.985194206237793, -0.6989054679870605, 0.7656424641609192),
                    (-3.9303150177001953, -0.5181548595428467, 1.5109076499938965),
                    (-3.795288562774658, -0.2553844451904297, 2.2154181003570557),
                    (-3.553771495819092, 0.03586721420288086, 2.8310279846191406),
                    (-3.1794209480285645, 0.3020601272583008, 3.3095905780792236),
                    (-2.6914026737213135, 0.5162158012390137, 3.6496047973632812),
                    (-2.108882188796997, 0.6513543128967285, 3.8495688438415527),
                    (-1.451664686203003, 0.734534740447998, 3.9495849609375),
                    (-0.739555299282074, 0.7928156852722168, 3.9897541999816895),
                    (0.0, 0.8157315254211426, 3.994877576828003),
                    (0.739555299282074, 0.7928156852722168, 3.9897541999816895),
                    (1.451664686203003, 0.734534740447998, 3.9495849609375),
                    (2.108882188796997, 0.6513543128967285, 3.8495688438415527),
                    (2.6914026737213135, 0.5162158012390137, 3.6496047973632812),
                    (3.1794209480285645, 0.3020601272583008, 3.3095905780792236),
                    (3.553771495819092, 0.03586721420288086, 2.8310279846191406),
                    (3.795288562774658, -0.2553844451904297, 2.2154181003570557),
                    (3.9303150177001953, -0.5181548595428467, 1.5109076499938965),
                    (3.985194206237793, -0.6989054679870605, 0.7656424641609192),
                    (3.9925971031188965, -0.7687759399414062, 0.0) ],
                    "knots":range(0,41)
                    }
        #add new shapes to end
        availableCurveShapes = {'sh01':sh01,  #this handles input on the function and returns the corresponding dictionary
                                'sh02':sh02,
                                'sh03':sh03,
                                'sh04':sh04,
                                'sh05':sh05,
                                'sh06':sh06,
                                'sh07':sh07,
                                'sh08':sh08}
        #add new shapes to end
        helpStr = OrderedDict([ ("sh01","A standard cube."),  #if a invalid argument is given, and string will tell the user to use 'help' which will return this.
                                ("sh02","A short cube."),
                                ("sh03","A square Pyramid."),
                                ("sh04","A Horse Shoe."),
                                ("sh05","A arrow in Z,Y."),
                                ("sh06","A two point line."),
                                ("sh07","A Arrow"),
                                ("sh08","A Warped, soft square") ])

        try:
            if self.shape == 'help':  #return the help strings
                for items in helpStr:
                    print('{} : {}'.format(items,helpStr[items]))
            else:
                curveData = availableCurveShapes.get(self.shape)  #look in the availableCurveShapes for corresponding a value
                shapeCrv = cmds.curve(n = shapeName, d=1,p=curveData['points'],k=curveData['knots'])  #create the curve based on the data
                cmds.select(cl=True)  #clear select
                return shapeCrv  #return the node
        except TypeError:
            print("{} not in an available shape.\nUse 'help' to get a list of shapes.".format(self.shape))  #string returned if invalid arguement is given
    def createLoc(self,charName,locSuffix,nodeUse):
        """Simple function to create locs.
        
        Just makes a loc with a specific name.
        
        Arguments:
            charName {string} -- The character name.
            locSuffix {string} -- Adds a suffix to say what the node type is.
            nodeUse {string} -- Adds a suffix to say what the node is used for.
        
        Returns:
            string -- Returns the locator.
        """
        self.charName = charName
        self.locSuffix = locSuffix
        self.nodeUse = str(nodeUse)
        locName = checkExists('{}_{}_{}'.format(self.charName,self.locSuffix,self.nodeUse))  #validate name
        loc = cmds.spaceLocator(n=locName)  #create a locator node
        return loc[0]  #return the node
    def createGrp(self,charName,grpSuffix,nodeUse):
        """Simple funciton to create groups.
        
        Just makes a group with a specific name.
        
        Arguments:
            charName {string} -- The character name.
            grpSuffix {string} -- Adds a suffix to say what the node type is.
            nodeUse {string} -- Adds a suffix to say what the node is used for.
        
        Returns:
            string -- Returns the group.
        """
        self.charName = charName
        self.grpSuffix = grpSuffix
        self.nodeUse = str(nodeUse)
        nodeName = checkExists('{}_{}_{}'.format(self.charName,self.grpSuffix,self.nodeUse))  #validate name
        grp = cmds.group(n=nodeName, em=1)  #create a group node
        return grp  #return the node
    def createChain(self,charName,typeOfNode,fromNode,toNode,amount,scale,chainName,nodeUse):
        """Creats a chain between two select nodes.
        
        Uses two given nodes to create a chain of x amount.
        The chain can be either locators, groups or joints.
        
        Arguments:
            charName {string} -- The character name.
            typeOfNode {string} -- Uses 'joint','group'or'loc' to pick the type of node created in the chain.
            fromNode {string} -- Starts the chain here.
            toNode {string} -- Ends the chain here.
            amount {int} -- The amount of nodes created.
            scale {int} -- The scale of the nodes created.
            chainName {string} -- A suffix to say what type of node it is.
            nodeUse {string} -- A suffix to say what the chain is used for.
        
        Returns:
            list -- Returns a chain of nodes (the chain).
        """
        self.charName = charName
        self.typeOfNode = typeOfNode
        self.fromNode = fromNode
        self.toNode = toNode
        self.amount = amount - 2
        self.scale = float(scale)
        self.nodeUse = nodeUse
        self.chainName = chainName
        typeOfNodeSelected = None
        chain = []  #                                                
        #this algorithm is used to get the points of a line. x,y = (x1 + k(x2 - x1),y1 + k(y2 - y1))
        #That algorithm works for x and y, so to get z I modified it to only work in 1 direction at a time, then ran it over x, y and z. x = ((k/k+1) * x1) + ((1/k+1) * x2) - x1
        gapTx = ((float(self.amount) / (float(self.amount) + 1) * self.fromNode[0][0]) + ((1 / (float(self.amount) + 1)) * self.toNode[0][0])) - self.fromNode[0][0]
        gapTy = ((float(self.amount) / (float(self.amount) + 1) * self.fromNode[0][1]) + ((1 / (float(self.amount) + 1)) * self.toNode[0][1])) - self.fromNode[0][1]
        gapTz = ((float(self.amount) / (float(self.amount) + 1) * self.fromNode[0][2]) + ((1 / (float(self.amount) + 1)) * self.toNode[0][2])) - self.fromNode[0][2]
        if self.typeOfNode == 'group' or self.typeOfNode == 'loc' or self.typeOfNode == 'joint':  #check if input is either 'group','loc' or 'joint'
            if self.typeOfNode == 'group': 
                typeOfNodeSelected = 'cmds.group(n=nodeName,em=1)'  #If I return the command as a string I can store the command as a variable and use it with eval later
            elif self.typeOfNode == 'loc':
                typeOfNodeSelected = 'cmds.spaceLocator(n=nodeName)'
            else:
                typeOfNodeSelected = 'cmds.joint(n=nodeName)'
            nodeName = checkExists('{}_{}_{}'.format(self.charName,self.chainName,self.nodeUse))  #validate name
            hipNode = eval(typeOfNodeSelected)  #run the command to create the start node
            cmds.xform(hipNode,translation=(fromNode[0][0],fromNode[0][1],fromNode[0][2]))  #position the start node
            cmds.xform(hipNode,rotation=fromNode[1])  #rotate the start node
            if self.typeOfNode == 'joint':  #if input was 'joint'
                cmds.setAttr(hipNode + '.radius',self.scale)  #set the start joint scale using the radius
            else:
                cmds.xform(hipNode,scale=(self.scale,self.scale,self.scale))  #otherwise set the node scale using scale
            chain.append(hipNode)  #append the start node to a list to return later
            cmds.select(cl=True)  #clear select
            for i in range(0, amount - 2):  #create the nodes that are placed between the start and end nodes
                nodeName = checkExists('{}_{}_{}'.format(self.charName,self.chainName,self.nodeUse))  #validate name
                posTx = self.fromNode[0][0] + (gapTx * (i + 1))  #get the gap from the algorithm above and nudge it based on how many iterations we have done
                posTy = self.fromNode[0][1] + (gapTy * (i + 1))  #do the same for y
                posTz = self.fromNode[0][2] + (gapTz * (i + 1))  #and z
                posR = self.fromNode[1]  #rotation stays the same but needs to be added to each node created
                chainNode = eval(typeOfNodeSelected)  #create the node using eval
                cmds.xform(chainNode,translation=(posTx,posTy,posTz))  #move the node
                cmds.xform(chainNode,rotation=posR)  #rotate the node
                if self.typeOfNode == 'joint':  #do the same as above when checking if joint (joint = radius, group or loc = scale)
                    cmds.setAttr(chainNode + '.radius',self.scale)
                else:
                    cmds.xform(chainNode,scale=(self.scale,self.scale,self.scale))
                chain.append(chainNode)  #add node to list
                cmds.select(cl=True)
            nodeName = checkExists('{}_{}_{}'.format(self.charName,self.chainName,self.nodeUse))  #validate name
            chestNode = eval(typeOfNodeSelected)  #create end node
            cmds.xform(chestNode,translation=(toNode[0][0],toNode[0][1],toNode[0][2]))  #position end node
            cmds.xform(chestNode,rotation=toNode[1])  #rotate end node
            if self.typeOfNode == 'joint':  #the same radius scale thing again
                cmds.setAttr(chestNode + '.radius',self.scale)
            else:
                cmds.xform(chestNode,scale=(self.scale,self.scale,self.scale))
            chain.append(chestNode)  #add end node to list
            cmds.select(cl=True)
        else:
            print("{} not allow, use 'group', 'loc', or 'joint'.".format(self.typeOfNode)) #return if invalid input is recieved
        return chain
    def createIkSpline(self,charName,chain,ctrlJnt01,ctrlJnt02,ctrl01,ctrl02,pointguide):
        """Create a IK Spline Spine.
        
        Uses a chain of joints to create a IK spline.
        Uses a chain of 4 nodes to create a curve for the IK spline.
        Uses two given joints to bind the IK curve created.
        Parent Constraint the given controls, and setup the advance twist.
        
        Arguments:
            charName {string} -- The character name.
            chain {list} -- The chain used to create the Ik Spline Spine.
            ctrlJnt01 {string} -- The first Joint bind the the IK curve.
            ctrlJnt02 {string} -- The second joint bound to the IK curve.
            ctrl01 {string} -- The first control used to control the first IK curve bind joint.
            ctrl02 {string} -- The second control used to control the second IK curve bind joint
            pointguide {list} -- A chain used to create the IK Spline curve.
        
        Returns:
            string,string -- Returns the IK curve and IK handle.
        """
        self.charName = charName
        self.chain = chain
        self.ctrlJnt01 = ctrlJnt01
        self.ctrlJnt02 = ctrlJnt02
        self.pointStart = pointguide[0]
        self.midPointStart = pointguide[1]
        self.midPointEnd = pointguide[2]
        self.ctrl01 = ctrl01
        self.ctrl02 = ctrl02
        self.pointEnd = pointguide[3]
        startJoint = self.chain[0]
        endJoint = self.chain[len(self.chain)-1]
        pointStartPos = cmds.xform(self.pointStart,q=1,t=1,a=1,ws=1)  #Creating the curve requires a chain to be created so we can plot the curve on those positions
        pointEndPos = cmds.xform(self.pointEnd,q=1,t=1,a=1,ws=1)  #a 4 point chain was created and positions extracted
        midPointStartPos = cmds.xform(self.midPointStart,q=1,t=1,a=1,ws=1)  #those 4 points are later used to create a bezier curve
        midPointEndPos = cmds.xform(self.midPointEnd,q=1,t=1,a=1,ws=1)  #a bezier curve is used as the ik spline curve as it bends nicely when skinned to joints
        for i in pointguide:  #we can now delete those points
            cmds.delete(i)
        psx = pointStartPos[0]  #for each point get the x,y,z translation values
        psy = pointStartPos[1]
        psz = pointStartPos[2]
        pex = pointEndPos[0]
        pey = pointEndPos[1]
        pez = pointEndPos[2]
        pmsx = midPointStartPos[0]
        pmsy = midPointStartPos[1]
        pmsz = midPointStartPos[2]
        pmex = midPointEndPos[0]
        pmey = midPointEndPos[1]
        pmez = midPointEndPos[2]
        splneCrvName = checkExists('{}_spline_crv'.format(self.charName))  #validate name
        ikHdlName = checkExists('{}_spline_hdl'.format(self.charName))  #validate name
        splineCrv = cmds.curve(n=splneCrvName,d=3,p=[(psx,psy,psz),(pmsx,pmsy,pmsz),(pmex,pmey,pmez),(pex,pey,pez)],k=[0,0,0,1,1,1])  #create the curve
        ikHdl = cmds.ikHandle(n=ikHdlName,ccv=0,c=splineCrv,sj=startJoint,ee=endJoint,sol='ikSplineSolver')[0]  #create the ik handle
        cmds.skinCluster(self.ctrlJnt01,self.ctrlJnt02,splineCrv,bindMethod=0,skinMethod=1,normalizeWeights=1,weightDistribution=0,mi=4,omi=1,dr=4,rui=1)  #skin the curve to a given joint chain
        #this is hard coded because I dont have a method of giving the user control over joint orientation on rig creation yet
        #normally that orientation would control what part of the matrix is used for the advanced twist attributes
        #this can be accomplished by a control at the fit rig stage that allows the user to choose a orientation by rotating the controller
        #alternatively they can enter it in the gui
        world_mat_ctrl01 = cmds.xform(self.ctrl01,q=1,m=1,ws=1)  #get the entire matrix for cltr01
        world_mat_ctrl02 = cmds.xform(self.ctrl02,q=1,m=1,ws=1)  #get the entire matrix for ctrl02
        ctrl01_axis = world_mat_ctrl01[8:11]  #return just the values for z for ctrl01
        ctrl02_axis = world_mat_ctrl02[8:11]  #return just the values for z for ctrl02
        cmds.setAttr(ikHdl + '.dTwistControlEnable',1)  #turn on advanced twist
        cmds.setAttr(ikHdl + '.dWorldUpType',4)  #use objects
        cmds.setAttr(ikHdl + '.dForwardAxis',2)  #set forward axis
        cmds.setAttr(ikHdl + '.dWorldUpAxis',4)  #set up axis
        cmds.setAttr(ikHdl + '.dWorldUpVectorX', 0)  #x up for ctrl01
        cmds.setAttr(ikHdl + '.dWorldUpVectorY', ctrl01_axis[1] * -1)  #y up for ctrl01
        cmds.setAttr(ikHdl + '.dWorldUpVectorZ', ctrl01_axis[2] * -1)  #z up for ctrl01
        cmds.setAttr(ikHdl + '.dWorldUpVectorEndX', 0)  #x up for ctrl02
        cmds.setAttr(ikHdl + '.dWorldUpVectorEndY', ctrl02_axis[1] * -1)  #y up for ctrl02
        cmds.setAttr(ikHdl + '.dWorldUpVectorEndZ', ctrl02_axis[2] * -1)  #z up for ctrl02
        cmds.connectAttr(self.ctrl01 + '.worldMatrix[0]',ikHdl + '.dWorldUpMatrix',f=1)  #connect ctrl01 to up 1 input
        cmds.connectAttr(self.ctrl02 + '.worldMatrix[0]',ikHdl + '.dWorldUpMatrixEnd',f=1)  #connect ctrl02 to up 2 input
        cmds.parentConstraint(self.ctrl01,self.ctrlJnt01,mo=1)  #constrain ctrl01 to the first joint skinned to the ik spline curve
        cmds.parentConstraint(self.ctrl02,self.ctrlJnt02,mo=1)  #constrain ctrl02 to the second joint skinned to the ik spline curve
        cmds.select(cl=1)  #clear selection
        return splineCrv, ikHdl  #return the curve and ik handle nodes
class EditNodes():
    """handles editing attributes.
    
    A collection of functions to help alter various values on select nodes.
    """
    def lockHideAll(self,node):
        """Lock and hide channel box.

        Locks and hides all the attributes on the node.
        
        Arguments:
            node {string} -- The node that will have its channel box locked and hidden.
        """
        self.node = node
        valueAttr = ['.tx','.ty','.tz','.rx','.ry','.rz','.sx','.sy','.sz','.v']  #a list of values used to lock and hide
        for i in range(0, len(valueAttr)):
            cmds.setAttr('{}{}'.format(self.node,valueAttr[i]), lock = 1, keyable = 0, channelBox = 0)  #iterate over the values and lock hide them 1 by 1
    def unlockUnHideAll(self,node):
        """Unlock and unhide channel box.
        
        Unlocks and Unhides all the attributes on the node.
        
        Arguments:
            node {string} -- The node that will have its channel box unlocked and unhidden.
        """
        self.node = node
        valueAttr = ['.tx','.ty','.tz','.rx','.ry','.rz','.sx','.sy','.sz','.v']  #a list of values used to unlock and unhide
        for i in range(0, len(valueAttr)):
            cmds.setAttr('{}{}'.format(self.node,valueAttr[i]), lock = 0, channelBox = 1)  #iterate over the valuese and unlock unhide them 1 by 1
            cmds.setAttr('{}{}'.format(self.node,valueAttr[i]), keyable = 1)  #keyable needs to be done after its shown on the channel box and unlocked otherwise it wont work (can't key something that isn't visible or locked)
    def lockHideSpecific(self,node,t,r,s,v):
        """Lock and Hide specific attributes.
        
        Uses inputs to select which attributes on the node to lock and hide.
        
        Arguments:
            node {string} -- The node that will have its channel box locked and hidden.
            t {list} -- Values to lock and hide the translation values (x,y,z).
            r {list} -- Values to lock and hide the rotation values (x,y,z).
            s {list} -- Values to lock and hide the scale values (x,y,z).
            v {int} -- Value to lock and hide the visibility attribute.
        """
        self.node = node
        self.t = t
        self.r = r
        self.s = s
        self.v = v
        tx = self.t[0]
        ty = self.t[1]
        tz = self.t[2]
        rx = self.r[0]
        ry = self.r[1]
        rz = self.r[2]
        sx = self.s[0]
        sy = self.s[1]
        sz = self.s[2]
        valueAttr = {'.tx':tx,'.ty':ty,'.tz':tz,'.rx':rx,'.ry':ry,'.rz':rz,'.sx':sx,'.sy':sy,'.sz':sz,'.v':v}  #values used to lock and hide specified attributes on a given node
        for i in valueAttr:
            if valueAttr[i] == 1:
                cmds.setAttr('{}{}'.format(self.node,i), lock = 1, keyable = 0, channelBox = 0)  #lock and hide specified attributes
    def unlockUnHideSpecific(self,node,t,r,s,v):
        """Unlock and unhide specific attributes.
        
        Uses inputs to select which attributes on the node to lock and hide.
        
        Arguments:
            node {string} -- The node that will have its channel box unlocked and unhidden.
            t {list} -- Values to unlock and unhide the translation values (x,y,z).
            r {list} -- Values to unlock and unhide the rotation values (x,y,z).
            s {list} -- Values to unlock and unhide the scale values (x,y,z).
            v {int} -- Value to unlock and unhide the visibility attribute.
        """
        self.node = node
        self.t = t
        self.r = r
        self.s = s
        self.v = v
        tx = self.t[0]
        ty = self.t[1]
        tz = self.t[2]
        rx = self.r[0]
        ry = self.r[1]
        rz = self.r[2]
        sx = self.s[0]
        sy = self.s[1]
        sz = self.s[2]
        valueAttr = {'.tx':tx,'.ty':ty,'.tz':tz,'.rx':rx,'.ry':ry,'.rz':rz,'.sx':sx,'.sy':sy,'.sz':sz,'.v':v}  #values used to unlock and unhide specified attributes on a given node
        for i in valueAttr:
            if valueAttr[i] == 1:
                cmds.setAttr('{}{}'.format(self.node,i), lock = 0, channelBox = 1)  #unlock and unhide specified attributes
                cmds.setAttr('{}{}'.format(self.node,i), keyable = 1)  #same issue as above
    def centerWorld(self,node):
        """Place the node at world center.
        
        Gets the nodes location and moves it back to world center by multiplying current translation values by -1.
        
        Arguments:
            node {string} -- The node to move to center.
        """
        self.node = node
        rpPos = cmds.xform(self.node, query=True, rp=True, worldSpace=True )  #find the nodes rotation pivot
        center = []
        for v in rpPos:
            negV = v * -1  #multiply values by -1 and plae them in a list
            center.append(negV)
        cmds.xform(self.node, translation=center)  #apply those valuese to the node
    def xformNode(self,node,t,r,s,rel,ws):
        """xform the select node.
        
        Uses inputs to move the selected node using the xform command.
        Supports using 'pass' to skip specified values.
        
        Arguments:
            node {string} -- The node to xform.
            t {list} -- Values used to translate the node (x,y,z).
            r {list} -- Values usesd to rotate the node (x,y,z).
            s {list} -- Values usesd to scale the node (x,y,z).
            rel {int} -- Use relative or not.
            ws {int} -- Use world space or not.
        """
        self.node = node
        self.relative = rel
        self.worldSpace = ws
        self.t = t
        self.r = r
        self.s = s
        tx = self.t[0]
        ty = self.t[1]
        tz = self.t[2]
        rx = self.r[0]
        ry = self.r[1]
        rz = self.r[2]
        sx = self.s[0]
        sy = self.s[1]
        sz = self.s[2]
        valueInput = [[tx,ty,tz],[rx,ry,rz],[sx,sy,sz]]
        valueAttr = ['.tx','.ty','.tz','.rx','.ry','.rz','.sx','.sy','.sz']  #values to run xform on
        preXformLockState = []  #is the value locked previously? store state here if so
        for i in range(0, len(valueAttr)):
            getLock = cmds.getAttr('{}{}'.format(self.node, valueAttr[i]), lock = 1)  #get the lock state of the attribute
            preXformLockState.append(getLock)  #add it to the list
            cmds.setAttr('{}{}'.format(self.node,valueAttr[i]), lock = 0)  #unlock
        a = 0
        t = []
        r = []
        s = []
        for v in valueInput[0]:
            if v == 'pass':  #if pass is used
                t.append(cmds.getAttr('{}{}'.format(self.node,valueAttr[a])))  #append its value to t
            else:
                t.append(v)  #otherwise append the given value
            a += 1
        cmds.xform('{}'.format(self.node),translation=t,relative=self.relative,worldSpace=self.worldSpace)  #translate the object based on values in the 't' list
        for v in valueInput[1]:  #exact same thing as before by for rotation
            if v == 'pass':
                r.append(cmds.getAttr('{}{}'.format(self.node,valueAttr[a])))
            else:
                r.append(v)
            a += 1
        cmds.xform('{}'.format(self.node),rotation=r,relative=self.relative,worldSpace=self.worldSpace)
        for v in valueInput[2]:  #exact same thing as before by for scale
            if v == 'pass':
                s.append(cmds.getAttr('{}{}'.format(self.node,valueAttr[a])))
            else:
                s.append(v)
            a += 1
        cmds.xform('{}'.format(self.node),scale=s,relative=self.relative,worldSpace=self.worldSpace)
        for i in range(0, len(valueAttr)):
            cmds.setAttr('{}{}'.format(self.node,valueAttr[i]), lock = preXformLockState[i])  #get the lock state we created above and lock attributes that were previously locked again
    def clusterCrv(self,node,point,suffix):
        self.node = node
        self.point = point
        self.suffix = suffix
        try:
            crvCls = cmds.cluster(self.node + '.cv[{}]'.format(self.point),n=self.node + '_{}_cls_'.format(self.suffix))  #cluster cv
            handle = (cmds.listConnections(crvCls[0] + ".matrix") or [None])[0]  #get the cluster handle name
            if not handle:
                return(crvCls)
            else:
                return(handle)
        except TypeError:
            print("Input error : (curve name[str], point[int],suffix[str]")  #tell the user what type of data to enter
        except ValueError:
            print("Input error : First item should be a nurbs curve.")  #the node should be a curve
    def setCol(self,node,col):
        self.node = node
        self.col = col
        colorValues = { 'black':1,  #specified common colors with their numerical value
                        'white':16,
                        'red':13,
                        'blue':6,
                        'yellow':17,
                        'pink':9,
                        'rose':4,
                        'ocean':15
                        }
        failed = 0
        for x, y in colorValues.items():
            if self.col == 'help'.lower():  #print that dictionary if 'help' is used
                helpList = ''
                for colString in colorValues:
                    print('{}'.format(colString))
                break                   
            if self.col.lower() == x:
                colVal = y  #get the corresponding numerical value of the given  input
                cmds.setAttr('{}.overrideEnabled'.format(self.node), 1)  #override enabled for the node
                cmds.setAttr('{}.overrideColor'.format(self.node),colVal)  #set color for the node
                failed = 0
                break
            else:
                failed = 1  #set failed to 1 if the user entered a bad argument
        if failed:
            print("Error passing color value.\nIt probably wasn't in the list of available colors.\nUse 'help' to get a list of available colors.")  #a helpful string
    def parentNodes(self,c,p):
        """Parent in hierarchy 
        
        Parent select nodes in hierarchy, 1-child 2-parent
        
        Arguments:
            c {string} -- The child node.
            p {string} -- The parent node.
        """
        self.child = c
        self.parent = p
        cmds.parent(self.child,self.parent)  #simply parent (c)hild to (p)arent
        cmds.select(clear=True)  #clear selection
    def matchNodes(self,targetNode):
        """Get translation/rotation/scale of select node.
        
        Uses xform to return translation/rotation/scale values on the select node.
        
        Arguments:
            targetNode {string} -- The node to match.
        
        Returns:
            list -- Return a list of values relating to the matched node.
        """
        self.targetNode = targetNode
        values = []  #empty list
        values.append(cmds.xform(targetNode,q=1,t=1,a=1,ws=1))  #add translation values to list
        values.append(cmds.xform(targetNode,q=1,ro=1,ws=1))  #add rotation values to list
        values.append(cmds.xform(targetNode,q=1,s=1,ws=1))  #add scale values to list
        return values  #return list
    def aimNode(self, driven, driver, aimV, upV):
        """Aim Constraint function.
        
        Aims nodes at other nodes.
        
        Arguments:
            driven {string} -- The node to be aimed.
            driver {string} -- The node to aim at.
            aimV {list} -- The aim vector.
            upV {list} -- The up vector.
        """
        self.driven = driven
        self.driver = driver
        self.aimV = aimV
        self.upV = upV
        const = cmds.aimConstraint(driver, driven, aim=self.aimV, u=self.upV)  #simply aim constrain the node
        return const
    def rotToOrient(self,nodes):
        """Convert rotation values to orient values
        
        Gets the rotation values on the given node and applies them to its orientation.
        Zeros the given rotation after.
        
        Arguments:
            nodes {string} -- The node to convert.
        """
        self.nodes = nodes
        for i in range(0, len(self.nodes)):
            if cmds.nodeType(self.nodes[i]) == 'joint':
                rotValue = cmds.xform(self.nodes[i], q=1, rotation=1)
                cmds.xform(self.nodes[i],rotation=(0,0,0))
                cmds.joint(self.nodes[i],edit=1,orientation=(rotValue[0],rotValue[1],rotValue[2]))
                cmds.select(clear=1)
            else:
                print('{} was not a joint, skipping.'.format(self.nodes[i]))
    def parentChain(self,chain):
        """Parents the given nodes into a hierarchy.
        
        Traverses the given list and places them into a hierarchy.
        
        Arguments:
            chain {list} -- The chain to place into a hierarchy.
        """
        self.chain = chain
        for i in range(0, len(self.chain) - 1,1):
            cmds.parent(self.chain[i+1],self.chain[i])
            cmds.select(clear=1)
    def setRotateOrder(self,node,order,chain):
        """Set rotation order.
        
        Sets the nodes rotaiton order.
        Allows chains to be usesd.
        
        Arguments:
            node {string} -- The single node to set rotation order on.
            order {int} -- The rotaton order
            chain {list} -- Multiple nodes to set rotation orders on.
        """
        self.node = node
        self.order = order
        self.chain = chain
        if self.chain == 1:
            for i in range(0, len(self.node),1):
                cmds.setAttr(self.node[i] + '.rotateOrder',self.order)
        else:
            cmds.setAttr(self.node + '.rotateOrder',self.order)
    def parentFk(self,chain,ctrls,guide,ctrlgrp02,ctrlgrp03):
        """Parent FK Ctrls to Joint chain.
        
        Creates a curve and skins it to three joints.
        Gets the bind values on the curves cvs.
        Parent constraint the fk controllers to the joint chain.
        Uses the bind values to set parent constraint values.
        
        Arguments:
            chain {list} -- The joint chain.
            ctrls {list} -- The FK controlleres.
            guide {list} -- Joints to bind the curve to.
            ctrlgrp02 {string} -- offset group for the fk ctrl.
            ctrlgrp03 {string} -- offset group for the fk ctrl.
        """
        self.chain = chain
        self.ctrl01 = ctrls[0]
        self.ctrl02 = ctrls[1]
        self.ctrl03 = ctrls[2]
        self.guide = guide
        self.ctrlgrp02 = ctrlgrp02
        self.ctrlgrp03 = ctrlgrp03
        chainTranslationValues = []
        for i in range(0, len(self.chain),1):
            chainTranslationValues.append(cmds.xform(self.chain[i],q=1,t=1,a=1,ws=1))
        knots = range(0,len(self.chain))
        points = []
        for i in range(0, len(chainTranslationValues),1):
            points.append(tuple(chainTranslationValues[i]))
        tempCrv = cmds.curve(n = 'temp_skin_bind_guide_crv',d=1,p=points,k=knots)
        skin = cmds.skinCluster(self.guide[0],self.guide[1],guide[2],tempCrv,bindMethod=0,skinMethod=1,normalizeWeights=1,weightDistribution=0,mi=4,omi=1,dr=4,rui=1)
        deg = cmds.getAttr(tempCrv + '.degree')
        span = cmds.getAttr(tempCrv + '.spans')
        if len(self.chain)%2 == 1:
            for i in range(1,(deg+span)/2,1):
                p = cmds.skinPercent( skin[0], tempCrv + '.cv[{}]'.format(i), query=True, value=True )
                cmds.orientConstraint(self.ctrl01,self.chain[i],w = p[0],mo=1)
                cmds.orientConstraint(self.ctrl02,self.chain[i],w = p[1],mo=1)
            for i in range(deg+span/2,(deg+span)-1,1):
                p = cmds.skinPercent( skin[0], tempCrv + '.cv[{}]'.format(i), query=True, value=True )
                cmds.orientConstraint(self.ctrl02,self.chain[i],w = p[1],mo=1)
                cmds.orientConstraint(self.ctrl03,self.chain[i],w = p[2],mo=1)
            cmds.orientConstraint(self.ctrl02,self.chain[len(self.chain)/2],w=1,mo=1)
            cmds.pointConstraint(self.chain[len(self.chain)/2],self.ctrl02,w=1,mo=1)
        else:
            for i in range(1,(deg+span)/2 - 1,1):
                p = cmds.skinPercent( skin[0], tempCrv + '.cv[{}]'.format(i), query=True, value=True )
                cmds.orientConstraint(self.ctrl01,self.chain[i],w = p[0],mo=1)
                cmds.orientConstraint(self.ctrl02,self.chain[i],w = p[1],mo=1)
            for i in range((deg+span)/2 + 1,(deg+span)-1 ,1):
                p = cmds.skinPercent( skin[0], tempCrv + '.cv[{}]'.format(i), query=True, value=True )
                cmds.orientConstraint(self.ctrl02,self.chain[i],w = p[1],mo=1)
                cmds.orientConstraint(self.ctrl03,self.chain[i],w = p[2],mo=1)
            lwr = self.chain[(len(self.chain)/2)-1]
            upr = self.chain[len(self.chain)/2]
            cmds.orientConstraint(self.ctrl02,lwr,w=1,mo=1)
            cmds.orientConstraint(self.ctrl02,upr,w=1,mo=1)
            cmds.pointConstraint(lwr,upr,self.ctrl02,w=.5,mo=1)
        cmds.orientConstraint(self.ctrl01,self.chain[0],w=1,mo=1)
        cmds.orientConstraint(self.ctrl03,self.chain[len(self.chain)-1],w=1,mo=1)
        cmds.pointConstraint(self.chain[0],self.ctrl01,w=1,mo=1)
        cmds.pointConstraint(self.chain[len(self.chain)-1],self.ctrl03,w=1,mo=1)
        cmds.delete(skin)
        cmds.delete(tempCrv)
        cmds.parentConstraint(self.ctrl01,self.ctrlgrp02,mo=1)
        cmds.parentConstraint(self.ctrl02,self.ctrlgrp03,mo=1)
        cmds.select(cl=1)
    def ikfk_switch(self,chain01,chain02,chain03,switchCtrl,ctrlfk,ctrlik):
        """IK FK switching
        
        Places a ik/fk switch attribute on the select node.
        Takes 3 joint chains.
        Parents them together.
        Creates set driven keys and uses the ik/fk switch attribute to swap values.
        
        Arguments:
            chain01 {list} -- IK joint chain.
            chain02 {list} -- FK joint chain.
            chain03 {list} -- Result joint chain.
            switchCtrl {string} -- Node with ik fk switch attribute.
            ctrlfk {list} -- The FK controls.
            ctrlik {list} -- The IK controls.
        """
        self.ikChain = chain01
        self.fkChain = chain02
        self.resultChain = chain03
        self.switchCtrl = switchCtrl
        self.ctrlfk = ctrlfk
        self.ctrlik = ctrlik
        cmds.addAttr(self.switchCtrl,ln='ik_fk_switch',nn='IK/FK Switch',at='double',min=0,max=1,dv=0,k=1)  #create switch attribute on cog grp node
        const = []
        for i in range(0, len(self.ikChain),1):  #use ik chain to loop over function, can be any chain though
            c = cmds.parentConstraint(self.ikChain[i],self.fkChain[i],self.resultChain[i],w=.5,mo=1)  #parent the ik and fk chain to result
            const.append(c)  #append the parent constraint name to the const list
        for i in range(0, len(self.ikChain),1):
            cmds.setAttr('{}.{}W0'.format(const[i][0],self.ikChain[i]),1)  #the name of the ik joint parent constraint
            cmds.setAttr('{}.{}W1'.format(const[i][0],self.fkChain[i]),0)  #the name of the fk joint parent cosntraint
            cmds.setAttr('{}.visibility'.format(self.ctrlfk[0]),0)  #set the visibility of the ik and fk controls
            cmds.setAttr('{}.visibility'.format(self.ctrlfk[1]),0)
            cmds.setAttr('{}.visibility'.format(self.ctrlfk[2]),0)
            cmds.setAttr('{}.visibility'.format(self.ctrlik[0]),1)
            cmds.setAttr('{}.visibility'.format(self.ctrlik[1]),1)
            cmds.setDrivenKeyframe('{}.{}W0'.format(const[i][0],self.ikChain[i]),cd = '{}.ik_fk_switch'.format(self.switchCtrl),itt='linear',ott='linear')  #create a key between the cog ik/fk switch
            cmds.setDrivenKeyframe('{}.{}W1'.format(const[i][0],self.fkChain[i]),cd = '{}.ik_fk_switch'.format(self.switchCtrl),itt='linear',ott='linear')  #and the ik/fk parent constraints
            cmds.setDrivenKeyframe('{}.visibility'.format(self.ctrlfk[0]),cd = '{}.ik_fk_switch'.format(self.switchCtrl),itt='linear',ott='linear')         #also set a key for the controllers visibility
            cmds.setDrivenKeyframe('{}.visibility'.format(self.ctrlfk[1]),cd = '{}.ik_fk_switch'.format(self.switchCtrl),itt='linear',ott='linear')
            cmds.setDrivenKeyframe('{}.visibility'.format(self.ctrlfk[2]),cd = '{}.ik_fk_switch'.format(self.switchCtrl),itt='linear',ott='linear')
            cmds.setDrivenKeyframe('{}.visibility'.format(self.ctrlik[0]),cd = '{}.ik_fk_switch'.format(self.switchCtrl),itt='linear',ott='linear')
            cmds.setDrivenKeyframe('{}.visibility'.format(self.ctrlik[1]),cd = '{}.ik_fk_switch'.format(self.switchCtrl),itt='linear',ott='linear')
        cmds.setAttr('{}.ik_fk_switch'.format(self.switchCtrl),1)  #set the ik/fk switch attribute to 1
        for i in range(0, len(self.ikChain),1):
            cmds.setAttr('{}.{}W0'.format(const[i][0],self.ikChain[i]),0)  #do the same again but in reverse
            cmds.setAttr('{}.{}W1'.format(const[i][0],self.fkChain[i]),1)  #parent cosntraints and visibility flipped 
            cmds.setAttr('{}.visibility'.format(self.ctrlfk[0]),1)
            cmds.setAttr('{}.visibility'.format(self.ctrlfk[1]),1)
            cmds.setAttr('{}.visibility'.format(self.ctrlfk[2]),1)
            cmds.setAttr('{}.visibility'.format(self.ctrlik[0]),0)
            cmds.setAttr('{}.visibility'.format(self.ctrlik[1]),0)
            cmds.setDrivenKeyframe('{}.{}W0'.format(const[i][0],self.ikChain[i]),cd = '{}.ik_fk_switch'.format(self.switchCtrl),itt='linear',ott='linear')
            cmds.setDrivenKeyframe('{}.{}W1'.format(const[i][0],self.fkChain[i]),cd = '{}.ik_fk_switch'.format(self.switchCtrl),itt='linear',ott='linear')
            cmds.setDrivenKeyframe('{}.visibility'.format(self.ctrlfk[0]),cd = '{}.ik_fk_switch'.format(self.switchCtrl),itt='linear',ott='linear')
            cmds.setDrivenKeyframe('{}.visibility'.format(self.ctrlfk[1]),cd = '{}.ik_fk_switch'.format(self.switchCtrl),itt='linear',ott='linear')
            cmds.setDrivenKeyframe('{}.visibility'.format(self.ctrlfk[2]),cd = '{}.ik_fk_switch'.format(self.switchCtrl),itt='linear',ott='linear')
            cmds.setDrivenKeyframe('{}.visibility'.format(self.ctrlik[0]),cd = '{}.ik_fk_switch'.format(self.switchCtrl),itt='linear',ott='linear')
            cmds.setDrivenKeyframe('{}.visibility'.format(self.ctrlik[1]),cd = '{}.ik_fk_switch'.format(self.switchCtrl),itt='linear',ott='linear')
        cmds.select(clear=1)  #clear selection
        """ if we didn't set the animation type to linear earlier we could do it with this.
        for i in range(0, len(self.ikChain),1):
            crv01 = cmds.listConnections(const[i][0],t='animCurve')  #get the first set of anim curves created
            crv02 = cmds.listConnections(const[i][0],t='animCurve')  #get the second set of anim curves created
            cmds.selectKey(crv01,add=1,k=1,f= (0.0,1.0))  #select the specific key range 0,1
            cmds.selectKey(crv02,add=1,k=1,f= (0.0,1.0))
        cmds.keyTangent(itt='linear',ott='linear')  #set those keys to linear
        """
        cmds.select(cl=1)  #clear selection
        cmds.setAttr('{}.ik_fk_switch'.format(self.switchCtrl),0)  #swap ik/fk back to 0
class BuildRigs():
    """Build the rigs
    
    Functions to build the fit rig and spine rig
    """
    def __init__(self,charName):
        self.charName = charName
    def buildFitRig(self, rigName):
        """Builds the fit rig.
        
        Builds the fit rig that is later used to build the spine rig.
        
        Arguments:
            rigName {string} -- The rig name.
        Returns:
            *string -- Returns nodes needed to build the spine rig.
        """
        self.rigName = rigName  #rig name ('fit rig')
        _makeNodeInstance = MakeNodes()  #instance the make and edit classes
        _editNodeInstance = EditNodes()
        #-------------------------- crate the controlls, locators and groups needed for the fit rig ----------------------------#
        rootCtrl = _makeNodeInstance.circleCtrl(self.charName,'{}_root'.format(self.rigName),'ctrl',1,0,7,360)                  #
        hipLoc = _makeNodeInstance.createLoc(self.charName,'{}_hip'.format(self.rigName),'pivPoint_loc')                        #
        chestLoc = _makeNodeInstance.createLoc(self.charName,'{}_chest'.format(self.rigName),'pivPoint_loc')                    #
        hipFinderLoc = _makeNodeInstance.createLoc(self.charName,'{}_root'.format(self.rigName),'finder_loc')                   #
        chestFinderLoc = _makeNodeInstance.createLoc(self.charName,'{}_chest'.format(self.rigName),'finder_loc')                #
        chestFinderGrp = _makeNodeInstance.createGrp(self.charName,'{}_chestFinder'.format(self.rigName),'offset')              #
        hipFinderGrp = _makeNodeInstance.createGrp(self.charName,'{}_rootFinder'.format(self.rigName),'offset')                 #
        hipGrp = _makeNodeInstance.createGrp(self.charName,'{}_hip'.format(self.rigName),'offset')                              #
        chestGrp = _makeNodeInstance.createGrp(self.charName,'{}_chest'.format(self.rigName),'offset')                          #
        rootGrp = _makeNodeInstance.createGrp(self.charName,'{}_root'.format(self.rigName),'offset')                            #
        pivConstGrp = _makeNodeInstance.createGrp(self.charName,'{}_piv'.format(self.rigName),'const')                          #
        aimGuideGrp = _makeNodeInstance.createGrp(self.charName,'{}_aimGuide'.format(self.rigName),'offset')                    #
        hipChestLineCrvGrp = _makeNodeInstance.createGrp(self.charName,'{}_hipChestLineCrv'.format(self.rigName),'grp')         #
        hipCtrl = _makeNodeInstance.createCurve(self.charName,'sh02','{}_hip'.format(self.rigName),'ctrl')                      #
        chestCtrl = _makeNodeInstance.createCurve(self.charName,'sh02','{}_chest'.format(self.rigName),'ctrl')                  #
        hipChestLineCrv = _makeNodeInstance.createCurve(self.charName,'sh06','{}_spineLine'.format(self.rigName),'guide')       #
        aimGuide = _makeNodeInstance.createCurve(self.charName,'sh07','{}_spineArrow'.format(self.rigName),'guide')             #
        #-----------------------------------------------------------------------------------------------------------------------+
        hipChestLineCrv_cls_lwr = _editNodeInstance.clusterCrv(hipChestLineCrv,0,'lwr')  #create clusters on the curve
        hipChestLineCrv_cls_upr = _editNodeInstance.clusterCrv(hipChestLineCrv,1,'upr')
        _editNodeInstance.setRotateOrder(rootCtrl,1,0)  #set rotation order on root ctrl
        _editNodeInstance.centerWorld(hipChestLineCrv_cls_upr)  #center the cluster grp
        #--------------------------------------------- Create hierarchy for fit rig --------------------------------------------#
        _editNodeInstance.parentNodes(hipFinderLoc,hipFinderGrp)                                                                #
        _editNodeInstance.parentNodes(chestFinderLoc,chestFinderGrp)                                                            #
        _editNodeInstance.parentNodes(rootCtrl,rootGrp)                                                                         #
        _editNodeInstance.parentNodes(pivConstGrp,rootCtrl)                                                                     #
        _editNodeInstance.parentNodes(hipChestLineCrv_cls_lwr,hipFinderLoc)                                                     #
        _editNodeInstance.parentNodes(hipChestLineCrv_cls_upr,chestFinderLoc)                                                   #
        _editNodeInstance.parentNodes(hipLoc,hipCtrl)                                                                           #
        _editNodeInstance.parentNodes(hipCtrl,hipGrp)                                                                           #
        _editNodeInstance.parentNodes(hipGrp,rootCtrl)                                                                          #
        _editNodeInstance.parentNodes(chestLoc,chestCtrl)                                                                       #
        _editNodeInstance.parentNodes(chestCtrl,chestGrp)                                                                       #
        _editNodeInstance.parentNodes(aimGuide,aimGuideGrp)                                                                     #
        _editNodeInstance.parentNodes(hipChestLineCrv,hipChestLineCrvGrp)                                                       #
        _editNodeInstance.parentNodes(aimGuideGrp,pivConstGrp)                                                                  #
        _editNodeInstance.parentNodes(hipChestLineCrvGrp,pivConstGrp)                                                           #
        _editNodeInstance.parentNodes(chestGrp,pivConstGrp)                                                                     #
        _editNodeInstance.parentNodes(chestFinderGrp,chestCtrl)                                                                 #
        _editNodeInstance.parentNodes(hipFinderGrp,hipCtrl)                                                                     #
        #-----------------------------------------------------------------------------------------------------------------------#
        _editNodeInstance.xformNode(aimGuideGrp,['pass','pass','pass'],[90,90,'pass'],['pass','pass','pass'],0,0)  #position the aim guide grp
        _editNodeInstance.xformNode(chestGrp,[0,10,0],['pass','pass','pass'],['pass','pass','pass'],0,0)  #position the chest grp
        cmds.pointConstraint(hipLoc,aimGuideGrp,mo=0)  #point constraint the hip loc to the aim guide grp
        cmds.pointConstraint(chestLoc,aimGuideGrp,mo=0)  #point constraint the chest loc to theaim guide grp
        cmds.setAttr(hipChestLineCrvGrp + '.inheritsTransform',0)  #turn off the curve inherit transform attribute
        cmds.setAttr(hipLoc + '.visibility',0)  #set hip loc visibility to 0
        cmds.setAttr(chestLoc + '.visibility',0)  #set chest loc visibility to 0
        cmds.setAttr(hipChestLineCrv_cls_lwr + '.visibility',0)  #set curve clusters visibility to 0
        cmds.setAttr(hipChestLineCrv_cls_upr + '.visibility',0)
        #--------------------------------- lock and hide nodes ---------------------------------#
        _editNodeInstance.lockHideAll(hipGrp)                                                   #
        _editNodeInstance.lockHideAll(hipLoc)                                                   #
        _editNodeInstance.lockHideAll(aimGuideGrp)                                              #
        _editNodeInstance.lockHideAll(hipChestLineCrvGrp)                                       #
        _editNodeInstance.lockHideAll(chestGrp)                                                 #
        _editNodeInstance.lockHideAll(chestLoc)                                                 #
        _editNodeInstance.lockHideAll(hipChestLineCrv_cls_lwr)                                  #
        _editNodeInstance.lockHideAll(hipChestLineCrv_cls_upr)                                  #
        _editNodeInstance.lockHideAll(pivConstGrp)                                              #
        _editNodeInstance.lockHideAll(chestFinderGrp)                                           #
        _editNodeInstance.lockHideAll(hipFinderGrp)                                             #
        _editNodeInstance.lockHideSpecific(hipCtrl,[0,0,0],[1,1,1],[0,1,0],0)                   #
        _editNodeInstance.lockHideSpecific(chestCtrl,[0,0,0],[1,1,1],[0,1,0],0)                 #
        _editNodeInstance.lockHideSpecific(rootCtrl,[0,0,0],[0,0,0],[0,0,0],0)                  #
        _editNodeInstance.lockHideSpecific(rootGrp,[1,1,1],[1,1,1],[1,1,1],0)                   #
        _editNodeInstance.lockHideSpecific(chestFinderLoc,[0,0,0],[1,1,1],[1,1,1],0)            #
        _editNodeInstance.lockHideSpecific(hipFinderLoc,[0,0,0],[1,1,1],[1,1,1],0)              #
        _editNodeInstance.lockHideSpecific(aimGuide,[1,1,1],[1,1,1],[1,1,1],0)                  #
        _editNodeInstance.lockHideSpecific(hipChestLineCrv,[1,1,1],[1,1,1],[1,1,1],0)           #
        #------------------------------ set node color overrides -------------------------------#
        _editNodeInstance.setCol(hipCtrl, 'yellow')                                             #
        _editNodeInstance.setCol(chestCtrl, 'yellow')                                           #
        _editNodeInstance.setCol(aimGuide, 'red')                                               #
        _editNodeInstance.setCol(hipChestLineCrv, 'red')                                        #
        _editNodeInstance.setCol(rootCtrl,'white')                                              #
        _editNodeInstance.setCol(chestFinderLoc,'pink')                                         #
        _editNodeInstance.setCol(hipFinderLoc,'pink')                                           #
        #---------------------------------------------------------------------------------------#
        cmds.connectAttr(rootCtrl + '.scaleY',rootCtrl + '.scaleX')  #connect root ctrl scale y to its scale z and x
        cmds.connectAttr(rootCtrl + '.scaleY',rootCtrl + '.scaleZ')
        cmds.setAttr(rootCtrl + '.sx',lock=1,keyable=0,channelBox = 0)  #lock its scale x and z
        cmds.setAttr(rootCtrl + '.sz',lock=1,keyable=0,channelBox = 0)
        return(hipCtrl,chestCtrl,hipLoc,chestLoc,rootCtrl,hipFinderLoc,chestFinderLoc,hipChestLineCrv,rootGrp)  #return nodes to be used to create the spine rig
    def buildSpineRig(self,rigName,data,jointAmount):
        """Build spine rig.
        
        Uses fit rig placements to build the spine rig.
        
        Arguments:
            rigName {string} -- The name of the rig.
            data {list} -- The nodes created by the fit rig used to build the spine rig.
            jointAmount {int} -- The amount of joints created for the spine rig.
        """
        self.rigName = rigName
        self.data = data
        self.jointAmount = jointAmount
        _makeNodeInstance = MakeNodes()  #instance the make and edit classes
        _editNodeInstance = EditNodes()
        #----------------------------------------- crate the controlls, locators and groups needed for the fit rig -----------------------------------------#
        hipCtrl = _makeNodeInstance.createCurve(self.charName,'sh08','{}_hip'.format(self.rigName),'ctrl')                                                  #
        chestCtrl = _makeNodeInstance.createCurve(self.charName,'sh08','{}_chest'.format(self.rigName),'ctrl')                                              #
        fkCtrl01 = _makeNodeInstance.circleCtrl(self.charName,'{}_spine'.format(self.rigName),'FK_ctrl_01',2,.125,4,360)                                    #
        fkCtrl02 = _makeNodeInstance.circleCtrl(self.charName,'{}_spine'.format(self.rigName),'FK_ctrl_02',2,.125,4,360)                                    #
        fkCtrl03 = _makeNodeInstance.circleCtrl(self.charName,'{}_spine'.format(self.rigName),'FK_ctrl_03',2,.125,4,360)                                    #
        indHipCtrlTempgrp = _makeNodeInstance.createGrp(self.charName,'{}_ind_hip_temp_grp'.format(self.rigName),'replace_with_your_indipendent_hip_ctrl')  #
        cogGrp = _makeNodeInstance.createGrp(self.charName,'{}_cog'.format(self.rigName),'replace_with_your_cog_ctrl')                                      #
        hipOffsetGrp = _makeNodeInstance.createGrp(self.charName,'{}_hip'.format(self.rigName),'offset')                                                    #
        chestOffsetGrp = _makeNodeInstance.createGrp(self.charName,'{}_chest'.format(self.rigName),'offset')                                                #
        chestCtrlGrp = _makeNodeInstance.createGrp(self.charName,'{}_chest'.format(self.rigName),'ctrl_grp')                                                #
        ikJntChainOffsetGrp = _makeNodeInstance.createGrp(self.charName,'{}_IK_jnt_chain'.format(self.rigName),'offset')                                    #
        fkJntChainOffsetGrp = _makeNodeInstance.createGrp(self.charName,'{}_FK_jnt_chain'.format(self.rigName),'offset')                                    #
        resultJntChainOffsetGrp = _makeNodeInstance.createGrp(self.charName,'{}_result_jnt_chain'.format(self.rigName),'offset')                            #
        ikSplineLwrBndJnt = _makeNodeInstance.createGrp(self.charName,'{}_spline_crv_lwr_bnd_jnt'.format(self.rigName),'offset')                            #
        ikSplineUprBndJnt = _makeNodeInstance.createGrp(self.charName,'{}_spline_crv_upr_bnd_jnt'.format(self.rigName),'offset')                            #
        doNotTouchGrp = _makeNodeInstance.createGrp(self.charName,'{}_spine_do_not_touch'.format(self.rigName),'grp')                                       #
        fk01OffsetGrp = _makeNodeInstance.createGrp(self.charName,'{}_FK_ctrl_01'.format(self.rigName),'offset')                                            #
        fk02OffsetGrp = _makeNodeInstance.createGrp(self.charName,'{}_FK_ctrl_02'.format(self.rigName),'offset')                                            #
        fk03OffsetGrp = _makeNodeInstance.createGrp(self.charName,'{}_FK_ctrl_03'.format(self.rigName),'offset')                                            #
        fk01CtrlGrp = _makeNodeInstance.createGrp(self.charName,'{}_fk_ctrl_01'.format(self.rigName),'ctrl_grp')                                            #
        fk02CtrlGrp = _makeNodeInstance.createGrp(self.charName,'{}_fk_ctrl_02'.format(self.rigName),'ctrl_grp')                                            #
        fk03CtrlGrp = _makeNodeInstance.createGrp(self.charName,'{}_fk_ctrl_03'.format(self.rigName),'ctrl_grp')                                            #
        #---------------------------------------------------------------------------------------------------------------------------------------------------#
        cmds.setAttr(doNotTouchGrp + '.inheritsTransform',0)  #turn off inherit transform attribute on the do not touch grp
        #---------------- Set node color rotation order ----------------#
        _editNodeInstance.setRotateOrder(hipCtrl,3,0)                   #
        _editNodeInstance.setRotateOrder(chestCtrl,3,0)                 #
        _editNodeInstance.setRotateOrder(chestCtrlGrp,3,0)              #
        _editNodeInstance.setRotateOrder(fkCtrl01,3,0)                  #
        _editNodeInstance.setRotateOrder(fkCtrl02,3,0)                  #
        _editNodeInstance.setRotateOrder(fkCtrl03,3,0)                  #
        _editNodeInstance.setRotateOrder(indHipCtrlTempgrp,3,0)         #
        _editNodeInstance.setRotateOrder(fk01CtrlGrp,3,0)               #
        _editNodeInstance.setRotateOrder(fk02CtrlGrp,3,0)               #
        _editNodeInstance.setRotateOrder(fk03CtrlGrp,3,0)               #
        #---------------------- create hierarchy -----------------------#
        _editNodeInstance.parentNodes(hipCtrl,hipOffsetGrp)             #
        _editNodeInstance.parentNodes(chestCtrlGrp,chestOffsetGrp)      #
        _editNodeInstance.parentNodes(chestCtrl,chestCtrlGrp)           #
        _editNodeInstance.parentNodes(fkCtrl01,fk01CtrlGrp)             #
        _editNodeInstance.parentNodes(fkCtrl02,fk02CtrlGrp)             #
        _editNodeInstance.parentNodes(fkCtrl03,fk03CtrlGrp)             #
        _editNodeInstance.parentNodes(indHipCtrlTempgrp,cogGrp)         #
        #------------------- find node positions -----------------------#
        hipMatch = _editNodeInstance.matchNodes(self.data[5])           #
        chestMatch = _editNodeInstance.matchNodes(self.data[6])         #
        rootPivMatch = _editNodeInstance.matchNodes(self.data[0])       #
        chestPivMatch = _editNodeInstance.matchNodes(self.data[1])      #
        #------------------------------------------ move nodes using xform -----------------------------------------#
        _editNodeInstance.xformNode(hipOffsetGrp,rootPivMatch[0],rootPivMatch[1],rootPivMatch[2],0,0)               #
        _editNodeInstance.xformNode(chestOffsetGrp,chestPivMatch[0],chestPivMatch[1],chestPivMatch[2],0,0)          #
        _editNodeInstance.xformNode(ikJntChainOffsetGrp,hipMatch[0],hipMatch[1],['pass','pass','pass'],0,0)         #
        _editNodeInstance.xformNode(fkJntChainOffsetGrp,hipMatch[0],hipMatch[1],['pass','pass','pass'],0,0)         #
        _editNodeInstance.xformNode(resultJntChainOffsetGrp,hipMatch[0],hipMatch[1],['pass','pass','pass'],0,0)     #
        _editNodeInstance.xformNode(ikSplineLwrBndJnt,hipMatch[0],hipMatch[1],['pass','pass','pass'],0,0)           #
        _editNodeInstance.xformNode(ikSplineUprBndJnt,chestMatch[0],chestMatch[1],['pass','pass','pass'],0,0)       #
        _editNodeInstance.xformNode(cogGrp,hipMatch[0],hipMatch[1],['pass','pass','pass'],0,0)                      #
        #-----------------------------------------------------------------------------------------------------------#
        ikJointChain = _makeNodeInstance.createChain(self.charName,'joint',hipMatch,chestMatch,self.jointAmount,.5,'spine','ik_jnt')  #create the ik chain
        fkJointChain = _makeNodeInstance.createChain(self.charName,'joint',hipMatch,chestMatch,self.jointAmount,.1,'spine','fk_jnt')  #create the fk chain
        resultJointChain = _makeNodeInstance.createChain(self.charName,'joint',hipMatch,chestMatch,self.jointAmount,.3,'spine','result_jnt')  #create the result bind chain
        ikSplineBndJnts = _makeNodeInstance.createChain(self.charName,'joint',hipMatch,chestMatch,0,.2,'bind','ik_jnt')  #create a chain to extract skin weights from for fk control setup
        #----------- convert rotation to orient ------------#
        _editNodeInstance.rotToOrient(ikJointChain)         #
        _editNodeInstance.rotToOrient(fkJointChain)         #
        _editNodeInstance.rotToOrient(resultJointChain)     #
        _editNodeInstance.rotToOrient(ikSplineBndJnts)      #
        #--------- parent chain nodes into a chain ---------#
        _editNodeInstance.parentChain(ikJointChain)         #
        _editNodeInstance.parentChain(fkJointChain)         #
        _editNodeInstance.parentChain(resultJointChain)     #
        #---------------------------------------------------#
        splineCrvGuide = _makeNodeInstance.createChain(self.charName,'loc',hipMatch,chestMatch,4,.1,'spline','guide_loc')  #create a chain of locs to guide the creation of the ik spline curve
        ikSpline = _makeNodeInstance.createIkSpline(self.charName,ikJointChain,ikSplineBndJnts[0],ikSplineBndJnts[1],hipCtrl,chestCtrl,splineCrvGuide)  #create the ik spline
        fkCtrlGuide = _makeNodeInstance.createChain(self.charName,'loc',hipMatch,chestMatch,3,.1,'FK_ctrl','guide_loc')  #create a chain of locs to guide the positioning of the fk controllers
        fk01Match = _editNodeInstance.matchNodes(fkCtrlGuide[0])  #find the positions of the locs
        fk02Match = _editNodeInstance.matchNodes(fkCtrlGuide[1])
        fk03Match = _editNodeInstance.matchNodes(fkCtrlGuide[2])
        cmds.setAttr(ikSpline[0] + '.inheritsTransform',0)  #turn off inherit transforms on the ik spline curve
        #------------------------------------------ move nodes using xform ---------------------------------#
        _editNodeInstance.xformNode(fk01OffsetGrp,fk01Match[0],fk01Match[1],['pass','pass','pass'],0,0)     #
        _editNodeInstance.xformNode(fk02OffsetGrp,fk01Match[0],fk01Match[1],['pass','pass','pass'],0,0)     #
        _editNodeInstance.xformNode(fk03OffsetGrp,fk02Match[0],fk02Match[1],['pass','pass','pass'],0,0)     #
        _editNodeInstance.xformNode(fk01CtrlGrp,fk01Match[0],fk01Match[1],['pass','pass','pass'],0,0)       #
        _editNodeInstance.xformNode(fk02CtrlGrp,fk02Match[0],fk02Match[1],['pass','pass','pass'],0,0)       #
        _editNodeInstance.xformNode(fk03CtrlGrp,fk03Match[0],fk03Match[1],['pass','pass','pass'],0,0)       #
        #---------------------------------------------------------------------------------------------------#
        for i in fkCtrlGuide: #delete the nodes create to guide the creation of the fk controllers
            cmds.delete(i)
        _editNodeInstance.parentNodes(doNotTouchGrp,indHipCtrlTempgrp)  #parent do not touch group under the hip temp grp node
        _editNodeInstance.xformNode(doNotTouchGrp,hipMatch[0],hipMatch[1],['pass','pass','pass'],0,0)  #move the do not touch group
        #------------------------------ create hierarchy -------------------------------#
        _editNodeInstance.parentNodes(ikJointChain[0],ikJntChainOffsetGrp)              #
        _editNodeInstance.parentNodes(fkJointChain[0],fkJntChainOffsetGrp)              #
        _editNodeInstance.parentNodes(resultJointChain[0],resultJntChainOffsetGrp)      #
        _editNodeInstance.parentNodes(ikSplineBndJnts[0],ikSplineLwrBndJnt)             #
        _editNodeInstance.parentNodes(ikSplineBndJnts[1],ikSplineUprBndJnt)             #
        _editNodeInstance.parentNodes(ikSpline[0],doNotTouchGrp)                        #
        _editNodeInstance.parentNodes(ikSpline[1],doNotTouchGrp)                        #
        _editNodeInstance.parentNodes(fk01CtrlGrp,fk01OffsetGrp)                        #
        _editNodeInstance.parentNodes(fk02CtrlGrp,fk02OffsetGrp)                        #
        _editNodeInstance.parentNodes(fk03CtrlGrp,fk03OffsetGrp)                        #
        #-------------------------------------------------------------------------------#
        fkChainGuide = _makeNodeInstance.createChain(self.charName,'joint',hipMatch,chestMatch,3,.1,'fk_temp_bind','guide')  #temp fk join chain to help find the parent constraint values to use with the fk controllers
        _editNodeInstance.parentFk(fkJointChain,[fkCtrl01,fkCtrl02,fkCtrl03],fkChainGuide,fk02CtrlGrp,fk03CtrlGrp)  #parent the fk controllers to fk joints
        for i in fkChainGuide:  #delete the fk chain guide we just made
            cmds.delete(i)
        _editNodeInstance.ikfk_switch(ikJointChain,fkJointChain,resultJointChain,cogGrp,[fkCtrl01,fkCtrl02,fkCtrl03],[hipCtrl,chestCtrl])  #create the ik/fk switch
        _editNodeInstance.parentNodes(ikSplineLwrBndJnt,doNotTouchGrp)  #parent the ik skin joints under the do not touch group
        _editNodeInstance.parentNodes(ikSplineUprBndJnt,doNotTouchGrp)
        #----------- set node visibility attributes ------------#
        cmds.setAttr(doNotTouchGrp + '.visibility',1)           #
        cmds.setAttr(ikSplineLwrBndJnt + '.visibility',1)       #
        cmds.setAttr(ikSplineUprBndJnt + '.visibility',1)       #
        cmds.setAttr(ikSplineBndJnts[0] + '.visibility',0)      #
        cmds.setAttr(ikSplineBndJnts[1] + '.visibility',0)      #
        cmds.setAttr(ikSpline[0] + '.visibility',0)             #
        cmds.setAttr(ikSpline[1] + '.visibility',0)             #
        for i in range(0, len(ikJointChain),1):                 #
            cmds.setAttr(ikJointChain[i] + '.visibility',0)     #
        for i in range(0, len(fkJointChain),1):                 #
            cmds.setAttr(fkJointChain[i] + '.visibility',0)     #
        #-------------------------- create hierarchy ---------------------------#
        _editNodeInstance.parentNodes(ikJntChainOffsetGrp,indHipCtrlTempgrp)    #
        _editNodeInstance.parentNodes(fkJntChainOffsetGrp,indHipCtrlTempgrp)    #
        _editNodeInstance.parentNodes(fk01OffsetGrp,indHipCtrlTempgrp)          #
        _editNodeInstance.parentNodes(fk02OffsetGrp,indHipCtrlTempgrp)          #
        _editNodeInstance.parentNodes(fk03OffsetGrp,indHipCtrlTempgrp)          #
        _editNodeInstance.parentNodes(hipOffsetGrp,indHipCtrlTempgrp)           #
        _editNodeInstance.parentNodes(chestOffsetGrp,cogGrp)                    #
        #------------------------- lock and hide nodes -------------------------#
        _editNodeInstance.lockHideAll(ikSpline[0])                              #
        _editNodeInstance.lockHideAll(doNotTouchGrp)                            #
        _editNodeInstance.lockHideAll(ikSplineLwrBndJnt)                        #
        _editNodeInstance.lockHideAll(ikSplineUprBndJnt)                        #
        _editNodeInstance.lockHideAll(doNotTouchGrp)                            #
        _editNodeInstance.lockHideAll(doNotTouchGrp)                            #
        _editNodeInstance.lockHideAll(ikJntChainOffsetGrp)                      #
        _editNodeInstance.lockHideAll(fkJntChainOffsetGrp)                      #
        _editNodeInstance.lockHideAll(resultJntChainOffsetGrp)                  #
        _editNodeInstance.lockHideAll(chestOffsetGrp)                           #
        _editNodeInstance.lockHideAll(chestCtrlGrp)                             #
        _editNodeInstance.lockHideAll(hipOffsetGrp)                             #
        _editNodeInstance.lockHideAll(fk01OffsetGrp)                            #
        _editNodeInstance.lockHideAll(fk01CtrlGrp)                              #
        _editNodeInstance.lockHideAll(fk02OffsetGrp)                            #
        _editNodeInstance.lockHideAll(fk02CtrlGrp)                              #
        _editNodeInstance.lockHideAll(fk03OffsetGrp)                            #
        _editNodeInstance.lockHideAll(fk03CtrlGrp)                              #
        _editNodeInstance.lockHideSpecific(fkCtrl01,[1,1,1],[0,0,0],[1,1,1],1)  #
        _editNodeInstance.lockHideSpecific(fkCtrl02,[1,1,1],[0,0,0],[1,1,1],1)  #
        _editNodeInstance.lockHideSpecific(fkCtrl03,[1,1,1],[0,0,0],[1,1,1],1)  #
        _editNodeInstance.lockHideSpecific(chestCtrl,[0,0,0],[0,0,0],[1,1,1],1) #
        _editNodeInstance.lockHideSpecific(hipCtrl,[0,0,0],[0,0,0],[1,1,1],1)   #
        #------------------------- set color overrides -------------------------#
        _editNodeInstance.setCol(chestCtrl,'yellow')                            #
        _editNodeInstance.setCol(hipCtrl,'yellow')                              #
        _editNodeInstance.setCol(fkCtrl01,'rose')                               #
        _editNodeInstance.setCol(fkCtrl02,'rose')                               #
        _editNodeInstance.setCol(fkCtrl03,'rose')                               #
        #-----------------------------------------------------------------------#
        cmds.delete(data[8])  #delete the fit rig
def maya_main_window():
    """gets the main window in maya
    
    returns the main window for maya so we can parent our gui to it
    
    Returns:
        class -- Maya main window
    """
    main_window_ptr=OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QWidget)  #return mayas main window
class Window(QDialog):
    def __init__(self, parent=maya_main_window()):
        """Build the GUI.
        
        A gui with a build fit button, amount of joints text field, and a build spine rig button.
        """
        super(Window, self).__init__(parent)  #parent the gui to mayas main window so it stays ontop
        self.runName = 0
        self.amount = 0
        self.runFit = 0
        res = QApplication.desktop().screenGeometry()  #get desktop size
        screenWidth, screenHeight, windowWidth, windowHeight = res.width(), res.height(), 400, 100  #position in middle of screen with 400,100 res
        self.setGeometry(screenWidth/2 - windowWidth, screenHeight/2 - windowHeight, windowWidth, windowHeight)
        self.characterName = QLineEdit('Enter Characters Name')  #character name input field
        self.fitRigBtn = QPushButton("Create Fit Rig")  #create fit rig button
        self.amountInput = QLineEdit('Amount Of Joints')  #amount of joints input field
        self.rigBtn = QPushButton("Create Rig")  #create rig button
        layout = QVBoxLayout()  #layout
        layout.addWidget(self.characterName)
        layout.addWidget(self.fitRigBtn)
        layout.addWidget(self.amountInput)
        layout.addWidget(self.rigBtn)
        self.setLayout(layout)
        self.fitRigBtn.clicked.connect(self.fitRig)  #connect buttons to functions
        self.rigBtn.clicked.connect(self.rig)
        self.amountInput.textChanged.connect(self.jntAmount)
        self.characterName.textChanged.connect(self.charName)
    def charName(self):
        """Character name input field.
        
        Get the characters name.
        """
        sender = self.sender()
        self.characterName = sender.text()  #get the text entered into the field
        try:
            (int(self.characterName))  #see if we can convert the first character to int, we dont want this
            self.runName = 0  #dont allow the fit rig to be built
            #self.characterName.setStyleSheet("color: red;")  #change field color to red
        except ValueError:
            self.runName = 1  #allow the fit rig to be built
    def jntAmount(self):
        """Joint amount input field.
        
        Get the amount text field.
        """
        sender = self.sender()
        self.amount = int(sender.text())  #get the text entered into the field and try to convert to int, otherwise just use 0 as defaulted above
    def fitRig(self):
        """Build Fit Rig.

        Command ran to build fit rig and send data to spine rig function.

        """
        if self.runName == 1:  #if a character name is added
            self._rig = BuildRigs(self.characterName)  #build the fit rig using that name
            self.fitRigBuild = self._rig.buildFitRig('fitRig')
            self.runFit = 1  #allow the spine rig to be built
        else:
            self.runFit = 0  #dont allow the spine rig to be built
    def rig(self):
        """Build spine rig.
        
        Command ran to build spine rig.
        """
        if self.runFit == 1:  #if the fit rig was built
            try:
                self._rig.buildSpineRig('mainRig',self.fitRigBuild,self.amount)  #build the spine rig
                self.runFit = 0  #since fit rig is deleted we disable the ability to build more spine rigs until its created again
            except TypeError:
                pass
        else:
            pass
if __name__ == '__main__':
    if not QApplication.instance():  #Create the Qt Application
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    GUI = Window()  #Create and show the form
    GUI.show()