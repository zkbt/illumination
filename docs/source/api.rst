.. _api:

API
===

This page details the methods and classes provided by the
``playground.tv`` package. All sequences inherit from the
:class:`Sequence`, all frames inherit from the :class:`FrameBase`,
and all illustrations inherit from the :class:`IllustrationBase`.

Sequences
---------
All these sequences keep track of timed datasets.

.. automodule:: playground.tv.sequences
  :members:
.. autoclass:: playground.tv.sequences.Sequence
  :members:
.. autoclass:: playground.tv.sequences.FITS_Sequence
  :members:
.. autoclass:: playground.tv.sequences.Stamp_Sequence
  :members:
.. autoclass:: playground.tv.sequences.TPF_Sequence
  :members:
  
Frames
------
All these frames provide windows for displaying sequences.

.. autoclass:: playground.tv.frames.FrameBase
  :members:
.. autoclass:: playground.tv.frames.imshowFrame
  :members:
.. autoclass:: playground.tv.frames.EmptyTimeseriesFrame
.. autoclass:: playground.tv.frames.ZoomFrame
.. autoclass:: playground.tv.frames.LocalZoomFrame
.. autoclass:: playground.tv.frames.CameraFrame
.. autoclass:: playground.tv.frames.CCDFrame

Illustrations
-------------
All these illustrations provide layouts in which to place frames.

.. autoclass:: playground.tv.illustrations.IllustrationBase
   :members:
.. autoclass:: playground.tv.illustrations.GenericIllustration
.. autoclass:: playground.tv.illustrations.CameraIllustration
.. autoclass:: playground.tv.illustrations.FourCameraIllustration
.. autoclass:: playground.tv.illustrations.SingleCameraWithZoomIllustration
.. autoclass:: playground.tv.illustrations.SideBySideIllustration
