# Aplicacion que gestionara la logica de un conversor de monedas conectada a una api
# ---------------------------------------------------------------------------------
# Imports necesarios para el funcionamiento de la aplicacion
import sys,requests,json,recursos,logging
from PyQt5.QtWidgets import(QApplication, QMessageBox, QMainWindow, QListWidgetItem)
from PyQt5.QtGui import QIcon
from ventanaPrincipal import Ui_MainWindow
# ---------------------------------------------------------------------------------
# Configuracion que usaremos en nuestro archivo .log
logging.basicConfig(filename='currency-exchange.log',
                    filemode='w',format='%(asctime)s : %(levelname)s : %(message)s',
                    datefmt='%d/%m/%y %H:%M:%S',
                    level=logging.ERROR
                        )
# --------------------------------------------------------------------------------- 
# Clase que gestionara las vistas de la aplicaion. 
# Esta cargara los datos recibidos de la clase Datos y los introducira en las vistas
class Ventana(QMainWindow, Ui_MainWindow):
# Inicio de la clase, atributos:
# listMonedas = List;codigoMonedas= list
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.listaMonedas=[]
        self.codigoMonedas=[]
        self.datos=Datos()
        self.cargarDatosMonedas()
        self.conexionSenyales()
# --------------------------------------------------------------------------------- 
# Metodos de la clase que cargaran los datos  
    #Metodo que cargara los datos en las vistas
    def cargarDatosMonedas(self):
        self.listaMonedas=self.datos.listaDeMonedas()
        if self.listaMonedas!=None:
            nombreMoneda=[]
            #recojemos los datos de todas las monedas y guardamos el codigo de moneda junto con su nombre para poder cargalo en los comboBoxes
            for nombre in self.listaMonedas:
                nombreMoneda.append(self.listaMonedas[nombre]['currency_name'])
                self.codigoMonedas.append(nombre)
            # rellenamos los comboBoxes con los datos
            self.rellenarComboBox(nombreMoneda,self.conversorMonedas)
            self.rellenarComboBox(nombreMoneda,self.cambioMonedas)
            self.rellenarComboBox(nombreMoneda,self.costeBase)
            self.rellenarComboBox(nombreMoneda,self.costeFechMoneda)
        else:
            self.msgError("No se pudo cargar los datos Iniciales")
            logging.error("Clase Ventana - No se pudo cargar comboBox por la conexion a la api")
    # --------------------------------------------------------------------------------- 
    # Metodo para cargar los datos en la ventana de Coste divisas en este momento
    def cargarDatosActual(self):
        self.costeList.clear()
        if self.codigoMonedas!=[]:
            precioMonedasActual=self.datos.listaMonedasActuales(self.codigoMonedas[self.costeBase.currentIndex()])
            if precioMonedasActual!=None:
                self.rellenarLista(precioMonedasActual,self.costeList)
            else:
                self.msgError("No se pudo cargar el listado de precios")
                logging.error("Clase Ventana - El listado de precios esta vacio")
        else:
            self.msgError("No hay datos de monedas")
            logging.error("Clase Ventana - No se pudo cargar comboBox por la conexion a la api")
    # --------------------------------------------------------------------------------- 
    # Metodo para cargar los datos en la ventana de Coste divisas en una fecha
    def cargarDatosFecha(self):
        self.costeFechLista.clear()
        anyo=str(self.costeFechFecha.date().year())
        mes=self.comprobarMesDia(self.costeFechFecha.date().month())
        dia=self.comprobarMesDia(self.costeFechFecha.date().day())
        fecha=(anyo+"-"+mes+"-"+dia)
        if self.codigoMonedas!=[]:
            precioMonedasFecha=self.datos.consultaMonedaFecha(self.codigoMonedas[self.costeBase.currentIndex()],fecha)
            if precioMonedasFecha!=None:
                self.rellenarLista(precioMonedasFecha,self.costeFechLista)
            else:
                self.msgError("No se pudo cargar el listado de precios")
                logging.error("Clase Ventana - El listado de precios esta vacio")
        else:
            self.msgError("No hay dato de las monedas")
            logging.error("Clase Ventana - No se pudo cargar comboBox por la conexion a la api")
    # --------------------------------------------------------------------------------- 
    #Metodo para convertir el dinero de la moneda base indicada a la que se quiere convertir 
    def convertirMonedas(self):
        if self.codigoMonedas!=[]:
            cantidad=self.conversorDinero.text()
            if cantidad.isdigit():
                if float(cantidad)>0:
                    monedaBase=self.codigoMonedas[self.conversorMonedas.currentIndex()]
                    monedaCambio=self.codigoMonedas[self.cambioMonedas.currentIndex()]
                    valor=self.datos.cambioMonedas(monedaBase,monedaCambio,cantidad)
                    if valor!=None:
                        self.cambioDinero.setText(str(valor))
                    else:
                        self.msgError("No se pudo realizar la conversion")
                        logging.error("Clase Ventana - Ocurrio un error en la api")
                else:
                    self.msgError("Introduzca un valor mallor de 0")
                    logging.error("Clase Ventana - El valor introducido no pude ser menor de 0")
            else:
                self.msgError("Introduzca valores correctos")
                logging.error("Clase Ventana - El valor introducido fue un str, debe ser un numero")
        else:
            self.msgError("No hay datos de las monedas")
            logging.error("Clase Ventana - No se pudo cargar comboBox por la conexion a la api")
    # --------------------------------------------------------------------------------- 
    #metodo que conectara los elementos a las acciones
    def conexionSenyales(self):
        #botones
        self.convertirPrincipal.pressed.connect(self.convertirMonedas)
        self.costeMostrar.pressed.connect(self.cargarDatosActual)
        self.costeFechMostrar.pressed.connect(self.cargarDatosFecha)
# --------------------------------------------------------------------------------- 
# Metodos Que rellenaran los elementos usados para cargarlos en la vista
    # metodo para rellenar los datos de los comboBoxes en el que se recibira los datos a rellenar y el comboBox que hace referencia
    def rellenarComboBox(self,nombreMoneda,comboBox):
         # juntamos los nombres con los codigos y lo añadimos al comboBox para construirlo
        for i in range(len(nombreMoneda)):
            comboBox.addItem(QIcon(":/iconos/"+self.codigoMonedas[i]+".png" ),"-"+self.codigoMonedas[i]+"-"+nombreMoneda[i])
    # --------------------------------------------------------------------------------- 
    # Metodo para rellenar los datos de las ListItem
    def rellenarLista(self,precioMonedas,listItem):
        # creamos un array para recojer el codigo de las monedas y lo recorremos para llenarlo
        nombreMoneda=[]
        for nombre in precioMonedas.keys():
            nombreMoneda.append(nombre)
        # recorremos el array de los nombres de los codigos de las monedas para poder inserar una a una en el ListBox los valores 
        for i in range(len(nombreMoneda)):
            listItem.insertItem(i,nombreMoneda[i]+"-"+str(precioMonedas[nombreMoneda[i]]))
    # --------------------------------------------------------------------------------- 
    # Metodo para comprobar si el dia o el mes es menor que 10 para asi poder crear un formato de fecha correcto
    def comprobarMesDia(self,digito):
        if digito<10:
            digito=str(digito)
            digito="0"+digito
            return digito
        else:
            return str(digito)
# --------------------------------------------------------------------------------- 
# Metodo para a gestion de errores de la clase Ventana
    def msgError(self,mensajeErr):
        mensaje=QMessageBox()
        mensaje.setIcon(QMessageBox.Warning)
        mensaje.setInformativeText(mensajeErr)
        mensaje.setWindowTitle("Error")
        mensaje.exec_()
# --------------------------------------------------------------------------------- 
# Clase Datos
class Datos():
    # Inicio de la clase con atributos:
    # apiKey=str;appName=str
    def __init__(self):
        self.apiKey=""
        self.appName=""
        self.cargarEnv(".env")
# --------------------------------------------------------------------------------- 
# Metodos de la clase
    #cargaremos las variables del fichero .env a las variables locales para el uso    
    def cargarEnv(self,ruta_Fichero):
        f=open(ruta_Fichero,"r")
        try:
            filas=f.readlines()
            nameIndex=filas[0].find("=")+1
            self.appName=filas[0][nameIndex:]
            keyIndex=filas[1].find("=")+1
            self.apiKey=filas[1][keyIndex:]  
        finally:
            f.close()
# --------------------------------------------------------------------------------- 
# Metodos que devolveran listas o dist para la gestion en las vistas   
    # Metodo que devolvera un listado con los datos de todas las monedas de la API   
    def listaDeMonedas(self):
        url="https://api.currencyscoop.com/v1/currencies?api_key="+self.apiKey
        try:
            resp=requests.get(url=url)
            self.data=resp.json()
            if self.data['meta']['code']==200:
                listaMonedas=self.data['response']['fiats']
                return listaMonedas
            else:
                self.mensajeError(self.data['meta']['code'])
        except:
            self.mensajeError("1")
    # --------------------------------------------------------------------------------- 
    # Metodo que devolvera un listado con el coste de todas las monedas actualizado en base a una moneda
    def listaMonedasActuales(self,monedaBase):
        url="https://api.currencyscoop.com/v1/latest?base="+monedaBase+"&api_key="+self.apiKey
        try:
            resp=requests.get(url=url)
            self.data=resp.json()
            if self.data['meta']['code']==200:
                precioActual=self.data['response']['rates']
                return precioActual
            else:
                self.mensajeError(self.data['meta']['code'])
        except:
            self.mensajeError(1)
    # --------------------------------------------------------------------------------- 
    # Metodo que devolvera un listado con el coste de todas las monedas en esa fecha en base a una moneda en concreto
    def consultaMonedaFecha(self,monedaBase,fechaConsulta):
        url="https://api.currencyscoop.com/v1/historical?base="+monedaBase+"&date="+fechaConsulta+"&api_key="+self.apiKey
        try:
            resp=requests.get(url=url)
            self.data=resp.json()
            if self.data['meta']['code']==200:
                preciosMoneda=self.data['response']['rates']
                return preciosMoneda
            else:
                self.mensajeError(self.data['meta']['code'])
        except:
           self.mensajeError(1)
    # --------------------------------------------------------------------------------- 
    # Metodo que reciviendo la moneda base y la moneda de cambio 
    # con la cantidad devolvera el valor del cambio
    def cambioMonedas(self,monedaBase,monedaCambio,cantidad):
        url="https://api.currencyscoop.com/v1/convert?from="+monedaBase+"&to="+monedaCambio+"&amount="+cantidad+"&api_key="+self.apiKey
        try:
            resp=requests.get(url=url)
            self.data=resp.json()
            if self.data['meta']['code']==200:
                cambio=self.data['response']['value']
                return cambio
            else:
                self.mensajeError(self.data['meta']['code'])
        except:
           self.mensajeError(1)
    # --------------------------------------------------------------------------------- 
    # Metodo que gestionara los errores de conexion de la aplicaion con la api
    def mensajeError(self,codigoError):
        #Errores de http
        if codigoError== 401:
            logging.error("Clase Datos - Token de API no autorizado faltante o incorrecto en el encabezado.")
        elif codigoError== 422:
            logging.error("Clase Datos - Entidad no procesable, lo que significa que algo con el mensaje no es correcto")
        elif codigoError== 500:
            logging.error("Clase Datos - Error interno del servidor")
        elif codigoError== 503:
            logging.error("Clase Datos - Servicio no disponible Durante las interrupciones del servicio planificadas")
        elif codigoError== 429:
            logging.error("Clase Datos - Demasiadas solicitudes. Se alcanzaron los límites de API.")
        #Errores de api
        elif codigoError== 600:
            logging.error("Clase Datos - Mantenimiento: la API de Currencyscoop está fuera de línea para su mantenimiento.")
        elif codigoError== 601:
            logging.error("Clase Datos - Token de API no autorizado faltante o incorrecto.")
        elif codigoError== 602:
            logging.error("Clase Datos - Parámetros de consulta no válidos.")
        elif codigoError== 603:
            logging.error("Clase Datos - Se requiere un nivel de suscripción autorizado.")
        elif codigoError== 1:
            logging.error("Clase Datos - No se pude realizar la peticion a la api")
            
# --------------------------------------------------------------------------------- 
if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setStyleSheet(open("styles.qss", "r").read())
    gui = Ventana()
    gui.show()
    sys.exit(app.exec())