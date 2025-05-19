#!/usr/bin/env python3

import sys
import subprocess, serial, time, os, sys, glob
 
# helper to run a command or bail

def run_cmd(cmd, err_msg):

    try:

        subprocess.run(cmd, check=True)

    except subprocess.CalledProcessError:

        print(f"ERROR: {err_msg}")

        sys.exit(1)
 
find_cli_root = r"C:\NXP\S32DS.3.5\S32DS\tools\S32FlashTool"
 
def pick_file(pattern, descr):

    """Glob for pattern, ensure exactly one match, return it."""

    matches = glob.glob(pattern)

    if len(matches) != 1:

        print(f"ERROR: expected one {descr}, found {len(matches)}: {pattern}")

        sys.exit(1)

    return matches[0]
 
def main():

    # ── CONFIG: adjust these three paths to your layout ─────────────────────────

    # flash_tool_root = find_cli_root()

    bin_dir       = r"D:\Jenkins\Flashing\f4.2"      # location of .bin/.sdcard files 

    # usb_mount     = "/mnt/usb"                          # where you mount the USB stick

    # ─────────────────────────────────────────────────────────────────────────────
 
    port          = "COM7"

    target_bin    = os.path.join(find_cli_root, "targets", "S32G3xxx.bin")

    alg_nor_bin   = os.path.join(find_cli_root, "flash",    "MX25UW51245G.bin")

    alg_emmc_bin  = os.path.join(find_cli_root, "flash",    "EMMC.bin")
 
    # pick the exact filenames from your bin_dir

    bootloader        = pick_file(os.path.join(bin_dir, "Bootloader_core_minimal.bin"),       "bootloader")

    fip_core          = pick_file(os.path.join(bin_dir, "fip_core.s32-sdcard"),  "FIP core")

    minimal_img       = pick_file(os.path.join(bin_dir, "core-image-minimal-s32g399acgm-20240912181032.rootfs.sdcard"), "minimal image")

    # full_rootfs_img   = pick_file(os.path.join(bin_dir, "ros-image-core-foxy-*.sdcard"),   "full rootfs")

    delivered_bootloader   = pick_file(os.path.join(bin_dir, "F5_Bootloader.bin"),  "delivered_bootloader")

    mcore_app         = pick_file(os.path.join(bin_dir, "f5_Mcore.bin"),       "M-core app")

    acore_fip         = pick_file(os.path.join(bin_dir, "bl2_w_dtb.s32-sdcard"),  "A-core FIP")
 
    def nor_erase():

        run_cmd([

            "S32FlashTool", "-t", target_bin,

            "-i", "uart", "-p", port,

            "-a", alg_nor_bin,

            "-ferase", "-addr", "0x0", "-size", "0xb90000"

        ], "NOR erase failed")
 
    def nor_program(file, addr):

        run_cmd([

            "S32FlashTool", "-t", target_bin,

            "-i", "uart", "-p", port,

            "-a", alg_nor_bin,

            "-fprogram", "-f", file,

            "-addr", addr

        ], f"NOR program {file} failed")

        print(f"SUCCESS: NOR programmed {os.path.basename(file)} at {addr}")
 
    def emmc_erase():

        run_cmd([

            "S32FlashTool", "-t", target_bin,

            "-i", "uart", "-p", port,

            "-a", alg_emmc_bin,

            "-ferase", "-addr", "0x0", "-size", "0xb9000000"

        ], "eMMC erase failed")
        
        print(f"SUCCESS: EMMC erased {os.path.basename(alg_emmc_bin)}")

 
    def emmc_program(file, addr):

        run_cmd([

            "S32FlashTool", "-t", target_bin,

            "-i", "uart", "-p", port,

            "-a", alg_emmc_bin,

            "-fprogram", "-f", file,

            "-addr", addr

        ], f"eMMC program {file} failed")

        print(f"SUCCESS: EMMC programmed {os.path.basename(file)} at {addr}")
 
    # ── Execute the flow ─────────────────────────────────────────────────────────

    nor_erase()

    nor_program(bootloader,      "0x0")

    nor_program(fip_core,        "0x600000")

    input("\n⏸ Please perform a POWER-ON RESET on the board, then press ENTER to continue…")
 
    emmc_erase()

    emmc_program(minimal_img,    "0x0")

    input("\n⏸ Please toggle the SW5 and perform POWER-ON RESET on the board then press ENTER to continue...")

    print("\nROS Flashing through MobaXterm under progress...")

    MOBAXTERM = r"C:\Program Files (x86)\Mobatek\MobaXterm\MobaXterm.exe"
    
    # launch the saved COM7 serial session

    subprocess.Popen([

        MOBAXTERM,

        "-bookmark", "COM7"       # open that saved session

    ])

    input("\n⏸ After ROS image flash, press Enter to continue...")

    input("\n⏸ Power OFF the board, Toggle SW5, Close MiniCom, Power ON the board, then press Enter to continue...")

    nor_erase()

    nor_program(delivered_bootloader,      "0x0")

    nor_program(mcore_app,        "0x50000")

    nor_program(acore_fip,        "0x600000")

    input("\n⏸ Power OFF the board, Toggle SW5, Power ON the board then press Enter to continue...")


    MOBAXTERM = r"C:\Program Files (x86)\Mobatek\MobaXterm\MobaXterm.exe"
    
    # launch the saved COM7 serial session

    subprocess.Popen([

        MOBAXTERM,

        "-bookmark", "COM7"        # open that saved session

    ])
 
    print("All done — please reboot and verify.")
 
if __name__ == "__main__":

    main()

 
