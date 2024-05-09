import zipfile
from io import BytesIO
from PIL import Image
from random import choice
import os
from web3 import Web3



def generate_image_from_zip(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as z:
        dirs = set(os.path.dirname(x) for x in z.namelist() if '/' in x)
        layer_folders = sorted(dirs)

        base_image = None


        for folder in layer_folders:

            images = [f for f in z.namelist() if f.startswith(folder + '/') and f.endswith(('.png', '.jpg'))]
            if images:
                image_path = choice(images)
                with z.open(image_path) as file:
                    current_image = Image.open(BytesIO(file.read())).convert("RGBA")

                    if base_image is None:
                        base_image = current_image
                    else:

                        base_image = Image.alpha_composite(base_image, current_image)

        return base_image


def verify_signature(address, message, signature):
    """
    Verify that the provided signature corresponds to the message signed by the given Ethereum address.

    :param address: str - The Ethereum address expected to have signed the message.
    :param message: str - The message that was signed (usually a nonce provided by the server).
    :param signature: str - The signature produced by signing the message.
    :return: bool - True if the signature is valid and was made by the owner of the address, False otherwise.
    """
    w3 = Web3()
    prefixed_msg = w3.solidity_keccak(['string', 'address'], [message, address])
    # Ensure the message hash is in the proper Ethereum signature format.
    eth_hash = w3.solidity_keccak(['string', 'bytes32'], ['\x19Ethereum Signed Message:\n32', prefixed_msg])

    # Recover the signer from the signature
    signer = w3.eth.account.recoverHash(eth_hash, signature=signature)

    # Check if the recovered signer address matches the provided address
    return signer.lower() == address.lower()

