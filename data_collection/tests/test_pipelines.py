import pytest
from gazette.pipelines import QueridoDiarioFilesPipeline

class MockResponse:
    """Simula uma resposta da web (com cabeçalhos HTTP e corpo do arquivo)"""
    def __init__(self, headers=None, body=b""):
        self.headers = headers or {}
        self.body = body

@pytest.fixture
def pipeline_setup():
    """Configura uma pipeline falsa para o teste"""
    return QueridoDiarioFilesPipeline(store_uri="/tmp")

def test_get_filename_pelo_header(pipeline_setup):
    """Cobre a decisão de identificar PDF pelo Header HTTP"""
    # A MUDANÇA: Tiramos os colchetes e colocamos o nome direto!
    response = MockResponse(headers={
        b"Content-Type": b"application/pdf", 
        "Content-Type": b"application/pdf"
    })
    result = pipeline_setup._get_filename_with_extension("diario", response)
    assert result == "diario.pdf"

def test_get_filename_pelo_body(pipeline_setup):
    """Cobre a decisão de identificar pelos Magic Bytes no corpo do arquivo (Ex: PNG)"""
    png_magic_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    response = MockResponse(body=png_magic_bytes)
    result = pipeline_setup._get_filename_with_extension("diario", response)
    assert result == "diario.png"