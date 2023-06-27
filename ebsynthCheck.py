import os
import tkinter as tk
from sys import byteorder
from tkinter import filedialog
import struct
import subprocess


def read_project(proj_filename):
    proj_path = os.path.join(proj_filename + ".ebs")
    
    with open(proj_path, 'rb') as f:
        # Skip the header
        f.seek(6)
        
        # Read the video path
        video_path_len = int.from_bytes(f.read(4), byteorder='little')
        video_path = f.read(video_path_len).decode('utf-8', errors='replace')
        
        # Read the mask path
        mask_path_len = int.from_bytes(f.read(4), byteorder='little')
        mask_path = f.read(mask_path_len).decode('utf-8', errors='replace')
        
        # Read the key path
        key_path_len = int.from_bytes(f.read(4), byteorder='little')
        key_path = f.read(key_path_len).decode('utf-8', errors='replace')
        
        # Skip the mask on flag
        f.seek(1, os.SEEK_CUR)
        
        # Skip the weights and mappings
        f.seek(20, os.SEEK_CUR)
        
        # Read the number of synths
        f.seek(4, os.SEEK_CUR)  # Skip the num_synths field for now
        num_synths = int.from_bytes(f.read(4), byteorder='little')
        #print("num_synths:", num_synths)
        #return
        # Read the synth paths
        synth_paths = []
        for _ in range(num_synths):
            # Read key frame
            key = int.from_bytes(f.read(4), byteorder='little')
            
            # Skip is start frame exist and is end frame exist
            f.seek(2, os.SEEK_CUR)
            
            # Read start frame
            prev_key = int.from_bytes(f.read(4), byteorder='little')
            
            # Read end frame
            next_key = int.from_bytes(f.read(4), byteorder='little')
            
            # Read out path
            out_path_len = int.from_bytes(f.read(4), byteorder='little')
            out_path = f.read(out_path_len).decode('utf-8', errors='replace')
            #print("out_path:", out_path)
            synth = {
                "key": key,
                "prev_key": prev_key,
                "next_key": next_key,
                "out_path": out_path
            }
            synth_paths.append(synth)
            
        
        return video_path, mask_path, key_path, synth_paths


#terminate all EbSynth progress
print("Terminate all EbSynth progress")
subprocess.call(["taskkill", "/F", "/IM", "EbSynth.exe"])
print("Open file dialog to choose the project root")
# Open file dialog to choose a folder
root = tk.Tk()
root.withdraw()
folder_path = filedialog.askdirectory()

if not os.path.isdir(folder_path):
    print("no folder selected")
    exit()
# Check all .ebs files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".ebs"):
        file_path = os.path.join(folder_path, filename)
        video_path, mask_path, key_path, synth_paths = read_project(file_path[:-4]) or ("", "", "", [])
        print("check synth_paths:", filename)
        # Check if synth_paths is empty
        if not synth_paths:
            print("Missing synth_paths:", filename," .ebs file corrupt")
        else:
            for synth in synth_paths:
                key_frame = synth["key"]
                prev_key = synth["prev_key"]
                next_key = synth["next_key"]
                out_path = synth["out_path"]
                out_path = out_path.replace("/[#####].png", "")
                synth_folder = os.path.join(folder_path, out_path)
                exists = os.path.isdir(synth_folder)
                file_not_exist = False;
                if not exists:
                    print("Missing Path in ",filename," -> re-open .ebs file")
                    os.startfile(file_path)
                    break
                else:
                    for frame_num in range(int(prev_key), int(next_key) + 1):
                        png_file = os.path.join(synth_folder, str(frame_num).zfill(5) + ".png")
                        
                        # Check if png_file exists
                        if not os.path.exists(png_file):
                            print("Missing png_file:", png_file," -> re-open .ebs file")
                            file_not_exist = True
                            break
                    if file_not_exist:
                        os.startfile(file_path)
                        break
        print("Passed")

print("done")
