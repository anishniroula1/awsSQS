import json
import logging

from data_prep.service import DataPreparationService, DataPreparationError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """
    Main Lambda entrypoint. Expects an S3 event containing a zip with one .txt and one .csv file.
    In plain English: pull the files, check them, merge with old data, split for analysis/training,
    save everything, and hand back the S3 keys.
    """
    try:
        service = DataPreparationService.from_env()
        response = service.process(event)
        logger.info("Prepared dataset response: %s", json.dumps(response))
        return response
    except DataPreparationError:
        # We already know what went wrong, just log and rethrow.
        logger.exception("Data preparation failed due to input/validation error")
        raise
    except Exception as e:
        # Last-resort catch so the Step Function sees the failure.
        logger.exception("Data preparation failed unexpectedly")
        raise DataPreparationError(f"Unexpected failure: {e}") from e
