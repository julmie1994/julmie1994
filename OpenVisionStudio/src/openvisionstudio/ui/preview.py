from __future__ import annotations

import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView


class ImagePreview(QGraphicsView):
    pixel_hovered = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._item = QGraphicsPixmapItem()
        self._scene.addItem(self._item)
        self._image: np.ndarray | None = None
        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def set_image(self, image: np.ndarray) -> None:
        self._image = image
        if image.ndim == 2:
            qimg = QImage(
                image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format_Grayscale8
            )
        else:
            rgb = image[:, :, ::-1].copy()
            qimg = QImage(
                rgb.data, rgb.shape[1], rgb.shape[0], rgb.strides[0], QImage.Format_RGB888
            )
        self._item.setPixmap(QPixmap.fromImage(qimg))
        self.fitInView(self._item, Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        factor = 1.25 if event.angleDelta().y() > 0 else 0.8
        self.scale(factor, factor)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self._image is None:
            return
        pos = self.mapToScene(event.pos())
        x, y = int(pos.x()), int(pos.y())
        if 0 <= y < self._image.shape[0] and 0 <= x < self._image.shape[1]:
            value = self._image[y, x]
            self.pixel_hovered.emit(f"({x}, {y})={value}")
