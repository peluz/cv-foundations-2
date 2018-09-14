import cv2
import numpy as np
import sys

coord_ini = [None,None]
coord_fin = [None,None]

def click_event(event,x,y,flags,param):
	if event == cv2.EVENT_LBUTTONDOWN:
		global coord_ini,coord_fin
		if coord_ini[0] is None:
			coord_ini = [x,y]
		else:
			if coord_fin[0] is None:
				coord_fin = [x,y]
				global img
				cv2.line(img,tuple(coord_ini),tuple(coord_fin),(0,0,255),4)
				cv2.imshow("image",img)
				dif = np.subtract(coord_ini,coord_fin)
				distance = np.power(np.dot(dif,dif),0.5)
				print("Distance:",distance)

img = cv2.imread(sys.argv[1])

if img is None:
	print("Ivalid name!")
else:
	#mostra a img valida
	cv2.imshow("image",img)

	cv2.setMouseCallback("image",click_event)

	cv2.waitKey(0)
	cv2.destroyAllWindows()



