#!/usr/bin/env python
# encoding: utf-8

import snakebasket
import os

snakebasket.main(['install', '-r', os.path.join('..', 'requirements.txt')])
input("Press Enter to continue...")
