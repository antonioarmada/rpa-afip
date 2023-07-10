from flet_core.control import Control, OptionalNumber
from flet_core.ref import Ref
from flet_core.types import AnimationValue, ClipBehavior, OffsetValue, ResponsiveNumber, RotateValue, ScaleValue
from typing import Any, List, Optional, Union

import yaml
import os

import flet

from flet import (
    Checkbox,
    Column,
    FloatingActionButton,
    IconButton,
    OutlinedButton,
    Page,
    Row,
    Text,
    TextField,
    UserControl,
    colors,
    icons,
    ResponsiveRow,
    CrossAxisAlignment,
    ProgressBar,
    TextThemeStyle,
    ListView,
    AlertDialog,
    MainAxisAlignment,
    TextButton,
    FilePicker,FilePickerResultEvent, FilePickerUploadFile,
    ElevatedButton,
    Divider


)

from planilla import Planilla
from rpa import RPA

# ---------------------------------------   GUI   ---------------------------------------------------

class Venta(UserControl):
 

    def __init__(self, venta_desc, venta_precio, venta_cant, venta_codigo, venta_delete):
        super().__init__()
        self.descripcion = venta_desc
        self.cantidad = venta_cant
        self.precio = venta_precio
        self.codigo = venta_codigo
        self.borrar = venta_delete

    def build(self):
        self.mostrar_venta = Checkbox(
            value=True, label=f"{self.cantidad.value}x {self.descripcion} ({self.codigo}) = ${self.precio} ", on_change=None
        )

        return Column(controls=[self.mostrar_venta])

    def delete_clicked(self, e):
        # heredo la funcion de la clase facturadorApp y la ejecuta
        self.task_delete(self)



class facturadorApp(UserControl):   
    
    
    def build(self):
        
        """ with open("config.yaml", 'r') as archivo:
            self.configs = yaml.load(archivo, Loader=yaml.FullLoader)
        """

        self.es_test = True #self.configs["test"]

        self.rpa = RPA(self.es_test)

        self.index = 0
        self.pagina = 2
        item_leido_xls = None # diccionario
        self.nueva_fecha = Text(value="")
        self.nuevo_estado = Text(value= "")
        self.nuevo_codigo = Text(value= "")
        self.nuevo_unidades = TextField(value= "", hint_text="cant.") #  style="headlineMedium"
        self.nueva_desc = TextField(value= "", hint_text="descripción")
        self.nuevo_precio = TextField(value= "", hint_text="subtotal venta")

        self.progreso = ProgressBar(width=Page.width)
        self.progreso.value = 0
        self.progreso_texto = Text(value= "sin datos", style= TextThemeStyle.BODY_SMALL)

        self.progreso_facturacion = ProgressBar(width=Page.width)

        self.ventas =  ListView(spacing=10, padding=20, auto_scroll=True, height=300)

        self.estado_facturacion_titulo = Text (value="Esperando para iniciar...", style= TextThemeStyle.HEADLINE_LARGE)
        self.estado_facturacion_subtitulo = Text (value=f"Se van a hacer ... facturas") #value=f"Se van a hacer {len(self.planilla.todos_los_items)}

        self.btn_factuar = OutlinedButton(text="FACTURAR", on_click= self.open_dlg)

        self.pick_files_dialog = FilePicker(on_result=self.pick_files_result)
        self.selected_files = Text()

        self.txt_cuit = TextField(value= "27115910669", label="CUIT")
        self.txt_pass= TextField(value= "", label="Clave Fiscal")
        

        self.head_config= Column (visible= True, controls = [
                            self.pick_files_dialog,
                            Row(
                                [
                                    ElevatedButton(
                                        "Seleccionar XLS",
                                        icon=icons.UPLOAD_FILE,
                                        on_click=lambda _: self.pick_files_dialog.pick_files(
                                            allow_multiple=False
                                        ),
                                    ),
                                ]
                            ),
                            Row(
                                [self.selected_files,]
                            ),
                            Divider(height=9, thickness=2),
                            Row(
                                [self.txt_cuit,self.txt_pass ]
                            ),
                            Divider(height=9, thickness=2),
                            OutlinedButton(text="CONTINUAR", on_click= self.fin_config)

                            
        ]) 


        self.head_agregar = Column (visible= False, controls = [
                            
                        ResponsiveRow([
                            Column(col=1, controls=[self.nuevo_unidades]),
                            Column(col=9, controls=[self.nueva_desc]),
                            Column(col=2, controls=[self.nuevo_precio]),
                        ], vertical_alignment= CrossAxisAlignment.CENTER ),
                        ResponsiveRow([
                            Column(col=3, controls=[self.nueva_fecha],),
                            Column(col=4, controls=[self.nuevo_estado]),
                            Column(col=3, controls=[self.nuevo_codigo]),
                            Column(col=1, controls=[FloatingActionButton(icon=icons.DELETE_FOREVER_ROUNDED , bgcolor=colors.WHITE, on_click= self.saltar_item)]), # self.add_clicked
                            Column(col=1, controls=[FloatingActionButton(icon=icons.ADD, on_click=self.add_clicked , autofocus = True)])
                        ], vertical_alignment= CrossAxisAlignment.CENTER ), 

        ]) 

        self.dlg_modal = AlertDialog(
                        modal=True,
                        title=Text("Confirmame esto Cristina"),
                        #content= Text(f"¿Empezamos a hacer {len(self.index)} facturas? "),
                        actions=[
                            TextButton("Si", on_click=self.facturar),
                            TextButton("No", on_click=self.close_dlg),
                        ],
                        actions_alignment=MainAxisAlignment.END,
                        on_dismiss=lambda e: print("Modal dialog dismissed!"),
            )
        
        self.head_facturando = Column (visible= False, controls = [
                        self.estado_facturacion_titulo,
                        self.estado_facturacion_subtitulo,
                        OutlinedButton(text="CANCELAR", on_click= self.cancelar_facturacion)
                        ])

        pagina = Column(
            width=800,
            controls=[ 
                        self.dlg_modal, 
                        self.head_config,
                        self.head_agregar,
                        self.head_facturando,

                        ResponsiveRow( controls=[self.progreso, self.progreso_texto] ),

                        Column(
                                spacing=25,
                                controls=[
                                    self.ventas,
                                    Row(
                                        alignment="spaceBetween",
                                        vertical_alignment="center",
                                        controls=[
                                            #self.items_left,
                                            self.btn_factuar,
                                        ],
                                    ),
                                ],
                            ),
                    ]
                )
        
        return pagina
    
    
    

    def carga_inicial_items(self):
        item_leido_xls = self.planilla.todos_los_items[self.index] # diccionario
        self.nueva_fecha.value =item_leido_xls["fecha"]
        self.nuevo_estado.value = item_leido_xls["estado"]
        self.nuevo_codigo.value = item_leido_xls["codigo"]
        self.nuevo_unidades.value = item_leido_xls["cantidad"] #  style="headlineMedium"
        self.nueva_desc.value = item_leido_xls["descripcion"]
        self.nuevo_precio.value = item_leido_xls["valor"]

        self.progreso = ProgressBar(width=Page.width)
        self.progreso.value = 0
        self.progreso_texto = Text(value= f"{self.index} / {len(self.planilla.todos_los_items)}", style= TextThemeStyle.BODY_SMALL)

    def fin_config(self, e):
        self.carga_inicial_items()
        self.head_config.visible = False
        self.head_agregar.visible = True
        self.update()

    def pick_files_result(self, e: FilePickerResultEvent):
        
        archivo = "".join(map(lambda f: f.path, e.files))
        print (archivo)

        if archivo:
            #levanta los datos de XLS
            self.planilla= Planilla(archivo,4)
            self.selected_files.value = archivo
            #self.carga_inicial_items()
        else:
            archivo = "Cancelaste, tenes que seleccionar una planilla para seguir..."

        """
        self.selected_files.value = (
            ", ".join(map(lambda f: f.path, e.files)) if e.files else "Cancelled!"
        )
        """

        #self.selected_files.value = e.files[0]
        self.selected_files.update()

    
    """
    def resource_path(self,relative_path):
         en teoria esto arregla la direccion relativa cuando importaba los archivos
        luego de compilar macOS pero no está funcionando
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
        """

    def close_dlg(self,e):
            self.dlg_modal.open = False
            self.update()
        
    def open_dlg(self,e):
            modo = "INDEFINIDO"
            if self.es_test:
                modo = "TEST"
            else:
                modo = "REAL"
            self.dlg_modal.content= Text(f"¿Empezamos a hacer {len(self.ventas.controls)} facturas? en modo {modo} ")
            self.dlg_modal.open = True
            self.update()

    def add_clicked(self, e):
        if self.nueva_desc.value:
            #(self, venta_desc, venta_precio, venta_cant, venta_codigo, venta_delete):
            venta = Venta( self.nueva_desc.value,
                           self.nuevo_precio.value,
                           self.nuevo_unidades,
                           self.nuevo_codigo.value,
                           self.venta_delete)
            self.ventas.controls.append(venta)

            # Acatualizo el item a agregar con los datos del XLS
            self.actualizo_campos_item()

    def saltar_item(self,e):
        # Acatualizo el item a agregar con los datos del XLS
        self.actualizo_campos_item()

    def actualizo_campos_item(self):
        self.index +=1
        item_leido_xls = self.planilla.todos_los_items[self.index]
        self.nueva_fecha.value = item_leido_xls["fecha"]
        self.nuevo_estado.value = item_leido_xls["estado"]
        self.nuevo_codigo.value = item_leido_xls["codigo"]
        self.nuevo_unidades.value = item_leido_xls["cantidad"]
        self.nueva_desc.value = item_leido_xls["descripcion"]
        self.nuevo_precio.value = item_leido_xls["valor"]
        self.progreso.value = self.index / len(self.planilla.todos_los_items)
        self.progreso_texto.value = f"{self.index} / {len(self.planilla.todos_los_items)}"
        self.update()

    def venta_delete(self, venta):
        self.ventas.controls.remove(venta)
        self.update()
    
    def facturar(self, e):
        #ventas_a_facturar = []
        #datos_venta_confirmados = []
        self.dlg_modal.open = False
        self.btn_factuar.visible = False
        self.head_agregar.visible = False
        self.head_facturando.visible = True
        self.progreso.value = None
        self.progreso_texto.value = f"0 / {len(self.ventas.controls)}"
        self.update()
        print ("////////////// --  FACTURANDO --  //////////////")

        # proceso RPA en Afip
        
        # Login
        try: 
            usuario = self.txt_cuit.value
            password = self.txt_pass.value
            self.estado_facturacion_titulo.value= "Ingresando al AFIP"
            self.estado_facturacion_subtitulo.value = f"CUIT: {usuario}"
            super().update()
            self.rpa.login(usuario , password)
        except Exception as e:
            self.estado_facturacion_titulo.value = "ERROR!"
            self.estado_facturacion_subtitulo.value = f"Error: {e}"
            super().update()
        else:
            self.estado_facturacion_titulo.value = "Login exitoso"
            super().update()

        # Hacer una factura
        self.progreso.value = 0
        super().update()
        i = 0
        i_ok =0 
        for venta in self.ventas.controls:
            i += 1
            if venta.mostrar_venta.value: # si el checkbox esta tildado
                cantidad = venta.cantidad.value
                descripcion = f"{venta.descripcion} ({venta.codigo})"
                precio = venta.precio
                try:
                    self.estado_facturacion_titulo.value = "Facturando"
                    self.estado_facturacion_subtitulo.value = f"{cantidad}x {descripcion} = {precio}"
                    super().update()
                    self.rpa.hacer_una_factura(cantidad,descripcion, precio)
                except Exception as e:
                    self.estado_facturacion_titulo.value = "ERROR!"
                    self.estado_facturacion_subtitulo.value = f"Error: {e}"
                    super().update()
                else:
                     venta.mostrar_venta.value = False # para que se muestre sin el tilde en la lista
                     self.progreso.value = i / len(self.ventas.controls)
                     self.progreso_texto.value = f"{i} / {len(self.ventas.controls)}"
                     i_ok += 1
                     super().update()

        self.estado_facturacion_titulo.value = "Finalizado"
        self.estado_facturacion_subtitulo.value = f"Se realizaron {i_ok} facturas"
        self.update()
        self.rpa.cerrar()


    def cancelar_facturacion(self,e):
        self.rpa.cerrar()
        self.estado_facturacion_titulo.value = "CANCELADO"
        self.update()
        
    def update(self):
        super().update()



# ---------------------------------------   MAIN   ---------------------------------------------------

def main(page: Page):
    page.title = "Facturador IMPULSO"
    page.horizontal_alignment = "center"
    page.scroll = "adaptive"
    page.padding = 30
    page.update()

    # create application instance
    app = facturadorApp()

    # add application's root control to the page
    page.add(app)
    


flet.app(target=main, assets_dir="assets", upload_dir="assets/uploads")  # 
# https://stackoverflow.com/questions/75571138/flet-paking-into-macos-application 
# page.add(ft.Image(src="/uploads/<some-uploaded-picture.png>"))