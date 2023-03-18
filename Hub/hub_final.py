import cv2
import numpy as np
import os

sdr = np.float32([
    [0, 0],
    [300, 0],
    [0, 300],
    [300, 300]
])

imPath = os.walk('images/')
cap = cv2.VideoCapture(0)
for i in imPath:
    imPath = i[2]
i = 0
need = ['g', 'b', 'g']
while i < 20:
    frame, ret = cap.read()#cv2.imread('images/' + imPath[i])
    if not ret:
        break
    filter = np.array([[-1, -1, -1],
                        [-1, 8, -1],
                        [-1, -1, -1]], dtype=np.float32)
    img = cv2.resize(frame, (480, 400))
    imgfl = cv2.filter2D(img, -1, filter) #delta=100)
    binimg = cv2.inRange(imgfl, (40, 40, 40), (255, 255, 255))
    # binimg = cv2.erode(binimg, None, iterations=1)
    binimg = cv2.dilate(binimg, None, iterations=1)
    binimg = cv2.erode(binimg, None, iterations=1)
    #binimg = cv2.inRange(binimg, 0, 0)
    contours, _ = cv2.findContours(binimg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    kubs = 0
    lines = []
    x_coordinates = []
    y_coordinates = []
    cv2.drawContours(imgfl, contours[0], -1, (0, 0, 255), 2)
    for j in range(len(contours)):
        # cv2.drawContours(img, contours, j, (0, 0, 255), 2)
        (x, y, w, h) = cv2.boundingRect(contours[j])
        if 23 < w < 60 and 23 < h < 60 and w - h <= 7:
            same = False
            for ii in range(len(x_coordinates)):
                if abs((x + w // 2) - x_coordinates[ii]) < 10 and abs((y + h // 2) - y_coordinates[ii]) < 10:
                    same = True
                    break
            if not same: # если контур не повторяется (иногда один куб жетектится дважду, то была провекра)
                ans = []
                kubs += 1
                x_coordinates.append(x + w // 2) # запоминаем координаты найденого куба
                y_coordinates.append(y + h // 2)

                # поиск куба
                rect = cv2.minAreaRect(contours[j])  # пытаемся вписать прямоугольник в контур
                box = cv2.boxPoints(rect)  # поиск четырех вершин прямоугольника
                box = np.int0(box)  # округление координат
                # cv2.drawContours(img, [box], 0, (0, 0, 0), 2)
                box = list(box)
                box[2], box[3] = box[3], box[2]
                box = np.float32(box)

                mm = cv2.getPerspectiveTransform(box, sdr) # растягиваем до квадрата, выравнивание
                marker = cv2.warpPerspective(img, mm, (300, 300), flags=cv2.INTER_LINEAR)

                # маски для поиска цветов
                red_mask = cv2.inRange(marker, (0, 0, 200), (160, 220, 255))
                green_mask = cv2.inRange(marker, (0, 125, 0), (100, 255, 160))
                blue_mask = cv2.inRange(marker, (220, 170, 0), (255, 255, 170))
                mask = cv2.bitwise_or(green_mask, red_mask)
                mask = cv2.bitwise_or(blue_mask, mask)

                # переводим в hsv и ищем серый
                hsv_mark = cv2.cvtColor(marker, cv2.COLOR_BGR2HSV)
                hsv_mask = cv2.inRange(hsv_mark, (0, 0, 0), (255, 50, 255))  # поиск серого
                hsv_mask = cv2.inRange(hsv_mask, 0,0)

                # исключаем бклый и чёрный (они нам нужны)
                blak_mask = cv2.inRange(marker, (0, 0, 0), (150, 150, 150))
                white_mask = cv2.inRange(marker, (230, 230, 230), (255, 255, 255))
                hsv_mask = cv2.bitwise_or(blak_mask, hsv_mask)
                hsv_mask = cv2.bitwise_or(white_mask, hsv_mask)
                # Bitwise-AND mask and original image
                res = cv2.bitwise_and(marker, marker, mask=mask)

                # получаем чисто метку, находим контур и обводим в прямоугольник
                contours2, _ = cv2.findContours(hsv_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                contours2 = sorted(contours2, key=cv2.contourArea, reverse=True)
                # cv2.drawContours(marker, contours2, -1, (0, 255, 255), 2)
                if len(contours2) != 0:
                    (x2, y2, w2, h2) = cv2.boundingRect(contours2[0])
                    # cv2.rectangle(marker, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 255), 2)
                    marker = marker[y2:y2+h2, x2:x2+w2]
                    hsv_mark = cv2.cvtColor(marker, cv2.COLOR_BGR2HSV)
                    hsv_mask = cv2.inRange(hsv_mark, (0, 0, 0), (255, 50, 255))  # поиск серого
                    hsv_mask = cv2.inRange(hsv_mask, 0, 0)

                    white_mask = cv2.inRange(marker, (230, 230, 230), (255, 255, 255))
                    hsv_mask = cv2.bitwise_or(white_mask, hsv_mask)

                    s1 = np.sum(hsv_mask[0:h2//2, 0:w2//2])
                    s2 = np.sum(hsv_mask[h2//2:h2, 0:w2//2])
                    s3 = np.sum(hsv_mask[0:h2//2, w2//2:w2])
                    s4 = np.sum(hsv_mask[h2//2:h2, w2//2:w2])
                    for ii in range(4):
                        if s3+10000 < s1 or s3+10000 < s2 or s3+100000 < s4:
                            #print('r' + str(ii))
                            marker = cv2.rotate(marker, cv2.ROTATE_90_COUNTERCLOCKWISE)
                            hsv_mask = cv2.rotate(hsv_mask, cv2.ROTATE_90_COUNTERCLOCKWISE)
                            s1 = np.sum(hsv_mask[0:h2 // 2, 0:w2 // 2])
                            s2 = np.sum(hsv_mask[h2 // 2:h2, 0:w2 // 2])
                            s3 = np.sum(hsv_mask[0:h2 // 2, w2 // 2:w2])
                            s4 = np.sum(hsv_mask[h2 // 2:h2, w2 // 2:w2])
                        else:
                            break
                    # cv2.circle(marker, (w2//2, h2//8), 1, (0,255,0), 1)
                    # cv2.circle(marker, (w2 //2, (h2//8)+(h2//4)), 1, (0, 255, 0), 1)
                    # cv2.circle(marker, (w2 //2, (h2//8)+(h2*2//4)), 1, (0, 255, 0), 1)
                    # cv2.circle(marker, (w2 //2, (h2//8)+(h2*3//4)), 1, (0, 255, 0), 1)
                    for pts in range(3):
                        pic_color = marker[(h2//8)+(pts*h2//4)][w2//2]
                        if pts == 0:
                            print(str(pic_color)+'   '+str(j))
                        col_r = pic_color[2]
                        col_g = pic_color[1]
                        col_b = pic_color[0]
                        if col_r > 200 and col_b > 200 and col_g > 200:
                            ans.append('0')
                        elif col_r < 150 and col_b < 150 and col_g < 150:
                            ans.append('0')
                        elif col_r > col_b and col_r > col_b:
                            ans.append('r')
                        elif col_b > col_r and col_b > col_g:
                            ans.append('b')
                        elif col_g > col_r and col_g > col_b:
                            ans.append('g')
                        print()
                    if ans == need:
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)
                    cv2.circle(marker, (w2//2, h2//8), 1, (0,255,0), 1)
                    cv2.circle(marker, (w2 //2, (h2//8)+(h2//4)), 1, (0, 255, 0), 1)
                    cv2.circle(marker, (w2 //2, (h2//8)+(h2*2//4)), 1, (0, 255, 0), 1)
                    #cv2.circle(marker, (w2 //2, (h2//8)+(h2*3//4)), 1, (0, 255, 0), 1)
                    # contours1, _ = cv2.findContours(hsv_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    # contours1 = sorted(contours1, key=cv2.contourArea, reverse=True)
                    # (mx1, my1, mx2, my2) = 600, 600, 0, 0
                    # for k in range(len(contours1)):
                    #     (x1, y1, w1, h1) = cv2.boundingRect(contours1[k])
                    #     if w1 > 30 or h1 > 30:
                    #         cv2.rectangle(marker, (x1, y1), (x1 + w1, y1 + h1), (0, 255, 0), 2)
                    #         # print(j, k, x1, y1, x1+w1, y1+h1)
                    #         mx1, my1 = min(x1, mx1), min(y1, my1)
                    #         mx2, my2 = max(x1 + w1, mx2), max(y1 + h1, my2)
                    # cv2.rectangle(marker, (mx1, my1), (mx2, my2), (255, 0, 255), 1)

                    # cuted = marker[my1:my2, mx1:mx2]
                    # if np.sum(cuted) > 490000:
                    #     lines.append(3)
                    # elif 490001 > np.sum(cuted) > 290000:
                    #     lines.append(2)
                    # else:
                    #     lines.append(1)
                    #cv2.rectangle(marker, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 255), 2)
                    # (x2, y2, w2, h2) = cv2.boundingRect(contours2[1])
                    # cv2.rectangle(marker, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 255), 2)
                '''TODO:
                после детакта маркировки поиск цветов 
                разворот началом маркировки вверх, как в final_goodimg
                само определение цветов и маркировки
                '''

                print(str(j) + '   ' +"".join(ans))
                cv2.imshow("mask" + str(j), hsv_mask)
                cv2.imshow("mmmark" + str(j), marker)
    cv2.imshow("bin", binimg)
    cv2.imshow("imgfl", imgfl)
    cv2.imshow("img", img)
    key = cv2.waitKey(1)
    if key == ord('n'):
        cv2.destroyAllWindows()
        i += 1
    if key == ord('q'):
        cv2.destroyAllWindows()
        break