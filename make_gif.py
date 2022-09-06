import glob
from PIL import Image

def make_gif(frame_folder):
    for image in glob.glob(f"{frame_folder}/*.png"):
        print(image)

    frames = [Image.open(image) for image in glob.glob(f"{frame_folder}/***.png")]
    frame_one = frames[0]
    for foo in range(50): frames.append(frames[-1])
    
    print(f"len(frames) : {len(frames)}")

    frame_one.save("output.gif", format="GIF", append_images=frames,
               save_all=True, duration=100, loop=0)
    
if __name__ == "__main__":
    make_gif("tmp/dump")