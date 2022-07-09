# domain-email-records
[![PyPi](https://img.shields.io/pypi/v/domain-email-records.svg)](https://pypi.python.org/pypi/domain-email-records/)
[![Build Tests](https://github.com/ndejong/domain-email-records/actions/workflows/build-tests.yml/badge.svg)](https://github.com/ndejong/domain-email-records/actions/workflows/build-tests.yml)
![License](https://img.shields.io/github/license/ndejong/domain-email-records.svg)

CLI tool to quickly lookup MX, SPF, DMARC records for many domains

__NOTE__ while it generally should not be a problem, this tool does generate 
several-hundred DNS queries per second, be sure your nameservers have 
capacity to handle this.

## Install
```shell
pip install [--upgrade] domain-email-records
```

## Usage
```shell
usage: domain-email-records [-h] [-q | -v] [-o <filename>] [-t <seconds>] [-c <size>] [-d [<domain> ...]] [-f <filename>] [--csv-column <col>]

domain-email-records v0.2.0

CLI tool to quickly lookup MX, SPF, DMARC records for many domains

options:
  -h, --help            show this help message and exit
  -q, --quiet           Set quiet logging output
  -v, --verbose         Set verbose logging output
  -o <filename>, --out <filename>
                        Filename to save JSON formatted output to (default: stdout)
  -t <seconds>, --timeout <seconds>
                        Timeout seconds per domain-record query (default: 5)
  -c <size>, --chunk <size>
                        Chunk size per async loop to resolve together (default: 1000)

direct:
  -d [<domain> ...], --domains [<domain> ...]
                        Space separated list of domain names to query

filename:
  -f <filename>, --filename <filename>
                        Filename with list of domains to use; plain list text file -or- a comma-separated CSV file list.
  --csv-column <col>    CSV column number to use for domain-names -if- the file is CSV formatted (default: 2)
```

## Examples

### Domains from CSV-file with output file
```shell
$ domain-email-records -f alexa-top-1m-20220708.csv -o /tmp/output.json
2022-07-09T14:29:06+1000 - INFO - Domains in list from:google.com to:icims.com queried (1000x) at approx 9.3ms per domain (3.1ms per query) ETA: 2022-07-09 16:29:00
2022-07-09T14:29:14+1000 - INFO - Domains in list from:aliyuncs.com to:rapidgator.net queried (1000x) at approx 8.8ms per domain (2.9ms per query) ETA: 2022-07-09 16:25:00
2022-07-09T14:29:31+1000 - INFO - Domains in list from:hola.org to:shaadi.com queried (1000x) at approx 16.5ms per domain (5.5ms per query) ETA: 2022-07-09 16:57:00
^C 2022-07-09T14:29:32+1000 - WARNING - Exiting...
```

### Domains from CLI-arg with output to file
```shell
$ domain-email-records -d google.com facebook.com apple.com amazon.com -o /tmp/output.json
2022-07-09T14:24:57+1000 - INFO - Domains in list from:google.com to:amazon.com queried (4x) at approx 121.1ms per domain (40.4ms per query) ETA: 2022-07-09 14:24:00
```

### Domains from CLI-arg with output to stdout
```
$ domain-email-records -d google.com facebook.com apple.com amazon.com
{
  "google.com": {
    "mx": [
      "smtp.google.com."
    ],
    "spf": [
      "v=spf1 include:_spf.google.com ~all"
    ],
    "dmarc": [
      "v=DMARC1; p=reject; rua=mailto:mailauth-reports@google.com"
    ]
  }
}
...
2022-07-09T14:27:22+1000 - INFO - Domains in list from:google.com to:amazon.com queried (4x) at approx 15.6ms per domain (5.2ms per query) ETA: 2022-07-09 14:27:00
```

---

Copyright &copy; 2022 Nicholas de Jong
