import cv2
#import yolopy

CAMERA_ID = '/dev/video0'

with open('data/objc.names', 'r') as f:
    classes = f.read().splitlines()

net = cv2.dnn.readNetFromDarknet('data/yoloc.cfg', 'data/yolo_bestc.weights')

model = cv2.dnn_DetectionModel(net)
model.setInputParams(scale=1 / 255, size=(416, 416), swapRB=True)

# открываем видеокамеру
cap = cv2.VideoCapture(CAMERA_ID, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(1280*0.6))
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(720*0.6))

while True:
    # получаем кадр
    ret, frame = cap.read()
    if not ret:
        break
    classIds, scores, boxes = model.detect(frame, confThreshold=0.6, nmsThreshold=0.4)


    for (classId, score, box) in zip(classIds, scores, boxes):
        cv2.rectangle(frame, (box[0], box[1]), (box[0] + box[2], box[1] + box[3]),
                      color=(0, 255, 0), thickness=2)

        text = '%s: %.2f' % (classes[classId[0]], score)
        cv2.putText(frame, text, (box[0], box[1] - 5), cv2.FONT_HERSHEY_COMPLEX, 1,
                    color=(0, 255, 0), thickness=2)
    cv2.putText(frame, str(len(classIds)), (20, 20), cv2.FONT_HERSHEY_COMPLEX, 1, color=(0, 255, 0), thickness=2)
    print(len(classIds))
    cv2.imshow('cam', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


    #classes, scores, boxes = model.detect(frame)

    # печатаем id классов объектов

    #print(classes)
cap.release()
cv2.destroyAllWindows()