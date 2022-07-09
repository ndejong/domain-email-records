# domain-email-records
[![PyPi](https://img.shields.io/pypi/v/domain-email-records.svg)](https://pypi.python.org/pypi/domain-email-records/)
[![Build Tests](https://github.com/ndejong/domain-email-records/actions/workflows/build-tests.yml/badge.svg)](https://github.com/ndejong/domain-email-records/actions/workflows/build-tests.yml)
![License](https://img.shields.io/github/license/ndejong/domain-email-records.svg)

CLI tool to quickly lookup MX, SPF, DMARC records for many domains

__NOTE__ this tool can generate several-hundred DNS queries per second, be sure 
your nameservers have capacity to handle this.

## Install
```shell
pip install [--upgrade] domain-email-records
```

## Usage
```shell
usage: domain-email-records [-h] [-q | -v] [-o <filename>] [-t <seconds>] [-n [<address> ...]] [-c <size>] [-d [<domain> ...]] [-f <filename>] [-col <col>]

domain-email-records v0.2.1

CLI tool to quickly lookup MX, SPF, DMARC records for many domains

options:
  -h, --help            show this help message and exit
  -q, --quiet           Set quiet logging output
  -v, --verbose         Set verbose logging output
  -o <filename>, --out <filename>
                        Filename to save JSON formatted output to (default: stdout)
  -t <seconds>, --timeout <seconds>
                        Timeout seconds per domain-record query (default: 10)
  -n [<address> ...], --nameservers [<address> ...]
                        Space separated list of alternate nameservers (default: system nameservers)
  -c <size>, --chunk <size>
                        Chunk size per async loop to resolve together (default: 1000)

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
$ domain-email-records -f alexa-top-1m-20220708.csv -o /tmp/output.json
2022-07-09T16:51:41+1000 - INFO - Looking up 772475 domains in chunks of 1000 per async loop using system-local nameservers.
2022-07-09T16:51:56+1000 - INFO - Domains in list from:google.com (index:0) to:icims.com (index:1000) query rate ~15.5ms per domain (5.2ms per query) ETA: 2022-07-09T20:11:09+1000
2022-07-09T16:52:11+1000 - INFO - Domains in list from:aliyuncs.com (index:1000) to:rapidgator.net (index:2000) query rate ~15.1ms per domain (5.0ms per query) ETA: 2022-07-09T20:08:23+1000
2022-07-09T16:52:27+1000 - INFO - Domains in list from:hola.org (index:2000) to:shaadi.com (index:3000) query rate ~15.4ms per domain (5.1ms per query) ETA: 2022-07-09T20:08:58+1000
^C2022-07-09T16:52:27+1000 - WARNING - Exiting...
```

### Domains from plain-file with specific nameservers
```shell
$ domain-email-records -n 9.9.9.9 1.1.1.1 8.8.8.8 -f alexa-top-1m-20220708.txt -o /tmp/output.json
2022-07-09T16:54:25+1000 - INFO - Looking up 772475 domains in chunks of 1000 per async loop using ['9.9.9.9', '1.1.1.1', '8.8.8.8'] nameservers.
2022-07-09T16:54:49+1000 - INFO - Domains in list from:google.com (index:0) to:icims.com (index:1000) query rate ~24.6ms per domain (8.2ms per query) ETA: 2022-07-09T22:10:36+1000
2022-07-09T16:55:08+1000 - INFO - Domains in list from:aliyuncs.com (index:1000) to:rapidgator.net (index:2000) query rate ~18.8ms per domain (6.3ms per query) ETA: 2022-07-09T21:33:26+1000
2022-07-09T16:55:38+1000 - INFO - Domains in list from:hola.org (index:2000) to:shaadi.com (index:3000) query rate ~30.5ms per domain (10.2ms per query) ETA: 2022-07-09T22:11:07+1000
^C2022-07-09T16:55:39+1000 - WARNING - Exiting...
```

### Domains from cli args with output to file
```shell
$ domain-email-records -d google.com facebook.com apple.com amazon.com -o /tmp/output.json
2022-07-09T14:24:57+1000 - INFO - Domains in list from:google.com to:amazon.com queried (4x) at approx 121.1ms per domain (40.4ms per query) ETA: 2022-07-09 14:24:00
```

### Domains from cli args with output to stdout
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
