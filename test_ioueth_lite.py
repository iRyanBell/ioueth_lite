import pytest
import logging

log = logging.getLogger().info

@pytest.fixture
def contract(w3, get_contract):
	with open('./ioueth_lite.vy') as f:
		contract_code = f.read()
	return get_contract(contract_code)

def get_ious(w3, contract, get_logs, fromBlock=0, toBlock='latest'):
	# Find IOU transactions.
	filter = w3.eth.filter({'fromBlock': fromBlock, 'toBlock': toBlock, 'address': contract.address})
	events = filter.get_all_entries()

	# Decode transaction.
	ious = [[w3.eth.getTransaction(x['transactionHash'])['from'][2:],
	         get_logs(x['transactionHash'], contract, 'Iou')[0]['args']['_to'][2:]] for x in events]
	return ious

def calc_iou_balance(ious):
	balances = {}

	# Rehydrate state
	for iouPair in ious:
		# Combine sorted IOU pair.
		direction = 1 if iouPair[0] < iouPair[1] else -1
		iouPair.sort()
		iouPair = ''.join(iouPair)

		# Add initial keys
		if iouPair not in balances: balances[iouPair] = 0

		# Apply IOUs
		balances[iouPair] += direction
	return balances

def calc_iou_account(addrA, addrB, balances):
	# Crop hex prefix.
	addrA, addrB = addrA[2:], addrB[2:]

	# Calculate direction.
	iouPair = [addrA, addrB]
	direction = 1 if iouPair[0] < iouPair[1] else -1

	# Combine sorted IOU pair.
	iouPair.sort()
	iouPair = ''.join(iouPair)

	if iouPair not in balances: return 0
	return balances[iouPair] * direction

def test_initial_balances(w3, contract, get_logs):
	k0 = w3.eth.accounts[0]
	k1 = w3.eth.accounts[1]

	ious = get_ious(w3, contract, get_logs)
	balances = calc_iou_balance(ious)

	assert k0 not in balances or balances[k0] == 0
	assert k1 not in balances or balances[k1] == 0

def test_iou(w3, contract, get_logs):
	k0 = w3.eth.accounts[0]
	k1 = w3.eth.accounts[1]
	k2 = w3.eth.accounts[2]

	# Send 1/2 IOU from k0 -> k1
	contract.iou(k1, transact={'from': k0})
	balances = calc_iou_balance(get_ious(w3, contract, get_logs))
	assert calc_iou_account(k0, k1, balances) == 1
	assert calc_iou_account(k1, k0, balances) == -1

	# Send IOU from k1 -> k2
	contract.iou(k2, transact={'from': k1})
	balances = calc_iou_balance(get_ious(w3, contract, get_logs))
	assert calc_iou_account(k1, k2, balances) == 1
	assert calc_iou_account(k2, k1, balances) == -1

	# Send 2/2 IOU from k0 -> k1
	contract.iou(k1, transact={'from': k0})
	balances = calc_iou_balance(get_ious(w3, contract, get_logs))
	assert calc_iou_account(k0, k1, balances) == 2
	assert calc_iou_account(k1, k0, balances) == -2

	# Reverse 1/2 IOU with k1 -> k0
	contract.iou(k0, transact={'from': k1})
	balances = calc_iou_balance(get_ious(w3, contract, get_logs))
	assert calc_iou_account(k0, k1, balances) == 1
	assert calc_iou_account(k1, k0, balances) == -1

	# Reverse 2/2 IOU with k1 -> k0
	contract.iou(k0, transact={'from': k1})
	balances = calc_iou_balance(get_ious(w3, contract, get_logs))
	assert calc_iou_account(k0, k1, balances) == 0
	assert calc_iou_account(k1, k0, balances) == 0

	# Reverse IOU from k2 -> k1
	contract.iou(k1, transact={'from': k2})
	balances = calc_iou_balance(get_ious(w3, contract, get_logs))
	assert calc_iou_account(k1, k2, balances) == 0
	assert calc_iou_account(k2, k1, balances) == 0

def test_logs(w3, contract, get_logs):
	k0 = w3.eth.accounts[0]
	k1 = w3.eth.accounts[1]

	# Send IOU from k1 -> k0
	tx = contract.iou(k0, transact={'from': k1})
	evt = get_logs(tx, contract, 'Iou')[0]

	# Output event details to logger
	log(format(evt))

	assert evt['event'] == 'Iou'
	assert evt['args']['_to'] == k0