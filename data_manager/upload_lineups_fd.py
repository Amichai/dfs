
import requests

headers = {
    'authority': 'api.fanduel.com',
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.9',
    'authorization': 'Basic ZWFmNzdmMTI3ZWEwMDNkNGUyNzVhM2VkMDdkNmY1Mjc6',
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://www.fanduel.com',
    'referer': 'https://www.fanduel.com/',
    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'x-auth-token': 'eyJraWQiOiIxIiwiYWxnIjoiUlMyNTYifQ.eyJzZXMiOjIyMDExMzk3NzAsInN1YiI6MjExMzU2MCwidXNuIjoiYW1sMiIsInByZCI6IkRGUyIsImNydCI6MTY3MjAyMDYzNywiZW1sIjoiYW1pY2hhaW1sZXZ5QGdtYWlsLmNvbSIsInNyYyI6MSwicmxzIjpbMV0sIm1mYSI6dHJ1ZSwidHlwIjoxLCJleHAiOjE2NzI1MTA2MzF9.XQrMHYx_9W97sBORQ8uV8JtmEmb3J2Z84zqsd3qM4p2SwxFTvWW-VAeozr535ptONrmFSnFt5ncGCQ4LkH33v_6zO-TnmvIDBBQypE7mdC2AEux8Kc3kjlnDRULRGNEbHPhfMEXpI1XIu76pBEcnMhbyY67nqxqVIP-u8opUdTBemDi3VW59-VEANCf2sGRYRhT4JvoMJ_g7bY76nblQL0A3Xi5ySMbckH-EOuNmHGJeTRBv-SgJUAZlZeJETD8eRw8HPd3kj7sdrlfQxzg6fq59SoLJAK7JX_-W7DlDQObcBgiRMnt7c6Pl8lKK_wVtgSdEt65IAFmnwjTJOK276Q',
    'x-brand': 'FANDUEL',
    'x-currency': 'USD',
    'x-geo-packet': 'eyJhbGciOiJSUzI1NiJ9.eyJzdGF0ZSI6Ik5KIiwicHJvZHVjdCI6IkRGUyIsImdjX3RyYW5zYWN0aW9uX2lkIjoiNjlmNzM0ZWViMjEyZTQxYiIsInRpbWVzdGFtcCI6IjIwMjItMTItMzFUMTE6NDI6MjUuMjU1WiIsInVzZXJfaWQiOiIyMTEzNTYwIiwicmVzdWx0Ijp0cnVlLCJleHBpcmVzIjoiMjAyMi0xMi0zMVQxMjo0MjoyNS4yNTVaIiwiZ2VvbG9jYXRlX2luIjozNjAwLCJpcF9hZGRyZXNzIjoiNjguMTMyLjIwMi4xOCIsInNlc3Npb25faWQiOjIyMDExMzk3NzAsImNvdW50cnlfY29kZSI6IlVTIiwicmVnaW9uX2NvZGUiOiJOWSJ9.dvttvA3XFFRNSAfl2-ceqyBcGeDtlrGZTXC3Oh8_awJTbpG-u7xt93Sx_6prKy7Vpkxjb4KqsTwUYZp9Cd5_8xTSUyFrd0-_npQ3xoW6bd7kNJ6SXUCNIK9rDDwLXLvvWR3U-MXxtbl2IwSDfPtI5PK6prLXVhFYxTKGvtOiRnbjwUQ8oS2Avu-4t9Kj1wNcgQQsdG2Vs0NQ9UcCYXS-9xiQYn3tv6XecDE6A8xq3cz0Dp4TQHXqcfIqbJzsGO97PpW3JI2ruNOkHXW6FmOrQI5FwfH1zqhC-yXDQbpv1wM6Fw7bHf5Y7XDdhEjOuRe2Gvuj7fC7MaGGpwcHho_Qtw',
    'x-geo-region': '',
    'x-px-context': '_px3=c801ed63e7f72708c29ba2f55a99bb7e8a00fbd0bef29736762c76a4989440b2:QzUOehF69v+CU6XJGV0qgrstEjGhFjtjvjdEzlFb1hOGwJJyGnibntFmjxjiMFNQQQUUHcrIDuIbYQ/tYi4fBQ==:1000:dKVax9bZCe01q6TfVEF5EsC4CCK3QAriBFxqHa9B+mwUh3d1ZrUEEv5YVl07rRx9g0XxXSFE24PtmV+SZGHOj5aza1bl7lNsnluI3sC0vJt/J0KgrNuPMtuh3VaqBGyUw9ttAtEyWl3gVsJkxKKmNEK/8KJZIXzePXt2+u1mYhBAxsydwq0qdj+bnHDQ1OkmS5TFOVyOizRrRSpDcW4xRQ==;_pxvid=6cbab6ca-774a-11ec-8289-5656456a4b6c;pxcts=30b280a5-3879-11ed-93fa-627452614e57;',
}

json_data = {
    'entries': [
        {
            'id': '3025239350',
            'roster': {
                'lineup': [
                    {
                        'position': 'PG',
                        'player': {
                            'id': '85412-15542',
                        },
                    },
                    {
                        'position': 'PG',
                        'player': {
                            'id': '85412-145348',
                        },
                    },
                    {
                        'position': 'SG',
                        'player': {
                            'id': '85412-110357',
                        },
                    },
                    {
                        'position': 'SG',
                        'player': {
                            'id': '85412-171780',
                        },
                    },
                    {
                        'position': 'SF',
                        'player': {
                            'id': '85412-14518',
                        },
                    },
                    {
                        'position': 'SF',
                        'player': {
                            'id': '85412-145319',
                        },
                    },
                    {
                        'position': 'PF',
                        'player': {
                            'id': '85412-145538',
                        },
                    },
                    {
                        'position': 'PF',
                        'player': {
                            'id': '85412-145538',
                        },
                    },
                    {
                        'position': 'C',
                        'player': {
                            'id': '85412-145538',
                        },
                    },
                ],
            },
        },
    ],
}

response = requests.put('https://api.fanduel.com/users/2113560/entries', headers=headers, json=json_data)

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{"entries":[{"id":"3025239350","roster":{"lineup":[{"position":"PG","player":{"id":"85412-15542"}},{"position":"PG","player":{"id":"85412-145348"}},{"position":"SG","player":{"id":"85412-110357"}},{"position":"SG","player":{"id":"85412-171780"}},{"position":"SF","player":{"id":"85412-14518"}},{"position":"SF","player":{"id":"85412-145319"}},{"position":"PF","player":{"id":"85412-145538"}},{"position":"PF","player":{"id":"85412-145538"}},{"position":"C","player":{"id":"85412-145538"}}]}}]}'
#response = requests.put('https://api.fanduel.com/users/2113560/entries', headers=headers, data=data)


print(response.text)