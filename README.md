Installation
============

1. download source `git clone https://github.com/pndni/pndni_utils.git`
2. `pip install -e pndni_utils` (Note, if you're not using a virtual
   environment, you will probably need to use
   `pip install --user -e pndni_utils`)
   
   
Command line utilities
======================

## fscombine

`fscombine` combines data extracted with freesurfer's `asegstats2table`
and `aparcstats2table` into one file. 

### Example

```bash
fscombine aparc_area_lh_small.txt aseg_mean_small.txt aseg_volume_small.txt out.txt
```

