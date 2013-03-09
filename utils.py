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

#Various global counts needed
total_count = { 
                "ndirs":1,  #to include the root directory in the count
                "nfiles":0,
                "npdfs":0, 
                "npages":0,
                "nlargepages":0,
                "nsmallpages":0,
                "nsizeDpages":0,
               }

#Keep track of the PDFs that PyPDF could not open
badpdfs = []

'''
TO REMOVE
---
def main():
    #prompt user for rootdir 
    print "Enter the complete path of the directory to parse."
    print "Example: C:\path\\to\\project "
    rootdir = raw_input(">>")
    
    try: 
        os.listdir(rootdir)
        print '\nOkay!'
    except:
        sys.exit("Invalid directory path or could not access.")
        
    print '\nRoot Directory for Page Count:', rootdir
    
    """
    Initiates the program by beginning the parse with rootdir
    """
    largeformatsize = 95
    dir_count = ParseDir(rootdir, largeformatsize)
    
    for key, value in dir_count.items(): 
        total_count[key] += value
    
    #Print out the final totals for all directories and sub-directories
    print '\n\n---Summary stats ---'
    print 'Directory:', rootdir
    print 'Total number of files:', total_count["nfiles"]
    print 'Total number of PDF files:', total_count["npdfs"]
    print 'Total number of pages in PDFs are:', total_count["npages"]
    print '\tSmall pages:', total_count["nsmallpages"]
    print '\tLarge pages:', total_count["nlargepages"]
    print '\tSize D page-equivalent:', total_count["nsizeDpages"]
    
    #Print out any PDFs that could not be opened by pyPDF
    if len(badpdfs) > 0: 
        print '\nWARNING!'
        print 'The following PDFs seem to be corrupt. They were not included in the page count.'
        for badpdf in badpdfs: 
            print '\t', badpdf
    print '\n--- END ---'
'''   
                 
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

def ProcessPDF ( filename, largeformatsize ):
    """
    Open a PDF to perform a page count and check for corrupt files
    Count small pages and large pages as defined above.
    """
    pdf_count = { 
                "npages":0,
                "nlargepages":0,
                "nsmallpages":0,
                "nsizeDpages":0,
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
            
        longside = width if width > height else height
        if longside > 34: 
            pdf_count["nsizeDpages"] += int(ceil(longside / 22))
        else: 
            pdf_count["nsizeDpages"] += 1
                    
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
                "nsizeDpages":0,
               }    
    print "Processing files",
    
    badpdfs = []

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
                  badpdfs.append(error)

                print ".",  #Useful to indicate progress 
            pass
       
        elif os.path.isdir(objpath):
            dir_count["ndirs"] += 1
            subdir_badpdfs, subdir_count = ParseDir(objpath , largeformatsize)
            
            for key, value in subdir_count.items(): 
                dir_count[key] += value
            
            badpdfs = badpdfs + subdir_badpdfs

        else: 
            #Wait, what? Not a file NOR a directory?
            badpdfs += "<{}>: Invalid Type!".format(objpath)
        
    return badpdfs, dir_count
