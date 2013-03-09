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
    if not os.path.exists(args):
      print 'Could not find a file at <{}>'.format(args)
      return
    
    s, count = utils.ProcessPDF(args, self.largeformatsize)

    if s:     
      print '\nFile Stats for <{}>'.format(args)
      for k,v in count.iteritems(): 
        print '{}: \t{}'.format(k,v)
    else: 
      #function returned error, handle here
      error = count 
      print error
    
  def do_dircount(self, args):
    """Process a directory and all the files inside
    Syntax: 
      dircount <x:\\path\\to\\dir\\>
    """
    if not os.path.exists(args):
      print 'Could not find specific path at <{}>'.format(args)
      return
    
    errors, counts = utils.ParseDir(args, self.largeformatsize)

    self._print_output (args, counts, errors)
      
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
  
  def _print_output(self, loc, counts, errors):
    print '\nDirectory Stats for <{}>:'.format(loc)
    print '(Includes sub-directories)'
    print '\tNumber of files:', counts["nfiles"]
    print '\tNumber of PDFs:', counts["npdfs"]
    print '\tNumber of pages:', counts["npages"]
    print '\t\tLarge pages:', counts["nlargepages"]
    print '\t\tSmall pages:', counts["nsmallpages"]
    print '\t\tSmall pages:', counts["nsizeDpages"]
    
    if errors: 
      #function encountered error, handle here
      print 'Encountered errors in the following files: '
      for err in errors: 
        print '\t%s' % err

    self._log_output(self, loc, counts, errors)
      
  def _log_output(self, loc, counts, errors):
    fout = self.outfile.write
    fout('\nDirectory Stats for <{}>:'.format(loc))
    fout('(Includes sub-directories)')
    fout('\tNumber of files:', counts["nfiles"])
    fout( '\tNumber of PDFs:', counts["npdfs"])
    fout('\tNumber of pages:', counts["npages"])
    fout('\t\tLarge pages:', counts["nlargepages"])
    fout('\t\tSmall pages:', counts["nsmallpages"])
    fout('\t\tSmall pages:', counts["nsizeDpages"])
    
    if errors: 
      #function encountered error, handle here
      fout('Encountered errors in the following files: ')
      for err in errors: 
        fout('\t%s' % err)
 
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
    self.outfile = file(self.logfilename, 'w')
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

