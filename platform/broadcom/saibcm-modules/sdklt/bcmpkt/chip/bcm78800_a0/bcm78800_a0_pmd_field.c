/*******************************************************************************
 *
 * DO NOT EDIT THIS FILE!
 * This file is auto-generated from the registers file.
 * Edits to this file will be lost when it is regenerated.
 * Tool: INTERNAL/regs/xgs/generate-pmd.pl
 *
 * Copyright 2018-2024 Broadcom. All rights reserved.
 * The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries.
 * 
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License 
 * version 2 as published by the Free Software Foundation.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * A copy of the GNU General Public License version 2 (GPLv2) can
 * be found in the LICENSES folder.
 *
 * This file provides PMD field info for BCM78800_A0.
 *
 ******************************************************************************/

#include <bcmpkt/bcmpkt_pmd_field_internal.h>
#include <bcmpkt/chip/bcm78800_a0/bcm78800_a0_pmd_field.h>

static bcmpkt_field_info_t
field_fmt_0_447_17_4_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 0;
    info.maxbit = 447;
    return info;
}

static void
field_fmt_0_447_17_4_set(uint32_t *pmd, uint32_t *val)
{
    pmd[17] = val[0];
    pmd[16] = val[1];
    pmd[15] = val[2];
    pmd[14] = val[3];
    pmd[13] = val[4];
    pmd[12] = val[5];
    pmd[11] = val[6];
    pmd[10] = val[7];
    pmd[9] = val[8];
    pmd[8] = val[9];
    pmd[7] = val[10];
    pmd[6] = val[11];
    pmd[5] = val[12];
    pmd[4] = val[13];
}

static void
field_fmt_0_447_17_4_get(uint32_t *pmd, uint32_t *val)
{
    val[0] = pmd[17];
    val[1] = pmd[16];
    val[2] = pmd[15];
    val[3] = pmd[14];
    val[4] = pmd[13];
    val[5] = pmd[12];
    val[6] = pmd[11];
    val[7] = pmd[10];
    val[8] = pmd[9];
    val[9] = pmd[8];
    val[10] = pmd[7];
    val[11] = pmd[6];
    val[12] = pmd[5];
    val[13] = pmd[4];
}

static bcmpkt_field_info_t
field_fmt_0_8_3_3_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 0;
    info.maxbit = 8;
    return info;
}

static void
field_fmt_0_8_3_3_set(uint32_t *pmd, uint32_t *val)
{
    pmd[3] = (pmd[3] & 0xfffffe00) | (*val & 0x1ff);
}

static void
field_fmt_0_8_3_3_get(uint32_t *pmd, uint32_t *val)
{
    *val = pmd[3] & 0x1ff;
}

static bcmpkt_field_info_t
field_fmt_10_10_3_3_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 10;
    info.maxbit = 10;
    return info;
}

static void
field_fmt_10_10_3_3_set(uint32_t *pmd, uint32_t *val)
{
    pmd[3] = (pmd[3] & 0xfffffbff) | ((*val & 0x1) << 10);
}

static void
field_fmt_10_10_3_3_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[3] >> 10) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_11_24_3_3_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 11;
    info.maxbit = 24;
    return info;
}

static void
field_fmt_11_24_3_3_set(uint32_t *pmd, uint32_t *val)
{
    pmd[3] = (pmd[3] & 0xfe0007ff) | ((*val & 0x3fff) << 11);
}

static void
field_fmt_11_24_3_3_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[3] >> 11) & 0x3fff;
}

static bcmpkt_field_info_t
field_fmt_120_125_0_0_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 120;
    info.maxbit = 125;
    return info;
}

static void
field_fmt_120_125_0_0_set(uint32_t *pmd, uint32_t *val)
{
    pmd[0] = (pmd[0] & 0xc0ffffff) | ((*val & 0x3f) << 24);
}

static void
field_fmt_120_125_0_0_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[0] >> 24) & 0x3f;
}

static bcmpkt_field_info_t
field_fmt_126_127_0_0_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 126;
    info.maxbit = 127;
    return info;
}

static void
field_fmt_126_127_0_0_set(uint32_t *pmd, uint32_t *val)
{
    pmd[0] = (pmd[0] & 0x3fffffff) | (*val << 30);
}

static void
field_fmt_126_127_0_0_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[0] >> 30) & 0x3;
}

static bcmpkt_field_info_t
field_fmt_25_25_3_3_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 25;
    info.maxbit = 25;
    return info;
}

static void
field_fmt_25_25_3_3_set(uint32_t *pmd, uint32_t *val)
{
    pmd[3] = (pmd[3] & 0xfdffffff) | ((*val & 0x1) << 25);
}

static void
field_fmt_25_25_3_3_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[3] >> 25) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_26_26_3_3_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 26;
    info.maxbit = 26;
    return info;
}

static void
field_fmt_26_26_3_3_set(uint32_t *pmd, uint32_t *val)
{
    pmd[3] = (pmd[3] & 0xfbffffff) | ((*val & 0x1) << 26);
}

static void
field_fmt_26_26_3_3_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[3] >> 26) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_35_35_2_2_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 35;
    info.maxbit = 35;
    return info;
}

static void
field_fmt_35_35_2_2_set(uint32_t *pmd, uint32_t *val)
{
    pmd[2] = (pmd[2] & 0xfffffff7) | ((*val & 0x1) << 3);
}

static void
field_fmt_35_35_2_2_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[2] >> 3) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_36_36_2_2_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 36;
    info.maxbit = 36;
    return info;
}

static void
field_fmt_36_36_2_2_set(uint32_t *pmd, uint32_t *val)
{
    pmd[2] = (pmd[2] & 0xffffffef) | ((*val & 0x1) << 4);
}

static void
field_fmt_36_36_2_2_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[2] >> 4) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_37_38_2_2_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 37;
    info.maxbit = 38;
    return info;
}

static void
field_fmt_37_38_2_2_set(uint32_t *pmd, uint32_t *val)
{
    pmd[2] = (pmd[2] & 0xffffff9f) | ((*val & 0x3) << 5);
}

static void
field_fmt_37_38_2_2_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[2] >> 5) & 0x3;
}

static bcmpkt_field_info_t
field_fmt_39_44_2_2_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 39;
    info.maxbit = 44;
    return info;
}

static void
field_fmt_39_44_2_2_set(uint32_t *pmd, uint32_t *val)
{
    pmd[2] = (pmd[2] & 0xffffe07f) | ((*val & 0x3f) << 7);
}

static void
field_fmt_39_44_2_2_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[2] >> 7) & 0x3f;
}

static bcmpkt_field_info_t
field_fmt_449_454_3_3_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 449;
    info.maxbit = 454;
    return info;
}

static void
field_fmt_449_454_3_3_set(uint32_t *pmd, uint32_t *val)
{
    pmd[3] = (pmd[3] & 0xffffff81) | ((*val & 0x3f) << 1);
}

static void
field_fmt_449_454_3_3_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[3] >> 1) & 0x3f;
}

static bcmpkt_field_info_t
field_fmt_455_455_3_3_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 455;
    info.maxbit = 455;
    return info;
}

static void
field_fmt_455_455_3_3_set(uint32_t *pmd, uint32_t *val)
{
    pmd[3] = (pmd[3] & 0xffffff7f) | ((*val & 0x1) << 7);
}

static void
field_fmt_455_455_3_3_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[3] >> 7) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_456_459_3_3_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 456;
    info.maxbit = 459;
    return info;
}

static void
field_fmt_456_459_3_3_set(uint32_t *pmd, uint32_t *val)
{
    pmd[3] = (pmd[3] & 0xfffff0ff) | ((*val & 0xf) << 8);
}

static void
field_fmt_456_459_3_3_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[3] >> 8) & 0xf;
}

static bcmpkt_field_info_t
field_fmt_45_45_2_2_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 45;
    info.maxbit = 45;
    return info;
}

static void
field_fmt_45_45_2_2_set(uint32_t *pmd, uint32_t *val)
{
    pmd[2] = (pmd[2] & 0xffffdfff) | ((*val & 0x1) << 13);
}

static void
field_fmt_45_45_2_2_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[2] >> 13) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_460_462_3_3_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 460;
    info.maxbit = 462;
    return info;
}

static void
field_fmt_460_462_3_3_set(uint32_t *pmd, uint32_t *val)
{
    pmd[3] = (pmd[3] & 0xffff8fff) | ((*val & 0x7) << 12);
}

static void
field_fmt_460_462_3_3_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[3] >> 12) & 0x7;
}

static bcmpkt_field_info_t
field_fmt_464_465_3_3_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 464;
    info.maxbit = 465;
    return info;
}

static void
field_fmt_464_465_3_3_set(uint32_t *pmd, uint32_t *val)
{
    pmd[3] = (pmd[3] & 0xfffcffff) | ((*val & 0x3) << 16);
}

static void
field_fmt_464_465_3_3_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[3] >> 16) & 0x3;
}

static bcmpkt_field_info_t
field_fmt_466_467_3_3_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 466;
    info.maxbit = 467;
    return info;
}

static void
field_fmt_466_467_3_3_set(uint32_t *pmd, uint32_t *val)
{
    pmd[3] = (pmd[3] & 0xfff3ffff) | ((*val & 0x3) << 18);
}

static void
field_fmt_466_467_3_3_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[3] >> 18) & 0x3;
}

static bcmpkt_field_info_t
field_fmt_468_468_3_3_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 468;
    info.maxbit = 468;
    return info;
}

static void
field_fmt_468_468_3_3_set(uint32_t *pmd, uint32_t *val)
{
    pmd[3] = (pmd[3] & 0xffefffff) | ((*val & 0x1) << 20);
}

static void
field_fmt_468_468_3_3_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[3] >> 20) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_469_469_3_3_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 469;
    info.maxbit = 469;
    return info;
}

static void
field_fmt_469_469_3_3_set(uint32_t *pmd, uint32_t *val)
{
    pmd[3] = (pmd[3] & 0xffdfffff) | ((*val & 0x1) << 21);
}

static void
field_fmt_469_469_3_3_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[3] >> 21) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_46_46_2_2_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 46;
    info.maxbit = 46;
    return info;
}

static void
field_fmt_46_46_2_2_set(uint32_t *pmd, uint32_t *val)
{
    pmd[2] = (pmd[2] & 0xffffbfff) | ((*val & 0x1) << 14);
}

static void
field_fmt_46_46_2_2_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[2] >> 14) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_470_470_3_3_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 470;
    info.maxbit = 470;
    return info;
}

static void
field_fmt_470_470_3_3_set(uint32_t *pmd, uint32_t *val)
{
    pmd[3] = (pmd[3] & 0xffbfffff) | ((*val & 0x1) << 22);
}

static void
field_fmt_470_470_3_3_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[3] >> 22) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_471_478_3_3_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 471;
    info.maxbit = 478;
    return info;
}

static void
field_fmt_471_478_3_3_set(uint32_t *pmd, uint32_t *val)
{
    pmd[3] = (pmd[3] & 0x807fffff) | ((*val & 0xff) << 23);
}

static void
field_fmt_471_478_3_3_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[3] >> 23) & 0xff;
}

static bcmpkt_field_info_t
field_fmt_47_47_2_2_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 47;
    info.maxbit = 47;
    return info;
}

static void
field_fmt_47_47_2_2_set(uint32_t *pmd, uint32_t *val)
{
    pmd[2] = (pmd[2] & 0xffff7fff) | ((*val & 0x1) << 15);
}

static void
field_fmt_47_47_2_2_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[2] >> 15) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_480_511_2_2_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 480;
    info.maxbit = 511;
    return info;
}

static void
field_fmt_480_511_2_2_set(uint32_t *pmd, uint32_t *val)
{
    pmd[2] = *val;
}

static void
field_fmt_480_511_2_2_get(uint32_t *pmd, uint32_t *val)
{
    *val = pmd[2];
}

static bcmpkt_field_info_t
field_fmt_48_51_2_2_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 48;
    info.maxbit = 51;
    return info;
}

static void
field_fmt_48_51_2_2_set(uint32_t *pmd, uint32_t *val)
{
    pmd[2] = (pmd[2] & 0xfff0ffff) | ((*val & 0xf) << 16);
}

static void
field_fmt_48_51_2_2_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[2] >> 16) & 0xf;
}

static bcmpkt_field_info_t
field_fmt_512_527_1_1_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 512;
    info.maxbit = 527;
    return info;
}

static void
field_fmt_512_527_1_1_set(uint32_t *pmd, uint32_t *val)
{
    pmd[1] = (pmd[1] & 0xffff0000) | (*val & 0xffff);
}

static void
field_fmt_512_527_1_1_get(uint32_t *pmd, uint32_t *val)
{
    *val = pmd[1] & 0xffff;
}

static bcmpkt_field_info_t
field_fmt_528_543_1_1_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 528;
    info.maxbit = 543;
    return info;
}

static void
field_fmt_528_543_1_1_set(uint32_t *pmd, uint32_t *val)
{
    pmd[1] = (pmd[1] & 0xffff) | (*val << 16);
}

static void
field_fmt_528_543_1_1_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[1] >> 16) & 0xffff;
}

static bcmpkt_field_info_t
field_fmt_52_53_2_2_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 52;
    info.maxbit = 53;
    return info;
}

static void
field_fmt_52_53_2_2_set(uint32_t *pmd, uint32_t *val)
{
    pmd[2] = (pmd[2] & 0xffcfffff) | ((*val & 0x3) << 20);
}

static void
field_fmt_52_53_2_2_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[2] >> 20) & 0x3;
}

static bcmpkt_field_info_t
field_fmt_544_545_0_0_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 544;
    info.maxbit = 545;
    return info;
}

static void
field_fmt_544_545_0_0_set(uint32_t *pmd, uint32_t *val)
{
    pmd[0] = (pmd[0] & 0xfffffffc) | (*val & 0x3);
}

static void
field_fmt_544_545_0_0_get(uint32_t *pmd, uint32_t *val)
{
    *val = pmd[0] & 0x3;
}

static bcmpkt_field_info_t
field_fmt_546_551_0_0_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 546;
    info.maxbit = 551;
    return info;
}

static void
field_fmt_546_551_0_0_set(uint32_t *pmd, uint32_t *val)
{
    pmd[0] = (pmd[0] & 0xffffff03) | ((*val & 0x3f) << 2);
}

static void
field_fmt_546_551_0_0_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[0] >> 2) & 0x3f;
}

static bcmpkt_field_info_t
field_fmt_54_55_2_2_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 54;
    info.maxbit = 55;
    return info;
}

static void
field_fmt_54_55_2_2_set(uint32_t *pmd, uint32_t *val)
{
    pmd[2] = (pmd[2] & 0xff3fffff) | ((*val & 0x3) << 22);
}

static void
field_fmt_54_55_2_2_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[2] >> 22) & 0x3;
}

static bcmpkt_field_info_t
field_fmt_552_552_0_0_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 552;
    info.maxbit = 552;
    return info;
}

static void
field_fmt_552_552_0_0_set(uint32_t *pmd, uint32_t *val)
{
    pmd[0] = (pmd[0] & 0xfffffeff) | ((*val & 0x1) << 8);
}

static void
field_fmt_552_552_0_0_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[0] >> 8) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_553_556_0_0_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 553;
    info.maxbit = 556;
    return info;
}

static void
field_fmt_553_556_0_0_set(uint32_t *pmd, uint32_t *val)
{
    pmd[0] = (pmd[0] & 0xffffe1ff) | ((*val & 0xf) << 9);
}

static void
field_fmt_553_556_0_0_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[0] >> 9) & 0xf;
}

static bcmpkt_field_info_t
field_fmt_557_557_0_0_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 557;
    info.maxbit = 557;
    return info;
}

static void
field_fmt_557_557_0_0_set(uint32_t *pmd, uint32_t *val)
{
    pmd[0] = (pmd[0] & 0xffffdfff) | ((*val & 0x1) << 13);
}

static void
field_fmt_557_557_0_0_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[0] >> 13) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_558_558_0_0_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 558;
    info.maxbit = 558;
    return info;
}

static void
field_fmt_558_558_0_0_set(uint32_t *pmd, uint32_t *val)
{
    pmd[0] = (pmd[0] & 0xffffbfff) | ((*val & 0x1) << 14);
}

static void
field_fmt_558_558_0_0_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[0] >> 14) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_559_559_0_0_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 559;
    info.maxbit = 559;
    return info;
}

static void
field_fmt_559_559_0_0_set(uint32_t *pmd, uint32_t *val)
{
    pmd[0] = (pmd[0] & 0xffff7fff) | ((*val & 0x1) << 15);
}

static void
field_fmt_559_559_0_0_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[0] >> 15) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_560_575_0_0_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 560;
    info.maxbit = 575;
    return info;
}

static void
field_fmt_560_575_0_0_set(uint32_t *pmd, uint32_t *val)
{
    pmd[0] = (pmd[0] & 0xffff) | (*val << 16);
}

static void
field_fmt_560_575_0_0_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[0] >> 16) & 0xffff;
}

static bcmpkt_field_info_t
field_fmt_56_56_2_2_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 56;
    info.maxbit = 56;
    return info;
}

static void
field_fmt_56_56_2_2_set(uint32_t *pmd, uint32_t *val)
{
    pmd[2] = (pmd[2] & 0xfeffffff) | ((*val & 0x1) << 24);
}

static void
field_fmt_56_56_2_2_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[2] >> 24) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_57_60_2_2_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 57;
    info.maxbit = 60;
    return info;
}

static void
field_fmt_57_60_2_2_set(uint32_t *pmd, uint32_t *val)
{
    pmd[2] = (pmd[2] & 0xe1ffffff) | ((*val & 0xf) << 25);
}

static void
field_fmt_57_60_2_2_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[2] >> 25) & 0xf;
}

static bcmpkt_field_info_t
field_fmt_64_71_1_1_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 64;
    info.maxbit = 71;
    return info;
}

static void
field_fmt_64_71_1_1_set(uint32_t *pmd, uint32_t *val)
{
    pmd[1] = (pmd[1] & 0xffffff00) | (*val & 0xff);
}

static void
field_fmt_64_71_1_1_get(uint32_t *pmd, uint32_t *val)
{
    *val = pmd[1] & 0xff;
}

static bcmpkt_field_info_t
field_fmt_72_79_1_1_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 72;
    info.maxbit = 79;
    return info;
}

static void
field_fmt_72_79_1_1_set(uint32_t *pmd, uint32_t *val)
{
    pmd[1] = (pmd[1] & 0xffff00ff) | ((*val & 0xff) << 8);
}

static void
field_fmt_72_79_1_1_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[1] >> 8) & 0xff;
}

static bcmpkt_field_info_t
field_fmt_80_80_1_1_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 80;
    info.maxbit = 80;
    return info;
}

static void
field_fmt_80_80_1_1_set(uint32_t *pmd, uint32_t *val)
{
    pmd[1] = (pmd[1] & 0xfffeffff) | ((*val & 0x1) << 16);
}

static void
field_fmt_80_80_1_1_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[1] >> 16) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_81_81_1_1_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 81;
    info.maxbit = 81;
    return info;
}

static void
field_fmt_81_81_1_1_set(uint32_t *pmd, uint32_t *val)
{
    pmd[1] = (pmd[1] & 0xfffdffff) | ((*val & 0x1) << 17);
}

static void
field_fmt_81_81_1_1_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[1] >> 17) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_82_82_1_1_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 82;
    info.maxbit = 82;
    return info;
}

static void
field_fmt_82_82_1_1_set(uint32_t *pmd, uint32_t *val)
{
    pmd[1] = (pmd[1] & 0xfffbffff) | ((*val & 0x1) << 18);
}

static void
field_fmt_82_82_1_1_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[1] >> 18) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_83_83_1_1_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 83;
    info.maxbit = 83;
    return info;
}

static void
field_fmt_83_83_1_1_set(uint32_t *pmd, uint32_t *val)
{
    pmd[1] = (pmd[1] & 0xfff7ffff) | ((*val & 0x1) << 19);
}

static void
field_fmt_83_83_1_1_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[1] >> 19) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_84_84_1_1_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 84;
    info.maxbit = 84;
    return info;
}

static void
field_fmt_84_84_1_1_set(uint32_t *pmd, uint32_t *val)
{
    pmd[1] = (pmd[1] & 0xffefffff) | ((*val & 0x1) << 20);
}

static void
field_fmt_84_84_1_1_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[1] >> 20) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_85_85_1_1_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 85;
    info.maxbit = 85;
    return info;
}

static void
field_fmt_85_85_1_1_set(uint32_t *pmd, uint32_t *val)
{
    pmd[1] = (pmd[1] & 0xffdfffff) | ((*val & 0x1) << 21);
}

static void
field_fmt_85_85_1_1_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[1] >> 21) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_86_86_1_1_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 86;
    info.maxbit = 86;
    return info;
}

static void
field_fmt_86_86_1_1_set(uint32_t *pmd, uint32_t *val)
{
    pmd[1] = (pmd[1] & 0xffbfffff) | ((*val & 0x1) << 22);
}

static void
field_fmt_86_86_1_1_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[1] >> 22) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_87_94_1_1_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 87;
    info.maxbit = 94;
    return info;
}

static void
field_fmt_87_94_1_1_set(uint32_t *pmd, uint32_t *val)
{
    pmd[1] = (pmd[1] & 0x807fffff) | ((*val & 0xff) << 23);
}

static void
field_fmt_87_94_1_1_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[1] >> 23) & 0xff;
}

static bcmpkt_field_info_t
field_fmt_95_95_1_1_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 95;
    info.maxbit = 95;
    return info;
}

static void
field_fmt_95_95_1_1_set(uint32_t *pmd, uint32_t *val)
{
    pmd[1] = (pmd[1] & 0x7fffffff) | (*val << 31);
}

static void
field_fmt_95_95_1_1_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[1] >> 31) & 0x1;
}

static bcmpkt_field_info_t
field_fmt_96_101_0_0_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 96;
    info.maxbit = 101;
    return info;
}

static void
field_fmt_96_101_0_0_set(uint32_t *pmd, uint32_t *val)
{
    pmd[0] = (pmd[0] & 0xffffffc0) | (*val & 0x3f);
}

static void
field_fmt_96_101_0_0_get(uint32_t *pmd, uint32_t *val)
{
    *val = pmd[0] & 0x3f;
}

static bcmpkt_field_info_t
field_fmt_9_9_3_3_info(void)
{
    bcmpkt_field_info_t info;
    info.minbit = 9;
    info.maxbit = 9;
    return info;
}

static void
field_fmt_9_9_3_3_set(uint32_t *pmd, uint32_t *val)
{
    pmd[3] = (pmd[3] & 0xfffffdff) | ((*val & 0x1) << 9);
}

static void
field_fmt_9_9_3_3_get(uint32_t *pmd, uint32_t *val)
{
    *val = (pmd[3] >> 9) & 0x1;
}

static bcmpkt_pmd_field_t bcm78800_a0_rxpmd_fields[BCM78800_A0_RXPMD_COUNT] = {
    {14, field_fmt_0_447_17_4_info, field_fmt_0_447_17_4_set, field_fmt_0_447_17_4_get, NULL, 0},
    {1, field_fmt_449_454_3_3_info, field_fmt_449_454_3_3_set, field_fmt_449_454_3_3_get, NULL, 0},
    {1, field_fmt_455_455_3_3_info, field_fmt_455_455_3_3_set, field_fmt_455_455_3_3_get, NULL, 0},
    {1, field_fmt_456_459_3_3_info, field_fmt_456_459_3_3_set, field_fmt_456_459_3_3_get, NULL, 0},
    {1, field_fmt_460_462_3_3_info, field_fmt_460_462_3_3_set, field_fmt_460_462_3_3_get, NULL, 0},
    {1, field_fmt_464_465_3_3_info, field_fmt_464_465_3_3_set, field_fmt_464_465_3_3_get, NULL, 0},
    {1, field_fmt_466_467_3_3_info, field_fmt_466_467_3_3_set, field_fmt_466_467_3_3_get, NULL, 0},
    {1, field_fmt_468_468_3_3_info, field_fmt_468_468_3_3_set, field_fmt_468_468_3_3_get, NULL, 0},
    {1, field_fmt_469_469_3_3_info, field_fmt_469_469_3_3_set, field_fmt_469_469_3_3_get, NULL, 0},
    {1, field_fmt_470_470_3_3_info, field_fmt_470_470_3_3_set, field_fmt_470_470_3_3_get, NULL, 0},
    {1, field_fmt_471_478_3_3_info, field_fmt_471_478_3_3_set, field_fmt_471_478_3_3_get, NULL, 0},
    {1, field_fmt_480_511_2_2_info, field_fmt_480_511_2_2_set, field_fmt_480_511_2_2_get, NULL, 0},
    {1, field_fmt_512_527_1_1_info, field_fmt_512_527_1_1_set, field_fmt_512_527_1_1_get, NULL, 0},
    {1, field_fmt_528_543_1_1_info, field_fmt_528_543_1_1_set, field_fmt_528_543_1_1_get, NULL, 0},
    {1, field_fmt_544_545_0_0_info, field_fmt_544_545_0_0_set, field_fmt_544_545_0_0_get, NULL, 0},
    {1, field_fmt_546_551_0_0_info, field_fmt_546_551_0_0_set, field_fmt_546_551_0_0_get, NULL, 0},
    {1, field_fmt_552_552_0_0_info, field_fmt_552_552_0_0_set, field_fmt_552_552_0_0_get, NULL, 0},
    {1, field_fmt_553_556_0_0_info, field_fmt_553_556_0_0_set, field_fmt_553_556_0_0_get, NULL, 0},
    {1, field_fmt_557_557_0_0_info, field_fmt_557_557_0_0_set, field_fmt_557_557_0_0_get, NULL, 0},
    {1, field_fmt_558_558_0_0_info, field_fmt_558_558_0_0_set, field_fmt_558_558_0_0_get, NULL, 0},
    {1, field_fmt_559_559_0_0_info, field_fmt_559_559_0_0_set, field_fmt_559_559_0_0_get, NULL, 0},
    {1, field_fmt_560_575_0_0_info, field_fmt_560_575_0_0_set, field_fmt_560_575_0_0_get, NULL, 0},

};

static const shr_enum_map_t bcm78800_a0_rxpmd_names[] =
{
    BCM78800_A0_RXPMD_NAME_MAP_INIT
};

bcmpkt_pmd_info_t bcm78800_a0_rxpmd_info_get(void)
{
    bcmpkt_pmd_info_t bcm78800_a0_rxpmd_info = {18, BCM78800_A0_RXPMD_COUNT, bcm78800_a0_rxpmd_names, bcm78800_a0_rxpmd_fields};
    return bcm78800_a0_rxpmd_info;
}

bcmpkt_pmd_info_t bcm78800_a0_rx_reason_info_get(void)
{
    bcmpkt_pmd_info_t bcm78800_a0_rx_reason_info = {0, 0, NULL, NULL};
    return bcm78800_a0_rx_reason_info;
}

bcmpkt_pmd_info_t bcm78800_a0_ep_rx_reason_info_get(void)
{
    bcmpkt_pmd_info_t bcm78800_a0_ep_rx_reason_info = {0, 0, NULL, NULL};
    return bcm78800_a0_ep_rx_reason_info;
}

static const shr_enum_map_t bcm78800_a0_txpmd_header_type_names[] =
{
    BCM78800_A0_TXPMD_HEADER_TYPE_NAME_MAP_INIT
};

static const shr_enum_map_t bcm78800_a0_txpmd_start_names[] =
{
    BCM78800_A0_TXPMD_START_NAME_MAP_INIT
};

static bcmpkt_pmd_field_t bcm78800_a0_txpmd_fields[BCM78800_A0_TXPMD_COUNT] = {
    {1, field_fmt_0_8_3_3_info, field_fmt_0_8_3_3_set, field_fmt_0_8_3_3_get, NULL, 0},
    {1, field_fmt_9_9_3_3_info, field_fmt_9_9_3_3_set, field_fmt_9_9_3_3_get, NULL, 0},
    {1, field_fmt_10_10_3_3_info, field_fmt_10_10_3_3_set, field_fmt_10_10_3_3_get, NULL, 0},
    {1, field_fmt_11_24_3_3_info, field_fmt_11_24_3_3_set, field_fmt_11_24_3_3_get, NULL, 0},
    {1, field_fmt_25_25_3_3_info, field_fmt_25_25_3_3_set, field_fmt_25_25_3_3_get, NULL, 0},
    {1, field_fmt_26_26_3_3_info, field_fmt_26_26_3_3_set, field_fmt_26_26_3_3_get, NULL, 0},
    {1, field_fmt_35_35_2_2_info, field_fmt_35_35_2_2_set, field_fmt_35_35_2_2_get, NULL, 0},
    {1, field_fmt_36_36_2_2_info, field_fmt_36_36_2_2_set, field_fmt_36_36_2_2_get, NULL, 0},
    {1, field_fmt_37_38_2_2_info, field_fmt_37_38_2_2_set, field_fmt_37_38_2_2_get, NULL, 0},
    {1, field_fmt_39_44_2_2_info, field_fmt_39_44_2_2_set, field_fmt_39_44_2_2_get, NULL, 0},
    {1, field_fmt_45_45_2_2_info, field_fmt_45_45_2_2_set, field_fmt_45_45_2_2_get, NULL, 0},
    {1, field_fmt_46_46_2_2_info, field_fmt_46_46_2_2_set, field_fmt_46_46_2_2_get, NULL, 0},
    {1, field_fmt_47_47_2_2_info, field_fmt_47_47_2_2_set, field_fmt_47_47_2_2_get, NULL, 0},
    {1, field_fmt_48_51_2_2_info, field_fmt_48_51_2_2_set, field_fmt_48_51_2_2_get, NULL, 0},
    {1, field_fmt_52_53_2_2_info, field_fmt_52_53_2_2_set, field_fmt_52_53_2_2_get, NULL, 0},
    {1, field_fmt_54_55_2_2_info, field_fmt_54_55_2_2_set, field_fmt_54_55_2_2_get, NULL, 0},
    {1, field_fmt_56_56_2_2_info, field_fmt_56_56_2_2_set, field_fmt_56_56_2_2_get, NULL, 0},
    {1, field_fmt_57_60_2_2_info, field_fmt_57_60_2_2_set, field_fmt_57_60_2_2_get, NULL, 0},
    {1, field_fmt_64_71_1_1_info, field_fmt_64_71_1_1_set, field_fmt_64_71_1_1_get, NULL, 0},
    {1, field_fmt_72_79_1_1_info, field_fmt_72_79_1_1_set, field_fmt_72_79_1_1_get, NULL, 0},
    {1, field_fmt_80_80_1_1_info, field_fmt_80_80_1_1_set, field_fmt_80_80_1_1_get, NULL, 0},
    {1, field_fmt_81_81_1_1_info, field_fmt_81_81_1_1_set, field_fmt_81_81_1_1_get, NULL, 0},
    {1, field_fmt_82_82_1_1_info, field_fmt_82_82_1_1_set, field_fmt_82_82_1_1_get, NULL, 0},
    {1, field_fmt_83_83_1_1_info, field_fmt_83_83_1_1_set, field_fmt_83_83_1_1_get, NULL, 0},
    {1, field_fmt_83_83_1_1_info, field_fmt_83_83_1_1_set, field_fmt_83_83_1_1_get, NULL, 0},
    {1, field_fmt_84_84_1_1_info, field_fmt_84_84_1_1_set, field_fmt_84_84_1_1_get, NULL, 0},
    {1, field_fmt_85_85_1_1_info, field_fmt_85_85_1_1_set, field_fmt_85_85_1_1_get, NULL, 0},
    {1, field_fmt_86_86_1_1_info, field_fmt_86_86_1_1_set, field_fmt_86_86_1_1_get, NULL, 0},
    {1, field_fmt_87_94_1_1_info, field_fmt_87_94_1_1_set, field_fmt_87_94_1_1_get, NULL, 0},
    {1, field_fmt_95_95_1_1_info, field_fmt_95_95_1_1_set, field_fmt_95_95_1_1_get, NULL, 0},
    {1, field_fmt_96_101_0_0_info, field_fmt_96_101_0_0_set, field_fmt_96_101_0_0_get, NULL, 0},
    {1, field_fmt_120_125_0_0_info, field_fmt_120_125_0_0_set, field_fmt_120_125_0_0_get, bcm78800_a0_txpmd_header_type_names, 0},
    {1, field_fmt_126_127_0_0_info, field_fmt_126_127_0_0_set, field_fmt_126_127_0_0_get, bcm78800_a0_txpmd_start_names, 0},

};

static const shr_enum_map_t bcm78800_a0_txpmd_names[] =
{
    BCM78800_A0_TXPMD_NAME_MAP_INIT
};

bcmpkt_pmd_info_t bcm78800_a0_txpmd_info_get(void)
{
    bcmpkt_pmd_info_t bcm78800_a0_txpmd_info = {4, BCM78800_A0_TXPMD_COUNT, bcm78800_a0_txpmd_names, bcm78800_a0_txpmd_fields};
    return bcm78800_a0_txpmd_info;
}

bcmpkt_pmd_info_t bcm78800_a0_lbhdr_info_get(void)
{
    bcmpkt_pmd_info_t bcm78800_a0_lbhdr_info = {0, 0, NULL, NULL};
    return bcm78800_a0_lbhdr_info;
}
