.. _api:

API
===

This page details the methods and classes provided by the
``illumination`` package. All sequences inherit from the
:class:`Sequence`, all frames inherit from the :class:`FrameBase`,
and all illustrations inherit from the :class:`IllustrationBase`.

Sequences
---------
All these sequences keep track of timed datasets.

.. automodule:: illumination.sequences
  :members:
.. autoclass:: illumination.sequences.Sequence
  :members:
.. autoclass:: illumination.sequences.FITS_Sequence
  :members:
.. autoclass:: illumination.sequences.Stamp_Sequence
  :members:
.. autoclass:: illumination.sequences.TPF_Sequence
  :members:

Frames
------
All these frames provide windows for displaying sequences.

.. autoclass:: illumination.frames.FrameBase
  :members:
.. autoclass:: illumination.frames.imshowFrame
  :members:
.. autoclass:: illumination.frames.EmptyTimeseriesFrame
.. autoclass:: illumination.frames.ZoomFrame
.. autoclass:: illumination.frames.LocalZoomFrame
.. autoclass:: illumination.frames.CameraFrame
.. autoclass:: illumination.frames.CCDFrame

Illustrations
-------------
All these illustrations provide layouts in which to place frames.

.. autoclass:: illumination.illustrations.IllustrationBase
   :members:
.. autoclass:: illumination.illustrations.GenericIllustration
.. autoclass:: illumination.illustrations.CameraIllustration
.. autoclass:: illumination.illustrations.FourCameraIllustration
.. autoclass:: illumination.illustrations.SingleCameraWithZoomIllustration
.. autoclass:: illumination.illustrations.SideBySideIllustration
