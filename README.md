Installation
============

## Python tools
1. download source `git clone https://github.com/pndni/pndni_utils.git`
2. `pip install -e pndni_utils` (Note, if you're not using a virtual
   environment, you will probably need to use
   `pip install --user -e pndni_utils`)
   
## Bash tools
1. download source `git clone https://github.com/pndni/pndni_utils.git`
2. `export PATH=$PATH:$PWD/pndni_utils/bin` (or add this command to your `.bashrc`
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

### combinelabels

Combine multiple label files into one, where output labels are the intersection
of the input labels. For example, if labelfile1.nii and labelfile2.nii have the following
labels:

| labelfile1.nii label name | Value |
| ------------------------- | ----- |
| Grey matter               |     1 |
| White matter              |     2 |

| labelfile2.nii label name | Value |
| ------------------------- | ----- |
| Left hemisphere           |     1 |
| Right hemisphere          |     2 |

the command
```bash
combinelabels out.nii labelfile1.nii labelfile2.nii
```
will result in

| out.nii label name         | Value |
| -------------------------- | ----- |
| Grey matter + left hemi.   |     1 |
| White matter + left hemi.  |     2 |
| Grey matter + right hemi.  |     3 |
| White matter + right hemi. |     4 |

A value of 0 in any label file will result in 0 in the output.

More than two label files may be used. For example
```bash
combinelabels out.nii labelfile1.nii labelfile2.nii labelfile3.nii
```
is equivalent to
```bash
combinelabels tmp.nii labelfile1.nii labelfile2.nii
combinelabels out.nii tmp.nii labelfile3.nii
```

### labels2probmaps

Create probability maps for multiple label files. See `labels2probmaps --help`

### swaplabels

Swap/remap labels in an image. For example, to change all the values of 2 in the image to 1 and all the values of 5 to 10
```bash
swaplabels "2: 1, 5: 10" input.nii output.nii
```
Any unspecified value will be set to 0.

### flattenhtml

Convert an html file with dependent png images into a flat file (i.e., embed those images into the html file). Currently only
png images are supported, and any other image format will cause an error.

```bash
flattenhtml input.html > output.html
```

## Bash
### combined_dirs.sh

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
