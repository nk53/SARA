from sima.ROI import ROI, ROIList
from sima.segment.segment import PostProcessingStep

class IdROIs(PostProcessingStep):
  def apply(self, rois, dataset=None):
    rois_with_ids = []
    for index, roi in enumerate(rois):
      newroi = roi.todict()
      newroi['id'] = index
      rois_with_ids.append(newroi)
    return ROIList(rois_with_ids)
