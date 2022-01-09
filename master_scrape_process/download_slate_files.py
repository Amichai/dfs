import requests

headers = {
    'authority': 'api.fanduel.com',
    'x-geo-packet': 'eyJhbGciOiJSUzI1NiJ9.eyJzdGF0ZSI6Ik5KIiwicHJvZHVjdCI6IkRGUyIsImdjX3RyYW5zYWN0aW9uX2lkIjoiMDg3MGE2NTk0MjFiMzQ2ZiIsInRpbWVzdGFtcCI6IjIwMjEtMTItMjJUMTQ6Mjg6MDIuNDczWiIsInVzZXJfaWQiOiIyMTEzNTYwIiwicmVzdWx0Ijp0cnVlLCJleHBpcmVzIjoiMjAyMS0xMi0yMlQxNToyODowMi40NzNaIiwiZ2VvbG9jYXRlX2luIjozNjAwLCJpcF9hZGRyZXNzIjoiMTA4LjQxLjEwOC4xNTciLCJzZXNzaW9uX2lkIjo4Mzk3MTg3MTEsImNvdW50cnlfY29kZSI6IlVTIiwicmVnaW9uX2NvZGUiOiJOWSJ9.GDvoOYeokm6R4hp2EbBQqwZed1sK7TPPczx3Gc8M5IkdYMw5WCF2E5TnXo4pLBqeHnwv8n8_r5wKIOut7CggBiyj7vov0XqLaS7m18t-3Yv9Fqd6ETvmNod0GI-gdRldpkxXh4gQPAU32O9WVuMe-GjUbnr75xI4WvFFZroBVt3XMoG5Pp9GkMPcSKr_lOWx1VvY2ILX3HOUkGeOFAzXr3QpHpBe5BrAee3tvevmEKEGIe7bQ6IL29p8DnRhPZlE3M8XM2RomOSaDMytHKE3NLMGI_N96dS3xFIc48gnuIqTC0rB_m-XJT9nt1lVk70k8qkhsIYNRaUNzA3vHhV_Xg',
    'x-brand': 'FANDUEL',
    'sec-ch-ua-mobile': '?0',
    'authorization': 'Basic ZWFmNzdmMTI3ZWEwMDNkNGUyNzVhM2VkMDdkNmY1Mjc6',
    'accept': 'application/json',
    'x-currency': 'USD',
    'x-auth-token': 'eyJraWQiOiIxIiwiYWxnIjoiUlMyNTYifQ.eyJzZXMiOjgzOTcxODcxMSwic3ViIjoyMTEzNTYwLCJ1c24iOiJhbWwyIiwicHJkIjoiREZTIiwiY3J0IjoxNjQwMTgzMjc3LCJlbWwiOiJhbWljaGFpbWxldnlAZ21haWwuY29tIiwic3JjIjoxLCJybHMiOlsxXSwibWZhIjpmYWxzZSwidHlwIjoxLCJleHAiOjE2NDAyMjY0Nzd9.FN69Nv57pmhO5omg-_Jkax7TD1JpS4HpUdJRUCxuDhIRhPbHrnO9_p0c5D_TBz9-QsmjSmQ9VNGqfLVBX8aseDv4PVeIH1xmCyfiXOoi9bzNDmoFfJK3q8h51ZXYQmbDluxukMyq4Iax9zChTDq8CwibHebmmEOSdsot10X1TzcHd9r43npioVdbJ2oWHmP_sq9xzTe6PL9RMV8PPOzU8eNlrUMRQK-yGsZtmJkRotpSu_2qzgYV6dAuCl6emV_-s05JOuG0jzPTuy3rCO1ghjtxDhdwoGbvBxIOf72USwPcikP5RjdfpUsRDI1e7O3HbZkIC218ffyp6ZoZUlw1_Q',
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
    'if-none-match': 'W/"05d3c4828e182001c4d100490a80ff5f"',
}

params = (
    ('content_sources', 'NUMBERFIRE,ROTOWIRE,ROTOGRINDERS'),
)

response = requests.get('https://api.fanduel.com/fixture-lists/69096/players', headers=headers, params=params)

__import__('pdb').set_trace()

#NB. Original query string below. It seems impossible to parse and

#reproduce query strings 100% accurately so the one below is given
#in case the reproduced version is not "correct".
# response = requests.get('https://api.fanduel.com/fixture-lists/69096/players?content_sources=NUMBERFIRE,ROTOWIRE,ROTOGRINDERS', headers=headers)