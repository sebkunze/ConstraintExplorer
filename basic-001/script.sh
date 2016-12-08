#!/bin/bash

for file in *-Symbooglix.TerminatedWithoutError.yml; do
    echo "---";
    echo "!!python/object:__main__.TerminatedState";
    cat ${file};

done > Symbooglix.TerminatedWithoutError.yml