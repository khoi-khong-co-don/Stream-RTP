# import time
# from PIL import Image
# import subprocess as sp
# import io
# import cv2
# import ffmpeg
# import numpy


# class VideoStream:
#     def __init__(self, rtsp_url):
#         # self.rtsp_url = rtsp_url
#         # self.cap = cv2.VideoCapture(rtsp_url)
#         # self.proc = (
#         #     ffmpeg.input(rtsp_url, {"rtsp_transport": "tcp"})
#         #     .output('pipe:', format='rawvideo', pix_fmt='rgb24')
#         #     .overwrite_output()
#         #     .run_async(pipe_stdout=True)
#         # )
#         self.frameNum = 0
#         command = [
#             'ffmpeg',
#             '-i', 'rtsp://admin:Oryza@123@192.168.111.6:5546/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif',
#             '-f', 'image2pipe',
#             '-pix_fmt', 'rgb24',
#             '-vcodec', 'rawvideo', '-',
#             '-preset', 'veryslow',
#             '-crf', '18',
#             '-vf', 'scale=640:480',
#         ]

#         self.pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10**8)

#     # def nextFrame(self):
#     #     in_bytes = self.process1.stdout.read(self.width * self.height * 3)

#     #     if in_bytes:
#     #         return Image.frombytes(
#     #             'RGB',
#     #             (self.width, self.height),
#     #             in_bytes,
#     #             'raw',
#     #             'RGB',
#     #             )
           

#     def nextFrame(self, jpeg_quality=80):
#         raw_image = self.pipe.stdout.read(640*480*3)
#     # print(f"Size of raw_image: {len(raw_image)} bytes")
#         image = numpy.fromstring(raw_image, dtype='uint8')
#         image = image.reshape((480,640,3))

#         _, image_bytes = cv2.imencode('.jpg', image)
#         return image_bytes.tobytes()


#     def frameNbr(self):
#         """Get frame number."""
#         return self.frameNum
    


# if __name__ == "__main__":
#     # Create a VideoStream object and call nextFrame method to get the frame  
#     # data from the camera
#     vs = VideoStream('rtsp://admin:Oryza@123@192.168.111.6:5546/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')
#     vs.nextFrame()


import time
from PIL import Image
import io
import cv2

class VideoStream:
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.cap = cv2.VideoCapture(rtsp_url)
        if self.cap.isOpened():
            print("Kết nối RTSP đã mở thành công.")
        else:
            print("Không thể mở kết nối RTSP. Kiểm tra đường dẫn và trạng thái camera.")
        # self.proc = (
        #     ffmpeg.input(rtsp_url, f='rtsp')
        #     .output('pipe:', format='rawvideo', pix_fmt='rgb24')
        #     .run_async(pipe_stdout=True)
        # )
        self.frameNum = 0

    # def nextFrame(self):
    #     data = self.proc.stdout.read(5)  # Đọc 5 byte đầu tiên để xác định độ dài của frame
    #     converted_data = bytes([int(byte) - 0x30 for byte in data])
    #     if data:
    #         data = bytearray(converted_data)
    #         data_int = (data[0] - 48) * 10000 + (data[1] - 48) * 1000 + (data[2] - 48) * 100 + (data[3] - 48) * 10 + (data[4] - 48)
    #         framelength = data_int

    #         # Đọc frame có độ dài đã xác định
    #         frame = self.proc.stdout.read(framelength)
    #         if len(frame) != framelength:
    #             raise ValueError('Dữ liệu khung không hoàn chỉnh')

    #         self.frameNum += 1
    #         print('-' * 10 + f'\nKhung tiếp theo (#{self.frameNum}) độ dài: {framelength}\n' + '-' * 10)
    #         image = Image.open(io.BytesIO(frame))
    #         png_data = io.BytesIO()
    #         image.save(png_data, format='PNG')
    #         png_data = png_data.getvalue()
    #         # Trả về dữ liệu frame dưới dạng hình ảnh PNG
    #         return png_data

    def nextFrame(self, jpeg_quality=80):
        ret, frame = self.cap.read()
        
        if ret:
            # print('-' * 10 + f'\nKhung tiếp theo (#{self.frameNum})\n' + '-' * 10)
            # frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            # Chuyển frame thành dạng hình ảnh JPEG và sau đó thành dạng bytes
            encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
            success, jpeg_data = cv2.imencode('.jpg', frame, encode_params)
            if success:
                return jpeg_data.tobytes()
        return None


    def frameNbr(self):
        """Get frame number."""
        return self.frameNum
    


# if __name__ == "__main__":
#     # Create a VideoStream object and call nextFrame method to get the frame  
#     # data from the camera
#     vs = VideoStream('rtsp://admin:Oryza@123@192.168.111.6:5546/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')
#     vs.nextFrame()