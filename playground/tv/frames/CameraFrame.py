from .imshowFrame import *
from matplotlib.colors import SymLogNorm, LogNorm

class CameraFrame(imshowFrame):
	frametype='Camera'
	def __init__(self, *args, **kwargs):

		imshowFrame.__init__(self, *args, **kwargs)

		# tidy up the axes for this camera
		self.ax.set_aspect('equal')
		plt.setp(self.ax.get_xticklabels(), visible=False)
		plt.setp(self.ax.get_yticklabels(), visible=False)
		self.ax.set_facecolor('black')

# FIXME -- make sure I understand the geometry here (I don't think I do now)
class Camera1Frame(CameraFrame):
	frametype='Camera 1'
	def _transformimage(self, image):
		'''
		horizontal:
		+x is up, +y is left
		'''
		if self._get_orientation() == 'horizontal':
			return image.T[:, :]

class Camera2Frame(CameraFrame):
	frametype='Camera 2'
	def _transformimage(self, image):
		'''
		horizontal:
		+x is up, +y is left
		'''
		if self._get_orientation() == 'horizontal':
			return image.T[:, :]

class Camera3Frame(CameraFrame):
	frametype='Camera 3'
	def _transformimage(self, image):
		'''
		horizontal:
		+x is down, +y is right
		'''
		if self._get_orientation() == 'horizontal':
			return image.T[::-1, ::-1]

class Camera4Frame(CameraFrame):
	frametype='Camera 4'
	def _transformimage(self, image):
		'''
		horizontal:
		+x is down, +y is right
		'''
		if self._get_orientation() == 'horizontal':
			return image.T[::-1, ::-1]

cameras = {'cam1':Camera1Frame, 'cam2':Camera2Frame, 'cam3':Camera3Frame, 'cam4':Camera4Frame}
