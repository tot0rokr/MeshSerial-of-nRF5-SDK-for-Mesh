if (NOT DFU_MODULE MATCHES "off")
    set(DFU_DEFINITIONS
        ${USER_DEFINITIONS}
        -DUSE_APP_CONFIG
        -DCONFIG_APP_IN_CORE
        ${${PLATFORM}_DEFINES}
        ${${SOFTDEVICE}_DEFINES}
        ${${BOARD}_DEFINES})

    set(DFU_MODULE_INCLUDE_DIRECTORIES
    # include_directories(
        "${CMAKE_SOURCE_DIR}/examples/dfu_module/include"
        "${MBTLE_SOURCE_DIR}/examples"
        "${CMAKE_SOURCE_DIR}/examples/common/include"
        ${BLE_SOFTDEVICE_SUPPORT_INCLUDE_DIRS}
        ${CONFIG_SERVER_INCLUDE_DIRS}
        ${HEALTH_SERVER_INCLUDE_DIRS}
        ${MESH_INCLUDE_DIRS}
        ${${SOFTDEVICE}_INCLUDE_DIRS}
        ${${PLATFORM}_INCLUDE_DIRS}
        ${${BOARD}_INCLUDE_DIRS}
        ${SERIAL_INCLUDE_DIRS}
        ${${nRF5_SDK_VERSION}_INCLUDE_DIRS})

    set(DFU_MODULE_MESH_FILES
        "${CMAKE_SOURCE_DIR}/examples/common/src/mesh_provisionee.c"
        "${CMAKE_SOURCE_DIR}/examples/common/src/simple_hal.c"
        "${SDK_ROOT}/modules/nrfx/drivers/src/nrfx_gpiote.c"
        "${CMAKE_SOURCE_DIR}/examples/common/src/mesh_app_utils.c"
        ${BLE_SOFTDEVICE_SUPPORT_SOURCE_FILES}
        ${ACCESS_SOURCE_FILES}
        ${CONFIG_SERVER_SOURCE_FILES}
        ${HEALTH_SERVER_SOURCE_FILES}
        ${PROV_PROVISIONEE_SOURCE_FILES}
        ${PROV_COMMON_SOURCE_FILES}
        ${PROV_BEARER_ADV_SOURCE_FILES}
        ${DFU_SOURCE_FILES}
        ${WEAK_SOURCE_FILES}
        ${MESH_STACK_SOURCE_FILES}
        ${MESH_CORE_SOURCE_FILES}
        ${MESH_BEARER_SOURCE_FILES}
        ${MESH_APP_TIMER_SOURCE_FILES}
        ${${PLATFORM}_SOURCE_FILES}
        ${${nRF5_SDK_VERSION}_SOURCE_FILES})

    if ((DFU_MODULE MATCHES "serial") AND (NOT PLATFORM MATCHES "nrf52810") AND (NOT PLATFORM MATCHES "nrf52820"))

        set(DFU_MODULE_FILES
            "${CMAKE_SOURCE_DIR}/examples/dfu_module/src/dfu_module.c"
            ${SERIAL_SOURCE_FILES}
            ${DFU_MODULE_MESH_FILES})

        function(dfu_module_target_compile_definitions)

            target_compile_definitions(${target} PUBLIC ${DFU_DEFINITIONS})
            target_compile_definitions(${target} PUBLIC NRF_MESH_SERIAL_ENABLE)

        endfunction()

        function(dfu_module_add_pc_lint)

            add_pc_lint(${target}
                "${CMAKE_SOURCE_DIR}/examples/dfu_module/src/dfu_module.c"
                "${target_include_dirs}"
                "${${PLATFORM}_DEFINES};${${SOFTDEVICE}_DEFINES};${${BOARD}_DEFINES};-DNRF_MESH_SERIAL_ENABLE=1")

        endfunction()

    else ()

        set(DFU_MODULE_FILES
            "${CMAKE_SOURCE_DIR}/examples/dfu_module/src/dfu_module.c"
            ${DFU_MODULE_MESH_FILES})

        function(dfu_module_target_compile_definitions)

            target_compile_definitions(${target} PUBLIC ${DFU_DEFINITIONS})

        endfunction()

        function(dfu_module_add_pc_lint)

            add_pc_lint(${target}
                "${CMAKE_SOURCE_DIR}/examples/dfu_module/src/dfu_module.c"
                "${target_include_dirs}"
                "${${PLATFORM}_DEFINES};${${SOFTDEVICE}_DEFINES};${${BOARD}_DEFINES};-DNRF_MESH_SERIAL_ENABLE=0")

        endfunction()

    endif()

else ()

endif ()
