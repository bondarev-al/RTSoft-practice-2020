#include <linux/module.h> 
#include <linux/kernel.h> 
#include <linux/fs.h>
#include <asm/uaccess.h>


MODULE_LICENSE("GPL");

#define DEVICE_NAME "test_char_dev"

int Major;
char msg[100];
char *msg_Ptr;
int Device_Open = 0;

static ssize_t device_read(struct file *filp, char *buffer, 
                           size_t length, loff_t * offset);
static int device_open(struct inode *inode, struct file *file);
static int device_release(struct inode *inode, struct file *file);

struct file_operations fops = {
    .read = device_read,
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
    printk(KERN_ALERT "Сleanup_module OK \n");
}

static int device_open(struct inode *inode, struct file *file)
{
    static int counter = 0;
    if (Device_Open)
        return -EBUSY;
    Device_Open++;
    sprintf(msg, "I already told you %d times Hello world!\n", counter++);
    msg_Ptr = msg;
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
    if (*msg_Ptr == 0) return 0;
    while (length && *msg_Ptr) {
        put_user(*(msg_Ptr++), buffer++);
        length--;
        bytes_read++;
    }
    return bytes_read;
}

 
