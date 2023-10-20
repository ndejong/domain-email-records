import asyncio
import logging
import sys

from . import __title__
from .exceptions import DomainEmailRecordsException
from .lib.args import parse_args
from .lib.domain_email_records import DomainEmailRecords


def main() -> None:
    args = parse_args()

    if args.quiet:
        logging_level = "CRITICAL"
    elif args.verbose:
        logging_level = "DEBUG"
    else:
        logging_level = "INFO"

    try:
        domain_email_records = DomainEmailRecords(
            chunk_size=args.chunk,
            csv_column=args.csv_column,
            query_timeout=args.timeout,
            nameservers=args.nameservers,
            logging_level=logging_level,
        )
        if args.filename:
            domains = domain_email_records.read_domain_list_file(filename=args.filename, csv_column=args.csv_column)
        else:
            domains = args.domains

        eventloop = asyncio.get_event_loop()
        eventloop.run_until_complete(
            domain_email_records.lookups(domains=domains, lookup_types=args.types, output=args.out)
        )
        eventloop.close()

    except KeyboardInterrupt:
        logging.getLogger(__title__).warning("Exiting...")
        eventloop.stop()
        sys.exit(1)

    except DomainEmailRecordsException as e:
        message = ""
        for part in e.args:
            message = f"{str(message)}\n{part}".strip()
        logging.getLogger(__title__).error(message)
        sys.exit(1)

    except Exception as e:  # noqa pylint:disable=broad-except
        message = ""
        for part in e.args:
            message = f"{str(message)}\n{part}".strip()
        logging.getLogger(__title__).critical(message, exc_info=True)
        sys.exit(1)
