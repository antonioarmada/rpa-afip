from typing import Any, List, Optional, Union
import openpyxl
import os

class Planilla():

    def __init__(self, archivo, fin_encabezados) -> None:
        """
        - archivo: ruta de archivo
        - fin_encabezados: (int) ultima fila con encabezados, se saltean
        """
        self.archivo = archivo #self.buscar_xls(carpeta)
        self.fin_encabezados = fin_encabezados

        self.todos_los_items = self.recorrer_xls()

    
    def buscar_xls(self, carpeta):
        """
        No la uso desde que puse el file piccker.. 
        Busca el archivo xlsx mas reciente en la carpeta planilla
        Devuelve la ruta
        """
        archivos = os.listdir(carpeta)
        archivos.sort(key=lambda x: os.path.getmtime(os.path.join(carpeta, x)), reverse=True)

        if archivos:
            # Obtener la ruta relativa del archivo más reciente
            archivo_mas_reciente = archivos[0]
            ruta_relativa = os.path.join(carpeta, archivo_mas_reciente)

            print(f"Ruta relativa del archivo más reciente: {ruta_relativa}")
            return ruta_relativa
        else:
            print("No se encontraron archivos en la carpeta.")
            return None



    def recorrer_xls(self) -> List:

        print (f"---- leyendo XLS: {self.archivo} --------")

        contador = 0
        lista_de_items = []

        # Cargar el archivo .xlsx
        libro = openpyxl.load_workbook(self.archivo)
        hoja = libro.active

        # Recorrer filas en la hoja
        for fila in hoja.iter_rows(min_row= self.fin_encabezados, values_only=True):
            fecha_actual = fila[1]  # Columna B (según el índice 1)
            estado = fila[2]        # Columna C (según el índice 2)
            unidades = fila[5]
            if unidades:            # Si no está vacío
                unidades = int(unidades)
            else:
                continue
            valor_de_venta = fila[6]
            if valor_de_venta:            # Si no está vacío
                valor_de_venta = int(valor_de_venta)
            else:
                continue
            codigo_ML= fila[14]
            descripcion = fila[15]
            variante = fila[16]
            if estado.strip():      # Verifica si el string no está vacío después de eliminar los espacios en blanco
                print (fecha_actual,estado,valor_de_venta, unidades, codigo_ML, descripcion, variante)
                item = {
                        "fecha" : fecha_actual,
                        "estado" : estado,
                        "valor" : valor_de_venta,
                        "cantidad" : unidades,
                        "codigo" : codigo_ML,
                        "descripcion" : descripcion,
                        "variante" : variante
                        }
                lista_de_items.append(item)
                contador += 1
        print (f"---- se leyero {contador} del XLS --------")
        
        return lista_de_items