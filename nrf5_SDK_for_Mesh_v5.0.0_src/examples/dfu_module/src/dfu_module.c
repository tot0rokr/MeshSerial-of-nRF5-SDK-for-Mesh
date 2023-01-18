/* Copyright (c) 2010 - 2020, Nordic Semiconductor ASA
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form, except as embedded into a Nordic
 *    Semiconductor ASA integrated circuit in a product or a software update for
 *    such product, must reproduce the above copyright notice, this list of
 *    conditions and the following disclaimer in the documentation and/or other
 *    materials provided with the distribution.
 *
 * 3. Neither the name of Nordic Semiconductor ASA nor the names of its
 *    contributors may be used to endorse or promote products derived from this
 *    software without specific prior written permission.
 *
 * 4. This software, with or without modification, must only be used with a
 *    Nordic Semiconductor ASA integrated circuit.
 *
 * 5. Any software provided in binary form under this license must not be reverse
 *    engineered, decompiled, modified and/or disassembled.
 *
 * THIS SOFTWARE IS PROVIDED BY NORDIC SEMICONDUCTOR ASA "AS IS" AND ANY EXPRESS
 * OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY, NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL NORDIC SEMICONDUCTOR ASA OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
 * GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include <boards.h>
#include "nrf_mesh_events.h"
#include "log.h"
#include "nrf_mesh_dfu.h"
#include "mesh_app_utils.h"
#include "mesh_stack.h"
#include "ble_softdevice_support.h"
#include "mesh_provisionee.h"
#include "nrf_mesh_config_examples.h"
#include "simple_hal.h"
#include "app_timer.h"
#include "example_common.h"
#include "mesh_app_utils.h"
#include "nrf_mesh_configure.h"
#include "app_util.h"
#if NRF_MESH_SERIAL_ENABLE
#include "nrf_mesh_serial.h"
#endif
#include "dfu_module.h"

/*****************************************************************************
 * Definitions
 *****************************************************************************/
/* LED mask bit 0 (1,2,..) represents BSP_LED_0 (1,2,..) from boards.h */
#define LEDS_MASK_DFU_RUNNING   (0x05)  /* BSP_LED_0 and BSP_LED_2 */
#define LEDS_MASK_DFU_ENDED     (0x03)  /* BSP_LED_0 and BSP_LED_1 */


/*****************************************************************************
 * Forward declaration of static functions
 *****************************************************************************/


/*****************************************************************************
 * Static variables
 *****************************************************************************/
static nrf_mesh_evt_handler_t m_evt_handler;
void (*dfu_module_default_log_callback)(uint32_t, const char *, uint16_t,
	uint32_t, const char *, va_list) = log_callback_rtt;
    
#if DFU_MODULE_DK_LED_ENABLE
static void dfu_module_dk_leds_init()
{
	__LOG(LOG_SRC_APP, LOG_LEVEL_INFO, "DFU led init\n");
    hal_leds_init();
	__LOG(LOG_SRC_APP, LOG_LEVEL_INFO, "DFU led init!\n");
}
static void dfu_module_dk_led_mask_set(uint32_t led_mask, bool value)
{
	__LOG(LOG_SRC_APP, LOG_LEVEL_INFO, "DFU led set\n");
	hal_led_mask_set(led_mask, value);
	__LOG(LOG_SRC_APP, LOG_LEVEL_INFO, "DFU led set!\n");
}
#else /* if DFU_MODULE_DK_LED_ENABLE */
static void dfu_module_dk_leds_init() {}
static void dfu_module_dk_led_mask_set(uint32_t led_mask, bool value) {}
#endif /* if DFU_MODULE_DK_LED_ENABLE */


static bool fw_updated_event_is_for_me(const nrf_mesh_evt_dfu_t * p_evt)
{
    switch (p_evt->fw_outdated.transfer.dfu_type)
    {
        case NRF_MESH_DFU_TYPE_APPLICATION:
            __LOG(LOG_SRC_APP, LOG_LEVEL_INFO, "DFU type Application\n");
            return (p_evt->fw_outdated.current.application.app_id == p_evt->fw_outdated.transfer.id.application.app_id &&
                    p_evt->fw_outdated.current.application.company_id == p_evt->fw_outdated.transfer.id.application.company_id &&
                    p_evt->fw_outdated.current.application.app_version < p_evt->fw_outdated.transfer.id.application.app_version);

        case NRF_MESH_DFU_TYPE_BOOTLOADER:
            __LOG(LOG_SRC_APP, LOG_LEVEL_INFO, "DFU type Bootloader\n");
            return (p_evt->fw_outdated.current.bootloader.bl_id == p_evt->fw_outdated.transfer.id.bootloader.bl_id &&
                    p_evt->fw_outdated.current.bootloader.bl_version < p_evt->fw_outdated.transfer.id.bootloader.bl_version);

        case NRF_MESH_DFU_TYPE_SOFTDEVICE:
            __LOG(LOG_SRC_APP, LOG_LEVEL_INFO, "DFU type Softdevice\n");
            return false;

        default:
            return false;
    }
}

static const uint32_t * optimal_bank_address(void)
{
    /* The incoming transfer has to fit on both sides of the bank address: First it needs to fit
     * above the bank address when we receive it, then it needs to fit below the bank address when
     * we install it. We want to put the bank address in the middle of the available application
     * code area, to maximize the potential transfer size we can accept. */
    const uint32_t * p_start;
    uint32_t dummy;
    ERROR_CHECK(mesh_stack_persistence_flash_usage(&p_start, &dummy));

    uint32_t middle_of_app_area = (CODE_START + (intptr_t) p_start) / 2;

    /* The bank can't start in the middle of the application code, and should be page aligned: */
    return (const uint32_t *) ALIGN_VAL(MAX(middle_of_app_area, CODE_END), PAGE_SIZE);
}

static void mesh_evt_handler(const nrf_mesh_evt_t* p_evt)
{
    switch (p_evt->type)
    {
        case NRF_MESH_EVT_DFU_FIRMWARE_OUTDATED:
        case NRF_MESH_EVT_DFU_FIRMWARE_OUTDATED_NO_AUTH:
            if (fw_updated_event_is_for_me(&p_evt->params.dfu))
            {
                const uint32_t * p_bank = optimal_bank_address();
                __LOG(LOG_SRC_APP, LOG_LEVEL_INFO, "Requesting DFU transfer with bank at 0x%p\n", p_bank);

                ERROR_CHECK(nrf_mesh_dfu_request(p_evt->params.dfu.fw_outdated.transfer.dfu_type,
                                                 &p_evt->params.dfu.fw_outdated.transfer.id,
                                                 p_bank));
                dfu_module_dk_led_mask_set(HAL_LED_MASK, false); /* Turn off all LEDs */
            }
            else
            {
                /**
                 * While preparing for the start of the DFU process, the DFU module
                 * will notify about any other ongoing DFU transfers by sending
                 * @ref NRF_MESH_EVT_DFU_FIRMWARE_OUTDATED_NO_AUTH or
                 * @ref NRF_MESH_EVT_DFU_FIRMWARE_OUTDATED.
                 *
                 * Check the current DFU state to avoid reverting the target state
                 * to the relay state.
                 */
                nrf_mesh_dfu_transfer_state_t state;
                uint32_t error_code = nrf_mesh_dfu_state_get(&state);
                if (error_code == NRF_SUCCESS && (state.state == NRF_MESH_DFU_STATE_INITIALIZED ||
                                                  state.state == NRF_MESH_DFU_STATE_FIND_FWID ||
                                                  state.state == NRF_MESH_DFU_STATE_RELAY_CANDIDATE ||
                                                  state.state == NRF_MESH_DFU_STATE_RELAY))
                {
                    __LOG(LOG_SRC_APP, LOG_LEVEL_INFO, "Starting relay\n");
                    ERROR_CHECK(nrf_mesh_dfu_relay(p_evt->params.dfu.fw_outdated.transfer.dfu_type,
                                                    &p_evt->params.dfu.fw_outdated.transfer.id));
                }
            }
            break;

        case NRF_MESH_EVT_DFU_START:
            dfu_module_dk_led_mask_set(LEDS_MASK_DFU_RUNNING, true);
            break;

        case NRF_MESH_EVT_DFU_END:
            dfu_module_dk_led_mask_set(HAL_LED_MASK, false); /* Turn off all LEDs */
            dfu_module_dk_led_mask_set(LEDS_MASK_DFU_ENDED, true);
            break;

        case NRF_MESH_EVT_DFU_BANK_AVAILABLE:
            dfu_module_dk_led_mask_set(HAL_LED_MASK, false); /* Turn off all LEDs */
            ERROR_CHECK(nrf_mesh_dfu_bank_flash(p_evt->params.dfu.bank.transfer.dfu_type));
            break;

        default:
            break;

    }
}

void dfu_module_mesh_init(void)
{
#if NRF_MESH_SERIAL_ENABLE
    ERROR_CHECK(nrf_mesh_serial_init(NULL));
    __LOG(LOG_SRC_APP, LOG_LEVEL_INFO, "Initialize serial interface...\n");
#endif

    m_evt_handler.evt_cb = mesh_evt_handler;
    nrf_mesh_evt_handler_add(&m_evt_handler);
}

void dfu_module_initialize(void)
{
	dfu_module_dk_leds_init();
    __LOG(LOG_SRC_APP, LOG_LEVEL_INFO, "DFU module initialized!\n");
}

void dfu_module_start(void)
{
#if NRF_MESH_SERIAL_ENABLE
    __LOG(LOG_SRC_APP, LOG_LEVEL_INFO, "Enabling serial interface...\n");
    ERROR_CHECK(nrf_mesh_serial_enable());
#endif

    __LOG(LOG_SRC_APP, LOG_LEVEL_INFO, "DFU module started!\n");
}
