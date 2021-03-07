import cv2 as cv

def capture(camera, width, height):
    cap = cv.VideoCapture(camera)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)
    # Define the codec and create VideoWriter object
    fourcc = cv.VideoWriter_fourcc(*'XVID')
    out = cv.VideoWriter('output.avi', fourcc, 20.0, (width,  height))
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            out.write(frame)
            cv.imshow('frame', frame)
            if cv.waitKey(1) == ord('q'):
                break
    except KeyboardInterrupt:
        pass
    # Release everything if job is finished
    cap.release()
    out.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    import sys
    capture(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))