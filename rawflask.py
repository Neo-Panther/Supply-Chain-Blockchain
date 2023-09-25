

from urllib import response
from flask import Flask, jsonify, request

from bchain import Blockchain

app = Flask(__name__)
bchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine(): 
    current_port = "localhost:"+ str(port)
    if(current_port in bchain.delegates):
        # response = {
        #         'message': "New block mined!",
        #         'index': "",
        #         'transactions': "",
        #         'previous_hash': ""
        #     }
        # return jsonify(response),200
        if len(bchain.unverified_txn) >= 2: #mining the block only if number of transactions exceed 2
            last_block = bchain.last_block
            previous_hash = bchain.calc_hash(last_block) #previous block hash included in the block header
            ver_txn = bchain.validate_txn() #all the unverified transactions are verified and added to the block
            block = bchain.add_block(previous_hash)
             
            response = {
                'message': "New block mined!",
                'index': block['index'],
                'transactions': block['transactions'],
                'previous_hash': block['previous_hash']
            }
            print(len(bchain.unverified_txn))
            return jsonify(response), 200

        else:
            response = {
                'message' : 'Not enough transactions to mine a new block and add to chain!'
            }
            print(len(bchain.unverified_txn))
            return jsonify(response),400

    

    else:
        response = {
            'message': 'You are not authorised to mine block! Only delegates can mine.'
        }
        return jsonify(response),400


@app.route('/add/node', methods=['POST'])
def add_nodes(): #using API calls to add nodes the to the network
    values = request.get_json()
    required = ['nodes','stake']
    
    if not all(value in values for value in required):
        return 'Error',400

    
    bchain.add_node(values['nodes'], values['stake'])
    
    response = {
        'message': 'New nodes have been added.',
        'total_nodes': list(bchain.nodes)
    }
    print(bchain.nodes)
    return jsonify(response), 201


@app.route('/add/txn', methods=['POST'])
def new_txn(): #new transactions using the given required attributes to enable property deal between parties 
    values = request.get_json()
    required = ['buyer_ID','seller_ID', 'property_ID','rent']

    if not all(value in values for value in required):
        return 'Please enter buyer_ID,seller_ID, property_ID and rent.', 400
    
    idx = bchain.new_txn(values['buyer_ID'], values['seller_ID'], values['property_ID'], values['rent'])

    response = {
        'message': f'Transaction will be added to block {idx}'
    }
    return jsonify(response), 201


@app.route('/show_full_chain', methods=['GET'])
def show_chain(): #prints entire blockchain chain
    response = {
        'chain': bchain.chain,
        'length': len(bchain.chain)
    }
    print(bchain.chain)
    return response, 200


@app.route('/voting',methods=['GET'])
def voting(): #API cals for voting for the delegates in the DPOS consensus algorithm
    bchain.vote_grp = []
    bchain.star_grp = []
    bchain.super_grp = []
    if(port == 5000):
        show_votes = bchain.voting_power()

        response ={
            'message': 'Voting Results: ',
            'nodes': bchain.vote_grp
            }
        
        return jsonify(response),200
        
    else:
        response={
            'message': 'You are not authorized to conduct the election process!'
        }
        return jsonify(response),400


@app.route('/show/delegates',methods=['GET'])
def delegates(): #maximum of 3 delgates for mining the block in blockchain
    bchain.delegates = []
    show_delegates = bchain.delegates_selection()

    response={
        'message': 'The 3 delegate nodes selected for block mining are: ',
        'delegates': bchain.delegates
    }
    return jsonify(response),200


@app.route('/broadcast',methods=['GET'])
def syncro_delegates():
    bdelegates = bchain.broadcast()

    response ={
        'message': 'The delegate nodes are: ',
        'delegates': bchain.delegates
    }
    return jsonify(response),200
# @app.route('/chain/resolve', methods=['GET'])
# def consensus():
#     replaced = bchain.resolve_chain()

#     if replaced:
#         response = {
#             'message': 'Our chain was replaced',
#             'new_chain': bchain.chain
#         }
#     else:
#         response = {
#             'message': 'Our chain is authoritative',
#             'chain': bchain.chain
#         }
#     return jsonify(response), 200


@app.route('/chain/valid', methods = ['GET'])
def is_chain():
    res = bchain.is_chain_valid()
    response={
        'message': res
    }
    return jsonify(response) , 200

@app.route('/show/seller',methods=['GET'])
def seller(): #prints entire history corresponding to a given Property_ID
    values = request.get_json()
    required = 'Seller_ID'
    
    # if not all(value in values for value in required):
    #     return 'Please enter property_ID.', 400
    
    id = values[required]
    
    txns_seller= bchain.show_seller(id)
    response ={
        'message': 'Seller history: ',
        'transactions_details': txns_seller
    }
    return jsonify(response),200


@app.route('/show/buyer',methods=['GET'])
def buyer(): #prints entire history corresponding to a given Property_ID
    values = request.get_json()
    required = 'Buyer_ID'
    
    # if not all(value in values for value in required):
    #     return 'Please enter property_ID.', 400
    
    id = values[required]
    
    txns_buyer = bchain.show_buyer(id)
    response ={
        'message': 'Buyer history: ',
        'transactions_details': txns_buyer
    }
    return jsonify(response),200




if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='Listening on port')
    args = parser.parse_args()
    port = args.port
    app.run(host = '0.0.0.0', port = port)