#!/bin/bash -eux
# Building sphinx and swagger docs

python -m sphinx . $BUILD_PATH
TARGET_PATH="$BUILD_PATH/swagger" ./build_swagger.sh
