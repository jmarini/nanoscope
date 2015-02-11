NanoScope AFM
==============

.. image:: https://travis-ci.org/jmarini/nanoscope.svg?branch=master
        :target: https://travis-ci.org/jmarini/nanoscope

.. image:: https://coveralls.io/repos/jmarini/nanoscope/badge.svg
        :target: https://coveralls.io/r/jmarini/nanoscope

Library to handle parsing and processing of Nanoscope Dimension AFM files. Currently hard-coded to only work for version 0x05120130, but it will likely work on newer versions.

Usage
-----

An example of typical usage is shown below, including using Pillow to save the image to png.

.. code:: python

    import nanoscope
    from PIL import Image

    p = nanoscope.NanoscopeParser('./file.000')
    p.read_file()
    p.height.flatten().convert()
    print(p.height.zrange, p.height.rms)
    pixels = p.height.colorize()
    Image.fromarray(pixels).save('file.png')
