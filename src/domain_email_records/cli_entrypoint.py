import sys
import json
import asyncio
import argparse
import textwrap
from signal import signal, SIGINT
from domain_email_records import __title__
from domain_email_records import __version__
from domain_email_records.domain_email_records import DomainEmailRecords
from domain_email_records.domain_email_records import DomainEmailRecordsException


def sigint_handler(__signal_received, __frame):
    print("SIGINT received, exiting.")
    exit(1)


def main():
    signal(SIGINT, sigint_handler)
    args = __argparse()

    if args.quiet:
        logging_level = "CRITICAL"
    elif args.verbose:
        logging_level = "DEBUG"
    else:
        logging_level = "INFO"

    try:
        asyncio.run(
            DomainEmailRecords(
                chunk_size=args.chunk_size,
                csv_column=args.csv_column,
                logging_level=logging_level,
            ).process(filename=args.filename, domains=args.domains)
        )
    except DomainEmailRecordsException as e:
        error = {"program": "{}".format(__title__), "version": "v{}".format(__version__), "message": str(e.args[0])}
        if len(e.args) > 1:
            error["data"] = str(e.args[1 : len(e.args)])

        print(json.dumps({"error": error}, indent="  "))
        exit(1)


def __argparse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        add_help=True,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """\
            {name} v{version}

            CLI tool to quickly lookup MX, SPF, DMARC records for many domains
        """.format(
                name=__title__, version=__version__
            )
        ),
    )

    output_parser = parser.add_mutually_exclusive_group(required=False)
    output_parser.add_argument("-q", "--quiet", action="store_true", help="Set quiet logging output")
    output_parser.add_argument("-v", "--verbose", action="store_true", help="Set verbose logging output")

    parser.add_argument(
        "--chunk-size",
        metavar="<size>",
        required=False,
        type=int,
        default=100,
        help="Number of domain names to async resolve together (default: 100)",
    )

    direct_list_parser = parser.add_argument_group(title="direct")
    direct_list_parser.add_argument(
        "-d", "--domains", metavar="<domain>", nargs="*", help="Space separated list of domain names to query"
    )

    file_list_parser = parser.add_argument_group(title="filename")
    file_list_parser.add_argument(
        "-f",
        "--filename",
        metavar="<filename>",
        type=str,
        help="Filename with list of domains to use; either a plain text file list -or- a comma-separated CSV file list.",
    )
    file_list_parser.add_argument(
        "--csv-column",
        metavar="<col>",
        required=False,
        type=int,
        default=2,
        help="CSV column number to use for domain-names -if- the file is CSV formatted (default: 2)",
    )

    args = parser.parse_args()

    if len(sys.argv) < 2 or (args.filename and args.domains):
        parser.print_help()
        print()
        exit(1)

    return args
