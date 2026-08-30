"""T2: contrato de invocación y código uno del uso incorrecto (RF-2, RF-3)."""

import pytest

from filepilot.cli import crear_analizador

# Fragmentos en inglés que `argparse` emitiría sin traducción (RNF-3).
RASTROS_EN_INGLES = (
    "usage:",
    "the following arguments",
    "unrecognized arguments",
    "invalid choice",
    "choose from",
    "ignored explicit argument",
    "expected one argument",
)

CASOS_DE_USO_INCORRECTO = [
    pytest.param([], "faltan argumentos obligatorios: orden", id="sin_subcomando"),
    pytest.param(["analizar"], "faltan argumentos obligatorios: ruta", id="sin_ruta"),
    pytest.param(
        ["analizar", ".", "--inexistente"],
        "argumentos no reconocidos: --inexistente",
        id="opcion_desconocida",
    ),
    pytest.param(["ordenar", "."], "valor no admitido para orden", id="subcomando_desconocido"),
    pytest.param(
        ["analizar", ".", "--recursivo=si"],
        "la opción --recursivo no admite un valor",
        id="opcion_con_valor",
    ),
]


@pytest.mark.parametrize("argumentos, causa", CASOS_DE_USO_INCORRECTO)
def test_uso_incorrecto_termina_en_uno(ejecutar_modulo, argumentos, causa, tmp_path):
    resultado = ejecutar_modulo(argumentos, tmp_path)

    assert resultado.returncode == 1, f"código inesperado con {argumentos}"
    assert resultado.stderr.startswith("uso: ")
    assert causa in resultado.stderr
    assert resultado.stdout == ""


@pytest.mark.parametrize("argumentos, causa", CASOS_DE_USO_INCORRECTO)
def test_diagnostico_en_espanol(ejecutar_modulo, argumentos, causa, tmp_path):
    """Ni la causa ni la línea de uso conservan el texto original en inglés."""
    resultado = ejecutar_modulo(argumentos, tmp_path)

    encontrados = [rastro for rastro in RASTROS_EN_INGLES if rastro in resultado.stderr]

    assert encontrados == [], f"salida de error en inglés con {argumentos}: {encontrados}"


def test_mensaje_sin_traduccion_conocida_no_deja_ingles():
    from filepilot.cli import MENSAJE_GENERICO, traducir_error

    assert traducir_error("some future argparse message") == MENSAJE_GENERICO


@pytest.mark.parametrize("argumentos", [["--help"], ["analizar", "--help"]])
def test_ayuda_termina_en_cero(ejecutar_modulo, argumentos, tmp_path):
    resultado = ejecutar_modulo(argumentos, tmp_path)

    assert resultado.returncode == 0
    assert "analizar" in resultado.stdout


def test_opciones_del_subcomando():
    """La ruta es obligatoria y las dos opciones están declaradas (RF-3, RF-14)."""
    opciones = crear_analizador().parse_args(["analizar", "carpeta"])

    assert opciones.ruta == "carpeta"
    assert opciones.recursivo is False
    assert opciones.incluir_ocultos is False

    completas = crear_analizador().parse_args(
        ["analizar", "carpeta", "--recursivo", "--incluir-ocultos"]
    )

    assert completas.recursivo is True
    assert completas.incluir_ocultos is True
