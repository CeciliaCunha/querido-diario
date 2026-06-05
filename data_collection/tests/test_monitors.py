import pytest

class DummyData:
    """Classe vazia apenas para simular objetos sem bloqueios de imutabilidade do Spidermon"""
    pass

@pytest.fixture
def monitor_setup():
    """Configura um monitor falso para isolar o teste unitário"""
    from gazette.monitors import RequestsItemsRatioMonitor

    monitor = RequestsItemsRatioMonitor(methodName="test_requests_items_ratio")
    
    monitor.data = DummyData()
    monitor.data.stats = {}
    monitor.data.crawler = DummyData()
    monitor.data.crawler.settings = DummyData()
    
    # Simulando o limite máximo para 5.0
    monitor.data.crawler.settings.get = lambda k, d: 5.0 if k == "QUERIDODIARIO_MAX_REQUESTS_ITEMS_RATIO" else d
    
    return monitor

def test_ratio_abaixo_do_limite(monitor_setup):
    monitor_setup.data.stats["downloader/request_count"] = 10
    monitor_setup.data.stats["item_scraped_count"] = 2
    monitor_setup.test_requests_items_ratio()

def test_ratio_acima_do_limite(monitor_setup):
    monitor_setup.data.stats["downloader/request_count"] = 11
    monitor_setup.data.stats["item_scraped_count"] = 2
    with pytest.raises(AssertionError):
        monitor_setup.test_requests_items_ratio()

def test_ratio_com_zero_itens(monitor_setup):
    monitor_setup.data.stats["downloader/request_count"] = 10
    monitor_setup.data.stats["item_scraped_count"] = 0
    monitor_setup.test_requests_items_ratio()