"""UAdeC home institution catalog (Unidades, faculties, licenciaturas).

Sourced from uadec.mx/licenciaturas and uadec.mx/admisiones (union of admission cycles).
"""

from __future__ import annotations

from typing import Any

# Keyed by Unidad name (Sureste, Laguna, Norte).
UADEC_CATALOG: dict[str, tuple[dict[str, Any], ...]] = {
    "Sureste": (
        {
            "name": "Facultad de Artes Plásticas “Profesor Rubén Herrera”",
            "code": "sureste_artes_plasticas",
            "programs": (
                ("Licenciatura en Diseño Gráfico", "diseno_grafico"),
                ("Licenciatura en Artes Plásticas", "artes_plasticas"),
            ),
        },
        {
            "name": "Facultad de Ciencia, Educación y Humanidades",
            "code": "sureste_ciencia_educacion",
            "programs": (
                ("Licenciatura en Ciencias de la Educación", "ciencias_educacion"),
                ("Licenciatura en Letras Españolas", "letras_espanolas"),
                ("Licenciatura en Formación y Organización Deportiva", "formacion_deportiva"),
            ),
        },
        {
            "name": "Facultad de Ciencias de la Comunicación",
            "code": "sureste_comunicacion",
            "programs": (("Licenciatura en Ciencias de la Comunicación", "ciencias_comunicacion"),),
        },
        {
            "name": "Facultad de Ciencias Sociales",
            "code": "sureste_ciencias_sociales",
            "programs": (("Licenciatura en Historia", "historia"),),
        },
        {
            "name": "Escuela Superior de Música",
            "code": "sureste_musica",
            "programs": (("Licenciatura en Música", "musica"),),
        },
        {
            "name": "Facultad de Trabajo Social",
            "code": "sureste_trabajo_social",
            "programs": (("Licenciatura en Trabajo Social", "trabajo_social"),),
        },
        {
            "name": "Facultad de Ciencias de la Administración",
            "code": "sureste_administracion",
            "programs": (
                ("Licenciatura en Contaduría", "contaduria"),
                ("Licenciatura en Negocios Internacionales", "negocios_intl"),
                ("Licenciatura en Administración de Empresas", "admin_empresas"),
                ("Licenciatura en Administración de Recursos Humanos", "admin_rrhh"),
            ),
        },
        {
            "name": "Facultad de Economía",
            "code": "sureste_economia",
            "programs": (("Licenciatura en Economía", "economia"),),
        },
        {
            "name": "Facultad de Jurisprudencia",
            "code": "sureste_jurisprudencia",
            "programs": (("Licenciatura en Derecho", "derecho"),),
        },
        {
            "name": "Facultad de Mercadotecnia",
            "code": "sureste_mercadotecnia",
            "programs": (("Licenciatura en Mercadotecnia", "mercadotecnia"),),
        },
        {
            "name": "Facultad de Ingeniería",
            "code": "sureste_ingenieria",
            "programs": (
                ("Ingeniería Civil", "ing_civil"),
                ("Ingeniero Mecánico Administrador", "ing_mec_admin"),
                ("Ingeniería Mecánica Electricista", "ing_mec_elec"),
            ),
        },
        {
            "name": "Facultad de Sistemas",
            "code": "sureste_sistemas",
            "programs": (
                ("Ingeniería Automotriz", "ing_automotriz"),
                ("Ingeniería en Sistemas Computacionales", "ing_sistemas"),
                ("Ingeniería Industrial y de Sistemas", "ing_ind_sistemas"),
                ("Ingeniería en Robótica y Sistemas Inteligentes", "ing_robotica"),
            ),
        },
        {
            "name": "Facultad de Ciencias Químicas",
            "code": "sureste_quimicas",
            "programs": (
                ("Ingeniería Química", "ing_quimica"),
                ("Licenciatura Químico Industrial", "quimico_industrial"),
                ("Licenciatura Químico Farmacobiólogo", "quimico_farmaco"),
            ),
        },
        {
            "name": "Facultad de Arquitectura",
            "code": "sureste_arquitectura",
            "programs": (("Licenciatura en Arquitectura", "arquitectura"),),
        },
        {
            "name": "Facultad de Ciencias Físico Matemáticas",
            "code": "sureste_fisico_matematicas",
            "programs": (
                ("Licenciatura en Matemáticas Aplicadas", "matematicas_aplicadas"),
                ("Ingeniería Física", "ing_fisica"),
            ),
        },
        {
            "name": "Facultad de Medicina",
            "code": "sureste_medicina",
            "programs": (("Médico Cirujano", "medico_cirujano"),),
        },
        {
            "name": "Facultad de Odontología",
            "code": "sureste_odontologia",
            "programs": (("Licenciatura en Cirujano Dentista", "cirujano_dentista"),),
        },
        {
            "name": "Facultad de Psicología",
            "code": "sureste_psicologia",
            "programs": (("Licenciatura en Psicología", "psicologia"),),
        },
        {
            "name": "Facultad de Enfermería y Nutrición “Dr. Santiago Valdés Galindo”",
            "code": "sureste_enfermeria",
            "programs": (
                ("Licenciatura en Enfermería", "enfermeria"),
                ("Licenciatura en Nutrición", "nutricion"),
            ),
        },
        {
            "name": "Instituto de Lenguas Extranjeras",
            "code": "sureste_ile",
            "programs": (("Licenciatura en Enseñanza del Idioma Inglés", "ensenanza_ingles"),),
        },
        {
            "name": "Instituto de Investigaciones Jurídicas Academia Interamericana de Derechos Humanos",
            "code": "sureste_derechos_humanos",
            "programs": (
                ("Licenciatura en Derecho con Perspectiva en Derechos Humanos", "derecho_ddhh"),
            ),
        },
        {
            "name": "Coordinación General de Educación a Distancia",
            "code": "sureste_cged",
            "programs": (
                ("Licenciatura en Contaduría (En Línea)", "cged_contaduria"),
                ("Licenciatura en Administración de Recursos Humanos (En Línea)", "cged_rrhh"),
                ("Licenciatura en Administración de Empresas (En Línea)", "cged_admin"),
                ("Licenciatura en Negocios Internacionales (En Línea)", "cged_negocios"),
            ),
        },
    ),
    "Laguna": (
        {
            "name": "Escuela de Ciencias de la Comunidad",
            "code": "laguna_ciencias_comunidad",
            "programs": (
                ("Licenciatura en Relaciones Humanas", "relaciones_humanas"),
                ("Licenciatura en Trabajo Social", "trabajo_social"),
            ),
        },
        {
            "name": "Facultad de Contaduría y Administración",
            "code": "laguna_contaduria",
            "programs": (
                ("Licenciatura en Contaduría Pública", "contaduria_publica"),
                ("Licenciatura en Administración de Empresas con Acentuación en Comercialización", "admin_comercializacion"),
                ("Licenciatura en Comercio Exterior y Aduanas", "comercio_exterior"),
                ("Licenciatura en Administración de Empresas Gastronómicas y Turísticas", "admin_gastronomica"),
                ("Licenciatura en Administración de Empresas con Acentuación en Producción", "admin_produccion"),
            ),
        },
        {
            "name": "Facultad de Economía y Mercadotecnia",
            "code": "laguna_economia_mercadotecnia",
            "programs": (
                ("Licenciatura en Mercadotecnia", "mercadotecnia"),
                ("Licenciatura en Economía", "economia"),
            ),
        },
        {
            "name": "Facultad de Ciencias Políticas y Sociales",
            "code": "laguna_ciencias_politicas",
            "programs": (
                ("Licenciatura en Ciencias de la Comunicación", "ciencias_comunicacion"),
                ("Licenciatura en Ciencias Políticas y Administración Pública", "ciencias_politicas"),
                ("Licenciatura en Sociología", "sociologia"),
            ),
        },
        {
            "name": "Facultad de Administración Fiscal y Financiera",
            "code": "laguna_admin_fiscal",
            "programs": (
                ("Licenciatura en Administración Financiera", "admin_financiera"),
                ("Licenciatura en Administración Fiscal", "admin_fiscal"),
            ),
        },
        {
            "name": "Facultad de Derecho",
            "code": "laguna_derecho",
            "programs": (
                ("Licenciatura en Derecho", "derecho"),
                ("Licenciatura en Criminología y Ciencias Forenses", "criminologia"),
            ),
        },
        {
            "name": "Escuela de Administración",
            "code": "laguna_escuela_admin",
            "programs": (
                ("Licenciatura en Administración de Empresas", "admin_empresas"),
                ("Ingeniero Industrial y Administración de Recursos Humanos", "ing_ind_rrhh"),
            ),
        },
        {
            "name": "Facultad de Ingeniería Mecánica y Eléctrica",
            "code": "laguna_ing_mec_elec",
            "programs": (
                ("Ingeniería Mecánica Electricista", "ing_mec_elec"),
                ("Ingeniería Automotriz", "ing_automotriz"),
            ),
        },
        {
            "name": "Facultad de Ingeniería Civil",
            "code": "laguna_ing_civil",
            "programs": (("Ingeniería Civil", "ing_civil"),),
        },
        {
            "name": "Escuela de Sistemas",
            "code": "laguna_sistemas",
            "programs": (
                ("Ingeniería en Tecnologías de la Información y Comunicaciones", "ing_tic"),
                ("Licenciatura en Sistemas Computacionales Administrativos", "sistemas_admin"),
                ("Ingeniería Industrial y de Sistemas", "ing_ind_sistemas"),
            ),
        },
        {
            "name": "Escuela de Arquitectura",
            "code": "laguna_arquitectura",
            "programs": (("Licenciatura en Arquitectura", "arquitectura"),),
        },
        {
            "name": "Facultad de Ciencias Biológicas",
            "code": "laguna_ciencias_biologicas",
            "programs": (("Ingeniería Bioquímica", "ing_bioquimica"),),
        },
        {
            "name": "Facultad de Medicina",
            "code": "laguna_medicina",
            "programs": (("Médico Cirujano", "medico_cirujano"),),
        },
        {
            "name": "Facultad de Odontología",
            "code": "laguna_odontologia",
            "programs": (("Licenciatura en Cirujano Dentista", "cirujano_dentista"),),
        },
        {
            "name": "Facultad de Enfermería y Nutrición",
            "code": "laguna_enfermeria",
            "programs": (
                ("Licenciatura en Enfermería", "enfermeria"),
                ("Licenciatura en Nutrición", "nutricion"),
            ),
        },
        {
            "name": "Escuela de Artes",
            "code": "laguna_artes",
            "programs": (("Licenciatura en Artes Escénicas y Gestión Cultural", "artes_escenicas"),),
        },
        {
            "name": "Escuela de Psicología",
            "code": "laguna_psicologia",
            "programs": (("Licenciatura en Psicología", "psicologia"),),
        },
    ),
    "Norte": (
        {
            "name": "Facultad de Contaduría y Administración",
            "code": "norte_contaduria",
            "programs": (
                ("Licenciatura en Contaduría", "contaduria"),
                ("Licenciatura en Administración de Empresas", "admin_empresas"),
                ("Licenciatura en Administración de Recursos Humanos", "admin_rrhh"),
                ("Licenciatura en Negocios Internacionales", "negocios_intl"),
            ),
        },
        {
            "name": "Facultad de Administración, Contaduría y Derecho",
            "code": "norte_admin_cont_derecho",
            "programs": (
                ("Licenciatura en Contaduría", "contaduria_pn"),
                ("Licenciatura en Administración de Empresas", "admin_empresas_pn"),
                ("Licenciatura en Derecho", "derecho_pn"),
                ("Licenciatura en Negocios Internacionales", "negocios_intl_pn"),
            ),
        },
        {
            "name": "Facultad de Ingeniería Mecánica y Eléctrica",
            "code": "norte_ing_mec_elec",
            "programs": (
                ("Ingeniería en Mecatrónica", "ing_mecatronica"),
                ("Ingeniería Mecánica Electricista", "ing_mec_elec"),
                ("Ingeniería en Sistemas Computacionales", "ing_sistemas"),
                ("Ingeniería Biomédica", "ing_biomedica"),
            ),
        },
        {
            "name": "Facultad de Metalurgia",
            "code": "norte_metalurgia",
            "programs": (
                ("Ingeniería Química Metalurgista y Materiales", "ing_metalurgia"),
                ("Ingeniería en Procesos de Manufactura", "ing_manufactura"),
            ),
        },
        {
            "name": "Escuela Superior de Ingeniería “Lic. Adolfo López Mateos”",
            "code": "norte_esc_sup_ing",
            "programs": (
                ("Ingeniería en Tecnologías Químicas", "ing_tecnologias_quimicas"),
                ("Ingeniería en Geociencias y Recursos Hídricos", "ing_geociencias"),
                ("Ingeniería Industrial y de Sistemas", "ing_ind_sistemas"),
            ),
        },
        {
            "name": "Escuela de Sistemas “Profesor Marcial Ruiz Vargas”",
            "code": "norte_sistemas",
            "programs": (
                ("Ingeniería Industrial y de Sistemas", "ing_ind_sistemas_ac"),
                ("Ingeniería en Sistemas Computacionales", "ing_sistemas_ac"),
            ),
        },
        {
            "name": "Escuela de Ciencias de la Salud",
            "code": "norte_ciencias_salud",
            "programs": (
                ("Licenciatura en Enfermería", "enfermeria"),
                ("Licenciatura en Nutrición", "nutricion"),
                ("Licenciatura en Psicología", "psicologia"),
            ),
        },
        {
            "name": "Escuela de Medicina",
            "code": "norte_medicina",
            "programs": (("Médico Cirujano", "medico_cirujano"),),
        },
        {
            "name": "Escuela de Psicología y Enfermería",
            "code": "norte_psicologia_enfermeria",
            "programs": (
                ("Licenciatura en Psicología", "psicologia_mon"),
                ("Licenciatura en Enfermería", "enfermeria_mon"),
            ),
        },
    ),
}
