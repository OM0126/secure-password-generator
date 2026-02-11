#!/bin/bash

read -p "Enter Student Name: " name

read -p "Enter marks of Subject 1: " m1
read -p "Enter marks of Subject 2: " m2
read -p "Enter marks of Subject 3: " m3

total=$((m1 + m2 + m3))
percentage=$((total / 3))


echo "Student Name  : $name"
echo "Total Marks   : $total"
echo "Percentage    : $percentage%"

if [ $percentage -ge 60 ]; then
    echo "Class Obtained : First Class"
elif [ $percentage -ge 50 ]; then
    echo "Class Obtained : Second Class"
elif [ $percentage -ge 35 ]; then
    echo "Class Obtained : Pass"
else
    echo "Class Obtained : Fail"
fi
