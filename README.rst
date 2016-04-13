NanoScope AFM
==============

.. image:: https://travis-ci.org/jmarini/nanoscope.svg?branch=master
        :target: https://travis-ci.org/jmarini/nanoscope

.. image:: https://coveralls.io/repos/jmarini/nanoscope/badge.svg
        :target: https://coveralls.io/r/jmarini/nanoscope

Nanoscope is a library to handle parsing and processing of Veeco Nanoscope Dimension AFM files. Currently hard-coded to only work for version 0x05120130 since that is what I have access to for testing, but it will likely work on newer versions.


Features
--------

The current featureset includes:

* Read raw Nanoscope files and image data (height, amplitude, phase)
* Calculate standard summary information (RMS Roughness, Z-range, etc.)
* Output the image in a Pillow-compatible format for saving
* Data is cached after individual process steps to avoid unneeded reprocessing


Installation
------------

Nanoscope can be easily installed using pip.

.. code::

    $ pip install nanoscope


Usage
-----

An example of typical usage is shown below, including using Pillow to save the image to png and printing Z-range and RMS data to the console

.. code:: python

    import nanoscope
    from PIL import Image

    p = nanoscope.read('./file.000')
    p.height.process()
    print(p.height.zrange, p.height.rms)
    pixels = p.height.colorize()
    Image.fromarray(pixels).save('file.png')


The various image types can also be looped through using an iterator when processing, and the settings of the processing steps customized

.. code:: python

    import nanoscope

    p = nanoscope.read('./file.000')
    for img in p:
        img.process(order=2)  # flatten the image using second-order function
        print(img.type, img.rms)


The processing steps can also be called individually if needed

.. code::python

    import nanoscope
    p = nanoscope.read('./file.000')
    p.height.flatten()  # flatten the image, defaults to first-order flatten
    p.height.convert()  # convert the raw data to scaled values
