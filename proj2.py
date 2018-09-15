import cv2
import numpy as np
import sys
import argparse


parser = argparse.ArgumentParser(
    description="Regua virtual")
parser.add_argument("requisito", type=int, nargs=1, choices=range(1, 5),
                    help="número do requisito de avaliação")
parser.add_argument("-file", nargs="?", default=None, metavar="path/to/file",
                    help="Caminho para a imagem/vídeo")


def openImage(file):
    if file is None:
        filename = "imgs/lena.png"
    else:
        filename = file
    img = cv2.imread(filename)
    if img is None:
        sys.exit("Não foi possível abrir imagem")
    return img


def imageDistance(file=None):
    global first, pos1, pos2, img, original
    first = True
    pos1 = pos2 = None
    img = openImage(file)
    original = openImage(file)
    cv2.namedWindow('Imagem')
    cv2.setMouseCallback('Imagem', getPixelsDistance)
    while(1):
        cv2.imshow("Imagem", img)
        cv2.waitKey(1)
        if cv2.waitKey(20) & 0xFF == 27:
            break
    cv2.destroyAllWindows()


def getPixelsDistance(event, x, y, flags, params):
    global first, pos1, pos2, img, original
    if event == cv2.EVENT_LBUTTONUP:
        if first:
            pos1 = [x, y]
        else:
            pos2 = [x, y]
        first = not first
        if pos1 is not None and pos2 is not None:
            img = original.copy()
            cv2.line(img, tuple(pos1),
                     tuple(pos2), (0, 0, 255), 2)
            distance = np.linalg.norm(np.array(pos2) - np.array(pos1))
            print("Pos1:{}, Pos2:{}, Distance: {}".format(pos1,
                  pos2, distance))
            pos1 = pos2 = None


def main(requisite, file=None):
    if requisite == 1:
        return imageDistance(file)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args.requisito[0], args.file)
