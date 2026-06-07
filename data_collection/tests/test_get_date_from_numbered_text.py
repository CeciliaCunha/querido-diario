"""
Cobertura completa de testes para `get_date_from_numbered_text`.

Estratégia adotada:
  1. CAIXA BRANCA: cobre cada ramo (branch) do fluxo interno da função.
  2. CAIXA PRETA: complementa com partições de equivalência e análise
     de valor-limite, sem olhar para a implementação.

Mapeamento dos ramos internos:
  B1  -> entrada não-string OU string vazia                  (early return None)
  B2  -> caso (a): 2 separadores casam e geram data válida   (retorna date)
  B3  -> caso (a) falha/inválido; caso (b): 1º separador     (retorna date)
  B4  -> casos (a),(b) falham; caso (c): 2º separador        (retorna date)
  B5  -> casos (a),(b),(c) falham; caso (d): sem separador   (retorna date)
  B6  -> nenhum dos 4 casos produz data válida               (retorna None)
"""

from datetime import date

import pytest

from gazette.utils.extraction import get_date_from_numbered_text


# ---------------------------------------------------------------------------
# CAIXA BRANCA — um teste por ramo
# ---------------------------------------------------------------------------
class TestWhiteBoxGetDateFromNumberedText:
    """Cada teste exercita explicitamente um ramo (branch) da função."""

    def test_b1_input_is_not_string_returns_none(self):
        # Ramo B1: isinstance check falha
        assert get_date_from_numbered_text(None) is None
        assert get_date_from_numbered_text(123) is None
        assert get_date_from_numbered_text([]) is None
        assert get_date_from_numbered_text({}) is None
        assert get_date_from_numbered_text(3.14) is None

    def test_b1_empty_string_returns_none(self):
        # Ramo B1: len == 0
        assert get_date_from_numbered_text("") is None

    def test_b2_two_separators_case_a_returns_date(self):
        # Ramo B2: regex (D)(sep)(M)(sep)(Y) casa e gera data válida
        assert get_date_from_numbered_text("01/02/2020") == date(2020, 2, 1)
        assert get_date_from_numbered_text("1 1 2020") == date(2020, 1, 1)
        assert get_date_from_numbered_text("11-11-1111") == date(1111, 11, 11)
        assert get_date_from_numbered_text("01_02_2020") == date(2020, 2, 1)

    def test_b3_one_separator_first_case_b_returns_date(self):
        # Ramo B3: caso (a) não casa (só 1 separador); caso (b)
        # (D)(sep)(MYYYY) casa e gera data válida
        assert get_date_from_numbered_text("5 062020") == date(2020, 6, 5)
        assert get_date_from_numbered_text("1 11111") == date(1111, 1, 1)
        assert get_date_from_numbered_text("1 111111") == date(1111, 11, 1)

    def test_b4_one_separator_second_case_c_returns_date(self):
        # Ramo B4: casos (a) e (b) não casam; caso (c)
        # (DDMM)(sep)(YYYY) casa e gera data válida
        assert get_date_from_numbered_text("1511 2020") == date(2020, 11, 15)
        assert get_date_from_numbered_text("1111 1111") == date(1111, 11, 11)

    def test_b5_no_separator_case_d_returns_date(self):
        # Ramo B5: casos (a), (b) e (c) não casam; caso (d)
        # (DDMMYYYY), sem separador, casa e gera data válida
        assert get_date_from_numbered_text("15112020") == date(2020, 11, 15)
        assert get_date_from_numbered_text("11111111") == date(1111, 11, 11)

    def test_b6_no_case_yields_valid_date_returns_none(self):
        # Ramo B6: nenhum dos 4 regexes produz uma data válida
        # (a) texto sem dígitos -> nenhum regex casa
        assert get_date_from_numbered_text("texto sem data nenhuma") is None
        # (b) regex casa, mas get_month_value/date() invalidam o resultado
        #     "99/99/9999": mês "99" não resolve -> None -> TypeError -> None
        assert get_date_from_numbered_text("99/99/9999") is None
        # (c) regex casa (dia=32, mes=13), porém date() lança ValueError
        assert get_date_from_numbered_text("32 13 2020") is None


# ---------------------------------------------------------------------------
# CAIXA PRETA — partições de equivalência + valor-limite
# ---------------------------------------------------------------------------
class TestBlackBoxGetDateFromNumberedText:
    """Testes que ignoram a implementação e exercitam o contrato público."""

    # Partição: tipos inválidos
    @pytest.mark.parametrize(
        "value",
        [None, [], {}, (), 1, 12, 3.5, object(), True],
    )
    def test_invalid_types_return_none(self, value):
        assert get_date_from_numbered_text(value) is None

    # Partição: strings vazias / só espaço
    @pytest.mark.parametrize("value", ["", " ", "   ", "\t", "\n"])
    def test_blank_strings_return_none(self, value):
        assert get_date_from_numbered_text(value) is None

    # Partição: datas com 2 separadores -- (D/DD)(sep)(M/MM)(sep)(YYYY)
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("01/02/2020", date(2020, 2, 1)),
            ("1/1/2020", date(2020, 1, 1)),
            ("31/12/1999", date(1999, 12, 31)),
            ("01-02-2020", date(2020, 2, 1)),
            ("01_02_2020", date(2020, 2, 1)),
            ("1 1 1111", date(1111, 1, 1)),
            ("01-02/2020", date(2020, 2, 1)),  # separadores diferentes (- e /)
        ],
    )
    def test_two_separator_dates_are_parsed(self, text, expected):
        assert get_date_from_numbered_text(text) == expected

    # Partição: 1 separador, separando dia de mês+ano colados -- (D)(sep)(MYYYY)
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("5 062020", date(2020, 6, 5)),
            ("1 062020", date(2020, 6, 1)),
            ("1 11111", date(1111, 1, 1)),
            ("1 111111", date(1111, 11, 1)),
        ],
    )
    def test_one_separator_first_dates_are_parsed(self, text, expected):
        assert get_date_from_numbered_text(text) == expected

    # Partição: 1 separador, separando dia+mês colados de ano -- (DDMM)(sep)(YYYY)
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("1511 2020", date(2020, 11, 15)),
            ("0102 2020", date(2020, 2, 1)),
            ("1111 1111", date(1111, 11, 11)),
        ],
    )
    def test_one_separator_second_dates_are_parsed(self, text, expected):
        assert get_date_from_numbered_text(text) == expected

    # Partição: sem separador -- (DDMMYYYY)
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("15112020", date(2020, 11, 15)),
            ("01022020", date(2020, 2, 1)),
            ("11111111", date(1111, 11, 11)),
        ],
    )
    def test_no_separator_dates_are_parsed(self, text, expected):
        assert get_date_from_numbered_text(text) == expected

    # Partição: texto sem nenhum dígito -- nenhum regex pode casar
    @pytest.mark.parametrize(
        "text",
        ["texto sem data nenhuma", "abcd", "10 de maio de 2020", "qualquer coisa"],
    )
    def test_text_without_digits_returns_none(self, text):
        assert get_date_from_numbered_text(text) is None

    # Partição: dígitos formam datas semanticamente inválidas
    # (mês/dia fora do intervalo, dia inexistente no mês, ano > 9999 etc.)
    @pytest.mark.parametrize(
        "text",
        [
            "99/99/9999",  # mês inválido (99)
            "32 13 2020",  # dia (32) e mês (13) inválidos
            "31/04/2020",  # abril não tem dia 31
            "29/02/2021",  # 2021 não é bissexto -> não existe 29/fev
            "00/00/0000",  # dia e mês zero são inválidos
            "1/1/20000",  # ano com 5 dígitos -> > 9999, ValueError
            "31 13 2020",  # dia e mês fora do intervalo
        ],
    )
    def test_numeric_text_with_invalid_date_returns_none(self, text):
        assert get_date_from_numbered_text(text) is None

    # Valor-limite: dia (1, 31 válidos / 0, 32 inválidos)
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("1/1/2020", date(2020, 1, 1)),
            ("31/1/2020", date(2020, 1, 31)),
        ],
    )
    def test_day_boundary_valid(self, text, expected):
        assert get_date_from_numbered_text(text) == expected

    @pytest.mark.parametrize("text", ["0/1/2020", "32/1/2020"])
    def test_day_boundary_invalid(self, text):
        assert get_date_from_numbered_text(text) is None

    # Valor-limite: mês (1, 12 válidos / 0, 13 inválidos)
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("1/1/2020", date(2020, 1, 1)),
            ("1/12/2020", date(2020, 12, 1)),
        ],
    )
    def test_month_boundary_valid(self, text, expected):
        assert get_date_from_numbered_text(text) == expected

    @pytest.mark.parametrize("text", ["1/0/2020", "1/13/2020"])
    def test_month_boundary_invalid(self, text):
        assert get_date_from_numbered_text(text) is None

    # Valor-limite: ano bissexto (29/fev existe em 2020, não em 2021)
    def test_leap_year_boundary(self):
        assert get_date_from_numbered_text("29/02/2020") == date(2020, 2, 29)
        assert get_date_from_numbered_text("29/02/2021") is None

    # Normalização: espaços extras e ocorrências de "de" são tratadas
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("  01/02/2020  ", date(2020, 2, 1)),
            ("10 de 05 de 2020", date(2020, 5, 10)),
            ("10  de  05  de  2020", date(2020, 5, 10)),
        ],
    )
    def test_whitespace_and_de_normalization(self, text, expected):
        assert get_date_from_numbered_text(text) == expected

    # Separadores aceitos pela expressão default `[ /_-]`
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("01/02/2020", date(2020, 2, 1)),
            ("01-02-2020", date(2020, 2, 1)),
            ("01_02_2020", date(2020, 2, 1)),
            ("01 02 2020", date(2020, 2, 1)),
        ],
    )
    def test_accepted_separators(self, text, expected):
        assert get_date_from_numbered_text(text) == expected

    # Separador não suportado -> nenhum regex casa
    @pytest.mark.parametrize("text", ["01.02.2020", "01:02:2020"])
    def test_unsupported_separator_returns_none(self, text):
        assert get_date_from_numbered_text(text) is None
