#include <linux/module.h> 
#include <linux/kernel.h> 
#include <linux/fs.h>
#include <asm/uaccess.h>
#include "ioctl_1.h"


MODULE_LICENSE("GPL");

#define DEVICE_NAME "test_ioctl_1"
#define BUFFER_SIZE 100

int Major;
char msg[BUFFER_SIZE];
char *msg_Ptr = msg, *msg_end_Ptr = msg + BUFFER_SIZE - 1;
char *msg_temp_Ptr = msg;
int Device_Open = 0;

static ssize_t device_read(struct file *filp, char *buffer, 
                           size_t length, loff_t * offset);
static ssize_t device_write (struct file *filp, const char *buffer, 
                             size_t length, loff_t * offset);                           
static int device_open(struct inode *inode, struct file *file);
static int device_release(struct inode *inode, struct file *file);

struct file_operations fops = {
    .read = device_read,
    .write = device_write,
    .open = device_open,
    .release = device_release
};

int init_module(void) 
{
    Major = register_chrdev(0, DEVICE_NAME, &fops);
    if (Major < 0) {
        printk(KERN_ALERT "Registering char device failed with %d\n", Major);
        return Major;
    }
    printk(KERN_INFO "I was assigned major number %d. To talk to\n", Major);
    printk(KERN_INFO "the driver, create a dev file with\n");
    printk(KERN_INFO "'mknod /dev/%s c %d 0'.\n", DEVICE_NAME, Major);
    return 0;
}

void cleanup_module(void) 
{
    unregister_chrdev(Major, DEVICE_NAME);
    printk(KERN_INFO "Сleanup_module %s OK\n", DEVICE_NAME);
}

static int device_open(struct inode *inode, struct file *file)
{
    if (Device_Open)
        return -EBUSY;
    Device_Open++; 
    try_module_get(THIS_MODULE);
    return 0;
}

static int device_release(struct inode *inode, struct file *file)
{
    Device_Open--;
    module_put(THIS_MODULE);
    return 0;
}

static ssize_t device_read(struct file *filp, char *buffer, 
                           size_t length, loff_t * offset)
{
    int bytes_read = 0; 
    if (length <= 0) return 0;
    while (length && (msg_Ptr != msg_temp_Ptr)) {
        put_user(*msg_Ptr, buffer);
        msg_Ptr++;
        buffer++;
        if (msg_Ptr > msg_end_Ptr) msg_Ptr = msg;
        length--;
        bytes_read++;
    }
    return bytes_read;
}

static ssize_t device_write (struct file *filp, const char *buffer, 
                             size_t length, loff_t * offset)
{
    int bytes_write = 0;
    bool change_beg = false; 
    if (length <= 0) return 0;
    while (length) {
        get_user(*msg_temp_Ptr, buffer);
        if (msg_temp_Ptr == msg_Ptr) change_beg = true;
        msg_temp_Ptr++;
        buffer++;
        if (msg_temp_Ptr > msg_end_Ptr) msg_temp_Ptr = msg;
        length--;
        bytes_write++;
    }
    if (change_beg) msg_Ptr = msg_temp_Ptr;
    return bytes_write;
}

int device_ioctl(struct inode *inode,struct file *filp, ulong cmd, ulong arg)
{
    int ret=0;
    switch (cmd) {
    case IOC_RES: msg_temp_Ptr = msg; msg_Ptr = msg;
    break;
    default: 
    return -ENOTTY;
    }
    return ret;
}


 
