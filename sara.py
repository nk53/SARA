from os.path import isfile, isdir
from os.path import join as path_join
from sys import stdout
from PIL import Image
from pandas import read_csv, Index, Series
from IPython.html import widgets
from IPython.display import display
from sima import Sequence, ImagingDataset
from sima.motion import PlaneTranslation2D
from sima.ROI import ROI, ROIList
from sima.segment import STICA
from sima.segment.segment import PostProcessingStep
import matplotlib.pyplot as plt

class SaraUI():
  def __init__(self, sima_dir=None):
    if sima_dir == None:
      prompt = "Name of SIMA analysis directory: "                   
      self.sima_dir = self.reserveDirectory(prompt, '.sima')
    else:
      self.sima_dir = sima_dir
  
  def defaultInput(self, prompt='', default_value=None):
    """Replace empty input with a default value"""
    value = raw_input(prompt)
    if value == '' and default_value != None:
      value = default_value
    return value
  
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
  
  def getFileWithExtension(self, prompt=None, extension={}):
    """Examples for extension:
       {"TIFF" : ['.tif', '.tiff']}
       {"PNG" : '.png'}"""
    if prompt == None:
      prompt = "Please input the full path to the file: "
    while True:
      file_path = self.getFilePath(prompt)
      for typeName, acceptedExtensions in extension.iteritems():
        if type(acceptedExtensions) == str:
          acceptedExtensions = [acceptedExtensions]
        for e in acceptedExtensions:
          if file_path.endswith(e):
            return file_path
      prompt = "Your file is not a valid %s file, please try again: " \
                % '/'.join(extension.keys())
  
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
  
  def getFloat(self, prompt=None, default=None):
    if prompt == None:
      prompt = "Please enter a decimal number (e.g. 1.51): "
    num = self.defaultInput(prompt, default)
    try:
      num = float(num)
    except ValueError:
      prompt = "The value you entered is not a valid number, " + \
               "please try again: "
      num = self.getFloat(prompt)
    return num
  
  def getInteger(self, prompt=None, default=None):
    if prompt == None:
      prompt = "Please enter an integer: "
    integer = self.defaultInput(prompt, default)
    try:
      integer = int(integer)
    except ValueError:
      prompt = "The value you entered is not a valid integer, " + \
                "please try again: "
      integer = self.getInteger(prompt)
    return integer
  
  def getNatural(self, prompt=None, default=None):
    if prompt == None:
      prompt = "Please enter a non-negative integer: "
    natural = self.getInteger(prompt, default)
    while natural < 0:
      prompt = "The number you entered is negative, please try again: "
      natural = self.getInteger(prompt)
    return natural
  
  def getPercent(self, prompt=None, default=None):
    """Prompt user for something like 90 or 42.2%
       
       Returns the percentage as a proportion;
       E.g. if user enter 90, getPercent() returns 0.9
       
       Default value must be given as a proportion, as above"""
    if prompt == None:
      "Please enter a percentage (e.g. 90.5%): "
    percent = -1
    while percent < 0 or percent > 100:
      try:
        # remove all '%', divide by 100 to make a proportion
        # str() cast is to make str.replace() work with default value
        percent = float(self.defaultInput(prompt, str(default)).replace(
          '%', '')) / 100
      except ValueError:
        prompt = "The value you entered is not a valid percentage, " + \
                 "please try again: "
        continue
      prompt = "Please enter a number between 0 and 100: "
    return percent
  
  def getPNG(self, prompt=None):
    if prompt == None:
      prompt = "File path to your PNG image: "
    extension = {"PNG" : '.png'}
    image_path = self.getFileWithExtension(prompt, extension)
    return image_path

  def getString(self, prompt=None):
    """Prompt the user for a string"""
    return raw_input(prompt)
  
  def getTIFF(self, prompt=None):
    if prompt == None:
      prompt = "File path to your TIFF image: "
    extension = {"TIFF" : ['.tif', '.tiff']}
    image_path = self.getFileWithExtension(prompt, extension)
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
      "None"                : lambda x, y: None,
    }
    
    self.setSettings()
  
  def setSettings(self, image_path=None):
    options = self.strategy_map.keys()
    options.sort() # force alphabetical order
    self.strategy_radio = self.showRadio(options)
    
    if image_path == None:
      # currently only TIFF is supported by SARA
      prompt = "File path to the image you want corrected (TIFF only): "
      self.image_path = self.getTIFF(prompt)
    else:
      self.image_path = image_path
    
    prompt = "Where would you like to save the corrected frames? "
    self.corrected_frames = self.reserveFilePath(prompt)
    
    self.sequence = Sequence.create('TIFF', self.image_path)
    prompt = ["Maximum %s displacement (in pixels; default 100): " \
               % ax for ax in ['X', 'Y']]
    md_x = self.getNatural(prompt[0], default=100)
    md_y = self.getNatural(prompt[1], default=100)
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
      self.components = self.getNatural(prompt, default=50)
      prompt = "Tradeoff between spatial and temporal information " + \
               "(must be between 0 and 1; low values give higher " + \
               "weight to temporal information; default 0.5): "
      mu = -1
      while self.mu < 0 or self.mu > 1:
        self.mu = self.getFloat(prompt, default=0.5)
      prompt = "Percent of ROIs that must overlap to be combined " + \
               "(must be between 0 and 100; enter 0 to skip " + \
               "this step; default 20%): "
      self.overlap_per = self.getPercent(prompt, default=0.2)
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

class VisualizationUI(SaraUI):
  def __init__(self, ui, settings=None):
    self.sima_dir = ui.sima_dir
    self.image = None
    self.image_height = None
    self.image_width = None
    
    if settings == None:
      self.settings = {
        "color_cycle" : ['blue', 'red', 'magenta', 'brown', 'cyan',
                        'orange', 'yellow', 'green'],
        "linewidth" : 2,
      }
    else:
      self.settings = settings
    plt.rc('axes', color_cycle=self.settings['color_cycle'])
    plt.rc('lines', linewidth=self.settings['linewidth'])
    
    self.visualize()
  
  def visualize(self, warn=False):
    # Weird things happen if we try to visualize multiple images
    # without doing this
    plt.clf()
    
    # prepare background image
    prompt = "File path to an RGB, PNG background image: "
    self.image = Image.open(self.getPNG(prompt))
    self.image_width, self.image_height = self.image.size
    plt.xlim(xmin=0, xmax=self.image_width)
    plt.ylim(ymin=0, ymax=self.image_height)
    plt.imshow(self.image)
    
    # get list of ROIs from SIMA analysis directory
    rois = ROIList.load(path_join(self.sima_dir, "rois.pkl"))
    
    # plot all of the ROIs, warn user if an ROI has internal loops
    for roi in rois:
      coords = roi.coords
      if warn and len(coords) > 1:
        print "Warning: Roi%s has >1 coordinate set" % roi.id
      x = coords[0][:,0]
      y = coords[0][:,1]
      plt.plot(x, y)
    
    plt.show()

class SignalUI(SaraUI):
  def __init__(self, ui):
    self.sima_dir = ui.sima_dir
    self.dataset = ImagingDataset.load(self.sima_dir)
    self.rois = self.dataset.ROIs['stICA ROIs']
    # get user inputs
    self.output_options = ['time', 'frame number']
    self.radio = self.showRadio(self.output_options)
    prompt = "File path to export to: "
    self.outfile = self.reserveFilePath(prompt)
    prompt = "Please input the recording's capture rate " + \
             "(seconds per frame): "
    self.frames_to_time = self.getFloat(prompt)
    # check if we've already extracted a signal
    if self.dataset.signals() == {}:
      print "Extracting signals from ROIs..."
      stdout.flush() # force print statement to output to IPython
      self.signal = self.dataset.extract(rois=self.rois, label='signal')
      print "Signals extracted"
    else:
      self.signal = self.dataset.signals()['signal']
    self.dataset.export_signals(self.outfile)
    # do we need to post-process the CSV?
    if self.radio.value == 'time':
      self.postProcessSignal()
  
  def postProcessSignal(self):
    # read in tab-separated data
    data = read_csv(self.outfile, sep='\t')
    
    # change name of 'frames' col to 'time'
    old_cols = data.columns.tolist()
    new_cols = [old_cols[0], 'time'] + old_cols[2:]
    # preserve useless labels/tags in case they are someday useful
    lab_tag = data['frame'].tolist()[:2]
    
    # cast frames from str to float so we can do math
    times = map(float, data['frame'].tolist()[2:])
    # convert frame number to time
    times = map(lambda x: x*self.frames_to_time, times)
    
    # prepare new data for output
    times = Series(lab_tag + times)
    data['frame'] = times
    data.columns = new_cols
    
    # export back to CSV
    data.to_csv(self.outfile, sep='\t')

class IdROIs(PostProcessingStep):
  def apply(self, rois, dataset=None):
    rois_with_ids = []
    for index, roi in enumerate(rois):
      newroi = roi.todict()
      newroi['id'] = index
      rois_with_ids.append(newroi)
    return ROIList(rois_with_ids)
