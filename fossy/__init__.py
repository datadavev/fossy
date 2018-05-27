'''

'''

import logging
import requests
import xml.etree.ElementTree as ET

class FosscamCamera(object):

  QUALITY_LOW = 2
  QUALITY_NORMAL = 2
  QUALITY_HIGH = 2


  def __init__(self, config):
    self._L = logging.getLogger(self.__class__.__name__)
    self.url = config['address'] + "cgi-bin/CGIProxy.fcgi"
    self.params = {'usr': config['user'],
                   'pwd': config['password']}


  def listPTZpoints(self):
    data = self.params
    data['cmd'] = 'getPTZPresetPointList'
    self._L.debug(self.url)
    response = requests.get(self.url, params=data)
    xml = ET.fromstring(response.text)
    results = []
    for child in xml:
      if child.tag.startswith("point"):
        preset = child
        if not preset.text is None:
          self._L.debug(preset)
          results.append(preset.text)
    return results


  def gotoPTZPoint(self, preset_point):
    data = self.params
    data['cmd'] = 'ptzGotoPresetPoint'
    data['name'] = preset_point
    self._L.debug(self.url)
    response = requests.get(self.url, params=data)
    return response.text


  def setSnapConfig(self, quality=QUALITY_HIGH):
    data = self.params
    data['cmd'] = 'setSnapConfig'
    data['snapPicQuality'] = quality
    self._L.debug(self.url)
    response = requests.get(self.url, params=data)
    return response


  def getStaticImage(self, dest_fn):
    data = self.params
    data['cmd'] = 'snapPicture2'
    self._L.debug(self.url)
    response = requests.get(self.url, params=data)
    with open(dest_fn, "wb") as dest_file:
      dest_file.write(response.content)
    return True
