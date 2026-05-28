from unittest.mock import MagicMock, patch
from scrapy.pipelines.files import FilesPipeline
from gazette.pipelines import QueridoDiarioFilesPipeline

def make_pipeline(s3_client):
    pipeline = QueridoDiarioFilesPipeline.__new__(QueridoDiarioFilesPipeline)
    pipeline.s3_client = s3_client
    return pipeline

def make_info():
    info = MagicMock()
    info.spider = MagicMock()
    return info

def make_response():
    response = MagicMock()
    response.body = b"file-content"
    return response

class TestFileDownloaded:

    def test_when_result_is_none_should_not_copy_to_secondary_bucket(self):
        pipeline = make_pipeline(s3_client=MagicMock())
        response = make_response()
        info = make_info()

        with patch.object(FilesPipeline, "file_downloaded", return_value=None):
            with patch.object(pipeline, "_copy_to_secondary_bucket") as copy_mock:
                result = pipeline.file_downloaded(response, MagicMock(), info, item=None)

        assert result is None
        copy_mock.assert_not_called()

    def test_when_s3_client_is_none_should_not_copy_to_secondary_bucket(self):
        pipeline = make_pipeline(s3_client=None)
        response = make_response()
        info = make_info()
        super_result = {"path": "arq.pdf"}

        with patch.object(FilesPipeline, "file_downloaded", return_value=super_result):
            with patch.object(pipeline, "_copy_to_secondary_bucket") as copy_mock:
                result = pipeline.file_downloaded(response, MagicMock(), info, item=None)

        assert result == super_result
        copy_mock.assert_not_called()

    def test_when_result_has_none_path_should_not_copy_to_secondary_bucket(self):
        pipeline = make_pipeline(s3_client=MagicMock())
        response = make_response()
        info = make_info()
        super_result = {"path": None}

        with patch.object(FilesPipeline, "file_downloaded", return_value=super_result):
            with patch.object(pipeline, "_copy_to_secondary_bucket") as copy_mock:
                result = pipeline.file_downloaded(response, MagicMock(), info, item=None)

        assert result == super_result
        copy_mock.assert_not_called()

    def test_when_result_has_path_should_copy_to_secondary_bucket(self):
        pipeline = make_pipeline(s3_client=MagicMock())
        response = make_response()
        info = make_info()
        super_result = {"path": "arq.pdf"}

        with patch.object(FilesPipeline, "file_downloaded", return_value=super_result):
            with patch.object(pipeline, "_copy_to_secondary_bucket") as copy_mock:
                result = pipeline.file_downloaded(response, MagicMock(), info, item=None)

        assert result == super_result
        copy_mock.assert_called_once_with("arq.pdf", response.body, info.spider)    