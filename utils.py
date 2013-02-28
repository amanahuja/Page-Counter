'''
Author: Aman Ahuja
https://github.com/amanahuja/Page-Counter
'''

largeformatsize = 95
''' 
# Define large format
    Dimensions expressed in Points (72 points = 1 inch)
    http://en.wikipedia.org/wiki/Point_(typography)
    http://en.wikipedia.org/wiki/Paper_size

#   8.5 x 11 is about 93.46
#   Use ~95 to define just over "Letter" size 
'''

import warnings
warnings.simplefilter("ignore", DeprecationWarning)

import os, sys
from pyPdf import PdfFileReader
from math import ceil

#Various global counts needed
total_count = { 
                "ndirs":1,  #to include the root directory in the count
                "nfiles":0,
                "npdfs":0, 
                "npages":0,
                "nlargepages":0,
                "nsmallpages":0,
                "nsizeD":0,
               }

#Keep track of the PDFs that PyPDF could not open
badpdfs = []

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
    dir_count = ParseDir(rootdir)
    
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
    print '\tSize D page-equivalent:', total_count["nsizeD"]
    
    #Print out any PDFs that could not be opened by pyPDF
    if len(badpdfs) > 0: 
        print '\nWARNING!'
        print 'The following PDFs seem to be corrupt. They were not included in the page count.'
        for badpdf in badpdfs: 
            print '\t', badpdf
    print '\n--- END ---'
    
                 
def _sorted_listdir(path):
    """
    Returns the contents of a directory, sorting in order to 
    show directories and then files, ordered alphabetically
    """
    contents = sorted([f for f in os.listdir(path) if os.path.isfile(path + os.path.sep + f)])
    contents.extend(sorted([d for d in os.listdir(path) if os.path.isdir(path + os.path.sep + d)]))

    return contents
    
def ProcessPDF ( filename ):
    """
    Open a PDF to perform a page count and check for corrupt files
    Count small pages and large pages as defined above.
    """
    pdf_count = { 
                "npages":0,
                "nlargepages":0,
                "nsmallpages":0,
                "nsizeD":0,
               }

    try: 
      filestream = file(filename, "rb")    
      pdfFile = PdfFileReader(filestream)
    except IOError: 
      print 'Could not open file. Check permissions? <{}>'.format(filename)
      return False
    
    npages = pdfFile.getNumPages()
    
    for ii in range(npages): 
        pdf_count["npages"] += 1

        # Calculate page dimensions and pricing category
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
            pdf_count["nsizeD"] += int(ceil(longside / 22))
        else: 
            pdf_count["nsizeD"] += 1
                    
    return pdf_count
   
def ParseDir (thisdir):
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
                "nsizeD":0,
               }    
    print     #Spacing for readability
    
    global badpdfs

    #Loop through each object in the directory
    for iobject in _sorted_listdir(thisdir):
        objpath = os.path.join(thisdir, iobject)

        #The directory object is a file            
        if os.path.isfile(objpath):
            dir_count["nfiles"] += 1

            if iobject.endswith('.pdf'):
                dir_count["npdfs"] += 1

                #Uncomment to print object to screen (debugging aid, mostly). 
                #print "Processing: ", iobject 
                try: 
                    pdf_count = ProcessPDF ( objpath )
                    for key, value in pdf_count.items(): 
                        dir_count[key] += value
                except:
                    badpdfs.append(str(objpath))

                print ".",  #Useful to indicate progress 
            pass
       
        elif os.path.isdir(objpath):
            dir_count["ndirs"] += 1
            subdir_count = ParseDir(objpath)
            
            for key, value in subdir_count.items(): 
                dir_count[key] += value

        else: 
            #Wait, what? Not a file NOR a directory?
            print "Invalid Type: ", objpath
        
        
    print '\nDirectory Stats for ', thisdir, ":"
    print '(Includes sub-directories)'
    print '\tNumber of files:', dir_count["nfiles"]
    print '\tNumber of PDFs:', dir_count["npdfs"]
    print '\tNumber of pages:', dir_count["npages"]
    print '\t\tLarge pages:', dir_count["nlargepages"]
    print '\t\tSmall pages:', dir_count["nsmallpages"]
    print '\t\tSmall pages:', dir_count["nsizeD"]

    return dir_count
