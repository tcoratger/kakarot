import pytest
from eth_account._utils.transaction_utils import transaction_rpc_to_rlp_structure
from rlp import encode

from tests.utils.constants import TRANSACTIONS
from tests.utils.helpers import flatten_tx_access_list, rlp_encode_signed_data


class TestEthTransaction:

    class TestDecodeTransaction:
        @pytest.mark.parametrize("transaction", TRANSACTIONS)
        async def test_should_decode_all_transactions_types(
            self, cairo_run, transaction
        ):
            encoded_unsigned_tx = rlp_encode_signed_data(transaction)
            decoded_tx = cairo_run(
                "test__decode",
                data=list(encoded_unsigned_tx),
            )

            expected_data = (
                "0x" + transaction["data"].hex()
                if isinstance(transaction["data"], bytes)
                else transaction["data"]
            )
            expected_access_list = flatten_tx_access_list(
                transaction.get("accessList", [])
            )
            expected_to = transaction["to"] or None

            assert transaction["nonce"] == decoded_tx["signer_nonce"]
            assert (
                transaction.get("gasPrice", transaction.get("maxFeePerGas"))
                == decoded_tx["max_fee_per_gas"]
            )
            assert transaction["gas"] == decoded_tx["gas_limit"]
            assert expected_to == decoded_tx["destination"]
            assert transaction["value"] == int(decoded_tx["amount"], 16)
            # pre-eip155 txs have an internal chain_id set to 0 in the decoded tx
            assert transaction.get("chainId", 0) == decoded_tx["chain_id"]
            assert expected_data == decoded_tx["payload"]
            assert expected_access_list == decoded_tx["access_list"]

    class TestParseAccessList:
        @pytest.mark.parametrize("transaction", TRANSACTIONS)
        def test_should_parse_access_list(self, cairo_run, transaction):
            rlp_structure_tx = transaction_rpc_to_rlp_structure(transaction)
            sanitized_access_list = [
                (
                    bytes.fromhex(address[2:]),
                    tuple(
                        bytes.fromhex(storage_key[2:]) for storage_key in storage_keys
                    ),
                )
                for address, storage_keys in rlp_structure_tx.get("accessList", [])
            ]
            encoded_access_list = encode(sanitized_access_list)

            output = cairo_run(
                "test__parse_access_list", data=list(encoded_access_list)
            )
            expected_output = flatten_tx_access_list(transaction.get("accessList", []))
            assert output == expected_output

    class TestGetTxType:
        @pytest.mark.parametrize("transaction", TRANSACTIONS)
        def test_should_return_tx_type(self, cairo_run, transaction):
            encoded_unsigned_tx = rlp_encode_signed_data(transaction)
            tx_type = cairo_run("test__get_tx_type", data=list(encoded_unsigned_tx))
            assert tx_type == transaction.get("type", 0)
