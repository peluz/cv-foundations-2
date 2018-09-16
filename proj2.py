import cv2
import numpy as np
import sys
import argparse
import time


DEFAULT_SQUARE = 28
D_MIN = 0
D_MED = 0
D_MAX = 0
BOARD_WIDTH = 8
BOARD_HEIGHT = 6


parser = argparse.ArgumentParser(
    description="Regua virtual")
parser.add_argument("requisito", type=int, nargs=1, choices=range(1, 5),
                    help="número do requisito de avaliação")
parser.add_argument("-distortion", nargs="?", default=None, metavar="path/to/file",
                    help="Caminho para a matriz de distorção media")
parser.add_argument("-intrinsics", nargs="?", default=None, metavar="path/to/file",
                    help="Caminho para a matrinz intrinseca media")
parser.add_argument("-size", nargs="?", default=DEFAULT_SQUARE, type=float,
                    help="Tamanho do lado do quadrado do tabuleiro em mm")
parser.add_argument("-bonus", default=False, type=bool,
                    help="Muda a forma de calcular os extrinsecos")


def openImage(file):
    if file is None:
        filename = "imgs/lena.png"
    else:
        filename = file
    img = cv2.imread(filename)
    if img is None:
        sys.exit("Não foi possível abrir imagem")
    return img


def imageDistance():
    global first, pos1, pos2
    first = True
    pos1 = pos2 = None

    cap = cv2.VideoCapture(0)

    while(True):
        ret, img = cap.read()
        cv2.namedWindow('Imagem')
        cv2.setMouseCallback('Imagem', getPixelsDistance, img)
        if ret:
            cv2.imshow("Imagem", img)
        cv2.waitKey(1)
        if cv2.waitKey(20) & 0xFF == 27:
            break
    cv2.destroyAllWindows()


def getPixelsDistance(event, x, y, flags, params):
    global first, pos1, pos2
    img = params
    if event == cv2.EVENT_LBUTTONUP:
        if first:
            pos1 = [x, y]
        else:
            pos2 = [x, y]
        first = not first
        if pos1 is not None and pos2 is not None:
            cv2.namedWindow('Medida')
            cv2.line(img, tuple(pos1),
                     tuple(pos2), (0, 0, 255), 2)
            cv2.imshow("Medida", img)
            distance = np.linalg.norm(np.array(pos2) - np.array(pos1))
            print("Pos1:{}, Pos2:{}, Distance: {}".format(pos1,
                                                          pos2, distance))
            pos1 = pos2 = None


def showRawAndUndistorted(distortion,
                          intrinsics):
    global first, pos1, pos2
    first = True
    pos1 = pos2 = None
    distMatrix = loadDistortionMatrix(distortion)
    intMatrix = loadIntrinsicMatrix(intrinsics)

    cap = cv2.VideoCapture(0)

    while(True):
        ret, img = cap.read()

        cv2.namedWindow('raw')
        cv2.namedWindow('undistorted')
        h, w = img.shape[:2]

        # undistort
        undst = cv2.undistort(img, intMatrix, distMatrix)

        cv2.setMouseCallback('raw', getPixelsDistance, img)
        cv2.setMouseCallback('undistorted', getPixelsDistance, undst)

        cv2.imshow("raw", img)
        cv2.imshow("undistorted", undst)
        cv2.waitKey(1)
        if cv2.waitKey(20) & 0xFF == 27:
            break
    cv2.destroyAllWindows()


def loadIntrinsicMatrix(intrinsics):
    if intrinsics is None:
        intrinsics = "xml/intrinsics_pedro.xml"
        print("\nUsando matrix intrinseca de Pedro!\nRode calibrate.py pra conseguir a sua ou indique o caminho para a mesma usando a flag -intrinsics\n")
    file = cv2.FileStorage(intrinsics, cv2.FileStorage_READ)
    intMatrix = file.getNode("intrinsics_avg").mat()
    file.release()
    return intMatrix


def loadDistortionMatrix(distortion):
    if distortion is None:
        distortion = "xml/distortion_pedro.xml"
        print("\nUsando vetor de distorção de Pedro!\nRode calibrate.py pra conseguir o seu ou indique o caminho para o mesmo usando a flag -distortion\n")
    file = cv2.FileStorage(distortion, cv2.FileStorage_READ)
    distMatrix = file.getNode("distortion_avg").mat()
    file.release()
    return distMatrix


def findBoardPoints(squareSize=DEFAULT_SQUARE):
    boardPoints = []
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            boardPoints.append((x * squareSize, y * squareSize, 0))
    boardPoints = np.array(boardPoints, dtype=np.float32)
    return boardPoints


def findExtrinsicParams(distortion, intrinsics, bonus):
    distMatrix = loadDistortionMatrix(distortion)
    intMatrix = loadIntrinsicMatrix(intrinsics)
    criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 30, 0.001)
    objectPoints = findBoardPoints()
    cap = cv2.VideoCapture(0)
    cv2.namedWindow('raw')
    cv2.namedWindow('capture')

    for distance in ["dmin", "dmax", "dmed"]:
        print("Calibrando extrínsecos para distância " + distance)

        rVecValues = []
        tVecValues = []
        objectPointsArray = [] # 3d pontos no mundo real
        imgPointsArray = []
        
        screenshots = 0
        while screenshots < 3:
            spanspots = 0
            while spanspots < 5:
                _, img = cap.read()
                cv2.imshow('raw', img)

                global gray
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                ret, corners = cv2.findChessboardCorners(
                    gray, (BOARD_WIDTH, BOARD_HEIGHT), None)

                if ret:
                    corners = cv2.cornerSubPix(
                        gray, corners, (11, 11), (-1, -1), criteria)

                    cv2.drawChessboardCorners(
                        img, (BOARD_WIDTH, BOARD_HEIGHT), corners, ret)

                    objectPointsArray.append(objectPoints)
                    imgPointsArray.append(corners)

                    cv2.imshow('capture', img)
                    spanspots += 1
                cv2.waitKey(30) & 0xff
            screenshots += 1

            global rvec, tvec
            if bonus:
                ret, _1, _2, rvec, tvec = cv2.calibrateCamera(objectPointsArray, 
                                                              imgPointsArray, gray.shape[::-1], None, None)
                
            else:
                ret, rvec, tvec = cv2.solvePnP(objectPoints, corners, intMatrix,
                                               distMatrix, flags=cv2.SOLVEPNP_ITERATIVE)

            rVecValues.append(rvec)
            tVecValues.append(tvec)
            print(tVecValues)
            print(rVecValues)
            if screenshots < 3:
                print("Buscando nova captura na mesma posição")
            time.sleep(1)
        print("Calculando parâmetros extrínsecos para distancia " + distance)
        rvec_avg = np.average(rVecValues, axis=0)
        rvec_std = np.std(rVecValues, axis=0)
        tvec_avg = np.average(tVecValues, axis=0)
        tvec_std = np.std(tVecValues, axis=0)
        print(tvec_avg)
        dist = float(input("Insira distância da captura em mm. Modo: " + distance + ": "))
        name = str(input("Insira nome para a câmera em questão: "))
        saveParameters(rvec_avg, rvec_std, tvec_avg, tvec_std, dist, name, bonus)
    cap.release()
    cv2.destroyAllWindows()


def saveParameters(rvec_avg, rvec_std, tvec_avg, tvec_std, dist, name, bonus):
    if bonus:
        cv_file = cv2.FileStorage("xml/rvec_{}_{}_bonus.xml".format(dist, name), cv2.FILE_STORAGE_WRITE)
        cv_file.write("rvec_avg", rvec_avg)
        cv_file.release()

        cv_file = cv2.FileStorage("xml/rvec_std_{}_{}_bonus.xml".format(dist, name), cv2.FILE_STORAGE_WRITE)
        cv_file.write("rvec_std", rvec_std)
        cv_file.release()

        cv_file = cv2.FileStorage("xml/tvec_{}_{}_bonus.xml".format(dist, name), cv2.FILE_STORAGE_WRITE)
        cv_file.write("tvec_avg", tvec_avg)
        cv_file.release()

        cv_file = cv2.FileStorage("xml/tvec_std_{}_{}_bonus.xml".format(dist, name), cv2.FILE_STORAGE_WRITE)
        cv_file.write("tvec_std", tvec_std)
        cv_file.release()

    else:
        cv_file = cv2.FileStorage("xml/rvec_{}_{}.xml".format(dist, name), cv2.FILE_STORAGE_WRITE)
        cv_file.write("rvec_avg", rvec_avg)
        cv_file.release()

        cv_file = cv2.FileStorage("xml/rvec_std_{}_{}.xml".format(dist, name), cv2.FILE_STORAGE_WRITE)
        cv_file.write("rvec_std", rvec_std)
        cv_file.release()

        cv_file = cv2.FileStorage("xml/tvec_{}_{}.xml".format(dist, name), cv2.FILE_STORAGE_WRITE)
        cv_file.write("tvec_avg", tvec_avg)
        cv_file.release()

        cv_file = cv2.FileStorage("xml/tvec_std_{}_{}.xml".format(dist, name), cv2.FILE_STORAGE_WRITE)
        cv_file.write("tvec_std", tvec_std)
        cv_file.release()

def main(requisite, distortion=None, intrinsics=None, size=DEFAULT_SQUARE, bonus=False):
    if requisite == 1:
        return imageDistance()
    elif requisite == 2:
        return showRawAndUndistorted(distortion, intrinsics)
    elif requisite == 3:
        return findExtrinsicParams(distortion, intrinsics, bonus)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args.requisito[0], args.distortion, args.intrinsics, args.size, args.bonus)
