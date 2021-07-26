#!/bin/bash
git submodule update --init
cd plugins/plotters/chia-plotter
git submodule update --init
sh make_release.sh
mv build/chia_plot ../chia_plot
sh clean_all.sh
cd ../../