#include <linux/module.h> 
#include <linux/kernel.h> 
MODULE_LICENSE("GPL");

int init_module(void) 
{
    printk(KERN_INFO "Hi! It's my test module.\n");
    return 0;
}

void cleanup_module(void) 
{
    printk(KERN_INFO "End of work of my test module.\n");
}
 
