#!/bin/bash
logOffset=1; tail -f `find /opt/logs -name "*zeroDay*"|sort|tail -"${logOffset}"|head -1`
