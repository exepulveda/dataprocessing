'''
copyright 2014 Exequiel Sepulveda

Free permission to copy, adapt, modify 

'''

import drillhole

collar_filename = "examples/collar.csv"
survey_filename = "examples/survey.csv"
data_filename = "examples/assay.csv"
delimiter=","

data = drillhole.composite(collar_filename,survey_filename,data_filename,True,delimiter)

for holeId,d in data:
    print holeId,d.start_coordinate,d.end_coordinate,d.values
