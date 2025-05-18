import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy.spatial import Delaunay
from scipy.ndimage import gaussian_filter
import trimesh

def is_contour_open(contour, tolerance=10):
    return cv2.norm(contour[0][0] - contour[-1][0]) > tolerance

def mirror_contour(contour, axis='vertical'):
    if axis == 'vertical':
        xs = [pt[0][0] for pt in contour]
        mid_x = (min(xs) + max(xs)) // 2
        mirrored = [[[2 * mid_x - pt[0][0], pt[0][1]]] for pt in contour]
    elif axis == 'horizontal':
        ys = [pt[0][1] for pt in contour]
        mid_y = (min(ys) + max(ys)) // 2
        mirrored = [[[pt[0][0], 2 * mid_y - pt[0][1]]] for pt in contour]
    return np.array(mirrored, dtype=np.int32)

# === Carregar imagem ===
#'C:\Users\Carlo\Desktop\Mestrado\TCC\curvas_de_nivel2.png'
path = r'C:\Users\joaop\Downloads\personal-downloads\curvas_de_nivel2.png'
img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

if img is None:
    print("❌ Erro: Imagem não encontrada.")
    exit()

# === Correção de Distorsão (caso você tenha os parâmetros de calibração da câmera) ===
# Para simplificação, vou comentar aqui. Se tiver parâmetros da câmera, use:
# camera_matrix, dist_coeffs = calibração_da_câmera()
# img = cv2.undistort(img, camera_matrix, dist_coeffs)

# === Pré-processamento ===
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
img_eq = clahe.apply(img)
img_blur = cv2.GaussianBlur(img_eq, (5, 5), 0)
img_thresh = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY_INV, 11, 2)
edges = cv2.Canny(img_thresh, 30, 100)
kernel = np.ones((3, 3), np.uint8)
edges_dilated = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)

# === Detecção de contornos ===
contours, _ = cv2.findContours(edges_dilated, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
contours = sorted(contours, key=cv2.contourArea, reverse=True)

# === Filtrar contornos pequenos e remover o maior (linha externa) ===
min_area = 60
contours_filtered = [c for c in contours if cv2.contourArea(c) >= min_area]
if contours_filtered:
    contours_filtered = contours_filtered[1:]  # Remove o maior

# === Completar contornos abertos ===
augmented_contours = []
for c in contours_filtered:
    if is_contour_open(c):
        mirrored = mirror_contour(c, axis='vertical')  # ou 'horizontal'
        combined = np.vstack((c, mirrored[::-1]))
        augmented_contours.append(combined)
    else:
        augmented_contours.append(c)

# === Correção de Perspectiva ===
# Detecta os 4 cantos do papel para corrigir a perspectiva (definir manualmente os pontos)
pts_originais = np.float32([[100, 150], [400, 130], [410, 500], [90, 520]])  # Exemplo de pontos
largura, altura = 512, 512
pts_destino = np.float32([[0, 0], [largura, 0], [largura, altura], [0, altura]])

# Calcular a matriz de homografia
matriz = cv2.getPerspectiveTransform(pts_originais, pts_destino)
img_retificada = cv2.warpPerspective(img, matriz, (largura, altura))

# === Renderização 2D ===
img_color = cv2.cvtColor(img_retificada, cv2.COLOR_GRAY2BGR)

max_altitude = 255
total_curves = len(augmented_contours)
lines_3d = []
altitudes = []

for idx, contour in enumerate(augmented_contours):
    altitude = int((idx / total_curves) * max_altitude)
    color = cv2.applyColorMap(np.uint8([[altitude]]), cv2.COLORMAP_JET)[0][0].tolist()
    cv2.drawContours(img_color, [contour], -1, color, 1)

    curve_3d = [(pt[0][0], pt[0][1], altitude) for pt in contour]
    lines_3d.append(curve_3d)
    altitudes.append(altitude)

# === Mostrar imagem 2D ===
cv2.imshow("Curvas de Nível em 2D (completadas)", img_color)
cv2.imwrite("curvas_completas_2d.png", img_color)

# === Visualização 3D ===
fig = plt.figure(figsize=(16, 8))

# Subplot 1: linhas 3D
ax1 = fig.add_subplot(121, projection='3d')
for line, z in zip(lines_3d, altitudes):
    xs, ys, zs = zip(*line)
    color = cm.jet(z / max_altitude)
    ax1.plot(xs, ys, zs, color=color, linewidth=1.5)
ax1.set_title('Modelo 3D com Linhas de Curvas', fontsize=12)
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Altitude')
ax1.view_init(elev=45, azim=135)

# Subplot 2: superfície interpolada
all_points = []
all_z = []
for line, z in zip(lines_3d, altitudes):
    for x, y, _ in line:
        all_points.append([x, y])
        all_z.append(z)

points = np.array(all_points)
values = np.array(all_z)

# Suavização opcional no eixo Z
values_smoothed = gaussian_filter(values.astype(float), sigma=2)

tri = Delaunay(points)
ax2 = fig.add_subplot(122, projection='3d')
ax2.plot_trisurf(points[:, 0], points[:, 1], values_smoothed, triangles=tri.simplices,
                 cmap='terrain', linewidth=0.2, antialiased=True)
ax2.set_title('Superfície 3D Interpolada do Terreno (suavizada)', fontsize=12)
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.set_zlabel('Altitude')
ax2.view_init(elev=60, azim=135)

plt.tight_layout()
plt.show()

# === Exportar para GLB com as cores ===
# Mapear cores para os vértices (associar altitude com cores)
max_altitude = max(altitudes)
colors = []
for z in altitudes:
    color = cm.jet(z / max_altitude)[:3]  # Pega a cor RGB
    colors.append(color)

# Criar a malha 3D com cores
vertices = np.column_stack((points, values_smoothed))
faces = tri.simplices

# Criar o objeto mesh no Trimesh
mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

# Associar as cores aos vértices
mesh.visual.vertex_colors = np.array(colors) * 255  # Normalizando para valores de 0 a 255

# Exportar o modelo 3D como um arquivo .glb com as cores
mesh.export("modelo_terreno_com_cores_2.glb")
print("✅ Modelo 3D exportado como 'modelo_terreno_com_cores.glb'")