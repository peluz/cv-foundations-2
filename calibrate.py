import numpy as np
import cv2
import time
#--------------------------------------------------------------------------------------------------------------------------
#1.tira 5 fotos seguidas quando encontra um tabuleiro
#2.espera um tempo (4 segundos) para tentar achar um novo tabuleiro - mudar a posicao do tabuleiro
#3.volta ao procedimento 1 até que se repita 5 vezes
#4.calcula a calibração da camera com os valores achados - existe alguma função que calcule só intrinseco e distortion? -
#5.realiza o precedimento 1 mais cinco vezes, até o atual
#6.calcula a media dos parametros
#7.salva num xml 
#--------------------------------------------------------------------------------------------------------------------------


#---fazer acoplar_requisito_1_mouse------------------------------------------------------------------------------------------

# Definine as linhas e colunas do tabuleiro de xadrez
board_w = 8
board_h = 6

# Set the termination criteria for the corner sub-pixel algorithm - Não sei o que é criteria
criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 30, 0.001)

# Prepara os objetos-pontos: (0,0,0), (1,0,0), (2,0,0), ..., (6,5,0). Eles são na mesma quantidade para todas imagens
objectPoints = np.zeros((board_w * board_h, 3), np.float32)
objectPoints[:, :2] = np.mgrid[0:board_w, 0:board_h].T.reshape(-1, 2)

#Cria arrays para armazenar os valores calibrados 
mtx_values = []
dist_values = []
rvecs_values = []
tvecs_values = []

#Cria as janelas e determina o tamanho destas
cv2.namedWindow('raw',cv2.WINDOW_NORMAL)
cv2.resizeWindow('raw', 300,300)
cv2.namedWindow('capture',cv2.WINDOW_NORMAL)
cv2.resizeWindow('capture', 300,300)

captura = cv2.VideoCapture(0)

#Calucula no maximo 5 calibracoes:
#	Calibracoes sao compostas de 5 screenshots
calibrations = 0
while calibrations < 5:

	# Cria os arrays para armazenar os pontos e as imagens
	objectPointsArray = [] # 3d pontos no mundo real
	imgPointsArray = [] # 2d pontos no plano da imagem

	print("Iniciando nova calibracao: Posicione o tabuleiro")

	#Calucula no maximo 5 screenshots:
	#	Cada screenshot captura 5 imagens(spanspots) rapidamente no mesmo ponto
	#	Após a captura das spanspots espera 4 segundos para capturar uma nova screenshot
	screenshots = 0
	while screenshots < 5:

		spanspots = 0
		while spanspots < 5:

			_, img = captura.read()
			cv2.imshow('raw', img)

			global gray
			gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

			# Encontra os cantos do tabuleiro
			ret, corners = cv2.findChessboardCorners(gray, (board_w, board_h), None)
	
			# Tem certeza que o padrao de tabuleiro foi detectado
			if ret:
				# Refina a posicao do canto
				corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
		
				# Adiciona os pontos e as imagens aos seus arrays
				objectPointsArray.append(objectPoints)
				imgPointsArray.append(corners)
	
				# Desenha os cantos na imagem
				cv2.drawChessboardCorners(img, (board_w, board_h), corners, ret)
	
				# Mostra a imagem
				cv2.imshow('capture', img)

				spanspots = spanspots + 1

			# Espera 30 milisegundos entre cada spanspot
			k = cv2.waitKey(30) & 0xff

		screenshots = screenshots + 1
		print("Mude de posicao -- tens 4 segundos")
		time.sleep(4)

	# Calclula os parametros de calibracao e adiciona eles no vetor de parametros
	#---fazer calcular_somente_intrisecos_e_distortion-----------------------------------------------------------------------
	print("Calculando parametros de calibração")
	ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objectPointsArray, imgPointsArray, gray.shape[::-1], None, None)
	mtx_values.append(mtx)
	dist_values.append(dist)
	rvecs_values.append(rvecs)
	tvecs_values.append(tvecs)
	
	calibrations = calibrations + 1
	print("Calculo de parametros feito. Digite ESC para iniciar a proxima calibraçao")
	print("Digite 'q' para acabar as calibrações")
	while(True):
		k = cv2.waitKey(30) & 0xff
		if k == 27:
			break
		if k == ord('q'):
			calibrations = 5
			break

# Cacula media vetores de parametros e desviopadrao
mtx_avrg = np.average(mtx_values,axis=0)
dist_avrg = np.average(dist_values,axis=0)
rvecs_avrg = np.average(rvecs_values,axis=0)
tvecs_avrg = np.average(tvecs_values,axis=0)

mtx_std = np.std(mtx_values,axis=0)
dist_std = np.std(dist_values,axis=0)
rvecs_std = np.std(rvecs_values,axis=0)
tvecs_std = np.std(tvecs_values,axis=0)

# Salva xml da media e desvio padrao
cv_file = cv2.FileStorage("xml/intrinsics.xml", cv2.FILE_STORAGE_WRITE)
cv_file.write("intrinsics_avg", mtx_avrg)
cv_file.release()

cv_file = cv2.FileStorage("xml/intrinsics_std.xml", cv2.FILE_STORAGE_WRITE)
cv_file.write("intrinsics_std", mtx_std)
cv_file.release()

cv_file = cv2.FileStorage("xml/distortion.xml", cv2.FILE_STORAGE_WRITE)
cv_file.write("distortion_avg", dist_avrg)
cv_file.release()

cv_file = cv2.FileStorage("xml/distortion_std.xml", cv2.FILE_STORAGE_WRITE)
cv_file.write("distortion_std", dist_std)
cv_file.release()

# Tudo feito, libera a captura
captura.release()
cv2.destroyAllWindows()
