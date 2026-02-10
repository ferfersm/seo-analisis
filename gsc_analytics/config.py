"""
Módulo de configuración para GSC Analytics.
Permite definir configuraciones específicas por cliente de manera flexible.
"""

from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field


@dataclass
class ConfigGSC:
    """
    Configuración flexible para análisis GSC.
    
    Attributes:
        cliente: Nombre del cliente
        marcas: Diccionario con grupos de palabras clave por marca/categoría
        keywords_importantes: Lista de términos importantes a trackear
        dimensiones: Columnas a analizar ('query', 'page', o ambas)
        columna_fecha: Nombre de la columna de fecha
        columna_metricas: Diccionario mapeando nombres estándar a columnas del df
    """
    
    cliente: str = "cliente_generico"
    marcas: Dict[str, List[str]] = field(default_factory=dict)
    keywords_importantes: List[str] = field(default_factory=list)
    dimensiones: List[str] = field(default_factory=lambda: ['query'])
    columna_fecha: str = 'date'
    columna_metricas: Dict[str, str] = field(default_factory=lambda: {
        'clicks': 'clicks',
        'impressions': 'impressions',
        'ctr': 'ctr',
        'position': 'position'
    })
    
    def __post_init__(self):
        """Validación post-inicialización."""
        dims_validas = {'query', 'page'}
        for dim in self.dimensiones:
            if dim not in dims_validas:
                raise ValueError(f"Dimensión '{dim}' no válida. Use: {dims_validas}")
    
    @property
    def todas_marcas(self) -> List[str]:
        """Retorna lista plana de todas las palabras de marca."""
        return [
            kw.lower() 
            for grupo in self.marcas.values() 
            for kw in grupo
        ]
    
    @property
    def brand_map(self) -> Dict[str, str]:
        """Crea mapeo palabra_clave -> nombre_grupo."""
        return {
            kw.lower(): grupo
            for grupo, kws in self.marcas.items()
            for kw in kws
        }
    
    def obtener_grupo(self, texto: str) -> Optional[str]:
        """Determina a qué grupo pertenece un texto (query o URL)."""
        texto_lower = texto.lower()
        for grupo, kws in self.marcas.items():
            for kw in kws:
                if kw.lower() in texto_lower:
                    return grupo
        return None
    
    def es_marca(self, texto: str) -> bool:
        """Verifica si un texto contiene términos de marca."""
        return self.obtener_grupo(texto) is not None
    
    def es_importante(self, texto: str) -> bool:
        """Verifica si un texto contiene keywords importantes."""
        texto_lower = texto.lower()
        return any(kw.lower() in texto_lower for kw in self.keywords_importantes)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ConfigGSC':
        """Crea configuración desde diccionario."""
        return cls(**config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte configuración a diccionario."""
        return {
            'cliente': self.cliente,
            'marcas': self.marcas,
            'keywords_importantes': self.keywords_importantes,
            'dimensiones': self.dimensiones,
            'columna_fecha': self.columna_fecha,
            'columna_metricas': self.columna_metricas
        }


# Configuraciones predefinidas como ejemplos
CONFIG_EJEMPLO_TRANSBANK = ConfigGSC(
    cliente='transbank',
    marcas={
        'tbk': [
            "tansbank", "tbk", "tramsbank", "tranasbank", "tranbank", "trans bank",
            "transabank", "transabnk", "transank", "transb", "transbabk", "transbak",
            "transban", "transbanc", "transbanck", "transbank", "transbnk", "transkbank",
            "trasbank", "trasnbank", "trnasbank", "teansbank"
        ],
        'webpay': ["webpay", "web pay", "web pay plus"],
        'onepay': ["onepay", "one pay", "one click", "one clic", "oneclick", "oneclic"],
        'redcompra': ["redcompra", "red compra", "red bank", "redbank"],
        'conversion': [
            "cobra con tarjeta de credito", "cobrar con tarjeta", "cobrar con tarjeta de crédito",
            "maquina para pagar con tarjeta", "comprar maquina redcompra", "comprar pos",
            "gestion pos", "maquina de debito", "maquina debito", "maquina pagar tarjeta",
            "maquina pago", "maquina pago con tarjeta", "maquina pago tarjeta",
            "maquina para cobrar con tarjeta", "maquina para cobrar con tarjeta de credito",
            "maquina pos", "maquina tarjeta de credito", "maquina tarjetas de credito",
            "maquinas de pago con tarjeta", "maquinas pago con tarjetas",
            "maquinas para pagar con tarjeta", "mobile pos", "mobile pos system", "mpos",
            "máquina para pagar con tarjeta transbank", "máquina redcompra",
            "pagar con tarjeta de debito", "pago con tarjeta", "pago con tarjeta de credito",
            "pago con tarjeta maquina", "pago movil", "pago por tarjeta", "pago sin contacto",
            "plataforma de pago", "pos de pago", "pos de venta", "pos machine",
            "pos minimarket", "pos para restaurantes", "pos para ventas", "pos punto de venta",
            "pos restaurante", "pos tarjeta", "pos terminal", "punto de venta para cafeteria",
            "punto de venta para negocio", "punto de venta para negocios pequeños",
            "puntos de venta para restaurantes", "sistema de cobro para negocio",
            "sistema de cobro para tienda", "sistema de pago movil", "sistema pago con tarjeta",
            "sistema pago movil", "sistema pos", "sistema pos caja registradora",
            "sistema pos para restaurantes", "sistema pos punto de venta", "sistema punto de venta",
            "sistema redcompra", "sistemapos", "sistemas de pago", "sistemas de punto de ventas",
            "smart pos terminal", "software de punto de venta", "software para punto de venta",
            "software punto de venta", "software punto de venta restaurante", "terminal de pago",
            "terminal punto de venta"
        ]
    },
    keywords_importantes=[
        "maquina para pagar con tarjeta", "maquina de pago con tarjeta", "maquina pago tarjeta",
        "maquina para pagar con tarjeta banco estado", "pago con tarjeta maquina",
        "maquina pago con tarjeta", "maquina para pagar con tarjeta visa",
        "comprar maquina para pagar con tarjeta", "maquina para pagar con tarjeta portatil",
        "codigo qr mercado pago", "pagar con qr", "pago qr banco estado",
        "pagar con codigo qr", "pago por qr", "pago qr mercadopago",
        "que es pagar con qr", "como pagar con codigo qr mercadopago",
        "mercado pago pagar con qr", "donde pagar con codigo qr", "como cobrar con codigo qr",
        "link de pago", "link de pago transbank", "link de pago webpay",
        "link de pago mercadopago", "transbank link de pago",
        "comision link de pago mercadopago", "crear link de pago paypal",
        "cuanto cobra mercado pago por link de pago", "cuál es el código de pago link",
        "generar link de pago mercadopago", "link de pago paypal", "paypal link de pago",
        "que es un link de pago", "tips para vender por redes sociales",
        "como vender por redes sociales pdf", "como vender por redes sociales",
        "como vender productos por redes sociales", "como vender un producto por redes sociales",
        "vender por las redes sociales", "vender por redes sociales", "vender rapido por internet",
        "plataformas de pago online", "plataformas de pago online chile",
        "pasarelas de pago online", "cobro con tarjeta de credito por internet"
    ],
    dimensiones=['query', 'page']
)
