import qrcode
import cv2

data = "Sheet ID"

Code = qrcode.make(data)

cv2.imshow("Sheet ID", Code)

cv2.waitKey(0)

cv2.destroyAllWindows()