# domain-email-records
![License](https://img.shields.io/github/license/verbnetworks/arpwitch.svg)

CLI tool to quickly lookup MX, SPF, DMARC records for many domains

## Install
```shell
pip install domain-email-records
```

## Usage
```shell
usage: domain-email-records [-h] [-q | -v] [--chunk-size <size>] [-d [<domain> ...]] [-f <filename>] [--csv-column <col>]

domain-email-records v0.0.0

CLI tool to quickly lookup MX, SPF, DMARC records for many domains

options:
  -h, --help            show this help message and exit
  -q, --quiet           Set quiet logging output
  -v, --verbose         Set verbose logging output
  --chunk-size <size>   Number of domain names to async resolve together (default: 100)

direct:
  -d [<domain> ...], --domains [<domain> ...]
                        Space separated list of domain names to query

filename:
  -f <filename>, --filename <filename>
                        Filename with list of domains to use; either a plain text file list -or- a comma-separated CSV file list.
  --csv-column <col>    CSV column number to use for domain-names -if- the file is CSV formatted (default: 2)
```

## Examples

### Domains directly at the CLI
```shell
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
```

### Domains listed in file
The file may be formatted as a flat plain list of domains names or as a CSV. 
```shell
$ domain-email-records -f alexa-top-1m-20220708.csv
{
  "google.com": {
  ...
}

```

---

Copyright &copy; 2022 Nicholas de Jong
