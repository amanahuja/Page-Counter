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
      https://github.com/amanahuja/Page-Counter
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
    count = utils.ProcessPDF(args, self.largeformatsize)
    print count
  
  def do_dircount(self, args):
    """Process a directory and all the files inside
    Syntax: 
      dircount <x:\\path\\to\\dir\\>
    """
    if not os.path.exists(args):
      print 'Could not find specific path at <{}>'.format(args)
      return
    
    count = utils.ParseDir(args, self.largeformatsize)
    if not count: 
      #function encountered error, handle here
      pass
  
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
  
  def precmd(self, line):
    self._hist += [ line.strip() ]
    return line

  def postloop(self):
    """On Exit
    """
    cmd.Cmd.postloop(self)
    print '\nBye.\n'
    

if __name__ == "__main__":
  console = PageCounterConsole()
  console . cmdloop() 

