from os.path import abspath, isfile, isdir
from os.path import join as path_join
from sys import exit, stdout
from PIL import Image
from pandas import read_csv, Index, Series
from IPython.html import widgets
from IPython.display import display
from sima import Sequence, ImagingDataset
from sima.motion import PlaneTranslation2D
from sima.ROI import ROI, ROIList
from sima.segment import STICA
from sima.segment.segment import PostProcessingStep
import warnings
import matplotlib.pyplot as plt

def ipython_loaded():
  """Returns ``True`` if ``__IPYTHON__`` is defined, ``False`` otherwise
     
  In theory, ``__IPYTHON__`` is only defined when this function is run from
  inside the IPython environment (e.g. an IPython notebook)
  """
  
  try:
    __IPYTHON__
    return True
  except NameError:
    return False

class CommandLineInterface(object):
  """A command-line based UI for grabbing user input.
  
  Implements several functions for obtaining user input using Python's
  built-in :func:`raw_input`.
  Meant to be a parent class. Does not have any attributes of its own.
  
  """

  def defaultInput(self, prompt='', default_value=None):
    """Replace empty user input from raw_input with a default value.
    
    Prompts user for input with :func:`raw_input`. If the returned string
    is empty, *default_value* is returned.
    
    Args:
      prompt (str): Prompt to pass to :func:`raw_input`.
      default_value (any, optional): Value to return if user returns
        empty string. If ``None``, this step is disregarded.
    
    Returns:
      str or *default_value*: User input from :func:`raw_input` or
        *default_value*, if *default_value* is not ``None``.
    
    """
    value = raw_input(prompt)
    if value == '' and default_value != None:
      value = default_value
    return value
  
  def getBoolean(self, prompt):
    """Prompts user for a y/n response. Returns a bool.
    
    Converts user input to lower case, then reads the first character of
    of input, returning ``True`` if it's ``"y"``, and ``False`` if
    ``"n"``. If the first character of user input is neither ``"n"`` nor
    ``"y"``, :meth:`.getBoolean` will try again until the user's response
    is valid.
    
    Args:
      prompt (str): Prompt to pass to :func:`raw_input`.
    
    Returns:
      ``True`` for ``"yes"``-type responses, ``False`` for ``"no"``-types.
    
    """
    bool_map = {'y' : True, 'n' : False}
    response = raw_input(prompt)[0].lower()
    if response != 'y' and response != 'n':
      prompt = "Please enter y (yes) or n (no): "
      return self.getBoolean(prompt)
    return bool_map[response]
  
  def getFilePath(self, prompt=None):
    """Prompt the user for path to an existing file.
       
    Uses :func:`raw_input` to prompt for a file path, which can either be an
    absolute or relative path. User's response must be a path to an
    existing file and **must not be a directory**. If response is
    invalid, :meth:`.getFilePath` will try again until the user's response
    is valid.
    
    Args:
      prompt (str, optional): Prompt to pass to :func:`raw_input`. If
        omitted, the user is prompted with ``"Please input the full path
        to the file: "``.
    
    Returns:
      A string containing a valid path to an existing file.
    
    """
    # default prompt
    if prompt == None:
      prompt = "Please input the full path to the file: "
    path = raw_input(prompt)
    if path == "" or not isfile(path):
      prompt = "The file path you input is invalid, please try again: "
      return self.getFilePath(prompt)
    return path
  
  def getFileWithExtension(self, prompt=None, extension={}):
    """Prompts user for a file path, possibly checking for an extension.
    
    Uses :func:`getFilePath` to prompt user for an existing filename that
    ends with one of the extensions in *extension*. *extension* is a
    dict with the format ``{typeName : acceptedExtensions}``.
    
    Examples:
      Checking for a PNG file::
        
        ui = CommandLineInterface()
        prompt = "File path to your PNG image: "
        extension = {"PNG" : '.png'}
        file_path = ui.getFileWithExtension(prompt, extension)
      
      Checking for a TIFF file::
        
        ui = CommandLineInterface()
        prompt = "File path to your TIFF image: "
        extension = {"TIFF" : ['.tif', '.tiff']}
        file_path = ui.getFileWithExtension(prompt, extension)
    
    If the user does not enter a valid file path,
    :meth:`.getFileWithExtension` prompts the user again using the
    *typeName* from *extension*.
    
    Args:
      prompt (str, optional): Prompt to pass to :func:`raw_input`.
      extension (dict, optional): File extension to require.
    
    Returns:
      A string containing a valid path to an existing file with the
      extension from *extension*.
    
    """
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
  
  def getFloat(self, prompt=None, default=None):
    """Prompt user for a float.
    
    Uses :meth:`.defaultInput` to prompt for a decimal number. If casting
    the user's response would result in a :exc:`~exceptions.ValueError`,
    the user is re-prompted until a valid response is given.
    
    Args:
      prompt (str, optional): Prompt to pass to :func:`raw_input`. If
        omitted, the user is prompted with ``"Please enter a decimal
        number (e.g. 1.51): "``
      default (optional): Value to return if user response is an empty
        string.
    
    Returns:
      Either a float or the value of *default*.

    """
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
    """Prompt user for an integer.
    
    Uses :meth:`.defaultInput` to prompt for an integer. If casting the
    user's response would result in a :exc:`~exceptions.ValueError`, the
    user is re-prompted until a valid response is given.
    
    Args:
      prompt (str, default): Prompt to pass to :func:`raw_input`. If
        omitted, the user is prompted with ``"Please enter an integer: "``.
      default (optional): Value to return if user response is an empty
        string.
    
    Returns:
      Either an int or the value of *default*.
    
    """
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
    """Prompts user for a non-negative integer.
    
    Uses :meth:`.defaultInput` to prompt for an integer. If user response
    is invalid, the user is re-prompted until a valid response is given.
    
    Args:
      prompt (str, optional): Prompt to pass to :func:`raw_input`. If
        omitted, the user is prompted with ``"Please enter a non-negative
        integer: "``.
      default (optional): Value to return if user response is an empty
        string.
      
    Returns:
      Either an int or the value of *default*.
    
    """
    if prompt == None:
      prompt = "Please enter a non-negative integer: "
    natural = self.getInteger(prompt, default)
    while natural < 0:
      prompt = "The number you entered is negative, please try again: "
      natural = self.getInteger(prompt)
    return natural
  
  def getPercent(self, prompt=None, default=None):
    """Prompt user for a percentage.
       
       Uses :meth:`.defaultInput` to prompt for a float. Any ``%``-signs
       appearing in user input are removed. User is expected to enter
       a percentage, but the response is divided by 100. See below.
       
       Example:
         Entering ``90`` versus ``90%``::
           
           >>> ui = CommandLineInterface()
           >>> p1 = ui.getPercent()
           Please enter a percentage (e.g. 90.5%): 90
           >>> p1
           0.9
           >>> p2 = ui.getPercent()
           Please enter a percentage (e.g. 90.5%): 90%
           >>> p2
           0.9
       
       Response must be an integer between 0 and 100 (inclusive). As with
       the other methods, :meth:`.getPercent` will re-prompt if response
       is invalid.
       
       Args:
         prompt (str, optional): Prompt to pass to :func:`raw_input`. If
           omitted, the user is prompted with ``"Please enter a percentage
           (e.g. 90.5%): "``.
         default (optional): Value to return if user response is empty
           string.
       
       Returns:
         Either a float or the value of *default*.
       
       """
    if prompt == None:
      prompt = "Please enter a percentage (e.g. 90.5%): "
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
  
  def reserveFilePath(self, prompt=None, allow_overwrite=False):
    """Prompt user for a path to create or overwrite a file.
    
    Uses :func:`raw_input` to prompt for a file path, which can either be
    an absolute or relative path. User's response must either be a path
    that does not point to any files, or a path to an existing file (not a
    directory). If the path is to an existing file and *allow_overwrite*
    is ``False``, the user will be prompted for whether to overwrite the
    file. Otherwise the path will be returned without any complaint.
    
    Args:
      prompt (str, optional): Prompt ot pass to :func:`raw_input`. If
        omitted, the user is prompted with ``"Please input file name: "``.
      allow_overwrite (bool, optional): Whether to prompt user if path
        points to exising file.
    
    Returns:
      A string containing a path not pointing to a directory.
    
    """
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
    """Prompt user for a path to create or overwrite a directory.
    
    Uses :func:`raw_input` to prompt for a directory path, which can be an
    absolute or relative path. User's response must be either a path that
    does not point to any files or directories, or must point to an
    existing directory. If the directory already exists, the user is
    prompted for whether to overwrite the directory.
    
    The user can specify a directory extension. If the user's
    response does not end with the given extension, *extension* is
    automatically appended.
    
    Example:
      Prompting for directory with extension::
      
        >>> ui = CommandLineInterface()
        >>> dirname = ui.reserveDirectory(extension='.sima')
        Please input a directory name: new_dir
        >>> dirname
        'new_dir.sima'
    
    Args:
      prompt (str, optional): Prompt to pass to :func:`raw_input`. If
        omitted, the user is prompted with ``"Please input a directory
        name: "``.
      extension (str, optional): Directory extension to add if not
        already included in user's response.
    
    Returns:
      A string containing a path not pointing to any file (including any
        directories), or pointing to an existing directory.
    
    """
    if prompt == None:
      prompt = "Please input a directory name: "
    path = raw_input(prompt)
    if not path.endswith(extension):
      path += extension
    if isfile(path):
      prompt = "The name you entered is a file and already exists, " + \
               "please try again: "
      self.reserveDirectory(prompt, extension)
    if isdir(path):
      prompt = "The directory you entered already exists, " + \
                "do you want to use it anyway? (y/n): "
      if not self.getBoolean(prompt):
        return self.reserveDirectory(None, extension)
    return path
  
class IdROIs(PostProcessingStep):
  """A SIMA segmentation post-processing step to give IDs to rois"""
  def apply(self, rois, dataset=None):
    rois_with_ids = []
    for index, roi in enumerate(rois):
      newroi = roi.todict()
      newroi['id'] = index
      rois_with_ids.append(newroi)
    return ROIList(rois_with_ids)
  
class SaraUI(CommandLineInterface):
  """An IPython-friendly CLI meant to interface with `SIMA`_.
  
  Example usage is demonstrated in ``serial.py`` and ``SARA.ipynb``.
  
  When used from an IPython notebook, one can simply initialize without
  explicit parameters::
    
    ui = sara.SaraUI()
  
  You will be prompted for the relevant options. If the SIMA analysis
  directory path or settings file paths are already known, you can
  specify either one or both like so::
    
    ui = sara.SaraUI(sima_dir='mydir.sima', settings_file='settings.csv')
  
  Note that choosing the former approach will cause ``".sima"`` to be
  appended to the end of the directory name you choose if it does not
  already end in ``".sima"``.
  
  The latter approach is **required** if running from outside the IPython
  notebook environment, as there is no way to display the radio buttons
  for selecting signal output format and motion-correction strategy. These
  options will be read from *settings_file*.
  
  It is recommended to use ``SARA.ipynb`` to test settings on a few
  recordings individually. This will cause a settings file to be generated,
  which can be edited manually and loaded outside of an IPython
  environment.
  
  Attributes:
    dataset (sima.ImagingDataset): Dataset from :data:`sima_dir`,
      loaded with :meth:`sima.ImagingDataset.load`.
    mc_radio (IPython.html.widgets.widget_selection.RadioButtonsWidget):
      Radio Button widget for choosing motion-correction strategy.
    rois (sima.ROI.ROIList): ROIs that were found by :meth:`.segment`.
    sequence (sima.Sequence): Imaging sequence generated using
      :meth:`sima.Sequence.create` when :meth:`.motionCorrect` is called.
    settings_file (str): File to save settings used for analysis.
    sima_dir (str): Name of analysis directory used by SIMA.
    signal : **TODO**
    signal_radio (IPython.html.widgets.widget_selection.RadioButtonsWidget):
      Radio Button widget for whether to convert "frames" column of signal
      output to time format.
    mu : **deprecated**
    components : **deprecated**
    overlap_per : **deprecated**
    image : **deprecated**
    image_height : **deprecated**
    image_width : **deprecated**
    signal_output : **deprecated**
  
  .. _SIMA:
    http://www.losonczylab.org/sima/1.0/index.html
  
  """
  
  def __init__(self, sima_dir=None, settings_file=None):
    # general parameters
    if sima_dir == None:
      prompt = "Name of SIMA analysis directory (ends with .sima): "
      self.sima_dir = self.reserveDirectory(prompt, '.sima')
    else:
      self.sima_dir = sima_dir
    if settings_file == None:
      prompt = "Path to save settings: "
      self.settings_file = self.reserveFilePath(prompt)
      self.settings = None
    else:
      self.settings_file = settings_file
      self.settings = Series.from_csv(settings_file)
    self.sequence = None
    self.dataset = None
    self.rois = None
    # segmentation parameters
    self.mu = -1.0
    self.components = -1
    self.overlap_per = 0.0
    # visualization parameters
    self.image = None
    self.image_height = None
    self.image_width = None
    # signal extraction parameters
    self._signal_output = ['time', 'frame number']
    self.signal = None
    # motion correction parameters
    self.mc_radio = None
    # maps radio options to function calls, shown in alphabetical order
    self._motion_correction_map = {
      "2D Plane Correction" : self._planeTranslation2D,
    }
    # If SaraUI is initialized outside of IPython,
    # a settings file MUST BE USED
    if ipython_loaded():
      options = self._motion_correction_map.keys()
      options.sort() # force alphabetical order
      label = "Motion correction strategy:"
      self.strategy_radio = self._showRadio(label, options)
      label = "Label signal output by time or by frame number?"
      self.signal_radio = self._showRadio(label, self._signal_output)

  def exportSignal(self, outfile=None, use_settings=False):
    """Write ROI signals to a file.
    
    Uses settings from :data:`signal_radio` or (if *use_settings* is True)
    :data:`settings_file`.
    
    Args:
      outfile (str, optional): where to store signal; if None or omitted,
        :meth:`.exportSignal` will prompt the user for a location
      use_settings (bool, optional): Whether to use the settings stored in
        :data:`settings_file`. If False, user is prompted for settings.
    
    """
    
    frames_to_time = None
    # initialize dataset and rois
    if self.rois == None:
      if self.dataset == None:
        self.dataset = ImagingDataset.load(self.sima_dir)
      self.rois = self.dataset.ROIs['stICA ROIs']
    # prompt user for export path if it hasn't already been provided
    if outfile == None:
      prompt = "File path to export to: "
      outfile = self.reserveFilePath(prompt)
    # get the frames to time conversion factor
    if use_settings and self.settings['signals_format'] == 'time':
      frames_to_time = float(self.settings['frames_to_time'])
    elif self.signal_radio.value == 'time':
      prompt = "Please input the recording's capture rate " + \
               "(seconds per frame): "
      while frames_to_time <= 0:
        frames_to_time = self.getFloat(prompt)
        prompt = "The number you entered is not a valid capture rate" + \
                 ", please try again: "
      self.signal_radio.close()
    # check if we've already extracted a signal
    if self.dataset.signals() == {}:
      print "Extracting signals from ROIs..."
      stdout.flush() # force print statement to output to IPython
      self.signal = self.dataset.extract(rois=self.rois, label='signal')
      print "Signals extracted"
    else:
      self.signal = self.dataset.signals()['signal']
    self.dataset.export_signals(outfile)
    # do we need to post-process the CSV?
    if frames_to_time != None:
      self._postProcessSignal(outfile, frames_to_time)
    
    # update settings file unless it's unnecessary
    if not use_settings:
      signal_settings = {
        'signals_file'   : abspath(outfile),
        'signals_format' : self.signal_radio.value,
        'frames_to_time' : frames_to_time,
      }
      self._updateSettingsFile(signal_settings)
    print "Signals Exported to", outfile
  
  def getPNG(self, prompt=None):
    """Prompts user for the path to an existing PNG image.
    
    A shortcut method for :meth:`.getFileWithExtension`.
    
    Args:
      prompt (str, optional): Prompt to pass to :func:`raw_input`.
    
    """
    if prompt == None:
      prompt = "File path to your PNG image: "
    extension = {"PNG" : '.png'}
    image_path = self.getFileWithExtension(prompt, extension)
    return image_path

  def getString(self, prompt=None):
    """**deprecated**"""
    return raw_input(prompt)
  
  def getTIFF(self, prompt=None):
    """Prompts user for the path to an existing TIFF image.
    
    A shortcut method for :meth:`.getFileWithExtension`.
    
    Args:
      prompt (str, optional): Prompt to pass to :func:`raw_input`.
    
    """
    if prompt == None:
      prompt = "File path to your TIFF image: "
    extension = {"TIFF" : ['.tif', '.tiff']}
    image_path = self.getFileWithExtension(prompt, extension)
    return image_path
  
  def motionCorrect(self, input_path=None, output_path=None, use_settings=False):
    """Perform motion correction on a recording and export frames.
    
    Uses settings from :data:`mc_radio` or (if *use_settings* is True)
    :data:`settings_file`. 
    
    Args:
      input_path (str, optional) : File path to the image to be corrected.
        If None, user is prompted for location.
      output_path (str, optional): File path to export corrected frames. If
        None, user is prompted for location.
      use_settings (bool, optional): Whether to use the settings stored in
        :data:`settings_file`. If False, user is prompted for settings.
    
    """
    # sima uses the builtin input() function, which is not compatible with IPython
    if isdir(self.sima_dir):
      if ipython_loaded():
        warnings.warn("You cannot perform motion correction using an" + \
                      " existing SIMA analysis directory")
        return # exit before we screw something up
     
    if input_path == None:
      # currently only TIFF is supported by SARA
      prompt = "File path to the image you want corrected (TIFF only): "
      input_path = self.getTIFF(prompt)
    
    if output_path == None:
      prompt = "Where would you like to save the corrected frames? "
      self.corrected_frames = self.reserveFilePath(prompt)
    else:
      self.corrected_frames = output_path
    
    self.sequence = Sequence.create('TIFF', input_path)
    if use_settings:
      md_x = int(self.settings['max_displacement_x'])
      md_y = int(self.settings['max_displacement_y'])
    else:
      prompt = ["Maximum %s displacement (in pixels; default 100): " \
                 % ax for ax in ['X', 'Y']]
      md_x = self.getNatural(prompt[0], default=100)
      md_y = self.getNatural(prompt[1], default=100)
    mc_settings = {"max_displacement" : [md_x, md_y]}
    
    if use_settings:
      strategy = self.settings['correction_strategy']
      self._motion_correction_map[strategy](mc_settings)
    else:
      # By this time, the user should have selected a strategy
      self.strategy_radio.close()
      self._motion_correction_map[self.strategy_radio.value](mc_settings)
      
      # export settings we used to settings file
      mc_settings = {
        'uncorrected_image'   : abspath(input_path),
        'corrected_image'     : abspath(self.corrected_frames),
        'max_displacement_x'  : md_x,
        'max_displacement_y'  : md_y,
        'correction_strategy' : self.strategy_radio.value,
      }
      self._updateSettingsFile(mc_settings)
  
  def _planeTranslation2D(self, mc_settings):
    """Performs motion correction with 2D Plane Translation.
    
    Uses :meth:`sima.motion.PlaneTranslation2D` with settings chosen
    in :meth:`.motionCorrect`.
    
    Args:
      mc_settings (dict) : The settings to use for motion correction.
    
    """
    print "Performing motion correction with 2D Plane Correction " + \
          "(this could take a while) . . ."
    stdout.flush() # force print statement to output to IPython
    self.dataset = PlaneTranslation2D(**mc_settings).correct(
                     [self.sequence], self.sima_dir)
    print "Motion correction complete"
    self.dataset.export_frames([[[self.corrected_frames]]])
  
  def _postProcessSignal(self, signal_file, frames_to_time):
    """Convert "frame" of signal output column to time format.
    
    Args:
      signal_file (str): File containing signal data.
      frames_to_time (float): Conversion factor in seconds per frame.
    
    """
    # read in tab-separated data
    data = read_csv(signal_file, sep='\t')
    
    # change name of 'frames' col to 'time'
    old_cols = data.columns.tolist()
    new_cols = [old_cols[0], 'time'] + old_cols[2:]
    # preserve useless labels/tags in case they are someday useful
    lab_tag = data['frame'].tolist()[:2]
    
    # cast frames from str to float so we can do math
    times = map(float, data['frame'].tolist()[2:])
    # convert frame number to time
    times = map(lambda x: x*frames_to_time, times)
    
    # prepare new data for output
    times = Series(lab_tag + times)
    data['frame'] = times
    data.columns = new_cols
    
    # export back to CSV
    data.to_csv(signal_file, sep='\t')
  
  def segment(self, use_settings=False):
    """Performs Spatiotemporal Independent Component Analysis.
    
    Currently only has options to use :class:`sima.segment.STICA`. User is
    prompted for parameters necessary to perform stICA. If *use_settings*
    is True, the settings from :data:`settings_file` are used instead.
    
    Args:
      use_settings (bool, optional): Whether to use the settings stored in
        :data:`settings_file`. If False, user is prompted for settings.
    
    """
    if use_settings:
      self.components = int(self.settings['components'])
      self.mu = float(self.settings['mu'])
      self.overlap_per = float(self.settings['overlap_per'])
    else:
      prompt = "Number of PCA components (default 50): "
      self.components = self.getNatural(prompt, default=50)
      prompt = "mu (default 0.5): "
      mu = -1.0
      while self.mu < 0 or self.mu > 1:
        self.mu = self.getFloat(prompt, default=0.5)
      prompt = "Minimum overlap " + \
               "(default 20%; enter 0 to skip): "
      self.overlap_per = self.getPercent(prompt, default=0.2)
    segment_settings = {
      'components' : self.components,
      'mu' : self.mu,
      'overlap_per' : self.overlap_per,
    }
    print "Performing Spatiotemporal Independent Component Analysis..."
    stdout.flush()
    stica = STICA(**segment_settings)
    stica.append(IdROIs())
    if self.dataset == None:
      self.dataset = ImagingDataset.load(self.sima_dir)
    self.rois = self.dataset.segment(stica, label="stICA ROIs")
    print len(self.dataset.ROIs['stICA ROIs']), "ROIs found"
    
    if not use_settings:
      segment_settings['segmentation_strategy'] = 'stICA'
      self._updateSettingsFile(segment_settings)
  
  def _showRadio(self, label, options, default=None):
    """Displays a radio button"""
    if default == None:
      default = options[0]
    radio = widgets.RadioButtonsWidget(
              description=label, values=options, value=default)
    display(radio)
    return radio
  
  def _updateSettingsFile(self, new_settings):
    if isfile(self.settings_file):
      old_settings = Series.from_csv(self.settings_file)
      for setting, value in new_settings.iteritems():
        if type(value) == list:
          # represent lists as csv encapsulated in quotes
          value = ','.join(map(str, value))
        old_settings[setting] = value
    else:
      old_settings = Series(new_settings)
    old_settings.to_csv(self.settings_file)
  
  def visualize(self, save_to=None, rgb_png=None, use_settings=False, warn=False):
    """Use matplotlib to show what ROIs were chosen by :meth:`.segment`.
    
    Args:
      save_to (str, optional): Where to save the image matplotlib
        generates. If None, the image is displayed instead.
      rgb_png (str, optional): Path to a 24-bit PNG file to use as a
        background for displaying ROIs.
      use_settings (bool, optional): Whether to use the settings stored in
        settings_file. Modifiable settings include *color_cycle*, and
        *linewidth*. If *rgb_png* is not given, will use *rgb_frame* from
        :data:`settings_file`.
      warn (bool, optional): Whether to print the IDs of ROIs with internal
        loops. See the `Shapely`_ documentation for more information.
      
    .. _Shapely:
      http://toblerity.org/shapely/manual.html
     
    """
    if use_settings:
      vis_settings = {
        "color_cycle" : self.settings['color_cycle'].split(','),
        "linewidth"   : self.settings['linewidth'],
      }
    else:
      vis_settings = {
        "color_cycle" : ['blue', 'red', 'magenta', 'brown', 'cyan',
                        'orange', 'yellow', 'green'],
        "linewidth" : 2,
      }
    plt.rc('axes', color_cycle=vis_settings['color_cycle'])
    plt.rc('lines', linewidth=vis_settings['linewidth'])
    # Weird things happen if we try to visualize multiple images
    # without doing this
    plt.clf()
    
    # prepare background image
    if use_settings:
      if rgb_png == None:
        rgb_png = self.settings['rgb_frame']
    else:
      prompt = "File path to an RGB, PNG background image: "
      rgb_png = self.getPNG(prompt)
    print "Using", rgb_png, "for rgb.png"
    self.image = Image.open(rgb_png)
    self.image_width, self.image_height = self.image.size
    plt.xlim(xmin=0, xmax=self.image_width)
    plt.ylim(ymin=0, ymax=self.image_height)
    plt.imshow(self.image)
    
    # get list of ROIs from SIMA analysis directory
    #rois = ROIList.load(path_join(self.sima_dir, "rois.pkl"))
    if self.rois == None:
      if self.dataset == None:
        self.dataset = ImagingDataset.load(self.sima_dir)
      self.rois = self.dataset.ROIs['stICA ROIs']
    
    # plot all of the ROIs, warn user if an ROI has internal loops
    for roi in self.rois:
      coords = roi.coords
      if warn and len(coords) > 1:
        print "Warning: Roi%s has >1 coordinate set" % roi.id
      x = coords[0][:,0]
      y = coords[0][:,1]
      plt.plot(x, y)
    
    if save_to != None:
      plt.savefig(save_to)
    else:
      plt.show()
    
    if not use_settings:
      vis_settings['rgb_frame'] = abspath(rgb_png)
      vis_settings['rgbf_width'] = self.image_width
      vis_settings['rgbf_height'] = self.image_height
      self._updateSettingsFile(vis_settings)
