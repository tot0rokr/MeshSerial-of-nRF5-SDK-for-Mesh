# DFU module

## How to use

1. DFU module cmake 설정을 추가할 application의 `CMakeLists.txt`에 추가
   1. target 변수 설정 뒤에 DFU\_module cmake file을 포함
      ```cmake
      include("${CMAKE_SOURCE_DIR}/examples/dfu_module/DFU_module.cmake")
      ```
   1. `add_executable`에 DFU module source 코드를 추가
      ```cmake
      ${DFU_MODULE_FILES}
      ```
   1. `target_include_directories`에 DFU module header directory를 추가
      ```cmake
      ${DFU_MODULE_INCLUDE_DIRECTORIES}
      ```
   1. `target_compile_definitions`에 DFU 관련 옵션을 추가
      ```cmake
      dfu_module_target_compile_definitions()
      ```
   1. `add_pc_lint`에 DFU 관련 함수를 호출
      ```cmake
      dfu_module_add_pc_lint()
      ```
   1. Light LC Server model에 추가한 예제
   ```diff
   diff --git a/nrf5_SDK_for_Mesh_v5.0.0_src/examples/light_lc/server/CMakeLists.txt b/nrf5_SDK_for_Mesh_v5.0.0_src/examples/light_lc/server/CMakeLists.txt
   index ea14052..1028bcf 100644
   --- a/nrf5_SDK_for_Mesh_v5.0.0_src/examples/light_lc/server/CMakeLists.txt
   +++ b/nrf5_SDK_for_Mesh_v5.0.0_src/examples/light_lc/server/CMakeLists.txt
   @@ -1,4 +1,5 @@
    set(target "light_lc_server_${PLATFORM}_${SOFTDEVICE}")
   +include("${CMAKE_SOURCE_DIR}/examples/dfu_module/DFU_module.cmake")

    add_executable(${target}
        "${CMAKE_CURRENT_SOURCE_DIR}/src/main.c"
   @@ -32,7 +33,9 @@ add_executable(${target}
        ${PROV_BEARER_ADV_SOURCE_FILES}
        ${PROV_BEARER_GATT_SOURCE_FILES}
        ${${PLATFORM}_SOURCE_FILES}
   -    ${${nRF5_SDK_VERSION}_SOURCE_FILES})
   +    ${${nRF5_SDK_VERSION}_SOURCE_FILES}
   +    ${DFU_MODULE_FILES}
   +    )

    target_include_directories(${target} PUBLIC
        "${CMAKE_CURRENT_SOURCE_DIR}/include"
   @@ -53,7 +56,9 @@ target_include_directories(${target} PUBLIC
        ${${SOFTDEVICE}_INCLUDE_DIRS}
        ${${PLATFORM}_INCLUDE_DIRS}
        ${${BOARD}_INCLUDE_DIRS}
   -    ${${nRF5_SDK_VERSION}_INCLUDE_DIRS})
   +    ${${nRF5_SDK_VERSION}_INCLUDE_DIRS}
   +    ${DFU_MODULE_INCLUDE_DIRECTORIES}
   +    )

    set_target_link_options(${target}
        ${CMAKE_CURRENT_SOURCE_DIR}/linker/${PLATFORM}_${SOFTDEVICE})
   @@ -69,6 +74,8 @@ target_compile_definitions(${target} PUBLIC
        ${${SOFTDEVICE}_DEFINES}
        ${${BOARD}_DEFINES})

   +dfu_module_target_compile_definitions()
   +
    target_link_libraries(${target}
        rtt_${PLATFORM}
        uECC_${PLATFORM}
   @@ -86,5 +93,6 @@ add_pc_lint(no_scene_${target}
        "${CMAKE_CURRENT_SOURCE_DIR}/src/main.c"
        "${target_include_dirs}"
        "${${PLATFORM}_DEFINES};${${SOFTDEVICE}_DEFINES};${${BOARD}_DEFINES};-DSCENE_SETUP_SERVER_INSTANCES_MAX=0")
   +dfu_module_add_pc_lint()

    add_ses_project(${target})
   ```
1. Application 코드에 DFU module 추가
   1. header 추가
      ```c
      #include "dfu_module.h"
      ```
   1. `mesh_init()` 마지막에 `dfu_module_mesh_init()` 추가
   1. `initialize()`에서 DFU log 옵션 추가
      ```c
      __LOG_INIT(DFU_MODULE_DEFAULT_LOG_MSK, DFU_MODULE_DEFAULT_LOG_LEVEL, DFU_MODULE_DEFAULT_LOG_CB)
      ```
      - Log mask는 OR bit 연산을 이용해 기존 application의 log mask와 병합 가능
      - Log level과 callback 함수는 사용자의 편의에 맞게 사용
   1. `initialize()` 처음에 `dfu_module_initialize()` 추가
   1. `start()`에서 provisionee 설정 이후 `dfu_module_start()` 추가
   1. Light LC Server model에 추가한 예제
   ```diff
   diff --git a/nrf5_SDK_for_Mesh_v5.0.0_src/examples/light_lc/server/src/main.c b/nrf5_SDK_for_Mesh_v5.0.0_src/examples/light_lc/server/src/main.c
   index e1c7f0f..f823bfd 100644
   --- a/nrf5_SDK_for_Mesh_v5.0.0_src/examples/light_lc/server/src/main.c
   +++ b/nrf5_SDK_for_Mesh_v5.0.0_src/examples/light_lc/server/src/main.c
   @@ -73,6 +73,7 @@
    #include "ble_softdevice_support.h"
    #include "app_timer.h"
    #include "app_scene.h"
   +#include "dfu_module.h"

    /*****************************************************************************
     * Definitions
   @@ -394,12 +395,15 @@ static void mesh_init(void)
            default:
                APP_ERROR_CHECK(status);
        }
   +
   +    dfu_module_mesh_init();
    }

    static void initialize(void)
    {
   -    __LOG_INIT(LOG_SRC_APP | LOG_SRC_ACCESS, LOG_LEVEL_INFO, LOG_CALLBACK_DEFAULT);
   +    __LOG_INIT(DFU_MODULE_DEFAULT_LOG_MSK | LOG_SRC_APP | LOG_SRC_ACCESS, LOG_LEVEL_INFO, LOG_CALLBACK_DEFAULT);
        __LOG(LOG_SRC_APP, LOG_LEVEL_INFO, "----- BLE Mesh LC Server Demo -----\n");
   +    dfu_module_initialize();

        pwm_utils_enable(&m_pwm);
        APP_ERROR_CHECK(app_timer_init());
   @@ -436,6 +440,8 @@ static void start(void)
            unicast_address_print();
        }

   +    dfu_module_start();
   +
        mesh_app_uuid_print(nrf_mesh_configure_device_uuid_get());

        /* NRF_MESH_EVT_ENABLED is triggered in the mesh IRQ context after the stack is fully enabled.
   ```
