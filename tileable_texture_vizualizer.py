import numpy as np
import cv2


def draw_roi(img, roi_rect, color=(255, 0, 0), thickness=3):
    cy, cx, h, w = roi_rect
    img_drawn = cv2.rectangle(
        img.copy(), (cx-w//2, cy-h//2), (cx+w//2, cy+h//2), color, thickness)

    return img_drawn


def make_tile(img, roi_rect, tile_multiple=(4, 4)):
    cy, cx, h, w = roi_rect
    roi = img[cy-h//2:cy+h//2, cx-w//2:cx+w//2, :]

    # Tile the roi
    img_tiled = np.tile(roi, (*tile_multiple, 1))
    img_tiled = img_tiled.astype(np.float32)
    img_tiled[:h, :w, :] *= 0.65
    img_tiled = img_tiled.astype(np.uint8)

    return roi, img_tiled


if __name__ == '__main__':
    # Have to be defined globaly for the mouse callback
    roi_rect = None
    MOVE_SPEED = 1
    SCALE_SPEED = 1
    img = None
    is_pressed = False

    def on_mouse(event, x, y, wheel, params):
        global roi_rect, MOVE_SPEED, SCALE_SPEED, img, is_pressed
        

        # Mouse down
        if event == cv2.EVENT_LBUTTONDOWN:
            is_pressed = True

        # Mouse up
        if event == cv2.EVENT_LBUTTONUP:
            is_pressed = False

        # Move ROI using mouse
        if is_pressed and\
            event == cv2.EVENT_MOUSEMOVE and\
            y-roi_rect[2]//2-MOVE_SPEED > 0 and\
            y+roi_rect[2]//2+MOVE_SPEED < img.shape[0] and\
            x-roi_rect[3]//2-MOVE_SPEED > 0 and\
            x+roi_rect[3]//2+MOVE_SPEED < img.shape[1]:

            roi_rect[0] = y
            roi_rect[1] = x

        # Scale ROI using mouse wheel
        if event == cv2.EVENT_MOUSEWHEEL:
            if wheel > 0 and roi_rect[2] < img.shape[0]//2 and roi_rect[3] < img.shape[1]//2:
                roi_rect[2] += SCALE_SPEED
                roi_rect[3] += SCALE_SPEED
            elif wheel <= 0 and roi_rect[2] > SCALE_SPEED+3 and roi_rect[3] > SCALE_SPEED+3:
                roi_rect[2] -= SCALE_SPEED
                roi_rect[3] -= SCALE_SPEED

    # Read the image
    file_name = 'hex.jpg'
    img = cv2.imread(file_name)

    # Resize the image
    IMG_SCALE = 2
    img = cv2.resize(img, (img.shape[1]//IMG_SCALE, img.shape[0]//IMG_SCALE))

    # ROI (Center_y, Center_x, heigth, width)
    roi_height, roi_width = 150, 150
    roi_rect = [img.shape[0]//2, img.shape[1]//2, roi_height, roi_width]

    # Main loop
    tile_multiplier = 4
    tileable_img = None
    while True:

        # region Handle Keyboard Input
        key = cv2.waitKey(1)

        if key == -1:
            pass

        elif key == ord('w'):
            if roi_rect[0]-roi_rect[2]//2-MOVE_SPEED > 0:
                roi_rect[0] -= MOVE_SPEED
            else:
                print("Out of Bounds!")

        elif key == ord('s'):
            if roi_rect[0]+roi_rect[2]//2+MOVE_SPEED < img.shape[0]:
                roi_rect[0] += MOVE_SPEED
            else:
                print("Out of Bounds!")

        elif key == ord('a'):
            if roi_rect[1]-roi_rect[3]//2-MOVE_SPEED > 0:
                roi_rect[1] -= MOVE_SPEED
            else:
                print("Out of Bounds!")

        elif key == ord('d'):
            if roi_rect[1]+roi_rect[3]//2+MOVE_SPEED < img.shape[1]:
                roi_rect[1] += MOVE_SPEED
            else:
                print("Out of Bounds!")

        elif key == ord('i'):
            if roi_rect[2] < img.shape[0]//2:
                roi_rect[2] += SCALE_SPEED
            else:
                print("Out of Bounds!")

        elif key == ord('k'):
            if roi_rect[2] > SCALE_SPEED+3:
                roi_rect[2] -= SCALE_SPEED
            else:
                print("Out of Bounds!")

        elif key == ord('l'):
            if roi_rect[3] < img.shape[1]//2:
                roi_rect[3] += SCALE_SPEED
            else:
                print("Out of Bounds!")

        elif key == ord('j'):
            if roi_rect[3] > SCALE_SPEED+3:
                roi_rect[3] -= SCALE_SPEED
            else:
                print("Out of Bounds!")

        elif key == ord('q'):
            if tile_multiplier > 2:
                tile_multiplier -= 1

        elif key == ord('e'):
            if tile_multiplier < 16:
                tile_multiplier += 1

        # Enter: Save tileable_img
        elif key == 13:
            if tileable_img is not None:
                print("saved")
                cv2.imwrite(
                    f"{file_name[:file_name.find('.')]}_tileable.{file_name[file_name.find('.'):]}",
                    tileable_img)

        # ESC: close
        elif key == 27:
            break

        else:
            continue

        # endregion

        cv2.namedWindow('Select the Tileable Area Using WASD, IJKL, QE')
        cv2.setMouseCallback(
            'Select the Tileable Area Using WASD, IJKL, QE', on_mouse)

        # Draw the ROI region on the original image
        img_drawn = draw_roi(img, roi_rect)
        cv2.imshow("Select the Tileable Area Using WASD, IJKL, QE", img_drawn)

        # Draw Tiled Image
        tileable_img, tiled_image = make_tile(
            img, roi_rect, tile_multiple=(tile_multiplier, tile_multiplier))
        cv2.imshow("Tiled Image", tiled_image)

    # Cleanup
    cv2.destroyAllWindows()
