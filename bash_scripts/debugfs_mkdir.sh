#!/bin/bash

if (($# < 1)); then
  echo "Usage:"
  echo $0 dir target_img
  exit 1
fi