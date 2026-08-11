#!/usr/bin/env python3
import sys, time, os
# Ensure package path
sys.path.insert(0, '/opt/hermes/ContextForge')
from ContextForge import AdaptiveRateLimiter

limiter = AdaptiveRateLimiter()
while True:
    print(f"Current delay: {limiter.delay_ms()} ms")
    time.sleep(30)
