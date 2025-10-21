/*
*
* Licensed under the GNU General Public License Version 2
*
* This program is free software; you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation; either version 2 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
*/

/*
* pddf_xilinx_device_7021_algo.c
* Description:
*   A sample i2c driver algorithms for Xilinx Corporation Device 7021 FPGA adapters
*
*********************************************************************************/
#define __STDC_WANT_LIB_EXT1__ 1
#include <linux/string.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/delay.h>
#include <linux/jiffies.h>
#include <linux/errno.h>
#include <linux/i2c.h>
#include "../../../../pddf/i2c/modules/include/pddf_i2c_algo.h"

#define DEBUG 0

enum {
    STATE_DONE = 0,
    STATE_INIT,
    STATE_ADDR,
    STATE_ADDR10,
    STATE_START,
    STATE_WRITE,
    STATE_READ,
    STATE_STOP,
    STATE_ERROR,
};

#define XIIC_MSB_OFFSET 0
#define XIIC_REG_OFFSET (0x100 + XIIC_MSB_OFFSET)

/*
 * Register offsets in bytes from RegisterBase. Three is added to the
 * base offset to access LSB (IBM style) of the word
 */
#define XIIC_CR_REG_OFFSET   (0x00 + XIIC_REG_OFFSET)	/* Control Register   */
#define XIIC_SR_REG_OFFSET   (0x04 + XIIC_REG_OFFSET)	/* Status Register    */
#define XIIC_DTR_REG_OFFSET  (0x08 + XIIC_REG_OFFSET)	/* Data Tx Register   */
#define XIIC_DRR_REG_OFFSET  (0x0C + XIIC_REG_OFFSET)	/* Data Rx Register   */
#define XIIC_ADR_REG_OFFSET  (0x10 + XIIC_REG_OFFSET)	/* Address Register   */
#define XIIC_TFO_REG_OFFSET  (0x14 + XIIC_REG_OFFSET)	/* Tx FIFO Occupancy  */
#define XIIC_RFO_REG_OFFSET  (0x18 + XIIC_REG_OFFSET)	/* Rx FIFO Occupancy  */
#define XIIC_TBA_REG_OFFSET  (0x1C + XIIC_REG_OFFSET)	/* 10 Bit Address reg */
#define XIIC_RFD_REG_OFFSET  (0x20 + XIIC_REG_OFFSET)	/* Rx FIFO Depth reg  */
#define XIIC_GPO_REG_OFFSET  (0x24 + XIIC_REG_OFFSET)	/* Output Register    */

/* Control Register masks */
#define XIIC_CR_ENABLE_DEVICE_MASK        0x01	/* Device enable = 1      */
#define XIIC_CR_TX_FIFO_RESET_MASK        0x02	/* Transmit FIFO reset=1  */
#define XIIC_CR_MSMS_MASK                 0x04	/* Master starts Txing=1  */
#define XIIC_CR_DIR_IS_TX_MASK            0x08	/* Dir of tx. Txing=1     */
#define XIIC_CR_NO_ACK_MASK               0x10	/* Tx Ack. NO ack = 1     */
#define XIIC_CR_REPEATED_START_MASK       0x20	/* Repeated start = 1     */
#define XIIC_CR_GENERAL_CALL_MASK         0x40	/* Gen Call enabled = 1   */

/* Status Register masks */
#define XIIC_SR_GEN_CALL_MASK             0x01	/* 1=a mstr issued a GC   */
#define XIIC_SR_ADDR_AS_SLAVE_MASK        0x02	/* 1=when addr as slave   */
#define XIIC_SR_BUS_BUSY_MASK             0x04	/* 1 = bus is busy        */
#define XIIC_SR_MSTR_RDING_SLAVE_MASK     0x08	/* 1=Dir: mstr <-- slave  */
#define XIIC_SR_TX_FIFO_FULL_MASK         0x10	/* 1 = Tx FIFO full       */
#define XIIC_SR_RX_FIFO_FULL_MASK         0x20	/* 1 = Rx FIFO full       */
#define XIIC_SR_RX_FIFO_EMPTY_MASK        0x40	/* 1 = Rx FIFO empty      */
#define XIIC_SR_TX_FIFO_EMPTY_MASK        0x80	/* 1 = Tx FIFO empty      */

/* Interrupt Status Register masks    Interrupt occurs when...       */
#define XIIC_INTR_ARB_LOST_MASK           0x01	/* 1 = arbitration lost   */
#define XIIC_INTR_TX_ERROR_MASK           0x02	/* 1=Tx error/msg complete */
#define XIIC_INTR_TX_EMPTY_MASK           0x04	/* 1 = Tx FIFO/reg empty  */
#define XIIC_INTR_RX_FULL_MASK            0x08	/* 1=Rx FIFO/reg=OCY level */
#define XIIC_INTR_BNB_MASK                0x10	/* 1 = Bus not busy       */
#define XIIC_INTR_AAS_MASK                0x20	/* 1 = when addr as slave */
#define XIIC_INTR_NAAS_MASK               0x40	/* 1 = not addr as slave  */
#define XIIC_INTR_TX_HALF_MASK            0x80	/* 1 = TX FIFO half empty */

/* The following constants specify the depth of the FIFOs */
#define IIC_RX_FIFO_DEPTH         16	/* Rx fifo capacity               */
#define IIC_TX_FIFO_DEPTH         16	/* Tx fifo capacity               */

/*
 * Tx Fifo upper bit masks.
 */
#define XIIC_TX_DYN_START_MASK            0x0100 /* 1 = Set dynamic start */
#define XIIC_TX_DYN_STOP_MASK             0x0200 /* 1 = Set dynamic stop */

/*
 * The following constants define the register offsets for the Interrupt
 * registers. There are some holes in the memory map for reserved addresses
 * to allow other registers to be added and still match the memory map of the
 * interrupt controller registers
 */
#define XIIC_IISR_OFFSET     0x20 /* Interrupt Status Register */
#define XIIC_RESETR_OFFSET   0x40 /* Reset Register */

#define XIIC_RESET_MASK             0xAUL

#define XIIC_PM_TIMEOUT		1000	/* ms */
/* timeout waiting for the controller to respond */
#define XIIC_I2C_TIMEOUT	(msecs_to_jiffies(1000))

struct fpgalogic_i2c {
    void __iomem *base;
    u32 reg_shift;
    u32 reg_io_width;
    wait_queue_head_t wait;
    struct i2c_msg *msg;
    int pos;
    int nmsgs;
    int state; /* see STATE_ */
    int ip_clock_khz;
    int bus_clock_khz;
    void (*reg_set)(struct fpgalogic_i2c *i2c, int reg, u8 value);
    u8 (*reg_get)(struct fpgalogic_i2c *i2c, int reg);
    u32 timeout;
    struct mutex lock;
};
static struct fpgalogic_i2c fpgalogic_i2c[I2C_PCI_MAX_BUS];
extern void __iomem * fpga_ctl_addr;
extern int (*ptr_fpgapci_read)(uint32_t);
extern int (*ptr_fpgapci_write)(uint32_t, uint32_t);
extern int (*pddf_i2c_pci_add_numbered_bus)(struct i2c_adapter *, int);
static int xiic_reinit(struct fpgalogic_i2c *i2c);

void i2c_get_mutex(struct fpgalogic_i2c *i2c)
{
    mutex_lock(&i2c->lock);
}

/**
 * i2c_release_mutex - release mutex
 */
void i2c_release_mutex(struct fpgalogic_i2c *i2c)
{
    mutex_unlock(&i2c->lock);
}

static inline void xiic_setreg32(struct fpgalogic_i2c *i2c, int reg, int value)
{
	(void)iowrite32(value, i2c->base + reg);
}

static inline int xiic_getreg32(struct fpgalogic_i2c *i2c, int reg)
{
	u32 ret;

	ret = ioread32(i2c->base + reg);
	
	return ret;
}

static inline void xiic_irq_clr(struct fpgalogic_i2c *i2c, u32 mask)
{
	u32 isr = xiic_getreg32(i2c, XIIC_IISR_OFFSET);

	xiic_setreg32(i2c, XIIC_IISR_OFFSET, isr & mask);
}

static int xiic_clear_rx_fifo(struct fpgalogic_i2c *i2c)
{
	u8 sr;
	unsigned long timeout;

	timeout = jiffies + XIIC_I2C_TIMEOUT;
	for (sr = xiic_getreg32(i2c, XIIC_SR_REG_OFFSET);
		!(sr & XIIC_SR_RX_FIFO_EMPTY_MASK);
		sr = xiic_getreg32(i2c, XIIC_SR_REG_OFFSET)) {
		xiic_getreg32(i2c, XIIC_DRR_REG_OFFSET);
		if (time_after(jiffies, timeout)) {
			printk("Failed to clear rx fifo\n");
			return -ETIMEDOUT;
		}
	}

	return 0;
}

/**
 * Wait until something change in a given register
 * @i2c: ocores I2C device instance
 * @reg: register to query
 * @mask: bitmask to apply on register value
 * @val: expected result
 * @timeout: timeout in jiffies
 *
 * Timeout is necessary to avoid to stay here forever when the chip
 * does not answer correctly.
 *
 * Return: 0 on success, -ETIMEDOUT on timeout
 */
static int poll_wait(struct fpgalogic_i2c *i2c,
		       int reg, u8 mask, u8 val,
		       const unsigned long timeout)
{
	unsigned long j;
	u8 status = 0;

	j = jiffies + timeout;
	while (1) {
		mutex_lock(&i2c->lock);
		status = xiic_getreg32(i2c, reg);
		mutex_unlock(&i2c->lock);
		if ((status & mask) == val)
			break;
		if (time_after(jiffies, j))
			return -ETIMEDOUT;
                cpu_relax();
                cond_resched();		
	}
	return 0;
}

/**
 * Wait until is possible to process some data
 * @i2c: ocores I2C device instance
 *
 * Used when the device is in polling mode (interrupts disabled).
 *
 * Return: 0 on success, -ETIMEDOUT on timeout
 */
static int ocores_poll_wait(struct fpgalogic_i2c *i2c)
{
	u8 mask = 0, status = 0;
	int err = 0;
	int val = 0;
	int tmp = 0;
	mutex_lock(&i2c->lock);
	if (i2c->state == STATE_DONE) {
		/* transfer is over */
		mask = XIIC_SR_BUS_BUSY_MASK;
	} else if (i2c->state == STATE_WRITE || i2c->state == STATE_START){
		/* on going transfer */
		if (0 == i2c->msg->len){
			mask = XIIC_INTR_TX_ERROR_MASK;
		} else {
			mask = XIIC_SR_TX_FIFO_FULL_MASK;
		}
	}
	else if (i2c->state == STATE_READ){
		/* on going receive */
		mask = XIIC_SR_TX_FIFO_EMPTY_MASK | XIIC_SR_RX_FIFO_EMPTY_MASK;
	}
	mutex_unlock(&i2c->lock);
	// printk("Wait for: 0x%x\n", mask);

	/*
	 * once we are here we expect to get the expected result immediately
	 * so if after 50ms we timeout then something is broken.
	 */
	
	if (1 == i2c->nmsgs && 0 == i2c->msg->len && i2c->state == STATE_START && !(i2c->msg->flags & I2C_M_RD)) { 	/* for i2cdetect I2C_SMBUS_QUICK mode*/
		err = poll_wait(i2c, XIIC_IISR_OFFSET, mask, mask, msecs_to_jiffies(50));
		mutex_lock(&i2c->lock);
		status = xiic_getreg32(i2c, XIIC_SR_REG_OFFSET);
		mutex_unlock(&i2c->lock);
		if (0 != err) { /* AXI IIC as an transceiver , if ever an XIIC_INTR_TX_ERROR_MASK interrupt happens, means no such i2c device */
			err = 0;
		} else {
			err = -ETIMEDOUT;
		}
	}
	else {
		if (mask & XIIC_SR_TX_FIFO_EMPTY_MASK){
			err = poll_wait(i2c, XIIC_SR_REG_OFFSET, mask, XIIC_SR_TX_FIFO_EMPTY_MASK, msecs_to_jiffies(50));
			mask &= ~XIIC_SR_TX_FIFO_EMPTY_MASK;
		}
		if (0 == err){
			err = poll_wait(i2c, XIIC_SR_REG_OFFSET, mask, 0, msecs_to_jiffies(50));
		}
		mutex_lock(&i2c->lock);
		status = xiic_getreg32(i2c, XIIC_IISR_OFFSET);	
		
		if ((status & XIIC_INTR_ARB_LOST_MASK) ||
			((status & XIIC_INTR_TX_ERROR_MASK) &&
			!(status & XIIC_INTR_RX_FULL_MASK) &&
			!(i2c->msg->flags & I2C_M_RD))) {  /* AXI IIC as an transceiver , if ever an XIIC_INTR_TX_ERROR_MASK interrupt happens, return */
			err = -ETIMEDOUT;
			
			if (status & XIIC_INTR_ARB_LOST_MASK) {
				val = xiic_getreg32(i2c, XIIC_CR_REG_OFFSET);
				tmp = XIIC_CR_MSMS_MASK;
				val &=(~tmp);
				xiic_setreg32(i2c, XIIC_CR_REG_OFFSET, val);
				xiic_setreg32(i2c, XIIC_IISR_OFFSET, XIIC_INTR_ARB_LOST_MASK);
				printk("%s: TRANSFER STATUS ERROR, ISR: bit 0x%x happens\n",
					 __func__, XIIC_INTR_ARB_LOST_MASK);
			} 
			if (status & XIIC_INTR_TX_ERROR_MASK) {
				int sta = 0;
				int cr = 0;
				sta = xiic_getreg32(i2c,XIIC_SR_REG_OFFSET);
				cr = xiic_getreg32(i2c,XIIC_CR_REG_OFFSET);
				xiic_setreg32(i2c, XIIC_IISR_OFFSET, XIIC_INTR_TX_ERROR_MASK);
				printk("%s: TRANSFER STATUS ERROR, ISR: bit 0x%x happens; SR: bit 0x%x; CR: bit 0x%x\n",
					 __func__, status, sta, cr);
			}
			/* Soft reset IIC controller. */
			xiic_setreg32(i2c, XIIC_RESETR_OFFSET, XIIC_RESET_MASK);
			(void)xiic_reinit(i2c);
			mutex_unlock(&i2c->lock);
			return err;
		}
		mutex_unlock(&i2c->lock);
	}
	
	return err;
}

static void ocores_process(struct fpgalogic_i2c *i2c)
{
	struct i2c_msg *msg = i2c->msg;
	//unsigned long flags;
	u16 val;

	/*
	 * If we spin here because we are in timeout, so we are going
	 * to be in STATE_ERROR. See ocores_process_timeout()
	 */
	mutex_lock(&i2c->lock);
	// printk("STATE: %d\n", i2c->state);

	if (i2c->state == STATE_START) {
		i2c->state =(msg->flags & I2C_M_RD) ? STATE_READ : STATE_WRITE;
		/* if it's the time sequence is 'start bit + address + read bit + stop bit' */
		if (i2c->state == STATE_READ){
			/* it's the last message so we include dynamic stop bit with length */
			val = msg->len | XIIC_TX_DYN_STOP_MASK;
			xiic_setreg32(i2c, XIIC_DTR_REG_OFFSET, val);
			goto out;
		}
	}
	if (i2c->state == STATE_READ){
                /* suit for I2C_FUNC_SMBUS_BLOCK_DATA */
                if (msg->flags & I2C_M_RECV_LEN) {
                        msg->len = xiic_getreg32(i2c, XIIC_DRR_REG_OFFSET);
                        msg->flags &= ~I2C_M_RECV_LEN;
                        msg->buf[i2c->pos++] = msg->len;
                }
                else {
                        msg->buf[i2c->pos++] = xiic_getreg32(i2c, XIIC_DRR_REG_OFFSET);
                }
	} else if (i2c->state == STATE_WRITE){
		/* if it reaches the last byte data to be sent */
		if ((i2c->pos == msg->len - 1) && (i2c->nmsgs == 1)){
			val = msg->buf[i2c->pos++] | XIIC_TX_DYN_STOP_MASK;
			xiic_setreg32(i2c, XIIC_DTR_REG_OFFSET, val);
			i2c->state = STATE_DONE;
			goto out;
		/* if it is not the last byte data to be sent */
		} else if (i2c->pos < msg->len) {
			xiic_setreg32(i2c, XIIC_DTR_REG_OFFSET, msg->buf[i2c->pos++]);
			goto out;
		}
	}

	/* end of msg? */
	if (i2c->pos == msg->len) {
		i2c->nmsgs--;
		i2c->pos = 0;
		if (i2c->nmsgs) {
			i2c->msg++;
			msg = i2c->msg;	
			if (!(msg->flags & I2C_M_NOSTART)) /* send start? */{
				i2c->state = STATE_START;			
				xiic_setreg32(i2c, XIIC_DTR_REG_OFFSET, i2c_8bit_addr_from_msg(msg) | XIIC_TX_DYN_START_MASK);
				goto out;
			}
		} else {	/* end? */
			i2c->state = STATE_DONE;
			goto out;
		}
	}

out:
	mutex_unlock(&i2c->lock);
	return ;
}


static int fpgai2c_poll(struct fpgalogic_i2c *i2c,
			                  struct i2c_msg *msgs, int num)
{
	int ret = 0;
	// u8 ctrl;
	
	mutex_lock(&i2c->lock);
	/* Soft reset IIC controller. */
	xiic_setreg32(i2c, XIIC_RESETR_OFFSET, XIIC_RESET_MASK);
	/* Set receive Fifo depth to maximum (zero based). */
	xiic_setreg32(i2c, XIIC_RFD_REG_OFFSET, IIC_RX_FIFO_DEPTH - 1);
		
	/* Reset Tx Fifo. */
	xiic_setreg32(i2c, XIIC_CR_REG_OFFSET, XIIC_CR_TX_FIFO_RESET_MASK);
	
	/* Enable IIC Device, remove Tx Fifo reset & disable general call. */
	xiic_setreg32(i2c, XIIC_CR_REG_OFFSET, XIIC_CR_ENABLE_DEVICE_MASK);
	
	/* set i2c clock as 100Hz. */
	//xiic_setreg32(i2c, 0x13c, 0x7C);
	
	/* make sure RX fifo is empty */
	ret = xiic_clear_rx_fifo(i2c);
	if (ret){
		mutex_unlock(&i2c->lock);
		return ret;
	}
	
	i2c->msg = msgs;
	i2c->pos = 0;
	i2c->nmsgs = num;
	i2c->state = STATE_START;

	// printk("STATE: %d\n", i2c->state);
	
	if (msgs->len == 0 && num == 1){ /* suit for i2cdetect time sequence */
		u8 status = xiic_getreg32(i2c, XIIC_IISR_OFFSET);
		xiic_irq_clr(i2c, status);
		/* send out the 1st byte data and stop bit */
		xiic_setreg32(i2c, XIIC_DTR_REG_OFFSET, i2c_8bit_addr_from_msg(msgs) | XIIC_TX_DYN_START_MASK | XIIC_TX_DYN_STOP_MASK);
	} else {
		/* send out the 1st byte data */
		xiic_setreg32(i2c, XIIC_DTR_REG_OFFSET, i2c_8bit_addr_from_msg(msgs) | XIIC_TX_DYN_START_MASK);
	}
	mutex_unlock(&i2c->lock);
	while (1) {
		int err;
		
		err = ocores_poll_wait(i2c);
		if (err) {
			i2c->state = STATE_ERROR;
			break;
		}else if (i2c->state == STATE_DONE){
			break;
		}
		ocores_process(i2c);
	}

	return (i2c->state == STATE_DONE) ? num : -EIO;
}

static int fpgai2c_xfer(struct i2c_adapter *adap, struct i2c_msg *msgs, int num)
{
    struct fpgalogic_i2c *i2c = i2c_get_adapdata(adap);
    int err = -EIO;
	u8 retry = 0, max_retry = 0;

	if( ( (1 == msgs->len && (msgs->flags & I2C_M_RD)) || (0 == msgs->len && !(msgs->flags & I2C_M_RD)) ) && num == 1 ) /* I2C_SMBUS_QUICK or I2C_SMBUS_BYTE */
		max_retry = 1;
	else
		max_retry = 5;  // retry 5 times if receive a NACK or other errors
	while( (-EIO == err) && (retry < max_retry))
	{
		err = fpgai2c_poll(i2c, msgs, num);
		retry++;
	}

     return err;

}

static u32 fpgai2c_func(struct i2c_adapter *adap)
{
/* a typical full-I2C adapter would use the following  */
    return I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL;
}

static const struct i2c_algorithm fpgai2c_algorithm= {
    .master_xfer = fpgai2c_xfer, /*write I2C messages */
    .functionality = fpgai2c_func, /* what the adapter supports */
};

static int xiic_reinit(struct fpgalogic_i2c *i2c)
{
	int ret;
	int val = 0;
	
	/* Soft reset IIC controller. */
	xiic_setreg32(i2c, XIIC_RESETR_OFFSET, XIIC_RESET_MASK);
	
	/* Set receive Fifo depth to maximum (zero based). */
	xiic_setreg32(i2c, XIIC_RFD_REG_OFFSET, IIC_RX_FIFO_DEPTH - 1);

	/* Reset Tx Fifo. */
	xiic_setreg32(i2c, XIIC_CR_REG_OFFSET, XIIC_CR_TX_FIFO_RESET_MASK);

	/* Enable IIC Device, remove Tx Fifo reset & disable general call. */
	val |= XIIC_CR_ENABLE_DEVICE_MASK;
	//val |= XIIC_CR_TX_FIFO_RESET_MASK;
	//val |= XIIC_CR_MSMS_MASK;
	val |= XIIC_CR_DIR_IS_TX_MASK;
	xiic_setreg32(i2c, XIIC_CR_REG_OFFSET, val);

	/* make sure RX fifo is empty */
	ret = xiic_clear_rx_fifo(i2c);
	if (ret)
		return ret;

	return 0;
}

static int fpgai2c_init(struct fpgalogic_i2c *i2c)
{
    // int prescale;
    // int diff;
    // u8 ctrl;
	int ret;

	
    //i2c->reg_set = xiic_setreg32;
    //i2c->reg_get = xiic_getreg32;
	
	ret = xiic_reinit(i2c);
	if (ret < 0) {
		printk("Cannot xiic_reinit\n");
		return ret;
	}

    /* Initialize interrupt handlers if not already done */
    init_waitqueue_head(&i2c->wait);
    return 0;
}

static int adap_data_init(struct i2c_adapter *adap, int i2c_ch_index)
{
    struct fpgapci_devdata *pci_privdata = 0;
    pci_privdata = (struct fpgapci_devdata*) dev_get_drvdata(adap->dev.parent);

    if (pci_privdata == 0) {
        printk("[%s]: ERROR pci_privdata is 0\n", __FUNCTION__);
        return -1;
    }
#if DEBUG
    pddf_dbg(FPGA, KERN_INFO "[%s] index: [%d] fpga_data__base_addr:0x%0x8lx"
        " fpgapci_bar_len:0x%08lx fpga_i2c_ch_base_addr:0x%08lx ch_size=0x%x supported_i2c_ch=%d",
             __FUNCTION__, i2c_ch_index, pci_privdata->fpga_data_base_addr,
            pci_privdata->bar_length, pci_privdata->fpga_i2c_ch_base_addr,
            pci_privdata->fpga_i2c_ch_size, pci_privdata->max_fpga_i2c_ch);
#endif
    if (i2c_ch_index >= pci_privdata->max_fpga_i2c_ch || pci_privdata->max_fpga_i2c_ch > I2C_PCI_MAX_BUS) {
        printk("[%s]: ERROR i2c_ch_index=%d max_ch_index=%d out of range: %d\n",
             __FUNCTION__, i2c_ch_index, pci_privdata->max_fpga_i2c_ch, I2C_PCI_MAX_BUS);
        return -1;
    }
#ifdef __STDC_LIB_EXT1__
    memset_s(&fpgalogic_i2c[i2c_ch_index], sizeof(fpgalogic_i2c[0]), 0, sizeof(fpgalogic_i2c[0]));
#else
    memset(&fpgalogic_i2c[i2c_ch_index], 0, sizeof(fpgalogic_i2c[0]));
#endif
   
    fpgalogic_i2c[i2c_ch_index].base = pci_privdata->fpga_i2c_ch_base_addr +
                          i2c_ch_index* pci_privdata->fpga_i2c_ch_size;
    mutex_init(&fpgalogic_i2c[i2c_ch_index].lock);
    fpgai2c_init(&fpgalogic_i2c[i2c_ch_index]);


    adap->algo_data = &fpgalogic_i2c[i2c_ch_index];
    i2c_set_adapdata(adap, &fpgalogic_i2c[i2c_ch_index]);
    return 0;
}

static int pddf_i2c_pci_add_numbered_bus_default (struct i2c_adapter *adap, int i2c_ch_index)
{
    int ret = 0;

    adap_data_init(adap, i2c_ch_index);
    adap->algo = &fpgai2c_algorithm;

    ret = i2c_add_numbered_adapter(adap);
    return ret;
}

/*
 * FPGAPCI APIs
 */
int board_i2c_fpgapci_read(uint32_t offset)
{
	int data;
	data=ioread32(fpga_ctl_addr+offset);
	return data;
}


int board_i2c_fpgapci_write(uint32_t offset, uint32_t value)
{
	iowrite32(value, fpga_ctl_addr+offset);
	return (0);
}


static int __init pddf_xilinx_device_7021_algo_init(void)
{
    pddf_dbg(FPGA, KERN_INFO "[%s]\n", __FUNCTION__);
    pddf_i2c_pci_add_numbered_bus = pddf_i2c_pci_add_numbered_bus_default;
    ptr_fpgapci_read = board_i2c_fpgapci_read;
    ptr_fpgapci_write = board_i2c_fpgapci_write;
    return 0;
}

static void __exit pddf_xilinx_device_7021_algo_exit(void)
{
    pddf_dbg(FPGA, KERN_INFO "[%s]\n", __FUNCTION__);

    pddf_i2c_pci_add_numbered_bus = NULL;
    ptr_fpgapci_read = NULL;
    ptr_fpgapci_write = NULL;
    return;
}


module_init (pddf_xilinx_device_7021_algo_init);
module_exit (pddf_xilinx_device_7021_algo_exit);
MODULE_DESCRIPTION("Xilinx Corporation Device 7021 FPGAPCIe I2C-Bus algorithm");
MODULE_LICENSE("GPL");
