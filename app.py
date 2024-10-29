import gradio as gr
import cv2
import numpy as np
import os
import configparser
import sys
from threading import Thread
import multiprocessing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import backend.main
from backend.tools.common_tools import is_image_file

# def remove_subtitles(video_path, subtitle_position=None):
#     # Placeholder function to simulate subtitle removal
#     # In a real implementation, this would process the video and remove subtitles
#     return f"Processed video from {video_path} with subtitle position {subtitle_position}"

# def process_video(video_file, subtitle_position):
#     # Convert subtitle_position to a tuple if provided
#     if subtitle_position:
#         subtitle_position = tuple(map(int, subtitle_position.split(',')))
#     else:
#         subtitle_position = None

#     # Call the subtitle removal function
#     result = remove_subtitles(video_file.name, subtitle_position)
#     return result

def process_video(video_path, x_slider, y_slider, width_slider, height_slider, frame_width, frame_height):
    xmin = x_slider
    xmax = x_slider + width_slider
    ymin = y_slider
    ymax = y_slider + height_slider
    if ymax > frame_height:
        ymax = frame_height
    if xmax > frame_width:
        xmax = frame_width

    subtitle_area = (ymin, ymax, xmin, xmax)

    sr = backend.main.SubtitleRemover(video_path, subtitle_area, True)
    finished_video_path = sr.run()
    return gr.Video(finished_video_path)

# Define the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("VIDEO SUBTITLE REMOVER")

    #video_path_input = gr.Textbox(label="Enter Video Path")
    submit_button = gr.Button("Submit Video File")

    frame_count = gr.Number(2000, label="frame count")
    frame_height = gr.Number(1920, label="frame height")
    frame_width = gr.Number(1080, label="frame width")



    def load_video_from_path(video_path):
        if os.path.exists(video_path):
            video_cap = cv2.VideoCapture(video_path)

            frame_count = video_cap.get(cv2.CAP_PROP_FRAME_COUNT)
            frame_height = video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            frame_width = video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            return gr.Video(value=video_path), frame_count, frame_height, frame_width, gr.Slider(maximum=frame_count), gr.Slider(maximum=frame_width), gr.Slider(maximum=frame_width), gr.Slider(maximum=frame_height), gr.Slider(maximum=frame_height)
        else:
            return gr.Video(value=None)

    def update_textbox_preview(x_slider, y_slider, width_slider, height_slider, frame_slider, video_path):
        video_cap = cv2.VideoCapture(video_path)

        video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_slider)
        ret, frame = video_cap.read()


        draw = cv2.rectangle(img=frame, pt1=(int(x_slider), int(y_slider)), pt2=(int(x_slider) + int(width_slider), int(y_slider) + int(height_slider)),
                             color=(0, 255, 0), thickness=3)

        def _img_resize(image):
            top, bottom, left, right = (0, 0, 0, 0)
            height, width = image.shape[0], image.shape[1]
            # 对长短不想等的图片，找到最长的一边
            longest_edge = height
            # 计算短边需要增加多少像素宽度使其与长边等长
            if width < longest_edge:
                dw = longest_edge - width
                left = dw // 2
                right = dw - left
            else:
                pass
            # 给图像增加边界
            constant = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0])
            return cv2.resize(constant, (360, 640))
        
        # resized_frame = _img_resize(draw)
        # 显示视频帧
        return gr.Image(value=draw)
    
    video_input = gr.Video(label="Upload Video")
    frame_slider = gr.Slider(minimum=0, maximum=10, value=0, label="Frame number")
    x_slider = gr.Slider(minimum=0, maximum=1080, value=0, label="X Position")
    y_slider = gr.Slider(minimum=0, maximum=1920, value=0, label="Y Position")
    width_slider = gr.Slider(minimum=0, maximum=1080, value=100, label="Width")
    height_slider = gr.Slider(minimum=0, maximum=1920, value=100, label="Height")
    preview_edit = gr.Image(label="Frame edit preview", value = update_textbox_preview, inputs=[x_slider, y_slider, width_slider, height_slider, frame_slider, video_input])
    run_button = gr.Button("Run")
    progress=gr.Progress()
    finished_video = gr.Video(label="Finished Video")

    submit_button.click(fn=load_video_from_path, inputs=video_input, outputs=[video_input, frame_count, frame_height, frame_width, frame_slider, x_slider, width_slider, y_slider, height_slider])



    run_button.click(fn=process_video,
      inputs=[video_input, x_slider, y_slider, width_slider, height_slider, frame_width, frame_height],
      outputs=finished_video)

demo.launch(server_port=8888)
