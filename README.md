# IOUeth (lite)

A Stateless IOU Smart Contract for Ethereum (Vyper)

See stateful version at https://github.com/iRyanBell/ioueth

**Contract Address:**
0x47fed4d44b5d9549f0eadf7415bd1c56ebae7d88

### ABI:

```json
[
  {
    "name": "Iou",
    "inputs": [{ "type": "address", "name": "_to", "indexed": false }],
    "anonymous": false,
    "type": "event"
  },
  {
    "name": "iou",
    "outputs": [],
    "inputs": [{ "type": "address", "name": "_to" }],
    "constant": false,
    "payable": false,
    "type": "function",
    "gas": 1695
  }
]
```

**View on Etherscan:**
https://etherscan.io/address/0x47fed4d44b5d9549f0eadf7415bd1c56ebae7d88

### Functions

- iou(recipient): Sends a stateless IOU to an Ethereum address.
