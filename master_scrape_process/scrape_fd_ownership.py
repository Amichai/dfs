

import requests

headers = {
    'authority': 'api.fanduel.com',
    'x-geo-packet': 'eyJhbGciOiJSUzI1NiJ9.eyJzdGF0ZSI6Ik5KIiwicHJvZHVjdCI6IkRGUyIsImdjX3RyYW5zYWN0aW9uX2lkIjoiZmFjYzcwMGE5NjAzMTRhZSIsInRpbWVzdGFtcCI6IjIwMjEtMTItMjVUMjA6MTc6NDEuNDY3WiIsInVzZXJfaWQiOiIyMTEzNTYwIiwicmVzdWx0Ijp0cnVlLCJleHBpcmVzIjoiMjAyMS0xMi0yNVQyMToxNzo0MS40NjdaIiwiZ2VvbG9jYXRlX2luIjozNjAwLCJpcF9hZGRyZXNzIjoiMTA4LjQxLjEwOC4xNTciLCJzZXNzaW9uX2lkIjo4Mzk3MTg3MTEsImNvdW50cnlfY29kZSI6IlVTIiwicmVnaW9uX2NvZGUiOiJOWSJ9.RtcrG7z45I-N_uZC2DDUdyjbIzSlZVBbebh_rZdglC__MfbfOh3CgM4CuWcLCT29KyY_Vy3QBAmPY5XpCtj7PknoXUc59YFFNoNgcjQOBNcLx3Yx45kMfpyzPNNe0EvqxZEkjfjmrvei3BygGvUc3HnF4pWDKvZEPIhhzFIa3kl9uBtGniwUMAhbW_2B9o6DFR-s3S3oaB5SFPqN88MU6CrMAgB9k59kaNQPTDHKHycNyi5QOFAjxS_XZtm-puiuwVxd5hrAIQRkCCDTwt6nPyfq1lmjeCCY_VCdm1X-7RAST1_6UqlTXQKHSJHpRFlHvNpYX0K1Og99LsmOn3ohDQ',
    'x-brand': 'FANDUEL',
    'sec-ch-ua-mobile': '?0',
    'authorization': 'Basic ZWFmNzdmMTI3ZWEwMDNkNGUyNzVhM2VkMDdkNmY1Mjc6',
    'accept': 'application/json',
    'x-currency': 'USD',
    'x-auth-token': 'eyJraWQiOiIxIiwiYWxnIjoiUlMyNTYifQ.eyJzZXMiOjgzOTcxODcxMSwic3ViIjoyMTEzNTYwLCJ1c24iOiJhbWwyIiwicHJkIjoiREZTIiwiY3J0IjoxNjQwMTgzMjc3LCJlbWwiOiJhbWljaGFpbWxldnlAZ21haWwuY29tIiwic3JjIjoxLCJybHMiOlsxXSwibWZhIjpmYWxzZSwidHlwIjoxLCJleHAiOjE2NDA0ODQ5NzF9.Wkz9uXfN0Bif_U8GgfCvRjhneOPrPDs3q79nAO09SK-1OIRfHjT8RXMXNMMsrDL539mFVYg1eyEwnOyX--aHJPRNpl01rKq9lhMTDMeDIM6e5UtkZnaxgl4m7eCJgH8rY_hyvnMIz-H_deDR87wadmWjfHH9vBU0loPqlwoyUi7yZNqFUkoaY1hoQW8Tcr5AAr1Q4pdcH6SkP_WQiSBihSrafrwFVhLlC_v_2aJmNsNfdhgGlKxfQL3yiMP5KXyNGOQ736Dfn-4aSFzeBjQSrktpQCnzi_a8XezDdu3aNGj5Yb0HHsymAKdBpHqcpWfkhIFPFZw31vUy3TuSai8Dew',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    'sec-ch-ua-platform': '"macOS"',
    'origin': 'https://www.fanduel.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.fanduel.com/',
    'accept-language': 'en-US,en;q=0.9,he;q=0.8',
    'sec-gpc': '1',
    'if-modified-since': 'Sat, 25 Dec 2021 20:34:58 GMT',
}

params = (
    ('include_projections', 'true'),
    ('page', '1'),
    ('page_size', '10'),
)

response = requests.get('https://api.fanduel.com/contests/69195-253438422/entries', headers=headers, params=params)

rosters = response.json()['rosters']
for roster in rosters:
    pass

__import__('pdb').set_trace()
#NB. Original query string below. It seems impossible to parse and
#reproduce query strings 100% accurately so the one below is given
#in case the reproduced version is not "correct".
# response = requests.get('https://api.fanduel.com/contests/69195-253438422/entries?include_projections=true&page=1&page_size=10', headers=headers)