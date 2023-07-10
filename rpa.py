from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


class RPA():

    def __init__(self, test= True) -> None:
       "Test: (bool: True) realiza casi todo el proceso, se detiene antes de confirmar la factura"
       self.es_test= test

    def login(self,usuario, password):

        # Configura el controlador de Selenium (en este caso, ChromeDriver)
        self.driver = webdriver.Chrome()

        # Abre una página web
        self.driver.get("https://auth.afip.gob.ar/contribuyente_/login.xhtml")

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

       # Ejecuta el código JavaScript para enfocar el campo de entrada de texto
        script = "$('input[id=\\'F1:username\\']').focus();"
        self.driver.execute_script(script)

        # aparece para poner la CUIT y lO completa   
        campo_CUIT = self.driver.find_element("id", "F1:username")
        campo_CUIT.send_keys(usuario)
        siguiente_cuit = self.driver.find_element(By.ID, "F1:btnSiguiente") #"F1:password"
        self.driver.execute_script("arguments[0].click();", siguiente_cuit)

        # aparece para poner la contrasena y la completa
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        campo_contrasena = self.driver.find_element(By.ID, "F1:password")
        campo_contrasena.send_keys(password)

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        siguiente_clave = self.driver.find_element(By.ID, "F1:btnIngresar") 
        self.driver.execute_script("arguments[0].click();", siguiente_clave)

        self.driver.implicitly_wait(3)

        # buscar el link de comprobantes en linea, voy asi porque no encuentro donde generar el id de sesion
        self.driver.get("https://portalcf.cloud.afip.gob.ar/portal/app/mis-servicios")
        # uso javascript porque el elemento está oculto al principio
        link_rcel = self.driver.find_element(By.CSS_SELECTOR, 'a[title="rcel"]')
        self.driver.execute_script("arguments[0].click();", link_rcel)
        self.driver.implicitly_wait(2)

        # Obtener todos los identificadores de ventana
        window_handles = self.driver.window_handles

        sleep(5) # importante mantener el sleep

        print(len(window_handles))

        # Obtiene los identificadores de todas las pestañas abiertas
        ventanas = self.driver.window_handles

        # Cambia el enfoque a la nueva pestaña (la última en la lista de ventanas)
        self.driver.switch_to.window(ventanas[-1])

        print(self.driver.title)

        # Obtén los identificadores y títulos de todas las pestañas abiertas
        ventanas = self.driver.window_handles
        titulos = self.driver.window_handles

        # Busca la pestaña con el título deseado
        titulo_deseado = "RCEL"

        # cambia a la pestaña
        for ventana, titulo in zip(ventanas, titulos):
            self.driver.switch_to.window(ventana)
            if self.driver.title == titulo_deseado:
                break
        
        print(self.driver.title)

        #self.driver.implicitly_wait(2)

    def hacer_una_factura(self, cantidad, descripcion, precio):
        """
        Ya estoy en el facturador
        """
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "btn_empresa")))

        boton_empresa = self.driver.find_element(By.CLASS_NAME, "btn_empresa")
        boton_empresa.click()

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "btn_gen_cmp")))

        self.boton_generar = self.driver.find_element(By.ID, "btn_gen_cmp")
        self.boton_generar.click()

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "puntodeventa")))

        # Localiza el elemento select
        selector =  self.driver.find_element(By.ID, "puntodeventa")
        # Crea un objeto Select a partir del elemento select
        select = Select(selector)
        select.select_by_value("6")

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "universocomprobante")))

        # Localiza el elemento select
        selector =  self.driver.find_element(By.ID, "universocomprobante")
        select = Select(selector)
        select.select_by_value("19")

        self.driver.implicitly_wait(1)

        # Localiza el elemento input
        input_element = self.driver.find_element("xpath", "//input[@type='button' and @value='Continuar >']")
        input_element.click()

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "idconcepto")))

        # Localiza el elemento select
        selector =  self.driver.find_element(By.ID, "idconcepto")
        select = Select(selector)
        select.select_by_value("1")

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "actiAsociadaId")))

        # Localiza el elemento select
        selector =  self.driver.find_element(By.ID, "actiAsociadaId")
        select = Select(selector)
        select.select_by_value("152011")

        self.driver.implicitly_wait(1)

        # Localiza el elemento input
        input_element = self.driver.find_element("xpath", "//input[@type='button' and @value='Continuar >']")
        input_element.click()

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "idivareceptor")))

        # Localiza el elemento select
        selector =  self.driver.find_element(By.ID, "idivareceptor")
        select = Select(selector)
        select.select_by_value("5")

        checkbox = self.driver.find_element("xpath", "//label[contains(text(), 'Contado')]")
        checkbox.click()

        # Localiza el elemento input
        input_element = self.driver.find_element("xpath", "//input[@type='button' and @value='Continuar >']")
        input_element.click()


        # ACA EMPIEZO A HACER LAS FACTURAS  ---------------------------------------------------------------------

        campo_descripcion = self.driver.find_element(By.ID, "detalle_descripcion1")
        campo_descripcion.send_keys(descripcion)

        campo_cantidad = self.driver.find_element(By.ID, "detalle_cantidad1")
        campo_cantidad.clear()  # Borra el contenido actual del campo de texto
        campo_cantidad.send_keys(cantidad)

        # Localiza el elemento select
        selector =  self.driver.find_element(By.ID, "detalle_tipo_iva1")
        select = Select(selector)
        select.select_by_value("5") 

        campo_descripcion = self.driver.find_element(By.ID, "detalle_precio1")
        campo_descripcion.send_keys(precio)

        input_element = self.driver.find_element("xpath", "//input[@type='button' and @value='Continuar >']")
        input_element.click()

        sleep(2)

        # si no estamos en modo TEST reamente hago la factura
        if self.es_test == False:
            """
            #ATENCIÓN: confirmar datos ACA YA SE GENERA LA FACTURA
            <input type="button" value="Confirmar Datos..." onclick="confirmar();" style="width:150px;" id="btngenerar">
            """
            boton_confirmar = driver.find_element("id", "btngenerar")
            boton_confirmar.click()

            sleep (5) # sacar luego, es para ver que pasa con el popup
            self.driver.switch_to.alert.accept()
            sleep (2) # sacar luego, es para ver que pasa con el popup

            # aparece este boton que estaba oculto para imprimir el comprobante
            #<input type="button" value="Imprimir..." onclick="parent.location.href='imprimirComprobante.do?c='+idComprobante;" style="width:150px;font-weight:bold;">
            boton_imprimir = driver.find_element("xpath", "//input[@value='Imprimir...']")
            boton_imprimir.click()
        
        # vuelve a empezar
        self.driver.get("https://fe.afip.gob.ar/rcel/jsp/index_bis.jsp")



    def cerrar(self):
        # Cierra el navegador
        self.driver.quit()
