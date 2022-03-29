# import requests

# params = {
#     'include_projections': 'true',
#     'page': '2',
#     'page_size': '10',
# }

# response = requests.get('https://api.fanduel.com/contests/73481-255835176/entries', params=params)

# __import__('pdb').set_trace()
from turtle import pd
import requests
import time

headers = {
    'authority': 'api.fanduel.com',
    'x-geo-packet': 'eyJhbGciOiJSUzI1NiJ9.eyJzdGF0ZSI6Ik5KIiwicHJvZHVjdCI6IkRGUyIsImdjX3RyYW5zYWN0aW9uX2lkIjoiYzAyMzllZmQ0YTU5MGY3NCIsInRpbWVzdGFtcCI6IjIwMjItMDMtMjdUMDE6MDE6MTQuODk1WiIsInVzZXJfaWQiOiIyMTEzNTYwIiwicmVzdWx0Ijp0cnVlLCJleHBpcmVzIjoiMjAyMi0wMy0yN1QwMjowMToxNC44OTVaIiwiZ2VvbG9jYXRlX2luIjozNjAwLCJpcF9hZGRyZXNzIjoiMTA4LjQxLjEwOC4xNTciLCJzZXNzaW9uX2lkIjoxMTEwNzE3NDI3LCJjb3VudHJ5X2NvZGUiOiJVUyIsInJlZ2lvbl9jb2RlIjoiTlkifQ.Agj0iq7Jf9xF6v5MeGT4XPJ66wJmxuBLZAhRYWLxBkZq_EVdY2hoISNRmjtmixzcc2UeNhV4y40t-QzcIGXpGyUau_d3wPXMi2dC0qD2rhuZ9brEnzp3pV6DUVjyK_bUGv9kZfqv4TpfgEebtA6Kc1CWOhHh0ZL-iZxqczE0OgbMzFokHSHp87N1d9FyMs2NxUDP8haSkVZiolOZYUAhvW891tSU7bQqN4rx2KUYDQgKk9WQ5k2FpWz5a4b1oKGqgbzKuL2ARayEw3qPmNZY2gByeTuVHDHaCANC1UYXo5mCcWkCGTEnIKvp2hazkI63B_KHVzjz8NuPMIKp8Z9Rwg',
    'x-brand': 'FANDUEL',
    'sec-ch-ua-mobile': '?0',
    'authorization': 'Basic ZWFmNzdmMTI3ZWEwMDNkNGUyNzVhM2VkMDdkNmY1Mjc6',
    'accept': 'application/json',
    'x-currency': 'USD',
    'x-auth-token': 'eyJraWQiOiIxIiwiYWxnIjoiUlMyNTYifQ.eyJzZXMiOjExMTA3MTc0MjcsInN1YiI6MjExMzU2MCwidXNuIjoiYW1sMiIsInByZCI6IkRGUyIsImNydCI6MTY0NjE3NjY5NiwiZW1sIjoiYW1pY2hhaW1sZXZ5QGdtYWlsLmNvbSIsInNyYyI6MSwicmxzIjpbMV0sIm1mYSI6ZmFsc2UsInR5cCI6MSwiZXhwIjoxNjQ4MzQ2MTgxfQ.TWgh7-dRIvjS2gJNPv9gWWSZqZ2u1PVeFlQJL1DwURhdUw0XDbwiSizGhbiFFxb-0hl7HaA0LUkm1-kV5YaRT4xqXaIxoztphT2REqK-Jq7-DOXy0yxiM_WKp-p5kwDwT_rN-weNg8yv9M7r3pgHmeF2HV27Y2ym2Jkcx7fXmqQLZDLII4kK64iLWqw_FGkn2S1Gz-0BB952oEJcz-euxj6ac00Rh2IqifiRgwOtUjq-ghMp4WYllOO4W3lKeGBrJMDchwnnbALG8tfFVkMQVmYs0mjF6JSUoWpAJit9mpVtcho-9KiDHsJRT2Lf9SzZCHsGZXVyUkIe2TIerWUH5Q',
    'x-geo-region': '',
    'x-px-context': '_px3=b1c4abc95c60630ae5be21643f76496410a76643f95feb8d41b77497da7dcc63:nTGf/PoHlm7U0YMNvR/QwykWWE2A5aAheo9+73N/C64YHUr3ndnfuJASj63uZnvVWYYUiISAeIZ8Pz/dKx1y3w==:1000:b7eBkKKeK3yLamqrl4WMP3F1Y6Amsn73xf8xWqUu1AcfwiFT7YGbmEGvUuG5mosvtd84nk/MNs/PHyWojLoNfuFRZOQQ7ckPuMJueIgBfVMxA9ZB6dmFQpZH48eOVETBSwtu86VYJUxyfVcuC4G4HxMJL+XQFlrOIYlMGMb0k8j8s7F2kKf9D9hekyKhkDaWo3lcqqXCftktlTzo2Jrdxw==;_pxvid=8b206e09-2836-11ec-b734-416f6a69746d;pxcts=5bdd51af-9530-11ec-9d4d-5a626e71524d;',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    'sec-ch-ua-platform': '"macOS"',
    'origin': 'https://www.fanduel.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.fanduel.com/',
    'accept-language': 'en-US,en;q=0.9,he;q=0.8',
    'if-modified-since': 'Sat, 26 Mar 2022 23:57:01 GMT',
}

#37600
for page_idx in range(3760):
    params = {
        'include_projections': 'true',
        'page': str(page_idx + 1),
        'page_size': '10',
    }

    response = requests.get('https://api.fanduel.com/contests/73481-255835176/entries', headers=headers, params=params)


    print(len(response.json()['entries']))
    __import__('pdb').set_trace()
    break