import sys
import json
import time
import logging
import asyncio
import datetime

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

    async def lookups(self, domains: list = None, output: str = None):
        logger.debug(f"lookups(len(domains)={len(domains)}, output={output})")

        def list_chunk(seq, size):
            return (seq[pos : pos + size] for pos in range(0, len(seq), size))

        sys.stdout.close = lambda: None

        with (open(output, "w") if output else sys.stdout) as output_handle:

            chunk_ms_per_domains = []
            estimate_finish_start = time.time()

            for chunk in list_chunk(domains, self.chunk_size):
                start_time = time.perf_counter()
                start_domain = chunk[0]

                results = await asyncio.gather(*[self.domain_record_lookups(domain) for domain in chunk])
                for result in results:
                    output_handle.write(json.dumps(result, indent="  ") + "\n")

                end_time = time.perf_counter()
                end_domain = chunk[len(chunk) - 1]
                ms_per_domain = (end_time - start_time) * 1000 / len(chunk)

                chunk_ms_per_domains.append(ms_per_domain)
                estimate_total_processing_time = len(domains) * (
                    (sum(chunk_ms_per_domains) / len(chunk_ms_per_domains)) / 1000
                )
                estimate_finish_time = datetime.datetime.fromtimestamp(
                    estimate_finish_start + estimate_total_processing_time
                ).strftime("%Y-%m-%d %H:%M:00")

                logger.info(
                    f"Domains in list from:{start_domain} to:{end_domain} queried ({len(chunk)}x) at "
                    f"approx {round(ms_per_domain,1)}ms per domain ({round(ms_per_domain / 3,1)}ms per query) "
                    f"ETA: {estimate_finish_time}"
                )

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
                txt_record = await self.rdata_decode(rdata, domain_name=domain_name)
                if txt_record and "spf1" in txt_record.lower():
                    if "spf" not in records:
                        records["spf"] = []
                    records["spf"].append(txt_record)

        # dmarc
        answers = await self.dns_query(f"_dmarc.{domain_name}", "txt")
        if answers:
            for rdata in answers:
                if "dmarc" not in records:
                    records["dmarc"] = []
                records["dmarc"].append(await self.rdata_decode(rdata, domain_name=domain_name))

        return {domain_name: records}

    async def rdata_decode(self, rdata, rdata_index=0, domain_name=None, decode_type="UTF-8"):
        try:
            decoded = rdata.strings[rdata_index].decode(decode_type)
        except UnicodeDecodeError:
            logger.warning(f"{domain_name} unable to {decode_type} decode rdata: " + str(rdata.strings[rdata_index]))
            decoded = None
        return decoded

    async def dns_query(self, domain_name, query_type):
        try:
            answers = await dns.asyncresolver.resolve(domain_name, query_type.upper(), lifetime=self.max_query_seconds)
        except dns.exception.DNSException:
            logger.debug(f"{domain_name} unable to query type:{query_type}")
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
                    domains.append(line.strip())
                else:
                    columns = line.strip().split(",")
                    if len(columns) >= csv_column:
                        domains.append(columns[csv_column - 1].strip())
                line = f.readline()

        return domains
