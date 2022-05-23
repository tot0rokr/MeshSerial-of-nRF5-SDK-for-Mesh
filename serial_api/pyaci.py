import sys

if sys.version_info < (3, 5):
    print(("ERROR: To use {} you need at least Python 3.5.\n" +
           "You are currently using Python {}.{}").format(sys.argv[0], *sys.version_info))
    sys.exit(1)

import logging
import IPython
import DateTime
import os
import colorama

from argparse import ArgumentParser
import traitlets.config

from aci.aci_uart import Uart
#  from aci.aci_utils import STATUS_CODE_LUT
from aci.aci_config import ApplicationConfig

#  from mesh import access
from mesh import types as mt                            # NOQA: ignore unused import
from mesh.database import MeshDB                        # NOQA: ignore unused import
#  from runtime.mesh_serial import MeshSerial
from runtime.local_mesh_serial import LocalMeshSerial

USAGE_STRING = \
    """
    {c_default}{c_text}To control your device, use {c_highlight}d[x]{c_text}, where x is the device index.
    Devices are indexed based on the order of the COM ports specified by the -d option.
    The first device, {c_highlight}d[0]{c_text}, can also be accessed using {c_highlight}device{c_text}.

    Type {c_highlight}d[x].{c_text} and hit tab to see the available methods.
""" # NOQA: Ignore long line
USAGE_STRING += colorama.Style.RESET_ALL

def start_ipython(options):
    colorama.init()
    #  comports = options.devices
    #  device_handles = list()
    #  session_handles = list()

    # Print out a mini intro to the interactive session --
    # Start with white and then magenta to keep the session white
    # (workaround for a bug in ipython)
    colors = {"c_default": colorama.Fore.WHITE + colorama.Style.BRIGHT,
              "c_highlight": colorama.Fore.YELLOW + colorama.Style.BRIGHT,
              "c_text": colorama.Fore.CYAN + colorama.Style.BRIGHT}

    print(USAGE_STRING.format(**colors))

    #  CONFIG = ApplicationConfig(
        #  header_path=os.path.join(os.path.dirname(sys.argv[0]),
                                 #  ("../nrf5_SDK_for_Mesh_v5.0.0_src/examples/serial/include/"
                                  #  + "nrf_mesh_config_app.h")))

    #  mesh = MeshSerial(options, CONFIG)

    #  for dev_com in comports:
        #  device_handles.append(mesh.create_device(Uart(port=dev_com,
                                         #  baudrate=options.baudrate,
                                         #  device_name=dev_com.split("/")[-1])))

    db = MeshDB("database/test_database.json")
    mesh = LocalMeshSerial(options, db)
    #  session_handles.append(mesh.create_session(device_handles[0], db))
    mesh_manager_handle = mesh.connect_session(0)
    #  mesh.initialize_provisioner(session_handles[0], db)
    mesh.set_provisioner(mesh_manager_handle)
    #  mesh.start_session(session_handles[0])
    mesh.start_session(mesh_manager_handle)

    # Set iPython configuration
    ipython_config = traitlets.config.get_config()
    if options.no_logfile:
        ipython_config.TerminalInteractiveShell.logstart = False
        ipython_config.InteractiveShellApp.db_log_output = False
    else:
        LOG_DIR = os.path.join(os.path.dirname(sys.argv[0]), "log")
        dt = DateTime.DateTime()
        logfile = "{}/{}-{}-{}-{}_interactive_session.log".format(
            LOG_DIR, dt.yy(), dt.dayOfYear(), dt.hour(), dt.minute())

        ipython_config.TerminalInteractiveShell.logstart = True
        ipython_config.InteractiveShellApp.db_log_output = True
        ipython_config.TerminalInteractiveShell.logfile = logfile

    ipython_config.TerminalInteractiveShell.confirm_exit = False
    ipython_config.InteractiveShellApp.multiline_history = True
    ipython_config.InteractiveShellApp.log_level = logging.DEBUG

    IPython.embed(config=ipython_config)
    # TODO: session delete
    #  for dev in device_handles:
        #  mesh.device_mgr.remove_device(dev)

    #  for ses in session_handles:
        #  mesh.session_mgr.remove_session(ses)
    del mesh

    raise SystemExit(0)


if __name__ == '__main__':
    parser = ArgumentParser(
        description="nRF5 SDK for Mesh Interactive PyACI")
    parser.add_argument("-d", "--device",
                        dest="devices",
                        nargs="+",
                        required=True,
                        help=("Device Communication port, e.g., COM216 or "
                              + "/dev/ttyACM0. You may connect to multiple "
                              + "devices. Separate devices by spaces, e.g., "
                              + "\"-d COM123 COM234\""))
    parser.add_argument("-b", "--baudrate",
                        dest="baudrate",
                        required=False,
                        default='115200',
                        help="Baud rate. Default: 115200")
    parser.add_argument("--no-logfile",
                        dest="no_logfile",
                        action="store_true",
                        required=False,
                        default=False,
                        help="Disables logging to file.")
    parser.add_argument("-l", "--log-level",
                        dest="log_level",
                        type=int,
                        required=False,
                        default=3,
                        help=("Set default logging level: "
                              + "1=Errors only, 2=Warnings, 3=Info, 4=Debug"))
    options = parser.parse_args()

    #  if options.log_level == 1:
        #  options.log_level = logging.ERROR
    #  elif options.log_level == 2:
        #  options.log_level = logging.WARNING
    #  elif options.log_level == 3:
        #  options.log_level = logging.INFO
    #  else:
        #  options.log_level = logging.DEBUG

    start_ipython(options)
