import utils
import cmd, os

class PageCounterConsole(cmd.Cmd):

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
    count = utils.ProcessPDF(args)
    print count
  
  def do_dircount(self, args):
    """Process a directory and all the files inside
    Syntax: 
      dircount <x:\path\to\dir\>
    """
    if not os.path.exists(args):
      print 'Could not find specific path at <{}>'.format(args)
      return
    
    count = utils.ParseDir(args)
    print count
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

