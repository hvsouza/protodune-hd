#!/bin/bash

runs=(\
    run026265 \
)

mainpwd=$( pwd )


for r in ${runs[@]}; do
    cd "20240519_tau_slow/$r"
    root -l -e ".L ../../convolution_fit.C" -e 'convolution_fit(1225, false, 69, "../run026261/analyzed.root", false)' 
    cd $mainpwd
done
