#!/bin/bash

echo "Enter three numbers:"
read a
read b
read c

largest=$a
smallest=$a

if [ $b -gt $largest ]; then
  largest=$b
fi

if [ $c -gt $largest ]; then
  largest=$c
fi

if [ $b -lt $smallest ]; then
  smallest=$b
fi

if [ $c -lt $smallest ]; then
  smallest=$c
fi

echo "Largest number: $largest"
echo "Smallest number: $smallest"


