#!/bin/bash
ls ./*.py | grep -v '^_' | xargs -I % sh -c 'python % --test'
