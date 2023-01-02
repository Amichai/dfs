
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
    'x-auth-token': 'eyJraWQiOiIxIiwiYWxnIjoiUlMyNTYifQ.eyJzZXMiOjIyMDExMzk3NzAsInN1YiI6MjExMzU2MCwidXNuIjoiYW1sMiIsInByZCI6IkRGUyIsImNydCI6MTY3MjAyMDYzNywiZW1sIjoiYW1pY2hhaW1sZXZ5QGdtYWlsLmNvbSIsInNyYyI6MSwicmxzIjpbMV0sIm1mYSI6dHJ1ZSwidHlwIjoxLCJleHAiOjE2NzI0NjQxMzd9.QSWwBzrR7fiMrksRWgarJNnh8wqZtMTnzXrsK_adzChsmba-CzgxQE4L7iGucVQoixLD5Yaa-JdVFIX8I0DdV93TnT4kdwR9-dsmTvK5CElGTJzxq0qXxNt_QWio1pswO-PJUZPrnzaTkNkSYPbF2jSy1suvhKJ_pPzK_2tBXc8l_OzDsp-5W5RqckpM546NtS4RKsCNFUdzoFujUec1i6zo5gL3sMhlAVGWc0Vk5u4rKORPT_YCY3waZZ3jdh624v7y1LCDejUqv6p6I85LHQJoWs0jNCe6jY86mjAClr-vQxFW7R_j3Q9f5p0LR-8SAxTRgfo59V38KwurS12ZSw',
    'x-brand': 'FANDUEL',
    'x-currency': 'USD',
    'x-geo-packet': 'eyJhbGciOiJSUzI1NiJ9.eyJzdGF0ZSI6Ik5KIiwicHJvZHVjdCI6IkRGUyIsImdjX3RyYW5zYWN0aW9uX2lkIjoiMjFhNzBkYzcxM2Q1NTNhOCIsInRpbWVzdGFtcCI6IjIwMjItMTItMzFUMDQ6NDQ6NDQuMzAwWiIsInVzZXJfaWQiOiIyMTEzNTYwIiwicmVzdWx0Ijp0cnVlLCJleHBpcmVzIjoiMjAyMi0xMi0zMVQwNTo0NDo0NC4zMDBaIiwiZ2VvbG9jYXRlX2luIjozNjAwLCJpcF9hZGRyZXNzIjoiNjguMTMyLjIwMi4xOCIsInNlc3Npb25faWQiOjIyMDExMzk3NzAsImNvdW50cnlfY29kZSI6IlVTIiwicmVnaW9uX2NvZGUiOiJOWSJ9.ZVWPBngbcaSLY_U54Ow22HuWm5D4CiCwe9NtSDpYbW9yPb7Zl8vCUYKujjjPKz3RLW-3oVVe9LP3vsuUGqBvdIptBabB2g_T3KG57iZdjP6DoGjIm88Ds_0fwgUjJr1pAM_hEb9koFLVCiu911g9PbYssguZn2aoivGdmE46mXfa4S5iXRh2XK_Zmd0A1iXk0wipA1rBvrblksH2dgPYW0EXgAjkhDay9VyuM4Zlnbz__1G1Yz5JGHIkyo8HqYRAc7U8Rl-Y-0bRfb-rrXC0YVjtqYlMyEAWFOSEg1mXG-W0pDCt5O8zYCyKu0P-dnzvY-4W48xsAw4K_BWuqxjuyw',
    'x-geo-region': '',
    'x-px-context': '_px3=3de61b8270c0a0cb336dc703aa0b1f80f6642f07bb99e85fc3623421b91ad52e:NISKfVHgXc9FMoHF6vrZiK7UAvzsrnpBLWXRG0zxCAWDxAqDy0jZTlnPO5h85XNRVdRYdYe1pGUNDj9aQvn6dQ==:1000:58jO1URIR70waGYU7gmL06msVs1VSg+3zAri46x704DwTVSPJdjEYWEy5+zkhea8wewyFGTEW6DWrB5wCGfBwREBVaOhZqFWTMXVKpUoVTDyudNDNDB+ZVj8okJkCJriwV2Qz4EyX3s/v5skyIRJoxJV8nhP+K6ai06TV6sYTIR727M8yuIE13YpkXZ5Tse6M4pYDaPDF7RR6o0Voe9V6w==;_pxvid=6cbab6ca-774a-11ec-8289-5656456a4b6c;pxcts=30b280a5-3879-11ed-93fa-627452614e57;',
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
                            'id': '85412-171749',
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
                            'id': '85412-110354',
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
#data = '{"entries":[{"id":"3025239350","roster":{"lineup":[{"position":"PG","player":{"id":"85412-15542"}},{"position":"PG","player":{"id":"85412-145348"}},{"position":"SG","player":{"id":"85412-110357"}},{"position":"SG","player":{"id":"85412-171780"}},{"position":"SF","player":{"id":"85412-14518"}},{"position":"SF","player":{"id":"85412-145319"}},{"position":"PF","player":{"id":"85412-171749"}},{"position":"PF","player":{"id":"85412-145538"}},{"position":"C","player":{"id":"85412-110354"}}]}}]}'
#response = requests.put('https://api.fanduel.com/users/2113560/entries', headers=headers, data=data)