#!/bin/bash
IP="127.0.0.1"

nohup python -u brakes_ALmotion_static_dynamic.py --ip=$IP --test=Cycling > cyclingWakeUpRest.txt &