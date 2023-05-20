import cv2

CAMERA_ID = '/dev/video0'

cap = cv2.VideoCapture(CAMERA_ID, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

with open('../YOLOv4-tiny/For-CPU/obj.names', 'r') as f:
    classes = f.read().splitlines()

net = cv2.dnn.readNetFromDarknet('../YOLOv4-tiny/For-CPU/yolo.cfg', '../YOLOv4-tiny/For-CPU/yolo_best.weights')

model = cv2.dnn_DetectionModel(net)
model.setInputParams(scale=1 / 255, size=(416, 416), swapRB=True)

last_err = 0

while True:
    ret, frame = cap.read()
    classes, scores, boxes = model.detect(frame)
    print(classes)
    cv2.imshow('cap', frame)

    data = list(zip(classes, boxes))
    if len(data) > 0:
        traffic_light = list(filter(lambda e: e[0][0] == 0, data))

        if len(traffic_light) > 0:

            traffic_light = traffic_light[0]

            #print(traffic_light[1][1], traffic_light[1][1]+traffic_light[1][3], traffic_light[1][0], traffic_light[1][0]+traffic_light[1][2])

            traffic_light_img = frame[traffic_light[1][1]:traffic_light[1][1]+traffic_light[1][3],traffic_light[1][0]:traffic_light[1][0]+traffic_light[1][2] ]
            #traffic_light_img = cv2.cvtColor(traffic_light_img, cv2.COLOR_RGB2HSV)
            traffic_light_img_green = cv2.inRange(traffic_light_img, (255, 0, 0), (255, 255, 255))
            traffic_light_img_red = cv2.inRange(traffic_light_img, (0, 215, 215), (255, 255, 255))
            green = sum(sum(traffic_light_img_green))
            red = sum(sum(traffic_light_img_red))
            if green > red:
                print('Зелёный')
            else:
                print('Красный')
            cv2.imshow('traffic light', traffic_light_img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

