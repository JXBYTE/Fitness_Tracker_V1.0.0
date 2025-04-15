import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox)


class MetricsTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Трекер показателей")
        self.setGeometry(100, 100, 800, 600)
        
        self.metrics = []  # Список для хранения показателей
        self.current_edit_id = None  # ID редактируемой записи
        
        self.init_ui()
        
    def init_ui(self):
        # Главный виджет и layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Форма для ввода данных
        form_layout = QHBoxLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Название показателя")
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Значение")
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("Дата (ГГГГ-ММ-ДД)")
        
        form_layout.addWidget(QLabel("Название:"))
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(QLabel("Значение:"))
        form_layout.addWidget(self.value_input)
        form_layout.addWidget(QLabel("Дата:"))
        form_layout.addWidget(self.date_input)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_metric)
        
        self.edit_button = QPushButton("Редактировать")
        self.edit_button.clicked.connect(self.edit_metric)
        self.edit_button.setEnabled(False)
        
        self.cancel_button = QPushButton("Отменить")
        self.cancel_button.clicked.connect(self.cancel_edit)
        self.cancel_button.setEnabled(False)
        
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_metric)
        self.delete_button.setEnabled(False)
        
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.delete_button)
        
        # Таблица с показателями
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Значение", "Дата"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.cellClicked.connect(self.table_row_selected)
        
        # Добавляем все в главный layout
        main_layout.addLayout(form_layout)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.table)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Обновляем таблицу
        self.update_table()
    
    def add_metric(self):
        """Добавление нового показателя"""
        name = self.name_input.text().strip()
        value = self.value_input.text().strip()
        date = self.date_input.text().strip()
        
        if not name or not value or not date:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return
        
        # Простая валидация даты (можно улучшить)
        if len(date) != 10 or date[4] != '-' or date[7] != '-':
            QMessageBox.warning(self, "Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД!")
            return
        
        # Добавляем новый показатель
        metric_id = len(self.metrics) + 1
        self.metrics.append({
            'id': metric_id,
            'name': name,
            'value': value,
            'date': date
        })
        
        # Очищаем поля ввода
        self.clear_inputs()
        # Обновляем таблицу
        self.update_table()
    
    def edit_metric(self):
        """Редактирование существующего показателя"""
        if self.current_edit_id is None:
            return
            
        name = self.name_input.text().strip()
        value = self.value_input.text().strip()
        date = self.date_input.text().strip()
        
        if not name or not value or not date:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return
        
        # Находим и обновляем показатель
        for metric in self.metrics:
            if metric['id'] == self.current_edit_id:
                metric['name'] = name
                metric['value'] = value
                metric['date'] = date
                break
        
        # Сбрасываем режим редактирования
        self.cancel_edit()
        # Обновляем таблицу
        self.update_table()
    
    def delete_metric(self):
        """Удаление показателя"""
        if self.current_edit_id is None:
            return
            
        # Подтверждение удаления
        reply = QMessageBox.question(
            self, 'Подтверждение', 
            'Вы уверены, что хотите удалить этот показатель?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Удаляем показатель
            self.metrics = [m for m in self.metrics if m['id'] != self.current_edit_id]
            # Сбрасываем режим редактирования
            self.cancel_edit()
            # Обновляем таблицу
            self.update_table()
    
    def cancel_edit(self):
        """Отмена редактирования"""
        self.current_edit_id = None
        self.clear_inputs()
        self.add_button.setEnabled(True)
        self.edit_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.table.clearSelection()
    
    def table_row_selected(self, row):
        """Обработка выбора строки в таблице"""
        self.current_edit_id = int(self.table.item(row, 0).text())
        
        # Находим показатель
        for metric in self.metrics:
            if metric['id'] == self.current_edit_id:
                self.name_input.setText(metric['name'])
                self.value_input.setText(metric['value'])
                self.date_input.setText(metric['date'])
                break
        
        # Активируем кнопки редактирования
        self.add_button.setEnabled(False)
        self.edit_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        self.delete_button.setEnabled(True)
    
    def update_table(self):
        """Обновление таблицы с показателями"""
        self.table.setRowCount(len(self.metrics))
        
        for row, metric in enumerate(self.metrics):
            self.table.setItem(row, 0, QTableWidgetItem(str(metric['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(metric['name']))
            self.table.setItem(row, 2, QTableWidgetItem(metric['value']))
            self.table.setItem(row, 3, QTableWidgetItem(metric['date']))
    
    def clear_inputs(self):
        """Очистка полей ввода"""
        self.name_input.clear()
        self.value_input.clear()
        self.date_input.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MetricsTracker()
    window.show()
    sys.exit(app.exec_())