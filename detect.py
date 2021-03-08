
import cv2 as cv
from datetime import datetime
import os

class Camera:
    def __init__(self, video, width, height, storage_dir, display):
        self.video = video
        self.width = width
        self.height = height
        self.storage_dir = storage_dir
        self.display = display

        self.still_image = None
        self.frame_count = 0
        self.write_frames = 0


    def detect_movement(self, frame):
        # Convert color image to gray_scale image
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        gray = cv.GaussianBlur(gray, (21, 21), 0)
        if self.still_image is None or self.frame_count > 100:
            self.still_image = gray
            self.frame_count = 0
            return False
        # Still Image and current image.
        diff_frame = cv.absdiff(self.still_image, gray)

        # change the image to white if static background and current frame is greater than 25.
        thresh_frame = cv.threshold(diff_frame, 25, 255, cv.THRESH_BINARY)[1]
        thresh_frame = cv.dilate(thresh_frame, None, iterations=3)
        # Finding contour and hierarchy from a moving object.
        contours,hierachy = cv.findContours(thresh_frame.copy(),
            cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv.contourArea(contour)
            if area < 10000:
                continue
            self.write_frames = 30
            (x, y, w, h) = cv.boundingRect(contour)
            cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            return True

        return False

    def save(self, frame):
        cv.imwrite(os.path.join(self.storage_dir, datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f.png")), frame)
        self.write_frames -= 1

    def display_frame(self, frame):
        cv.imshow('frame', frame)
        if cv.waitKey(1) == ord('q'):
            raise KeyboardInterrupt

    def run(self):
        cap = cv.VideoCapture(self.video)
        cap.set(cv.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, self.height)
        # Define the codec and create VideoWriter object

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                self.frame_count += 1
                if not ret:
                    print("Can't receive frame (stream end?). Exiting ...")
                    break

                if not self.write_frames:
                    self.detect_movement(frame)

                if self.write_frames:
                    self.save(frame)

                if self.display:
                    self.display_frame(frame)

        except KeyboardInterrupt:
            pass
        # Release everything if job is finished
        cap.release()
        cv.destroyAllWindows()

if __name__ == "__main__":
    import argparse
    import pathlib

    parser = argparse.ArgumentParser(description='Detect motion')
    parser.add_argument(
        '--video',
        type=int,
        dest='video',
        help='video number /dev/video<number>',
        required=True,
    )

    parser.add_argument(
        '--width',
        type=int,
        dest='width',
        required=True,
    )

    parser.add_argument(
        '--height',
        type=int,
        dest='height',
        required=True,
    )

    parser.add_argument(
        '--storage-dir',
        type=pathlib.Path,
        dest='storage_dir',
        required=True,
    )

    parser.add_argument(
        '--display',
        type=bool,
        dest='display',
    )

    args = parser.parse_args()
    cam = Camera(
        video=args.video,
        width=args.width,
        height=args.height,
        storage_dir=args.storage_dir,
        display=args.display,
    )
    cam.run()