Installation
============

## Python
1. download source `git clone https://github.com/pndni/pndni_utils.git`
2. `pip install -e pndni_utils` (Note, if you're not using a virtual
   environment, you will probably need to use
   `pip install --user -e pndni_utils`)
   
## Bash
1. download source `git clone https://github.com/pndni/pndni_utils.git`
2. `export PATH=$PATH:$PWD/pndni_utils/bash` (or add this command to your `.bashrc`
   to make persistent, with $PWD expanded appropriately)
   
Command line utilities
======================

## Python
### fscombine

`fscombine` combines data extracted with freesurfer's `asegstats2table`
and `aparcstats2table` into one file. 

#### Example

```bash
fscombine aparc_area_lh_small.txt aseg_mean_small.txt aseg_volume_small.txt out.txt
```

### mnclabel2niilabel

Converts a minc file to a nifti file using `mnc2nii`, then rounds all the data 
to the nearest integer and converts the nifti file to uint8. Checks that
all the values are within 0.1 of the nearest integer.

#### Example
```bash
mnclabel2niilabel input.mnc output.nii
```

## Bash
## combined_dirs.sh

`combine_dirs.sh` combines multiple directories. If multiple files of the same
name exist, `combine_dirs.sh` ensures that they are equal or returns with status 1

#### Example

Say we have a folder organized as
```.
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
```
where all the `info.txt` are identical.
Running
```bash
mkdir combined
combine_dirs combined out*/*
```
results in
```
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
```

## create_readme

Creates a starting point readme file. Calling `create_readme file1 file2 file3` will write the following to stdout
```yaml
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

```
