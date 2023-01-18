if (NOT BUILD_HOST)
    set(DFU_MODULE "off" CACHE STRING "DFU module used for updating on-the-air")
    set_property(CACHE DFU_MODULE PROPERTY STRINGS
        "off" "on" "serial")
    string(TOLOWER ${DFU_MODULE} DFU_MODULE)
    message(STATUS "DFU: ${DFU_MODULE}")
else ()
    set(DFU_MODULE "off" CACHE STRING "DFU module can not used for host build" FORCE)
endif ()
