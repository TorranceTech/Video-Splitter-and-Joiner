import argparse
import os
import numpy as np
from moviepy.editor import concatenate_videoclips, VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from PIL import Image
from colorama import Fore, Style

print(r"""
__     ___     _           ____        _ _ _   
\ \   / (_) __| | ___  ___/ ___| _ __ | (_) |_ 
 \ \ / /| |/ _` |/ _ \/ _ \___ \| '_ \| | | __|
  \ V / | | (_| |  __/ (_) |__) | |_) | | | |_ 
   \_/  |_|\__,_|\___|\___/____/| .__/|_|_|\__|
                                |_|
""")

def resizer(pic, newsize):
    pilim = Image.fromarray(pic)
    return np.array(pilim.resize(newsize, Image.LANCZOS))

def split_video(video_file_path, interval, output_dir, ratio):
    clip = VideoFileClip(video_file_path)
    duration = clip.duration

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    os.environ['MOVIEPY_TEMP_FOLDER'] = output_dir  # Set the environment variable here

    start_time = 0
    end_time = interval

    i = 1
    while start_time < duration:
        output_file_path = os.path.join(output_dir, f"split_video_{i}.mp4")
        clip_sub = clip.subclip(start_time, min(end_time, duration))
        clip_resized = clip_sub.fl_image(lambda image: resizer(image, ratio))
        clip_resized.write_videofile(output_file_path)
        
        start_time += interval
        end_time += interval
        i += 1

def join_videos(input_dir):
    clips = []

    files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    files.sort(key=lambda f: int(f.split('_')[-1].split('.')[0]))

    for file in files:
        if file.endswith(".mp4"):
            video_path = os.path.join(input_dir, file)
            clip = VideoFileClip(video_path)
            clips.append(clip)

    final_clip = concatenate_videoclips(clips)

    # Create a new directory for the final video on the desktop
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    final_video_dir = os.path.join(desktop, "final_video")
    if not os.path.exists(final_video_dir):
        os.makedirs(final_video_dir)

    output_file_path = os.path.join(final_video_dir, "final_video.mp4")
    final_clip.write_videofile(output_file_path, codec='libx264')

    print(f"{Fore.GREEN}Videos successfully concatenated. The final video was saved in {output_file_path}{Style.RESET_ALL}")

def menu():
    print(f"{Fore.YELLOW}1. Change video format")
    print("2. Change time interval")
    print("3. Change output directory")
    print("4. Change video ratio")
    print("5. Split video")
    print("6. Join videos")
    print(f"7. Exit{Style.RESET_ALL}")
    return input("Choose an option: ")


def main():
    parser = argparse.ArgumentParser(description='Divides a video into parts.')
    parser.add_argument('-i', '--input', help='Path of the input video', required=False)
    parser.add_argument('-o', '--output', help='Path of the output video', required=False)
    parser.add_argument('-s', '--start', help='Start time to split the video', required=False)
    parser.add_argument('-e', '--end', help='End time to split the video', required=False)
    parser.add_argument('-r', '--ratio', help='Ratio of the video', required=False)
    parser.add_argument('-j', '--join', help='Directory that contains the videos to be joined', required=False)
    parser.add_argument('-f', '--format', help='Video format', required=False)
    parser.add_argument('-t', '--interval', help='Time interval', required=False)

    args = parser.parse_args()

    if args.input and args.output and args.start and args.end and args.ratio:
        split_video(args.input, int(args.start), args.output, tuple(map(int, args.ratio.split(':'))))

    if args.join:
        join_videos(args.join)

    if not any(vars(args).values()):
        interval = 10
        format = ".mp4"
        output_dir = "split_videos"
        ratio = (1080, 1920)

        while True:
            option = menu()
            if option == "1":
                format = input("Enter the new video format (for example, .avi, .mov): ")
            elif option == "2":
                interval = int(input("Enter the new time interval (in seconds): "))
            elif option == "3":
                output_dir = input("Enter the new output directory: ")
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                os.environ['MOVIEPY_TEMP_FOLDER'] = output_dir
            elif option == "4":
                print("Examples of video ratios:")
                print("TikTok: 9:16")
                print("YouTube: 16:9")
                print("Instagram (square): 1:1")
                ratio_input = input("Enter the desired ratio for the video (for example, 9:16, TikTok): ")
                if ratio_input.lower() == "tiktok":
                    ratio = (1080, 1920)
                elif ratio_input.lower() == "youtube":
                    ratio = (1920, 1080)
                elif ratio_input.lower() == "instagram":
                    ratio = (1080, 1080)
                else:
                    width, height = map(int, ratio_input.split(':'))
                    ratio = (width, height)
            elif option == "5":
                video_file_path = input("Enter the full path or Drag and Drop the video: ")
                split_video(video_file_path, interval, output_dir, ratio)
            elif option == "6":
                input_dir = input("Enter the directory that contains the videos to be joined: ")
                join_videos(input_dir)
            elif option == "7":
                break
            else:
                print(f"{Fore.RED}Invalid option. Try again.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
