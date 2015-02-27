from os import stat
from IPython.html import widgets
from IPython.display import display
from sima import Sequence
from sima.motion import PlaneTranslation2D

class SaraUI():
  
  def __init__(self):
    self.dataset = None
  
  def getBooleanUserInput(self, prompt):
    pass
  
  def getFilePath(self, message=None):
    """Prompt the user for full path to a file
       
       Also works if relative path is given"""
    # default message
    if message == None:
      message = "Please input the full path to the file:"
    path = raw_input(message)
    try:
      stat(path)
    except OSError as e:
      if e.errno == 2:
        message = "The file path you input is invalid, please try again:"
        return self.getFilePath(message)
    return path
  
  def showRadioInput(self, options, default=None):
    if default == None:
      default = options[0]
    radio = widgets.RadioButtonsWidget(values=options, value=default)
    display(radio)
    return radio
  
  #def getRadioInput(self, radio):
  #  return radio.value

class MotionCorrectionUI(SaraUI):
  """Handles different SIMA motion correction strategies"""
  
  def __init__(self, showNow=True):
    self.strategy_radio = None
    self.sequence = None
    self.dataset = None
    
    # maps radio options to function calls, shown in alphabetical order
    self.strategy_map = {
      "2D Plane Correction" : self.planeTranslation2D,
      "Hidden Markov Model" : self.hmm,
    }
    
    if showNow == True:
      self.showStrategies()
  
  def showStrategies(self):
    options = self.strategy_map.keys()
    options.sort() # force alphabetical order
    self.strategy_radio = self.showRadioInput(options)
  
  def correct(self):
    if self.strategy_radio == None:
      print "You need to select a motion correction strategy first"
    # call the correction function
    self.strategy_map[self.strategy_radio.value]()

  def planeTranslation2D(self):
    message = "Please input the file path to your image:"
    image_path = self.getFilePath(message)
    self.sequence = Sequence.create('TIFF', image_path)
  
  def hmm(self):
    pass
