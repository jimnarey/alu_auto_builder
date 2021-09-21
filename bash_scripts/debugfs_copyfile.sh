#!/bin/bash

if (($# < 2)); then
  echo "Usage:"
  echo $0 file target_img
  exit 1
fi