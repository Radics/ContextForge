#!/usr/bin/env python3
import sys, time, os
sys.path.insert(0, '/opt/hermes/ContextForge')
from ContextForge import add_fact

while True:
    add_fact({'event':'heartbeat','ts':time.time()})
    print('Added heartbeat fact')
    time.sleep(60)
