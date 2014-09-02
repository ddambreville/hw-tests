'''
Created on August 22, 2014

@author: amartin
'''

import threading
import time

def dance_motion(dance, behavior_manager):
    """
    Dance function
    """
    apps_list = behavior_manager.getBehaviorNames()
    #print apps_list
    dance = "User/" + dance
    if dance in apps_list:
        print "haha"
        behavior_manager.startBehavior(dance)
        while behavior_manager.isBehaviorRunning(dance):
            print "hihi"
            time.sleep(0.5)

def test_faux_positifs_dance(mem, remove_diagnosis, wakeup, dance,
    remove_safety, behavior_manager):
    """
    Test function
    """
    print dance
    time.sleep(10)
    #dance_thread = threading.Thread(target=dance_motion, args=(dance, behavior_manager))
    #dance_thread.start()
    dance_motion(dance, behavior_manager)



