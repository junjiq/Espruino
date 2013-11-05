#!/usr/bin/python

# This file is part of Espruino, a JavaScript interpreter for Microcontrollers
#
# Copyright (C) 2013 Gordon Williams <gw@pur3.co.uk>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# ----------------------------------------------------------------------------------------
# Reads board information from boards/BOARDNAME.py and uses it to generate a header file
# which describes the available peripherals on the board
# ----------------------------------------------------------------------------------------
import subprocess;
import re;
import json;
import sys;
import os;
import importlib;
import common;

scriptdir = os.path.dirname(os.path.realpath(__file__))
basedir = scriptdir+"/../"
sys.path.append(basedir+"scripts");
sys.path.append(basedir+"boards");

import pinutils;

# -----------------------------------------------------------------------------------------

# Now scan AF file
print "Script location "+scriptdir

if len(sys.argv)!=2:
  print "ERROR, USAGE: build_platform_config.py BOARD_NAME"
  exit(1)
boardname = sys.argv[1]
headerFilename = "gen/platform_config.h"
print "HEADER_FILENAME "+headerFilename
print "BOARD "+boardname
# import the board def
board = importlib.import_module(boardname)

# -----------------------------------------------------------------------------------------

LINUX = board.chip["family"]=="LINUX"

if not "default_console" in board.info:
  board.info["default_console"] = "EV_SERIAL1"

if not LINUX:
  if board.chip["part"]=="STM32F100RB" or board.chip["part"]=="STM32F103RB" or board.chip["part"]=="STM32F103TB": board.chip["subfamily"]="MD";

  # how much room for stack (and EVERYTHING else)
  space_for_stack = 4 #kB
  if board.chip["ram"] > 20: space_for_stack = 5
  variable_storage = board.chip["ram"] - space_for_stack
  # work out # of variables
  # We need to know if we should be using 8 or 16 bit addresses
  #variables_8bit = (variable_storage*1024 )/ 16
  #variables_16bit = (variable_storage*1024) / 20
  #if variables_8bit > 254 and variables_16bit > 254:
  #  variables = variables_16bit
  #else:
  #  variables = variables_8bit
  # But in some cases we may not have enough flash memory!
  variables=board.info["variables"]

  var_size = 16 if variables<255 else 20
  var_cache_size = var_size*variables
  flash_needed = var_cache_size + 4 # for magic number
  flash_page_size = 1024 # just a geuss
  if board.chip["family"]=="STM32F1": flash_page_size = 1024 if "subfamily" in board.chip and board.chip["subfamily"]=="MD" else 2048
  if board.chip["family"]=="STM32F2": flash_page_size = 128*1024
  if board.chip["family"]=="STM32F3": flash_page_size = 2*1024
  if board.chip["family"]=="STM32F4": flash_page_size = 128*1024
  flash_pages = (flash_needed+flash_page_size-1)/flash_page_size
  total_flash = board.chip["flash"]*1024
  flash_available_for_code = total_flash - flash_pages*flash_page_size

  print "Variables = "+str(variables)
  print "JsVar size = "+str(var_size)
  print "VarCache size = "+str(var_cache_size)
  print "Flash pages = "+str(flash_pages)
  print "Total flash = "+str(total_flash)
  print "Flash available for code = "+str(flash_available_for_code)


# -----------------------------------------------------------------------------------------
headerFile = open(headerFilename, 'w')
def codeOut(s): headerFile.write(s+"\n");
# -----------------------------------------------------------------------------------------
def die(err):
  print("ERROR: "+err)
  sys.exit(1)

def toPinDef(pin):
  return "(Pin)(JSH_PORT"+pin[0]+"_OFFSET + "+pin[1:]+")"

def codeOutDevice(device):
  if device in board.devices:
    codeOut("#define "+device+"_PININDEX "+toPinDef(board.devices[device]["pin"]))
    if device=="BTN1":
      codeOut("#define "+device+"_ONSTATE "+("0" if "inverted" in board.devices[device] else "1"))
  
def codeOutDevicePin(device, pin, definition_name):
  if device in board.devices:
    codeOut("#define "+definition_name+" "+toPinDef(board.devices[device][pin]))
# -----------------------------------------------------------------------------------------


codeOut("""
// Automatically generated header file for """+boardname+"""
// Generated by scripts/build_platform_config.py

#ifndef _PLATFORM_CONFIG_H
#define _PLATFORM_CONFIG_H

""");

if board.chip["family"]=="LINUX":
  board.chip["class"]="LINUX"
elif board.chip["family"]=="STM32F1":
  board.chip["class"]="STM32"
  codeOut('#include "stm32f10x.h"')
elif board.chip["family"]=="STM32F2":
  board.chip["class"]="STM32"
  codeOut('#include "stm32f2xx.h"')
  codeOut("#define STM32API2 // hint to jshardware that the API is a lot different")
elif board.chip["family"]=="STM32F3":
  board.chip["class"]="STM32"
  codeOut('#include "stm32f30x.h"')
  codeOut("#define STM32API2 // hint to jshardware that the API is a lot different")
  codeOut("#define USB_INT_DEFAULT") # hack 
elif board.chip["family"]=="STM32F4":
  board.chip["class"]="STM32"
  codeOut('#include "stm32f4xx.h"')
  codeOut("#define STM32API2 // hint to jshardware that the API is a lot different")
elif board.chip["family"]=="LPC1768":
  board.chip["class"]="MBED"
else:
  die('Unknown chip family '+board.chip["family"])

if board.chip["class"]=="MBED":
  codeOut("""
  #pragma diag_suppress 1295 // deprecated decl
  #pragma diag_suppress 188 // enumerated type mixed with another type
  #pragma diag_suppress 111 // statement is unreachable
  #pragma diag_suppress 68 // integer conversion resulted in a change of sign
  """);

codeOut("""

// SYSTICK is the counter that counts up and that we use as the real-time clock
// The smaller this is, the longer we spend in interrupts, but also the more we can sleep!
#define SYSTICK_RANGE 0x1000000 // the Maximum (it is a 24 bit counter) - on Olimexino this is about 0.6 sec
#define SYSTICKS_BEFORE_USB_DISCONNECT 2

#define DEFAULT_BUSY_PIN_INDICATOR (Pin)-1 // no indicator
#define DEFAULT_SLEEP_PIN_INDICATOR (Pin)-1 // no indicator

// When to send the message that the IO buffer is getting full
#define IOBUFFER_XOFF ((TXBUFFERMASK)*6/8)
// When to send the message that we can start receiving again
#define IOBUFFER_XON ((TXBUFFERMASK)*3/8)

""");

if board.chip["class"]=="STM32":
  if "subfamily" in board.chip and board.chip["subfamily"]=="MD" : 
   codeOut("""
// frustratingly the 103_MD (non-VL) chips in Olimexino don't have any timers other than 1-4
#define UTIL_TIMER TIM4
#define UTIL_TIMER_IRQn TIM4_IRQn
#define UTIL_TIMER_IRQHandler TIM4_IRQHandler
#define UTIL_TIMER_APB1 RCC_APB1Periph_TIM4
""")
  else:
   codeOut("""
// nice timer not used by anything else
#define UTIL_TIMER TIM7
#define UTIL_TIMER_IRQn TIM7_IRQn
#define UTIL_TIMER_IRQHandler TIM7_IRQHandler
#define UTIL_TIMER_APB1 RCC_APB1Periph_TIM7
""")

codeOut("");
# ------------------------------------------------------------------------------------- Chip Specifics
codeOut("#define RAM_TOTAL ("+str(board.chip['ram'])+"*1024)")
codeOut("#define FLASH_TOTAL ("+str(board.chip['flash'])+"*1024)")
codeOut("");
if LINUX:
  codeOut('#define RESIZABLE_JSVARS // Allocate variables in blocks using malloc')
else:
  codeOut("#define JSVAR_CACHE_SIZE                "+str(variables)+" // Number of JavaScript variables in RAM")
  codeOut("#define FLASH_AVAILABLE_FOR_CODE        "+str(flash_available_for_code))
  codeOut("#define FLASH_PAGE_SIZE                 "+str(flash_page_size))
  codeOut("#define FLASH_PAGES                     "+str(flash_pages))
  codeOut("#define BOOTLOADER_SIZE                 "+str(common.get_bootloader_size()))
codeOut("");
codeOut("#define USARTS                          "+str(board.chip["usart"]))
codeOut("#define SPIS                            "+str(board.chip["spi"]))
codeOut("#define I2CS                            "+str(board.chip["i2c"]))
codeOut("#define ADCS                            "+str(board.chip["adc"]))
codeOut("#define DACS                            "+str(board.chip["dac"]))
codeOut("");
codeOut("#define DEFAULT_CONSOLE_DEVICE              "+board.info["default_console"]);
codeOut("");
codeOut("#define IOBUFFERMASK 31 // (max 255) amount of items in event buffer - events take ~9 bytes each")
codeOut("#define TXBUFFERMASK 31 // (max 255)")
codeOut("");
codeOutDevice("LED1")
codeOutDevice("LED2")
codeOutDevice("LED3")
codeOutDevice("LED4")
codeOutDevice("LED5")
codeOutDevice("LED6")
codeOutDevice("LED7")
codeOutDevice("LED8")
codeOutDevice("BTN1")
codeOutDevice("BTN2")
codeOutDevice("BTN3")
codeOutDevice("BTN4")

if "USB" in board.devices:
  if "pin_disc" in board.devices["USB"]: codeOutDevicePin("USB", "pin_disc", "USB_DISCONNECT_PIN")

codeOut("""
#endif // _PLATFORM_CONFIG_H
""");


