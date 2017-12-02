#!/bin/bash

pushd wpiformat
rm -rf dist
git checkout master
if [ $? == 0 ]; then
  python setup.py sdist bdist_wheel
  twine upload dist/*
fi
popd
