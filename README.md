# NanoScope AFM

Library to handle parsing and processing of Nanoscope Dimension AFM files. Currently hard-coded to only work for version 0x05120130, but it will likely work on newer versions.

## Usage

An example of typical usage is shown below, including using Pillow to save the image to png.

    import nanoscope
    from PIL import Image

    p = nanoscope.NanoscopeParser('./file.000')
    p.read_file()
    p.height.flatten(order=1).convert()
    print(p.height.zrange(), p.height.rms())
    pixels = p.height.colorize(colortable=12)
    Image.fromarray(pixels).save('file.png')
