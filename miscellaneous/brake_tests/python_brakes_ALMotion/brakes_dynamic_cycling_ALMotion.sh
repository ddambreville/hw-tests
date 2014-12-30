#!/bin/bash
IP="10.0.206.22"
DIRECTION="Positive"
NBCYCLES="2"

nohup python -u brakes_ALmotion_static_dynamic.py --ip=$IP --test=DynamicCycling --joint=HipPitch --direction=$DIRECTION --cycleNumber=$NBCYCLES --cyclingBrakingAngle=10.0 &
