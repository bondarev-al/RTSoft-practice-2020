#ifndef __MYDRIVERIO_H__
#define __MYDRIVERIO _H__
#include <linux/ioctl.h>
#define MAGIC_NUM 0xF1
#define IOC_OP _IO (MAGIC_NUM, 0)
#define IOC_CL _IO (MAGIC_NUM, 1)
#endif 
