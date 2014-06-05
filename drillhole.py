'''
copyright 2014 Exequiel Sepulveda

Free permission to copy, adapt, modify 

'''
import numpy as np
import csv
import math

class Collar_Record(object):
    '''Collar object
    The main attributes are hole identification, coordinate and total depth
    '''
    def __init__(self,holeId,coordinate,depth):
        #basic attributes
        self.holeId = holeId
        self.coordinate = np.array(coordinate)
        self.depth =  depth
        
        #validation attributes
        self.times =  0
        self.additional_records = []
        self.surveys = []
        self.data = []

        self.invalid_surveys = []
        self.invalid_data = []
        
    def validate(self):
        #data
        idx = []
        for i,dat in enumerate(self.data):
            dat.validate()
            if not dat.is_valid:
                idx += [i]
                self.invalid_data += [dat]
                
        j = 0
        while len(idx) > 0:
            i = idx.pop(0)
            self.data.pop(i-j)
            j += 1

        #sort by depth
        self.data.sort(key=lambda x: x.depth)
        
        #survey
        idx = []
        for i,survey in enumerate(self.surveys):
            survey.validate()
            if not survey.is_valid:
                idx += [i]
                self.invalid_surveys += [survey]

        j = 0
        while len(idx) > 0:
            i = idx.pop(0)
            self.surveys.pop(i-j)
            j += 1
            
        if len(self.surveys) > 1:
            #fix surveys without final depth. Complete until collar total depth
            if self.last_depth() is not None:
                new_survey = Survey_Record(self.depth,self.surveys[-1].azimuth_degree,self.surveys[-1].dip_degree)
                new_survey.validate()
                self.surveys += [new_survey]

        #sort by depth
        self.surveys.sort(key=lambda survey: survey.depth)

        problem = False
        if len(self.additional_records) > 0:
            problem = True
            
        if len(self.invalid_surveys) > 0:
            problem = True
    
        if len(self.invalid_data) > 0:
            problem = True

        if len(self.surveys) < 2:
            problem = True

        if len(self.data) < 1:
            problem = True
            
        return not problem

    def last_depth(self):
        #try to find discontinuties in surveys
        n = len(self.surveys)
        last_depth = self.surveys[-1].depth
        if math.fabs(last_depth - self.depth) > 0.00001:
            return last_depth
        
        return None
        
    def __str__(self):
        return str(self.__dict__)        

class Survey_Record(object):
    '''Survey object
    The main attributes are starting depth, azimuth and dip (both are in degrees)
    '''
    def __init__(self,depth,azimuth,dip):
        self.depth = depth
        self.azimuth_degree = azimuth
        self.dip_degree =  dip
        self.length = 0
            
    def project(self,large,initial_point = None):
        #given a distance return the relative coordinate 
        ret = self.vector * large
        if initial_point is not None:
            ret = initial_point + ret
            
        return ret
        
    def ending_point(self):
        return self.project(self.length)
        
        
    def validate(self):
        try:
            self.depth = float(self.depth)
            self.azimuth_degree = float(self.azimuth_degree)
            self.dip_degree = float(self.dip_degree)

            self.azm = math.radians(90.0-self.azimuth_degree)
            self.dip = math.radians(-self.dip_degree)

            self.start_coordinate = None
            self.end_coordinate = None

            #for projection
            aux = math.cos(self.dip)
            a = math.sin(self.azm) * aux
            b = math.cos(self.azm) * aux
            c = math.sin(self.dip)       
            self.vector = np.array([a,b,c])


            self.is_valid = True
            
        except Exception as e:
            self.is_valid = False
            #print self.depth,self.azimuth_degree,self.dip_degree,e
        #self.size = depth_end - depth 
        
    def __str__(self):
        return str(self.__dict__)        
        
class Assay_Record(object):
    '''Assay object
    The main attributes are starting depth, ending depth and values (values are untouched)
    '''
    def __init__(self,depth,depth_end,values=None):
        self.depth = depth
        self.depth_end = depth_end
        self.values = values
        
    def validate(self):
        try:
            self.depth = float(self.depth)
            self.depth_end = float(self.depth_end)
            self.length = self.depth_end - self.depth
            self.is_valid = True
            
        except:
            self.is_valid = False
            
        return self.is_valid

    def __str__(self):
        return str(self.__dict__)

class Projection(object):
    '''Class utility
    Useful to calculate projection given azimuth and dip
    '''
    def __init__(self,azimuth,dip):
        self.azm = math.radians(90.0-azimuth)
        self.dip = math.radians(dip)

        aux = math.cos(dip)
        a = math.sin(self.azm) * aux
        b = math.cos(self.azm) * aux
        c = math.sin(dip)
        
        self.vector = np.array([a,b,c])

    def project(self,large,initialPoint = None):
        ret = self.vector * large
        if initialPoint is not None:
            ret = initialPoint + ret
            
        return ret

def fix_coordinates_composites(surveys, composites,log=False):
    '''According to different cases between a survey and a composite, fill starting and ending coordinates of composite projected into survey.
    Surveys and composites have to be ordered according depth
    '''
    n = len(surveys)
    m = len(composites)
    
    if log:
        print n,m
    
    i = 0 #i goes through surveys
    j = 0 #j goes through composites
    
    
    while i < n and j < m:
        #print i,j,
        survey = surveys[i]
        composite = composites[j]

        #print survey,

        sc = segment_case(survey.depth,survey.length,composite.depth,composite.length)
        if log:
            print i,j,sc,survey.depth,survey.length,composite.depth,composite.length

        #print sc,

        if sc == 1:
            composite.start_coordinate = survey.project(composite.depth - survey.depth,survey.start_coordinate)
            i += 1
        elif sc == 2: 
            composite.start_coordinate = survey.project(composite.depth - survey.depth,survey.start_coordinate)
            composite.end_coordinate = survey.end_coordinate
            i += 1
            j += 1
        elif sc == 3: 
            composite.start_coordinate = survey.project(composite.depth - survey.depth,survey.start_coordinate)
            composite.end_coordinate = survey.project(composite.length + (composite.depth - survey.depth),survey.start_coordinate)
            j += 1
        elif sc == 4:
            composite.start_coordinate = survey.start_coordinate
            i += 1
        elif sc == 5:
            composite.start_coordinate = survey.start_coordinate
            composite.end_coordinate = survey.project(composite.length + (composite.depth - survey.depth),survey.start_coordinate) #survey.end_coordinate
            j += 1
            i += 1
        elif sc == 6:
            composite.start_coordinate = survey.start_coordinate
            composite.end_coordinate = survey.project(composite.length,survey.start_coordinate)
            j += 1
        elif sc == 7:
            i += 1
        elif sc == 8:
            composite.end_coordinate = survey.end_coordinate
            j += 1
            i += 1
        elif sc == 9:
            composite.end_coordinate = survey.project(composite.length + (composite.depth - survey.depth),survey.start_coordinate)
            j += 1
        elif sc == 10:
            i += 1
        elif sc == 11:
            j += 1

    return composites
    
def segment_case(s1_depth,s1_length,s2_depth,s2_length):
    '''Determine which case is according  two segments s1 and s2. Consult the cases in jpg case documentation
    '''
    if (s1_depth + s1_length) < s2_depth: 
        return 10
    
    if s1_depth < s2_depth and (s1_depth + s1_length) < (s2_depth + s2_length): 
        return 1
    elif s1_depth < s2_depth and (s1_depth + s1_length) == (s2_depth + s2_length):
        return 2
    elif s1_depth < s2_depth and (s1_depth + s1_length) > (s2_depth + s2_length): 
        return 3
    elif s1_depth == s2_depth and (s1_depth + s1_length) < (s2_depth + s2_length):
        return 4
    elif s1_depth == s2_depth and (s1_depth + s1_length) == (s2_depth + s2_length):
        return 5
    elif s1_depth == s2_depth and (s1_depth + s1_length) > (s2_depth + s2_length):
        return 6
    elif s1_depth > s2_depth and (s1_depth + s1_length) < (s2_depth + s2_length): 
        return 7
    elif s1_depth > s2_depth and (s1_depth + s1_length) == (s2_depth + s2_length):
        return 8
    elif s1_depth > s2_depth and (s1_depth + s1_length) > (s2_depth + s2_length):
        return 9
    else:
        return 11


def composite(collar_filename,survey_filename,data_filename,header=True,delimiter="\t"):
    collars = dict()

    isolated_surveys = []
    isolated_data = []

    reader_collar = csv.reader(open(collar_filename,"r"),delimiter=delimiter)
    reader_survey = csv.reader(open(survey_filename,"r"),delimiter=delimiter)
    reader_data = csv.reader(open(data_filename,"r"),delimiter=delimiter)
    
    if header:
        reader_collar.next()
        reader_survey.next()
        reader_data.next()


    for row in reader_collar:
        holeId = row[0]
        x = row[1]
        y = row[2]
        z = row[3]
        depth = row[4]
        
        try:
            x = float(x)
            y = float(y)
            z = float(z)
            depth = float(depth)
            
            collar = Collar_Record(holeId,[x,y,z],depth)
            if holeId in collars:
                collars[holeId].additional_records += [collar]
            else:
                collars[holeId] = collar
        except:
            print holeId,"invalid collar data"
        

    for row in reader_survey:
        holeId = row[0]
        depth = row[1]
        azimuth = row[2]
        dip = row[3]
        survey = Survey_Record(depth,azimuth,dip)
        if holeId in collars:
            collars[holeId].surveys += [survey]
        else:
            isolated_surveys += [survey]

    for row in reader_data:
        holeId = row[0]
        depth = row[1]
        end = row[2]
        values = row[3:]
        data = Assay_Record(depth,end,values)
        if holeId in collars:
            collars[holeId].data += [data]
        else:
            isolated_data += [data]

    #use orderded holeid
    keys = collars.keys()
    keys.sort()

    #print "HoleID","Has duplicated","Surveys","Invalid surveys","Assays","Invalid assays","Legth"

    output = []

    for holeId in keys:
        collar = collars[holeId]
        #try:
        ret = collar.validate()

        n = len(collar.surveys)
        m = len(collar.data)
        
        #print holeId,n,m,ret

        if ret:
            if n > 1 and m > 1:
                fixed_surveys = []
                
                initial_point = collar.coordinate 
                for i in xrange(1,n):
                    current_survey = collar.surveys[i-1]
                    next_survey = collar.surveys[i]
                    
                    current_survey.start_coordinate = initial_point
                    current_survey.length = next_survey.depth - current_survey.depth
                    current_survey.end_coordinate = initial_point + current_survey.ending_point()
                    
                    initial_point = current_survey.end_coordinate
            
                fix_coordinates_composites(collar.surveys,collar.data,False)
                
                for d in collar.data:
                    output += [[collar.holeId,d]]

        #except Exception as e:
        #    print "error processing:",collar.holeId,e
        #    raise e

    return output

