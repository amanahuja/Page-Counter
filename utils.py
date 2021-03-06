'''
Author: Aman Ahuja
https://github.com/amanahuja/Page-Counter
'''

import warnings
warnings.simplefilter("ignore", DeprecationWarning)

import os
from pyPdf import PdfFileReader
from math import ceil
from datetime import datetime

def _sorted_listdir(path):
    """
    Returns the contents of a directory, sorting in order to 
    show directories and then files, ordered alphabetically
    """
    contents = sorted([f for f in os.listdir(path) if os.path.isfile(path + os.path.sep + f)])
    contents.extend(sorted([d for d in os.listdir(path) if os.path.isdir(path + os.path.sep + d)]))

    return contents

def _get_logfile_name(logfilebase = 'count', usetimestamp = True):
  """
  Figure out what to name the log file
  """  
  suffix = '.log'
  name = '{}.{:%d-%m-%Y}'.format(logfilebase, datetime.now())
  ii = 0
  logfilename = name + '.{:02d}'.format(ii) + suffix
  while os.path.exists(logfilename):
    ii += 1
    logfilename = name + '.{:02d}'.format(ii) + suffix
  
  return logfilename

def clean_input ( instring ):
  outstring = instring.strip()

  outstring = outstring.strip('"')
  outstring = outstring.strip("'")
  return outstring  
  
  
def ProcessPDF ( filename, largeformatsize ):
    """
    Open a PDF to perform a page count and check for corrupt files
    Count small pages and large pages as defined above.
    """
    pdf_count = { 
                "npages":0,
                "nlargepages":0,
                "nsmallpages":0,
               }

    try: 
      #Open file
      filestream = file(filename, "rb")    
      #load into pypdf
      pdfFile = PdfFileReader(filestream)
      
      #First access into pdf contents
      #  Raises decryption/security exceptions here
      npages = pdfFile.getNumPages()

    except IOError: 
      err = '<{}> :: Could not open file. Check permissions?'.format(filename)
      return False, err
    except Exception as e: 
      err = '<{}> :: {}'.format(filename, e)
      return False, err
    
    for ii in range(npages): 
        pdf_count["npages"] += 1

        '''
        Calculate page dimensions and pricing category
        Dimensions are returned by pyPDF in Points (72 points = 1 inch)
        See: 
           http://en.wikipedia.org/wiki/Point_(typography)
           http://en.wikipedia.org/wiki/Paper_size
        '''
        width = (pdfFile.getPage(ii).artBox.getUpperRight_x()/72 - 
             pdfFile.getPage(ii).artBox.getLowerLeft_x()/72)
    
        height = (pdfFile.getPage(ii).artBox.getUpperRight_y()/72 -
                  pdfFile.getPage(ii).artBox.getLowerLeft_y()/72)
        
        if (width * height) > largeformatsize:
            pdf_count["nlargepages"] += 1
        else:
            pdf_count["nsmallpages"] += 1
                    
    return True, pdf_count
   
def ParseDir (thisdir, largeformatsize):
    """
    Traverse a directory and its contents (sub-directories and files)
    Calls ProcessPDF for a page count for each PDF File
    Intended to be called recursively to traverse sub-directories
    """
    
    #local directory-based counts needed
    dir_count = {
                "ndirs":0,
                "nfiles":0,
                "npdfs":0, 
                "npages":0,
                "nlargepages":0,
                "nsmallpages":0,
               }    
    print "Processing files",
    
    errors = []

    #Loop through each object in the directory
    for iobject in _sorted_listdir(thisdir):
        objpath = os.path.join(thisdir, iobject)

        #The directory object is a file            
        if os.path.isfile(objpath):
            dir_count["nfiles"] += 1

            if iobject.endswith('.pdf'):
                dir_count["npdfs"] += 1

                #DEBUG output: print "Processing: ", iobject 
                s, content = ProcessPDF( objpath, largeformatsize )

                if s: 
                  pdf_counts = content
                  for key, value in pdf_counts.items(): 
                      dir_count[key] += value
                else: 
                  #function returned error, handle here
                  error = content
                  errors.append(error)

                print ".",  #Useful to indicate progress 
            pass
       
        elif os.path.isdir(objpath):
            dir_count["ndirs"] += 1
            subdir_errors, subdir_count = ParseDir(objpath , largeformatsize)
            
            for key, value in subdir_count.items(): 
                dir_count[key] += value
            
            errors = errors + subdir_errors

        else: 
            #Wait, what? Not a file NOR a directory?
            errors += "<{}>: Invalid Type!".format(objpath)
        
    return errors, dir_count
