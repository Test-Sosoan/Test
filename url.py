# url.py
import asyncio
import aiohttp
import socket
import re

async def analyze_website(url):
    result = {
        'url': url,
        'https': "HTTPS" if url.lower().startswith("https") else "Not HTTPS",
        'http_status': None,
        'cloudflare': "Not detected🟢",
        'captcha': "Not detected🟢",
        'payment_gateway': "Not detected",
        'ip': None
    }

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                result['http_status'] = response.status

                # Check for Cloudflare
                if 'Server' in response.headers and 'cloudflare' in response.headers['Server'].lower():
                    result['cloudflare'] = "Cloudflare detected🔴"

                # Check for Captcha
                content = await response.text()
                content = content.lower()
                captcha_providers = ['www.google.com/recaptcha', 'hcaptcha.com', 'funcaptcha.com', 'geetest.com', 'captcha.com']
                if any(provider in content for provider in captcha_providers):
                    result['captcha'] = "Captcha detected🔴"

                # Check for Payment Gateways
                payment_gateways = {
                    'Stripe': ['checkout.stripe.com', 'js.stripe.com', 'stripe.com', 'stripe.js', 'stripe.checkout'],
                    'PayPal': ['paypal.com', 'paypalobjects.com', 'paypal-sdk', 'paypal-button', 'paypal.me', 'braintreepayments.com', 'venmo.com', 'www.paypal.com/sdk'],
                    # ... (အခြား payment gateways များ)
                }

                for gateway, keywords in payment_gateways.items():
                    if any(keyword in content for keyword in keywords):
                        result['payment_gateway'] = f"{gateway}"
                        break

                # Resolve IP
                hostname = url.split("//")[-1].split("/")[0]
                result['ip'] = socket.gethostbyname(hostname)

    except asyncio.TimeoutError:
        result['http_status'] = "Timeout Error"
    except aiohttp.ClientError as e:
        result['http_status'] = f"HTTP Error: {e}"
    except socket.gaierror as e:
        result['ip'] = f"Error resolving IP: {e}"

    return result

async def check_url(url):
    if url:
        result = await analyze_website(url)
        return f"Result for {result['url']}\nPayment Gateway: {result['payment_gateway']}\nCloudflare: {result['cloudflare']}\nCaptcha: {result['captcha']}"
