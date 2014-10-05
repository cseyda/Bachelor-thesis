#!/bin/bash

set -b

echo [00s] start tracing CPU
./traceLoop "CPU" &
PID=$!

sleep 10
echo [10s] start stressing first CPU with 100%
taskset 0x1 stress --cpu 1 --timeout 20s &

sleep 10
echo [20s] start stressing second CPU with 100\%
taskset 0x2 stress --cpu 1 --timeout 20s &

sleep 10
echo [30s] stop stressing first CPU

sleep 10
echo [40s] stop stressing second CPU

sleep 10
echo [50s] start writing to local HDD
dd if=/dev/zero of=/tmp/verifyRUT.tmp bs=16M count=64 2> /dev/null &

sleep 40
echo [90s] terminate program
kill -INT $PID