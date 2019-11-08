.. pndni_utils documentation master file, created by
   sphinx-quickstart on Tue Aug 27 18:41:23 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

***************************************
Welcome to pndni_utils's documentation!
***************************************

************
Installation
************

Python tools
============

#. download source ``git clone https://github.com/pndni/pndni_utils.git``
#. ``pip install -e pndni_utils`` (Note, if you're not using a virtual
   environment, you will probably need to use
   ``pip install --user -e pndni_utils``)
   
Bash tools
==========
#. download source ``git clone https://github.com/pndni/pndni_utils.git``
#. ``export PATH=$PATH:$PWD/pndni_utils/bin`` (or add this command to your ``.bashrc``
   to make persistent, with $PWD expanded appropriately)


**********************
Command Line Utilities
**********************

allequal
========

.. argparse::
   :prog: allequal
   :module: pndni.all_equal
   :func: get_parser


combined_dirs.sh
================

``combine_dirs.sh`` combines multiple directories. If multiple files of the same
name exist, ``combine_dirs.sh`` ensures that they are equal or returns with status 1

Example
-------

Say we have a folder organized as::

    .
    ├── out-1
    │   ├── info.txt
    │   └── sub-1
    │       └── result.txt
    ├── out-2
    │   ├── info.txt
    │   └── sub-2
    │       └── result.txt
    └── out-3
        ├── info.txt
        └── sub-3
            └── result.txt

where all the `info.txt` are identical.
Running

.. code-block:: bash

    mkdir combined
    combine_dirs combined out*/*

results in::

    .
    ├── combined
    │   ├── info.txt
    │   ├── sub-1
    │   │   └── result.txt
    │   ├── sub-2
    │   │   └── result.txt
    │   └── sub-3
    │       └── result.txt
    ├── out-1
    │   ├── info.txt
    │   └── sub-1
    │       └── result.txt
    ├── out-2
    │   ├── info.txt
    │   └── sub-2
    │       └── result.txt
    └── out-3
        ├── info.txt
        └── sub-3
            └── result.txt


combinelabels
=============

.. argparse::
   :prog: combinelabels
   :module: pndni.combinelabels
   :func: get_parser

create_readme
=============

Creates a starting point readme file. Calling ``create_readme file1 file2 file3`` will write the following to stdout

.. code-block:: yaml

    Name:
    Dataset:
    Authors:
    PI: 
    Description:
    Scripts:
      -name: file1
       desc:
       md5sum: FILE1_MD5
      -name: file2
       desc:
       md5sum: FILE2_MD5
      -name: file3
       desc:
       md5sum: FILE3_MD5
    Outputs:
    Server:
    Notes:



convertpoints
=============

.. argparse::
   :prog: convertpoints
   :module: pndni.convertpoints
   :func: get_parser
	  
flattenhtml
===========

.. argparse::
   :prog: flattenhtml
   :module: pndni.flattenhtml
   :func: get_parser


forceqform
==========
.. argparse::
   :prog: forceqform
   :module: pndni.forceqform
   :func: get_parser


fscombine
=============

.. argparse::
   :prog: fscombine
   :module: pndni.fscombine
   :func: get_parser


labels2probmaps
===============

.. argparse::
   :prog: labels2probmaps
   :module: pndni.labels2probmaps
   :func: get_parser


minc_default_dircos
===================

.. argparse::
   :prog: minc_default_dircos
   :module: pndni.minc_default_dircos
   :func: get_parser


mnclabel2niilabel
=================

.. argparse::
   :prog: mnclabel2niilabel
   :module: pndni.mnclabel2niilabel
   :func: get_parser


niftiheader
===========

Output the nifti header using hexdump


stats
=====

.. argparse::
   :prog: stats
   :module: pndni.stats
   :func: get_parser

	  
swaplabels
=============

.. argparse::
   :prog: swaplabels
   :module: pndni.swaplabels
   :func: get_parser
