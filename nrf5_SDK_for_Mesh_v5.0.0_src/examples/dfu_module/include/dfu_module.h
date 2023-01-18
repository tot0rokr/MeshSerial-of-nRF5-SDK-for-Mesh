#ifndef DFU_MODULE_H__
#define DFU_MODULE_H__

#define DFU_MODULE_DEFAULT_LOG_MSK (LOG_MSK_DEFAULT | LOG_SRC_DFU | LOG_SRC_APP | LOG_SRC_SERIAL)
#define DFU_MODULE_DEFAULT_LOG_LEVEL LOG_LEVEL_INFO
#define DFU_MODULE_DEFAULT_LOG_CB dfu_module_default_log_callback

#ifndef DFU_MODULE_DK_LED_ENABLE
#define DFU_MODULE_DK_LED_ENABLE 0
#endif

void dfu_module_mesh_init(void);
void dfu_module_initialize(void);
void dfu_module_start(void);

#endif /* DFU_MODULE_H__ */
