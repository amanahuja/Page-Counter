import utils
import cmd, os

class PageCounterConsole(cmd.Cmd):

  #Define default largeformatsize
  # See module do_setsize for more information
  largeformatsize = 95
    
  #Override Cmd init
  def __init__(self):
    cmd.Cmd.__init__(self)
    self.prompt = "==> "
    self.intro = """
      PDF Page Counter
      Author: @amanqa
      ----------------------
      Type 'help' for a list of commands.
      Type 'help <command>' for help on any command
      
      """
  ##
  ## Page-counter commands
  ## 
  
  def do_filecount(self, args):
    """Process a document, count pages
    Syntax: 
      filecount <filename>
    """
    #Clean input
    filepath = utils.clean_input(args)
    
    #check if file exists
    if not os.path.exists(filepath):
      print 'Could not find a file at <{}>'.format(filepath)
      return
    
    #check file extension is PDF
    if not filepath.endswith('.pdf'):
      print 'Invalid extension'
      return      

    #Get counts
    s, count = utils.ProcessPDF(filepath, self.largeformatsize)

    #Print out counts
    lout = self._log_line
    if s:     
      lout('\nFile Stats for <{}>\n'.format(filepath))
      for k,v in count.iteritems(): 
        lout('{}: \t{}\n'.format(k,v))
    else: 
      #function returned error, handle here
      error = count 
      lout(error + '\n')
    
  def do_dircount(self, args):
    """Process a directory and all the files inside
    Syntax: 
      dircount <x:\\path\\to\\dir\\>
    """
    #Clean input
    dirpath = utils.clean_input(args)
    
    #Check that directory exists
    if not os.path.exists(dirpath):
      print 'Could not find specific path at <{}>'.format(dirpath)
      return
    
    #Get counts
    errors, counts = utils.ParseDir(dirpath, self.largeformatsize)

    #Print output
    self._log_output (dirpath, counts, errors)
    
    #Print warning if any files ignored
    if counts["nfiles"] != counts["npdfs"]:
      self._log_line('Warning: Ignored {} files that were not PDFs.\n'.format(
          counts["nfiles"] - counts["npdfs"]))
      
  def do_setsize(self, args):
    """Change the default size formats for counting.
    Currently, you can only set the size that differentiates "large" format
    pages from other pages. 
    Syntax: 
      setsize <MIN_SIZE_FOR_LARGE_PAGES>
    Example: 
      setsize 95

    MIN_SIZE_FOR_LARGE_PAGES should be number greater than zero, representing 
    size of a page in square inches. All pages larger than this will be counted
    as large pages. 
    
    See: 
      http://en.wikipedia.org/wiki/Paper_size

    Dimensions are in square inches. For reference, 8.5 x 11 is about 93.46 
    square inches. So the default value of 95 defines large format as pages 
    just over "Letter" size.

    """
    try:     
      self.largeformatsize = float(args)
    except ValueError:
      print 'Invalid value for size.'
      print 'Try again. Enter a single number in square inches. Example:' 
      print '\tsetsize 95'
      return

    print 'Set MIN_SIZE_FOR_LARGE_PAGES = {}'.format(self.largeformatsize)
    
  ##
  ## Utility Commands
  ## 
        
  def _log_output(self, loc, counts, errors):
    lout = self._log_line
    lout('\nDirectory Stats for <{}>:\n'.format(loc))
    lout('(Includes sub-directories)\n')
    lout('\tNumber of files: {}\n'.format(counts["nfiles"]))
    lout('\tNumber of PDFs: {}\n'.format(counts["npdfs"]))
    lout('\tNumber of pages: {}\n'.format(counts["npages"]))
    lout('\t\tLarge pages: {}\n'.format(counts["nlargepages"]))
    lout('\t\tSmall pages: {}\n'.format(counts["nsmallpages"]))
    lout('\t\tSmall pages: {}\n'.format(counts["nsizeDpages"]))
    
    if errors: 
      #function encountered error, handle here
      lout('Encountered errors in the following files:\n')
      for err in errors: 
        lout('\t%s\n' % err)
 
  def _log_line(self, line):
    print line,
    fout = self.outfile.write
    fout (line)
    
  def do_hist(self, args):
    """Print recently used commands"""
    print 'Recently used commands: '
    history = ''
    for h in self._hist[-11:-1] : 
      history += h + ', '
    print '{}'.format(history.rstrip(', '))
    
  def do_exit(self, args):
    """Exit from the console."""
    return -1
  
  def do_EOF(self, line):
    """EOF or <Control-D> to Exit from Console"""
    return True
  
  ##
  ## Overide cmd methods
  ##
  def preloop(self):
    """Initialization
    """
    cmd.Cmd.preloop(self)
    self._hist = []  
    self.logfilename = utils._get_logfile_name()
    self.outfile = file(self.logfilename, 'wb')
    print 'Logging to file <{}>.'.format(self.logfilename)
  
  def precmd(self, line):
    self._hist += [ line.strip() ]
    return line

  def postcmd(self, stop, line):
    """After each command is completed.
    """
    print '-' * 10
    return stop
    
  def postloop(self):
    """On Exit
    """
    cmd.Cmd.postloop(self)
    self.outfile.close()
    print 'Log saved to file <{}>.'.format(self.logfilename)
    print 'Bye.\n'

if __name__ == "__main__":
  console = PageCounterConsole()
  console . cmdloop() 

