/*
 * This file is part of Espruino, a JavaScript interpreter for Microcontrollers
 *
 * Copyright (C) 2013 Gordon Williams <gw@pur3.co.uk>
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 *
 * ----------------------------------------------------------------------------
 * JavaScript methods for Espruino utility functions
 * ----------------------------------------------------------------------------
 */
#include "jsvar.h"
#include "jshardware.h"

JsVar *jswrap_espruino_nativeCall(JsVarInt addr, JsVar *signature, JsVar *data);

JsVarFloat jswrap_espruino_clip(JsVarFloat x, JsVarFloat min, JsVarFloat max);
JsVarFloat jswrap_espruino_sum(JsVar *arr);
JsVarFloat jswrap_espruino_variance(JsVar *arr, JsVarFloat mean);
JsVarFloat jswrap_espruino_convolve(JsVar *a, JsVar *b, int offset);
void jswrap_espruino_FFT(JsVar *arrReal, JsVar *arrImag, bool inverse);

JsVarFloat jswrap_espruino_interpolate(JsVar *array, JsVarFloat findex);
JsVarFloat jswrap_espruino_interpolate2d(JsVar *array, int width, JsVarFloat x, JsVarFloat y);

void jswrap_espruino_enableWatchdog(JsVarFloat time, JsVar *isAuto);
void jswrap_espruino_kickWatchdog();
JsVar *jswrap_espruino_getErrorFlags();
JsVar *jswrap_espruino_toArrayBuffer(JsVar *str);
JsVar *jswrap_espruino_toUint8Array(JsVar *args);
JsVar *jswrap_espruino_toString(JsVar *args);
JsVar *jswrap_espruino_memoryArea(int addr, int len);
void jswrap_espruino_setBootCode(JsVar *code, bool alwaysExec);
int jswrap_espruino_setClock(JsVar *options);

int jswrap_espruino_reverseByte(int v);
void jswrap_espruino_dumpTimers();
JsVar *jswrap_espruino_getSizeOf(JsVar *v, int depth);
void jswrap_espruino_mapInPlace(JsVar *from, JsVar *to, JsVar *map, JsVarInt bits);
JsVar *jswrap_e_dumpStr();
JsVarInt jswrap_espruino_HSBtoRGB(JsVarFloat hue, JsVarFloat sat, JsVarFloat bri);

void jswrap_espruino_setUSBHID(JsVar *arr);
bool jswrap_espruino_sendUSBHID(JsVar *arr);


