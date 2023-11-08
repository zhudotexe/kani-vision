API Reference
=============

Message Parts
-------------

.. autoclass:: kani.ext.vision.ImagePart
    :members:
    :class-doc-from: class

The following classes are the types constructed by the ImagePart methods.

.. autoclass:: kani.ext.vision.parts.FileImagePart
    :class-doc-from: class

.. autoclass:: kani.ext.vision.parts.BytesImagePart
    :class-doc-from: class

.. autoclass:: kani.ext.vision.parts.PillowImagePart
    :class-doc-from: class

.. autoclass:: kani.ext.vision.parts.RemoteURLImagePart
    :class-doc-from: class

Engines
-------
.. autoclass:: kani.ext.vision.engines.openai.OpenAIVisionEngine
    :members:
    :show-inheritance:

.. autoclass:: kani.ext.vision.engines.llava.LlavaEngine
    :members:
    :show-inheritance:
