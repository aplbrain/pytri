pytri
===============================

A jupyter wrapper for substrate

Installation
------------

To install use pip:

    $ pip install pytri
    $ jupyter nbextension enable --py --sys-prefix pytri


For a development installation (requires npm),

    $ git clone https://github.com/jtpdowns/pytri.git
    $ cd pytri
    $ pip install -e .
    $ jupyter nbextension install --py --symlink --sys-prefix pytri
    $ jupyter nbextension enable --py --sys-prefix pytri
