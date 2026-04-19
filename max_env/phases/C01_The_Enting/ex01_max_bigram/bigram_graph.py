import onnx
from onnx import helper, TensorProto
from max import engine
import numpy as np

def create_onnx():
    X = helper.make_tensor_value_info('input', TensorProto.FLOAT, [3])
    Y = helper.make_tensor_value_info('output', TensorProto.FLOAT, [3])
    
    # Softmax node
    node = helper.make_node('Softmax', inputs=['input'], outputs=['output'], axis=0)
    graph = helper.make_graph(nodes=[node], name='SoftmaxGraph', inputs=[X], outputs=[Y])
    model = helper.make_model(graph, producer_name='ents_oracle')
    
    onnx.save(model, 'bigram.onnx')

def main():
    create_onnx()
    session = engine.InferenceSession()
    model = session.load('bigram.onnx')
    
    input_tensor = np.array([-1.0, -2.0, 5.0], dtype=np.float32)
    out = model.execute(input=input_tensor)
    
    print(out['output'])

if __name__ == "__main__":
    main()
