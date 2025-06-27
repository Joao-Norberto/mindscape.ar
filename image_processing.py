# image_processing.py

def process_image(input_path, output_path):
    import cv2
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib import cm
    from scipy.spatial import Delaunay
    from scipy.ndimage import gaussian_filter
    import trimesh

    # === Carregar imagem ===
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise Exception("❌ Erro: Imagem não encontrada.")

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
        contours_filtered = contours_filtered[1:]

    # === Completar contornos abertos ===
    augmented_contours = []
    for c in contours_filtered:
        if is_contour_open(c):
            mirrored = mirror_contour(c, axis='vertical')
            combined = np.vstack((c, mirrored[::-1]))
            augmented_contours.append(combined)
        else:
            augmented_contours.append(c)

    # === Correção de Perspectiva ===
    pts_originais = np.float32([[100, 150], [400, 130], [410, 500], [90, 520]])  # Exemplo fixo
    largura, altura = 512, 512
    pts_destino = np.float32([[0, 0], [largura, 0], [largura, altura], [0, altura]])
    matriz = cv2.getPerspectiveTransform(pts_originais, pts_destino)
    img_retificada = cv2.warpPerspective(img, matriz, (largura, altura))

    # === Renderização e geração das curvas 3D ===
    max_altitude = 255
    total_curves = len(augmented_contours)
    lines_3d = []
    altitudes = []

    for idx, contour in enumerate(augmented_contours):
        altitude = int((idx / total_curves) * max_altitude)
        curve_3d = [(pt[0][0], pt[0][1], altitude) for pt in contour]
        lines_3d.append(curve_3d)
        altitudes.append(altitude)

    # === Geração da malha 3D para exportação ===
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

    # Delaunay triangulation
    tri = Delaunay(points)
    vertices = np.column_stack((points, values_smoothed))
    faces = tri.simplices

    # Cores para os vértices
    max_altitude = max(altitudes) if altitudes else 1
    colors = []
    for z in values_smoothed:
        color = cm.jet(z / max_altitude)[:3]
        colors.append(np.array(color) * 255)

    # Criação da malha
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    mesh.visual.vertex_colors = np.array(colors, dtype=np.uint8)

    # Exporta como GLB
    mesh.export(output_path)
    print(f"✅ Modelo 3D exportado como '{output_path}'")
    