#!/bin/bash

for file in *-Symbooglix.TerminatedWithoutError.yml; do
    echo "---";
    echo "!!python/object:__main__.TerminatedSymbooglixState";
    cat ${file};

done > Symbooglix.TerminatedWithoutError.yml