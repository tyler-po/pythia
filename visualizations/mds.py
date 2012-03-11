'''
Created on 22 Jan 2012

@author: george
'''
import random, math
import pylab#!@UnresolvedImport 
from analysis.clustering.algorithms import pearson
from PIL import Image, ImageDraw #!@UnresolvedImport 
from tools.orange_utils import construct_distance_matrix, orange_mds
import matplotlib.cm as cm#!@UnresolvedImport 

class MDS(object):
    '''
    Uses multidimensional scaling (MDS) to visualize clusters. 
    For more info see: http://orange.biolab.si/doc/modules/orngMDS.htm
    or http://orange.biolab.si/doc/reference/Orange.projection.mds/#Orange.projection.mds.MDS
    '''
    def __init__(self, data):
        '''
        Constructor
        '''
        self.data = data
    
    def plot(self, classes_list=None, class_col_name=None, color=None):
        '''
        Projects the data points using MDS.
        Optionally we can input with the classes names in order to 
        plot the points painted according to their class.
        '''
        distance = construct_distance_matrix(self.data)
        mds = orange_mds(distance)
        
        labelled = classes_list != None and class_col_name != None
        colors = ["red", "yellow", "blue"]
        # Construct points (x, y, instanceClass)
        points = []
        for (i, d) in enumerate(self.data):
            if labelled:
                points.append((mds.points[i][0], mds.points[i][1], d.get_metas(str)[class_col_name].value))
            else:
                points.append((mds.points[i][0], mds.points[i][1], 0))

        # Paint each class separately
        if labelled:
            for c in classes_list:
                sel = filter(lambda x: x[-1] == str(c), points)
                x = [s[0] for s in sel]
                y = [s[1] for s in sel]
                if len(classes_list) > 1:
                    pylab.scatter(x, y, c=cm.jet(float(c)/(len(classes_list)-1)))
                else:
                    pylab.scatter(x, y, c=cm.jet(1))
        else:
            sel = filter(lambda x: x[-1] == 0, points)
            x = [s[0] for s in sel]
            y = [s[1] for s in sel]
            pylab.scatter(x, y, c=colors[0])

        pylab.show()
        
class Cluster2DPlot(object):
    '''
    Uses multidimensional scaling to visualize clusters in 2D. Code adopted from
    Programming Collective Intelligence.
    '''

    def __init__(self, data, labels, filename, similarity=pearson, rate=0.01):
        '''
        Constructor
        '''
        self.data = data
        self.similarity=similarity
        self.rate = rate
        self.labels = labels
        self.filename = filename
    
    def draw(self):
        '''
        Draws a 2D plot of the clusters.
        '''
        self._scale_down()
        img=Image.new('RGB',(2000,2000),(255,255,255))
        draw=ImageDraw.Draw(img)
        for i in range(len(self.data)):
            x=(self.data[i][0]+0.5)*1000
            y=(self.data[i][1]+0.5)*1000
            draw.content((x,y),self.labels[i],(0,0,0))
        img.save(self.filename,'JPEG')
    
    def _scale_down(self):
        '''
        Performs multidimensional scaling.
        '''
        n=len(self.data)

        # The real distances between every pair of items
        realdist=[[self.similarity(self.data[i],self.data[j]) for j in range(n)] 
             for i in range(0,n)]
        
        # Randomly initialize the starting points of the locations in 2D
        loc=[[random.random(),random.random()] for i in range(n)]
        fakedist=[[0.0 for j in range(n)] for i in range(n)]
        
        lasterror=None
        for m in range(0,1000):
            # Find projected distances
            for i in range(n):
                for j in range(n):
                    fakedist[i][j]=math.sqrt(sum([pow(loc[i][x]-loc[j][x],2) 
                                       for x in range(len(loc[i]))]))
        
            # Move points
            grad=[[0.0,0.0] for i in range(n)]
          
            totalerror=0
            for k in range(n):
                for j in range(n):
                    if j==k: continue
                    # The error is percent difference between the distances
                    errorterm=(fakedist[j][k]-realdist[j][k])/realdist[j][k]
              
                    # Each point needs to be moved away from or towards the other
                    # point in proportion to how much error it has
                    grad[k][0]+=((loc[k][0]-loc[j][0])/fakedist[j][k])*errorterm
                    grad[k][1]+=((loc[k][1]-loc[j][1])/fakedist[j][k])*errorterm
        
                    # Keep track of the total error
                    totalerror+=abs(errorterm)
        
            # If the answer got worse by moving the points, we are done
            if lasterror and lasterror<totalerror: break
            lasterror=totalerror
          
            # Move each of the points by the learning rate times the gradient
            for k in range(n):
                loc[k][0] -= self.rate*grad[k][0]
                loc[k][1] -= self.rate*grad[k][1]
        
        return loc