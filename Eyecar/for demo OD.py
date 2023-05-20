import cv2

with open('../YOLOv4-tiny/For-CPU/obj.names', 'r') as f:
    classes = f.read().splitlines()

net = cv2.dnn.readNetFromDarknet('../YOLOv4-tiny/For-CPU/yolo.cfg', '../YOLOv4-tiny/For-CPU/yolo_best.weights')

model = cv2.dnn_DetectionModel(net)
model.setInputParams(scale=1 / 255, size=(416, 416), swapRB=True)

last_err = 0

frame = cv2.imread('Signs/2.jpg')

classes, scores, boxes = model.detect(frame)
print(classes)
data = list(zip(classes, boxes))

cv2.imshow('frame', frame)

for i, fr in enumerate(data):

    if i % 2 == 0:

        image = frame[fr[1][1]:fr[1][1]+fr[1][3],fr[1][0]:fr[1][0]+fr[1][2]]
        cv2.imshow(str(i), image)
cv2.waitKey(0)
cv2.destroyAllWindows()


# if len(data) > 0:
#
#     traffic_light = list(filter(lambda e: e[0] == 0, data))
#
#     if len(traffic_light) > 0:
#
#         traffic_light = traffic_light[0]
#
#         #print(traffic_light[1][1], traffic_light[1][1]+traffic_light[1][3], traffic_light[1][0], traffic_light[1][0]+traffic_light[1][2])
#
#         traffic_light_img = frame[traffic_light[1][1]:traffic_light[1][1]+traffic_light[1][3],traffic_light[1][0]:traffic_light[1][0]+traffic_light[1][2]]
#
#         #traffic_light_img = cv2.cvtColor(traffic_light_img, cv2.COLOR_RGB2HSV)
#         traffic_light_img_green = cv2.inRange(traffic_light_img, (200, 140, 0), (240, 210, 10))
#         traffic_light_img_red = cv2.inRange(traffic_light_img, (81, 125, 220), (189, 255, 250))
#         green = sum(sum(traffic_light_img_green))
#         red = sum(sum(traffic_light_img_red))
#         if green > red:
#             r = 'Зеленый'
#         else:
#             r = 'Красный'
#         print(r)
#         frame = cv2.putText(frame, r, (50, 50), cv2.FONT_HERSHEY_COMPLEX,
#                    1, (255, 0, 0), 2, cv2.LINE_AA)
#         cv2.imshow('cap', frame)
#         cv2.imshow('traffic light red', traffic_light_img_red)
#         cv2.imshow('traffic light green', traffic_light_img_green)
#
#         cv2.waitKey(0)
#
#         cv2.destroyAllWindows()

