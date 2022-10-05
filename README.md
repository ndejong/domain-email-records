# domain-email-records
[![PyPi](https://img.shields.io/pypi/v/domain-email-records.svg)](https://pypi.python.org/pypi/domain-email-records/)
[![Python Versions](https://img.shields.io/pypi/pyversions/domain-email-records.svg)](https://github.com/ndejong/domain-email-records/)
[![Build Tests](https://github.com/ndejong/domain-email-records/actions/workflows/build-tests.yml/badge.svg)](https://github.com/ndejong/domain-email-records/actions/workflows/build-tests.yml)
![License](https://img.shields.io/github/license/ndejong/domain-email-records.svg)

CLI tool to quickly lookup MX, SPF, DMARC records for many domains

__NB1__ this tool can generate several-hundred DNS queries per second, be sure your 
nameservers have capacity to handle this.

__NB2__ if you get errors like `OSError: [Errno 24] Too many open files: '/etc/resolv.conf'` then 
you are trying to set the chunk-size too large for your system - use a smaller chunk-size.

## Install
```shell
pip install [--upgrade] domain-email-records
```

## Usage
```shell
usage: domain-email-records [-h] [-q | -v] [-o <filename>] [-T <seconds>] [-n [<address> ...]] [-t [<qtype> ...]] [-c <size>] [-d [<domain> ...]] [-f <filename>] [-col <col>]

domain-email-records v0.4.1

CLI tool to quickly lookup MX, SPF, DMARC records for many domains

options:
  -h, --help            show this help message and exit
  -q, --quiet           Set quiet logging output
  -v, --verbose         Set verbose logging output
  -o <filename>, --out <filename>
                        Filename to save JSON formatted output to (default: stdout)
  -T <seconds>, --timeout <seconds>
                        Timeout seconds per domain-record query (default: 10)
  -n [<address> ...], --nameservers [<address> ...]
                        Space separated list of alternate nameservers (default: system nameservers)
  -t [<qtype> ...], --types [<qtype> ...]
                        Space separated list lookup types to collect (default: ['ns', 'apex', 'mx', 'spf', 'dmarc']); also 'txt' type is available
  -c <size>, --chunk <size>
                        Chunk size per async loop to resolve together (default: 500)

domains-by-cli:
  -d [<domain> ...], --domains [<domain> ...]
                        Space separated list of domain names to query

domains-by-file:
  -f <filename>, --filename <filename>
                        Filename with list of domains to use; plain list text file -or- a comma-separated CSV file list.
  -col <col>, --csv-column <col>
                        CSV column number to use for domain-names -if- the file is CSV formatted (default: 2)
```

## Examples

### Domains from CSV-file with output file
```shell
$ domain-email-records -c 1000 -f alexa-top-1m-20220708.csv -o /tmp/output.json
2022-07-09T16:51:41+1000 - INFO - Looking up 772475 domains in chunks of 1000 per async loop using system-local nameservers.
2022-07-09T16:51:56+1000 - INFO - Domains in list from:google.com (index:0) to:icims.com (index:1000) query rate ~15.5ms per domain (5.2ms per query) ETA: 2022-07-09T20:11:09+1000
2022-07-09T16:52:11+1000 - INFO - Domains in list from:aliyuncs.com (index:1000) to:rapidgator.net (index:2000) query rate ~15.1ms per domain (5.0ms per query) ETA: 2022-07-09T20:08:23+1000
2022-07-09T16:52:27+1000 - INFO - Domains in list from:hola.org (index:2000) to:shaadi.com (index:3000) query rate ~15.4ms per domain (5.1ms per query) ETA: 2022-07-09T20:08:58+1000
^C2022-07-09T16:52:27+1000 - WARNING - Exiting...
```

### Domains from plain-file with specific nameservers
```shell
$ domain-email-records -n 9.9.9.9 1.1.1.1 8.8.8.8 -f alexa-top-1m-20220708.txt -o /tmp/output.json
2022-07-09T07:34:08+0000 - INFO - Looking up 772475 domains in chunks of 500 per async loop using ['1.1.1.1', '9.9.9.9', '8.8.8.8'] nameservers.
2022-07-09T07:34:18+0000 - INFO - Domains in list from:google.com (index:0) to:googlesyndication.com (index:500) query rate ~18.3ms per domain (6.1ms per query) ETA: 2022-07-09T11:30:18+0000
2022-07-09T07:34:20+0000 - WARNING - cisco.com unable to UTF-8 decode rdata: b'\xc8atlassian-domain-verification=blI4HshP3kJO1PV8nZFlncJ6TwVviYYxBNhkMi9wIa9DTxUjY4p1GO7O5SjiioyT'
2022-07-09T07:34:24+0000 - INFO - Domains in list from:chegg.com (index:500) to:icims.com (index:1000) query rate ~12.4ms per domain (4.1ms per query) ETA: 2022-07-09T10:51:50+0000
2022-07-09T07:34:32+0000 - INFO - Domains in list from:aliyuncs.com (index:1000) to:poshukach.com (index:1500) query rate ~15.3ms per domain (5.1ms per query) ETA: 2022-07-09T10:51:43+0000
^C2022-07-09T07:35:10+0000 - WARNING - Exiting...
```

### Domains from cli args with output to file
```shell
$ domain-email-records -d google.com facebook.com apple.com amazon.com -o /tmp/output.json
2022-07-09T14:24:57+1000 - INFO - Domains in list from:google.com to:amazon.com queried (4x) at approx 121.1ms per domain (40.4ms per query) ETA: 2022-07-09 14:24:00
```

### Domains from cli args with output to stdout
```
$ domain-email-records -d google.com facebook.com apple.com amazon.com
2022-10-06T09:37:38+1000 - INFO - Looking up 4 domains in chunks of 500 per async loop using system-local nameservers.
{
  "google.com": {
    "ns": [
      "ns2.google.com.",
      "ns4.google.com.",
      "ns1.google.com.",
      "ns3.google.com."
    ],
    "apex": [
      "142.250.204.14"
    ],
    "mx": [
      "smtp.google.com."
    ],
    "mx_preference": [
      "10"
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
2022-10-06T09:37:38+1000 - INFO - Domains in list from:google.com (index:0) to:amazon.com (index:4) query rate ~21.2ms per domain (2.4ms per query) ETA: 2022-10-06T09:37:38+1000
```

---

Copyright &copy; 2022 Nicholas de Jong
