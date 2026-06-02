class IngestError(Exception):
    """Base error for ingestion failures."""

    def __init__(self, message: str, code: str = "ingest_error"):
        self.message = message
        self.code = code
        super().__init__(message)


class UnsupportedUrlError(IngestError):
    def __init__(self, message: str):
        super().__init__(message, code="unsupported_url")


class MetadataExtractionError(IngestError):
    def __init__(self, message: str):
        super().__init__(message, code="metadata_extraction_failed")


class TranscriptExtractionError(IngestError):
    def __init__(self, message: str):
        super().__init__(message, code="transcript_extraction_failed")
