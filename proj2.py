import cv2
import numpy as np
import sys
import argparse


parser = argparse.ArgumentParser(
    description="Regua virtual")
parser.add_argument("requisito", type=int, nargs=1, choices=range(1, 5),
                    help="número do requisito de avaliação")
parser.add_argument("-distortion", nargs="?", default=None, metavar="path/to/file",
                    help="Caminho para a matriz de distorção media")
parser.add_argument("-intrinsics", nargs="?", default=None, metavar="path/to/file",
                    help="Caminho para a matrinz intrinseca media")


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


def main(requisite, distortion=None, intrinsics=None):
    if requisite == 1:
        return imageDistance()
    elif requisite == 2:
        return showRawAndUndistorted(distortion, intrinsics)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args.requisito[0], args.distortion, args.intrinsics)
