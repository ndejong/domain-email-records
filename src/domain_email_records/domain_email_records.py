import json
import logging
import asyncio
import dns.asyncresolver
from domain_email_records.logger import Logger
from domain_email_records import __title__


logger = logging.getLogger(__title__)


class DomainEmailRecordsException(Exception):
    pass


class DomainEmailRecords:

    chunk_size: int
    csv_column: int
    max_query_seconds: int

    def __init__(self, chunk_size=100, csv_column=2, max_query_seconds=5, logging_level="INFO"):
        self.chunk_size = chunk_size
        self.csv_column = csv_column
        self.max_query_seconds = max_query_seconds

        global logger
        logger = Logger(name=__title__).setup(level=logging_level)

    async def process(self, filename: str = None, domains: list = None):
        logger.debug(f"process(filename={filename}, domains={domains})")

        if filename and domains:
            raise DomainEmailRecordsException("Must supply either --filename or --domains not both")

        if filename:
            domains = self.read_domains_file(filename=filename, csv_column=self.csv_column)

        def list_chunk(seq, size):
            return (seq[pos : pos + size] for pos in range(0, len(seq), size))

        for chunk in list_chunk(domains, self.chunk_size):
            results = await asyncio.gather(*[self.domain_record_lookups(domain) for domain in chunk])
            for result in results:
                print(json.dumps(result, indent="  "))

    async def domain_record_lookups(self, domain_name: str) -> dict:
        """
        Query for mx, spf (via apex-TXT) and dmarc records

        :param domain_name:
        :return:
        """
        logger.debug(f"dns_lookups(domain_name={domain_name})")

        records = {}

        # mx
        answers = await self.dns_query(domain_name, "mx")
        if answers:
            for rdata in answers:
                if "mx" not in records:
                    records["mx"] = []
                records["mx"].append(str(rdata.exchange))

        # spf
        answers = await self.dns_query(domain_name, "txt")
        if answers:
            for rdata in answers:
                txt_record = rdata.strings[0].decode("utf8").lower()
                if "spf1" in txt_record:
                    if "spf" not in records:
                        records["spf"] = []
                    records["spf"].append(rdata.strings[0].decode("utf8"))

        # dmarc
        answers = await self.dns_query(f"_dmarc.{domain_name}", "txt")
        if answers:
            for rdata in answers:
                if "dmarc" not in records:
                    records["dmarc"] = []
                records["dmarc"].append(rdata.strings[0].decode("utf8"))

        return {domain_name: records}

    async def dns_query(self, domain_name, query_type):
        try:
            answers = await dns.asyncresolver.resolve(domain_name, query_type.upper(), lifetime=self.max_query_seconds)
        except dns.exception.DNSException:
            answers = None
        return answers

    def read_domains_file(self, filename: str, csv_column: int = 2) -> list:
        """
        Loads domain names from a plain file with domain names only; or detects the comma(,)
        character, then splits and takes the csv_column_index

        :param filename:
        :param csv_column:
        :return:
        """

        domains = []

        with open(filename, "r") as f:
            line = f.readline()
            while line:
                if "," not in line:
                    domains.append(line)
                else:
                    columns = line.strip().split(",")
                    if len(columns) >= csv_column:
                        domains.append(columns[csv_column - 1].strip())
                line = f.readline()

        return domains
