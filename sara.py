from os.path import isfile, isdir
from sys import stdout
from IPython.html import widgets
from IPython.display import display
from sima import Sequence, ImagingDataset
from sima.motion import PlaneTranslation2D
from sima.ROI import ROI, ROIList
from sima.segment import STICA
from sima.segment.segment import PostProcessingStep

class SaraUI():
  def __init__(self, sima_dir=None):
    if sima_dir == None:
      prompt = "Name of SIMA analysis directory: "                   
      self.sima_dir = self.reserveDirectory(prompt, '.sima')
    else:
      self.sima_dir = sima_dir
  
  def getBoolean(self, prompt):
    """Expects a response of the form (y/n)"""
    bool_map = {'y' : True, 'n' : False}
    response = raw_input(prompt)[0].lower()
    if response != 'y' and response != 'n':
      prompt = "Please enter y (yes) or n (no): "
      return self.getBoolean(prompt)
    return bool_map[response]
  
  def getFilePath(self, prompt=None):
    """Prompt the user for full path to a file
       
       Also works if relative path is given; MUST NOT BE A DIRECTORY!"""
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
      prompt = "The name you entered already exists, do you want to " + \
               "overwrite it? (y/n): "
      if not self.getBoolean(prompt):
        return self.reserveFilePath()
    if isdir(path):
      prompt = "The name you entered is a directory, please try again: "
      return self.reserveFilePath(prompt)
    return path
  
  def reserveDirectory(self, prompt=None, extension=''):
    if prompt == None:
      prompt = "Please input a directory name: "
    path = raw_input(prompt) + extension
    if not path.endswith(extension):
      path += extension
    if isfile(path):
      prompt = "The name you entered is a file and already exists, " + \
               "please try again: "
    if isdir(path):
      prompt = "The directory you entered already exists, " + \
                "do you want to use it anyway? (y/n): "
      if not self.getBoolean(prompt):
        return self.reserveDirectory()
    return path
  
  def getFloat(self, prompt=None):
    if prompt == None:
      prompt = "Please enter a decimal number (e.g. 1.51): "
    try:
      num = float(raw_input(prompt))
    except ValueError:
      prompt = "The value you entered is not a valid number, " + \
               "please try again: "
      num = self.getFloat(prompt)
    return num
  
  def getInteger(self, prompt=None):
    if prompt == None:
      prompt = "Please enter an integer: "
    integer = raw_input(prompt)
    try:
      integer = int(integer)
    except ValueError:
      prompt = "The value you entered is not a valid integer, " + \
                "please try again: "
      integer = self.getInteger(prompt)
    return integer
  
  def getNatural(self, prompt=None):
    if prompt == None:
      prompt = "Please enter a non-negative integer: "
    natural = self.getInteger(prompt)
    while natural < 0:
      prompt = "The number you entered is negative, please try again: "
      natural = self.getInteger(prompt)
    return natural
  
  def getPercent(self, prompt=None):
    """Prompt user for something like 90 or 42.2%"""
    if prompt == None:
      "Please enter a percentage (e.g. 90.5%): "
    # get rid of all '%' that appear
    percent = -1
    while percent < 0 or percent > 100:
      try:
        percent = float(raw_input(prompt).replace('%', ''))
      except ValueError:
        prompt = "The value you entered is not a valid percentage, " + \
                 "please try again: "
        continue
      prompt = "Please enter a number between 0 and 100: "
    return percent
  
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
  
  def __init__(self, ui=None):
    self.strategy_radio = None
    self.sequence = None
    self.dataset = None
    if ui == None:
      ui = SaraUI()
    self.sima_dir = ui.sima_dir
    
    # maps radio options to function calls, shown in alphabetical order
    self.strategy_map = {
      "2D Plane Correction" : self.planeTranslation2D,
      "Hidden Markov Model" : self.hmm,
      "None"                : lambda x, y: None,
    }
    
    self.setSettings()
  
  def setSettings(self, image_path=None):
    options = self.strategy_map.keys()
    options.sort() # force alphabetical order
    self.strategy_radio = self.showRadio(options)
    
    if image_path == None:
      # currently only TIFF is supported by SARA
      prompt = "File path to your image: "
      self.image_path = self.getTIFF(prompt)
    else:
      self.image_path = image_path
    
    prompt = "Where would you like to save the corrected frames? "
    self.corrected_frames = self.reserveFilePath(prompt)
    
    self.sequence = Sequence.create('TIFF', self.image_path)
    prompt = ["Maximum %s displacement (in pixels): " \
               % ax for ax in ['X', 'Y']]
    md_x = self.getNatural(prompt[0])
    md_y = self.getNatural(prompt[1])
    self.settings = {"max_displacement" : [md_x, md_y]}
    
    # By this time, the user should have selected a strategy
    self.strategy_radio.close()
    self.strategy_map[self.strategy_radio.value]()
  
  def planeTranslation2D(self):
    print "Performing motion correction with 2D Plane Correction " + \
          "(this could take a while) . . ."
    stdout.flush() # force print statement to output to IPython
    self.dataset = PlaneTranslation2D(**self.settings).correct(
                     [self.sequence], self.sima_dir)
    print "Motion correction complete"
    self.dataset.export_frames([[[self.corrected_frames]]])
  
  def hmm(self):
    pass

class SegmentationUI(SaraUI):
  def __init__(self, ui=None):
    # check if motion is defined
    self.sima_dir = ui.sima_dir
    self.dataset = ImagingDataset.load(self.sima_dir)
    self.mu = -1
    self.components = -1
    self.overlap_per = 0
    self.rois = None
    
    self.segment()
  
  def segment(self, settings=None):
    if settings == None:
      prompt = "Number of PCA components (higher numbers take longer; " + \
               "default 50): "
      self.components = self.getNatural(prompt)
      prompt = "Tradeoff between spatial and temporal information " + \
               "(must be between 0 and 1; low values give higher " + \
               "weight to temporal information; default 0.5): "
      mu = -1
      while self.mu < 0 or self.mu > 1:
        self.mu = self.getFloat(prompt)
      prompt = "Percent of ROIs that must overlap to be combined " + \
               "(must be between 0 and 100; enter 0 to skip " + \
               "this step; default 20): "
      self.overlap_per = self.getPercent(prompt)
      settings = {
        'components' : self.components,
        'mu' : self.mu,
        'overlap_per' : self.overlap_per,
      }
    print "Performing Spatiotemporal Independent Component Analysis..."
    stdout.flush()
    stica = STICA(**settings)
    stica.append(IdROIs())
    self.rois = self.dataset.segment(stica, label="stICA ROIs")
    print len(self.dataset.ROIs['stICA ROIs']), "ROIs found"

class IdROIs(PostProcessingStep):
  def apply(self, rois, dataset=None):
    rois_with_ids = []
    for index, roi in enumerate(rois):
      newroi = roi.todict()
      newroi['id'] = index
      rois_with_ids.append(newroi)
    return ROIList(rois_with_ids)
