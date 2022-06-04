import fitz
from PyQt6 import QtGui

# 显示 PDF 封面
# page_data 为 page 对象
def render_pdf_page(page_data, for_cover=False):
    # 图像缩放比例
    zoom_matrix = fitz.Matrix(4, 4)
    if for_cover:
        zoom_matrix = fitz.Matrix(1, 1)
    
    # 获取封面对应的 Pixmap 对象
    # alpha 设置背景为白色
    pagePixmap = page_data.get_pixmap(
        matrix = zoom_matrix, 
        alpha=False) 
    # 获取 image 格式
    imageFormat = QtGui.QImage.Format.Format_RGB888 
    # 生成 QImage 对象
    pageQImage = QtGui.QImage(
        pagePixmap.samples,
        pagePixmap.width, 
        pagePixmap.height, 
        pagePixmap.stride,
        imageFormat)

    # 生成 pixmap 对象
    pixmap = QtGui.QPixmap()
    pixmap.convertFromImage(pageQImage)
    return pixmap

def getPDFCoverAsQPixelmap(f_path: str):
    doc = fitz.open(f_path)
    page = doc.load_page(0)
    cover = render_pdf_page(page, True)
    return cover
