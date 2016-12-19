#!/bin/bash

for file in *-Symbooglix.TerminatedWithoutError.yml; do
    echo "---";
    echo "!!python/object:core.symbooglix.TerminatedSymbooglixState";
    cat ${file};

done > Symbooglix.TerminatedWithoutError.yml