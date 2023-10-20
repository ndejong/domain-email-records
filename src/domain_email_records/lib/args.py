import argparse
import sys
import textwrap

from domain_email_records import __title__, __version__


def parse_args() -> argparse.Namespace:
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
        "-o",
        "--out",
        metavar="<filename>",
        required=False,
        type=str,
        help="Filename to save JSON formatted output to (default: stdout)",
    )
    parser.add_argument(
        "-T",
        "--timeout",
        metavar="<seconds>",
        required=False,
        type=int,
        default=10,
        help="Timeout seconds per domain-record query (default: 10)",
    )
    parser.add_argument(
        "-n",
        "--nameservers",
        metavar="<address>",
        required=False,
        type=str,
        nargs="*",
        default=None,
        help="Space separated list of alternate nameservers (default: system nameservers)",
    )
    parser.add_argument(
        "-t",
        "--types",
        metavar="<qtype>",
        required=False,
        type=str,
        nargs="*",
        default=["ns", "apex", "mx", "spf", "dmarc"],
        help="Space separated list lookup types to collect (default: ['ns', 'apex', 'mx', 'spf', 'dmarc']); "
        "also 'txt' type is available",
    )
    parser.add_argument(
        "-c",
        "--chunk",
        metavar="<size>",
        required=False,
        type=int,
        default=500,
        help="Chunk size per async loop to resolve together (default: 500)",
    )

    direct_list_parser = parser.add_argument_group(title="domains-by-cli")
    direct_list_parser.add_argument(
        "-d", "--domains", metavar="<domain>", nargs="*", help="Space separated list of domain names to query"
    )

    file_list_parser = parser.add_argument_group(title="domains-by-file")
    file_list_parser.add_argument(
        "-f",
        "--filename",
        metavar="<filename>",
        type=str,
        help="Filename with list of domains to use; plain list text file -or- a comma-separated CSV file list.",
    )
    file_list_parser.add_argument(
        "-col",
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
