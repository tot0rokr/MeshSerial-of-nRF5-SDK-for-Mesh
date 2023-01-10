# DFU Nordic Firmware

## Version

- dfu_v0.0: Nordic에서 개발
- dfu_v1.0: v0.0보다 안정성을 10x 개선
- dfu_v1.1: dfu 실패 fwid 전송 및 릴레이
- dfu_v1.2: 서로 다른 firmware 간의 dfu 실패 릴레이

## Usage

[자세한 설명은 이곳을 보세요][문서]

[문서]: https://neostack.atlassian.net/wiki/spaces/MES/pages/121634846?atlOrigin=eyJpIjoiODIyZDExMDIzYTc4NDJhODljY2YyMGU4YzY0ODA3YjgiLCJwIjoiYyJ9

### Example

```shell
cd ~
git clone https://github.com/tot0rokr/MeshSerial-of-nRF5-SDK-for-Mesh.git dfu
cd ~/dfu
cmake -G Ninja \
    -DTOOLCHAIN=gccarmemb \
    -DPLATFORM=nrf52840_xxAA \
    -DBOARD=pca10056 \
    -DSOFTDEVICE=s140_7.2.0 \
    -DBUILD_BOOTLOADER=ON \
    ../nrf5_SDK_for_Mesh_v5.0.0_src/                                        # 펌웨어 빌드환경 빌드
#-------------------------------------------------------------------------- 빌드 환경 세팅 (처음 한 번만 수행)

ninja mesh/bootloader/mesh_bootloader_serial_gccarmemb_nrf52840_xxAA.hex  # bootloader 빌드
ninja dfu_nrf52840_xxAA_s140_7.2.0                                        # application 빌드
#-------------------------------------------------------------------------- 펌웨어 빌드 (펌웨어 변경될 때)

docker run -itd --privileged \
    -v ~/dfu:/dfu \
    -v /dev:/dev \
    --name nrfutil \
    tot0ro/nrfutil                                                          # nrfutil(python2) 실행을 위한 docker
#-------------------------------------------------------------------------- dfu 작업을 위한 도커 실행

cd ~/dfu/dfu
docker exec nrfutil /bin/bash /dfu/dfu/commands.sh config 10000           # bootloader config 생성. 인자는 company id
docker exec nrfutil /bin/bash /dfu/dfu/commands.sh genkey                 # 암호키 생성
./commands.sh version 2                                                   # application version 설정
docker exec nrfutil /bin/bash /dfu/dfu/commands.sh device_page            # device page 생성
#-------------------------------------------------------------------------- dfu 설정

./commands.sh gather_hex                                                  # application, bootloader, softdevice를 가져옴
sudo ./commands.sh download                                               # 펌웨어 다운로드 (옵션은 아래를 참고)
sudo ./commands.sh verify 683241207 "/dev/ttyACM2"                        # 다운로드 펌웨어 검증. (옵션은 아래를 참고)
#-------------------------------------------------------------------------- dfu 펌웨어 다운로드

docker exec nrfutil /bin/bash /dfu/dfu/commands.sh dfu_archive \          # dfu 바이너리 생성.  (옵션은 아래를 참고)
    -a /dfu/dfu/application.hex 3 \                                         # 새로운 펌웨어 application version 및 hex파일 설정
    /dfu/dfu/dfu3.zip                                                       # output
docker exec -it nrfutil /bin/bash /dfu/dfu/commands.sh dfu \              # dfu 전송 (옵션은 아래를 참고)
    /dfu/dfu/dfu3.zip \                                                     # 바이너리
    /dev/ttyACM2 \                                                          # serial COM port
    60                                                                      # 전송 속도
#-------------------------------------------------------------------------- dfu 전송
```
