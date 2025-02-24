"""
referral_agent_demo.py

A local agent that simulates a donation-based query system with referral tracking.
This demonstration combines elements from pft_transact_check.py and agent_example.py
to implement a referral program on the XRP ledger.

Workflow:
1. Accept commands starting with "!pythia"
2. Handle referral codes in the format "refer-XXXX" 
3. Store user ID and referrer info in cache
4. Process user donations to the main wallet
5. After successful query handling, send 30% of donation to referrer wallet
"""

import os
import sys
import time
import random
import json
from decimal import Decimal
import asyncio
import logging
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configuration variables from .env
XRPL_RPC_ENDPOINT = os.getenv("XRPL_RPC_ENDPOINT", "https://xrplcluster.com")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "rYourTestWalletAddress")
MIN_AMOUNT = Decimal(os.getenv("MIN_AMOUNT", "2"))
TIMEOUT = int(os.getenv("TIMEOUT", "300"))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "10"))
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Import the transaction verification function from our transaction monitor module
from pft_transact_check import run_transaction_poll, VERIFIED

# Load postfiat SDK for sending transactions
from postfiat.wallet import Wallet
from postfiat.tokens import PFT
from postfiat.ripplestate import RippleState

# Set OpenAI API key
client = OpenAI(api_key=OPENAI_API_KEY)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple cache as a dictionary - in production use Redis or similar
referral_cache = {}

# Referrer wallet addresses mapping - in production store in database
referrer_wallets = {
    "zeno": "rZenoReferrerWalletAddress",
    "apollo": "rApolloReferrerWalletAddress",
    "athena": "rAthenaReferrerWalletAddress"
}

def generate_donation_memo() -> str:
    """
    Generate a donation memo in the format 'offerXXXXXX',
    where XXXXXX is a random 6-digit number.
    """
    return "offer" + str(random.randint(100000, 999999))

def store_referral_data(user_id, referrer_code):
    """
    Store referral data in cache: user ID, referrer code, and referrer wallet
    """
    referrer_name = referrer_code.replace("refer-", "")
    referrer_wallet = referrer_wallets.get(referrer_name)
    
    if referrer_wallet:
        referral_cache[user_id] = {
            "referrer_name": referrer_name,
            "referrer_wallet": referrer_wallet,
            "timestamp": time.time()
        }
        logger.info(f"Stored referral: User {user_id} referred by {referrer_name}")
        return True
    else:
        logger.warning(f"Unknown referrer code: {referrer_code}")
        return False

async def send_referral_commission(user_id, donation_amount):
    """
    Send 30% of the donation amount to the referrer wallet
    """
    if user_id not in referral_cache:
        logger.info(f"No referral data for user {user_id}, skipping commission")
        return False
    
    referral_data = referral_cache[user_id]
    referrer_wallet = referral_data["referrer_wallet"]
    commission_amount = donation_amount * Decimal("0.3")  # 30% commission
    
    try:
        # Load sender wallet (service wallet) from environment
        seed = os.getenv("SERVICE_WALLET_SEED")
        sender_wallet = Wallet.from_seed(seed)
        
        # Prepare RippleState for PFT transfer
        ripple_state = RippleState(XRPL_RPC_ENDPOINT)
        
        # Send PFT commission to referrer
        tx_hash = await ripple_state.send_pft(
            sender_wallet,
            referrer_wallet,
            commission_amount,
            memo=f"Commission for user {user_id}"
        )
        
        logger.info(f"Sent commission of {commission_amount} PFT to {referrer_wallet}, tx: {tx_hash}")
        return True
    
    except Exception as e:
        logger.error(f"Error sending referral commission: {e}")
        return False

def query_openai_advice(prompt: str) -> str:
    """
    Query the OpenAI GPT-4-turbo model using the provided prompt and the system prompt.
    This uses an instantiated client (client) and the new API call.
    """
    try:
        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
        advice = completion.choices[0].message.content.strip()
        return advice
    except Exception as e:
        logger.error(f"Error querying OpenAI: {e}")
        return "I'm sorry, I cannot provide advice at this time."

def parse_command(user_input):
    """
    Parse user command for !pythia and referral codes
    Returns (original_query, referral_code)
    """
    # Remove command prefix
    if not user_input.lower().startswith("!pythia"):
        return None, None
    
    content = user_input[len("!pythia"):].strip()
    
    # Check for referral code in format refer-XXXX
    referral_code = None
    query_parts = content.split()
    
    for part in query_parts:
        if part.lower().startswith("refer-"):
            referral_code = part.lower()
            # Remove referral code from query
            query_parts.remove(part)
            break
    
    original_query = " ".join(query_parts).strip()
    return original_query, referral_code

async def main():
    print("The gatekeepers of Pythia greet you!")
    print("To receive guidance from the techno-gods, you must first make an offering.")
    print("Please use the command '!pythia' followed by your question, for example:")
    print("!pythia refer-zeno Shall I change my career to align more with a post-AGI reality now?")
    
    # Simulate a user ID (in production, get from auth system)
    user_id = f"user_{random.randint(1000, 9999)}"
    
    # Wait for the command input
    user_input = input("Enter your command: ").strip()
    original_query, referral_code = parse_command(user_input)
    
    if original_query is None:
        print("Command not recognized. Exiting.")
        sys.exit(0)
    
    # If original query is empty, ask for it
    if not original_query:
        original_query = input("Please enter your question for Pythia: ").strip()
    
    # Store referral data if present
    if referral_code:
        if store_referral_data(user_id, referral_code):
            print(f"Referral from {referral_code.replace('refer-', '')} recognized!")
    
    # Explain donation mechanism
    donation_memo = generate_donation_memo()
    print("\nGreetings, seeker. I am Pythia, keeper of AI derived wisdom.")
    print(f"To unlock my guidance, you must first offer a donation of at least {MIN_AMOUNT} PFT tokens.")
    print(f"Please send your donation to the oracle wallet address: {WALLET_ADDRESS}")
    print(f"IMPORTANT: When donating, include the following memo EXACTLY: '{donation_memo}'")
    print("Once you have sent the donation, type 'DONATED' and press Enter.\n")
    
    donated_response = input("Type 'DONATED' once your donation is sent: ").strip()
    if donated_response.upper() != "DONATED":
        print("Donation not confirmed. The prophecy ritual cannot proceed. Please restart the process.")
        sys.exit(0)
    
    print("Verifying your donation, please wait...")
    # Call the transaction verification function
    result = run_transaction_poll(
        rpc_endpoint=XRPL_RPC_ENDPOINT,
        account=WALLET_ADDRESS,
        min_amount=MIN_AMOUNT,
        temp_id=donation_memo,
        timeout=TIMEOUT,
        poll_interval=POLL_INTERVAL
    )
    
    if result.get("status") != VERIFIED:
        print("The prophecy ritual cannot proceed. Your donation could not be verified. Please try again.")
        sys.exit(0)
    
    # Store the verified donation amount for commission calculation
    donation_amount = result.get("transaction", {}).amount_pft or MIN_AMOUNT
    print(f"Your donation of {donation_amount} PFT has been verified! The sacred ritual may now continue.\n")
    
    # Ask if user wants to proceed with the original query
    choice = input(f"Do you want to refine your question or continue with your original query:\n\"{original_query}\"\nRefine - press R, Original - press O: ").strip().upper()
    if choice == "O":
        final_prompt = original_query
    else:
        final_prompt = input("Please enter your final prompt for advice from Pythia: ").strip()
    
    print("\nConsulting the oracle for wisdom, please wait...\n")
    advice = query_openai_advice(final_prompt)
    
    print("Pythia's advice:")
    print(advice)
    print("\nIf you found this guidance valuable, consider offering extra PFT donations to the oracle treasury:")
    print(WALLET_ADDRESS)
    print("We are ready to give you guidance next time, seeker.") 
    
    # After successful completion, send referral commission if applicable
    if user_id in referral_cache:
        print("\nProcessing referral reward...")
        success = await send_referral_commission(user_id, donation_amount)
        if success:
            referrer = referral_cache[user_id]["referrer_name"]
            print(f"Thank you for using {referrer}'s referral code!")
    
if __name__ == "__main__":
    asyncio.run(main())