# cv-foundations-2

## Conteúdo
 1. [Requisitos](#requisitos)
 2. [Estrutura](#estrutura)
 3. [Uso](#uso)

## Requisitos 
1.  Python 3.5.2	
2.  OpenCV 3.3.0

## Estrutura
- Pasta xml com arquivos com matrizes instrínsecas e vetores de rotação e translação:
	- Arquivos distortion são vetores de translação, com o nome dos donos das respectivas câmeras
	- Arquivos intrinsics são matrizes de parâmetros intrínsecos, com o nome dos donos das respectivas câmeras
	- Arquivos rvec são vetores de rotação, com a distância entre a câmera e o centro de coordenadas em mm e o nome do dono da câmera
	- Arquivos tvec são vetores de translação, análogos aos de rotação
	- Arquivos std contém os desvios padrões da entidade correspondente
- Pasta tex_src com código fonte do relatório
- Arquivo paper.pdf com o relatório
- scrips python:
	- calibrate.py para obter matriz de instrinsecos e vetor de distorção, além de extrinsecos estimados por calibrateCamera
	- proj2.pu com o código principal do projeto

## Uso
- A partir do diretório raiz rodar com configurações padrão:
	```bash
	python proj1.py [número do requisito]
	```
-  [número do requisito] corresponde a 1, 2, 3 ou 4 dependendo do requisito a ser testado.
- Pode-se customizar o uso do programa por meio de flags opcionais:
	- -distortion para forncecer caminho para vetor de distorção
	- -intrinsics para fornecer caminho para matriz de intrinsecos
	- -tvec para fornecer caminho para vetor de translação
	- -rvec para forncecer caminho para vetor de rotação
	- -size para fornecer tamanho do lado do quadrado do tabuleiro, em mm
- [Repositório do github](https://github.com/peluz/cv-foundations-2/)
- Obs:
	- Para o requisito 2, pressupõe-se que foram obtidas as matrizes de intrinsecos e de distorções por meio do script calibrate.py. Ao rodar o requisito 2, as matrizes devem ser indicadas pelas flags correspondentes, descritas acima.
	- Para o requisito 4, devem ser indicadas todas as matrizes obtidas da calibração da câmera. O objeto medido deverá se localizar no mesmo plano do padrão de calibração no momento de obtenção dos extrínsecos (requisito 3).
