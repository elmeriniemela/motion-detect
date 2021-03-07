import cv2 as cv
from datetime import datetime

def capture(camera, width, height):
    cap = cv.VideoCapture(camera)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)
    # Define the codec and create VideoWriter object
    stillImage = None
    frame_count = 0
    write_frames = 0
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            frame_count += 1
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break

            # Convert color image to gray_scale image
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            gray = cv.GaussianBlur(gray, (21, 21), 0)
            if stillImage is None or frame_count > 100:
                stillImage = gray
                frame_count = 0
                continue
            # Still Image and current image.
            diff_frame = cv.absdiff(stillImage, gray)

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
                write_frames = 30
                (x, y, w, h) = cv.boundingRect(contour)
                cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                break
            if write_frames:
                cv.imwrite(f'imgs/{datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f.png")}', frame)
                write_frames -= 1
            cv.imshow('frame', frame)
            if cv.waitKey(1) == ord('q'):
                break
    except KeyboardInterrupt:
        pass
    # Release everything if job is finished
    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    import sys
    capture(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))