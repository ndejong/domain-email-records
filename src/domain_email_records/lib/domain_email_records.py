import asyncio
import copy
import datetime
import json
import sys
import time
from typing import Any, Dict, Generator, List, Optional, Sequence, Tuple

import dns.asyncresolver
from async_lru import alru_cache
from dns.resolver import Answer

from .. import __title__
from ..constants import DOMAIN_RECORD_TYPES_VALID
from ..exceptions import DomainEmailRecordsException
from ..lib.logger import logger_get, logger_setlevel

logger = logger_get(__title__)


class DomainEmailRecords:
    chunk_size: int
    csv_column: int
    query_timeout: int
    nameservers: Optional[List[str]]

    def __init__(
        self,
        chunk_size: int = 1000,
        csv_column: int = 2,
        query_timeout: int = 10,
        nameservers: Optional[List[str]] = None,
        logging_level: str = "INFO",
    ):
        self.chunk_size = chunk_size
        self.csv_column = csv_column
        self.query_timeout = query_timeout
        self.nameservers = nameservers

        global logger
        logger = logger_setlevel(name=__title__, loglevel=logging_level)

    def read_domain_list_file(self, filename: str, csv_column: int = 2) -> List[str]:
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

    async def lookups(self, domains: List[str], lookup_types: List[str], output: Optional[str] = None) -> None:
        logger.debug(f"lookups(len(domains)={len(domains)}, lookup_types={lookup_types}, output={output})")

        chunk_ms_per_domains = []
        estimate_finish_start = time.time()
        domain_list_index_start = 0
        sys.stdout.close = lambda: None  # type: ignore[method-assign]

        def list_chunk(seq: Sequence[str], size: int) -> Generator[Sequence[str], Any, None]:
            return (seq[pos : pos + size] for pos in range(0, len(seq), size))

        logger.info(
            f"Looking up {len(domains)} domains in chunks of {self.chunk_size} per async loop "
            f"using {self.nameservers if self.nameservers else 'system-local'} nameservers."
        )

        with open(output, "w") if output else sys.stdout as output_handle:
            for chunk in list_chunk(domains, self.chunk_size):
                start_time = time.perf_counter()
                start_domain = chunk[0]

                results = await asyncio.gather(*[self.domain_record_lookups(domain, lookup_types) for domain in chunk])
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
                    estimate_finish_start + estimate_total_processing_time,
                    tz=datetime.datetime.now().astimezone().tzinfo,
                ).strftime("%Y-%m-%dT%H:%M:%S%z")

                logger.info(
                    f"Domains in list "
                    f"from:{start_domain} (index:{domain_list_index_start}) "
                    f"to:{end_domain} (index:{domain_list_index_start + len(chunk)}) "
                    f"query rate ~{round(ms_per_domain,1)}ms per domain "
                    f"({round(ms_per_domain / len(lookup_types),1)}ms per query) "
                    f"ETA: {estimate_finish_time}"
                )

                domain_list_index_start += self.chunk_size

    async def domain_record_lookups(self, domain_name: str, lookup_types: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Query for mx, spf and dmarc records

        :param domain_name:
        :param lookup_types: list of lookup types to conduct
        :return:
        """
        logger.debug(f"domain_record_lookups(domain_name={domain_name}, lookup_types={lookup_types})")

        if not set(lookup_types).issubset(set(DOMAIN_RECORD_TYPES_VALID)):
            raise DomainEmailRecordsException("Unsupported domain record lookup_type requested", lookup_types)

        lookup_types_local = copy.copy(lookup_types)

        if "mx" in lookup_types_local:
            lookup_types_local.insert(lookup_types_local.index("mx") + 1, "mx_preference")

        records = {}
        for lookup_type in lookup_types_local:
            result = await getattr(self, f"domain_record_lookup_{lookup_type}")(domain_name=domain_name)
            if result:
                records[lookup_type] = result

        return {domain_name: records}

    async def domain_record_lookup_ns(self, domain_name: str) -> List[str]:
        results = []
        answers = await self.dns_query(domain_name, "ns")
        if answers:
            for rdata in answers:
                results.append(str(rdata.target))
        return results

    async def domain_record_lookup_apex(self, domain_name: str) -> List[str]:
        results = []
        answers = await self.dns_query(domain_name, "a")
        if answers:
            for rdata in answers:
                results.append(str(rdata))
        return results

    async def domain_record_lookup_mx(self, domain_name: str) -> List[str]:
        exchanges, _ = await self.__domain_record_lookup_mx_w_exchange_preference(domain_name=domain_name)
        return exchanges

    async def domain_record_lookup_mx_preference(self, domain_name: str) -> List[str]:
        _, preferences = await self.__domain_record_lookup_mx_w_exchange_preference(domain_name=domain_name)
        return preferences

    @alru_cache(maxsize=100)
    async def __domain_record_lookup_mx_w_exchange_preference(self, domain_name: str) -> Tuple[List[str], List[str]]:
        exchanges = []
        preferences = []
        answers = await self.dns_query(domain_name, "mx")
        if answers:
            for rdata in answers:
                exchanges.append(str(rdata.exchange))
                preferences.append(str(rdata.preference))
        return exchanges, preferences

    async def domain_record_lookup_spf(self, domain_name: str) -> List[str]:
        results = []
        answers = await self.dns_query(domain_name, "txt")
        if answers:
            for rdata in answers:
                txt_record = await self.rdata_decode(rdata, domain_name=domain_name)
                if txt_record and ("spf1" in txt_record.lower() or "spf2" in txt_record.lower()):
                    results.append(txt_record)
        return results

    async def domain_record_lookup_txt(self, domain_name: str) -> List[str]:
        results = []
        answers = await self.dns_query(domain_name, "txt")
        if answers:
            for rdata in answers:
                data = await self.rdata_decode(rdata, domain_name=domain_name)
                if data:
                    results.append(data)
        return results

    async def domain_record_lookup_dmarc(self, domain_name: str) -> List[str]:
        results = []
        answers = await self.dns_query(f"_dmarc.{domain_name}", "txt")
        if answers:
            for rdata in answers:
                data = await self.rdata_decode(rdata, domain_name=domain_name)
                if data:
                    results.append(data)
        return results

    async def dns_query(
        self, domain_name: str, query_type: str, query_timeout: Optional[int] = None
    ) -> Optional[Answer]:
        resolver = dns.asyncresolver.Resolver()
        if self.nameservers:
            resolver.nameservers = self.nameservers
        if not query_timeout:
            query_timeout = self.query_timeout
        try:
            answers = await resolver.resolve(domain_name, query_type.upper(), lifetime=query_timeout)
        except dns.exception.DNSException:
            logger.debug(f"{domain_name} unable to query type:{query_type}")
            answers = None
        return answers

    async def rdata_decode(
        self, rdata: Answer, rdata_index: int = 0, domain_name: Optional[str] = None, decode_type: str = "UTF-8"
    ) -> Optional[str]:
        try:
            decoded: str = rdata.strings[rdata_index].decode(decode_type)
        except UnicodeDecodeError:
            logger.warning(f"{domain_name} unable to {decode_type} decode rdata: " + str(rdata.strings[rdata_index]))
            return None
        return decoded
