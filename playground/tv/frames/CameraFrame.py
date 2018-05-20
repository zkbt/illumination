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


		self.xmin, self.ymin = 0, 0
		self.ymax, self.xmax = self.data[0].shape
		# need to implement something for a camera that has no image in it


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

	def _transformxy(self, x, y):
		'''
		This handles the same transformation as that which goes into
		transform image, but for x and y arrays.
		'''
		if self._get_orientation() == 'horizontal':
			displayy = x
			displayx = self.ymax-y
		return x, y

class Camera2Frame(Camera1Frame):
	frametype='Camera 2'


class Camera3Frame(CameraFrame):
	frametype='Camera 3'
	def _transformimage(self, image):
		'''
		horizontal:
		+x is down, +y is right
		'''
		if self._get_orientation() == 'horizontal':
			return image.T[::-1, ::-1]

	def _transformxy(self, x, y):
		'''
		This handles the same transformation as that which goes into
		transform image, but for x and y arrays.
		'''
		if self._get_orientation() == 'horizontal':
			displayy = self.xmax - x
			displayx = y
		return x, y

class Camera4Frame(Camera3Frame):
	frametype='Camera 4'


cameras = {'cam1':Camera1Frame, 'cam2':Camera2Frame, 'cam3':Camera3Frame, 'cam4':Camera4Frame}
