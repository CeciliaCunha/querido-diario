"""
Cobertura completa de testes para `get_month_value`.

Estratégia adotada:
  1. CAIXA BRANCA: cobre cada ramo (branch) do fluxo interno da função.
  2. CAIXA PRETA: complementa com partições de equivalência e análise
     de valor-limite, sem olhar para a implementação.

Mapeamento dos ramos internos:
  B1  -> entrada não-string OU string vazia          (early return None)
  B2  -> string numérica e dentro de 1..12           (retorna int)
  B3  -> len < 3 OU em conflicting_cases ("juho")    (retorna None)
  B4a -> texto não está em MONTHS, fuzzy ACHA match  (retorna int)
  B4b -> texto não está em MONTHS, fuzzy NÃO acha    (retorna None)
  B5  -> texto exatamente em MONTHS                  (retorna int)
"""

import pytest

from gazette.utils.extraction import get_month_value


# ---------------------------------------------------------------------------
# CAIXA BRANCA — um teste por ramo
# ---------------------------------------------------------------------------
class TestWhiteBoxGetMonthValue:
    """Cada teste exercita explicitamente um ramo (branch) da função."""

    def test_b1_input_is_not_string_returns_none(self):
        # Ramo B1: isinstance check falha
        assert get_month_value(None) is None
        assert get_month_value(123) is None
        assert get_month_value([]) is None
        assert get_month_value({}) is None
        assert get_month_value(3.14) is None

    def test_b1_empty_string_returns_none(self):
        # Ramo B1: len == 0
        assert get_month_value("") is None

    def test_b2_numeric_string_in_valid_range_returns_int(self):
        # Ramo B2: isdigit() True e valor em MONTHS.values()
        for n in range(1, 13):
            assert get_month_value(str(n)) == n

    def test_b2_numeric_string_out_of_range_does_not_take_b2_branch(self):
        # Ramo B2 falha (valor fora 1..12), texto longo o suficiente
        # cai em B4 (fuzzy) que deve retornar None p/ números altos
        assert get_month_value("100") is None
        assert get_month_value("999") is None

    def test_b3_len_less_than_3_returns_none(self):
        # Ramo B3: len < 3 (e não é dígito válido)
        assert get_month_value("ja") is None
        assert get_month_value("fe") is None
        assert get_month_value("a") is None

    def test_b3_conflicting_case_juho_returns_none(self):
        # Ramo B3: "juho" listado em conflicting_cases
        # (ambíguo entre "junho" e "julho")
        assert get_month_value("juho") is None

    def test_b4a_typo_resolved_by_fuzzy_match(self):
        # Ramo B4a: not in MONTHS + fuzzy encontra match (score >= 80)
        assert get_month_value("janero") == 1  # janeiro
        assert get_month_value("fevreiro") == 2  # fevereiro
        assert get_month_value("marco") == 3  # marco (após unidecode de março)
        assert get_month_value("setembr") == 9  # setembro
        assert get_month_value("dezembr") == 12  # dezembro

    def test_b4b_unknown_text_fuzzy_match_fails(self):
        # Ramo B4b: not in MONTHS + fuzzy não acha (score < 80)
        assert get_month_value("xyzabc") is None
        assert get_month_value("qwerty") is None
        assert get_month_value("aaaaaa") is None

    def test_b5_exact_match_in_months_dict(self):
        # Ramo B5: texto exatamente igual a chave de MONTHS
        # (após strip+lower+unidecode)
        assert get_month_value("janeiro") == 1
        assert get_month_value("fevereiro") == 2
        assert get_month_value("marco") == 3
        assert get_month_value("abril") == 4
        assert get_month_value("maio") == 5
        assert get_month_value("junho") == 6
        assert get_month_value("julho") == 7
        assert get_month_value("agosto") == 8
        assert get_month_value("setembro") == 9
        assert get_month_value("outubro") == 10
        assert get_month_value("novembro") == 11
        assert get_month_value("dezembro") == 12


# ---------------------------------------------------------------------------
# CAIXA PRETA — partições de equivalência + valor-limite
# ---------------------------------------------------------------------------
class TestBlackBoxGetMonthValue:
    """Testes que ignoram a implementação e exercitam o contrato público."""

    # Partição: tipos inválidos
    @pytest.mark.parametrize(
        "value",
        [None, [], {}, (), 1, 12, 3.5, object(), True],
    )
    def test_invalid_types_return_none(self, value):
        assert get_month_value(value) is None

    # Partição: strings vazias / só espaço
    @pytest.mark.parametrize("value", ["", " ", "   ", "\t", "\n"])
    def test_blank_strings_return_none(self, value):
        assert get_month_value(value) is None

    # Partição: números válidos (boundary 1, 12)
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("1", 1),  # limite inferior
            ("01", 1),  # zero à esquerda
            ("6", 6),  # meio
            ("12", 12),  # limite superior
        ],
    )
    def test_valid_numeric_month(self, text, expected):
        assert get_month_value(text) == expected

    # Partição: números fora do intervalo válido
    @pytest.mark.parametrize("text", ["0", "13", "100", "9999"])
    def test_invalid_numeric_month(self, text):
        assert get_month_value(text) is None

    # Partição: nomes válidos canônicos
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("janeiro", 1),
            ("fevereiro", 2),
            ("marco", 3),
            ("abril", 4),
            ("maio", 5),
            ("junho", 6),
            ("julho", 7),
            ("agosto", 8),
            ("setembro", 9),
            ("outubro", 10),
            ("novembro", 11),
            ("dezembro", 12),
        ],
    )
    def test_canonical_month_names(self, text, expected):
        assert get_month_value(text) == expected

    # Partição: normalização (case, whitespace, diacríticos)
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("JANEIRO", 1),
            ("Janeiro", 1),
            ("jAnEiRo", 1),
            ("  março  ", 3),
            ("\tmarço\n", 3),
            ("março", 3),  # com cedilha
            ("MARÇO", 3),
            ("máíó", 5),  # acentos em maio
            ("ABRÍL", 4),
        ],
    )
    def test_normalization_works(self, text, expected):
        assert get_month_value(text) == expected

    # Partição: typos corrigíveis pelo fuzzy
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("janero", 1),
            ("fevreiro", 2),
            ("abrill", 4),
            ("agost", 8),
            ("setembr", 9),
            ("dezembr", 12),
        ],
    )
    def test_typos_resolved_by_fuzzy(self, text, expected):
        assert get_month_value(text) == expected

    # Partição: caso conflituoso
    def test_conflicting_case_juho_is_ambiguous(self):
        # "juho" é ambíguo entre junho e julho -> retorna None
        assert get_month_value("juho") is None

    # Valor-limite: comprimento de string
    @pytest.mark.parametrize("text", ["a", "ab", "ja", "fe"])
    def test_strings_too_short_return_none(self, text):
        # boundary: len < 3
        assert get_month_value(text) is None

    @pytest.mark.parametrize("text", ["jan", "fev", "mar"])
    def test_three_char_abbreviations_are_resolved(self, text):
        # boundary: len == 3 deve passar pelo fuzzy match
        # (estes prefixos têm alta similaridade com o nome completo)
        result = get_month_value(text)
        assert result is not None
        assert 1 <= result <= 12

    # Strings totalmente irreconhecíveis
    @pytest.mark.parametrize("text", ["xyzabc", "qwerty", "asdfghjk", "123abc"])
    def test_unrecognizable_strings_return_none(self, text):
        assert get_month_value(text) is None
