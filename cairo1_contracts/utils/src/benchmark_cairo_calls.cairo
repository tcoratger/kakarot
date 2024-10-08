#[starknet::contract]
mod BenchmarkCairoCalls {
    const MAX_FELT: felt252 = 0x800000000000011000000000000000000000000000000000000000000000000;

    #[storage]
    struct Storage {}

    #[external(v0)]
    fn receive_felt_inputs(self: @ContractState, inputs: Array<felt252>) {}

    #[external(v0)]
    fn produce_bytes_output(self: @ContractState, output_size: u32) -> Array<felt252> {
        let mut res = array![];
        while (res.len() != output_size) {
            res.append(MAX_FELT);
        };
        return res;
    }
}
