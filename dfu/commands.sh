#!/bin/bash


FILE_PATH=`dirname "$0"`

echo $FILE_PATH
echo $0


if [ $# -lt 1 ]; then
    echo "$0 [device_page|genkey|version|dfu_archive|verify|download|dfu]"
    exit 1
fi

python_version=$(python --version 2>&1 | awk '{print $2}' | sed 's/\.[0-9]*$//g')

echo "python: $python_version, operator: $1"

if [ "$1" == "config" ]; then
    if [ $# -lt 2 ]; then
        echo "$0 $1 <company id>"
        exit 1
    fi
    if [ -e "$FILE_PATH/tools_dfu/bootloader_config.json" ]; then
        rm "$FILE_PATH/tools_dfu/bootloader_config.json"
    fi
    cp "$FILE_PATH/tools_dfu/bootloader_config_default.json" "$FILE_PATH/tools_dfu/bootloader_config.json"
    $(python -c "import json; file = open('$FILE_PATH/tools_dfu/bootloader_config.json'); jsonString = json.load(file); jsonString['bootloader_config']['company_id'] = $2; file2 = open('$FILE_PATH/tools_dfu/bootloader_config.json', 'w'); json.dump(jsonString, file2)")
fi

if [ "$1" == "device_page" ]; then
    if [ "$python_version" != "2.7" ]; then
        echo "Need python >= 2.7"
        exit 1
    fi
	python "$FILE_PATH/tools_dfu/device_page_generator.py" -c "$FILE_PATH/tools_dfu/bootloader_config.json" -d nrf52840_xxAA -sd "s140_7.2.0" -o "$FILE_PATH/devicepage.hex"
fi

if [ "$1" == "gather_hex" ]; then
    cp -f "$FILE_PATH/../build/mesh/bootloader/mesh_bootloader_serial_gccarmemb_nrf52840_xxAA.hex" "$FILE_PATH/bootloader.hex"
    cp -f "$FILE_PATH/../build/examples/dfu/dfu_nrf52840_xxAA_s140_7.2.0.hex" "$FILE_PATH/application.hex"
    cp -f "$FILE_PATH/../nrf5_SDK_for_Mesh_v5.0.0_src/bin/softdevice/s140_nrf52_7.2.0_softdevice.hex" "$FILE_PATH/softdevice.hex"
fi

if [ "$1" == "genkey" ]; then
    if [ "$python_version" != "2.7" ]; then
        echo "Need python >= 2.7"
        exit 1
    fi
    if [ -e "$FILE_PATH/private_key.txt" ]; then
        rm "$FILE_PATH/private_key.txt"
    fi
    nrfutil keys --gen-key "$FILE_PATH/private_key.txt"
    key=$(nrfutil keys --show-vk hex "$FILE_PATH/private_key.txt" | awk -F ":" '{print $2}' | xargs echo | sed 's/ //g')
    $(python -c "import json; file = open('$FILE_PATH/tools_dfu/bootloader_config.json'); jsonString = json.load(file); jsonString['bootloader_config']['public_key'] = \"$key\"; file2 = open('$FILE_PATH/tools_dfu/bootloader_config.json', 'w'); json.dump(jsonString, file2)")
fi

if [ "$1" == "version" ]; then
    re='^[0-9]+$'
    if ! [[ "$2" =~ $re ]]; then
        exit 1
    fi
    if [ $# -lt 2 ]; then
        echo "$0 version <version>"
        exit 1
    fi
    $(python -c "import json; file = open('$FILE_PATH/tools_dfu/bootloader_config.json'); jsonString = json.load(file); jsonString['bootloader_config']['application_version'] = $2; file2 = open('$FILE_PATH/tools_dfu/bootloader_config.json', 'w'); json.dump(jsonString, file2)")
fi

if [ "$1" == "dfu_archive" ]; then
    if [ "$python_version" != "2.7" ]; then
        echo "Need python >= 2.7"
        exit 1
    fi
    if [ $# -lt 4 ]; then
        echo "Too few arguments"
        exit 1
    fi
    shift 1

    company_id=$(python -c "import json; file = open('$FILE_PATH/tools_dfu/bootloader_config.json'); jsonString = json.load(file); print(jsonString['bootloader_config']['company_id'])")

    cmd="nrfutil dfu genpkg --company-id $company_id --key-file $FILE_PATH/private_key.txt --sd-req 0x0100 --mesh"

    while [ $# -gt 0 ]; do
        case ${1} in
            "-s"|"--softdevice")
                cmd="$cmd --softdevice $2"
                shift 2
                ;;
            "-b"|"--bootloader")
                re='^(0x)?[0-9A-Fa-f]+$'
                if ! [[ "$3" =~ $re ]]; then
                    echo "bootloader id should be a number."
                    exit 1
                fi
                cmd="$cmd --bootloader $2 --bootloader-id $3"
                shift 3
                ;;
            "-a"|"--application")
                re='^(0x)?[0-9A-Fa-f]+$'
                if ! [[ "$3" =~ $re ]]; then
                    echo "application version should be a number."
                    exit 1
                fi
                cmd="$cmd --application $2 --application-id 1 --application-version $3"
                shift 3
                ;;
            *)
                cmd="$cmd $1"
                shift 1
        esac
    done

    echo "$cmd"

    $cmd
fi

if [ "$1" == "verify" ]; then
    if [ "$python_version" == "2.7" ]; then
        echo "Need python >= 3"
        exit 1
    fi
    if [ $# -lt 3 ]; then
        echo "$0 verify <serial number> <COM port>"
        exit 1
    fi
    python3 "$FILE_PATH/tools_dfu/bootloader_verify.py" "$2" "$3"
fi

if [ "$1" == "download" ]; then
    if [ "$python_version" == "2.7" ]; then
        echo "Need python >= 3"
        exit 1
    fi
    softdevice="$FILE_PATH/softdevice.hex"
    bootloader="$FILE_PATH/bootloader.hex"
    application="$FILE_PATH/application.hex"
    devicepage="$FILE_PATH/devicepage.hex"
    options=""
    shift 1

    while [ $# -gt 0 ]; do
        case ${1} in
            "-s"|"--softdevice")
                softdevice="$2"
                shift 2
                ;;
            "-b"|"--bootloader")
                bootloader="$2"
                shift 2
                ;;
            "-a"|"--application")
                application="$2"
                shift 2
                ;;
            "-d"|"--devicepage")
                devicepage="$2"
                shift 2
                ;;
            "--snr")
                options="$options --snr $2"
                shift 2
                ;;
            "--log")
                options="$options --log"
                shift 1
                ;;
            *)
                echo "Unknown arguments"
                exit 1
        esac
    done
    mergehex -m $softdevice $bootloader $application $devicepage -o "$FILE_PATH/out.hex"
    nrfjprog --program "$FILE_PATH/out.hex" --chiperase --verify --reset $options
    # nrfjprog --chiperase $options
    # nrfjprog --program $softdevice --verify $options
    # nrfjprog --program $bootloader --verify $options
    # nrfjprog --program $application --verify $options
    # nrfjprog --program $devicepage --verify $options
    # nrfjprog --reset $options
fi

if [ "$1" == "dfu" ]; then
    if [ "$python_version" != "2.7" ]; then
        echo "Need python >= 2.7"
        exit 1
    fi
    interval=200
    if [ $# -ge 4 ]; then
        interval=$4
    elif [ $# -lt 3 ]; then
        echo "$0 dfu <output> <COM port> [<interval ms>] [-v]"
        exit 1
    fi
    if [ $# -eq 5 ] && [ $5 == "-v" ]; then
        nrfutil --verbose dfu serial -pkg $2 -p $3 -b 115200 -fc --mesh -i "$interval"
    else
        nrfutil dfu serial -pkg $2 -p $3 -b 115200 -fc --mesh -i "$interval"
    fi
fi
