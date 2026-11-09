import unittest
from wordmoth import normalizar, validar_fecha, validar_telefono, extraer_anclas, PerfilWiFi

class TestWordMoth(unittest.TestCase):

    def test_normalizar(self):
        self.assertEqual(normalizar("CARLOS"), "carlos")
        self.assertEqual(normalizar("  María  "), "maria")
        self.assertEqual(normalizar(""), "")

    def test_validar_fecha(self):
        self.assertEqual(validar_fecha("1990-05-15"), "1990-05-15")
        self.assertEqual(validar_fecha("15/05/1990"), "1990-05-15")
        self.assertIsNone(validar_fecha("fecha_mala"))

    def test_validar_telefono(self):
        self.assertEqual(validar_telefono("1234"), "1234")
        self.assertEqual(validar_telefono("12-34"), "1234")
        self.assertEqual(validar_telefono("123"), "")

    def test_extraer_anclas(self):
        p = PerfilWiFi()
        p.ssid = "MOVISTAR_4521"
        p.fecha_nacimiento = "1990-05-15"
        p.telefono = "7890"
        
        anclas = extraer_anclas(p)
        self.assertIn("4521", anclas)
        self.assertIn("1990", anclas)
        self.assertIn("1505", anclas)
        self.assertIn("7890", anclas)

if __name__ == '__main__':
    unittest.main()
