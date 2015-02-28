from os.path import isfile, isdir
from sys import stdout
from IPython.html import widgets
from IPython.display import display
from sima import Sequence
from sima.motion import PlaneTranslation2D

class SaraUI():
  def __init__(self):
    self.dataset = None
  
  def getBoolean(self, prompt):
    pass
  
  def getFilePath(self, prompt=None):
    """Prompt the user for full path to a file
       
       Also works if relative path is given"""
    # default prompt
    if prompt == None:
      prompt = "Please input the full path to the file: "
    path = raw_input(prompt)
    if not isfile(path):
      prompt = "The file path you input is invalid, please try again: "
      return self.getFilePath(prompt)
    return path
  
  def reserveFilePath(self, prompt=None, allow_overwrite=False):
    if prompt == None:
      prompt = "Please input file name: "
    path = raw_input(prompt)
    if not allow_overwrite and isfile(path):
      prompt = "The name you entered already exists, please try again: "
      return self.reserveFilePath(prompt)
    if isdir(path):
      prompt = "The name you entered is a directory, please try again: "
      return self.reserveFilePath(prompt)
    return path
  
  def reserveDirectory(self, prompt=None):
    if prompt == None:
      prompt = "Please input a directory name: "
    path = raw_input(prompt)
    if isdir(path):
      prompt = "The directory you entered already exists, " + \
                "please try again: "
      return self.reserveDirectory(prompt)
    return path
    
  def getInteger(self, prompt=None):
    if prompt == None:
      prompt = "Please enter an integer: "
    integer = raw_input(prompt)
    try:
      integer = int(integer)
    except ValueError:
      prompt = "The value you entered is not a valid integer, " + \
                "please try again: "
      self.getInteger(prompt)
    return integer
  
  def getNatural(self, prompt=None):
    if prompt == None:
      prompt = "Please enter a non-negative integer: "
    natural = self.getInteger(prompt)
    while natural < 0:
      prompt = "The number you entered is negative, please try again: "
      natural = self.getInteger(prompt)
    return natural
  
  def getString(self, prompt=None):
    """Prompt the user for a string"""
    return raw_input(prompt)
  
  def getTIFF(self, prompt=None):
    prompt = "File path to your image: "
    image_path = self.getFilePath(prompt)
    while not image_path.endswith('.tif') \
      and not image_path.endswith('.tiff'):
      prompt = "The file you selected is not a TIFF file, " + \
                "please try again: "
      image_path = self.getFilePath(prompt)
    return image_path
  
  def showRadio(self, options, default=None):
    if default == None:
      default = options[0]
    radio = widgets.RadioButtonsWidget(values=options, value=default)
    display(radio)
    return radio
  
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
    self.strategy_radio = self.showRadio(options)
  
  def correct(self, file_path=None, verbose=True):
    if self.strategy_radio == None:
      print "You need to select a motion correction strategy first"
      return
    self.strategy_radio.close()
    # call the correction function
    self.strategy_map[self.strategy_radio.value](file_path, verbose)

  def planeTranslation2D(self, file_path=None, verbose=True):
    if file_path == None:
      # currently only TIFF is supported by SARA
      prompt = "File path to your image: "
      image_path = self.getTIFF(prompt)

    self.sequence = Sequence.create('TIFF', image_path)
    prompt = "Name of SIMA analysis directory: "
    project_directory = self.reserveFilePath(prompt)
    prompt = ["Maximum %s displacement (in pixels): " \
               % ax for ax in ['X', 'Y']]
    md_x = self.getNatural(prompt[0])
    md_y = self.getNatural(prompt[1])
    prompt = "Where would you like to save the corrected frames? "
    corrected_frames = self.reserveDirectory(prompt)
    settings = {'max_displacement':[md_x, md_y]}
    print "Performing motion correction (this could take a while) . . ."
    stdout.flush() # force print statement to output to IPython
    self.dataset = PlaneTranslation2D(**settings).correct(
                     [self.sequence], project_directory)
    print "Motion correction complete"
    self.dataset.export_frames([[[corrected_frames]]])
  
  def hmm(self):
    pass
